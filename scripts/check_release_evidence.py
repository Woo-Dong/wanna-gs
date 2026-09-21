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
    def eval_manifest(self,ref,catalog_hash):
        original_path=relative(self.root,'evals/manifest.json');original_bytes=original_path.read_bytes();original=json.loads(original_bytes)
        if ref is None:return original
        require(isinstance(ref,dict) and set(ref)=={'path','sha256'} and ref['path']=='evals/manifest-v2.json' and sha(ref['sha256']),'EVAL_REVISION_REFERENCE')
        raw=relative(self.root,ref['path']).read_bytes();require(digest(raw)==ref['sha256'],'EVAL_REVISION_HASH');value=json.loads(raw);sanitized(value);self.checked.add(ref['path'])
        require(value.get('version')=='EVAL-20260921-v2' and value.get('revision')=='holdout-v2-c6' and value.get('status')=='frozen','EVAL_REVISION_NOT_FROZEN')
        require(value.get('predecessor_manifest')=={'path':'evals/manifest.json','sha256':digest(original_bytes)},'EVAL_PREDECESSOR_MISMATCH')
        require(value.get('catalog_hash')==catalog_hash==original.get('catalog_hash') and value.get('catalog_size')==original.get('catalog_size') and value.get('total_cases')==420 and value.get('archived_cases')==84 and value.get('holdout_access')=='evaluator_only','EVAL_REVISION_SCOPE')
        for split in ('dev','validation'):require(value.get('splits',{}).get(split)==original.get('splits',{}).get(split),'PUBLIC_SPLIT_CHANGED')
        old=original['splits']['holdout'];new=value.get('splits',{}).get('holdout',{})
        require(value.get('label_counts')=={'customer':{'clear':40,'uncertain':20},'merchant':{'clear':15,'uncertain':9}},'HOLDOUT_REPLACEMENT_LABEL_COUNTS')
        require(new.get('cases')==84 and new.get('counts')==old['counts'] and new.get('user_turns')==92 and new.get('worst_attempts')==276 and sha(new.get('dataset_hash')) and new['dataset_hash']!=old['dataset_hash'],'HOLDOUT_REPLACEMENT_COVERAGE')
        families=new.get('family_hashes',[]);used={h for split in original['splits'].values() for h in split.get('family_hashes',[])}
        require(isinstance(families,list) and len(families)>=len(old.get('family_hashes',[])) and all(sha(h) for h in families) and len(set(families))==len(families) and not (set(families)&used),'HOLDOUT_REPLACEMENT_FAMILY')
        retired=value.get('retired_holdouts',[])
        require(isinstance(retired,list) and len(retired)==1 and retired[0].get('dataset_hash')==old['dataset_hash'] and retired[0].get('status')=='FAIL' and retired[0].get('replay_authorized') is False and retired[0].get('retired_reason') and sha(retired[0].get('file_sha256')),'HOLDOUT_HISTORY_REQUIRED')
        bundle=self.artifact(retired[0]['execution_evidence']);report=self.artifact(bundle['report'])
        require(bundle.get('role')=='holdout_aggregate' and report.get('dataset_hash')==old['dataset_hash'] and report.get('cases')==84 and report.get('nl_minimum_pass') is False,'HOLDOUT_FAILURE_NOT_PRESERVED')
        review=self.artifact(value.get('independent_data_review'))
        require(review.get('status')=='PASS' and review.get('reviewer') and isinstance(review.get('implementers'),list) and review['implementers'] and review['reviewer'] not in review['implementers'] and review.get('dataset_hash')==new['dataset_hash'] and review.get('previous_dataset_hash')==old['dataset_hash'] and type(review.get('semantic_family_overlap')) is int and review['semantic_family_overlap']==0 and review.get('difficulty_equivalent') is True and review.get('thresholds_unchanged') is True and review.get('protected_content_not_published') is True,'HOLDOUT_DATA_REVIEW_REQUIRED')
        timestamp(value.get('frozenAt'))
        return value
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
    def ux_v3(self,ref,best,candidate):
        v=self.artifact(ref);stage='best' if best else 'baseline'
        require(v.get('version')=='UX-BENCHMARK-v3' and v.get('mode')=='live' and v.get('studyId')=='ux-study-v3-01' and v.get('stage')==stage and v.get('runId')==('ux-best-v3-01' if best else 'ux-baseline-b0-v3-01'),'V3_IDENTITY')
        require(v.get('planHash')=='515a97609bc51b3ebb463bd5e7b5bd3814b6241b99ad50750741a7ea1a1da386','V3_PLAN_HASH')
        require(v.get('stopCode') is None and v.get('pendingAttempts')==0 and v.get('unknownProviderCalls')==0 and v.get('complete') is True,'V3_STUDY_STOP_OR_PENDING')
        require(v.get('clock')==1789959600000 and all(sha(v.get(k)) for k in ('seedHash','workloadHash','authorizationHash','budgetRunnerHash')),'V3_BINDING')
        require(v['budgetRunnerHash']==digest(relative(self.root,'scripts/run_nl_eval.py').read_bytes()),'V3_BUDGET_SOURCE_STALE')
        bs=v.get('budgetSourceFiles');require(isinstance(bs,dict) and set(bs)=={'scripts/run_nl_eval.py','evals/adapter.py','evals/scorer.py'} and all(value==digest(relative(self.root,name).read_bytes()) for name,value in bs.items()),'V3_BUDGET_DEPENDENCY_STALE')
        hh=v.get('harnessHashes',{});required=('run.mts','plan.mjs','metrics.mjs','binding.mjs','live.mts','budget_bridge.py','seed.mts','v2-metrics.mjs')
        require(set(hh)==set(required),'V3_HARNESS_SET')
        for name in required:
            source='tests/ux-benchmark/'+('seed.mts' if name=='seed.mts' else 'metrics.mjs' if name=='v2-metrics.mjs' else 'v3/'+name)
            require(sha(hh[name]) and hh[name]==digest(relative(self.root,source).read_bytes()),'V3_HARNESS_STALE')
        ws=v.get('workloads');require(isinstance(ws,list) and len(ws)==8 and [w.get('id') for w in ws]==list(WORKLOADS),'V3_WORKLOAD_ORDER')
        for i,w in enumerate(ws):require(w.get('viewport')==({'width':390,'height':844} if i<5 else {'width':1440,'height':900}),'V3_VIEWPORT')
        rows=v.get('runs');require(isinstance(rows,list) and len(rows)==56,'V3_TRIAL_DENOMINATOR')
        usage=v.get('liveUsage');require(isinstance(usage,list) and integer(v.get('outboundAttempts')) and len(usage)==v['outboundAttempts']<=42,'V3_PROVIDER_DENOMINATOR')
        require(len({u.get('attemptId') for u in usage})==len(usage) and all(u.get('attemptId') for u in usage),'V3_DUPLICATE_ATTEMPT')
        require(v.get('modelCalls')==sum(u.get('provider_called') is True for u in usage),'V3_PROVIDER_COUNT')
        for item in usage:
            u=item.get('usage');require(type(item.get('provider_called')) is bool and item.get('status') in ('ok','failed') and isinstance(u,dict) and all(integer(u.get(k)) for k in ('input_tokens','output_tokens','total_tokens')) and u['total_tokens']==u['input_tokens']+u['output_tokens'] and finite(item.get('cost_usd')),'V3_UNKNOWN_USAGE')
            require(item['status']!='ok' or item['provider_called'] is True,'V3_SUCCESS_REQUIRES_LIVE_PROVIDER')
        byid={u['attemptId']:u for u in usage};all_network=[];result={}
        for wi,w in enumerate(WORKLOADS):
            group=rows[wi*7:(wi+1)*7];success=[];planned=2 if w=='ambiguous' else 1 if w.startswith('clear-') or w=='auto-normal' else 0
            for n,row in enumerate(group,1):
                require(row.get('workload')==w and row.get('repetition')==n and row.get('attempted') is True and row.get('status') in ('PASS','FAIL'),'V3_ORDER_OR_UNATTEMPTED')
                network=row.get('network',[]);steps=row.get('modelSteps');require(row.get('plannedModelCalls')==planned and isinstance(steps,list) and len(steps)==planned and len(network)<=planned,'V3_MODEL_STEP_DENOMINATOR')
                for si,step in enumerate(steps):
                    require(step.get('status') in ('PASS','FAIL','NOT_RUN'),'V3_MODEL_STEP_STATUS')
                    if si<len(network):
                        aid=network[si].get('attemptId');require(aid in byid and step.get('attemptId')==aid and step['status']==('PASS' if byid[aid]['status']=='ok' else 'FAIL'),'V3_MODEL_STEP_BINDING')
                    else:require(step['status']=='NOT_RUN' and step.get('attemptId') is None,'V3_MODEL_STEP_NOT_RUN')
                all_network.extend(network)
                if row['status']=='FAIL':
                    require(not best and isinstance(row.get('error'),str) and row['error'],'V3_BEST_FAILURE');continue
                success.append(row)
                require(len(network)==planned and all(byid[x['attemptId']]['status']=='ok' and byid[x['attemptId']]['provider_called'] is True for x in network),'V3_PASS_WITH_FAILED_MODEL')
                require(not row.get('setupFailed') and not row.get('pageErrors') and sha(row.get('durableHash')) and row.get('observedClock')==v['clock'],'V3_SQL_CORRECTNESS')
                for key in ('activations','screenTransitions','questions','merchantPerOrderApprovals'):require(integer(row.get(key)),'V3_ACTIONS')
                for key in ('elapsedMs','modelNetworkMs','nonModelMs','budgetInstrumentationMs'):require(finite(row.get(key)),'V3_TIMING')
                require(row['modelNetworkMs']+row['budgetInstrumentationMs']<=row['elapsedMs']+.001 and abs(row['nonModelMs']-(row['elapsedMs']-row['modelNetworkMs']-row['budgetInstrumentationMs']))<.001,'V3_TIME_ACCOUNTING')
                require(abs(interval_union(network)-row['modelNetworkMs'])<.001 and abs(sum(x['budgetInstrumentationMs'] for x in network)-row['budgetInstrumentationMs'])<.001,'V3_NETWORK_TIME')
                require(row['questions']<=2,'V3_QUESTIONS')
                if w.startswith('clear-'):require(row['activations']-1<=7,'V3_CUSTOMER_ACTIONS')
                if w=='batch-10':require(row['screenTransitions']==0 and row['merchantPerOrderApprovals']==1,'V3_BATCH_APPROVAL')
                if w=='auto-normal':require(row['merchantPerOrderApprovals']==0 and str(row.get('unchangedReviewCheck','')).startswith('PASS'),'V3_AUTO_DUPLICATE')
            require(len(success)>=(7 if best else 3),'V3_INSUFFICIENT_SUCCESS')
            result[w]={'planned':7,'attempted':7,'passed':len(success),'failed':7-len(success),'actions':max(r['activations'] for r in success),'screens':max(r['screenTransitions'] for r in success),'median':statistics.median(r['nonModelMs'] for r in success)}
        require(len(all_network)==len(usage) and len({x.get('attemptId') for x in all_network})==len(usage) and {x.get('attemptId') for x in all_network}==set(byid),'V3_NETWORK_PROVIDER_BINDING')
        for n in all_network:require(n.get('mode')=='live' and n.get('observation')=={k:byid[n['attemptId']][k] for k in ('status','provider_called','usage','cost_usd')},'V3_NETWORK_OBSERVATION')
        source=v.get('sourceFiles');require(isinstance(source,dict) and all(sha(x) for x in source.values()) and v.get('runtimeHash')==fingerprint(source),'V3_RUNTIME_BINDING')
        for name in ANCHORS:require(name in source,'V3_REQUIRED_SOURCE')
        for name in ('src/domain/engine.ts','src/contracts/domain.ts'):require(v.get('seedEngineBinding',{}).get(name)==source[name],'V3_SEED_ENGINE')
        if best:
            require(source==self.files and v['runtimeHash']==self.runtime_hash and v.get('candidateId')==candidate['id'] and v.get('sourceSha')==candidate['sourceSha'] and v.get('model')==candidate['model'] and v.get('promptVersion')==candidate['promptVersion'] and v.get('catalogHash')==candidate['catalogHash'],'V3_CURRENT_CANDIDATE')
        else:require(v.get('sourceSha')=='10c00723d0b64ea47a06dcbd00e2b671e7c62daf' and v.get('model')=='gpt-5-mini-2025-08-07' and v.get('promptVersion')=='baseline-v1','V3_B0_SOURCE')
        return v,result
    def ux_v3_history(self,refs):
        require(isinstance(refs,list) and len(refs)==2,'V3_HISTORY_REQUIRED');summaries=[]
        bindings=[('ux-baseline-b0-v2-01','4989b1053468134ff8a3099b951493ba483687f57fb14de49db48ea4e87b4209',3,2,1,21),('ux-baseline-b0-v2-recovery-01','2b9839efff2d118b48751642e7382b41d6e41fa49b837ccb4beff56fd1433c4b',12,11,1,12)]
        for ref,(rid,sha256,attempted,passed,failed,missing) in zip(refs,bindings):
            old=self.artifact(ref);require(old.get('runId')==rid and old.get('originalSha256')==sha256 and old.get('mode')=='live' and old.get('complete') is False,'V3_HISTORY_SOURCE')
            rows=old.get('runs');require(isinstance(rows,list) and len(rows)==attempted,'V3_HISTORY_ROWS')
            require([(r.get('workload'),r.get('repetition')) for r in rows]==[(w,n) for w in WORKLOADS for n in (1,2,3)][:attempted],'V3_HISTORY_ORDER')
            require([r.get('status') for r in rows]==['PASS']*passed+['FAIL'],'V3_HISTORY_FAILURES')
            summary=dict(runId=rid,originalSha256=sha256,planned=24,attempted=attempted,passed=passed,failed=failed,notRun=missing)
            require(all(old.get(k)==v for k,v in summary.items()),'V3_HISTORY_DENOMINATOR');summaries.append(summary)
        return summaries
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
        public_manifest=self.eval_manifest(m.get('eval_manifest'),candidate['catalogHash'])
        if m.get('eval_manifest'):
            require(timestamp(public_manifest['frozenAt'])<=freeze,'HOLDOUT_DATA_FROZEN_AFTER_CANDIDATE')
            for bundle in [*m['nl']['validation'],m['nl']['holdout']]:
                bound=self.artifact(bundle['binding'])['config']['source_files']
                require(bound.get(m['eval_manifest']['path'])==m['eval_manifest']['sha256'],'EVAL_REVISION_SOURCE_BINDING')
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
        if m.get('eval_manifest'):
            for role,labels in public_manifest['label_counts'].items():
                for label,count in labels.items():
                    require(hold['metrics'].get(f'{role}/holdout/{label}',{}).get('cases')==count,'HOLDOUT_LABEL_DENOMINATOR_CHANGED')
        require(len({b['run_id'],first['run_id'],second['run_id'],hold['run_id']})==4,'DUPLICATE_NL_RUN')
        require(timestamp(he['started_at'])>=max(freeze,timestamp(e1['finished_at']),timestamp(e2['finished_at'])),'HOLDOUT_BEFORE_BEST_FROZEN')
        ha=self.artifact(h['independent_report']);require(ha.get('role')=='holdout_evaluator' and ha.get('status')=='PASS' and ha.get('run_id')==hold['run_id'] and ha.get('candidate_id')==candidate['id'] and ha.get('runtime_hash')==self.runtime_hash and ha.get('protected_content_not_published') is True,'HOLDOUT_INDEPENDENT_ATTESTATION')
        require(ha.get('reviewer') and isinstance(ha.get('implementers'),list) and ha['implementers'] and ha['reviewer'] not in ha['implementers'],'HOLDOUT_NOT_INDEPENDENT')
        if m['ux'].get('version')=='UX-BENCHMARK-v3':
            history=self.ux_v3_history(m['ux'].get('history'))
            ub,bs=self.ux_v3(m['ux']['baseline'],False,candidate);uv,vs=self.ux_v3(m['ux']['best'],True,candidate)
            require(ub.get('history')==history and uv.get('history')==history,'V3_HISTORY_BINDING')
            require(m['ux'].get('plannedTotals')=={'historicalBaseline':48,'newBaseline':56,'newBest':56,'total':160},'V3_TOTAL_PLANNED')
        else:
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
