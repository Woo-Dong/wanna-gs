# ADR007 UX-v3 instrumentation

Implementation preparation, not paid run authorization or release PASS. Original v2 paths and failed runs are unchanged. Fixed study ux-study-v3-01; baseline ux-baseline-b0-v3-01, best ux-best-v3-01; exact8 workloads×7, fixed order,42 planned model calls per arm, no model retries. Existing v2 seed/clock/UI actions/SQLite correctness are reused unchanged and included in harness hashes. Every output has56 planned rows from the start; an actual trial is marked attempted only after setup attempt reaches its row. Known model failures with accounted usage and UI/SQL failures are FAIL, then next planned trial. Remaining model steps and broad trial stages preserve NOT_RUN. Unknown provider/usage/cost, pending, auth/quota, source/model/prompt/catalog mismatch or budget exhaustion stop the entire study, never create another run ID. Model/HTTP failure is not a quality success.

`app-root` is the exact preserved B0 or selected-best app; `budget-root` is the single current goal ledger/runner. The old app runner is never imported for budget enforcement. Ledger namespace is ux_v3_studies, with one fixed study and arm claim each. Study STOP blocks either arm. Best begin requires baseline execution complete (56 attempted, not necessarily successful); insufficient baseline successes still makes comparison NOT_READY. Success minimum and best56/56 are evaluated independently of execution completeness.

## Read-only draft preparation

Node22/tsx, Python3.11+ and existing Playwright/Chrome dependencies. Run from the instrumentation checkout. Create a fresh unapproved config only:

```sh
node --import tsx tests/ux-benchmark/v3/prepare.mts \
 --app-root /absolute/preserved-app --budget-root /absolute/current-goal \
 --stage baseline --source-sha 10c00723d0b64ea47a06dcbd00e2b671e7c62daf \
 --origin http://127.0.0.1:APP_PORT \
 --output /absolute/new-private-output --draft /absolute/new-private-draft.json
```

This reads actual runtime files/git objects/build ID and writes approved:false. It never opens the ledger or performs HTTP. Coordinator must independently verify exact server PID/source/build/origin, fixed best model/prompt/candidate identity, remaining mandatory reservations and private output. Supply a processId>0; do not convert the placeholder approval/reserve fields into execution authorization automatically. `server_proof` is coordinator attribution, not cryptographic runtime attestation.

Same v3 harness hashes and workload hash must be fixed for both arms before actual study. App UI/domain/seed consistency must be reviewed before either arm. B0 source/model/prompt are enforced; best full source/runtime/model/prompt must match selected release evidence. All source files are compared to the supplied app commit and actual working files. New source changes require revalidation before any paid execution; runtime, budget dependencies and harness are checked before/after every trial and changes mid-run cause STOP.

## Execution contract (not executed by implementation task)

```sh
PLAYWRIGHT_MODULE=/absolute/playwright/index.mjs \
CHROMIUM_EXECUTABLE='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome' \
node --import tsx tests/ux-benchmark/v3/run.mts \
 --app-root /absolute/preserved-app --budget-root /absolute/current-goal \
 --url http://127.0.0.1:APP_PORT --live \
 --budget-config /absolute/approved-config.json --output /absolute/new-private-output
```

The same command without --live uses fixture responses and never instantiates a Budget. Fixture does not satisfy live NL/UX/G5. Use a separate non-live local app server for own browser fixture checks. Remote Preview is intentionally unsupported, preserving the same app execution approach for both arms.

All remaining authorized model attempts reserve $.05 each plus explicit future mandatory cost; prior50/2400 and current Budget20 remain. The coordinator reserves the other arm and required NL/QA/G6 in mandatory_reserve/cost. A 96-call planning reservation is not permission to send more than42 per arm. Budget begin is a mutation; do not call it to inspect readiness. No caller source creates a new actual ledger.

Output complete means every planned trial was actually attempted without study stop. bestAbsoluteReady is separate. Conditional comparison uses every successful trial (not first3/fastest subset), minimum3 per baseline workload and7 best; maxima decisions/screens and median non-model time, best<=baseline and<=110%. Failed times are retained, not imputed or used as normal completion times. Old48 denominator and new112 remain distinct (160 total).

## Public release evidence

Existing v2 protocol remains supported. For v3 manifest.ux use version UX-BENCHMARK-v3; baseline/best refs; history array of exactly two sanitized original exports; plannedTotals={historicalBaseline:48,newBaseline:56,newBest:56,total:160}. Each original export preserves mode=live, complete=false, originalSha256, runId, planned/attempted/passed/failed/notRun and original executed rows with workload/repetition/status. Required original hashes/IDs/counts are fixed in plan.mjs and checker, not caller-chosen. Original raw files stay private/unchanged. A sanitizer must remove failureSnapshot/raw user content rather than changing outcome rows; independent evidence review still checks export truth. No result signing claim.

V3 result public fields include sourceFiles full inventory/runtimeHash, sourceSha/model/promptVersion/catalogHash, candidateId, budgetRunnerHash/budgetSourceFiles (runner+adapter+scorer), harnessHashes, seedEngineBinding and all raw trial/network/usage denominators. Export only after real execution, preserving actual values. The checker recomputes successful-trial metrics, rejects study STOP/pending/NOT_RUN/best failure, validates known usage/step mapping and source/harness/old-history bindings, then applies the existing role/policy/CORE/Preview gates. Missing evidence remains NOT_READY.

## Test collector proposal (root owns integration)

- Python collector: add tests/ux-benchmark/v3 as its own required nonzero suite (`test_*.py`), because existing discover on parent does not recurse into this non-package directory.
- Node collector: add both tests/ux-benchmark/v3/*.test.mjs and tests/ux-benchmark/v3/*.test.mts; each glob must collect nonzero.
- Existing tests/release collection automatically includes test_release_v3.py. No package/lock change is required.
- Existing v2 script/hash source patterns remain; append v3/**/*.mjs, v3/**/*.mts, v3/**/*.py as needed for runtime test fingerprints. Do not silently replace v2 evidence.

Own checks use temp roots/ledgers and mock HTTP only. Source/script versions and actual browser fixture results are recorded separately in SELF-REVIEW.md; independent research review follows.
