import copy
import importlib.util
import unittest
from pathlib import Path
spec=importlib.util.spec_from_file_location('eval_scorer',Path(__file__).parents[1]/'scorer.py')
s=importlib.util.module_from_spec(spec);spec.loader.exec_module(s)
CAT={'sku-a','sku-b','sku-c'}
def case():
 return {'id':'case-1','role':'customer','category':'C01','split':'validation','family_id':'family-1','origin':'synthetic_expansion','research_ids':['RC-01'],'scenario_id':'SC-01','catalog_hash':'catalog-rev','binding_status':'verified','label':'clear','turns':[{'role':'user','text':'유효 상품'}],'max_model_turns':1,'expected':{'allowed_actions':['candidates'],'required_any_skus':['sku-a'],'candidate_pool':['sku-a'],'minimum_candidates':1}}
def obs():
 return {'case_id':'case-1','role':'customer','mode':'fixture','run_fingerprint':'run-a','transport':'ok','schema_valid':True,'response':{'action':'candidates','candidate_ids':['sku-a'],'confirmation_required':True},'attempts':[]}
class ScorerTest(unittest.TestCase):
 def test_valid_normal_case_and_fixture_are_distinct(self):
  r=s.evaluate([case()],[obs()],CAT);self.assertTrue(r['nl_minimum_pass']);self.assertFalse(r['live_evidence']);self.assertEqual(r['product_gates'],'not_assessed')
 def test_zero_case_never_passes(self):self.assertFalse(s.evaluate([],[],CAT)['nl_minimum_pass'])
 def test_missing_case_fails_and_denominator_remains(self):
  r=s.evaluate([case()],[],CAT);self.assertEqual(r['cases'],1);self.assertEqual(r['incomplete'],1);self.assertFalse(r['nl_minimum_pass'])
 def test_unverified_binding_fails(self):
  c=case();c['binding_status']='pending';self.assertFalse(s.evaluate([c],[obs()],CAT)['nl_minimum_pass'])
 def test_fabricated_sku_and_automatic_choice_are_mandatory(self):
  o=obs();o['response']['candidate_ids']=['sku-a','fake'];o['response']['confirmed_sku']='sku-a';r=s.score_case(case(),o,CAT);self.assertFalse(r['passed']);self.assertIn('fabricated_sku',r['mandatory']);self.assertIn('unconfirmed_customer_choice',r['mandatory'])
 def test_correct_candidate_missing_and_unnecessary_clarification_fail(self):
  o=obs();o['response']={'action':'clarify','question':'다시 말해주세요'};r=s.score_case(case(),o,CAT);self.assertIn('unnecessary_clarification',r['reasons']);self.assertFalse(r['passed'])
 def test_wrong_candidate_with_correct_candidate_does_not_pass(self):
  o=obs();o['response']['candidate_ids']=['sku-b','sku-a'];self.assertFalse(s.score_case(case(),o,CAT)['passed'])
 def test_no_confirmation_path_fails(self):
  o=obs();del o['response']['confirmation_required'];self.assertFalse(s.score_case(case(),o,CAT)['passed'])
 def test_duplicate_and_unexpected_observation_fail(self):
  self.assertFalse(s.evaluate([case()],[obs(),obs()],CAT)['nl_minimum_pass']);o=obs();o['case_id']='alien';self.assertFalse(s.evaluate([case()],[o],CAT)['nl_minimum_pass'])
 def test_stale_dataset_and_run_fingerprint_fail(self):
  self.assertFalse(s.evaluate([case()],[obs()],CAT,'stale')['nl_minimum_pass']);self.assertFalse(s.evaluate([case()],[obs()],CAT,run_fingerprint='run-b')['nl_minimum_pass'])
 def test_schema_transport_failure_not_accepted(self):
  for field,val in [('transport','timeout'),('schema_valid',False)]:
   o=obs();o[field]=val;r=s.evaluate([case()],[o],CAT);self.assertFalse(r['nl_minimum_pass']);self.assertEqual(r['incomplete'],1)
 def test_cross_split_family_and_identical_utterance_detected(self):
  c=case();d=copy.deepcopy(c);d.update(id='case-2',split='holdout');r=s.validate_dataset([c,d],CAT);self.assertIn('family_split_overlap',r['errors']);self.assertIn('identical_utterance_split_overlap',r['errors'])
 def test_merchant_partial_field_match_is_failure(self):
  c=case();c.update(role='merchant',category='M02');c['expected']={'allowed_actions':['propose'],'command':{'intent':'modify','scope':'once','budget_won':20000,'excluded_skus':['sku-a']}}
  o=obs();o.update(role='merchant');o['response']={'action':'propose','confirmation_required':True,'command':dict(c['expected']['command'])};self.assertTrue(s.score_case(c,o,CAT)['passed']);o['response']['command']['budget_won']=30000;self.assertFalse(s.score_case(c,o,CAT)['passed'])
 def test_merchant_type_confusion_does_not_pass(self):
  self.assertFalse(s.strict_equal({'budget_won':1},{'budget_won':True}));self.assertFalse(s.strict_equal({'budget_won':1000},{'budget_won':'1000'}))
 def test_full_dataset_minimums_not_faked_by_one_case(self):self.assertFalse(s.validate_dataset([case()],CAT,require_full=True)['valid'])
 def test_live_mode_cannot_consume_fixture_or_no_provider(self):
  self.assertFalse(s.evaluate([case()],[obs()],CAT,mode='live')['nl_minimum_pass']);o=obs();o['mode']='live';self.assertFalse(s.evaluate([case()],[o],CAT,mode='live')['nl_minimum_pass'])
 def test_attempts_account_retries_and_unknown_usage(self):
  o=obs();o['mode']='live';o['attempts']=[{'provider_called':True,'status':'timeout','latency_ms':45000},{'provider_called':True,'status':'ok','latency_ms':4000,'usage':{'total_tokens':100}},{'provider_called':False,'status':'401'}];r=s.evaluate([case()],[dict(o,run_id='id-a')],CAT,mode='live',run_fingerprint='run-a',run_id='id-a');self.assertTrue(r['nl_minimum_pass']);self.assertEqual(r['outbound_attempts'],2);self.assertEqual(r['tokens_known'],100);self.assertEqual(r['usage_unknown_attempts'],1);self.assertEqual(r['latency_p95_ms'],45000)
 def test_domain_violations_are_never_offset(self):
  o=obs();o['domain_violations']=['consent'];self.assertFalse(s.evaluate([case()],[o],CAT)['nl_minimum_pass'])
 def test_budget_reserve_preserved(self):
  self.assertFalse(s.reserve_check(2200,100,150)['allowed']);self.assertTrue(s.reserve_check(2200,50,150)['allowed']);self.assertRaises(ValueError,s.reserve_check,0,-1,0)
 def test_oracle_unknown_sku_fails(self):
  c=case();c['expected']['required_any_skus']=['fake'];self.assertFalse(s.validate_dataset([c],CAT)['valid'])
 def test_stale_catalog_fails_even_when_id_exists(self):
  self.assertFalse(s.evaluate([case()],[obs()],CAT,catalog_hash="changed-name-revision")['nl_minimum_pass'])
 def test_alternative_is_not_wrong_primary_but_unknown_alternative_fails(self):
  o=obs();o['response']['alternative_ids']=['sku-b'];self.assertTrue(s.score_case(case(),o,CAT)['passed']);o['response']['alternative_ids']=['fake'];self.assertFalse(s.score_case(case(),o,CAT)['passed'])
 def test_candidate_cannot_improve_by_changing_dataset(self):
  r=s.evaluate([case()],[obs()],CAT);c=copy.deepcopy(r);c['dataset_hash']='other';self.assertFalse(s.compare_candidate(r,c)['adoptable'])
 def test_one_repeat_cannot_hide_second_failure(self):
  r=s.evaluate([case()],[obs()],CAT);bad=s.evaluate([case()],[],CAT);self.assertFalse(s.repeat_ready(r,r));a=dict(r,run_id='one',run_fingerprint='x',stage_ready=True);b=dict(r,run_id='two',run_fingerprint='x',stage_ready=True);self.assertTrue(s.repeat_ready(a,b));self.assertFalse(s.repeat_ready(a,dict(b,run_fingerprint='y')));self.assertFalse(s.repeat_ready(r,bad))
 def test_latency_adoption_requires_no_correctness_regression(self):
  r=s.evaluate([case()],[obs()],CAT);r['latency_p95_ms']=1000;c=copy.deepcopy(r);c['latency_p95_ms']=850;self.assertTrue(s.compare_candidate(r,c)['adoptable']);c['passed']=0;self.assertFalse(s.compare_candidate(r,c)['adoptable'])
 def test_earlier_bad_turn_not_erased_by_final_success(self):
  o=obs();o['prior_observations']=[{'transport':'ok','schema_valid':True,'response':{'action':'candidates','candidate_ids':['invented']}}];r=s.score_case(case(),o,CAT);self.assertIn('earlier_fabricated_sku',r['mandatory']);self.assertFalse(r['passed'])
 def test_model_turn_upper_bound_must_cover_dialogue(self):
  c=case();c['turns'].append({'role':'user','text':'정정합니다'});self.assertIn('model_turn_bound_too_small',s.validate_case(c,CAT))
 def test_empty_prior_does_not_fake_success(self):
  c=case();c['turns'].append({'role':'user','text':'다시요'});c['max_model_turns']=2;o=obs();o['prior_observations']=[{}];self.assertFalse(s.evaluate([c],[o],CAT)['nl_minimum_pass'])
 def test_timeout_only_does_not_fake_live_success(self):
  o=obs();o.update(mode='live',run_id='id-a');o['attempts']=[{'provider_called':True,'status':'timeout'}];self.assertFalse(s.evaluate([case()],[o],CAT,mode='live',run_id='id-a',run_fingerprint='run-a')['nl_minimum_pass'])
 def test_missing_pool_rejects_wrong_primary(self):
  c=case();del c['expected']['candidate_pool'];o=obs();o['response']['candidate_ids']=['sku-a','sku-b'];self.assertFalse(s.evaluate([c],[o],CAT)['nl_minimum_pass'])
 def test_partial_metrics_are_not_stage_ready(self):
  r=s.evaluate([case()],[obs()],CAT);self.assertTrue(r['nl_minimum_pass']);self.assertFalse(r['stage_ready']);self.assertEqual(r['evaluation_scope'],'partial_metrics')
 def test_ambiguous_prior_then_clear_final_is_valid(self):
  c=case();c['turns'].append({'role':'user','text':'명확한 답변'});c['max_model_turns']=2;c['expected_prior']=[{'allowed_actions':['clarify']}];o=obs();o['prior_observations']=[{'case_id':c['id'],'role':c['role'],'transport':'ok','schema_valid':True,'response':{'action':'clarify','question':'어떤 맛인가요?'}}];self.assertTrue(s.evaluate([c],[o],CAT)['nl_minimum_pass']);o['prior_observations'][0]['case_id']='alien';self.assertFalse(s.evaluate([c],[o],CAT)['nl_minimum_pass'])
if __name__=='__main__':unittest.main(verbosity=2)
