"""ADR-008 deterministic public-oracle correction. No network or protected data.
Original live artifacts are immutable; derived scores never rewrite execution identity.
"""
from __future__ import annotations
import copy, hashlib, json, re, sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'evals'))
from scorer import evaluate, fingerprint, read_jsonl, validate_dataset

KIND='derived_public_oracle_rescore'
REVISION='public-oracle-v4'
SLOTS={'C02-validation-007':('expected',), 'C06-validation-006':('expected_prior',0)}
PAIR=['DEMO-778B67C87CCC','DEMO-6AFC6A69B100']
SOURCE_EXCEPTIONS={'scripts/check_release_evidence.py','scripts/run_nl_eval.py'}
OBS_KEYS={'case_id','role','transport','schema_valid','attempts','response','mode','run_id','run_fingerprint','prior_observations','domain_violations','prior_responses'}
RESPONSE_KEYS={'action','candidate_ids','alternative_ids','confirmed_sku','confirmation_required','question','raw_kind_valid','command','forbidden_actions'}
ATTEMPT_KEYS={'http_status','latency_ms','provider_called','status','usage','cost_usd','code','diagnostic','attempt_id'}

def need(ok,code):
    if not ok: raise ValueError('ORACLE_V4_'+code)
def digest(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ref(root,p):
    p=Path(p);return {'path':p.relative_to(root).as_posix(),'sha256':digest(p)}
def public_path(root,value):
    root=Path(root).resolve();need(type(value)is str and not Path(value).is_absolute() and '..' not in Path(value).parts,'PUBLIC_PATH')
    raw=root/value;need(not any(v.is_symlink() for v in [raw,*raw.parents] if v.is_relative_to(root)),'SYMLINK')
    p=raw.resolve();need(p.is_relative_to(root) and 'private' not in p.parts and Path(value).parts[0] in {'evals','quality','docs'},'PUBLIC_PATH')
    return p

def artifact(root,r):
    need(isinstance(r,dict) and set(r)=={'path','sha256'},'REFERENCE')
    p=public_path(root,r['path']);need(digest(p)==r['sha256'],'HASH');return json.loads(p.read_text())

def rows(root,r):
    need(isinstance(r,dict) and set(r)=={'path','sha256'},'REFERENCE')
    p=public_path(root,r['path']);need(r['path'] in {'evals/baseline.jsonl','evals/validation.jsonl','evals/revisions/public-oracle-v4/baseline.jsonl','evals/revisions/public-oracle-v4/validation.jsonl'},'PUBLIC_DATASET_PATH')
    need(digest(p)==r['sha256'],'DATA_HASH');v=read_jsonl(p);need(all(x['split'] in {'dev','validation'} for x in v),'PROTECTED_DATA');return v

def corrected(cases):
    result=copy.deepcopy(cases)
    for c in result:
        if c['id'] in SLOTS:
            slot=c
            for key in SLOTS[c['id']]:slot=slot[key]
            for field in ('required_any_skus','candidate_pool'):
                need(slot[field]==PAIR[:1],'ORIGINAL_ORACLE');slot[field]=PAIR[:]
    return result

def typed_values(o):
    import math
    def enum(v,values):need(type(v)is str and v in values,'VALUE_ENUM')
    def boolean(v):need(type(v)is bool,'VALUE_BOOLEAN')
    def number(v):need(type(v)in (int,float) and math.isfinite(v) and v>=0,'VALUE_NUMBER')
    def sku(v):need(type(v)is str and re.fullmatch(r'DEMO-[0-9A-F]{12}',v),'VALUE_SKU')
    def array(v,validator):need(type(v)is list,'VALUE_ARRAY');[validator(x) for x in v]
    for key,pattern in [('case_id',r'[CM]0[1-9]-(dev|validation)-[0-9]{3}'),('run_id',r'[0-9a-f]{8}-[0-9a-f-]{27}'),('run_fingerprint',r'[0-9a-f]{64}')]:
        if key in o:need(type(o[key])is str and re.fullmatch(pattern,o[key]),'VALUE_ID')
    if 'role' in o:enum(o['role'],{'customer','merchant'})
    if 'transport' in o:enum(o['transport'],{'ok','error'})
    if 'mode' in o:enum(o['mode'],{'live'})
    if 'schema_valid' in o:boolean(o['schema_valid'])
    r=o.get('response')
    need(r is None or type(r)is dict,'VALUE_RESPONSE')
    if r is not None:
        if 'action' in r:enum(r['action'],{'candidates','clarify','unidentified','reject','propose','execute','invalid'})
        for k in ('raw_kind_valid','confirmation_required'):
            if k in r:boolean(r[k])
        for k in ('candidate_ids','alternative_ids'):
            if k in r:array(r[k],sku)
        if r.get('confirmed_sku') is not None:sku(r['confirmed_sku'])
        if 'command' in r:
            c=r['command'];need(type(c)is dict and set(c)=={'intent','scope','constraints'},'VALUE_COMMAND');enum(c['intent'],{'modify','restore','clarify'});enum(c['scope'],{'current_proposal','policy','clarify'})
            z=c['constraints'];need(type(z)is dict and set(z)<={'budgetLimitKrw','maxQuantity','restorePrevious','excludeProductIds','excludeCategories'},'VALUE_CONSTRAINTS')
            for k in ('budgetLimitKrw','maxQuantity'):
                if k in z:need(type(z[k])is int and 0<=z[k]<=10**12,'VALUE_INTEGER')
            if 'restorePrevious' in z:boolean(z['restorePrevious'])
            if 'excludeProductIds' in z:array(z['excludeProductIds'],sku)
            if 'excludeCategories' in z:
                allowed={x['category'] for x in json.loads((Path(__file__).resolve().parents[1]/'data/seed/products.json').read_text())}
                array(z['excludeCategories'],lambda x:enum(x,allowed))
    need(type(o.get('attempts',[]))is list,'VALUE_ATTEMPTS')
    for a in o.get('attempts',[]):
        need(type(a)is dict,'VALUE_ATTEMPT')
        if 'http_status' in a:need(a['http_status'] is None or type(a['http_status'])is int and 0<=a['http_status']<=599,'VALUE_HTTP')
        if 'provider_called' in a:need(a['provider_called'] is None or type(a['provider_called'])is bool,'VALUE_PROVIDER')
        if 'status' in a:enum(a['status'],{'ok','failed','error','timeout'})
        for k in ('latency_ms','cost_usd'):
            if a.get(k) is not None:number(a[k])
        if a.get('usage') is not None:
            u=a['usage'];need(type(u)is dict and set(u)=={'input_tokens','output_tokens','total_tokens'} and all(type(x)is int and x>=0 for x in u.values()) and u['input_tokens']+u['output_tokens']==u['total_tokens'],'VALUE_USAGE')

def normalize(observation):
    """Keep only scorer inputs and execution accounting; no natural-language strings."""
    need(type(observation)is dict and set(observation)<=OBS_KEYS,'OBSERVATION_KEYS');typed_values(observation)
    o=copy.deepcopy(observation)
    if isinstance(o.get('response'),dict):
        r=o['response'];need(set(r)<=RESPONSE_KEYS,'RESPONSE_KEYS')
        if 'question' in r:
            q=r.pop('question');need(q is None or isinstance(q,str),'QUESTION_TYPE')
            r['question_shape']={'truthy':bool(q),'nonempty':bool(str(q or '').strip())}
    for key in ('prior_responses','domain_violations'):
        need(not o.get(key),'UNSUPPORTED_FREE_TEXT_VIOLATION')
    if isinstance(o.get('response'),dict):need(not o['response'].get('forbidden_actions'),'UNSUPPORTED_FREE_TEXT_VIOLATION')
    for a in o.get('attempts',[]):
        need(set(a)<=ATTEMPT_KEYS,'ATTEMPT_KEYS')
        for key in ('diagnostic','code','attempt_id'):a.pop(key,None)
    need(type(o.get('prior_observations',[]))is list,'VALUE_PRIOR')
    o['prior_observations']=[normalize(v) for v in o.get('prior_observations',[])]
    return o

def materialize(o):
    o=copy.deepcopy(o);r=o.get('response')
    if isinstance(r,dict) and 'question_shape' in r:
        q=r.pop('question_shape');need(set(q)=={'truthy','nonempty'} and all(type(x)is bool for x in q.values()) and (q['truthy'] or not q['nonempty']),'QUESTION_SHAPE')
        r['question']='question' if q['nonempty'] else (' ' if q['truthy'] else None)
    o['prior_observations']=[materialize(v) for v in o.get('prior_observations',[])]
    return o


def score(cases,obs,ids,identity,coverage):
    return evaluate(cases,obs,ids,expected_fingerprint=fingerprint(cases),include_cases=True,mode='live',run_id=identity['run_id'],run_fingerprint=identity['run_fingerprint'],catalog_hash=identity['catalog_hash'],coverage_contract=coverage)

def aggregate(report):return {k:v for k,v in report.items() if k!='case_results'}

def revision(root,r):
    root=Path(root);m=artifact(root,r)
    need(m.get('version')=='EVAL-20260922-v4' and m.get('revision_kind')=='public_oracle_correction' and m.get('revision')==REVISION and m.get('status')=='frozen','REVISION')
    need(m['predecessor_manifest']['path']=='evals/manifest-v3.json','PREDECESSOR')
    old=artifact(root,m['predecessor_manifest'])
    for k in ('catalog_hash','catalog_size','total_cases','holdout_access','label_counts','retired_holdouts','archived_cases'):
        need(m[k]==old[k],'UNCHANGED_'+k)
    need(m['splits']['dev']==old['splits']['dev'] and m['splits']['holdout']==old['splits']['holdout'] and m['holdout_frozenAt']==old['frozenAt'],'HOLDOUT_UNCHANGED')
    need(m['correction_slots']=={k:list(v) for k,v in SLOTS.items()} and m['allowed_skus']==PAIR,'PATCH_SCOPE')
    need(m['decision']['path']=='docs/decisions/ADR-008-public-oracle-equivalence.md','DECISION_PATH')
    adr=public_path(root,m['decision']['path']);need(digest(adr)==m['decision']['sha256'] and '- status: adopted' in adr.read_text(),'ADOPTED_DECISION')
    for split,count in [('validation',84),('baseline',336)]:
        entry=m['public_datasets'][split];original=rows(root,entry['original']);new=rows(root,entry['revised']);cov=artifact(root,entry['coverage'])
        need(len(new)==count and corrected(original)==new and len({c['id'] for c in new})==count,'EXACT_ORACLE_DIFF')
        need(set(SLOTS)<={c['id'] for c in original},'SLOT_COVERAGE')
        need(cov['dataset_hash']==fingerprint(new) and cov['cases']==count and cov['counts']==validate_dataset(new)['counts'],'COVERAGE')
        need(cov==dict(json.loads((root/f'evals/{split}-coverage.json').read_text()),dataset_hash=fingerprint(new)),'COVERAGE_UNCHANGED')
    impact=artifact(root,m['protected_independence_review']);need(impact.get('status')=='PASS' and impact.get('reviewer') and impact.get('implementers') and impact['reviewer'] not in impact['implementers'] and impact.get('dataset_hash')==m['splits']['holdout']['dataset_hash'] and impact.get('protected_dataset_changed') is False and impact.get('protected_state_changed') is False and type(impact.get('new_semantic_family_overlap')) is int and impact['new_semantic_family_overlap']==0 and impact.get('protected_content_not_published') is True,'PROTECTED_INDEPENDENCE')
    registry=artifact(root,m['historical_public_runs']);need(len(registry.get('runs',[]))==23 and len({x['run'] for x in registry['runs']})==23,'HISTORICAL_REGISTER')
    need(m['splits']['validation']==artifact(root,m['public_datasets']['validation']['coverage']),'VALIDATION_METADATA')
    return m

def source_compatible(root,original,current=None):
    root=Path(root);files=original['source_files']
    for name,h in files.items():
        if name not in SOURCE_EXCEPTIONS:need(digest(root/name)==h,'APP_OR_SCORER_CHANGED')
    if current is not None:
        for k in ('mode','model','prompt_version','prompt_hash','catalog_version','catalog_hash','api_version'):
            need(original[k]==current[k],'CANDIDATE_IDENTITY')
        need(original.get('max_attempts',3)==current.get('max_attempts',3),'ATTEMPT_LIMIT')
        need(set(files)<=set(current['source_files']),'SOURCE_SET')
        for name,h in current['source_files'].items():need(digest(root/name)==h,'CURRENT_SOURCE')
        need({'evals/manifest-v4.json','scripts/rescore_public_oracle.py'}<=set(current['source_files']),'CURRENT_REVISION_BINDING')

def verify_bundle(root,bundle,current=False,require_review=True):
    from check_release_evidence import SCORER_KEYS,runtime_files
    root=Path(root);need(bundle.get('kind')==KIND,'KIND');m=revision(root,bundle['revision'])
    original=bundle['original'];need(bundle.get('binding')==original['binding'] and bundle.get('execution')==original['execution'],'ORIGINAL_ALIASES');oldreport=artifact(root,original['report']);execution=artifact(root,original['execution']);binding=artifact(root,original['binding'])
    config=binding['config'];identity={k:oldreport[k] for k in ('run_id','run_fingerprint','catalog_hash')}
    need(fingerprint(binding)==identity['run_fingerprint'] and config['mode']=='live','ORIGINAL_BINDING')
    split='baseline' if oldreport['cases']==336 else 'validation';entry=m['public_datasets'][split]
    old=rows(root,entry['original']);new=rows(root,entry['revised']);oldcov=json.loads((root/f'evals/{split}-coverage.json').read_text());newcov=artifact(root,entry['coverage'])
    need(execution['run_id']==identity['run_id'] and execution['run_fingerprint']==identity['run_fingerprint'] and execution['dataset_hash']==oldreport['dataset_hash']==fingerprint(old),'ORIGINAL_EXECUTION')
    n=artifact(root,bundle['normalized']);need(isinstance(n,list),'NORMALIZED_ROWS');obs=[materialize(v) for v in n]
    need([normalize(v) for v in obs]==n,'NORMALIZED_CANONICAL')
    ids={p['sku'] for p in json.loads((root/'data/seed/products.json').read_text())}
    oldscore=score(old,obs,ids,identity,oldcov);newscore=score(new,obs,ids,identity,newcov)
    need({k:oldscore[k] for k in SCORER_KEYS}==oldreport,'ORIGINAL_SCORE_REPLAY')
    derived=artifact(root,bundle['report']);need(derived=={'kind':KIND,'actual_new_calls':0,'score':{k:newscore[k] for k in SCORER_KEYS}},'DERIVED_SCORE')
    for a,b in zip(oldscore['case_results'],newscore['case_results']):
        if a['case_id'] not in SLOTS:need(a==b,'UNRELATED_SCORE_CHANGED')
        need(a['complete']==b['complete'] and a['mandatory']==b['mandatory'],'SAFETY_OR_COMPLETENESS_CHANGED')
    d=artifact(root,bundle['derivation'])
    need(d['original']==original and d['revision']==bundle['revision'] and d['normalized']==bundle['normalized'] and d['report']==bundle['report'] and d['actual_new_calls']==0,'DERIVATION_CHAIN')
    need(d.get('evaluation_source_hashes')=={n:digest(root/n) for n in sorted(SOURCE_EXCEPTIONS)},'EVALUATION_SOURCE_CHANGED')
    need(d['scorer_sha256']==digest(root/'evals/scorer.py') and d['adapter_sha256']==digest(root/'evals/adapter.py') and d['tool_sha256']==digest(root/'scripts/rescore_public_oracle.py'),'TOOL_CHANGED')
    observation_hashes={v for k,v in execution['source_artifact_hashes'].items() if k.endswith('/observations.jsonl')}
    need(d['original_observations_sha256'] in observation_hashes,'ORIGINAL_OBSERVATION_HASH')
    if require_review:
        need(bundle.get('cohort'),'COHORT_REQUIRED')
        verify_cohort(root,bundle['cohort'],bundle['revision'],bundle['independent_review'])
        cohort=artifact(root,bundle['cohort']);need(bundle['derivation'] in [x.get('derivation') for x in cohort['runs']],'COHORT_MEMBERSHIP')
        audit=artifact(root,bundle['independent_review']);need(audit.get('status')=='PASS' and audit.get('reviewer') and audit['reviewer'] not in audit.get('implementers',[]) and audit.get('implementers'),'INDEPENDENT_REVIEW')
        need(digest(root/bundle['derivation']['path']) in audit.get('derivation_sha256',[]) and audit.get('private_full_replay_verified') is True,'PRIVATE_REPLAY_ATTESTATION')
    if current:
        source_compatible(root,config)
        need(execution['runtime_hash']==fingerprint(runtime_files(root)),'RUNTIME_CHANGED')
    return newscore,execution,binding

def lineage(root,reference,old_source,new_source,runtime_hash):
    from check_release_evidence import runtime_files
    a=artifact(root,reference)
    need(a.get('status')=='PASS' and a.get('reviewer') and a.get('implementers') and a['reviewer'] not in a['implementers'],'LINEAGE_REVIEW')
    need(a.get('original_source_sha')==old_source and a.get('current_source_sha')==new_source and a.get('runtime_files')==runtime_files(root) and a.get('runtime_hash')==runtime_hash==fingerprint(a['runtime_files']),'APPLICATION_LINEAGE')
    return a

def prepare(root,private,output_version='revision-02'):
    """One-shot authoring; no overwrite. Independent review is deliberately pending."""
    from datetime import datetime,timezone
    from check_release_evidence import SCORER_KEYS
    root=Path(root).resolve();private=Path(private).resolve()
    need(private==root/'artifacts/private/run-20260921','PRIVATE_SCOPE')
    need(re.fullmatch(r'revision-[0-9]{2}',output_version) is not None,'OUTPUT_VERSION')
    output=root/'quality/release/evidence/oracle-v4'/output_version;need(not output.exists(),'ALREADY_PREPARED')
    dest=root/'evals/revisions/public-oracle-v4'
    def save(p,v):
        need(not p.exists(),'NO_OVERWRITE');p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n');return ref(root,p)
    if (root/'evals/manifest-v4.json').exists():
        mr=ref(root,root/'evals/manifest-v4.json');manifest=revision(root,mr)
    else:
        dest.mkdir(parents=True)
        manifest=copy.deepcopy(json.loads((root/'evals/manifest-v3.json').read_text()))
        manifest.update(version='EVAL-20260922-v4',revision=REVISION,revision_kind='public_oracle_correction',frozenAt=datetime.now(timezone.utc).isoformat(),holdout_frozenAt=manifest['frozenAt'],predecessor_manifest=ref(root,root/'evals/manifest-v3.json'),correction_slots={k:list(v) for k,v in SLOTS.items()},allowed_skus=PAIR,decision=ref(root,root/'docs/decisions/ADR-008-public-oracle-equivalence.md'),public_datasets={})
        for split in ('baseline','validation'):
            old=read_jsonl(root/f'evals/{split}.jsonl');new=corrected(old);p=dest/f'{split}.jsonl';p.write_text(''.join(json.dumps(c,ensure_ascii=False,separators=(',',':'))+'\n' for c in new))
            cov=json.loads((root/f'evals/{split}-coverage.json').read_text());cov['dataset_hash']=fingerprint(new)
            manifest['public_datasets'][split]={'original':ref(root,root/f'evals/{split}.jsonl'),'revised':ref(root,p),'coverage':save(dest/f'{split}-coverage.json',cov)}
            if split=='validation':manifest['splits'][split]=cov
        mr=save(root/'evals/manifest-v4.json',manifest);revision(root,mr)
    registry=artifact(root,manifest['historical_public_runs']);registered={x['run']:x for x in registry['runs']}
    states=json.loads((private/'eval-state.json').read_text());configs=[]
    for f in private.glob('n*config*.json'):
        if 'holdout' in f.name or 'draft' in f.name:continue
        c=json.loads(f.read_text())
        if 'source_files' in c:configs.append((f,c))
    ids={x['sku'] for x in json.loads((root/'data/seed/products.json').read_text())}
    inventory=[];audits=[]
    for file in sorted(private.glob('n*/observations.jsonl')):
        if 'holdout' in file.parent.name:continue
        cp=json.loads((file.parent/'checkpoint.json').read_text());name=file.parent.name
        entry={'run':name,'run_id':cp['run_id'],'run_fingerprint':cp['run_fingerprint'],'dataset_hash':cp['dataset_hash'],'original_observations_sha256':digest(file),'cases':len(cp['cases'])}
        need(entry==registered.get(name),'REGISTER_MISMATCH')
        if len(cp['cases'])==30:
            dev=read_jsonl(private/'n02-c1-dev30.jsonl');need(fingerprint(dev)==cp['dataset_hash'] and set(cp['cases'])=={c['id'] for c in dev} and not set(SLOTS)&set(cp['cases']),'DEV_AFFECTED')
            entry['status']='unchanged_dev_no_corrected_slots';inventory.append(entry);continue
        need(len(cp['cases']) in (84,336),'UNKNOWN_PUBLIC_RUN')
        split='baseline' if len(cp['cases'])==336 else 'validation';original=rows(root,manifest['public_datasets'][split]['original']);new=rows(root,manifest['public_datasets'][split]['revised'])
        obs=read_jsonl(file);normalized=[normalize(o) for o in obs];materialized=[materialize(o) for o in normalized]
        reportpath=private/(name+'-analysis')/('baseline-report.json' if split=='baseline' else 'candidate-report.json');oldreport=json.loads(reportpath.read_text())
        oldcov=json.loads((root/f'evals/{split}-coverage.json').read_text());newcov=artifact(root,manifest['public_datasets'][split]['coverage'])
        oldscore=score(original,obs,ids,cp,oldcov);newscore=score(new,obs,ids,cp,newcov)
        need(all(oldscore[k]==oldreport[k] for k in SCORER_KEYS),'PRIVATE_ORIGINAL_REPLAY')
        need(oldscore==score(original,materialized,ids,cp,oldcov) and newscore==score(new,materialized,ids,cp,newcov),'NORMALIZED_REPLAY')
        existing=None
        for b in (root/'quality/release/evidence').glob('*/bundle.json'):
            if 'holdout' in str(b):continue
            v=json.loads(b.read_text())
            if artifact(root,v['report']).get('run_id')==cp['run_id']:existing=v;break
        folder=output/name
        if existing:
            original_bundle={k:existing[k] for k in ('report','execution','binding')}
            execution=artifact(root,original_bundle['execution'])
            need(digest(file) in {v for k,v in execution['source_artifact_hashes'].items() if k.endswith('/observations.jsonl')},'HISTORICAL_OBSERVATION_HASH')
        else:
            matches=[(f,c) for f,c in configs if fingerprint({'runner':'E02-v1','config':c,'state_fixtures_hash':fingerprint(states)})==cp['run_fingerprint']];need(bool(matches),'ORIGINAL_CONFIG_NOT_FOUND');f,c=matches[0]
            binding={'runner':'E02-v1','config':c,'state_fixtures_hash':fingerprint(states)}
            execution={'version':'historical-public-execution-snapshot-v1','mode':'live','run_id':cp['run_id'],'run_fingerprint':cp['run_fingerprint'],'dataset_hash':cp['dataset_hash'],'source_sha':cp['source_sha'],'source_artifact_hashes':{name+'/observations.jsonl':digest(file),name+'/checkpoint.json':digest(file.parent/'checkpoint.json'),'private-original-report':digest(reportpath),'private-original-config':digest(f)},'new_calls':0}
            original_bundle={'report':save(folder/'original-report.json',{k:oldreport[k] for k in SCORER_KEYS}),'execution':save(folder/'original-execution.json',execution),'binding':save(folder/'original-binding.json',binding)}
        nr=save(folder/'normalized.json',normalized);rr=save(folder/'report.json',{'kind':KIND,'actual_new_calls':0,'score':{k:newscore[k] for k in SCORER_KEYS}})
        derivation={'original':original_bundle,'revision':mr,'normalized':nr,'report':rr,'actual_new_calls':0,'original_observations_sha256':digest(file),'evaluation_source_hashes':{n:digest(root/n) for n in sorted(SOURCE_EXCEPTIONS)},'scorer_sha256':digest(root/'evals/scorer.py'),'adapter_sha256':digest(root/'evals/adapter.py'),'tool_sha256':digest(root/'scripts/rescore_public_oracle.py')}
        dr=save(folder/'derivation.json',derivation)
        bundle={'kind':KIND,'revision':mr,'original':original_bundle,'binding':original_bundle['binding'],'report':rr,'execution':original_bundle['execution'],'normalized':nr,'derivation':dr}
        br=save(folder/'bundle.pending.json',bundle);verify_bundle(root,bundle,require_review=False)
        before={x['case_id']:x for x in oldscore['case_results']};changed=[x['case_id'] for x in newscore['case_results'] if x!=before[x['case_id']]]
        entry.update(status='derived_pending_independent_review',original_passed=oldscore['passed'],derived_passed=newscore['passed'],incomplete=newscore['incomplete'],mandatory_errors=newscore['mandatory_errors'],changed_case_ids=changed,bundle=br,derivation=dr)
        inventory.append(entry);audits.append({'run':name,'raw_path':str(file.relative_to(root)),'raw_sha256':digest(file),'old_report_path':str(reportpath.relative_to(root)),'normalized':nr,'derivation':dr,'old_replay_exact':True,'normalized_old_new_equal':True})
    need({x['run'] for x in inventory}==set(registered),'REGISTER_COVERAGE')
    cr=save(output/'inventory.json',{'version':REVISION,'actual_new_calls':0,'protected_accessed':False,'registry':manifest['historical_public_runs'],'runs':inventory})
    for e in inventory:
        if e.get('bundle'):
            b=artifact(root,e['bundle']);b['cohort']=cr;save(output/e['run']/'bundle.review-pending.json',b)
    auditpath=private/f'n15-oracle-v4-local-audit-{output_version}.json';save(auditpath,{'version':REVISION,'actual_new_calls':0,'runs':audits})
    print(json.dumps({'runs':len(inventory),'rescored':len(audits),'results':[{k:v for k,v in e.items() if k in ('run','original_passed','derived_passed','changed_case_ids')} for e in inventory],'manifest':mr}))


def verify_cohort(root,cohort_ref,revision_ref,audit_ref):
    m=revision(root,revision_ref);cohort=artifact(root,cohort_ref);registry=artifact(root,m['historical_public_runs']);audit=artifact(root,audit_ref)
    need(cohort.get('actual_new_calls')==0 and cohort.get('protected_accessed') is False and cohort.get('registry')==m['historical_public_runs'],'COHORT_SCOPE')
    registered={x['run']:x for x in registry['runs']};entries=cohort['runs'];need(len(entries)==len(registered)==23 and {x['run'] for x in entries}==set(registered),'COHORT_COVERAGE')
    need(audit.get('revision')==revision_ref and audit.get('cohort')==cohort_ref,'COHORT_AUDIT_BINDING')
    need(audit.get('status')=='PASS' and audit.get('reviewer') and audit.get('implementers') and audit['reviewer'] not in audit['implementers'] and audit.get('private_full_replay_verified') is True,'COHORT_AUDIT')
    for e in entries:
        base=registered[e['run']];need(all(e.get(k)==v for k,v in base.items()),'REGISTER_MISMATCH')
        if base['cases']==30:need(e.get('status')=='unchanged_dev_no_corrected_slots','DEV_STATUS');continue
        d=artifact(root,e['derivation']);need(d['original_observations_sha256']==base['original_observations_sha256'] and e['derivation']['sha256'] in audit.get('derivation_sha256',[]),'COHORT_REPLAY_CHAIN')
        b={'kind':KIND,'revision':revision_ref,'original':d['original'],'binding':d['original']['binding'],'execution':d['original']['execution'],'normalized':d['normalized'],'report':d['report'],'derivation':e['derivation']}
        score,_,_=verify_bundle(root,b,require_review=False)
        need(score['run_id']==base['run_id'] and score['run_fingerprint']==base['run_fingerprint'] and e['derived_passed']==score['passed'],'COHORT_SCORE')
    return cohort

def verify_holdout_freeze(root,cases,config,frozen):
    bundles=frozen.get('validation_rescore_bundles');need(isinstance(bundles,list) and len(bundles)==2,'TWO_DERIVED_VALIDATIONS')
    revision_ref=frozen.get('oracle_revision');m=revision(root,revision_ref)
    need(fingerprint(cases)==m['splits']['holdout']['dataset_hash'],'UNCHANGED_HOLDOUT')
    reports=[];bindings=[]
    for ref_value in bundles:
        b=artifact(root,ref_value);need(b['revision']==revision_ref,'SAME_REVISION')
        r,e,binding=verify_bundle(root,b,current=True)
        from check_release_evidence import Checker
        original_cov=json.loads((Path(root)/'evals/validation-coverage.json').read_text())
        Checker(root).nl(b['original'],{'hash':original_cov['dataset_hash'],'cases':original_cov['cases'],'counts':original_cov['counts']},False,{})
        need(e.get('runner_complete') is True and e.get('planned_user_turns')==92 and e.get('recorded_turns')==92 and e.get('unattempted_user_turns')==0 and e.get('unknown_provider_count')==0 and r['usage_unknown_attempts']==0,'EXECUTION_UNCERTAIN')
        normalized=artifact(root,b['normalized']);all_attempts=[a for o in normalized for t in [o]+o.get('prior_observations',[]) for a in t.get('attempts',[])]
        need(e.get('known_tokens')==r['tokens_known'] and e.get('usage_unknown_attempts')==0 and e.get('outbound_http_attempts')==len(all_attempts),'EXECUTION_USAGE_MISMATCH')
        known_cost=sum(a.get('cost_usd') or 0 for a in all_attempts)
        import math
        need(type(e.get('known_cost_usd')) in (int,float) and math.isfinite(e['known_cost_usd']) and e['known_cost_usd']>=0 and math.isclose(e['known_cost_usd'],known_cost,rel_tol=0,abs_tol=1e-10),'EXECUTION_COST_MISMATCH')
        need(r['cases']==84 and r['stage_ready'] and r['nl_minimum_pass'] and r['incomplete']==0 and r['mandatory_errors']==0 and e['stop_code'] is None,'VALIDATION_NOT_READY')
        source_compatible(root,binding['config'],config)
        if binding['config']['source_sha']!=config['source_sha']:lineage(root,b['application_lineage'],binding['config']['source_sha'],config['source_sha'],e['runtime_hash'])
        reports.append(r);bindings.append(binding)
    need(reports[0]['run_id']!=reports[1]['run_id'] and reports[0]['run_fingerprint']==reports[1]['run_fingerprint'] and reports[0]['dataset_hash']==reports[1]['dataset_hash'],'INDEPENDENT_REPEATS')
    need(set(frozen.get('validation_run_ids',[]))=={r['run_id'] for r in reports} and frozen.get('validation_both_stage_ready') is True,'FROZEN_RUNS')
    return reports

if __name__=='__main__':
    import argparse
    ap=argparse.ArgumentParser();ap.add_argument('--prepare',action='store_true');ap.add_argument('--output-version',default='revision-02');ap.add_argument('--root',default=str(Path(__file__).resolve().parents[1]));ap.add_argument('--private-root',default='artifacts/private/run-20260921');a=ap.parse_args()
    if a.prepare:prepare(Path(a.root),Path(a.root)/a.private_root,a.output_version)
    else:ap.error('--prepare required; network execution is not supported')
