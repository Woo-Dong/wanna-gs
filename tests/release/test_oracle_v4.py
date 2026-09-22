import copy,json,sys,unittest
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'scripts'))
import rescore_public_oracle as r

class OracleV4Tests(unittest.TestCase):
    def setUp(self):
        self.cases=r.read_jsonl(ROOT/'evals/validation.jsonl')
        self.ref=r.ref(ROOT,ROOT/'evals/manifest-v4.json')
    def test_only_two_oracles_changed(self):
        n=r.corrected(self.cases);self.assertEqual([c['id'] for c,x in zip(n,self.cases) if c!=x],list(r.SLOTS));self.assertEqual(r.corrected(self.cases),n)
        for c in n:
            if c['id'] in r.SLOTS:
                z=c
                for k in r.SLOTS[c['id']]:z=z[k]
                self.assertEqual(z['candidate_pool'],r.PAIR);self.assertEqual(z['required_any_skus'],r.PAIR)
    def test_wrong_original_oracle_rejected(self):
        c=copy.deepcopy(self.cases);next(x for x in c if x['id'] in r.SLOTS)['expected']['candidate_pool']=['wrong']
        with self.assertRaisesRegex(ValueError,'ORIGINAL_ORACLE'):r.corrected(c)
    def test_question_shapes_no_text(self):
        for q in [None,'',' ','private question']:
            o={'response':{'action':'clarify','question':q},'attempts':[]}
            n=r.normalize(o);self.assertNotIn('private question',json.dumps(n));m=r.materialize(n)
            self.assertEqual(bool(q),bool(m['response']['question']));self.assertEqual(bool(str(q or '').strip()),bool(str(m['response']['question'] or '').strip()))
    def test_diagnostic_and_code_removed(self):
        n=r.normalize({'attempts':[{'status':'error','diagnostic':'secret','code':'sensitive','provider_called':True}]});self.assertNotIn('secret',json.dumps(n));self.assertNotIn('sensitive',json.dumps(n))
    def test_unrecognized_observation_key_rejected(self):
        with self.assertRaisesRegex(ValueError,'OBSERVATION_KEYS'):r.normalize({'authorization':'secret'})
    def test_unrecognized_response_key_rejected(self):
        with self.assertRaisesRegex(ValueError,'RESPONSE_KEYS'):r.normalize({'response':{'reason':'secret'}})
    def test_free_text_violations_rejected(self):
        for o in [{'domain_violations':['secret']},{'prior_responses':['secret']},{'response':{'forbidden_actions':['secret']}}]:
            with self.assertRaisesRegex(ValueError,'FREE_TEXT'):r.normalize(o)
    def test_invalid_question_shape_rejected(self):
        with self.assertRaisesRegex(ValueError,'QUESTION_SHAPE'):r.materialize({'response':{'question_shape':{'truthy':False,'nonempty':True}}})
    def test_prior_question_preserved(self):
        o={'prior_observations':[{'response':{'action':'clarify','question':'   '}}]};self.assertTrue(r.materialize(r.normalize(o))['prior_observations'][0]['response']['question'])
    def test_revision_checks_real_data(self):
        m=r.revision(ROOT,self.ref);self.assertEqual(m['public_datasets']['validation']['coverage']['path'],'evals/revisions/public-oracle-v4/validation-coverage.json')
    def test_revision_wrong_allowed_set_rejected(self):
        original=r.artifact
        def get(root,ref):
            v=original(root,ref)
            if ref==self.ref:v['allowed_skus']=v['allowed_skus'][:1]
            return v
        with patch.object(r,'artifact',get),self.assertRaisesRegex(ValueError,'PATCH_SCOPE'):r.revision(ROOT,self.ref)
    def test_revision_holdout_changed_rejected(self):
        original=r.artifact
        def get(root,ref):
            v=original(root,ref)
            if ref==self.ref:v['splits']['holdout']['dataset_hash']='0'*64
            return v
        with patch.object(r,'artifact',get),self.assertRaisesRegex(ValueError,'HOLDOUT_UNCHANGED'):r.revision(ROOT,self.ref)
    def test_revision_unrelated_input_change_rejected(self):
        original=r.rows
        def get(root,ref):
            v=original(root,ref)
            if '/revisions/' in ref['path']:v[0]['turns'][0]['text']='changed'
            return v
        with patch.object(r,'rows',get),self.assertRaisesRegex(ValueError,'EXACT_ORACLE_DIFF'):r.revision(ROOT,self.ref)
    def test_manifest_hash_mismatch_rejected(self):
        x=dict(self.ref,sha256='0'*64)
        with self.assertRaisesRegex(ValueError,'HASH'):r.revision(ROOT,x)
    def test_no_protected_prepare_path(self):
        with self.assertRaisesRegex(ValueError,'PRIVATE_SCOPE'):r.prepare(ROOT,ROOT/'artifacts/private/holdout')

    def test_scorer_ignored_boolean_string_rejected(self):
        with self.assertRaisesRegex(ValueError,'VALUE_BOOLEAN'):r.normalize({'response':{'raw_kind_valid':'SENTINEL_NON_ENUM_TEXT'}})
    def test_numeric_and_enum_free_text_rejected(self):
        values=[{'role':'secret'},{'response':{'action':'secret'}},{'attempts':[{'status':'secret'}]},{'attempts':[{'latency_ms':'secret'}]},{'response':{'candidate_ids':['secret']}},{'response':{'command':{'intent':'modify','scope':'policy','constraints':{'budgetLimitKrw':'secret'}}}}]
        for v in values:
            with self.assertRaisesRegex(ValueError,'VALUE_'):r.normalize(v)
    def test_usage_nan_and_bool_rejected(self):
        for v in [float('nan'),True,-1]:
            with self.assertRaisesRegex(ValueError,'VALUE_NUMBER'):r.normalize({'attempts':[{'cost_usd':v}]})
    def test_denied_path_never_hashed(self):
        for path in ['../outside.jsonl','artifacts/private/holdout.jsonl','/tmp/outside.jsonl','evals/holdout.jsonl']:
            with patch.object(r,'digest',side_effect=AssertionError('read attempted')):
                with self.assertRaises(ValueError):r.rows(ROOT,{'path':path,'sha256':'0'*64})
    def test_bad_decision_path_never_read(self):
        original=r.artifact
        def get(root,ref):
            v=original(root,ref)
            if ref==self.ref:v['decision']['path']='../secret'
            return v
        with patch.object(r,'artifact',get),self.assertRaisesRegex(ValueError,'DECISION_PATH'):r.revision(ROOT,self.ref)

class DerivedBundleTests(unittest.TestCase):
    def setUp(self):
        self.folder=ROOT/'quality/release/evidence/oracle-v4/revision-04'
        self.bundle=json.loads((self.folder/'n14-c11-validation-02/bundle.review-pending.json').read_text())
        self.auditref={'path':'docs/execution/run-20260921/test-audit.json','sha256':'1'*64}
        self.bundle['independent_review']=self.auditref
        inventory=json.loads((self.folder/'inventory.json').read_text())
        self.audit={'status':'PASS','reviewer':'independent','implementers':['method_auditor'],'private_full_replay_verified':True,'revision':self.bundle['revision'],'cohort':self.bundle['cohort'],'derivation_sha256':[e['derivation']['sha256'] for e in inventory['runs'] if 'derivation' in e]}
        self.original_artifact=r.artifact
    def read(self,root,ref):
        return copy.deepcopy(self.audit) if ref==self.auditref else self.original_artifact(root,ref)
    def test_current_c11_full_cohort_replay(self):
        with patch.object(r,'artifact',self.read):
            score,execution,binding=r.verify_bundle(ROOT,self.bundle,current=True)
        self.assertEqual(score['passed'],84);self.assertEqual(execution['quality_passed_cases'],83);self.assertNotEqual(score['dataset_hash'],execution['dataset_hash'])
    def test_missing_independent_review_blocks(self):
        b=copy.deepcopy(self.bundle);del b['independent_review']
        with self.assertRaises((ValueError,KeyError)):r.verify_bundle(ROOT,b)
    def test_same_author_blocks(self):
        self.audit['reviewer']='method_auditor'
        with patch.object(r,'artifact',self.read),self.assertRaisesRegex(ValueError,'AUDIT'):r.verify_bundle(ROOT,self.bundle)
    def test_one_run_omission_blocks(self):
        def read(root,ref):
            value=self.read(root,ref)
            if ref==self.bundle['cohort']:value['runs'].pop()
            return value
        with patch.object(r,'artifact',read),self.assertRaisesRegex(ValueError,'COHORT_COVERAGE'):r.verify_bundle(ROOT,self.bundle)
    def test_alias_binding_swap_blocks(self):
        b=copy.deepcopy(self.bundle);b['binding']=b['report']
        with self.assertRaisesRegex(ValueError,'ORIGINAL_ALIASES'):r.verify_bundle(ROOT,b,require_review=False)
    def test_forged_score_blocks(self):
        def read(root,ref):
            value=self.read(root,ref)
            if ref==self.bundle['report']:value['score']['tokens_known']+=1
            return value
        with patch.object(r,'artifact',read),self.assertRaisesRegex(ValueError,'DERIVED_SCORE'):r.verify_bundle(ROOT,self.bundle)
    def test_unrelated_source_change_blocks(self):
        binding=self.original_artifact(ROOT,self.bundle['original']['binding']);binding['config']['source_files']['src/server/provider.ts']='0'*64
        with self.assertRaisesRegex(ValueError,'APP_OR_SCORER_CHANGED'):r.source_compatible(ROOT,binding['config'])
    def test_checker_derived_branch_preserves_original(self):
        import check_release_evidence as g
        checker=g.Checker(ROOT);checker.runtime_hash=g.fingerprint(g.runtime_files(ROOT));b=self.original_artifact(ROOT,self.bundle['original']['binding']);c=b['config'];m=r.revision(ROOT,self.bundle['revision']);cov=r.artifact(ROOT,m['public_datasets']['validation']['coverage'])
        candidate={'id':'C11','runtimeHash':checker.runtime_hash,'sourceSha':c['source_sha'],'model':c['model'],'promptVersion':c['prompt_version'],'promptHash':c['prompt_hash'],'catalogHash':c['catalog_hash']}
        with patch.object(r,'artifact',self.read):report,execution=checker.nl(self.bundle,{'hash':cov['dataset_hash'],'cases':84,'counts':cov['counts']},True,candidate)
        self.assertEqual(report['passed'],84);self.assertEqual(execution['quality_passed_cases'],83)

    def frozen_fixture(self):
        first=json.loads((self.folder/'n14-c11-validation-01/bundle.review-pending.json').read_text());first['independent_review']=self.auditref
        refs=[{'path':'quality/test-first.json','sha256':'2'*64},{'path':'quality/test-second.json','sha256':'3'*64}]
        original_revision=r.revision
        def revision(root,ref):
            m=original_revision(root,ref);m['splits']['holdout']['dataset_hash']=r.fingerprint([]);return m
        def read(root,ref):
            if ref==refs[0]:return first
            if ref==refs[1]:return self.bundle
            return self.read(root,ref)
        config=copy.deepcopy(self.original_artifact(ROOT,self.bundle['original']['binding'])['config'])
        for path in r.SOURCE_EXCEPTIONS|{'scripts/rescore_public_oracle.py','evals/manifest-v4.json'}:config['source_files'][path]=r.digest(ROOT/path)
        frozen={'validation_rescore_bundles':refs,'oracle_revision':self.bundle['revision'],'validation_run_ids':['729d6477-6db9-4fd7-a9d0-960de3286b69','3acf1e6a-caee-4275-8c88-a1abc1a9f2c9'],'validation_both_stage_ready':True}
        return read,revision,config,frozen
    def test_holdout_derived_freeze_checks_without_protected_rows(self):
        read,revision,config,frozen=self.frozen_fixture()
        with patch.object(r,'artifact',read),patch.object(r,'revision',revision):reports=r.verify_holdout_freeze(ROOT,[],config,frozen)
        self.assertEqual([v['passed'] for v in reports],[84,84])
    def test_duplicate_validation_freeze_blocked(self):
        read,revision,config,frozen=self.frozen_fixture();frozen['validation_rescore_bundles'][1]=frozen['validation_rescore_bundles'][0]
        with patch.object(r,'artifact',read),patch.object(r,'revision',revision),self.assertRaisesRegex(ValueError,'INDEPENDENT_REPEATS'):r.verify_holdout_freeze(ROOT,[],config,frozen)
    def test_different_model_freeze_blocked(self):
        read,revision,config,frozen=self.frozen_fixture();config['model']='different-model'
        with patch.object(r,'artifact',read),patch.object(r,'revision',revision),self.assertRaisesRegex(ValueError,'CANDIDATE_IDENTITY'):r.verify_holdout_freeze(ROOT,[],config,frozen)
    def test_different_attempt_limit_freeze_blocked(self):
        read,revision,config,frozen=self.frozen_fixture();config['max_attempts']=3
        with patch.object(r,'artifact',read),patch.object(r,'revision',revision),self.assertRaisesRegex(ValueError,'ATTEMPT_LIMIT'):r.verify_holdout_freeze(ROOT,[],config,frozen)

    def test_original_execution_uncertainty_rejected_before_holdout(self):
        import check_release_evidence as g
        read,revision,config,frozen=self.frozen_fixture()
        target=self.bundle['original']['execution'];original_checker=g.Checker.artifact
        for key,value in [('pending_attempts',1),('attempted_cases',83),('known_tokens',-1),('unknown_provider_count',1),('runner_complete',False),('recorded_turns',91),('known_cost_usd',-1),('usage_unknown_attempts',1)]:
            def mutate(v,ref):
                if ref==target:v[key]=value
                return v
            def checker_read(instance,ref,json_required=True):return mutate(original_checker(instance,ref,json_required),ref)
            def read_changed(root,ref):return mutate(read(root,ref),ref)
            with self.subTest(key=key),patch.object(r,'artifact',read_changed),patch.object(r,'revision',revision),patch.object(g.Checker,'artifact',checker_read),self.assertRaises((ValueError,g.EvidenceError)):
                r.verify_holdout_freeze(ROOT,[],config,frozen)

if __name__=='__main__':unittest.main()
