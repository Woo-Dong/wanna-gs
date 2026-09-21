"""ADR007 public evidence counterexamples; all evidence is synthetic temp data."""
import unittest,copy
from test_release_evidence import Package,gate,H
class V3Tests(unittest.TestCase):
 def setUp(self):
  import tempfile
  self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.p=Package(self.tmp.name)
  self.hh={}
  for name in ('run.mts','plan.mjs','metrics.mjs','binding.mjs','live.mts','budget_bridge.py','seed.mts','v2-metrics.mjs'):
   f='tests/ux-benchmark/'+('seed.mts' if name=='seed.mts' else 'metrics.mjs' if name=='v2-metrics.mjs' else 'v3/'+name);self.p.write(f,b'synthetic harness');self.hh[name]=gate.digest(b'synthetic harness')
  hist=[];self.history=[]
  for rid,digest,attempted,passed,failed,notrun in [('ux-baseline-b0-v2-01','4989b1053468134ff8a3099b951493ba483687f57fb14de49db48ea4e87b4209',3,2,1,21),('ux-baseline-b0-v2-recovery-01','2b9839efff2d118b48751642e7382b41d6e41fa49b837ccb4beff56fd1433c4b',12,11,1,12)]:
   h=dict(runId=rid,originalSha256=digest,planned=24,attempted=attempted,passed=passed,failed=failed,notRun=notrun);self.history.append(h)
   rows=[{'workload':w,'repetition':n,'status':'PASS'} for w in gate.WORKLOADS for n in (1,2,3)][:attempted];rows[-1]['status']='FAIL';hist.append(self.p.art(rid,dict(h,mode='live',complete=False,runs=rows)))
  self.p.m['ux']={'version':'UX-BENCHMARK-v3','baseline':self.arm(False),'best':self.arm(True),'history':hist,'plannedTotals':{'historicalBaseline':48,'newBaseline':56,'newBest':56,'total':160}}
 def arm(self,best):
  v=self.p.read(self.p.ux(best));v.update(version='UX-BENCHMARK-v3',studyId='ux-study-v3-01',planHash='515a97609bc51b3ebb463bd5e7b5bd3814b6241b99ad50750741a7ea1a1da386',runId='ux-best-v3-01' if best else 'ux-baseline-b0-v3-01',clock=1789959600000,history=self.history,pendingAttempts=0,budgetRunnerHash=gate.digest((self.p.root/'scripts/run_nl_eval.py').read_bytes()),budgetSourceFiles={n:gate.digest((self.p.root/n).read_bytes()) for n in ('scripts/run_nl_eval.py','evals/adapter.py','evals/scorer.py')},harnessHashes=self.hh,sourceSha=self.p.candidate['sourceSha'] if best else '10c00723d0b64ea47a06dcbd00e2b671e7c62daf',model=self.p.candidate['model'] if best else 'gpt-5-mini-2025-08-07',promptVersion='p' if best else 'baseline-v1',catalogHash=self.p.catalog)
  rows=[];usage=[]
  for wi,w in enumerate(gate.WORKLOADS):
   planned=2 if w=='ambiguous' else 1 if w.startswith('clear-') or w=='auto-normal' else 0
   for rep in range(1,8):
    row=dict(workload=w,repetition=rep,status='PASS',attempted=True,plannedModelCalls=planned,durableHash=H('db'),observedClock=v['clock'],activations=5,screenTransitions=0,questions=0,merchantPerOrderApprovals=0 if w=='auto-normal' else 1,elapsedMs=200,modelNetworkMs=15*planned,budgetInstrumentationMs=5*planned,nonModelMs=200-20*planned,unchangedReviewCheck='PASS',network=[],modelSteps=[])
    for i in range(planned):
     aid=str(len(usage));o={'status':'ok','provider_called':True,'usage':{'input_tokens':1,'output_tokens':1,'total_tokens':2},'cost_usd':.001};usage.append(dict(attemptId=aid,**o));row['network'].append(dict(attemptId=aid,mode='live',start=1+30*i,networkStart=3+30*i,networkEnd=18+30*i,end=22+30*i,budgetInstrumentationMs=5,observation=o));row['modelSteps'].append({'status':'PASS','attemptId':aid})
    rows.append(row)
  v.update(runs=rows,liveUsage=usage,outboundAttempts=len(usage),modelCalls=len(usage));return self.p.art('v3-best' if best else 'v3-baseline',v)
 def mutate(self,arm,fn):self.p.mutate(self.p.m['ux'][arm],fn)
 def reject(self,code):
  with self.assertRaisesRegex(gate.EvidenceError,code):self.p.check()
 def test_v3_all56_success_and_v2_still_separately_supported(self):self.assertEqual(self.p.check()['status'],'PASS')
 def test_best_all_success_cannot_have_zero_provider_calls(self):
  def update(v):
   for item in v['liveUsage']:item['provider_called']=False
   for row in v['runs']:
    for network in row['network']:network['observation']['provider_called']=False
   v['modelCalls']=0
  self.mutate('best',update);self.reject('V3_SUCCESS_REQUIRES_LIVE_PROVIDER')
 def test_baseline_success_also_requires_actual_provider(self):
  def update(v):
   v['liveUsage'][0]['provider_called']=False;v['runs'][0]['network'][0]['observation']['provider_called']=False;v['modelCalls']-=1
  self.mutate('baseline',update);self.reject('V3_SUCCESS_REQUIRES_LIVE_PROVIDER')
 def test_failed_baseline_known_not_called_observation_preserved(self):
  def update(v):
   row=v['runs'][0];observation={'status':'failed','provider_called':False,'usage':{'input_tokens':0,'output_tokens':0,'total_tokens':0},'cost_usd':0}
   v['liveUsage'][0].update(observation);row['network'][0]['observation']=observation;row['modelSteps'][0]['status']='FAIL';row.update(status='FAIL',error='known accounted failure before provider call');v['modelCalls']-=1
  self.mutate('baseline',update);self.assertEqual(self.p.check()['status'],'PASS')
 def test_failed_ui_trial_cannot_relabel_nonprovider_as_success(self):
  def update(v):
   row=v['runs'][0];row.update(status='FAIL',error='UI failure');v['liveUsage'][0]['provider_called']=False;row['network'][0]['observation']['provider_called']=False;v['modelCalls']-=1
  self.mutate('baseline',update);self.reject('V3_SUCCESS_REQUIRES_LIVE_PROVIDER')
 def test_baseline_three_success_each_with_failures_allowed(self):
  self.mutate('baseline',lambda v:[r.update(status='FAIL',error='known SQL assertion') for r in v['runs'] if r['repetition']<=4]);self.assertEqual(self.p.check()['status'],'PASS')
 def test_best_one_failure_rejects(self):self.mutate('best',lambda v:v['runs'][0].update(status='FAIL',error='known'));self.reject('V3_BEST_FAILURE')
 def test_baseline_two_success_rejects(self):self.mutate('baseline',lambda v:[r.update(status='FAIL',error='known') for r in v['runs'][:5]]);self.reject('V3_INSUFFICIENT')
 def test_stop_precedes_other_success(self):self.mutate('baseline',lambda v:v.update(stopCode='AUTH'));self.reject('V3_STUDY_STOP')
 def test_pending_cannot_be_ignored(self):self.mutate('best',lambda v:v.update(pendingAttempts=1));self.reject('V3_STUDY_STOP')
 def test_missing_actual_attempt_even_with56rows(self):self.mutate('baseline',lambda v:v['runs'][0].update(attempted=False));self.reject('V3_ORDER_OR_UNATTEMPTED')
 def test_duplicate_repetition(self):self.mutate('best',lambda v:v['runs'][1].update(repetition=1));self.reject('V3_ORDER')
 def test_original_failure_removed_rejects(self):self.p.mutate(self.p.m['ux']['history'][0],lambda v:v['runs'][-1].update(status='PASS'));self.reject('V3_HISTORY_FAILURES')
 def test_history_original_hash_and_denominator_binding(self):self.p.mutate(self.p.m['ux']['history'][0],lambda v:v.update(originalSha256=H('invented')));self.reject('V3_HISTORY_SOURCE')
 def test_old48_new112_totals_required(self):self.p.m['ux']['plannedTotals']['total']=112;self.reject('V3_TOTAL_PLANNED')
 def test_unknown_usage_on_failed_baseline_stops(self):self.mutate('baseline',lambda v:v['liveUsage'][0].update(usage=None));self.reject('V3_UNKNOWN_USAGE')
 def test_unperformed_model_step_cannot_be_pass(self):self.mutate('best',lambda v:v['runs'][0]['modelSteps'][0].update(attemptId='none'));self.reject('V3_MODEL_STEP_BINDING')
 def test_stale_harness_and_budget_runner_reject(self):self.mutate('best',lambda v:v.update(budgetRunnerHash=H('old15')));self.reject('V3_BUDGET_SOURCE_STALE')
 def test_budget_import_dependency_cannot_be_omitted(self):self.mutate('best',lambda v:v['budgetSourceFiles'].pop('evals/adapter.py'));self.reject('V3_BUDGET_DEPENDENCY_STALE')
 def test_budget_import_dependency_cannot_be_stale(self):self.mutate('baseline',lambda v:v['budgetSourceFiles'].update({'evals/scorer.py':H('changed')}));self.reject('V3_BUDGET_DEPENDENCY_STALE')
 def test_full_current_runtime_required(self):self.mutate('best',lambda v:v.update(sourceSha='b'*40));self.reject('V3_CURRENT_CANDIDATE')
 def test_same_old_baseline_model_and_source(self):self.mutate('baseline',lambda v:v.update(model='new-best'));self.reject('V3_B0_SOURCE')
 def test_all_success_times_used_not_first_three(self):
  def update(v):
   for row in v['runs']:
    if row['repetition']>=4:row.update(elapsedMs=300,nonModelMs=300-row['modelNetworkMs']-row['budgetInstrumentationMs'])
  self.mutate('best',update);self.reject('UX_REGRESSION')
 def test_failed_trial_remaining_model_turn_can_be_not_run(self):
  def update(v):
   row=v['runs'][21];second=row['network'].pop();row['modelSteps'][1]={'status':'NOT_RUN','attemptId':None};row.update(status='FAIL',error='known failure before second turn');v['liveUsage']=[a for a in v['liveUsage'] if a['attemptId']!=second['attemptId']];v['outboundAttempts']-=1;v['modelCalls']-=1
  self.mutate('baseline',update);self.assertEqual(self.p.check()['status'],'PASS')
if __name__=='__main__':unittest.main()
