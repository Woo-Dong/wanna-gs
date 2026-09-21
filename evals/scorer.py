"""Independent offline scoring. Never calls a provider or reads holdout implicitly."""
from __future__ import annotations
import argparse
import hashlib
import json
import math
from collections import Counter, defaultdict
from pathlib import Path

VERSION = "EVAL-20260921-v1"
ROLES = {"customer", "merchant"}
SPLITS = {"dev", "validation", "holdout"}
ACTIONS = {"candidates", "clarify", "unidentified", "reject", "propose", "execute"}
THRESHOLDS = {"clear": .95, "uncertain": .90}


def fingerprint(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def read_jsonl(path):
    with open(path, encoding="utf-8") as stream:
        return [json.loads(line) for line in stream if line.strip()]


def validate_case(case, catalog_ids=None):
    errors = []
    required = {"id", "role", "category", "split", "family_id", "origin", "research_ids", "scenario_id", "catalog_hash", "binding_status", "label", "turns", "max_model_turns", "expected"}
    missing = required - case.keys()
    if missing:
        return ["missing:" + ",".join(sorted(missing))]
    for key in ("id", "family_id", "category", "scenario_id", "catalog_hash"):
        if not isinstance(case[key], str) or not case[key]: errors.append("invalid:" + key)
    if case["role"] not in ROLES: errors.append("invalid:role")
    elif case["category"] not in {( "C" if case["role"]=="customer" else "M")+f"{i:02}" for i in range(1,10)}: errors.append("invalid:category")
    if case["split"] not in SPLITS: errors.append("invalid:split")
    if case["label"] not in {"clear", "ambiguous", "unidentified", "out_of_scope", "injection"}: errors.append("invalid:label")
    if case["binding_status"] != "verified": errors.append("unverified_catalog_binding")
    if case["origin"] not in {"evidence_backed", "synthetic_expansion"}: errors.append("invalid:origin")
    if not isinstance(case["research_ids"], list) or not case["research_ids"]: errors.append("missing:research_ids")
    if not isinstance(case["turns"], list) or not case["turns"] or any(not isinstance(t, dict) or t.get("role") not in {"user", "assistant"} or not isinstance(t.get("text"), str) or not t["text"].strip() for t in case["turns"]): errors.append("invalid:turns")
    prior_count=max(0,sum(t.get("role")=="user" for t in case["turns"] if isinstance(t,dict))-1)
    if len(case.get("expected_prior",[]))!=prior_count: errors.append("missing_prior_turn_oracles")
    bound = case["max_model_turns"]
    if type(bound) is not int or bound < 1: errors.append("invalid:max_model_turns")
    elif bound < sum(t.get("role")=="user" for t in case["turns"] if isinstance(t,dict)): errors.append("model_turn_bound_too_small")
    exp = case["expected"]
    if not isinstance(exp, dict): return errors + ["invalid:expected"]
    allowed = exp.get("allowed_actions")
    if not isinstance(allowed, list) or not allowed or not set(allowed) <= ACTIONS: errors.append("invalid:allowed_actions")
    if "execute" in (allowed or []): errors.append("model_cannot_authorize_execution")
    sku_fields = ["required_any_skus", "candidate_pool"]
    for key in sku_fields:
        ids = exp.get(key, [])
        if not isinstance(ids, list) or any(not isinstance(x, str) for x in ids): errors.append("invalid:" + key)
        elif catalog_ids is not None and not set(ids) <= set(catalog_ids): errors.append("unknown_oracle_sku:" + key)
    if case["role"] == "customer" and case["label"] == "clear":
        if not exp.get("required_any_skus"): errors.append("missing:clear_customer_oracle")
        if not exp.get("candidate_pool"): errors.append("missing:clear_customer_candidate_pool")
    if case["role"] == "merchant" and case["label"] == "clear" and (not isinstance(exp.get("command"), dict) or not exp["command"]): errors.append("missing:clear_merchant_oracle")
    return errors


def validate_dataset(cases, catalog_ids=None, require_full=False):
    errors = []
    if not cases: return {"valid": False, "errors": ["zero_cases"], "counts": {}}
    ids = Counter(c.get("id") for c in cases)
    if any(n != 1 for n in ids.values()): errors.append("duplicate_case_id")
    families = defaultdict(set)
    texts = defaultdict(set)
    counts = Counter()
    for case in cases:
        ce = validate_case(case, catalog_ids)
        errors.extend(f"{case.get('id','?')}:{e}" for e in ce)
        families[case.get("family_id")].add(case.get("split"))
        for turn in case.get("turns", []):
            if isinstance(turn,dict) and turn.get("role")=="user":
                normalized="".join(turn.get("text", "").lower().split())
                texts[normalized].add(case.get("split"))
        counts[(case.get("role"), case.get("split"), case.get("category"))] += 1
    if any(len(s)>1 for s in families.values()): errors.append("family_split_overlap")
    if any(len(s)>1 for t,s in texts.items() if t): errors.append("identical_utterance_split_overlap")
    if require_full:
        for role, total in (("customer",300),("merchant",120)):
            if sum(n for (r,s,c),n in counts.items() if r==role)!=total: errors.append(f"{role}:total_mismatch")
            for split, nominal in (("dev",int(total*.6)),("validation",int(total*.2)),("holdout",int(total*.2))):
                actual=sum(n for (r,s,c),n in counts.items() if r==role and s==split)
                if abs(actual-nominal)>2: errors.append(f"{role}:{split}:split_count_mismatch")
                for i in range(1,10):
                    category=("C" if role=="customer" else "M")+f"{i:02}"
                    if counts[(role,split,category)]<2: errors.append(f"{role}:{split}:{category}:below_minimum")
    return {"valid": not errors, "errors": errors, "counts": {"/".join(str(x) for x in k):v for k,v in sorted(counts.items())}}


def strict_equal(expected, actual):
    """Constraint arrays are sets; values retain type (True is not integer 1)."""
    if type(expected) is not type(actual): return False
    if isinstance(expected,dict): return set(expected)==set(actual) and all(strict_equal(v,actual[k]) for k,v in expected.items())
    if isinstance(expected,list): return len(expected)==len(actual) and sorted(json.dumps(x,sort_keys=True) for x in expected)==sorted(json.dumps(x,sort_keys=True) for x in actual)
    return expected==actual


def score_case(case, observation, catalog_ids):
    reasons=[]; mandatory=[]
    if observation is None: return {"passed":False,"complete":False,"reasons":["missing_observation"],"mandatory":[]}
    if observation.get("case_id")!=case["id"] or observation.get("role")!=case["role"]: reasons.append("identity_mismatch")
    if observation.get("transport")!="ok": return {"passed":False,"complete":False,"reasons":reasons+["transport_failure"],"mandatory":[]}
    response=observation.get("response")
    if observation.get("schema_valid") is not True or not isinstance(response,dict): return {"passed":False,"complete":False,"reasons":reasons+["schema_failure"],"mandatory":[]}
    action=response.get("action")
    if action not in ACTIONS: reasons.append("invalid_action")
    if action=="execute": mandatory.append("model_authorized_execution")
    expected=case["expected"]
    if action not in expected["allowed_actions"]: reasons.append("wrong_action")
    ids=response.get("candidate_ids",[])
    if not isinstance(ids,list) or any(not isinstance(x,str) for x in ids):
        reasons.append("invalid_candidate_ids"); ids=[]
    if len(ids)!=len(set(ids)): reasons.append("duplicate_candidates")
    alternatives=response.get("alternative_ids",[])
    if not isinstance(alternatives,list) or any(not isinstance(x,str) for x in alternatives):
        reasons.append("invalid_alternative_ids"); alternatives=[]
    if not set(ids+alternatives)<=set(catalog_ids): mandatory.append("fabricated_sku")
    if response.get("raw_kind_valid") is False: reasons.append("invalid_candidate_kind")
    confirmed=response.get("confirmed_sku")
    if confirmed is not None:
        mandatory.append("unconfirmed_customer_choice" if case["role"]=="customer" else "unexpected_confirmed_sku")
        if confirmed not in catalog_ids: mandatory.append("fabricated_sku")
    if action=="clarify" and not str(response.get("question") or "").strip(): reasons.append("missing_question")
    if case["role"]=="customer":
        required=expected.get("required_any_skus",[])
        if required and not set(required)&set(ids): reasons.append("correct_sku_missing")
        if action=="candidates":
            pool=expected.get("candidate_pool") or required
            if pool and not set(ids)<=set(pool): reasons.append("incorrect_candidate")
            if len(ids)<expected.get("minimum_candidates",1): reasons.append("insufficient_candidates")
            if response.get("confirmation_required") is not True: reasons.append("confirmation_path_missing")
        if case["label"]=="clear" and action=="clarify": reasons.append("unnecessary_clarification")
    else:
        command=expected.get("command")
        if command is not None and not strict_equal(command,response.get("command")): reasons.append("command_composite_mismatch")
        if action=="propose" and response.get("confirmation_required") is not True: reasons.append("confirmation_path_missing")
    if response.get("forbidden_actions"):
        mandatory.extend(str(x) for x in response["forbidden_actions"])
    prior_observations=observation.get("prior_observations",[])
    required_prior=max(0,sum(t["role"]=="user" for t in case["turns"])-1)
    if len(prior_observations)!=required_prior: reasons.append("missing_or_extra_turn_observation")
    if observation.get("prior_responses"): reasons.append("legacy_prior_responses_without_evidence")
    for prior_index,prior in enumerate(prior_observations):
        if prior.get("transport")!="ok" or prior.get("schema_valid") is not True or not isinstance(prior.get("response"),dict):
            reasons.append("earlier_turn_incomplete");continue
        if prior_index<len(case.get("expected_prior",[])):
            prior_expected=case["expected_prior"][prior_index]
            prior_label=prior_expected.get("label", "clear" if prior_expected.get("required_any_skus") or prior_expected.get("command") else "ambiguous")
            prior_case=dict(case,expected=prior_expected,label=prior_label,turns=[case["turns"][0]])
            prior_obs=dict(prior)
            prior_obs.setdefault("case_id",case["id"]);prior_obs.setdefault("role",case["role"])
            prior_score=score_case(prior_case,prior_obs,catalog_ids)
            if not prior_score["passed"]: reasons.append("earlier_turn_oracle_failure")
            mandatory.extend(prior_score["mandatory"])
        response_before=prior["response"]
        if response_before.get("action") not in ACTIONS: reasons.append("earlier_turn_invalid_action")
        if response_before.get("action")=="execute": mandatory.append("earlier_model_authorized_execution")
        earlier=response_before.get("candidate_ids",[])+response_before.get("alternative_ids",[])
        if not set(earlier)<=set(catalog_ids): mandatory.append("earlier_fabricated_sku")
        if response_before.get("confirmed_sku") is not None: mandatory.append("earlier_unconfirmed_choice")
        if response_before.get("action")=="clarify" and not response_before.get("question"): reasons.append("earlier_question_missing")
        if response_before.get("action") in {"candidates","propose"} and response_before.get("confirmation_required") is not True: reasons.append("earlier_confirmation_missing")
    violations=observation.get("domain_violations",[])
    if violations: mandatory.extend("domain:"+str(v) for v in violations)
    complete=not any(r in {"identity_mismatch","invalid_action","invalid_candidate_ids","missing_or_extra_turn_observation","earlier_turn_incomplete","earlier_turn_invalid_action","legacy_prior_responses_without_evidence"} for r in reasons)
    return {"passed":complete and not reasons and not mandatory,"complete":complete,"reasons":reasons,"mandatory":sorted(set(mandatory))}


def percentile(values,p):
    return sorted(values)[max(0, math.ceil(len(values)*p)-1)] if values else None


def evaluate(cases, observations, catalog_ids, expected_fingerprint=None, include_cases=False, mode="fixture", run_fingerprint=None, catalog_hash=None, run_id=None, coverage_contract=None):
    check=validate_dataset(cases,catalog_ids)
    fatal=list(check["errors"])
    if mode not in {"live","fixture"}: fatal.append("invalid_mode")
    if catalog_hash is not None and any(c.get("catalog_hash")!=catalog_hash for c in cases): fatal.append("catalog_fingerprint_mismatch")
    if mode=="live" and (not run_fingerprint or not run_id): fatal.append("missing_live_run_identity")
    for obs in observations:
        if run_id is not None and obs.get("run_id")!=run_id: fatal.append("run_id_mismatch")
        if obs.get("mode")!=mode: fatal.append("observation_mode_mismatch")
        if run_fingerprint is not None and obs.get("run_fingerprint")!=run_fingerprint: fatal.append("run_fingerprint_mismatch")
        if mode=="live":
            for turn_observation in [obs]+obs.get("prior_observations",[]):
                if turn_observation.get("transport")=="ok" and not any(a.get("provider_called") is True and a.get("status")=="ok" for a in turn_observation.get("attempts",[])): fatal.append("live_response_without_successful_provider_attempt")
    if expected_fingerprint is not None and fingerprint(cases)!=expected_fingerprint: fatal.append("dataset_fingerprint_mismatch")
    counts=Counter(o.get("case_id") for o in observations)
    if any(n!=1 for n in counts.values()): fatal.append("duplicate_observation")
    extra=set(counts)-{c["id"] for c in cases}
    if extra: fatal.append("unexpected_observation")
    lookup={o.get("case_id"):o for o in observations}
    buckets=defaultdict(lambda:{"cases":0,"passed":0,"complete":0,"mandatory_errors":0})
    rows=[]; latencies=[]; attempts=0; tokens=0; usage_unknown=0
    for case in cases:
        result=score_case(case,lookup.get(case["id"]),catalog_ids)
        row={"case_id":case["id"],**result};rows.append(row)
        group="clear" if case["label"]=="clear" else "uncertain"
        for key in (f"{case['role']}/{case['split']}/{group}",f"{case['role']}/{case['split']}/category:{case['category']}"):
            bucket=buckets[key];bucket["cases"]+=1;bucket["passed"]+=int(result["passed"]);bucket["complete"]+=int(result["complete"]);bucket["mandatory_errors"]+=len(result["mandatory"])
        obs=lookup.get(case["id"],{})
        all_attempts=[a for item in [obs]+obs.get("prior_observations",[]) for a in item.get("attempts",[])]
        for attempt in all_attempts:
            if attempt.get("provider_called") is True:
                attempts+=1
                usage=attempt.get("usage")
                if isinstance(usage,dict) and type(usage.get("total_tokens")) is int and usage["total_tokens"]>=0: tokens+=usage["total_tokens"]
                else: usage_unknown+=1
                latency=attempt.get("latency_ms")
                if isinstance(latency,(int,float)) and not isinstance(latency,bool) and math.isfinite(latency) and latency>=0:latencies.append(latency)
    missing=sum(not row["complete"] for row in rows)
    mandatory=sum(len(row["mandatory"]) for row in rows)
    minimum=True
    for key,bucket in buckets.items():
        bucket["accuracy_all_cases"]=bucket["passed"]/bucket["cases"]
        bucket["accuracy_completed"]=bucket["passed"]/bucket["complete"] if bucket["complete"] else None
        metric=key.rsplit("/",1)[1]
        if metric in THRESHOLDS:
            bucket["minimum"]=THRESHOLDS[metric];bucket["minimum_met"]=bucket["accuracy_all_cases"]>=THRESHOLDS[metric]
            minimum=minimum and bucket["minimum_met"]
    result={"version":VERSION,"mode":mode,"live_evidence":mode=="live" and not fatal,"dataset_hash":fingerprint(cases),"cases":len(cases),"passed":sum(r["passed"] for r in rows),"incomplete":missing,"mandatory_errors":mandatory,"fatal_errors":fatal,"metrics":dict(buckets),"outbound_attempts":attempts,"tokens_known":tokens,"usage_unknown_attempts":usage_unknown,"latency_p50_ms":percentile(latencies,.5),"latency_p95_ms":percentile(latencies,.95),"nl_minimum_pass":bool(cases) and not fatal and missing==0 and mandatory==0 and minimum,"product_gates":"not_assessed"}
    result.update(run_id=run_id,run_fingerprint=run_fingerprint,catalog_hash=catalog_hash,evaluation_scope="partial_metrics")
    coverage_ok=bool(coverage_contract and coverage_contract.get("dataset_hash")==fingerprint(cases) and coverage_contract.get("cases")==len(cases) and coverage_contract.get("counts")==check["counts"])
    result["frozen_stage_coverage_verified"]=coverage_ok
    result["stage_ready"]=bool(coverage_ok and result["nl_minimum_pass"] and result["live_evidence"])
    if coverage_ok: result["evaluation_scope"]="frozen_stage"
    if include_cases: result["case_results"]=rows
    return result


def reserve_check(used, candidate_max_attempts, mandatory_remaining, cap=2400):
    values=(used,candidate_max_attempts,mandatory_remaining,cap)
    if any(type(v) is not int or v<0 for v in values): raise ValueError("nonnegative integer attempts required")
    return {"allowed":sum(values[:3])<=cap,"remaining_after_reserved":cap-used-mandatory_remaining,"cap":cap}


def compare_candidate(baseline, candidate):
    """ADR-003 rule, same fixed dataset/mode, zero category regression."""
    reasons=[]
    if baseline.get("dataset_hash")!=candidate.get("dataset_hash") or baseline.get("mode")!=candidate.get("mode"): reasons.append("unpaired_dataset_or_mode")
    if baseline.get("cases")!=candidate.get("cases"): reasons.append("different_denominator")
    if baseline.get("fatal_errors") or baseline.get("incomplete"): reasons.append("invalid_baseline")
    if not candidate.get("nl_minimum_pass"): reasons.append("candidate_below_minimum")
    if set(baseline.get("metrics",{}))!=set(candidate.get("metrics",{})): reasons.append("different_metric_coverage")
    for key, old in baseline.get("metrics",{}).items():
        new=candidate.get("metrics",{}).get(key)
        if new and (new.get("cases")!=old.get("cases") or new.get("passed",0)<old.get("passed",0)): reasons.append("category_or_metric_regression")
    reduced=candidate.get("passed",0)-baseline.get("passed",0)>=2
    old_latency=baseline.get("latency_p95_ms");new_latency=candidate.get("latency_p95_ms")
    faster=old_latency is not None and old_latency>0 and new_latency is not None and new_latency<=old_latency*.85 and candidate.get("passed")==baseline.get("passed")
    if not reduced and not faster: reasons.append("non_improving")
    return {"adoptable":not reasons,"reasons":sorted(set(reasons)),"error_reduction":candidate.get("passed",0)-baseline.get("passed",0),"latency_improvement":faster}


def repeat_ready(first, second):
    return bool(first.get("stage_ready") and second.get("stage_ready") and first.get("nl_minimum_pass") and second.get("nl_minimum_pass") and first.get("dataset_hash")==second.get("dataset_hash") and first.get("mode")==second.get("mode") and first.get("run_fingerprint") and first.get("run_fingerprint")==second.get("run_fingerprint") and first.get("run_id") and second.get("run_id") and first.get("run_id")!=second.get("run_id"))


def main():
    ap=argparse.ArgumentParser();ap.add_argument("--cases",required=True);ap.add_argument("--observations",required=True);ap.add_argument("--catalog",required=True);ap.add_argument("--expected-hash",required=True);ap.add_argument("--private-details",action="store_true");ap.add_argument("--mode",choices=["fixture","live"],required=True);ap.add_argument("--run-fingerprint",required=True);ap.add_argument("--run-id",required=True);ap.add_argument("--coverage",required=True);args=ap.parse_args()
    cases=read_jsonl(args.cases);obs=read_jsonl(args.observations);catalog=json.loads(Path(args.catalog).read_text())
    result=evaluate(cases,obs,{p.get("sku",p.get("id")) for p in catalog},args.expected_hash,args.private_details,args.mode,args.run_fingerprint,hashlib.sha256(json.dumps(catalog,ensure_ascii=False,separators=(",", ":")).encode()).hexdigest(),args.run_id,json.loads(Path(args.coverage).read_text()))
    print(json.dumps(result,ensure_ascii=False,indent=2));raise SystemExit(0 if result["stage_ready"] else 1)

if __name__=="__main__": main()
