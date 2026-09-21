# D02 implementation self-check

2026-09-21, preflight_builder, worktree `/Users/gsr/Desktop/workspace/2026-ralphton-domain`, base `5cf1ed0282c2c6cc75408d920a0dc52ce6e777e9`, branch `codex/d02-domain`.

Purpose preserved: known product + explicit consent → request → conservative batch/policy order → confirmed supply → whole FIFO + mock payment → all sources received → 48-hour pickup → merchant collection. No HTTP transaction endpoint, real payment, server DB, private holdout, or new user policy.

## Executed

- `node scripts/build-seed.mjs`: 248 products / 9 sourced stores, SQLite integrity PASS; catalog canonical bytes SHA `f2696abe92521e3ff8f9ab43cb36a1d297a6fd23d272e239605b49fab4343b1e`.
- `node --import tsx --test tests/domain/domain.test.mts`: 25/25 PASS, 0 skipped. Actual sql.js SQL/constraints/transactions/export-import. Transcript `self-test.tap`.
- `npx tsc --noEmit`: PASS.
- `node_modules/.bin/esbuild src/db/worker.ts --bundle --platform=browser --format=iife --outfile=/tmp/wanna-domain-worker.js`: browser bundle smoke, not browser execution.

Node22 `/opt/homebrew/opt/node@22/bin`. package/lockfile changes are root-owned files copied with explicit coordinator authorization; not independently authored here. Schema uses real STRICT SQLite tables and cross-session actor/request/order/allocation FKs; no transaction state array-store or single JSON document substitute.

## Corrections and regression evidence

1. Test runner initially used `.ts` CommonJS output with top-level await. Renamed own test module `.mts`; no product behavior/test expectations changed.
2. C01 review found assortment `not_listed` was incorrectly treated as transaction impossibility. Read docs27: confirmed price/supply may support normal intake independently of assortment label. Removed label-only gate in intake/proposal, retained condition observation/price/consent/supply checks. Added normal not-listed + supply-available integration case.
3. STRICT-table query planner exposed unordered SELECT nondeterminism: UI/test choosing latest proposal/order sometimes saw earlier UUID rows. Added explicit rowid ordering for scoped reads unless caller already specifies business order (FIFO remains sequence). No weakening of MOQ/FIFO expected values. Latest run all 25 PASS.
4. Initial incompatible-snapshot recovery endpoint could have bypassed normal merchant reset on an already initialized runtime. Restricted recovery to uninitialized runtime; restored generation advances beyond saved version. Added actual recovery and ready-runtime refusal test.

## Limits / remaining independent gates

This is the implementer's own check, not independent QA. IndexedDB browser transaction completion/abort and actual Worker/new URL bundling in Next remain G3/G4/browser checks. In-memory SnapshotStore failure injection proves SQL/runtime restoration but is not an IndexedDB browser claim. N01 live model and both-role UI/Preview/Production are separate owners/gates. Independent reviewer has been sent paths and commands. Final product gate report cannot cite this file as independent approval.

Data source facts remain separated from simulated conditions. Retail inventory/capacity/prices/budget are explicitly simulated, real-store operation is unverified. Public seed contains no evaluation utterances/answers. Recent28 records retain limited dated vendor trend evidence and unknown sizes instead of fabricated mass.

## Freeze for independent browser review

- engine SHA256 `dc934949eeaba9046e56e52c0e7bec3619bc6588837fbf32f63da8816510a5fe`
- runtime SHA256 `b567984ecef5504f6d091c30ab518dffbef767e69e06c4c8ee8d7f7ae1ecf631`
- contracts SHA256 `be4ce230606b5b2b78d9b6f3dafc8fc5700e7f70c277d7228e98206643738743`

`src/demo/scenarios.ts` provides explicit merchant-confirmed reset/presets through the same public domain commands. Last regression adds permanent supply end → unpaid review, preserves original request record. No application source edits after this freeze until reviewer coordination.

## Independent feedback corrections (supersedes earlier engine freeze)

Reviewer reproduced three runtime gaps: empty reconsent terms, unknown excluded SKU, and silently ignored `budgetLimitKrw`. Central consent validation now rejects empty/whitespace/non-string/overlong terms on every consent path. Proposal changes validate their exact allowlist, existing SKU/category, scope and safe integer limits before modifying drafts. Negative tests assert unchanged consent/version/sequence and unchanged draft/lines after rejection; valid zero-budget change still works. Latest own suite **27/27 PASS**, typecheck PASS. New engine SHA `bd6ea7ca138c9a44c8c7ce7336146f261161a64c6f20ee178e8bddd20cc2cd6b`; runtime/worker/schema/catalog unchanged. Independent counterexample rerun requested. Potential ADR-005 policy-per-review cap is not implemented or accepted by this report.

D04 demo controls are new optional UI files under `src/components/demo/`, with the shared props `{snapshot,client,onSnapshot}`. Typecheck passed. Their browser/UI verification is separate and pending. Default collapsed, merchant intervention only, explicit reset/preset confirmation, bounded forward clock, synthetic payment outcomes and scoped condition-version guard. No global stylesheet, app shell, package or frozen DB files changed for this UI task.

## ADR-005 adopted implementation + observation contract (latest)

ADR-005 adopted document copied and ACKed. Policy `maxQuantityPerReview` is a nullable positive integer, reported in PolicyView. `policy.update` omission preserves the stored cap; explicit null removes it. Unknown policy fields/unknown SKU/category/zero/fractional cap reject and roll back. Proposal quantity respects the smaller current-proposal and active-policy cap, then supplier remaining capacity/budget/MOQ/multiple.

Automatic ordering now has one permitted call path per store per external event. `autoOrder.run` no longer calls auto twice. `merchant.review` performs one reconcile then creates its proposal; passive snapshot/query has no auto side effects. Manual approval, supply/receive/time-advance do not recursively create another automatic review. Their expiry/FIFO/payment processing remains intact. New request, condition/policy change, explicit review and reopen remain permitted automatic triggers.

Model observation command: `agent.record.usage` accepts the observed token object or null; `providerCalled` records whether a provider request was attempted. Unknown timeout/429 usage remains null, never an invented 0. These records do not create needs or purchase demand.

Version change: `schema-v2`, `seed-248-v2`, `ADR002+004+005`. Catalog remains `catalog-248-v1` with unchanged hash `f2696abe92521e3ff8f9ab43cb36a1d297a6fd23d272e239605b49fab4343b1e`. Seed bytes SHA `4cb10e899c9706bb0a9278b458bd7b70d3c34bf28f649b62ffae0894794a2b45`. Old schema snapshots require the existing explicit recovery path, never silent replacement.

Latest checks: **34/34 actual sql.js integration tests PASS**, no skip; TypeScript PASS. New cases cover per-event cap/replay, MOQ deferral, omitted/null/off semantics, tighter manual cap, no additional auto after manual approval, invalid-policy rollback, unknown usage, tighter budget/capacity, and snapshot failure restoring policy+cap+budget+capacity+auto order while preserving the original customer request.

Latest freeze engine SHA `18fc77a60534d35804206668d8bd0d85da2a20a4fe1279909ae5a73bf6916c98`, domain contract SHA `952c22bb73bb93218c6fcf573d8c7264a2c749560d809a8bb26c2f15eb968105`, schema SHA `48c5c59a7e74a793139ab7a38062abc76709b08b1b4956117dc21e5f8b24416c`. Independent ADR-005 rerun requested. Prior independent browser runtime evidence does not automatically prove the new policy semantics.
