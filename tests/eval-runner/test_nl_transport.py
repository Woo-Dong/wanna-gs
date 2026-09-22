"""Independent transport harness unit/integration cases. Local fake HTTP only; no provider."""
import copy
import hashlib
import importlib.util
import json
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
import tempfile
import threading
import unittest

ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('transport_runner',ROOT/'scripts/run_nl_eval.py');r=importlib.util.module_from_spec(spec);spec.loader.exec_module(r)


def case(cid='C01-dev-001',split='dev',multi=False):
    c={'id':cid,'role':'customer','category':'C01','split':split,'family_id':cid,'origin':'synthetic_expansion','research_ids':['R1'],'scenario_id':'S1','catalog_hash':'h','binding_status':'verified','label':'clear','turns':[{'role':'user','text':'공개 테스트 제품'}],'max_model_turns':1,'expected':{'allowed_actions':['candidates'],'required_any_skus':['SKU1'],'candidate_pool':['SKU1']}}
    if multi:c['turns'].append({'role':'user','text':'아까 말한 제품을 다시 확인해 주세요'});c['max_model_turns']=2;c['expected_prior']=[copy.deepcopy(c['expected'])]
    return c

def config(origin='http://127.0.0.1:1',mode='fixture'):
    return {'mode':mode,'origin':origin,'model':'mock-model','prompt_version':'p1','prompt_hash':r.file_hash(ROOT/'src/server/prompts.ts'),'catalog_version':'c1','catalog_hash':'h','source_sha':'s1','api_version':'assistant-v1','source_files':{name:r.file_hash(ROOT/name) for name in r.REQUIRED_SOURCES},'mandatory_reserve':{'future':0},'mandatory_cost_reserve_usd':0}

def raw():return {'action':'show_candidates','candidates':[{'id':'SKU1','kind':'exact','sharedEvidence':['제품명'],'differences':[],'unknownConditions':[]}],'question':None,'reason':'고객이 확인합니다','confirmationRequired':True}
def success(body,conf):
    return {'ok':True,'data':{**{k:body[k] for k in r.ENVELOPE},'mode':conf['mode'],'model':conf['model'],'promptVersion':conf['prompt_version'],'catalogVersion':conf['catalog_version'],'result':raw(),'usage':{'inputTokens':10,'outputTokens':2,'totalTokens':12,'estimatedCostUsd':.001},'latencyMs':10}}
def failure(code,called=True):return {'ok':False,'error':{'code':code,'retryable':True,'attempt':{'providerCalled':called,'model':'mock-model','mode':'live','usage':None,'latencyMs':10}}}

class FakeHTTP:
    def __init__(self,callback):
        self.requests=[];self.callback=callback;outer=self
        class Handler(BaseHTTPRequestHandler):
            def log_message(self,*args):pass
            def do_POST(self):
                body=json.loads(self.rfile.read(int(self.headers['Content-Length'])));outer.requests.append({'path':self.path,'headers':dict(self.headers),'body':body})
                status,value,headers=outer.callback(body,len(outer.requests))
                self.send_response(status)
                for k,v in headers.items():self.send_header(k,v)
                self.end_headers();self.wfile.write(json.dumps(value).encode())
        self.server=ThreadingHTTPServer(('127.0.0.1',0),Handler);self.origin='http://127.0.0.1:'+str(self.server.server_port)
        self.thread=threading.Thread(target=self.server.serve_forever,daemon=True);self.thread.start()
    def close(self):self.server.shutdown();self.server.server_close();self.thread.join()

class RunnerTests(unittest.TestCase):
    def setUp(self):self.tmp=tempfile.TemporaryDirectory();self.path=Path(self.tmp.name);self.servers=[]
    def tearDown(self):
        for server in self.servers:server.close()
        self.tmp.cleanup()
    def server(self,callback):
        server=FakeHTTP(callback);self.servers.append(server);return server
    def runner(self,cases,callback,mode='fixture',states=None):
        conf=config(mode=mode);server=self.server(lambda body,n:callback(body,n,conf));conf['origin']=server.origin
        runner=r.Runner(cases,conf,self.path/'run',r.Budget(self.path/'ledger.json'),r.HttpTransport(server.origin),states,run_id='run-1')
        return runner,server
    def test_real_http_two_turns_use_only_actual_assistant_history(self):
        c=case(multi=True);c['expected']['notes']='SECRET_ORACLE_SENTINEL';runner,server=self.runner([c],lambda b,n,c:(200,success(b,c),{}))
        result=runner.run({'SKU1'},sleep=lambda _:None);self.assertTrue(result['complete']);self.assertEqual(len(server.requests),2)
        first,second=[x['body'] for x in server.requests];self.assertEqual(first['history'],[]);self.assertEqual(second['history'][0]['content'],c['turns'][0]['text']);self.assertEqual(json.loads(second['history'][1]['content']),raw());self.assertNotIn('SECRET_ORACLE_SENTINEL',json.dumps(server.requests));self.assertNotIn('expected',first)
        observations=r.read_jsonl(runner.out/'observations.jsonl');self.assertEqual(len(observations),1);self.assertEqual(len(observations[0]['prior_observations']),1)
    def test_clarification_count_follows_real_response(self):
        c=case(multi=True)
        def callback(body,n,conf):
            response=success(body,conf)
            if n==1:response['data']['result']={**raw(),'action':'ask_clarification','question':'어떤 맛인가요?','candidates':[]}
            return 200,response,{}
        runner,server=self.runner([c],callback);runner.run({'SKU1'},sleep=lambda _:None);self.assertEqual(server.requests[1]['body']['clarificationCount'],1)
    def test_chunk_resume_never_reexecutes_finished_case(self):
        cases=[case(),case('C01-dev-002')];runner,server=self.runner(cases,lambda b,n,c:(200,success(b,c),{}));self.assertFalse(runner.run({'SKU1'},max_cases=1)['complete']);self.assertEqual(len(server.requests),1)
        runner.run({'SKU1'},resume=True);self.assertEqual(len(server.requests),2);runner.run({'SKU1'},resume=True);self.assertEqual(len(server.requests),2)
    def test_pending_attempt_stops_resume_without_new_http(self):
        runner,server=self.runner([case()],lambda b,n,c:(200,success(b,c),{}));runner.initialize();runner.state['pending']={'attempt_id':'uncertain'};runner.save()
        with self.assertRaisesRegex(r.RunnerError,'UNCERTAIN_PENDING'):runner.run({'SKU1'},resume=True)
        self.assertEqual(len(server.requests),0)
    def test_received_success_journal_resume_does_not_duplicate_call(self):
        runner,server=self.runner([case()],lambda b,n,c:(200,success(b,c),{}));runner.initialize();runner.state['cases'][case()['id']]={'turns':[],'observation':None,'current_attempts':[{'status':'ok','provider_called':False}],'current_raw':raw()};runner.save();runner.run({'SKU1'},resume=True);self.assertEqual(len(server.requests),0)
    def test_retry_counts_and_unknown_usage_preserved(self):
        runner,server=self.runner([case()],lambda b,n,c:(429,failure('RATE_LIMITED'),{}) if n<3 else (200,success(b,c),{}),mode='live');result=runner.run({'SKU1'},sleep=lambda _:None)
        self.assertEqual(len(server.requests),3);obs=r.read_jsonl(runner.out/'observations.jsonl')[0];self.assertEqual(len(obs['attempts']),3);self.assertEqual(obs['attempts'][0]['usage'],None);self.assertEqual(result['budget']['known_provider_calls'],3)
    def test_retry_limit_not_reset_on_resume(self):
        runner,server=self.runner([case()],lambda b,n,c:(429,failure('RATE_LIMITED'),{}));runner.initialize();runner.state['cases'][case()['id']]={'turns':[],'observation':None,'current_attempts':[{'status':'failed','code':'RATE_LIMITED','provider_called':True}]*2,'current_raw':None};runner.save();runner.run({'SKU1'},resume=True,sleep=lambda _:None);self.assertEqual(len(server.requests),1)
    def limited_runner(self,cases,limit,callback):
        conf=config(mode='live');conf['max_attempts']=limit
        server=self.server(lambda body,n:callback(body,n,conf));conf['origin']=server.origin
        return r.Runner(cases,conf,self.path/'limited',r.Budget(self.path/'ledger'),r.HttpTransport(server.origin)),server
    def test_one_attempt_failure_retains_denominator_and_adjacent_success(self):
        runner,server=self.limited_runner([case(),case('C01-dev-002')],1,lambda b,n,c:(429,failure('RATE_LIMITED'),{}) if n==1 else (200,success(b,c),{}))
        result=runner.run({'SKU1'},sleep=lambda _:self.fail('retry sleep forbidden'))
        self.assertEqual(len(server.requests),2);self.assertTrue(result['complete']);self.assertEqual(result['failed_cases'],1)
        obs=r.read_jsonl(runner.out/'observations.jsonl');self.assertEqual(len(obs),2);self.assertEqual(len(obs[0]['attempts']),1);self.assertEqual(obs[0]['transport'],'error')
        runner.run({'SKU1'},resume=True);self.assertEqual(len(server.requests),2)
    def test_one_attempt_received_failure_cannot_retry_after_resume(self):
        runner,server=self.limited_runner([case()],1,lambda b,n,c:(200,success(b,c),{}))
        runner.initialize();runner.state['cases'][case()['id']]={'turns':[],'observation':None,'current_attempts':[{'status':'failed','code':'RATE_LIMITED','provider_called':True}],'current_raw':None};runner.save()
        result=runner.run({'SKU1'},resume=True);self.assertEqual(len(server.requests),0);self.assertEqual(result['failed_cases'],1)
    def test_configured_attempt_cap_is_strict_and_defaults_to_three(self):
        self.assertEqual(r.attempt_limit({}),3)
        for value in [1,2,3]:self.assertEqual(r.attempt_limit({'max_attempts':value}),value)
        for value in [True,False,0,4,-1,1.0,'1',None,[],{}]:
            with self.subTest(value=value):
                cases,conf,coverage,path=self.valid_inputs();conf['max_attempts']=value
                with self.assertRaisesRegex(r.RunnerError,'INVALID_MAX_ATTEMPTS'):r.check_inputs(cases,conf,coverage,path,{})
                with self.assertRaisesRegex(r.RunnerError,'INVALID_MAX_ATTEMPTS'):r.Runner(cases,conf,self.path/'bad',None,None)
    def test_current_stage_reservation_uses_configured_cap(self):
        runner,server=self.limited_runner([case(),case('C01-dev-002')],1,lambda b,n,c:(200,success(b,c),{}))
        reservations=[];reserve=runner.budget.reserve
        def record(run_id,mandatory,cost):
            reservations.append(mandatory);return reserve(run_id,mandatory,cost)
        runner.budget.reserve=record;runner.run({'SKU1'});self.assertEqual(reservations,[1,0]);self.assertEqual(len(server.requests),2)
    def test_changing_attempt_allowance_cannot_resume_existing_run(self):
        runner,server=self.limited_runner([case()],1,lambda b,n,c:(200,success(b,c),{}));runner.initialize()
        changed=r.Runner(runner.cases,{**runner.config,'max_attempts':3},runner.out,runner.budget,runner.transport)
        with self.assertRaisesRegex(r.RunnerError,'RESUME_FINGERPRINT_MISMATCH'):changed.run({'SKU1'},resume=True)
        self.assertEqual(len(server.requests),0)
    def test_auth_quota_config_stop_every_next_case(self):
        for code in ['LLM_AUTH_ERROR','LLM_QUOTA','LLM_CONFIGURATION','LLM_MODEL_UNAVAILABLE']:
            with self.subTest(code=code):
                folder=self.path/code;conf=config();server=self.server(lambda b,n,code=code:(503,failure(code),{}));conf['origin']=server.origin
                runner=r.Runner([case(),case('C01-dev-002')],conf,folder,r.Budget(folder/'ledger'),r.HttpTransport(server.origin));result=runner.run({'SKU1'},sleep=lambda _:None);self.assertEqual(result['stop_code'],code);self.assertEqual(len(server.requests),1)
    def test_stale_envelope_and_wrong_mode_stop(self):
        for field,value in [('requestId','old'),('generation',9),('mode','live'),('model','other')]:
            with self.subTest(field=field):
                conf=config();server=self.server(lambda b,n,field=field,value=value:(200,{'ok':True,'data':{**success(b,conf)['data'],field:value}},{}));conf['origin']=server.origin
                folder=self.path/field;runner=r.Runner([case()],conf,folder,r.Budget(folder/'ledger'),r.HttpTransport(server.origin));res=runner.run({'SKU1'});self.assertIsNotNone(res['stop_code'])
    def test_bypass_is_origin_scoped_and_redirect_is_never_followed(self):
        target=self.server(lambda b,n:(200,{},{}));source=self.server(lambda b,n:(307,{}, {'Location':target.origin+'/steal'}));secret_path=self.path/'bypass';secret_path.write_text(json.dumps({'secret':'PRIVATE_HEADER_SENTINEL'}));transport=r.HttpTransport(source.origin,secret_path)
        result=transport.post('customer',{'text':'hello'});self.assertEqual(result['error'],'REDIRECT_BLOCKED');self.assertEqual(len(target.requests),0);self.assertEqual({k.lower():v for k,v in source.requests[0]['headers'].items()}['x-vercel-protection-bypass'],'PRIVATE_HEADER_SENTINEL');self.assertNotIn('PRIVATE_HEADER_SENTINEL',json.dumps(result))
    def test_bad_origin_or_header_controls_rejected(self):
        for origin in ['https://a.example?token=secret','https://user:pass@a.example','http://a.example','https://a.example/scope']:
            with self.assertRaises(r.RunnerError):r.origin_url(origin)
        p=self.path/'bad';p.write_text(json.dumps({'secret':'a\r\nb'}))
        with self.assertRaises(r.RunnerError):r.HttpTransport('https://a.example',p)
    def test_budget_prior_is_reserve_not_measured_and_calls_stop(self):
        budget=r.Budget(self.path/'ledger');self.assertEqual(budget.snapshot()['accounted_calls_upper_bound'],20);self.assertEqual(budget.snapshot()['known_provider_calls'],0)
        with self.assertRaisesRegex(r.RunnerError,'CALL_RESERVE_STOP'):budget.reserve('r',2380)
        self.assertEqual(budget.snapshot()['accounted_calls_upper_bound'],20)
    def test_cost_reserve_stop_and_provider_false_release(self):
        budget=r.Budget(self.path/'ledger');aid=budget.reserve('r',0);budget.finish(aid,{'status':'failed','provider_called':False});self.assertEqual(budget.snapshot()['accounted_calls_upper_bound'],20)
        with self.assertRaisesRegex(r.RunnerError,'COST_SOFT_STOP'):budget.reserve('r',0,19)
    def test_user_approved_twenty_dollar_boundary_and_just_below(self):
        self.assertEqual(r.GOAL_API_COST_SOFT_LIMIT_USD,20.0)
        for name,future in [('equal',17.45),('above',17.46)]:
            budget=r.Budget(self.path/name,prior_reserve=50)
            with self.assertRaisesRegex(r.RunnerError,'COST_SOFT_STOP'):budget.reserve('r',0,future)
            self.assertEqual(budget.snapshot()['accounted_calls_upper_bound'],50)
        budget=r.Budget(self.path/'below',prior_reserve=50)
        aid=budget.reserve('r',0,17.449)
        self.assertEqual(r.load_json(budget.path)['attempts'][aid]['status'],'pending')
        self.assertAlmostEqual(budget.snapshot()['cost_upper_estimate_usd'],2.55)
    def test_old_fifteen_boundary_allowed_without_rewriting_history(self):
        budget=r.Budget(self.path/'history',prior_reserve=50)
        history={'run_id':'old-failed-run','status':'failed','provider_called':True,'cost':12.4}
        unknown={'run_id':'old-timeout','status':'unknown','provider_called':None,'cost':None}
        with budget.locked() as state:
            state['attempts'].update(old=history,unknown=unknown)
        before=r.load_json(budget.path)
        self.assertAlmostEqual(budget.snapshot()['cost_upper_estimate_usd'],14.95)
        aid=budget.reserve('new-run',0)
        after=r.load_json(budget.path)
        self.assertAlmostEqual(budget.snapshot()['cost_upper_estimate_usd'],15.0)
        self.assertEqual(after['attempts']['old'],before['attempts']['old'])
        self.assertEqual(after['attempts']['unknown'],before['attempts']['unknown'])
        for key in set(before)-{'attempts'}:self.assertEqual(after[key],before[key])
        self.assertIsNone(after['attempts'][aid]['provider_called'])
        self.assertIsNone(after['attempts'][aid]['cost'])
    def test_future_cost_reserve_still_counts_every_pending_attempt(self):
        budget=r.Budget(self.path/'future',prior_reserve=50)
        budget.reserve('r',0,17.4)  # 2.50 + .05 + 17.40 < 20.
        with self.assertRaisesRegex(r.RunnerError,'COST_SOFT_STOP'):budget.reserve('r',0,17.4)
        self.assertEqual(len(r.load_json(budget.path)['attempts']),1)
    def test_fifty_prior_call_reserve_and_2400_limit_unchanged(self):
        budget=r.Budget(self.path/'calls',prior_reserve=50)
        budget.reserve('r',2349)
        with self.assertRaisesRegex(r.RunnerError,'CALL_RESERVE_STOP'):budget.reserve('r',2349)
        snapshot=budget.snapshot()
        self.assertEqual(snapshot['accounted_calls_upper_bound'],51)
        self.assertEqual(snapshot['known_provider_calls'],0)
        self.assertEqual(snapshot['unknown_provider_calls'],1)
    def test_holdout_claim_is_once_per_dataset(self):
        b=r.Budget(self.path/'ledger');b.claim_holdout('d','r1');b.claim_holdout('d','r1')
        with self.assertRaisesRegex(r.RunnerError,'HOLDOUT_ALREADY'):b.claim_holdout('d','r2')
    def test_schema_and_fake_sku_never_success(self):
        bad=raw();bad['candidates'][0]['id']='FAKE';runner,_=self.runner([case()],lambda b,n,c:(200,{'ok':True,'data':{**success(b,c)['data'],'result':bad}},{}));runner.run({'SKU1'});obs=r.read_jsonl(runner.out/'observations.jsonl')[0];self.assertFalse(obs['schema_valid']);self.assertEqual(obs['attempts'][0]['code'],'INVALID_RESPONSE_SCHEMA')
    def test_actual_business_state_allowlist_never_oracle(self):
        c=case();c.update(role='merchant',category='M01',context={'proposalRevision':3,'currentRevision':4,'stale':True,'expected':'LEAK','currentConstraints':{'budgetLimitKrw':4000}})
        state={'storeId':'S','proposalId':'P','proposalVersion':1,'dailyBudgetKrw':5000,'groups':[],'currentConstraints':None,'previousConstraints':None}
        body=r.make_request(c,[],config(),{'default':state},'r');self.assertNotIn('expected',body['state']);self.assertEqual(body['state']['proposalVersion'],3);self.assertEqual(body['state']['currentProposalVersion'],4);self.assertEqual(body['state']['currentConstraints']['budgetLimitKrw'],4000)
        with self.assertRaisesRegex(r.RunnerError,'STATE_FIXTURE_REQUIRED'):r.make_request(c,[],config(),{},'r')
    def test_content_files_private_permissions(self):
        runner,_=self.runner([case()],lambda b,n,c:(200,success(b,c),{}));runner.run({'SKU1'});self.assertEqual((runner.out/'checkpoint.json').stat().st_mode&0o777,0o600);self.assertEqual((runner.out/'observations.jsonl').stat().st_mode&0o777,0o600)

    def valid_inputs(self,split='dev'):
        catalog=[{'sku':'SKU1','name':'test'}];path=self.path/'catalog.json';path.write_text(json.dumps(catalog));h=hashlib.sha256(json.dumps(catalog,ensure_ascii=False,separators=(',',':')).encode()).hexdigest();c=case(split=split);c['catalog_hash']=h;conf=config();conf['catalog_hash']=h;coverage={'cases':1,'dataset_hash':r.fingerprint([c]),'counts':r.validate_dataset([c])['counts']};return [c],conf,coverage,path
    def test_frozen_dataset_and_source_fingerprints_enforced(self):
        cases,conf,coverage,path=self.valid_inputs();self.assertFalse(r.check_inputs(cases,conf,coverage,path,{})[2])
        with self.assertRaisesRegex(r.RunnerError,'COVERAGE'):r.check_inputs(cases,conf,{**coverage,'cases':2},path,{})
        conf['source_files']['scripts/run_nl_eval.py']='stale'
        with self.assertRaisesRegex(r.RunnerError,'SOURCE_FINGERPRINT'):r.check_inputs(cases,conf,coverage,path,{})
    def test_missing_runner_or_evaluator_source_is_rejected(self):
        for name in ['scripts/run_nl_eval.py','evals/scorer.py','src/server/assistant.ts','app/api/product-assistant/route.ts']:
            cases,conf,coverage,path=self.valid_inputs();del conf['source_files'][name]
            with self.assertRaisesRegex(r.RunnerError,'SOURCE_BINDING_REQUIRED'):r.check_inputs(cases,conf,coverage,path,{})
    def test_live_requires_actual_deployment_proof_content(self):
        cases,conf,coverage,path=self.valid_inputs();conf['mode']='live'
        with self.assertRaisesRegex(r.RunnerError,'SOURCE_PROOF_REQUIRED'):r.check_inputs(cases,conf,coverage,path,{})
        artifact=self.path/'deployment.json';artifact.write_text(json.dumps({'readyState':'READY','id':'dpl_test','url':'another.example','gitSource':{'sha':'s1'}}));conf['deployment_proof']={'origin':conf['origin'],'source_sha':'s1','artifact':str(artifact),'sha256':r.file_hash(artifact)}
        with self.assertRaisesRegex(r.RunnerError,'IMMUTABLE_DEPLOYMENT_PROOF'):r.check_inputs(cases,conf,coverage,path,{})
    def test_holdout_requires_explicit_flag_and_frozen_repeat_artifacts(self):
        cases,conf,coverage,path=self.valid_inputs('holdout')
        with self.assertRaisesRegex(r.RunnerError,'HOLDOUT_NOT_AUTHORIZED'):r.check_inputs(cases,conf,coverage,path,{})
        with self.assertRaisesRegex(r.RunnerError,'FROZEN_BEST_REQUIRED'):r.check_inputs(cases,conf,coverage,path,{},True,{})
        conf['mode']='live';proof=self.path/'local-proof.json';proof.write_text(json.dumps({'origin':conf['origin'],'source_sha':'s1','source_files':conf['source_files']}));conf['deployment_proof']={'kind':'local_exact_source','origin':conf['origin'],'source_sha':'s1','artifact':str(proof),'sha256':r.file_hash(proof)}
        best={'approved':True,'model':conf['model'],'source_sha':'s1','prompt_hash':conf['prompt_hash'],'catalog_hash':conf['catalog_hash'],'validation_run_ids':['v1','v2'],'validation_both_stage_ready':True}
        with self.assertRaisesRegex(r.RunnerError,'ARTIFACTS_REQUIRED'):r.check_inputs(cases,conf,coverage,path,{},True,best)
        vc=self.path/'validation-config.json';vc.write_text(json.dumps(conf));vs=self.path/'validation-states.json';vs.write_text('{}')
        best['validation_binding']={'config':{'path':str(vc),'sha256':r.file_hash(vc)},'state_fixtures':{'path':str(vs),'sha256':r.file_hash(vs)}}
        validation_fp=r.fingerprint({'runner':r.VERSION,'config':conf,'state_fixtures_hash':r.fingerprint({})})
        proofs=[]
        for rid in ['v1','v2']:
            p=self.path/(rid+'.json');p.write_text(json.dumps({'stage_ready':True,'run_id':rid,'mode':'live','catalog_hash':conf['catalog_hash'],'run_fingerprint':validation_fp,'dataset_hash':r.load_json(ROOT/'evals/validation-coverage.json')['dataset_hash']}));proofs.append({'path':str(p),'sha256':r.file_hash(p)})
        best['validation_reports']=proofs;self.assertTrue(r.check_inputs(cases,conf,coverage,path,{},True,best)[2])
        conf['max_attempts']=1
        with self.assertRaisesRegex(r.RunnerError,'CANDIDATE_MISMATCH'):r.check_inputs(cases,conf,coverage,path,{},True,best)
        conf['max_attempts']=3
        self.assertTrue(r.check_inputs(cases,conf,coverage,path,{},True,best)[2])
        del conf['max_attempts']
        old=dict(conf);old['model']='wrong-model';vc.write_text(json.dumps(old));best['validation_binding']['config']['sha256']=r.file_hash(vc)
        with self.assertRaisesRegex(r.RunnerError,'CANDIDATE_MISMATCH'):r.check_inputs(cases,conf,coverage,path,{},True,best)
        vc.write_text(json.dumps(conf));best['validation_binding']['config']['sha256']=r.file_hash(vc)
        for proof in proofs:
            report=r.load_json(proof['path']);report['run_fingerprint']='old-model-and-prompt';r.atomic_json(proof['path'],report);proof['sha256']=r.file_hash(proof['path'])
        with self.assertRaisesRegex(r.RunnerError,'CANDIDATE_PROOF_MISMATCH'):r.check_inputs(cases,conf,coverage,path,{},True,best)
    def test_unknown_error_code_does_not_echo_remote_secret(self):
        body=r.make_request(case(),[],config(),{},'r');attempt,_=r.parse_attempt({'status':500,'latency_ms':1,'body':failure('PRIVATE_SECRET_SENTINEL')},body,'customer',config(),{'SKU1'});self.assertEqual(attempt['code'],'INVALID_HTTP_ENVELOPE');self.assertNotIn('PRIVATE_SECRET',json.dumps(attempt))

    def test_fixture_mode_mismatch_still_accounts_observed_live_call(self):
        body=r.make_request(case(),[],config(),{},'r');response=success(body,config(mode='live'));attempt,_=r.parse_attempt({'status':200,'latency_ms':1,'body':response},body,'customer',config(),{'SKU1'});self.assertTrue(attempt['provider_called']);self.assertEqual(attempt['code'],'RESPONSE_VERSION_MISMATCH')

    def test_fixed_diagnostic_rules_preserve_original_failure_accounting(self):
        body=r.make_request(case(),[],config(),{},'r')
        rules=['OUTPUT_CONTRACT','OUTPUT_SCHEMA','CANDIDATE_LIMIT','CANDIDATE_DUPLICATE','CANDIDATE_UNKNOWN_ID','OUTPUT_TEXT_LIMIT','CANDIDATE_ACTION_CONTRACT','UNIDENTIFIED_ACTION_CONTRACT','CLARIFICATION_CONTRACT','EXACT_WITH_UNKNOWN_CONDITION','SUPPLIED_CATALOG_SCHEMA']
        for rule in rules:
            response=failure('INVALID_MODEL_RESPONSE');response['error']['diagnostic']=rule
            attempt,raw_value=r.parse_attempt({'status':502,'latency_ms':7,'body':response},body,'customer',config(),{'SKU1'})
            self.assertEqual(attempt['diagnostic'],rule);self.assertEqual(attempt['code'],'INVALID_MODEL_RESPONSE');self.assertEqual(attempt['status'],'failed');self.assertTrue(attempt['provider_called']);self.assertIsNone(attempt['usage']);self.assertIsNone(raw_value)

    def test_arbitrary_diagnostics_and_wrong_error_code_never_echo(self):
        body=r.make_request(case(),[],config(),{},'r')
        for value in [None,True,123,[],{},['OUTPUT_SCHEMA'],'OUTPUT_SCHEMA PRIVATE_SECRET','OUTPUT_SCHEMA\nPRIVATE_SECRET','private original user text','x'*10000]:
            response=failure('INVALID_MODEL_RESPONSE');response['error']['diagnostic']=value
            attempt,_=r.parse_attempt({'status':502,'latency_ms':1,'body':response},body,'customer',config(),{'SKU1'})
            self.assertNotIn('diagnostic',attempt);self.assertNotIn('PRIVATE_SECRET',json.dumps(attempt));self.assertNotIn('original user',json.dumps(attempt))
        response=failure('LLM_AUTH_ERROR');response['error']['diagnostic']='OUTPUT_SCHEMA'
        attempt,_=r.parse_attempt({'status':503,'latency_ms':1,'body':response},body,'customer',config(),{'SKU1'});self.assertNotIn('diagnostic',attempt);self.assertEqual(attempt['code'],'LLM_AUTH_ERROR')

    def test_diagnostic_http_journal_keeps_failure_and_adjacent_success(self):
        def callback(body,n,conf):
            if n==1:
                response=failure('INVALID_MODEL_RESPONSE');response['error'].update(diagnostic='CANDIDATE_UNKNOWN_ID',message='PRIVATE_SECRET original model text')
                return 502,response,{}
            return 200,success(body,conf),{}
        runner,server=self.runner([case(),case('C01-dev-002')],callback,mode='live');result=runner.run({'SKU1'},sleep=lambda _:None)
        self.assertEqual(len(server.requests),2);self.assertTrue(result['complete']);self.assertEqual(result['failed_cases'],1);self.assertEqual(result['transport_success_cases'],1);self.assertEqual(result['budget']['known_provider_calls'],2)
        obs=r.read_jsonl(runner.out/'observations.jsonl');self.assertEqual(obs[0]['attempts'][0]['diagnostic'],'CANDIDATE_UNKNOWN_ID');self.assertEqual(obs[0]['transport'],'error');self.assertEqual(obs[1]['transport'],'ok')
        self.assertNotIn('PRIVATE_SECRET',runner.checkpoint.read_text());self.assertNotIn('original model text',runner.checkpoint.read_text())

if __name__=='__main__':unittest.main()
