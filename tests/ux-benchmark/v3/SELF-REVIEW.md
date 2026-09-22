# UX v3 implementation self-review

Author: preflight_builder. This is implementation-owned verification, not independent QA, paid study authorization, or G5 PASS. Scope follows adopted ADR007/D46. Root product/evaluation source, actual goal ledger, protected holdout, original v2 harness and failed originals were not modified. No actual model request occurred.

## Scope and source ownership

Isolated checkout `/Users/gsr/Desktop/workspace/2026-ralphton-ux-v3-instrument`, branch `codex/ux-v3-instrument`, base `560706f6796c1ff84fa2ebd1ad06f373f7d2a9ae`. Integrate only new `tests/ux-benchmark/v3/`, `scripts/check_release_evidence.py`, `tests/release/test_release_v3.py`, and the release README delta. Current Budget20 runner, ADR007 and context-v13 were copied as read/test dependencies; do not integrate them over root's current versions. No package/lock/CI/Git mutation was performed.

Context v13 `f4a0ccd9d96c2536b50476baadf68aa3355533d3c1999d4cea2edeb5d7fe4a43` acknowledged and listed input hashes checked. Fixed plan SHA256 `515a97609bc51b3ebb463bd5e7b5bd3814b6241b99ad50750741a7ea1a1da386` preserves adopted IDs, all eight workloads, seven repetitions, source clock and old failed execution counts/hashes.

## Purpose preservation and meaningful boundaries

The product, browser SQLite transaction assertions, consent/reconsent, per-order approval and no-duplicate automatic order checks remain. Trial known failure can advance only to the next planned trial; it cannot retry an outbound or become PASS. Unknown provider/usage/cost, quota/auth, source/config mismatch and uncertain ledger finalization stop the single study. Either-arm STOP blocks the other claim. Best completion is separate from best 56/56 correctness. Baseline minimum three per workload never erases its failures; conditional maxima/median use every successful trial. Old48/new112/total160 evidence remains separate. V2 release evidence retains its original branch.

App-root and budget-root are explicit independent paths. Current goal Budget20 runner plus imported adapter/scorer are exact-bound before each bridge operation. Runtime inventory includes additions/deletions; app commit, actual build and coordinator server attribution must match. Each trial checks actual runtime, budget dependencies and harness before/after. Server PID attribution is not a cryptographic process/source proof and still needs coordinator/independent inspection before live GO.

## Executed own checks

- Python bridge: 12 tests PASS, all using disposable fake goal roots/ledgers. Covers 56-trial/42-call sequence, accounted failure next-trial/no retry, unknown/global STOP, auth/quota/model mismatch, pending/no replay, output/workload/config binding, removed/changed budget dependencies, current $20 boundary with future/prior/$.05 reserves.
- Node metrics/binding/mock transport: 9 tests PASS. Covers all-success conditional median, first-three bias counterexample, baseline 3-success threshold/best failure, duplicate/missing repetitions, old history, app/budget separation, no outbound after reserve/unknown, delivery delay outside budget accounting.
- Release checker: 68 tests PASS (48 existing v2 +20 v3). Temporary synthetic packages only. Covers all56 attempted, min baseline successes, best failure, STOP/pending, old failure preservation, source/usage/denominator/step binding, current budget dependency hashes and conditional comparison.
- `npm run typecheck` PASS after final instrumentation changes. `npm run build` PASS for the isolated app; BUILD_ID `yt7fn88eKbcYV9lXwjcLF`. Initial build exposed an inferred empty-object type in the new draft generator; an explicit `Record<string,string>` type fixed it, followed by successful type/build. No product source correction was needed.
- Default real checkout checker: NOT_READY_MANIFEST_MISSING, exit1, as expected. No actual manifest was created.
- Original v2 run/seed/metrics/live/bridge files have an empty Git diff against the worktree base.

Commands use Node22 `/opt/homebrew/opt/node@22/bin` and bundled Python `/Users/gsr/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin`. Run `python3 -m unittest discover -s tests/ux-benchmark/v3 -p 'test_*.py' -v`, `python3 -m unittest discover -s tests/release -p 'test_*.py' -v`, and `node --import tsx --test tests/ux-benchmark/v3/*.test.mjs tests/ux-benchmark/v3/*.test.mts`.

## Actual browser fixture evidence

Separate non-live app server `http://127.0.0.1:3231`, `LLM_MODE=fixture`, no `.env.local` copied, Chrome executable `/Applications/Google Chrome.app/Contents/MacOS/Google Chrome`. Every assistant response is intercepted as fixture; models0/shared goal ledger writes0. Each of56 fresh browser contexts reads/writes actual sql.js SQLite and IndexedDB, verifies the observed Worker clock `1789959600000`, durable SQLite integrity/foreign keys and workload state. Clock injection scope is window+Worker Date.now and is verified by initial snapshot, not an assertion that external wall time is frozen.

1. `artifacts/private/ux-v3-fixture-01/result.json`: baseline-mode fixture56/56 PASS, STOPnull/pending0, raw SHA256 `e52965ec35b493dabe3e539a55316e11cfcd1b2c0f26ad90d835c6e1c041b423`. This preceded final live dependency/source guards and remains preserved, not relabeled as the final harness.
2. Final-harness best-mode fixture `artifacts/private/ux-v3-fixture-final-02/result.json`: 56 planned/56 attempted/56 PASS/0 FAIL/0 NOT_RUN, STOPnull/pending0, provider/model calls0. Raw SHA256 `f777b614edae8ce2982ea254237f04fce0a07eedff0200120c81b6fb8b0abd3e`. Exit0. All56 rows retain actual durable SQLite hashes and observed fixed clock.

Screenshots and raw rows remain in their respective private output directories. These fixture checks establish measurement/browser plumbing, not actual model UX performance. No comparison of fixture execution times is claimed as live product improvement. Independent research verification follows source freeze.

## Independent counterexample F-V3-01 and repair

Research independently found that consistently changing successful usage/network observations to provider_called=false and modelCalls=0 was accepted by the initial v3 release checker. Earlier own89 PASS did not cover this defect and remains only its original scope. Added successful-observation provider_called=true enforcement in both observation and PASS-row checks. Known accounted failed baseline observations may retain provider_called=false and zero known usage/cost; they are not relabeled as successful model calls. Four regressions cover best zero-provider spoofing, baseline success spoofing, preserved legitimate baseline non-provider failure and a failed UI trial containing a falsely successful model observation. Release suite now72 PASS (48 v2 +24 v3); own total93 with prior unchanged bridge12/Node9. Execution harness, app/build, final fixture raw and original v2 sources are unchanged; no new actual fixture run was required for a checker-only delta. Independent recheck remains separate.
