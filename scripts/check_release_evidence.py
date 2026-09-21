"""G5 public evidence consistency gate. Never calls a model or opens private holdout.
Evidence is attributable, source-bound reporting, not cryptographic proof of truth.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
from pathlib import Path
import re
import statistics
import sys
from datetime import datetime

VERSION = 'G5-evidence-v1'
WORKLOADS = ('clear-1','clear-2','clear-3','ambiguous','reconsent','batch-10','auto-normal','exception-batch')
CORES = {f'CORE-{i:02}' for i in range(1,27)}
RUNTIME_TREES = ('app','src','public','data/seed','data/schema')
RUNTIME_CONFIGS = ('package.json','package-lock.json','tsconfig.json','next.config.mjs','next.config.js','next.config.ts','vercel.json')
ANCHORS = ('app/page.tsx','app/api/product-assistant/route.ts','app/api/merchant-assistant/route.ts','src/domain/engine.ts','src/db/worker.ts','src/db/runtime.ts','src/db/client.ts','src/contracts/domain.ts','src/contracts/assistant.ts','src/server/provider.ts','src/server/prompts.ts','src/server/catalog.ts','src/components/customer/CustomerView.tsx','src/components/merchant/MerchantView.tsx','src/components/demo/AppShell.tsx','public/demo/seed.sqlite','public/demo/sql-wasm.wasm','public/demo/catalog.json','public/demo/manifest.json','data/seed/products.json','data/seed/config.json','package.json','package-lock.json','tsconfig.json','vercel.json')
FORBIDDEN_KEYS = {'api_key','apikey','openai_api_key','authorization','cookie','set-cookie','bypass_token','bypass_secret','x-vercel-protection-bypass','expected','expected_prior','case_results','utterance','utterances','turns','raw_response','raw_responses','observations'}
EVAL_SOURCES = ('scripts/run_nl_eval.py','evals/adapter.py','evals/scorer.py','evals/taxonomy.json','evals/manifest.json','evals/validation.jsonl','evals/validation-coverage.json','package.json')
SCORER_KEYS = {'version','mode','live_evidence','dataset_hash','cases','passed','incomplete','mandatory_errors','fatal_errors','metrics','outbound_attempts','tokens_known','usage_unknown_attempts','latency_p50_ms','latency_p95_ms','nl_minimum_pass','product_gates','run_id','run_fingerprint','catalog_hash','evaluation_scope','frozen_stage_coverage_verified','stage_ready'}

class EvidenceError(Exception): pass

def require(condition, code):
    if not condition: raise EvidenceError(code)

def digest(data): return hashlib.sha256(data).hexdigest()
def fingerprint(value): return digest(json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False).encode())
def sha(value): return isinstance(value,str) and re.fullmatch('[0-9a-f]{64}',value) is not None
def integer(value, minimum=0): return type(value) is int and value>=minimum
def finite(value): return type(value) in (int,float) and math.isfinite(value) and value>=0

def interval_union(network):
    intervals=[]
    for n in network:
        require(all(finite(n.get(k)) for k in ('start','end','networkStart','networkEnd','budgetInstrumentationMs')),'UX_NETWORK_INTERVAL_REQUIRED')
        require(n['start']<=n['networkStart']<=n['networkEnd']<=n['end'],'UX_NETWORK_INTERVAL_INVALID')
        intervals.append((n['networkStart'],n['networkEnd']))
    total=0;end=0
    for a,b in sorted(intervals):total+=max(0,b-max(a,end));end=max(end,b)
    return total

def timestamp(value):
    require(isinstance(value,str),'TIMESTAMP_REQUIRED')
    try: result=datetime.fromisoformat(value.replace('Z','+00:00'))
    except ValueError: raise EvidenceError('INVALID_TIMESTAMP')
    require(result.tzinfo is not None,'TIMESTAMP_ZONE_REQUIRED')
    return result

def sanitized(value):
    if isinstance(value,dict):
        for key,item in value.items():
            require(key.lower() not in FORBIDDEN_KEYS,'SECRET_OR_CASE_CONTENT_FORBIDDEN')
            sanitized(item)
    elif isinstance(value,list):
        for item in value: sanitized(item)
    elif isinstance(value,str):
        require(not re.search(r'(?i)(?:sk-(?:proj-|svcacct-)?[a-z0-9_-]{20,}|Bearer\s+[a-z0-9._-]{12,}|x-vercel-protection-bypass[=:]|[?&](?:token|bypass|secret)=)',value),'SECRET_VALUE_FORBIDDEN')

def relative(root, name, evidence=False):
    root=Path(root).resolve()
    require(isinstance(name,str) and name and '\\' not in name,'INVALID_PATH')
    p=Path(name)
    require(not p.is_absolute() and '..' not in p.parts and all(not x.startswith('.') for x in p.parts),'UNSAFE_PATH')
    require(not any(x.lower() in {'private','secrets'} for x in p.parts),'PRIVATE_PATH_FORBIDDEN')
    if evidence:
        require(name.startswith(('quality/release/evidence/','docs/execution/')) and p.suffix in {'.json','.md'},'PUBLIC_EVIDENCE_PATH_REQUIRED')
    target=root/p
    require(target.is_file() and not target.is_symlink(),'MISSING_OR_SYMLINK_FILE')
    require(target.resolve().is_relative_to(root.resolve()),'PATH_ESCAPE')
    # A symlink in an ancestor must not substitute an unreviewed/private artifact.
    require(not any(parent.is_symlink() for parent in [target,*target.parents] if parent.is_relative_to(root)),'SYMLINK_PATH_FORBIDDEN')
    return target

def runtime_files(root):
    for anchor in ANCHORS: relative(root,anchor)
    require(any((root/name).is_file() for name in ('next.config.mjs','next.config.js','next.config.ts')),'NEXT_CONFIG_REQUIRED')
    paths=set(name for name in RUNTIME_CONFIGS if (root/name).is_file())
    for tree in RUNTIME_TREES:
        folder=root/tree
        require(folder.is_dir(),'RUNTIME_TREE_MISSING')
        for p in folder.rglob('*'):
            require(not p.is_symlink(),'RUNTIME_SYMLINK_FORBIDDEN')
            if p.is_file(): paths.add(p.relative_to(root).as_posix())
    return {name:digest(relative(root,name).read_bytes()) for name in sorted(paths)}

class Checker:
    def __init__(self,root): self.root=Path(root).resolve(); self.checked=set()
    def artifact(self,ref,json_required=True):
        require(isinstance(ref,dict) and set(ref)=={'path','sha256'} and sha(ref['sha256']),'ARTIFACT_REFERENCE_REQUIRED')
        p=relative(self.root,ref['path'],True);data=p.read_bytes()
        require(digest(data)==ref['sha256'],'ARTIFACT_HASH_MISMATCH'); self.checked.add(ref['path'])
        if not json_required:
            sanitized(json.loads(data) if p.suffix=='.json' else data.decode());return data.decode()
        require(p.suffix=='.json','JSON_ARTIFACT_REQUIRED')
        value=json.loads(data);sanitized(value);return value
    def binding(self,ref,candidate,current=True):
        b=self.artifact(ref)
        require(set(b)=={'runner','config','state_fixtures_hash'} and b['runner']=='E02-v1' and sha(b['state_fixtures_hash']),'RUN_BINDING_REQUIRED')
        c=b['config'];require(c.get('mode')=='live','BINDING_NOT_LIVE')
        for source,target in ([('model','model'),('prompt_version','promptVersion'),('prompt_hash','promptHash'),('catalog_hash','catalogHash'),('source_sha','sourceSha')] if current else []):
            require(c.get(source)==candidate[target],'CANDIDATE_BINDING_MISMATCH')
        require(isinstance(c.get('source_files'),dict) and c['source_files'],'SOURCE_BINDING_REQUIRED')
        for name,value in c['source_files'].items():
            require(sha(value),'SOURCE_HASH_REQUIRED')
            if current: require(value==digest(relative(self.root,name).read_bytes()),'STALE_CANDIDATE_SOURCE')
        for name in list(EVAL_SOURCES)+['src/server/provider.ts','src/server/prompts.ts','src/server/catalog.ts','src/contracts/assistant.ts','app/api/product-assistant/route.ts','app/api/merchant-assistant/route.ts','data/seed/products.json','package-lock.json']:
            require(sha(c['source_files'].get(name)),'CANDIDATE_REQUIRED_SOURCE_MISSING')
            if current:require(c['source_files'][name]==digest(relative(self.root,name).read_bytes()),'STALE_CANDIDATE_SOURCE')
        return fingerprint(b)
    def nl(self,bundle,dataset,best,candidate):
        r=self.artifact(bundle['report']);e=self.artifact(bundle['execution'])
        require(set(r)<=SCORER_KEYS,'NON_AGGREGATE_REPORT_FORBIDDEN')
        require(r.get('version')=='EVAL-20260921-v1' and r.get('mode')=='live' and r.get('live_evidence') is True,'NL_NOT_LIVE')
        require(r.get('cases')==dataset['cases'] and r.get('dataset_hash')==dataset['hash'],'NL_DATASET_MISMATCH')
        require(r.get('frozen_stage_coverage_verified') is True and r.get('evaluation_scope')=='frozen_stage','FROZEN_COVERAGE_REQUIRED')
        require(r.get('fatal_errors')==[],'NL_FATAL_ERRORS')
        require(isinstance(r.get('run_id'),str) and r['run_id'] and sha(r.get('run_fingerprint')),'NL_RUN_ID_REQUIRED')
        for key in ('passed','incomplete','mandatory_errors','outbound_attempts','tokens_known','usage_unknown_attempts'):
            require(integer(r.get(key)),'NL_COUNTS_REQUIRED')
        require(r['passed']+r['incomplete']<=r['cases'] and r['outbound_attempts']>0,'NL_COUNTS_INCONSISTENT')
        require(e.get('mode')=='live' and e.get('run_id')==r['run_id'] and e.get('run_fingerprint')==r['run_fingerprint'] and e.get('dataset_hash')==r['dataset_hash'],'EXECUTION_ID_MISMATCH')
        require(e.get('cases_expected')==r['cases'] and e.get('cases_recorded')==r['cases'] and e.get('attempted_cases')==r['cases'],'FULL_CASE_ATTEMPTS_REQUIRED')
        require(e.get('provider_called_count')==r['outbound_attempts'] and integer(e.get('unknown_provider_count')) and e.get('pending_attempts')==0,'PROVIDER_EVIDENCE_REQUIRED')
        require(integer(e.get('provider_not_called_count')) and integer(e.get('outbound_http_attempts')) and e['outbound_http_attempts']==e['provider_called_count']+e['provider_not_called_count']+e['unknown_provider_count'],'HTTP_PROVIDER_DENOMINATOR_MISMATCH')
        require(timestamp(e['finished_at'])>=timestamp(e['started_at']),'EXECUTION_TIME_INVALID')
        metrics=r.get('metrics');require(isinstance(metrics,dict) and metrics,'NL_METRICS_REQUIRED')
        split_names={'dev','validation'} if r['cases']==336 else ({'holdout'} if bundle.get('role')=='holdout_aggregate' else {'validation'})
        clear_uncertain=[]
        for role in ('customer','merchant'):
            for split in split_names:
                for category in [f'category:{"C" if role=="customer" else "M"}{i:02}' for i in range(1,10)]+['clear','uncertain']:
                    key=f'{role}/{split}/{category}';m=metrics.get(key)
                    require(isinstance(m,dict) and integer(m.get('cases'),1) and integer(m.get('passed')) and integer(m.get('complete')) and integer(m.get('mandatory_errors')),'NL_CATEGORY_COVERAGE_REQUIRED')
                    require(m['passed']<=m['complete']<=m['cases'],'NL_BUCKET_COUNTS_INVALID')
                    if category.startswith('category:'):require(m['cases']==dataset['counts'].get(f'{role}/{split}/{category[9:]}'),'NL_FROZEN_CATEGORY_COUNTS')
                    require(m.get('accuracy_all_cases')==m['passed']/m['cases'],'NL_BUCKET_RATE_MISMATCH')
                    if category in ('clear','uncertain'):
                        clear_uncertain.append(m)
                        if best: require(m['passed']/m['cases']>=({'clear':.95,'uncertain':.9}[category]),'NL_MINIMUM_FAILED')
                buckets=[metrics[f'{role}/{split}/category:{"C" if role=="customer" else "M"}{i:02}'] for i in range(1,10)]
                groups=[metrics[f'{role}/{split}/{g}'] for g in ('clear','uncertain')]
                for field in ('cases','passed','complete','mandatory_errors'):
                    require(sum(x[field] for x in buckets)==sum(x[field] for x in groups),'NL_CATEGORY_TOTAL_MISMATCH')
        require(sum(m['cases'] for m in clear_uncertain)==r['cases'] and sum(m['passed'] for m in clear_uncertain)==r['passed'] and sum(m['complete'] for m in clear_uncertain)==r['cases']-r['incomplete'] and sum(m['mandatory_errors'] for m in clear_uncertain)==r['mandatory_errors'],'NL_GLOBAL_TOTAL_MISMATCH')
        if best:
            require(r.get('stage_ready') is True and r.get('nl_minimum_pass') is True and r['incomplete']==0 and r['mandatory_errors']==0,'NL_STAGE_NOT_READY')
            require(e.get('candidate_id')==candidate['id'] and e.get('runtime_hash')==self.runtime_hash and e.get('source_sha')==candidate['sourceSha'] and r.get('catalog_hash')==candidate['catalogHash'],'STALE_NL_CANDIDATE')
            require(e.get('stop_code') is None,'NL_EXECUTION_UNCERTAIN')
            require(r['run_fingerprint']==self.binding(bundle['binding'],candidate),'RUN_FINGERPRINT_MISMATCH')
        else:require(r['run_fingerprint']==self.binding(bundle['binding'],candidate,False),'BASELINE_RUN_FINGERPRINT_MISMATCH')
        return r,e
    def ux(self,ref,best,candidate):
        v=self.artifact(ref);require(v.get('mode')=='live' and v.get('stage')==('best' if best else 'baseline'),'UX_NOT_LIVE')
        require(v.get('stopCode') is None and v.get('unknownProviderCalls')==0 and v.get('complete') is True,'UX_INCOMPLETE')
        for key in ('workloadHash','seedHash','authorizationHash'): require(sha(v.get(key)),'UX_FINGERPRINT_REQUIRED')
        require(isinstance(v.get('runId'),str) and v['runId'],'UX_RUN_ID_REQUIRED')
        ws=v.get('workloads');require(isinstance(ws,list) and len(ws)==8 and {w.get('id') for w in ws}==set(WORKLOADS),'UX_WORKLOAD_SET')
        require(integer(v.get('clock'),1) and isinstance(v.get('harnessHashes'),dict) and all(sha(v['harnessHashes'].get(k)) for k in ('run.mts','seed.mts','metrics.mjs','live.mts','budget_bridge.py')),'UX_HARNESS_BINDING_REQUIRED')
        for w in ws:
            require(w.get('viewport')==({'width':390,'height':844} if w['id'] in WORKLOADS[:5] else {'width':1440,'height':900}),'UX_VIEWPORT_MISMATCH')
        rows=v.get('runs');require(isinstance(rows,list) and len(rows)==24,'UX_RAW_DENOMINATOR')
        require({(r.get('workload'),r.get('repetition')) for r in rows}=={(w,n) for w in WORKLOADS for n in (1,2,3)},'UX_DUPLICATE_OR_MISSING_RUN')
        require(integer(v.get('modelCalls'),18) and v.get('outboundAttempts')==v['modelCalls'] and isinstance(v.get('liveUsage'),list) and len(v['liveUsage'])==v['modelCalls'],'UX_PROVIDER_COUNT')
        require(len({i.get('attemptId') for i in v['liveUsage']})==v['modelCalls'] and all(i.get('attemptId') for i in v['liveUsage']),'UX_DUPLICATE_PROVIDER_ATTEMPT')
        for item in v['liveUsage']:
            require(item.get('provider_called') is True and isinstance(item.get('usage'),dict) and item.get('status')=='ok','UX_PROVIDER_EVIDENCE')
            u=item['usage'];require(all(integer(u.get(k)) for k in ('input_tokens','output_tokens','total_tokens')) and u['total_tokens']==u['input_tokens']+u['output_tokens'] and finite(item.get('cost_usd')),'UX_UNKNOWN_USAGE_OR_COST')
        network=[n for r in rows for n in r.get('network',[])]
        require(len(network)==v['modelCalls'] and {n.get('attemptId') for n in network}=={i['attemptId'] for i in v['liveUsage']},'UX_NETWORK_PROVIDER_MISMATCH')
        require(all(n.get('mode')=='live' and n.get('observation',{}).get('provider_called') is True for n in network),'UX_NETWORK_NOT_LIVE')
        result={}
        for w in WORKLOADS:
            group=[r for r in rows if r['workload']==w]
            for r in group:
                require(r.get('status')=='PASS' and not r.get('setupFailed') and not r.get('pageErrors') and sha(r.get('durableHash')) and r.get('observedClock')==v.get('clock'),'UX_CORRECTNESS_FAILED')
                for k in ('activations','screenTransitions','questions','merchantPerOrderApprovals'):require(integer(r.get(k)),'UX_ACTION_COUNT')
                for k in ('elapsedMs','modelNetworkMs','nonModelMs','budgetInstrumentationMs'):require(finite(r.get(k)),'UX_TIME_REQUIRED')
                require(r['modelNetworkMs']+r['budgetInstrumentationMs']<=r['elapsedMs']+.001 and abs(r['nonModelMs']-(r['elapsedMs']-r['modelNetworkMs']-r['budgetInstrumentationMs']))<.001,'UX_TIME_ACCOUNTING')
                require(abs(interval_union(r.get('network',[]))-r['modelNetworkMs'])<.001 and abs(sum(n['budgetInstrumentationMs'] for n in r.get('network',[]))-r['budgetInstrumentationMs'])<.001,'UX_NETWORK_AGGREGATE_MISMATCH')
                require(r['questions']<=2,'UX_QUESTION_LIMIT')
                if w.startswith('clear-'):require(r['activations']-1<=7 and r['questions']<=2,'UX_ABSOLUTE_CUSTOMER')
                if w=='batch-10':require(r['screenTransitions']==0 and r['merchantPerOrderApprovals']==1,'UX_ABSOLUTE_BATCH')
                if w=='auto-normal':require(r['merchantPerOrderApprovals']==0 and str(r.get('unchangedReviewCheck','')).startswith('PASS'),'UX_ABSOLUTE_AUTO')
            result[w]={'actions':max(r['activations'] for r in group),'screens':max(r['screenTransitions'] for r in group),'median':statistics.median(r['nonModelMs'] for r in group)}
        if best:
            require(v.get('runtimeHash')==self.runtime_hash and v.get('candidateId')==candidate['id'],'STALE_UX_RUNTIME')
            for name in ['src/domain/engine.ts','src/contracts/domain.ts']:
                require(v.get('seedEngineBinding',{}).get(name)==self.files[name],'UX_SEED_ENGINE_BINDING')
            required=['app/page.tsx','src/components/demo/AppShell.tsx','src/components/customer/CustomerView.tsx','src/components/merchant/MerchantView.tsx','src/db/worker.ts','src/db/runtime.ts','src/db/client.ts']
            source=v.get('sourceFiles',{})
            require(all(name in source for name in required),'UX_REQUIRED_SOURCE_MISSING')
            require(all(name in self.files and value==self.files[name] for name,value in source.items()),'STALE_UX_SOURCE')
        return v,result
    def qa(self,ref,candidate):
        q=self.artifact(ref);require(q.get('scope')=='G5' and q.get('provider')=='openai' and isinstance(q.get('coverage'),list) and q['coverage'] and set(q['coverage'])<=CORES,'QA_SCOPE_MISSING')
        require(q.get('status')=='PASS' and q.get('mode')=='live' and q.get('actual_browser') is True and q.get('actual_sql') is True and integer(q.get('provider_calls'),1),'QA_NOT_LIVE_BROWSER_SQL')
        require(q.get('runtime_hash')==self.runtime_hash and q.get('candidate_id')==candidate['id'],'STALE_QA')
        require(isinstance(q.get('reviewer'),str) and q['reviewer'] and isinstance(q.get('implementers'),list) and q['implementers'] and q['reviewer'] not in q['implementers'],'QA_NOT_INDEPENDENT')
        require(q.get('failures')==0 and q.get('mandatory_errors')==0 and integer(q.get('checks_executed'),1),'QA_FAILURES')
        require(q.get('evidence'),'QA_REPORT_REQUIRED')
        for ref in q['evidence']:self.artifact(ref,False)
        return q
    def check(self,manifest):
        manifest=Path(manifest)
        manifest=manifest.parent.resolve()/manifest.name
        require(manifest.resolve().is_relative_to(self.root),'UNSAFE_MANIFEST_PATH')
        m=json.loads(relative(self.root,manifest.relative_to(self.root).as_posix()).read_text());sanitized(m)
        require(m.get('version')==VERSION and m.get('scope')=='G5' and m.get('g6_status')=='pending','WRONG_GOAL_SCOPE')
        require(isinstance(m.get('versions'),dict) and all(isinstance(m['versions'].get(k),str) and m['versions'][k] for k in ('research','catalog','scenario','eval','seed','policy','prompt','model','context')),'VERSION_CONTEXT_REQUIRED')
        self.files=runtime_files(self.root);self.runtime_hash=fingerprint(self.files)
        require(m.get('runtime',{}).get('files')==self.files and m['runtime'].get('sha256')==self.runtime_hash,'RUNTIME_SET_OR_HASH_MISMATCH')
        candidate=m['candidate'];require(isinstance(candidate.get('model'),str) and candidate['model'] and isinstance(candidate.get('promptVersion'),str) and candidate['promptVersion'],'CANDIDATE_MODEL_REQUIRED')
        require(candidate.get('runtimeHash')==self.runtime_hash and candidate.get('id') and sha(candidate.get('promptHash')) and sha(candidate.get('catalogHash')) and re.fullmatch('[0-9a-f]{40}',candidate.get('sourceSha','')),'CANDIDATE_REQUIRED')
        require(candidate['promptHash']==self.files['src/server/prompts.ts'],'CANDIDATE_PROMPT_STALE')
        catalog=json.loads(relative(self.root,'data/seed/products.json').read_text())
        require(candidate['catalogHash']==digest(json.dumps(catalog,ensure_ascii=False,separators=(',',':')).encode()),'CANDIDATE_CATALOG_STALE')
        freeze=timestamp(candidate['frozenAt'])
        d=m['datasets']
        for name,count in [('baseline',336),('validation',84),('holdout',84)]:require(d.get(name,{}).get('cases')==count and sha(d[name].get('hash')),'FROZEN_DATASET_REQUIRED')
        require(set(d)=={'baseline','validation','holdout'} and len({x['hash'] for x in d.values()})==3,'DATASET_SPLITS_NOT_DISTINCT')
        public_manifest=json.loads(relative(self.root,'evals/manifest.json').read_text())
        require(public_manifest.get('holdout_access')=='evaluator_only' and public_manifest.get('catalog_hash')==candidate['catalogHash'],'EVAL_MANIFEST_MISMATCH')
        for name in ('baseline','validation','holdout'):
            frozen=(public_manifest['splits']['holdout'] if name=='holdout' else json.loads(relative(self.root,f'evals/{name}-coverage.json').read_text()))
            require(d[name]=={'hash':frozen['dataset_hash'],'cases':frozen['cases'],'counts':frozen['counts']},'FROZEN_DATASET_MISMATCH')
        b,_=self.nl(m['nl']['baseline'],d['baseline'],False,candidate)
        validations=m['nl']['validation'];require(isinstance(validations,list) and len(validations)==2,'TWO_VALIDATIONS_REQUIRED')
        first,e1=self.nl(validations[0],d['validation'],True,candidate);second,e2=self.nl(validations[1],d['validation'],True,candidate)
        require(first['run_id']!=second['run_id'] and first['run_fingerprint']==second['run_fingerprint'],'VALIDATION_REPEAT_MISMATCH')
        h=m['nl']['holdout'];require(h.get('role')=='holdout_aggregate','HOLDOUT_AGGREGATE_ONLY')
        hold,he=self.nl(h,d['holdout'],True,candidate)
        require(len({b['run_id'],first['run_id'],second['run_id'],hold['run_id']})==4,'DUPLICATE_NL_RUN')
        require(timestamp(he['started_at'])>=max(freeze,timestamp(e1['finished_at']),timestamp(e2['finished_at'])),'HOLDOUT_BEFORE_BEST_FROZEN')
        ha=self.artifact(h['independent_report']);require(ha.get('role')=='holdout_evaluator' and ha.get('status')=='PASS' and ha.get('run_id')==hold['run_id'] and ha.get('candidate_id')==candidate['id'] and ha.get('runtime_hash')==self.runtime_hash and ha.get('protected_content_not_published') is True,'HOLDOUT_INDEPENDENT_ATTESTATION')
        require(ha.get('reviewer') and isinstance(ha.get('implementers'),list) and ha['implementers'] and ha['reviewer'] not in ha['implementers'],'HOLDOUT_NOT_INDEPENDENT')
        ub,bs=self.ux(m['ux']['baseline'],False,candidate);uv,vs=self.ux(m['ux']['best'],True,candidate)
        require(ub['runId']!=uv['runId'] and all(ub.get(k)==uv.get(k) for k in ('workloadHash','seedHash','clock','workloads','harnessHashes')),'UX_COMPARISON_MISMATCH')
        require(all(vs[w]['actions']<=bs[w]['actions'] and vs[w]['screens']<=bs[w]['screens'] and vs[w]['median']<=bs[w]['median']*1.1 for w in WORKLOADS),'UX_REGRESSION')
        qs=[self.qa(r,candidate) for r in m['role_qa']]
        require(len(qs)==2 and {q.get('role') for q in qs}=={'customer','merchant'} and len({q['reviewer'] for q in qs})==2,'TWO_DISTINCT_ROLE_QA_REQUIRED')
        policies=[self.artifact(r) for r in m['policy_reviews']]
        require(len(policies)==2 and len({p.get('reviewer') for p in policies})==2 and len({p.get('perspective') for p in policies})==2,'TWO_POLICY_PERSPECTIVES_REQUIRED')
        for p in policies:
            require(p.get('scope')=='G5' and p.get('reviewer') and p.get('perspective') and p.get('status')=='PASS' and p.get('unresolved_major')==0 and p.get('runtime_hash')==self.runtime_hash and p.get('candidate_id')==candidate['id'],'POLICY_UNRESOLVED_OR_STALE')
            require(p.get('evidence'),'POLICY_REPORT_REQUIRED')
            for ref in p['evidence']:self.artifact(ref,False)
        coverage=m['core_coverage'];require(set(coverage)==CORES,'CORE_COVERAGE_MISSING')
        for core,entry in coverage.items():
            require(entry.get('status')=='PASS' or (core=='CORE-13' and entry.get('status')=='G6_PENDING'),'CORE_NOT_READY')
            require(entry.get('scope')=='G5' and entry.get('evidence'),'CORE_SCOPE_OR_EVIDENCE_MISSING')
            for ref in entry['evidence']:self.artifact(ref,False)
        preview=self.artifact(m['preview']);require(preview.get('readyState')=='READY' and preview.get('target') in (None,'preview') and preview.get('id') and preview.get('url') and preview.get('gitSource',{}).get('sha')==candidate['sourceSha'],'PREVIEW_REVISION_MISMATCH')
        require(m.get('independent_evidence_review'),'EVIDENCE_REVIEW_REQUIRED');review=self.artifact(m['independent_evidence_review'])
        require(review.get('status')=='PASS' and review.get('runtime_hash')==self.runtime_hash and review.get('candidate_id')==candidate['id'] and isinstance(review.get('implementers'),list) and review['implementers'] and review.get('reviewer') not in review['implementers'] and review.get('reviewer'),'EVIDENCE_REVIEW_NOT_INDEPENDENT')
        return {'version':VERSION,'status':'PASS','scope':'G5','g6_status':'pending','runtime_hash':self.runtime_hash,'artifacts_checked':len(self.checked),'truth_limit':'Hash and independent report consistency; not cryptographic proof that executions occurred.'}

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1]);ap.add_argument('--manifest',default='quality/release/manifest.json');args=ap.parse_args()
    try:
        name=Path(args.manifest);require(not name.is_absolute() and '..' not in name.parts,'UNSAFE_MANIFEST_PATH');manifest=args.root/name
        require(manifest.is_file(),'NOT_READY_MANIFEST_MISSING')
        result=Checker(args.root).check(manifest)
    except (EvidenceError,KeyError,TypeError,ValueError,OSError) as error:
        code=str(error) if isinstance(error,EvidenceError) else 'MALFORMED_OR_UNREADABLE_EVIDENCE'
        result={'version':VERSION,'status':'NOT_READY','scope':'G5','code':code};print(json.dumps(result));return 1
    print(json.dumps(result));return 0
if __name__=='__main__':sys.exit(main())
