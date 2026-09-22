import copy
import tempfile
import unittest
from pathlib import Path
from gate_contract import validate, fingerprint

class GateContractTests(unittest.TestCase):
    def setUp(self):
        self.config = {'phase':'bootstrap','checks':[{'id':'unit','tests':True},{'id':'live','live':True}], 'tasks':[{'id':'B01','implementers':['root'],'requirements':['CORE-16']}]}
        self.report = {'phase':'bootstrap','fingerprint':'current','purpose':'consent to pickup','normal_case':'valid request succeeds','adjacent_regressions':['retry'], 'checks':[{'id':'unit','status':'PASS','exit_code':0,'fingerprint':'current','tests':2,'skipped':0,'failures':0,'errors':0},{'id':'live','status':'PASS','exit_code':0,'fingerprint':'current','mode':'live'}]}
        self.review = [{'task':'B01','reviewer':'independent','status':'PASS','fingerprint':'current','purpose_preserved':True,'evidence':['independently executed'], 'requirements':['CORE-16']}]
    def assertRejected(self):
        self.assertTrue(validate(self.config,self.report,self.review,'current'))
    def test_valid_executed_and_independent_report(self):
        self.assertEqual(validate(self.config,self.report,self.review,'current'),[])
    def test_child_missing(self):
        self.report['checks'].pop(); self.assertRejected()
    def test_stale_parent_child_review(self):
        for target in (self.report,self.report['checks'][0],self.review[0]):
            target['fingerprint']='old'; self.assertRejected(); target['fingerprint']='current'
    def test_zero_skip_fail_error_never_pass(self):
        for field, value in [('tests',0),('skipped',1),('failures',1),('errors',1)]:
            saved=copy.deepcopy(self.report); self.report['checks'][0][field]=value; self.assertRejected(); self.report=saved
    def test_nonpass_states_rejected(self):
        for state in ('not_run','stale','BLOCKED','FAIL','not_applicable'):
            self.report['checks'][0]['status']=state; self.assertRejected()
    def test_failed_command_overrides_claimed_pass(self):
        self.report['checks'][0]['exit_code']=1; self.assertRejected()
    def test_fixture_cannot_replace_live(self):
        self.report['checks'][1]['mode']='fixture'; self.assertRejected()
    def test_same_implementer_is_not_independent(self):
        self.review[0]['reviewer']='root'; self.assertRejected()
    def test_missing_review(self):
        self.review=[]; self.assertRejected()
    def test_coverage_cannot_be_dropped(self):
        self.review[0]['requirements']=[]; self.assertRejected()
    def test_purpose_and_normal_regression_required(self):
        for field in ('purpose','normal_case','adjacent_regressions'):
            saved=self.report.pop(field); self.assertRejected(); self.report[field]=saved
        self.review[0]['purpose_preserved']=False; self.assertRejected()
    def test_scope_mismatch(self):
        self.report['phase']='release'; self.assertRejected()
    def test_duplicate_child_id(self):
        self.report['checks'].append(self.report['checks'][0]); self.assertRejected()
    def test_missing_counts_and_bool_are_rejected(self):
        saved=copy.deepcopy(self.report)
        for field in ('tests','skipped','failures','errors'):
            del self.report['checks'][0][field]; self.assertRejected(); self.report=copy.deepcopy(saved)
            self.report['checks'][0][field]=True; self.assertRejected(); self.report=copy.deepcopy(saved)
    def test_false_string_and_blank_evidence_rejected(self):
        self.review[0]['purpose_preserved']='false'; self.assertRejected()
        self.review[0]['purpose_preserved']=True
        for evidence in (' ', [' '], [], None):
            self.review[0]['evidence']=evidence; self.assertRejected()
    def test_duplicate_review_cannot_mask_failure(self):
        failed=copy.deepcopy(self.review[0]); failed['status']='FAIL'
        self.review.insert(0,failed); self.assertRejected()
    def test_context_ack_must_match(self):
        self.config['context_manifest']='current.json'; self.assertRejected()
        self.report['context_manifest']='current.json'; self.assertRejected()
        self.review[0]['context_manifest']='current.json'
        self.assertEqual(validate(self.config,self.report,self.review,'current'),[])
    def test_fingerprint_detects_content_path_and_addition(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d); (root/'quality').mkdir(); (root/'quality/gates.json').write_text('{"source_patterns":["*.ts"]}')
            p=root/'one.ts'; p.write_text('a'); first=fingerprint(root)
            p.write_text('b'); self.assertNotEqual(first,fingerprint(root))
            p.write_text('a'); self.assertEqual(first,fingerprint(root))
            p.rename(root/'two.ts'); self.assertNotEqual(first,fingerprint(root))
            (root/'extra.ts').write_text('a'); self.assertNotEqual(first,fingerprint(root))
if __name__=='__main__': unittest.main()
