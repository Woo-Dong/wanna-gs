"""Synthetic isolated ledgers only. No network/provider and no production goal-ledger writes."""
import importlib.util,json,shutil,tempfile,unittest,os
from pathlib import Path
HERE=Path(__file__).resolve().parent;SOURCE=Path(os.environ.get('UX_BUDGET_TEST_ROOT',str(HERE.parents[1])))
spec=importlib.util.spec_from_file_location('bridge',HERE/'budget_bridge.py');b=importlib.util.module_from_spec(spec);spec.loader.exec_module(b)
class BridgeTests(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name);(self.root/'scripts').mkdir();(self.root/'evals').mkdir()
  for name in ['scripts/run_nl_eval.py','evals/adapter.py','evals/scorer.py']:shutil.copy(SOURCE/name,self.root/name)
  self.ledger=self.root/'artifacts/private/run-20260921/nl-budget.json';self.ledger.parent.mkdir(parents=True)
  self.ledger.write_text(json.dumps({'version':'E02-v1','prior_call_reserve':50,'prior_actual_calls':'unknown','prior_cost_reserve_usd':2.5,'prior_actual_cost_usd':'unknown','unknown_attempt_cost_reserve_usd':.05,'attempts':{},'holdout_claims':{}}))
  self.cfg={'approved':True,'run_id':'synthetic-only','stage':'baseline','prior_call_reserve':50,'authorized_calls':18,'mandatory_reserve':{'future':10},'mandatory_cost_reserve_usd':1,'origin':'http://localhost:3217','model':'synthetic-model','prompt_version':'v1','catalog_hash':'h'};self.path=self.root/'config.json';self.write();self.token=''
 def tearDown(self):self.temp.cleanup()
 def write(self):self.path.write_text(json.dumps(self.cfg))
 def call(self,op,**payload):return b.run(self.root,self.path,op,{'token':self.token,**payload})
 def begin(self):self.token=self.call('begin',output='private-test',workloadHash='w')['token']
 def response(self):return {'ok':True,'data':{'mode':'live','model':'synthetic-model','promptVersion':'v1','catalogHash':'h','usage':{'inputTokens':2,'outputTokens':1,'totalTokens':3,'estimatedCostUsd':.001}}}
 def test_authorization_required_before_claim(self):
  self.cfg['approved']=False;self.write()
  with self.assertRaisesRegex(ValueError,'AUTHORIZATION'):self.begin()
  self.assertEqual(json.loads(self.ledger.read_text())['attempts'],{})
 def test_pending_no_replay_and_claim_cannot_restart(self):
  self.begin();self.call('reserve')
  with self.assertRaisesRegex(ValueError,'UNCERTAIN_PENDING'):self.call('reserve')
  with self.assertRaisesRegex(ValueError,'ALREADY_CLAIMED'):self.begin()
 def test_unknown_timeout_preserves_null_and_stops_next_call(self):
  self.begin();aid=self.call('reserve')['attemptId'];out=self.call('finish',attemptId=aid,response=None,httpStatus=0);self.assertFalse(out['continue']);self.assertIsNone(out['observation']['usage']);self.assertIsNone(out['observation']['provider_called']);self.assertIsNone(out['observation']['cost_usd'])
  with self.assertRaisesRegex(ValueError,'STOPPED'):self.call('reserve')
  item=json.loads(self.ledger.read_text())['attempts'][aid];self.assertEqual(item['status'],'unknown');self.assertIsNone(item['cost'])
 def test_known_error_unknown_usage_preserves_provider_attempt(self):
  self.begin();aid=self.call('reserve')['attemptId'];out=self.call('finish',attemptId=aid,response={'ok':False,'error':{'attempt':{'providerCalled':True,'mode':'live','usage':None}}},httpStatus=429);self.assertTrue(out['observation']['provider_called']);self.assertIsNone(out['observation']['usage']);self.assertFalse(out['continue'])
 def test_hard_authorized_cap_and_known_usage(self):
  self.begin()
  for _ in range(18):
   aid=self.call('reserve')['attemptId'];out=self.call('finish',attemptId=aid,response=self.response(),httpStatus=200);self.assertTrue(out['continue'])
  with self.assertRaisesRegex(ValueError,'AUTHORIZED_CALL_LIMIT'):self.call('reserve')
  state=json.loads(self.ledger.read_text());self.assertEqual(len(state['attempts']),18);self.assertTrue(all(a['provider_called'] is True for a in state['attempts'].values()))
 def test_future_call_reserve_and_cost_stop_before_attempt(self):
  for key,value,reason in [('mandatory_reserve',{'future':2400},'CALL_RESERVE_STOP'),('mandatory_cost_reserve_usd',18,'COST_SOFT_STOP')]:
   self.cfg['run_id']=key;self.cfg[key]=value;self.write();self.begin()
   with self.assertRaisesRegex(Exception,reason):self.call('reserve')
   self.cfg['mandatory_reserve']={'future':10};self.assertEqual(len(json.loads(self.ledger.read_text())['attempts']),0)
 def test_mismatched_model_never_success_and_auth_change_rejected(self):
  self.begin();aid=self.call('reserve')['attemptId'];response=self.response();response['data']['model']='other';self.assertFalse(self.call('finish',attemptId=aid,response=response,httpStatus=200)['continue']);self.cfg['authorized_calls']=19;self.write()
  with self.assertRaisesRegex(ValueError,'AUTHORIZATION_CHANGED'):self.call('reserve')
if __name__=='__main__':unittest.main(verbosity=2)
