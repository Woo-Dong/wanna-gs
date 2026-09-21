"""Bounded HTTP evaluation transport. Default invocation is plan-only, never a model call.
The evaluator owns protected holdout. All content-bearing outputs are private (0600).
"""
from __future__ import annotations
import argparse
import contextlib
import fcntl
import hashlib
import json
import math
import os
from pathlib import Path
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'evals'))
from adapter import product_response, merchant_response
from scorer import fingerprint, read_jsonl, validate_dataset
VERSION = 'E02-v1'
REQUIRED_SOURCES = frozenset({'scripts/run_nl_eval.py','evals/adapter.py','evals/scorer.py','evals/taxonomy.json','evals/manifest.json','evals/validation.jsonl','evals/validation-coverage.json','src/contracts/assistant.ts','data/seed/products.json','package.json','package-lock.json','app/api/product-assistant/route.ts','app/api/merchant-assistant/route.ts'} | {str(p.relative_to(ROOT)) for p in (ROOT/'src/server').glob('*.ts')})
CANDIDATE_KEYS = ('mode','model','prompt_version','prompt_hash','catalog_version','catalog_hash','source_sha','api_version','source_files')
ENVELOPE = ('sessionId','generation','actorId','roleEpoch','requestId','conversationId','inputRevision','catalogHash')
CONSTRAINT_DEFAULTS = {'budgetLimitKrw':None,'excludeCategories':[],'excludeProductIds':[],'maxQuantity':None,'restorePrevious':False}
TRANSIENT = {'RATE_LIMITED','LLM_TIMEOUT','LLM_UNAVAILABLE','HTTP_TRANSPORT_UNKNOWN'}
STOP_CODES = {'LLM_AUTH_ERROR','LLM_QUOTA','LLM_CONFIGURATION','LLM_MODEL_UNAVAILABLE','LOCAL_CALL_LIMIT','CONNECTION_NOT_READY'}
STATE_KEYS = {'storeId','proposalId','proposalVersion','currentProposalVersion','stale','dailyBudgetKrw','currentConstraints','previousConstraints','groups'}

class RunnerError(Exception):
    """Only static, nonsecret error codes cross the CLI output boundary."""


def atomic_json(path, value):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    temp=path.with_name(path.name+'.tmp-'+uuid.uuid4().hex)
    fd=os.open(temp,os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600)
    with os.fdopen(fd,'w') as stream:
        json.dump(value,stream,ensure_ascii=False,indent=2,allow_nan=False);stream.write('\n');stream.flush();os.fsync(stream.fileno())
    os.replace(temp,path)


def file_hash(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def load_json(path): return json.loads(Path(path).read_text())
def integer(value, minimum=0): return type(value) is int and value>=minimum


def origin_url(value):
    parsed=urllib.parse.urlsplit(value)
    if parsed.username or parsed.password or parsed.query or parsed.fragment or parsed.path not in ('','/'):
        raise RunnerError('ORIGIN_MUST_BE_EXACT')
    if parsed.scheme not in {'http','https'} or not parsed.hostname: raise RunnerError('INVALID_ORIGIN')
    if parsed.scheme=='http' and parsed.hostname not in {'localhost','127.0.0.1','::1'}: raise RunnerError('HTTPS_REQUIRED')
    return urllib.parse.urlunsplit((parsed.scheme,parsed.netloc,'','',''))


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl): return None


class HttpTransport:
    def __init__(self, origin, bypass_path=None, timeout=50):
        self.origin=origin_url(origin);self.timeout=timeout;self.secret=None
        self.opener=urllib.request.build_opener(NoRedirect())
        if bypass_path:
            raw=load_json(bypass_path)
            if isinstance(raw,dict) and isinstance(raw.get('protectionBypass'),dict):
                values=list(raw['protectionBypass']);self.secret=values[0] if len(values)==1 else None
            elif isinstance(raw,dict): self.secret=raw.get('secret')
            if not isinstance(self.secret,str) or not self.secret or '\r' in self.secret or '\n' in self.secret:
                raise RunnerError('INVALID_BYPASS_FILE')
    def post(self, role, body):
        path='/api/product-assistant' if role=='customer' else '/api/merchant-assistant'
        headers={'Content-Type':'application/json','Accept':'application/json'}
        if self.secret: headers['x-vercel-protection-bypass']=self.secret
        request=urllib.request.Request(self.origin+path,data=json.dumps(body,ensure_ascii=False).encode(),headers=headers,method='POST')
        started=time.monotonic()
        try:
            with self.opener.open(request,timeout=self.timeout) as response:
                status=response.status;raw=response.read(2_000_001)
        except urllib.error.HTTPError as error:
            status=error.code;raw=error.read(2_000_001)
        except (TimeoutError,urllib.error.URLError,ConnectionError,OSError):
            return {'status':0,'error':'HTTP_TRANSPORT_UNKNOWN','latency_ms':int((time.monotonic()-started)*1000)}
        elapsed=int((time.monotonic()-started)*1000)
        if 300<=status<400: return {'status':status,'error':'REDIRECT_BLOCKED','latency_ms':elapsed}
        if len(raw)>2_000_000: return {'status':status,'error':'HTTP_BODY_TOO_LARGE','latency_ms':elapsed}
        try: value=json.loads(raw)
        except (ValueError,UnicodeError): return {'status':status,'error':'HTTP_INVALID_JSON','latency_ms':elapsed}
        return {'status':status,'body':value,'latency_ms':elapsed}


class Budget:
    """One goal ledger, locked/atomic before every possible outbound attempt.
    Unknown calls are conservatively charged; never claim the prior reserve was observed.
    """
    def __init__(self,path,prior_reserve=20,unknown_cost_reserve=.05):
        self.path=Path(path);self.prior=prior_reserve;self.unknown_cost=unknown_cost_reserve
        if not integer(prior_reserve) or not isinstance(unknown_cost_reserve,(int,float)) or unknown_cost_reserve<=0 or not math.isfinite(unknown_cost_reserve): raise RunnerError('INVALID_BUDGET_CONFIG')
    @contextlib.contextmanager
    def locked(self):
        self.path.parent.mkdir(parents=True,exist_ok=True)
        with open(str(self.path)+'.lock','a') as lock:
            fcntl.flock(lock,fcntl.LOCK_EX)
            data=load_json(self.path) if self.path.exists() else {'version':VERSION,'prior_call_reserve':self.prior,'prior_actual_calls':'unknown','prior_cost_reserve_usd':self.prior*self.unknown_cost,'prior_actual_cost_usd':'unknown','unknown_attempt_cost_reserve_usd':self.unknown_cost,'attempts':{},'holdout_claims':{}}
            if data['prior_call_reserve']!=self.prior or data['unknown_attempt_cost_reserve_usd']!=self.unknown_cost: raise RunnerError('BUDGET_RESERVE_CONFIG_CHANGED')
            if data.get('version')!=VERSION or not isinstance(data.get('attempts'),dict):raise RunnerError('CORRUPT_BUDGET_LEDGER')
            for item in data['attempts'].values():
                cost=item.get('cost');called=item.get('provider_called')
                if called is not None and type(called) is not bool:raise RunnerError('CORRUPT_BUDGET_LEDGER')
                if cost is not None and (isinstance(cost,bool) or not isinstance(cost,(int,float)) or not math.isfinite(cost) or cost<0):raise RunnerError('CORRUPT_BUDGET_LEDGER')
            yield data
            atomic_json(self.path,data)
    @staticmethod
    def totals(data):
        attempts=list(data['attempts'].values())
        return {'accounted_calls_upper_bound':data['prior_call_reserve']+sum(a.get('provider_called') is not False for a in attempts),
                'known_provider_calls':sum(a.get('provider_called') is True for a in attempts),
                'unknown_provider_calls':sum(a.get('provider_called') is None for a in attempts),
                'cost_upper_estimate_usd':data['prior_cost_reserve_usd']+sum(a.get('cost') if a.get('cost') is not None else (0 if a.get('provider_called') is False else data['unknown_attempt_cost_reserve_usd']) for a in attempts),
                'known_cost_usd':sum(a.get('cost') or 0 for a in attempts)}
    def reserve(self, run_id, mandatory_reserve, mandatory_cost_reserve=0):
        if not integer(mandatory_reserve) or isinstance(mandatory_cost_reserve,bool) or not isinstance(mandatory_cost_reserve,(int,float)) or not math.isfinite(mandatory_cost_reserve) or mandatory_cost_reserve<0:raise RunnerError('INVALID_MANDATORY_RESERVE')
        with self.locked() as data:
            totals=self.totals(data)
            if totals['accounted_calls_upper_bound']+1+mandatory_reserve>2400: raise RunnerError('CALL_RESERVE_STOP')
            if totals['cost_upper_estimate_usd']+self.unknown_cost+mandatory_cost_reserve>=15: raise RunnerError('COST_SOFT_STOP')
            aid=str(uuid.uuid4());data['attempts'][aid]={'run_id':run_id,'status':'pending','provider_called':None,'cost':None}
        return aid
    def finish(self, aid, observation):
        with self.locked() as data:
            if aid not in data['attempts'] or data['attempts'][aid]['status']!='pending': raise RunnerError('ATTEMPT_LEDGER_CONFLICT')
            data['attempts'][aid].update(status=observation['status'],provider_called=observation.get('provider_called'),cost=observation.get('cost_usd'))
    def claim_holdout(self,dataset_hash,run_id):
        with self.locked() as data:
            old=data['holdout_claims'].get(dataset_hash)
            if old and old!=run_id: raise RunnerError('HOLDOUT_ALREADY_STARTED')
            data['holdout_claims'][dataset_hash]=run_id
    def snapshot(self):
        with self.locked() as data: return self.totals(data)


def normalize_constraints(value):
    if value is None:return None
    if not isinstance(value,dict) or not set(value)<=set(CONSTRAINT_DEFAULTS):raise RunnerError('INVALID_STATE_CONSTRAINTS')
    return {**CONSTRAINT_DEFAULTS,**value}


def make_request(case, turns, config, state_fixtures, run_id):
    user_turns=[t['text'] for t in case['turns'] if t['role']=='user'];index=len(turns)
    if index>=len(user_turns):raise RunnerError('NO_UNEXECUTED_TURN')
    history=[]
    for i,turn in enumerate(turns):
        history.extend([{'role':'user','content':user_turns[i]},{'role':'assistant','content':json.dumps(turn['raw_response'],ensure_ascii=False,separators=(',',':'))}])
    body={'sessionId':'EVAL-'+run_id,'generation':1,'actorId':'EVAL-'+case['role'],'roleEpoch':1,
          'requestId':run_id+'-'+case['id']+'-'+str(index),'conversationId':run_id+'-'+case['id'],'inputRevision':index+1,
          'catalogHash':config['catalog_hash'],'text':user_turns[index],'history':history}
    if any(len(body[k])>100 for k in ENVELOPE if isinstance(body[k],str)):raise RunnerError('ENVELOPE_IDENTIFIER_TOO_LONG')
    if not 1<=len(body['text'].strip())<=1200 or len(history)>12 or any(not 1<=len(t['content'])<=5000 for t in history):raise RunnerError('INPUT_OR_HISTORY_EXCEEDS_API_BOUND')
    if case['role']=='customer':body['clarificationCount']=sum(t['raw_response'].get('action')=='ask_clarification' for t in turns)
    else:
        context=case.get('context',{});base=state_fixtures.get(case['id'],state_fixtures.get('default'))
        if not isinstance(base,dict):raise RunnerError('MERCHANT_STATE_FIXTURE_REQUIRED')
        if not set(base)<=STATE_KEYS:raise RunnerError('UNEXPECTED_STATE_FIXTURE_KEYS')
        state=dict(base)
        for key in STATE_KEYS:
            if key in context:state[key]=context[key]
        for old,new in [('proposalRevision','proposalVersion'),('currentRevision','currentProposalVersion')]:
            if old in context:state[new]=context[old]
        for key in ['currentConstraints','previousConstraints']:state[key]=normalize_constraints(state.get(key))
        required={'storeId','proposalId','proposalVersion','dailyBudgetKrw','currentConstraints','previousConstraints','groups'}
        if not required<=state.keys() or not integer(state['dailyBudgetKrw']) or not isinstance(state['groups'],list):raise RunnerError('INCOMPLETE_MERCHANT_STATE')
        for group in state['groups']:
            if not isinstance(group,dict) or set(group)!={'sku','requestedQty','orderableQty','purchaseCostKrw'} or not isinstance(group['sku'],str) or any(not integer(group[k]) for k in ['requestedQty','orderableQty','purchaseCostKrw']):raise RunnerError('INVALID_MERCHANT_GROUP_STATE')
        body['state']=state
    # Build from an allowlist; never copy cases, labels, expected, IDs, research or oracle metadata.
    return body


def usage_record(usage):
    if not isinstance(usage,dict):return None,None
    keys=['inputTokens','outputTokens','totalTokens']
    if any(not integer(usage.get(k)) for k in keys) or usage['totalTokens']!=usage['inputTokens']+usage['outputTokens']:return None,None
    cost=usage.get('estimatedCostUsd')
    if cost is not None and (isinstance(cost,bool) or not isinstance(cost,(int,float)) or not math.isfinite(cost) or cost<0):return None,None
    return {'input_tokens':usage['inputTokens'],'output_tokens':usage['outputTokens'],'total_tokens':usage['totalTokens']},cost


def validate_response(raw,role,catalog):
    if not isinstance(raw,dict):return False
    if role=='customer':
        if set(raw)!={'action','candidates','question','reason','confirmationRequired'} or raw['confirmationRequired'] is not True:return False
        if raw['action'] not in {'show_candidates','ask_clarification','unidentified'} or not isinstance(raw['reason'],str) or not isinstance(raw['candidates'],list) or len(raw['candidates'])>6:return False
        ids=[]
        for c in raw['candidates']:
            if not isinstance(c,dict) or set(c)!={'id','kind','sharedEvidence','differences','unknownConditions'}:return False
            if c['id'] not in catalog or c['kind'] not in {'exact','confirm','alternative'}:return False
            if any(not isinstance(c[k],list) or any(not isinstance(v,str) for v in c[k]) for k in ['sharedEvidence','differences','unknownConditions']):return False
            ids.append(c['id'])
        if len(ids)!=len(set(ids)):return False
        primary=any(c['kind']!='alternative' for c in raw['candidates'])
        if raw['action']=='show_candidates' and (not primary or raw['question'] is not None):return False
        if raw['action']=='unidentified' and (primary or raw['question'] is not None):return False
        if raw['action']=='ask_clarification' and (not isinstance(raw['question'],str) or not raw['question'].strip()):return False
        return True
    if set(raw)!={'intent','scope','constraints','question','reason'} or raw['intent'] not in {'modify','restore','clarify'} or not isinstance(raw['reason'],str):return False
    c=raw['constraints']
    if not isinstance(c,dict) or set(c)!=set(CONSTRAINT_DEFAULTS):return False
    if any(c[k] is not None and not integer(c[k]) for k in ['budgetLimitKrw','maxQuantity']):return False
    if type(c['restorePrevious']) is not bool or not isinstance(c['excludeProductIds'],list) or any(x not in catalog for x in c['excludeProductIds']):return False
    if not isinstance(c['excludeCategories'],list) or any(not isinstance(x,str) for x in c['excludeCategories']):return False
    if len(c['excludeProductIds'])!=len(set(c['excludeProductIds'])) or len(c['excludeCategories'])!=len(set(c['excludeCategories'])):return False
    if raw['intent']=='restore' and (raw['scope']!='current_proposal' or c!={**CONSTRAINT_DEFAULTS,'restorePrevious':True}):return False
    if raw['intent']=='modify' and (c['restorePrevious'] or c==CONSTRAINT_DEFAULTS):return False
    if raw['intent']=='clarify':return raw['scope'] is None and isinstance(raw['question'],str) and bool(raw['question'].strip()) and c==CONSTRAINT_DEFAULTS
    return raw['scope'] in {'policy','current_proposal'} and raw['question'] is None


def parse_attempt(http,body,role,config,catalog):
    base={'http_status':http['status'],'latency_ms':http['latency_ms'],'provider_called':None,'status':'unknown','usage':None,'cost_usd':None}
    if http.get('error'):return base|{'code':http['error']},None
    response=http.get('body')
    if not isinstance(response,dict):return base|{'code':'INVALID_HTTP_ENVELOPE'},None
    if response.get('ok') is False:
        error=response.get('error',{});attempt=error.get('attempt',{}) if isinstance(error,dict) else {}
        if not isinstance(attempt,dict):attempt={}
        used,cost=usage_record(attempt.get('usage'))
        called=attempt.get('providerCalled');called=called if type(called) is bool else None
        code=error.get('code','INVALID_HTTP_ENVELOPE') if isinstance(error,dict) else 'INVALID_HTTP_ENVELOPE'
        if code=='LLM_UNAVAILABLE' and called is False:code='CONNECTION_NOT_READY'
        if code not in STOP_CODES|TRANSIENT|{'INVALID_INPUT','CATALOG_MISMATCH','INVALID_MODEL_RESPONSE'}:code='INVALID_HTTP_ENVELOPE'
        return base|{'provider_called':called,'usage':used,'cost_usd':cost,'status':'failed','code':code},None
    data=response.get('data',{})
    if response.get('ok') is not True or http['status']!=200 or not isinstance(data,dict):return base|{'code':'INVALID_HTTP_ENVELOPE'},None
    used,cost=usage_record(data.get('usage'))
    base.update(provider_called=True if data.get('mode')=='live' else False if data.get('mode')=='fixture' else None,usage=used,cost_usd=cost)
    if any(data.get(k)!=body[k] for k in ENVELOPE):return base|{'code':'STALE_RESPONSE_ENVELOPE'},None
    for actual,expected in [('mode','mode'),('model','model'),('promptVersion','prompt_version'),('catalogVersion','catalog_version')]:
        if data.get(actual)!=config[expected]:return base|{'code':'RESPONSE_VERSION_MISMATCH'},None
    for actual,expected in [('apiVersion','api_version'),('promptHash','prompt_hash'),('sourceCommit','source_sha')]:
        if config.get('require_remote_attestation') and data.get(actual)!=config.get(expected):return base|{'code':'REMOTE_ATTESTATION_MISMATCH'},None
        if actual in data and data[actual]!=config.get(expected):return base|{'code':'REMOTE_ATTESTATION_MISMATCH'},None
    if used is None:return base|{'code':'INVALID_USAGE'},None
    raw=data.get('result')
    if not validate_response(raw,role,catalog):return base|{'code':'INVALID_RESPONSE_SCHEMA'},None
    return base|{'status':'ok'},raw


def check_inputs(cases,config,coverage,catalog_path,state_fixtures,holdout=False,frozen_best=None):
    required={'mode','origin','model','prompt_version','prompt_hash','catalog_version','catalog_hash','source_sha','api_version','source_files','mandatory_reserve'}
    if not required<=config.keys() or config['mode'] not in {'live','fixture'}:raise RunnerError('INVALID_RUN_CONFIG')
    config=dict(config);config['origin']=origin_url(config['origin'])
    if config['mode']=='fixture' and urllib.parse.urlsplit(config['origin']).hostname not in {'localhost','127.0.0.1','::1'}:raise RunnerError('FIXTURE_REQUIRES_LOCAL_MOCK_HTTP')
    if not REQUIRED_SOURCES<=config['source_files'].keys():raise RunnerError('SOURCE_BINDING_REQUIRED')
    if config['prompt_hash']!=config['source_files']['src/server/prompts.ts']:raise RunnerError('PROMPT_FINGERPRINT_MISMATCH')
    for name,digest in config['source_files'].items():
        path=(ROOT/name).resolve()
        if not path.is_relative_to(ROOT) or not path.is_file() or file_hash(path)!=digest:raise RunnerError('LOCAL_SOURCE_FINGERPRINT_MISMATCH')
    if config['mode']=='live':
        proof=config.get('deployment_proof',{})
        if not isinstance(proof,dict) or proof.get('origin')!=config['origin'] or proof.get('source_sha')!=config['source_sha']:raise RunnerError('DEPLOYMENT_SOURCE_PROOF_REQUIRED')
        if not proof.get('artifact') or file_hash(ROOT/proof['artifact'])!=proof.get('sha256'):raise RunnerError('DEPLOYMENT_PROOF_FINGERPRINT_MISMATCH')
        artifact=load_json(ROOT/proof['artifact'])
        if proof.get('kind')=='local_exact_source':
            if urllib.parse.urlsplit(config['origin']).hostname not in {'localhost','127.0.0.1','::1'} or artifact.get('origin')!=config['origin'] or artifact.get('source_sha')!=config['source_sha'] or artifact.get('source_files')!=config['source_files']:raise RunnerError('LOCAL_SOURCE_PROOF_MISMATCH')
        else:
            remote_url=artifact.get('url','');remote_url=remote_url if remote_url.startswith('https://') else 'https://'+remote_url
            if artifact.get('readyState')!='READY' or not str(artifact.get('id','')).startswith('dpl_') or origin_url(remote_url)!=config['origin'] or artifact.get('gitSource',{}).get('sha')!=config['source_sha']:raise RunnerError('IMMUTABLE_DEPLOYMENT_PROOF_MISMATCH')
    catalog=json.loads(Path(catalog_path).read_text());catalog_hash=hashlib.sha256(json.dumps(catalog,ensure_ascii=False,separators=(',',':')).encode()).hexdigest()
    if catalog_hash!=config['catalog_hash'] or any(c['catalog_hash']!=catalog_hash for c in cases):raise RunnerError('CATALOG_MISMATCH')
    ids={p['sku'] for p in catalog};check=validate_dataset(cases,ids)
    if not check['valid']:raise RunnerError('INVALID_EVAL_DATASET')
    if coverage.get('dataset_hash')!=fingerprint(cases) or coverage.get('cases')!=len(cases) or coverage.get('counts')!=check['counts']:raise RunnerError('FROZEN_COVERAGE_MISMATCH')
    if any(t['role']!='user' for c in cases for t in c['turns']):raise RunnerError('SCRIPTED_ASSISTANT_HISTORY_FORBIDDEN')
    protected=any(c['split']=='holdout' for c in cases)
    if protected:
        if not holdout or any(c['split']!='holdout' for c in cases):raise RunnerError('PROTECTED_HOLDOUT_NOT_AUTHORIZED')
        if not isinstance(frozen_best,dict) or frozen_best.get('approved') is not True or frozen_best.get('source_sha')!=config['source_sha'] or frozen_best.get('prompt_hash')!=config['prompt_hash'] or frozen_best.get('catalog_hash')!=catalog_hash or frozen_best.get('model')!=config['model']:raise RunnerError('FROZEN_BEST_REQUIRED')
        if config['mode']!='live':raise RunnerError('HOLDOUT_REQUIRES_FROZEN_LIVE_CANDIDATE')
        runs=frozen_best.get('validation_run_ids',[])
        if len(runs)!=2 or len(set(runs))!=2 or frozen_best.get('validation_both_stage_ready') is not True:raise RunnerError('INDEPENDENT_REPEAT_PROOF_REQUIRED')
        proofs=frozen_best.get('validation_reports',[])
        if len(proofs)!=2:raise RunnerError('VALIDATION_REPORT_ARTIFACTS_REQUIRED')
        reports=[]
        for proof in proofs:
            if not isinstance(proof,dict) or file_hash(ROOT/proof['path'])!=proof.get('sha256'):raise RunnerError('VALIDATION_PROOF_FINGERPRINT_MISMATCH')
            reports.append(load_json(ROOT/proof['path']))
        binding=frozen_best.get('validation_binding',{})
        bound=[]
        for key in ['config','state_fixtures']:
            proof=binding.get(key,{})
            if not isinstance(proof,dict) or not proof.get('path') or file_hash(ROOT/proof['path'])!=proof.get('sha256'):raise RunnerError('VALIDATION_BINDING_ARTIFACT_REQUIRED')
            bound.append(load_json(ROOT/proof['path']))
        validation_config,validation_states=bound
        if any(validation_config.get(key)!=config.get(key) for key in CANDIDATE_KEYS):raise RunnerError('VALIDATION_CANDIDATE_MISMATCH')
        expected_validation_fp=fingerprint({'runner':VERSION,'config':validation_config,'state_fixtures_hash':fingerprint(validation_states)})
        expected_validation_dataset=load_json(ROOT/'evals/validation-coverage.json')['dataset_hash']
        if any(report.get('run_fingerprint')!=expected_validation_fp or report.get('dataset_hash')!=expected_validation_dataset for report in reports):raise RunnerError('VALIDATION_CANDIDATE_PROOF_MISMATCH')
        if {p.get('run_id') for p in reports}!=set(runs) or any(p.get('stage_ready') is not True or p.get('mode')!='live' or p.get('catalog_hash')!=catalog_hash for p in reports) or not reports[0].get('run_fingerprint') or reports[0]['run_fingerprint']!=reports[1].get('run_fingerprint') or reports[0].get('dataset_hash')!=reports[1].get('dataset_hash'):raise RunnerError('VALIDATION_REPEAT_PROOF_MISMATCH')
    cost_reserve=config.get('mandatory_cost_reserve_usd',0)
    if isinstance(cost_reserve,bool) or not isinstance(cost_reserve,(int,float)) or not math.isfinite(cost_reserve) or cost_reserve<0:raise RunnerError('INVALID_COST_RESERVE')
    reserve=config['mandatory_reserve']
    if not isinstance(reserve,dict) or not reserve or any(not integer(n) for n in reserve.values()):raise RunnerError('MANDATORY_RESERVE_REQUIRED')
    # Known full follow-up requirements cannot silently disappear from a baseline run.
    if len(cases)==336 and {c['split'] for c in cases}=={'dev','validation'}:
        if reserve.get('best_validation',0)<276 or reserve.get('holdout',0)<276 or reserve.get('ux',0)<144 or reserve.get('g5_g6',0)<=0:raise RunnerError('BASELINE_RESERVE_TOO_SMALL')
    for case in cases:make_request(case,[],config,state_fixtures,'preflight')
    return config,ids,protected


class Runner:
    def __init__(self,cases,config,output,budget,transport,state_fixtures=None,run_id=None):
        self.cases=cases;self.config=config;self.out=Path(output);self.budget=budget;self.transport=transport;self.states=state_fixtures or {}
        self.run_id=run_id or str(uuid.uuid4());self.run_fingerprint=fingerprint({'runner':VERSION,'config':config,'state_fixtures_hash':fingerprint(self.states)})
        self.checkpoint=self.out/'checkpoint.json';self.state=None
    def save(self):
        atomic_json(self.checkpoint,self.state)
        dest=self.out/'observations.jsonl';temporary=dest.with_suffix('.tmp');fd=os.open(temporary,os.O_CREAT|os.O_TRUNC|os.O_WRONLY,0o600)
        with os.fdopen(fd,'w') as stream:
            for case in self.cases:
                item=self.state['cases'].get(case['id'],{}).get('observation')
                if item:stream.write(json.dumps(item,ensure_ascii=False)+'\n')
            stream.flush();os.fsync(stream.fileno())
        os.replace(temporary,dest)
        atomic_json(self.out/'progress.json',{'run_id':self.run_id,'mode':self.config['mode'],'cases_expected':len(self.cases),'cases_recorded':sum(bool(v.get('observation')) for v in self.state['cases'].values()),'turns_recorded':sum(len(v.get('turns',[])) for v in self.state['cases'].values()),'pending_attempt':bool(self.state['pending']),'stop_code':self.state['stop_code']})
    def initialize(self,resume=False):
        self.out.mkdir(parents=True,exist_ok=True)
        if self.checkpoint.exists():
            if not resume:raise RunnerError('RUN_ALREADY_EXISTS')
            self.state=load_json(self.checkpoint);self.run_id=self.state['run_id']
            if self.state['run_fingerprint']!=self.run_fingerprint or self.state['dataset_hash']!=fingerprint(self.cases):raise RunnerError('RESUME_FINGERPRINT_MISMATCH')
            if self.state.get('pending'):raise RunnerError('UNCERTAIN_PENDING_ATTEMPT_DO_NOT_REPLAY')
            if self.state.get('stop_code') in STOP_CODES or self.state.get('stop_code') in {'REDIRECT_BLOCKED','STALE_RESPONSE_ENVELOPE','RESPONSE_VERSION_MISMATCH','REMOTE_ATTESTATION_MISMATCH'}:raise RunnerError('STOPPED_RUN_REQUIRES_NEW_REVIEW')
        else:
            if resume:raise RunnerError('NO_RUN_TO_RESUME')
            self.state={'version':VERSION,'run_id':self.run_id,'run_fingerprint':self.run_fingerprint,'dataset_hash':fingerprint(self.cases),'mode':self.config['mode'],'source_sha':self.config['source_sha'],'prompt_hash':self.config['prompt_hash'],'catalog_hash':self.config['catalog_hash'],'api_version':self.config['api_version'],'cases':{},'pending':None,'stop_code':None,'complete':False}
            self.save()
    def run(self,catalog_ids,resume=False,max_cases=None,sleep=time.sleep):
        self.out.mkdir(parents=True,exist_ok=True)
        with open(self.out/'run.lock','a') as lock:
            try:fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
            except BlockingIOError:raise RunnerError('RUN_ALREADY_ACTIVE')
            self.initialize(resume)
            if any(c['split']=='holdout' for c in self.cases):self.budget.claim_holdout(self.state['dataset_hash'],self.run_id)
            completed_now=0
            for case in self.cases:
                record=self.state['cases'].setdefault(case['id'],{'turns':[],'observation':None})
                if record['observation']:continue
                while len(record['turns'])<sum(t['role']=='user' for t in case['turns']):
                    body=make_request(case,record['turns'],self.config,self.states,self.run_id)
                    # Remaining current-stage turns are also reserved before optional retries.
                    remaining=sum(sum(t['role']=='user' for t in c['turns'])-len(self.state['cases'].get(c['id'],{}).get('turns',[])) for c in self.cases if not self.state['cases'].get(c['id'],{}).get('observation'))
                    attempts=record.get('current_attempts',[]);raw=record.get('current_raw');stop=None
                    previous_code=attempts[-1].get('code') if attempts else None
                    should_retry=not attempts or previous_code in TRANSIENT
                    if previous_code in STOP_CODES or previous_code in {'REDIRECT_BLOCKED','STALE_RESPONSE_ENVELOPE','RESPONSE_VERSION_MISMATCH','REMOTE_ATTESTATION_MISMATCH'}:stop=previous_code
                    retry_range=range(len(attempts),3) if raw is None and should_retry and not stop else []
                    for retry in retry_range:
                        mandatory=sum(self.config['mandatory_reserve'].values())+max(0,remaining*3-len(attempts)-1)
                        cost_reserve=self.config.get('mandatory_cost_reserve_usd',sum(self.config['mandatory_reserve'].values())*.01)
                        try:aid=self.budget.reserve(self.run_id,mandatory,cost_reserve)
                        except RunnerError as error:self.state['stop_code']=str(error);self.save();return self.summary()
                        self.state['pending']={'attempt_id':aid,'case_id':case['id'],'turn':len(record['turns']),'retry':retry};self.save()
                        http=self.transport.post(case['role'],body)
                        attempt,raw=parse_attempt(http,body,case['role'],self.config,catalog_ids);attempt['attempt_id']=aid
                        self.budget.finish(aid,attempt);attempts.append(attempt)
                        # Journal after every response, before any retry. Interrupted uncertain requests are never replayed.
                        self.state['pending']=None;record['current_attempts']=attempts;record['current_raw']=raw;self.save()
                        if raw is not None:break
                        code=attempt.get('code','UNKNOWN_FAILURE')
                        if code in STOP_CODES or code in {'REDIRECT_BLOCKED','STALE_RESPONSE_ENVELOPE','RESPONSE_VERSION_MISMATCH','REMOTE_ATTESTATION_MISMATCH'}:stop=code;break
                        if code not in TRANSIENT or retry==2:break
                        sleep(min(2**retry,4))
                    turn={'case_id':case['id'],'role':case['role'],'transport':'ok' if raw is not None else 'error','schema_valid':raw is not None,'attempts':attempts,
                          'response':(product_response(raw) if case['role']=='customer' else merchant_response(raw)) if raw is not None else None,'raw_response':raw}
                    record.pop('current_attempts',None);record.pop('current_raw',None);record['turns'].append(turn)
                    if raw is None or len(record['turns'])==sum(t['role']=='user' for t in case['turns']):
                        current={k:v for k,v in turn.items() if k!='raw_response'}
                        current.update(mode=self.config['mode'],run_id=self.run_id,run_fingerprint=self.run_fingerprint,prior_observations=[{k:v for k,v in t.items() if k!='raw_response'} for t in record['turns'][:-1]])
                        record['observation']=current
                    self.state['stop_code']=stop;self.save()
                    if stop:return self.summary()
                    if record['observation']:break
                completed_now+=1
                if max_cases is not None and completed_now>=max_cases:return self.summary()
            self.state['complete']=all(self.state['cases'].get(c['id'],{}).get('observation') for c in self.cases);self.save();return self.summary()
    def summary(self):
        self.state['complete']=all(self.state['cases'].get(c['id'],{}).get('observation') for c in self.cases)
        atomic_json(self.checkpoint,self.state)
        result={'version':VERSION,'run_id':self.run_id,'run_fingerprint':self.run_fingerprint,'mode':self.config['mode'],'cases_expected':len(self.cases),'cases_recorded':sum(bool(v.get('observation')) for v in self.state['cases'].values()),'complete':self.state['complete'],'stop_code':self.state['stop_code'],'budget':self.budget.snapshot(),'product_gates':'not_assessed','remote_source_attestation':bool(self.config.get('require_remote_attestation'))}
        result['transport_success_cases']=sum(v.get('observation',{}).get('transport')=='ok' for v in self.state['cases'].values() if v.get('observation'))
        result['failed_cases']=result['cases_recorded']-result['transport_success_cases']
        result['quality_pass']='not_scored'
        atomic_json(self.out/'summary.json',result);return result


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config',required=True);parser.add_argument('--cases',default='evals/baseline.jsonl');parser.add_argument('--coverage',default='evals/baseline-coverage.json');parser.add_argument('--catalog',default='data/seed/products.json');parser.add_argument('--state-fixtures',required=True);parser.add_argument('--output',required=True);parser.add_argument('--ledger',default='artifacts/private/run-20260921/nl-budget.json');parser.add_argument('--bypass-file');parser.add_argument('--resume',action='store_true');parser.add_argument('--execute',action='store_true');parser.add_argument('--evaluator-holdout',action='store_true');parser.add_argument('--frozen-best');args=parser.parse_args()
    try:
        if ('holdout' in Path(args.cases).parts or 'holdout' in Path(args.cases).name) and not args.evaluator_holdout:raise RunnerError('PROTECTED_HOLDOUT_NOT_AUTHORIZED')
        cases=read_jsonl(args.cases);config=load_json(args.config);coverage=load_json(args.coverage);states=load_json(args.state_fixtures)
        config,ids,protected=check_inputs(cases,config,coverage,args.catalog,states,args.evaluator_holdout,load_json(args.frozen_best) if args.frozen_best else None)
        output=Path(args.output).resolve()
        if protected and not output.is_relative_to(ROOT/'artifacts/private'):raise RunnerError('HOLDOUT_OUTPUT_MUST_BE_PRIVATE')
        plan={'mode':config['mode'],'cases':len(cases),'user_turns':sum(sum(t['role']=='user' for t in c['turns']) for c in cases),'mandatory_reserve':sum(config['mandatory_reserve'].values()),'prior_call_reserve':20,'prior_actual_calls':'unknown','execute_requested':args.execute}
        if not args.execute:print(json.dumps(plan));return 0
        runner=Runner(cases,config,output,Budget(args.ledger),HttpTransport(config['origin'],args.bypass_file),states)
        result=runner.run(ids,resume=args.resume);print(json.dumps(result,ensure_ascii=False));return 0 if result['complete'] and not result['stop_code'] else 2
    except RunnerError as error:print(json.dumps({'status':'STOPPED','code':str(error)}));return 2
    except Exception:print(json.dumps({'status':'STOPPED','code':'INVALID_LOCAL_INPUT_OR_IO'}));return 2
if __name__=='__main__':raise SystemExit(main())
