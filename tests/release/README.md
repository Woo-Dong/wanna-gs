# G5 public evidence checker

`python3 scripts/check_release_evidence.py --root /absolute/repo` reads `quality/release/manifest.json`. `--manifest` accepts another root-relative path. Missing, malformed, stale, incomplete, fixture, or inconsistent evidence returns JSON `status: NOT_READY` and exit1. PASS is G5 only and always reports `g6_status: pending`. No model, browser, network, secret, or protected holdout content is read or executed. This tool does not generate release evidence or a release PASS record.

The checker implements existing ADR003/CORE/G5 evidence requirements, not a new accuracy standard. Baseline336 must preserve all attempts/failures but need not pass accuracy or stage_ready. Only best validation84 twice and holdout84 require the existing95% clear/90% uncertain minima separately by role/split, complete coverage and zero mandatory errors. Runtime declarations are compared to actual files, including additions/deletions; they cannot choose a smaller source subset.

## Public evidence protocol

The coordinator/evaluator creates sanitized exports only **after actual execution**. Private originals and holdout remain private. Every artifact reference is exactly `{path, sha256}`; the hash is SHA256 of file bytes. Allowed artifact roots are `quality/release/evidence/` and `docs/execution/`, `.json`/`.md` only. Absolute, traversal, hidden/private paths, symlink files/ancestors and bad hashes fail. Holdout aggregate filenames may contain `holdout`; raw `case_results`, `turns`, `expected`, utterances, raw responses and secret fields are rejected. JSON references reached through coverage/report links are scanned too. Secret scanning is a denylist safeguard, not a general DLP guarantee; the publisher and independent reviewer must inspect sanitized exports before committing.

Top-level manifest contract:

- `version: G5-evidence-v1`, `scope: G5`, `g6_status: pending`.
- `versions`: nonempty strings for research, catalog, scenario, eval, seed, policy, prompt, model, context. These identify the applied docs09 execution context; they do not change policies.
- `runtime: {files: {relativePath: sha256}, sha256}`. The aggregate is canonical JSON SHA256 (UTF8, sorted keys, compact separators, no ASCII escaping). File set includes all files in app/src/public/data/seed/data/schema and existing package/lock/tsconfig/next.config/vercel config. Next default configuration without a next.config file is valid; when any supported next.config file exists, its addition/modification/deletion remains part of the exact runtime file set. Required app routes, role views, domain/Worker/contracts/provider/prompts/catalog, seed/WASM/catalog/manifest and config anchors must exist independently of the declared set. Runtime excludes evidence/QA/config files that do not run in the app, avoiding self-referential release hashes.
- `candidate: {id, model, promptVersion, promptHash, catalogHash, sourceSha, runtimeHash, frozenAt}`. sourceSha is40hex, file/aggregate hashes64hex, frozenAt zoned ISO time. Prompt hash and compact catalog JSON hash are compared to current sources.
- `datasets: {baseline, validation, holdout}`. Each is `{hash,cases,counts}` matching public `evals/baseline-coverage.json`, `evals/validation-coverage.json`, or `evals/manifest.json.splits.holdout`. Counts are the existing role/split/category distribution, not a newly generated split. No holdout JSONL is opened.
- `nl: {baseline, validation: [first,second], holdout}` bundles below.
- `ux: {baseline: ref, best: ref}` of actual UX raw results, below.
- `role_qa: [customerRef,merchantRef]`; `policy_reviews: [firstRef,secondRef]`; `core_coverage`; `preview`; `independent_evidence_review` below.

## NL bundle and sanitized export

Each bundle contains `report`, `execution`, `binding` artifact refs. `report` is the original scorer aggregate schema without case_results. It keeps version/mode/live_evidence, dataset_hash/cases/passed/incomplete/mandatory_errors/fatal_errors, all role/split/category metrics, outbound_attempts/tokens_known/usage_unknown_attempts, run_id/run_fingerprint/catalog_hash, evaluation_scope/frozen_stage_coverage_verified/stage_ready/nl_minimum_pass; scorer latency/product_gates fields are accepted. No exact question/oracle/response is required or allowed.

`execution` is a **sanitized derivation of actual runner progress/checkpoint/attempt evidence**, not a hand-invented result: mode, run_id, run_fingerprint, dataset_hash, cases_expected, cases_recorded, attempted_cases, provider_called_count, provider_not_called_count, unknown_provider_count, outbound_http_attempts, pending_attempts, started_at, finished_at, candidate_id, runtime_hash, source_sha, stop_code. Preserve baseline failures and unknown usage. Every stage must have all expected cases attempted and recorded, pending0; baseline may have failed model responses/poor accuracy. Best stages additionally require no unresolved pending attempt/stop and exact current candidate runtime binding. Earlier legal timeout/429 retry attempts may preserve unknown provider/usage counts even when the final turn succeeds; they are not replaced by0 and do not create a new rejection criterion. HTTP attempt count must equal true+false+unknown provider counts. `outbound_attempts` in the scorer counts known provider-called attempts and must equal provider_called_count; cases are not conflated with multi-turn calls.

`binding` is `{runner: E02-v1, config: exactOriginalRunnerConfig, state_fixtures_hash: canonicalHash}`. Keep the exact original nonsecret config to recompute the existing runner run_fingerprint. Config path strings that describe historical private proof locations are metadata only and are never followed. The state hash is published; actual holdout states are not opened. The independent evaluator must verify that hash against its original evidence. For best runs, model/prompt/catalog/source metadata and all declared source_files are compared to current files, and required server/route/contract/catalog/runner/scorer/adapter/taxonomy/coverage/lock source keys cannot be omitted. Baseline binding is recomputed but need not match the new best sources.

The two validation reports require distinct run IDs and identical candidate binding, dataset hash and recomputed run_fingerprint. Both must independently meet the existing minima. Metric bucket totals and rates are recalculated; a forged stage_ready boolean alone is insufficient. Latency P95 target is reported by scorer and not converted to an accuracy waiver or new hard gate.

Holdout bundle adds `role: holdout_aggregate` and `independent_report` ref. This aggregate attestation has role=holdout_evaluator, status=PASS, reviewer, nonempty implementers, run_id, candidate_id, runtime_hash, protected_content_not_published=true. Reviewer must not implement the evaluated candidate. Holdout start must be after candidate freeze and both validation finishes. No protected content is accessed to enforce this order. Independent reporting, not a signature, attests execution time and state hash.

## UX raw evidence

Use actual `tests/ux-benchmark/run.mts` raw result (mode=live/stage=baseline|best), preserving runs/workloads/clock/seedHash/workloadHash/harnessHashes/sourceFiles/seedEngineBinding/network/liveUsage/authorizationHash/runId. The sanitized exporter additionally attaches `runtimeHash` and `candidateId` to the **best** export using source provenance verified at execution. Do not relabel a fixture result as live. Baseline may bind older app sources but must have identical fixed workload/harness/seed/clock/viewports.

The checker ignores cached summary PASS claims and recomputes: exactly the8 adopted workload IDs, three unique repetitions1/2/3 each, every correctnessPASS and durable SQLite hash, fixed clock, actual provider-called unique attempts matched to per-run network rows, and no setup/page/uncertain failure. Calls and cases are separate; nominal18 calls is a floor and no retry budget is newly authorized. Unique provider attempts require known integer token sums and finite nonnegative cost. Each row's nonModelMs is checked against elapsed−network−budget instrumentation without allowing impossible waits to be clamped to zero; network interval union and budget sums are recomputed. All workloads retain the existing maximum2 clarification questions. All24 raw rows remain in the denominator.

Existing ADR003 absolute criteria are checked for clear customer decisions (after submit<=7/questions<=2), one merchant batch screen/approval, automatic per-order approvals0 and unchanged-review duplicate check. Compare best against baseline using workload maximum decisions/transitions (increase0) and nonmodel median (<=110%). The supplied tool already performs SQL correctness assertions; this checker validates their bound raw reports and cannot reconstruct an actual browser session from a JSON file.

## Independent reports, scope and Preview

Role QA JSON: role customer|merchant, scope G5, provider openai, status PASS, mode live, actual_browser=true, actual_sql=true, provider_calls>0, runtime_hash, candidate_id, reviewer, implementers, coverage (CORE ID list), failures=0, mandatory_errors=0, checks_executed>0, evidence=[refs to sanitized independent reports]. Role reviewers must differ, and each must not implement the **role being reviewed**. Cross-role work is allowed by the existing project allocation; a customer implementer may independently review merchant work.

Policy review JSON: scope G5, reviewer, distinct perspective, status PASS, unresolved_major=0, runtime_hash, candidate_id, evidence=[refs]. Exactly two reviewers/perspectives. Reports must cover final policy gaps and adopted decisions; empty evidence/stale/unresolved major issues fail.

`core_coverage` maps every CORE-01..26 to `{status: PASS, scope: G5, evidence:[refs]}`. CORE-13 alone may use `G6_PENDING`: G5 records available deployment preparation while actual submission access/AC19 remains G6. Other CORE requirements cannot be silently omitted or deferred. `preview` references existing sanitized Vercel metadata shape `{id,url,target:null|preview,readyState:READY,gitSource:{sha}}`; SHA must equal selected candidate sourceSha. This is evidence of a Preview revision, not G6 Production verification.

`independent_evidence_review` JSON: status PASS, reviewer, nonempty implementers, runtime_hash, candidate_id. Reviewer must not be an evidence-tool/package implementer. This report supplies the independent human/agent audit layer; the checker does not prove the truth of reported executions cryptographically. Successful G5 still needs actual G6 at the submitted origin.

## Self-tests and current readiness

Run `python3 -m unittest discover -s tests/release -p 'test_*.py' -v`. Tests construct **temporary synthetic protocol packages only**, then delete them. A synthetic positive tests the checker acceptance contract, not live application quality. Counterexamples cover missing/stale runtime and files, removed anchors, private/path/symlink/hash attacks, holdout/oracle/secret publication, missing attempts, baseline failure allowed, stage flag spoofing, repeated run/config mismatch, premature holdout, missing/duplicate UX repetitions/provider rows, changed timings/decisions, scope/independence/CORE/Preview mismatches and false G6 completion.

No real release manifest is created by this task. Default execution against current root is expected NOT_READY/exit1 until the coordinator/evaluator publishes actual NL/UX/G5 evidence. CI/config integration is root-owned and intentionally not modified here.

## Prepared source verification

- Own temporary protocol tests44 PASS (including reviewer-reported unknown usage/cost, impossible network waits, ambiguous99questions and adjacent legal NL retry history with unknown usage/provider counts).
- Real repository invocation returns NOT_READY_MANIFEST_MISSING/exit1 as expected. No fake actual release record, model request or budget mutation.
- Independent review is a separate pending step; own tests do not claim independent acceptance or G5 readiness.

### Optional Next configuration correction

The real app uses Next defaults without a next.config file. Removed only the erroneous existence requirement; runtime inclusion of present config files and all other required anchors is unchanged. New regressions cover absent-config success plus added/modified/deleted config rejection against a frozen fingerprint. This is an evidence-tool correction, not a release criterion waiver.
