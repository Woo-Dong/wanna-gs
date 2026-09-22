"""Synthetic temporary artifacts only; no models, ledger, real QA or protected data."""
import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'scripts'))
import check_functional_release as gate
spec=importlib.util.spec_from_file_location('functional_test_fixtures',Path(__file__).with_name('test_release_evidence.py'))
fixtures=importlib.util.module_from_spec(spec);spec.loader.exec_module(fixtures)

class FunctionalTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.p=fixtures.Package(self.tmp.name);p=self.p
        p.candidate.update(id='C11',sourceSha=gate.SOURCE,model=gate.MODEL,promptVersion=gate.PROMPT)
        authority={'path':'docs/decisions/D50-functional-release.md','sha256':gate.digest(b'Synthetic user authority, never a real authorization')}
        p.write(authority['path'],b'Synthetic user authority, never a real authorization')
        failed=p.art('original-failed-holdout',dict(mode='live',cases=84,passed=75,nl_minimum_pass=False,stage_ready=False,catalog_hash=p.catalog))
        for name,value in [('RUNTIME',p.runtime),('AUTHORITY',authority),('HOLDOUT',failed),('DISCLOSURE',p.note)]:
            change=patch.object(gate,name,value);change.start();self.addCleanup(change.stop)
        qrefs=[]
        for role,n in [('customer',6),('merchant',11)]:
            qrefs.append(p.art('functional-'+role,dict(role=role,scope='G5',provider='openai',coverage=['CORE-17'],reviewer='review-'+role,implementers=['builder'],status='PASS',mode='live',actual_browser=True,actual_sql=True,provider_calls=3,runtime_hash=p.runtime,candidate_id='C11',failures=0,mandatory_errors=0,checks_executed=n,checks_planned=n,not_run=0,unresolved_major=0,evidence=[p.note],source_sha=gate.SOURCE,model=gate.MODEL,prompt_version=gate.PROMPT,catalog_hash=p.catalog,deployment_id='dpl_test',**({'fixture_checks_planned':12,'fixture_checks_executed':12,'fixture_failures':0,'fixture_not_run':0,'fixture_actual_model_calls':0} if role=='customer' else {}))))
        policies=[p.art('functional-policy-'+x,dict(scope=gate.SCOPE,reviewer='policy-'+x,perspective=x,status='PASS',unresolved_major=0,runtime_hash=p.runtime,candidate_id='C11',evidence=[p.note])) for x in ['product','state']]
        self.m=dict(version=gate.VERSION,scope=gate.SCOPE,original_quality_status='NOT_READY',optimization_status='stopped_by_user',g6_status='pending',user_authority=authority,runtime={'files':p.files,'sha256':p.runtime},candidate=p.candidate,known_limitations={'holdout_report':failed,'ux_comparison_status':'not_run','original_quality_status':'NOT_READY','disclosure_evidence':[p.note]},role_qa=qrefs,policy_reviews=policies,preview=p.art('functional-preview',dict(id='dpl_test',url='https://test.vercel.app',readyState='READY',target=None,gitSource={'sha':gate.SOURCE})))
    def check(self):
        name='quality/release/functional-manifest.json';self.p.write(name,self.m)
        return gate.FunctionalChecker(self.p.root).check(self.p.root/name)
    def reject(self,pattern):
        with self.assertRaisesRegex(gate.EvidenceError,pattern):self.check()
    def test_synthetic_pass_never_g5_or_g6_pass(self):
        out=self.check();self.assertEqual(out['scope'],gate.SCOPE);self.assertEqual(out['status'],'PASS');self.assertEqual(out['original_quality_status'],'NOT_READY');self.assertEqual(out['g6_status'],'pending')
    def test_manifest_absent_cli_fails_closed(self):
        out=subprocess.run([sys.executable,str(ROOT/'scripts/check_functional_release.py'),'--root',str(self.p.root)],capture_output=True,text=True)
        self.assertEqual(out.returncode,1);self.assertEqual(json.loads(out.stdout)['status'],'NOT_READY')
    def test_malformed_cli_fails_closed(self):
        self.p.write('quality/release/functional-manifest.json',b'{broken')
        out=subprocess.run([sys.executable,str(ROOT/'scripts/check_functional_release.py'),'--root',str(self.p.root)],capture_output=True,text=True)
        self.assertEqual(out.returncode,1);self.assertEqual(json.loads(out.stdout)['error'],'MALFORMED_OR_UNREADABLE_EVIDENCE')
    def test_original_status_and_optimization_and_g6_cannot_be_relabelled(self):
        for key,value in [('scope','G5'),('original_quality_status','PASS'),('optimization_status','complete'),('g6_status','PASS')]:
            with self.subTest(key=key):
                old=self.m[key];self.m[key]=value;self.reject('SCOPE|QUALITY');self.m[key]=old
    def test_authority_absent_wrong_and_tampered(self):
        original=copy.deepcopy(self.m['user_authority']);self.m['user_authority']=None;self.reject('AUTHORITY')
        self.m['user_authority']=original;self.p.write(original['path'],b'changed');self.reject('AUTHORITY_HASH')
    def test_runtime_changed_even_with_rehashed_manifest(self):
        self.p.write('src/extra.ts',b'new');files=gate.runtime_files(self.p.root)
        self.m['runtime']={'files':files,'sha256':gate.fingerprint(files)};self.reject('RUNTIME_MISMATCH')
    def test_candidate_model_prompt_catalog_source(self):
        for key in ['sourceSha','model','promptVersion','catalogHash','promptHash']:
            with self.subTest(key=key):
                old=self.m['candidate'][key];self.m['candidate'][key]='changed';self.reject('CANDIDATE');self.m['candidate'][key]=old
    def test_original_failure_content_cannot_be_changed(self):
        ref=self.m['known_limitations']['holdout_report'];self.p.write(ref['path'],{'cases':84,'passed':84});self.reject('ARTIFACT_HASH')
    def test_failure_and_ux_disclosures_cannot_be_omitted(self):
        for key in ['holdout_report','ux_comparison_status','original_quality_status','disclosure_evidence']:
            with self.subTest(key=key):
                old=self.m['known_limitations'].pop(key);self.reject('REQUIRED');self.m['known_limitations'][key]=old
    def test_qa_missing_fixture_and_unperformed(self):
        ref=self.m['role_qa'][0];original=self.p.read(ref)
        for changes in [{'mode':'fixture'},{'actual_browser':False},{'actual_sql':False},{'provider_calls':0},{'provider_calls':1},{'provider_calls':2},{'provider_calls':4},{'provider_calls':True},{'checks_executed':5},{'not_run':1},{'unresolved_major':1},{'failures':True}]:
            with self.subTest(changes=changes):
                self.p.mutate(ref,lambda q:q.update(changes));self.reject('QA_');self.p.write(ref['path'],original);ref['sha256']=gate.digest((self.p.root/ref['path']).read_bytes())
        self.m['role_qa'].pop();self.reject('TWO_ROLE')
    def test_customer_fixture_twelve_and_zero_model_are_mandatory(self):
        ref=self.m['role_qa'][0];original=self.p.read(ref)
        for key,value in [('fixture_checks_planned',None),('fixture_checks_executed',11),('fixture_failures',1),('fixture_not_run',1),('fixture_actual_model_calls',1),('fixture_actual_model_calls',False)]:
            with self.subTest(key=key,value=value):
                self.p.mutate(ref,lambda q:q.update({key:value}));self.reject('CUSTOMER_FIXTURE');self.p.write(ref['path'],original);ref['sha256']=gate.digest((self.p.root/ref['path']).read_bytes())
    def test_qa_independence_duplicate_role_or_reviewer(self):
        ref=self.m['role_qa'][1];original=self.p.read(ref)
        for changes in [{'role':'customer'},{'reviewer':'review-customer'},{'reviewer':'builder'}]:
            self.p.mutate(ref,lambda q:q.update(changes));self.reject('INDEPENDENT|DISTINCT');self.p.write(ref['path'],original);ref['sha256']=gate.digest((self.p.root/ref['path']).read_bytes())
    def test_qa_source_model_deployment_bindings(self):
        ref=self.m['role_qa'][0];original=self.p.read(ref)
        for key in ['source_sha','model','prompt_version','catalog_hash','deployment_id']:
            self.p.mutate(ref,lambda q:q.update({key:'stale'}));self.reject('QA_DEPLOYMENT_BINDING');self.p.write(ref['path'],original);ref['sha256']=gate.digest((self.p.root/ref['path']).read_bytes())
    def test_policy_major_bool_missing_and_stale(self):
        ref=self.m['policy_reviews'][0];original=self.p.read(ref)
        for changes in [{'unresolved_major':1},{'unresolved_major':False},{'status':'NOT_RUN'},{'runtime_hash':'old'},{'scope':'G5'},{'evidence':[]}]:
            self.p.mutate(ref,lambda q:q.update(changes));self.reject('POLICY|EVIDENCE');self.p.write(ref['path'],original);ref['sha256']=gate.digest((self.p.root/ref['path']).read_bytes())
    def test_policy_duplicate_reviewer_or_perspective(self):
        ref=self.m['policy_reviews'][1];original=self.p.read(ref)
        for changes in [{'reviewer':'policy-product'},{'perspective':'product'}]:
            self.p.mutate(ref,lambda q:q.update(changes));self.reject('DISTINCT_POLICY');self.p.write(ref['path'],original);ref['sha256']=gate.digest((self.p.root/ref['path']).read_bytes())
    def test_preview_wrong_source_not_ready_http_or_secret_url(self):
        ref=self.m['preview'];original=self.p.read(ref)
        for changes in [{'gitSource':{'sha':'b'*40}},{'readyState':'BUILDING'},{'url':'http://test.vercel.app'},{'url':'https://user:pass@test.vercel.app'}]:
            self.p.mutate(ref,lambda q:q.update(changes));self.reject('PREVIEW');self.p.write(ref['path'],original);ref['sha256']=gate.digest((self.p.root/ref['path']).read_bytes())
    def test_private_or_secret_evidence_rejected_before_read(self):
        self.m['known_limitations']['disclosure_evidence'].append({'path':'artifacts/private/not-opened.json','sha256':'a'*64});self.reject('PRIVATE_PATH')
    def test_tampered_policy_evidence_ref_hash(self):
        self.p.write(self.m['policy_reviews'][0]['path'],{});self.reject('ARTIFACT_HASH')

if __name__=='__main__':unittest.main()
