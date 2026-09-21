"""Synthetic protocol fixtures in TemporaryDirectory only. No model or real evidence."""
import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SPEC=importlib.util.spec_from_file_location('release',Path(__file__).resolve().parents[2]/'scripts/check_release_evidence.py')
gate=importlib.util.module_from_spec(SPEC);SPEC.loader.exec_module(gate)
H=lambda value:gate.digest(str(value).encode())

class Package:
    def __init__(self,root,config_name="next.config.mjs"):
        self.root=Path(root)
        for tree in gate.RUNTIME_TREES:(self.root/tree).mkdir(parents=True,exist_ok=True)
        for name in set(gate.ANCHORS)|set(gate.EVAL_SOURCES)|({'evals/baseline-coverage.json',config_name} if config_name else {'evals/baseline-coverage.json'}):
            self.write(name, b'// private synthetic unittest source')
        self.write('data/seed/products.json',[])
        self.catalog=gate.digest(b'[]')
        self.datasets={}
        frozen={}
        for stage,count,splits in [('baseline',336,['dev','validation']),('validation',84,['validation']),('holdout',84,['holdout'])]:
            counts={}
            for split in splits:
                mul=3 if split=='dev' else 1
                for role,ns in [('customer',[9,8,8,7,6,6,6,5,5]),('merchant',[3,3,3,3,3,3,2,2,2])]:
                    for i,n in enumerate(ns,1):counts[f'{role}/{split}/{"C" if role=="customer" else "M"}{i:02}']=n*mul
            f={'dataset_hash':H(stage),'cases':count,'counts':counts};frozen[stage]=f
            self.datasets[stage]={'hash':f['dataset_hash'],'cases':count,'counts':counts}
            if stage!='holdout':self.write(f'evals/{stage}-coverage.json',f)
        self.write('evals/manifest.json',{'holdout_access':'evaluator_only','catalog_hash':self.catalog,'splits':{'holdout':frozen['holdout']}})
        self.files=gate.runtime_files(self.root);self.runtime=gate.fingerprint(self.files)
        self.candidate={'id':'synthetic-best','model':'test-only','promptVersion':'p','promptHash':self.files['src/server/prompts.ts'],'catalogHash':self.catalog,'sourceSha':'a'*40,'runtimeHash':self.runtime,'frozenAt':'2026-09-21T05:00:00Z'}
        self.note=self.art('execution-report','Synthetic unittest report. No real model or application execution.',False)
        nl={'baseline':self.nl('baseline','base'), 'validation':[self.nl('validation','v1'),self.nl('validation','v2')], 'holdout':self.nl('holdout','h1')}
        role_qa=[]
        for role,reviewer in [('customer','qa-c'),('merchant','qa-m')]:
            role_qa.append(self.art('qa-'+role,dict(role=role,scope='G5',provider='openai',coverage=['CORE-17'],reviewer=reviewer,implementers=['builder'],status='PASS',mode='live',actual_browser=True,actual_sql=True,provider_calls=1,runtime_hash=self.runtime,candidate_id=self.candidate['id'],failures=0,mandatory_errors=0,checks_executed=10,evidence=[self.note])))
        policies=[self.art('policy-'+name,dict(scope='G5',reviewer='policy-'+name,perspective=name,status='PASS',unresolved_major=0,runtime_hash=self.runtime,candidate_id=self.candidate['id'],evidence=[self.note])) for name in ['product','state']]
        self.m={'version':gate.VERSION,'scope':'G5','g6_status':'pending','versions':{k:'synthetic-v1' for k in ('research','catalog','scenario','eval','seed','policy','prompt','model','context')},'runtime':{'files':self.files,'sha256':self.runtime},'candidate':self.candidate,'datasets':self.datasets,'nl':nl,'ux':{'baseline':self.ux(False),'best':self.ux(True)},'role_qa':role_qa,'policy_reviews':policies,'core_coverage':{c:{'status':'G6_PENDING' if c=='CORE-13' else 'PASS','scope':'G5','evidence':[self.note]} for c in gate.CORES},'preview':self.art('preview',{'id':'dpl_test','url':'test.vercel.app','readyState':'READY','target':None,'gitSource':{'sha':'a'*40}}),'independent_evidence_review':self.art('evidence-review',{'reviewer':'reviewer','implementers':['checker-author'],'status':'PASS','runtime_hash':self.runtime,'candidate_id':self.candidate['id']})}
    def write(self,name,value):
        p=self.root/name;p.parent.mkdir(parents=True,exist_ok=True)
        p.write_bytes(value if isinstance(value,bytes) else json.dumps(value,ensure_ascii=False).encode())
    def art(self,name,value,json_mode=True):
        name='quality/release/evidence/'+name+('.json' if json_mode else '.md');self.write(name,value if json_mode else value.encode());return {'path':name,'sha256':gate.digest((self.root/name).read_bytes())}
    def read(self,ref):return json.loads((self.root/ref['path']).read_text())
    def mutate(self,ref,fn):
        value=self.read(ref);fn(value);self.write(ref['path'],value);ref['sha256']=gate.digest((self.root/ref['path']).read_bytes())
    def nl(self,stage,rid):
        d=self.datasets[stage];metrics={};groups={}
        for key,n in d['counts'].items():
            role,split,cat=key.split('/');bucket={'cases':n,'passed':n,'complete':n,'mandatory_errors':0,'accuracy_all_cases':1.0}
            metrics[f'{role}/{split}/category:{cat}']=bucket
            group=f'{role}/{split}/{"clear" if int(cat[1:])<=5 else "uncertain"}';groups[group]=groups.get(group,0)+n
        metrics.update({k:{'cases':n,'passed':n,'complete':n,'mandatory_errors':0,'accuracy_all_cases':1.0} for k,n in groups.items()})
        source={k:gate.digest((self.root/k).read_bytes()) for k in set(gate.EVAL_SOURCES)|set(self.files)}
        binding={'runner':'E02-v1','config':{'mode':'live','model':self.candidate['model'],'prompt_version':'p','prompt_hash':self.candidate['promptHash'],'catalog_hash':self.catalog,'source_sha':'a'*40,'source_files':source},'state_fixtures_hash':H('holdout-state' if stage=='holdout' else 'validation-state')}
        fp=gate.fingerprint(binding)
        report=dict(version='EVAL-20260921-v1',mode='live',live_evidence=True,dataset_hash=d['hash'],cases=d['cases'],passed=d['cases'],incomplete=0,mandatory_errors=0,fatal_errors=[],metrics=metrics,outbound_attempts=d['cases'],tokens_known=123,usage_unknown_attempts=0,nl_minimum_pass=True,run_id=rid,run_fingerprint=fp,catalog_hash=self.catalog,evaluation_scope='frozen_stage',frozen_stage_coverage_verified=True,stage_ready=True)
        execution=dict(mode='live',run_id=rid,run_fingerprint=fp,dataset_hash=d['hash'],cases_expected=d['cases'],cases_recorded=d['cases'],attempted_cases=d['cases'],provider_called_count=d['cases'],provider_not_called_count=0,outbound_http_attempts=d['cases'],unknown_provider_count=0,pending_attempts=0,started_at='2026-09-21T06:00:00Z' if stage=='holdout' else '2026-09-21T03:00:00Z',finished_at='2026-09-21T07:00:00Z' if stage=='holdout' else '2026-09-21T04:00:00Z',candidate_id=self.candidate['id'],runtime_hash=self.runtime,source_sha='a'*40,stop_code=None)
        bundle={'report':self.art(rid+'-report',report),'execution':self.art(rid+'-execution',execution),'binding':self.art(rid+'-binding',binding)}
        if stage=='holdout':bundle.update(role='holdout_aggregate',independent_report=self.art('holdout-attestation',{'role':'holdout_evaluator','reviewer':'evaluator','implementers':['builder'],'status':'PASS','run_id':rid,'candidate_id':self.candidate['id'],'runtime_hash':self.runtime,'protected_content_not_published':True}))
        return bundle
    def ux(self,best):
        rows=[]
        for w in gate.WORKLOADS:
            for n in (1,2,3):rows.append(dict(workload=w,repetition=n,status='PASS',durableHash=H('sqlite'),observedClock=123,activations=5,screenTransitions=0,questions=0,merchantPerOrderApprovals=0 if w=='auto-normal' else 1,elapsedMs=120,modelNetworkMs=15,nonModelMs=100,budgetInstrumentationMs=5,unchangedReviewCheck='PASS; synthetic'))
        for i,row in enumerate(rows):
            if i<18:row['network']=[{'attemptId':str(i),'mode':'live','start':1,'networkStart':3,'networkEnd':18,'end':22,'budgetInstrumentationMs':5,'observation':{'provider_called':True}}]
            else:row.update(modelNetworkMs=0,budgetInstrumentationMs=0,nonModelMs=120)
        return self.art('ux-best' if best else 'ux-baseline',dict(mode='live',stage='best' if best else 'baseline',runId='ux-best' if best else 'ux-baseline',authorizationHash=H('authorization'),workloadHash=H('workload'),seedHash=H('seed'),clock=123,harnessHashes={k:H(k) for k in ('run.mts','seed.mts','metrics.mjs','live.mts','budget_bridge.py')},workloads=[{'id':w,'viewport':{'width':390,'height':844} if w in gate.WORKLOADS[:5] else {'width':1440,'height':900}} for w in gate.WORKLOADS],runs=rows,stopCode=None,unknownProviderCalls=0,complete=True,modelCalls=18,outboundAttempts=18,liveUsage=[{'attemptId':str(i),'provider_called':True,'usage':{'input_tokens':1,'output_tokens':1,'total_tokens':2},'cost_usd':.001,'status':'ok'} for i in range(18)],runtimeHash=self.runtime,candidateId=self.candidate['id'],seedEngineBinding={k:self.files[k] for k in ['src/domain/engine.ts','src/contracts/domain.ts']},sourceFiles=self.files))
    def check(self):
        p=self.root/'quality/release/manifest.json';self.write('quality/release/manifest.json',self.m);return gate.Checker(self.root).check(p)

class ReleaseTests(unittest.TestCase):
    def setUp(self):self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.p=Package(self.tmp.name)
    def reject(self,code=None):
        with self.assertRaisesRegex(gate.EvidenceError,code or '.+'):self.p.check()
    def test_synthetic_positive_and_g6_pending(self):self.assertEqual(self.p.check()['status'],'PASS');self.assertEqual(self.p.check()['g6_status'],'pending')
    def test_no_real_manifest_is_not_ready(self):
        p=subprocess.run([sys.executable,str(Path(gate.__file__)),'--root',self.tmp.name],capture_output=True,text=True);self.assertEqual(p.returncode,1);self.assertIn('NOT_READY_MANIFEST_MISSING',p.stdout)
    def test_runtime_new_file_rejects_even_if_existing_hashes_match(self):self.p.write('src/extra.ts',b'new');self.reject('RUNTIME_SET_OR_HASH_MISMATCH')
    def test_runtime_missing_anchor_cannot_be_removed_from_manifest(self):
        (self.p.root/'src/db/worker.ts').unlink();self.p.m['runtime']['files'].pop('src/db/worker.ts');self.reject('MISSING_OR_SYMLINK')
    def test_runtime_modified_asset_rejected(self):self.p.write('public/demo/seed.sqlite',b'changed');self.reject('RUNTIME_SET_OR_HASH')
    def test_stale_artifact_hash(self):self.p.write(self.p.m['preview']['path'],{});self.reject('ARTIFACT_HASH')
    def test_unsafe_private_path_and_symlink_reject(self):
        ref=self.p.m['preview'];ref['path']='artifacts/private/holdout.json';self.reject('PRIVATE_PATH');ref['path']='../private.json';self.reject('UNSAFE_PATH')
    def test_secret_and_holdout_content_never_accepted(self):
        for key in ['expected','case_results','turns','OPENAI_API_KEY']:
            with self.subTest(key=key):
                ref=self.p.m['nl']['holdout']['report'];before=self.p.read(ref);self.p.mutate(ref,lambda r:r.update({key:[]}));self.reject('SECRET_OR_CASE');self.p.write(ref['path'],before);ref['sha256']=gate.digest((self.p.root/ref['path']).read_bytes())
    def test_baseline_quality_failure_is_allowed_if_all_cases_attempted(self):
        ref=self.p.m['nl']['baseline']['report']
        def fail(r):
            r.update(passed=0,incomplete=336,nl_minimum_pass=False,stage_ready=False)
            for m in r['metrics'].values():m.update(passed=0,complete=0,accuracy_all_cases=0)
        self.p.mutate(ref,fail);self.assertEqual(self.p.check()['status'],'PASS')
    def test_baseline_missing_attempt_not_allowed(self):self.p.mutate(self.p.m['nl']['baseline']['execution'],lambda e:e.update(attempted_cases=335));self.reject('FULL_CASE')
    def test_fixture_nl_rejected(self):self.p.mutate(self.p.m['nl']['validation'][0]['report'],lambda r:r.update(mode='fixture'));self.reject('NL_NOT_LIVE')
    def test_repeated_validation_run_id_rejected(self):
        a,b=self.p.m['nl']['validation'];rid=self.p.read(a['report'])['run_id'];self.p.mutate(b['report'],lambda r:r.update(run_id=rid));self.p.mutate(b['execution'],lambda r:r.update(run_id=rid));self.reject('VALIDATION_REPEAT')
    def test_best_quality_cannot_trust_stage_ready_flag(self):
        ref=self.p.m['nl']['validation'][0]['report'];self.p.mutate(ref,lambda r:r['metrics']['customer/validation/clear'].update(passed=0,accuracy_all_cases=0));self.reject('NL_MINIMUM_FAILED')
    def test_best_changed_config_cannot_keep_run_fingerprint(self):
        self.p.mutate(self.p.m['nl']['validation'][0]['binding'],lambda b:b['config'].update(model='other'));self.reject('CANDIDATE_BINDING')
    def test_required_eval_source_removed(self):
        ref=self.p.m['nl']['validation'][0]['binding'];self.p.mutate(ref,lambda b:b['config']['source_files'].pop('scripts/run_nl_eval.py'));self.reject('CANDIDATE_REQUIRED_SOURCE')
    def test_holdout_before_freeze_rejected(self):self.p.mutate(self.p.m['nl']['holdout']['execution'],lambda e:e.update(started_at='2026-09-21T02:00:00Z'));self.reject('HOLDOUT_BEFORE')
    def test_holdout_not_independent_rejected(self):self.p.mutate(self.p.m['nl']['holdout']['independent_report'],lambda e:e.update(reviewer='builder'));self.reject('HOLDOUT_NOT_INDEPENDENT')
    def test_ux_duplicate_repeat_cannot_hide_missing_run(self):self.p.mutate(self.p.m['ux']['best'],lambda u:u['runs'][1].update(repetition=1));self.reject('UX_DUPLICATE')
    def test_ux_missing_workload_rejected(self):self.p.mutate(self.p.m['ux']['best'],lambda u:u['workloads'].pop());self.reject('UX_WORKLOAD_SET')
    def test_ux_fixture_rejected(self):self.p.mutate(self.p.m['ux']['best'],lambda u:u.update(mode='fixture'));self.reject('UX_NOT_LIVE')
    def test_ux_time_and_action_regression_rejected(self):
        self.p.mutate(self.p.m['ux']['best'],lambda u:[r.update(activations=6) for r in u['runs']]);self.reject('UX_REGRESSION')
    def test_ux_accounting_and_no_sql_hash_rejected(self):self.p.mutate(self.p.m['ux']['best'],lambda u:u['runs'][0].update(nonModelMs=0));self.reject('UX_TIME_ACCOUNTING')
    def test_qa_implementer_or_same_reviewer_rejected(self):
        self.p.mutate(self.p.m['role_qa'][0],lambda q:q.update(reviewer='builder'));self.reject('QA_NOT_INDEPENDENT')
    def test_two_role_same_qa_rejected(self):self.p.mutate(self.p.m['role_qa'][1],lambda q:q.update(reviewer='qa-c'));self.reject('TWO_DISTINCT')
    def test_stale_qa_and_unresolved_policy_rejected(self):self.p.mutate(self.p.m['policy_reviews'][0],lambda p:p.update(unresolved_major=1));self.reject('POLICY_UNRESOLVED')
    def test_missing_core_and_g6_false_completion_rejected(self):self.p.m['core_coverage'].pop('CORE-26');self.reject('CORE_COVERAGE')
    def test_not_g6_completion(self):self.p.m['g6_status']='PASS';self.reject('WRONG_GOAL_SCOPE')
    def test_preview_other_commit_rejected(self):self.p.mutate(self.p.m['preview'],lambda p:p['gitSource'].update(sha='b'*40));self.reject('PREVIEW_REVISION')
    def test_frozen_distribution_cannot_be_replaced(self):self.p.m['datasets']['validation']['counts']['customer/validation/C01']=1;self.reject('FROZEN_DATASET_MISMATCH')

    def test_symlink_public_artifact_cannot_escape(self):
        ref=self.p.m['preview'];p=self.p.root/ref['path'];outside=self.p.root/'outside.json';outside.write_bytes(p.read_bytes());p.unlink();p.symlink_to(outside);self.reject('MISSING_OR_SYMLINK')
    def test_transitive_json_reference_cannot_publish_oracles(self):
        ref=self.p.art('oracle-in-coverage',{'case_results':[]});self.p.m['core_coverage']['CORE-01']['evidence']=[ref];self.reject('SECRET_OR_CASE')
    def test_ux_duplicate_provider_attempts_rejected(self):
        self.p.mutate(self.p.m['ux']['best'],lambda u:u['liveUsage'][1].update(attemptId='0'));self.reject('UX_DUPLICATE_PROVIDER')
    def test_ux_provider_evidence_cannot_be_disconnected_from_network(self):
        self.p.mutate(self.p.m['ux']['best'],lambda u:u['runs'][0].update(network=[]));self.reject('UX_NETWORK_PROVIDER')
    def test_qa_fixture_sql_or_earlier_scope_rejected(self):
        ref=self.p.m['role_qa'][0];self.p.mutate(ref,lambda q:q.update(scope='I01 smoke only'));self.reject('QA_SCOPE_MISSING')
    def test_stale_qa_runtime_rejected(self):
        self.p.mutate(self.p.m['role_qa'][0],lambda q:q.update(runtime_hash=H('old')));self.reject('STALE_QA')
    def test_baseline_run_fingerprint_is_verified_despite_quality_exemption(self):
        self.p.mutate(self.p.m['nl']['baseline']['binding'],lambda b:b.update(state_fixtures_hash=H('other')));self.reject('BASELINE_RUN_FINGERPRINT')
    def test_ux_slow_best_cannot_pass_unchanged_summary(self):
        def slower(u):
            for row in u['runs']:row.update(elapsedMs=row['elapsedMs']+20,nonModelMs=row['nonModelMs']+20)
        self.p.mutate(self.p.m['ux']['best'],slower);self.reject('UX_REGRESSION')
    def test_absent_versions_cannot_claim_context_coverage(self):
        self.p.m.pop('versions');self.reject('VERSION_CONTEXT_REQUIRED')

    def test_independence_is_per_reviewed_role_not_entire_app(self):
        self.p.mutate(self.p.m['role_qa'][0],lambda q:q.update(implementers=['qa-m']))
        self.assertEqual(self.p.check()['status'],'PASS')

    def test_unknown_live_usage_cannot_claim_ready(self):
        self.p.mutate(self.p.m['ux']['best'],lambda u:[i.update(usage={},cost_usd=None) for i in u['liveUsage']]);self.reject('UX_UNKNOWN_USAGE_OR_COST')
    def test_impossible_network_time_cannot_clamp_residual_to_zero(self):
        self.p.mutate(self.p.m['ux']['best'],lambda u:[r.update(modelNetworkMs=1e6,nonModelMs=0) for r in u['runs']]);self.reject('UX_TIME_ACCOUNTING')
    def test_ambiguous_question_limit_applies_to_both_stages(self):
        self.p.mutate(self.p.m['ux']['baseline'],lambda u:[r.update(questions=99) for r in u['runs'] if r['workload']=='ambiguous']);self.reject('UX_QUESTION_LIMIT')
    def test_network_interval_sum_recomputed(self):
        self.p.mutate(self.p.m['ux']['best'],lambda u:u['runs'][0]['network'][0].update(networkEnd=19));self.reject('UX_NETWORK_AGGREGATE')

    def test_nl_retry_unknown_history_preserved_when_final_stage_succeeds(self):
        bundle=self.p.m['nl']['validation'][0]
        self.p.mutate(bundle['report'],lambda r:r.update(usage_unknown_attempts=1))
        self.p.mutate(bundle['execution'],lambda e:e.update(unknown_provider_count=1,provider_not_called_count=1,outbound_http_attempts=e['provider_called_count']+2))
        self.assertEqual(self.p.check()['status'],'PASS')

    def test_next_default_without_config_is_valid(self):
        self.p=Package(Path(self.tmp.name)/'default-next',config_name=None)
        self.assertEqual(self.p.check()['status'],'PASS')
        self.assertFalse(any(name.startswith('next.config.') for name in self.p.files))
    def test_next_config_addition_is_fingerprint_change(self):
        self.p=Package(Path(self.tmp.name)/'default-next',config_name=None)
        self.p.write('next.config.mjs',b'export default {}')
        self.reject('RUNTIME_SET_OR_HASH_MISMATCH')
    def test_next_config_modification_is_fingerprint_change(self):
        self.p.write('next.config.mjs',b'export default { poweredByHeader: false }')
        self.reject('RUNTIME_SET_OR_HASH_MISMATCH')
    def test_next_config_deletion_is_fingerprint_change(self):
        (self.p.root/'next.config.mjs').unlink()
        self.reject('RUNTIME_SET_OR_HASH_MISMATCH')

if __name__=='__main__':unittest.main()
