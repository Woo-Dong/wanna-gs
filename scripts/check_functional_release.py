"""D50-only functional evidence gate; never relabels original G5 or runs models.
Pinned authority/runtime/failed-report identify this release, not a general waiver.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
from urllib.parse import urlparse
from check_release_evidence import (Checker, EvidenceError, digest, fingerprint,
    integer, relative, require, runtime_files, sanitized)

VERSION = 'FUNCTIONAL-RELEASE-v1'
SCOPE = 'D50-functional-release'
SOURCE = 'e727b99a640743c744082f8a3cf754260f0d755a'
RUNTIME = 'd49c13dcbe3f5b358b8f7fb80d4316a68fd738c9f83a0e6395ec6f56a5dfbb9d'
MODEL = 'gpt-4.1-mini-2025-04-14'
PROMPT = 'customer-classification-v11'
AUTHORITY = {'path':'docs/decisions/D50-functional-release.md',
             'sha256':'8c0ea80d9e4d1390047e1d31897e1da844c85fed9b394fbcf17dcf2ae8a30358'}
HOLDOUT = {'path':'quality/release/evidence/c11-holdout-v3/report.json',
           'sha256':'c6cf5196db67718d7635224942878ccebf1836ee00d3afa35d0286c61a896942'}

DISCLOSURE = {'path':'docs/execution/run-20260921/n16-known-limitations.md',
              'sha256':'4fd006b5438a6829dbb0d10ccd51ff5719bac93b80fe4df82c2da77907b29b69'}

def nonblank(value): return isinstance(value,str) and bool(value.strip())
def zero(value): return type(value) is int and value == 0

def evidence(checker, refs):
    require(isinstance(refs,list) and bool(refs),'EVIDENCE_REQUIRED')
    for ref in refs: checker.artifact(ref,False)

class FunctionalChecker(Checker):
    def check(self, manifest):
        path=Path(manifest)
        path=path.parent.resolve()/path.name
        require(path.is_relative_to(self.root),'UNSAFE_MANIFEST_PATH')
        m=json.loads(relative(self.root,path.relative_to(self.root).as_posix()).read_text())
        require(isinstance(m,dict),'MALFORMED_MANIFEST');sanitized(m)
        require(m.get('version')==VERSION and m.get('scope')==SCOPE,'FUNCTIONAL_SCOPE_REQUIRED')
        require(m.get('original_quality_status')=='NOT_READY' and m.get('optimization_status')=='stopped_by_user' and m.get('g6_status')=='pending','ORIGINAL_QUALITY_MUST_REMAIN_NOT_READY')
        require(m.get('user_authority')==AUTHORITY,'D50_AUTHORITY_REQUIRED')
        authority=relative(self.root,AUTHORITY['path']).read_bytes()
        require(digest(authority)==AUTHORITY['sha256'],'D50_AUTHORITY_HASH');sanitized(authority.decode())
        self.files=runtime_files(self.root);self.runtime_hash=fingerprint(self.files)
        require(self.runtime_hash==RUNTIME and m.get('runtime')=={'files':self.files,'sha256':self.runtime_hash},'FUNCTIONAL_RUNTIME_MISMATCH')
        c=m.get('candidate');require(isinstance(c,dict),'CANDIDATE_REQUIRED')
        require(c.get('id')=='C11' and c.get('sourceSha')==SOURCE and c.get('runtimeHash')==self.runtime_hash and c.get('model')==MODEL and c.get('promptVersion')==PROMPT,'FUNCTIONAL_CANDIDATE_MISMATCH')
        require(c.get('promptHash')==self.files['src/server/prompts.ts'],'CANDIDATE_PROMPT_STALE')
        catalog=json.loads(relative(self.root,'data/seed/products.json').read_text())
        require(c.get('catalogHash')==digest(json.dumps(catalog,ensure_ascii=False,separators=(',',':')).encode()),'CANDIDATE_CATALOG_STALE')
        limits=m.get('known_limitations');require(isinstance(limits,dict),'KNOWN_LIMITATIONS_REQUIRED')
        require(limits.get('holdout_report')==HOLDOUT,'ORIGINAL_HOLDOUT_REQUIRED')
        h=self.artifact(limits['holdout_report'])
        require(h.get('mode')=='live' and type(h.get('cases')) is int and h['cases']==84 and type(h.get('passed')) is int and h['passed']==75 and h.get('nl_minimum_pass') is False and h.get('stage_ready') is False and h.get('catalog_hash')==c['catalogHash'],'ORIGINAL_HOLDOUT_FAILURE_HIDDEN')
        require(limits.get('ux_comparison_status')=='not_run' and limits.get('original_quality_status')=='NOT_READY','UX_OR_QUALITY_DISCLOSURE_REQUIRED')
        require(isinstance(limits.get('disclosure_evidence'),list) and DISCLOSURE in limits['disclosure_evidence'],'PINNED_DISCLOSURE_REQUIRED')
        evidence(self,limits['disclosure_evidence'])
        preview=self.artifact(m.get('preview'))
        url=preview.get('url','');parsed=urlparse(url if '://' in url else 'https://'+url)
        require(preview.get('readyState')=='READY' and preview.get('target') in (None,'preview') and nonblank(preview.get('id')) and preview.get('gitSource',{}).get('sha')==SOURCE and parsed.scheme=='https' and bool(parsed.hostname) and parsed.username is None and parsed.password is None and not parsed.query and not parsed.fragment,'FUNCTIONAL_PREVIEW_MISMATCH')
        refs=m.get('role_qa');require(isinstance(refs,list) and len(refs)==2,'TWO_ROLE_QA_REQUIRED')
        roles=set();reviewers=set()
        for ref in refs:
            q=self.qa(ref,c) # G5-scoped component evidence; not whole-G5 approval.
            require(q.get('role') in {'customer','merchant'} and q['role'] not in roles and q['reviewer'] not in reviewers,'DISTINCT_ROLE_QA_REQUIRED')
            require(all(nonblank(x) for x in q['implementers']) and nonblank(q['reviewer']),'QA_IDENTITY_REQUIRED')
            roles.add(q['role']);reviewers.add(q['reviewer'])
            require(q.get('source_sha')==SOURCE and q.get('model')==MODEL and q.get('prompt_version')==PROMPT and q.get('catalog_hash')==c['catalogHash'] and q.get('deployment_id')==preview['id'],'QA_DEPLOYMENT_BINDING')
            require(all(zero(q.get(k)) for k in ('failures','mandatory_errors','not_run','unresolved_major')),'QA_MAJOR_FAILURE_OR_MISSING')
            planned=6 if q['role']=='customer' else 11
            require(type(q.get('checks_planned')) is int and q['checks_planned']==planned and q['checks_executed']==planned and type(q.get('provider_calls')) is int and q['provider_calls']==3,'QA_FIXED_PLAN_INCOMPLETE')
            if q['role']=='customer':
                require(type(q.get('fixture_checks_planned')) is int and q['fixture_checks_planned']==12 and type(q.get('fixture_checks_executed')) is int and q['fixture_checks_executed']==12 and all(zero(q.get(k)) for k in ('fixture_failures','fixture_not_run','fixture_actual_model_calls')),'CUSTOMER_FIXTURE_BOUNDARIES_REQUIRED')
        policies=m.get('policy_reviews');require(isinstance(policies,list) and len(policies)==2,'TWO_FUNCTIONAL_POLICY_REVIEWS_REQUIRED')
        reviewers=set();perspectives=set()
        for ref in policies:
            p=self.artifact(ref)
            require(p.get('scope')==SCOPE and p.get('status')=='PASS' and zero(p.get('unresolved_major')) and p.get('candidate_id')=='C11' and p.get('runtime_hash')==self.runtime_hash,'FUNCTIONAL_POLICY_NOT_READY')
            require(nonblank(p.get('reviewer')) and nonblank(p.get('perspective')) and p['reviewer'] not in reviewers and p['perspective'] not in perspectives,'DISTINCT_POLICY_REVIEWERS_REQUIRED')
            reviewers.add(p['reviewer']);perspectives.add(p['perspective']);evidence(self,p.get('evidence'))
        return {'version':VERSION,'scope':SCOPE,'status':'PASS','original_quality_status':'NOT_READY','optimization_status':'stopped_by_user','g6_status':'pending','candidate_id':'C11','source_sha':SOURCE,'runtime_hash':self.runtime_hash,'artifacts_checked':len(self.checked),'truth_limit':'Functional evidence consistency only; original G5 quality remains NOT_READY. Unsigned evidence is not cryptographic execution proof.'}

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1]);ap.add_argument('--manifest',default='quality/release/functional-manifest.json');args=ap.parse_args()
    try:
        name=Path(args.manifest);require(not name.is_absolute() and '..' not in name.parts,'UNSAFE_MANIFEST_PATH')
        require((args.root/name).is_file(),'FUNCTIONAL_MANIFEST_NOT_READY')
        result=FunctionalChecker(args.root).check(args.root/name)
    except (EvidenceError,KeyError,TypeError,ValueError,OSError,AttributeError) as error:
        result={'version':VERSION,'scope':SCOPE,'status':'NOT_READY','original_quality_status':'NOT_READY','g6_status':'pending','error':str(error) if isinstance(error,EvidenceError) else 'MALFORMED_OR_UNREADABLE_EVIDENCE'}
        print(json.dumps(result,ensure_ascii=False));return 1
    print(json.dumps(result,ensure_ascii=False));return 0
if __name__=='__main__':raise SystemExit(main())
