import importlib.util,json,pathlib,tempfile,shutil,unittest,hashlib
HERE=pathlib.Path(__file__).resolve().parent;SOURCE=HERE.parents[2]
s=importlib.util.spec_from_file_location('v3bridge',HERE/'budget_bridge.py');b=importlib.util.module_from_spec(s);s.loader.exec_module(b)
class BridgeTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.root=pathlib.Path(self.tmp.name).resolve()
  for f in ['scripts/run_nl_eval.py','evals/adapter.py','evals/scorer.py']:
   to=self.root/f;to.parent.mkdir(parents=True,exist_ok=True);shutil.copy(SOURCE/f,to)
  self.ledger=self.root/'artifacts/private/run-20260921/nl-budget.json';self.ledger.parent.mkdir(parents=True);self.ledger.write_text(json.dumps({'version':'E02-v1','prior_call_reserve':50,'prior_actual_calls':'unknown','prior_cost_reserve_usd':2.5,'prior_actual_cost_usd':'unknown','unknown_attempt_cost_reserve_usd':.05,'attempts':{},'holdout_claims':{}}))
  self.c={'approved':True,'study_id':b.STUDY,'run_id':b.RUNS['baseline'],'stage':'baseline','authorized_calls':42,'prior_call_reserve':50,'budget_root':str(self.root),'budget_runner_hash':hashlib.sha256((self.root/'scripts/run_nl_eval.py').read_bytes()).hexdigest(),'budget_source_files':{f:hashlib.sha256((self.root/f).read_bytes()).hexdigest() for f in b.BUDGET_SOURCES},'output':'synthetic-only','mandatory_reserve':{'future':50},'mandatory_cost_reserve_usd':1,'origin':'http://localhost:3217','model':'synthetic','prompt_version':'p','catalog_hash':'h','plan_hash':'ph','workload_hash':'wh'};self.path=self.root/'config';self.save();self.token=''
 def save(self):self.path.write_text(json.dumps(self.c))
 def call(self,op,**p):return b.run(self.root,self.path,op,{'token':self.token,**p})
 def begin(self):self.token=self.call('begin',output='synthetic-only',workloadHash=self.c['workload_hash'])['token']
 def start(self,i):self.call('trial.begin',index=i)
 def response(self,good=True,code='INVALID_MODEL_RESPONSE'):
  data={'mode':'live','model':'synthetic','promptVersion':'p','catalogHash':'h','usage':{'inputTokens':2,'outputTokens':1,'totalTokens':3,'estimatedCostUsd':.001}}
  return {'ok':True,'data':data} if good else {'ok':False,'error':{'code':code,'attempt':dict(data,providerCalled=True)}}
 def attempt(self,good=True,**kw):
  aid=self.call('reserve')['attemptId'];return self.call('finish',attemptId=aid,response=self.response(good,**kw),httpStatus=200 if good else 502)
 def test_accounted_failure_trial_can_continue_without_retry(self):
  self.begin();self.start(0);r=self.attempt(False);self.assertTrue(r['trialFailed']);self.assertIsNone(r['stopCode'])
  with self.assertRaisesRegex(ValueError,'V3_RESERVE_STOP'):self.call('reserve')
  with self.assertRaisesRegex(ValueError,'FAILED_TRIAL'):self.call('trial.end',status='PASS')
  self.call('trial.end',status='FAIL');self.start(1);self.assertFalse(self.attempt()['trialFailed']);self.call('trial.end',status='PASS')
 def test_all_56_and_42_then_distinct_best_claim(self):
  self.begin()
  for i in range(56):
   self.start(i)
   for _ in range(2 if 21<=i<28 else 1 if i<21 or 42<=i<49 else 0):self.attempt()
   self.call('trial.end',status='PASS')
  done=self.call('complete');self.assertTrue(done['complete']);self.assertEqual(done['budget']['known_provider_calls'],42)
  with self.assertRaisesRegex(ValueError,'ALREADY_CLAIMED'):self.begin()
  self.c.update(stage='best',run_id=b.RUNS['best']);self.save();self.begin()
 def test_unknown_stops_both_arms(self):
  self.begin();self.start(0);aid=self.call('reserve')['attemptId'];r=self.call('finish',attemptId=aid,response=None,httpStatus=0);self.assertIsNotNone(r['stopCode']);self.assertIsNone(r['observation']['usage']);self.assertFalse(self.call('complete')['complete'])
  self.c.update(stage='best',run_id=b.RUNS['best']);self.save()
  with self.assertRaisesRegex(ValueError,'STUDY_STOPPED'):self.begin()
 def test_known_auth_quota_and_model_contract_stop(self):
  self.begin();self.start(0);r=self.attempt(False,code='LLM_QUOTA');self.assertIsNotNone(r['stopCode'])
 def test_success_wrong_model_is_study_stop(self):
  self.begin();self.start(0);aid=self.call('reserve')['attemptId'];r=self.response();r['data']['model']='wrong';self.assertIsNotNone(self.call('finish',attemptId=aid,response=r,httpStatus=200)['stopCode'])
 def test_pending_blocks_next_reserve_and_completion(self):
  self.begin();self.start(0);self.call('reserve')
  with self.assertRaisesRegex(ValueError,'RESERVE_STOP'):self.call('reserve')
  done=self.call('complete');self.assertTrue(done['pending']);self.assertFalse(done['complete'])
 def test_budget_future_reserve_and_20_dollar_cap(self):
  self.c['mandatory_cost_reserve_usd']=15.4;self.save();self.begin();self.start(0)
  # 2.5 prior + 42*.05 + 15.4 = 20, stop without outbound.
  with self.assertRaisesRegex(Exception,'COST_SOFT_STOP'):self.call('reserve')
  self.assertEqual(json.loads(self.ledger.read_text())['attempts'],{})
 def test_fixed_ids_source_root_and_approval(self):
  for key,value in [('approved',False),('run_id','retry-id'),('authorized_calls',43),('budget_root','/other'),('budget_runner_hash','bad')]:
   old=self.c[key];self.c[key]=value;self.save()
   with self.assertRaises(ValueError):self.begin()
   self.c[key]=old;self.save()
 def test_wrong_order_and_config_cannot_resume(self):
  self.begin()
  with self.assertRaisesRegex(ValueError,'TRIAL_SEQUENCE'):self.start(1)
  self.c['mandatory_cost_reserve_usd']=2;self.save()
  with self.assertRaisesRegex(ValueError,'AUTHORIZATION_CHANGED'):self.start(0)
 def test_imported_budget_dependencies_missing_changed_or_removed(self):
  before=self.ledger.read_bytes()
  for name in b.BUDGET_SOURCES:
   value=self.c['budget_source_files'].pop(name);self.save()
   with self.assertRaisesRegex(ValueError,'BUDGET_SOURCE'):self.begin()
   self.c['budget_source_files'][name]=value;self.save()
  (self.root/'evals/scorer.py').write_text('# changed')
  with self.assertRaisesRegex(ValueError,'BUDGET_SOURCE'):self.begin()
  self.assertEqual(self.ledger.read_bytes(),before)
 def test_begin_output_and_workload_must_match_config(self):
  for payload in [dict(output='wrong',workloadHash='wh'),dict(output='synthetic-only',workloadHash='wrong')]:
   with self.assertRaisesRegex(ValueError,'CLAIM_BINDING'):self.call('begin',**payload)
  self.begin()
 def test_auth_http_cannot_hide_behind_known_usage(self):
  self.begin();self.start(0);aid=self.call('reserve')['attemptId']
  response=self.response(False,code='RATE_LIMITED')
  self.assertIsNotNone(self.call('finish',attemptId=aid,response=response,httpStatus=403)['stopCode'])
if __name__=='__main__':unittest.main(verbosity=2)
