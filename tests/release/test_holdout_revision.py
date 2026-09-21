"""Synthetic metadata fixtures only; no protected examples or model calls."""
import copy
import tempfile
import unittest
from test_release_evidence import Package,gate,H

class HoldoutRevisionTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.p=Package(self.tmp.name);self.path='evals/manifest-v2.json'
        old=self.p.read({'path':'evals/manifest.json'})
        old.update(catalog_size=248,total_cases=420)
        old['splits'].update(dev={'dataset_hash':H('dev'),'family_hashes':[H('dev-family')]},validation={'dataset_hash':H('validation'),'family_hashes':[H('validation-family')]})
        old['splits']['holdout'].update(user_turns=92,worst_attempts=276,family_hashes=[H('retired-family')])
        self.p.write('evals/manifest.json',old);self.old=old
        report=self.p.art('retired-report',{'dataset_hash':old['splits']['holdout']['dataset_hash'],'cases':84,'nl_minimum_pass':False})
        bundle=self.p.art('retired-bundle',{'role':'holdout_aggregate','report':report})
        new=copy.deepcopy(old);new['splits']['holdout'].update(dataset_hash=H('fresh-holdout'),family_hashes=[H('fresh-family')])
        review=self.p.art('data-review',dict(status='PASS',reviewer='independent-data-reviewer',implementers=['dataset-author'],dataset_hash=H('fresh-holdout'),previous_dataset_hash=old['splits']['holdout']['dataset_hash'],semantic_family_overlap=0,difficulty_equivalent=True,thresholds_unchanged=True,protected_content_not_published=True))
        new.update(version='EVAL-20260921-v2',revision='holdout-v2-c6',status='frozen',archived_cases=84,frozenAt='2026-09-21T01:00:00Z',predecessor_manifest={'path':'evals/manifest.json','sha256':gate.digest((self.p.root/'evals/manifest.json').read_bytes())},retired_holdouts=[dict(revision='v1',dataset_hash=old['splits']['holdout']['dataset_hash'],file_sha256=H('private-retired-file'),status='FAIL',replay_authorized=False,retired_reason='Used aggregate in later hypothesis',execution_evidence=bundle)],independent_data_review=review)
        self.value=new
        self.value['label_counts']={'customer':{'clear':40,'uncertain':20},'merchant':{'clear':15,'uncertain':9}}
    def check(self):
        self.p.write(self.path,self.value)
        return gate.Checker(self.p.root).eval_manifest({'path':self.path,'sha256':gate.digest((self.p.root/self.path).read_bytes())},self.p.catalog)
    def reject(self,code):
        with self.assertRaisesRegex(gate.EvidenceError,code):self.check()
    def test_revision_keeps_public_splits_and_retired_failure(self):
        self.assertEqual(self.check()['splits']['dev'],self.old['splits']['dev'])
        self.assertEqual(gate.Checker(self.p.root).eval_manifest(None,self.p.catalog),self.old)
    def test_unfrozen_replacement_and_changed_original_rejected(self):
        self.value['status']='review_pending';self.reject('NOT_FROZEN');self.value['status']='frozen'
        self.value['predecessor_manifest']['sha256']=H('new-original');self.reject('PREDECESSOR')
    def test_public_validation_cannot_change(self):
        self.value['splits']['validation']['dataset_hash']=H('changed');self.reject('PUBLIC_SPLIT')
    def test_denominator_and_turns_cannot_shrink(self):
        self.value['splits']['holdout']['user_turns']=91;self.reject('COVERAGE')
        self.value['splits']['holdout']['user_turns']=92;self.value['splits']['holdout']['cases']=83;self.reject('COVERAGE')
    def test_label_denominators_must_match_the_original_contract(self):
        self.value['label_counts']['merchant'].update(clear=14,uncertain=10);self.reject('LABEL_COUNTS')
    def test_same_dataset_and_overlapping_family_rejected(self):
        self.value['splits']['holdout']['dataset_hash']=self.old['splits']['holdout']['dataset_hash'];self.reject('COVERAGE')
        self.value['splits']['holdout']['dataset_hash']=H('fresh-holdout');self.value['splits']['holdout']['family_hashes']=[H('dev-family')];self.reject('FAMILY')
    def test_old_failure_and_no_replay_are_required(self):
        self.value['retired_holdouts'][0]['replay_authorized']=True;self.reject('HISTORY')
        self.value['retired_holdouts'][0]['replay_authorized']=False
        b=self.p.read(self.value['retired_holdouts'][0]['execution_evidence'])
        self.p.mutate(b['report'],lambda r:r.update(nl_minimum_pass=True))
        self.p.mutate(self.value['retired_holdouts'][0]['execution_evidence'],lambda r:r.update(report=b['report']))
        self.reject('FAILURE_NOT_PRESERVED')
    def test_independence_correct_revision_difficulty_and_thresholds(self):
        ref=self.value['independent_data_review'];original=self.p.read(ref)
        for delta in [dict(status='FAIL'),dict(reviewer='dataset-author'),dict(dataset_hash=H('wrong')),dict(semantic_family_overlap=1),dict(semantic_family_overlap=False),dict(difficulty_equivalent=False),dict(thresholds_unchanged=False),dict(protected_content_not_published=False)]:
            self.p.mutate(ref,lambda r:r.update({**original,**delta}));self.reject('DATA_REVIEW')
    def test_reference_cannot_point_to_private_or_unhashed_manifest(self):
        for ref in [{'path':'artifacts/private/fake.json','sha256':H('fake')},{'path':self.path,'sha256':'bad'}]:
            with self.assertRaisesRegex(gate.EvidenceError,'REFERENCE'):gate.Checker(self.p.root).eval_manifest(ref,self.p.catalog)

if __name__=='__main__':unittest.main()
