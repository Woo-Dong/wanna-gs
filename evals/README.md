# Independent NL evaluation

Owner: nl-evaluator (`/root/method_auditor`). Context APP-v3, ADR-003. These tools never call a model. `python3 -m unittest discover -s evals/tests -v` checks the scorer, not application quality.

- taxonomy.json fixes 300 customer +120 merchant cases (dev252, validation84, private holdout84).
- case.schema.json documents cases. scorer.py also validates critical execution fields and rejects pending catalog bindings.
- adapter.py normalizes N01 customer/merchant responses. It does not infer a completed customer consent or grant execution authority.
- dev.jsonl / validation.jsonl will contain source-bound public cases. The private holdout is evaluator-only under the ignored `artifacts/private/run-20260921/holdout/` directory. Do not inspect, import, bundle, copy into aliases/prompts, or print those files.
- All observed errors and provider attempts remain in the denominator/accounting. Product domain checks and FE confirmation are separate G1~G6 evidence; a passing NL metric cannot substitute for them.

The customer API adapter separates primary exact/confirm IDs and explicitly labelled alternatives. Scoring requires the correct primary SKU, no wrong primary assertion, no unknown SKU and a confirmation-oriented response. The UI's actual confirmation behavior requires independent browser QA. The merchant normalized command is `{intent: modify|restore, scope: current_proposal|policy, constraints: {...}}`. All nonempty explicit constraints must match exactly; null, empty arrays and false schema defaults are removed by the adapter. A clarify action requires a nonempty question and never executes.

A runner observation includes case_id, role, mode=fixture|live, run_fingerprint, transport, schema_valid, normalized response, and attempts with provider_called/status/latency_ms/usage. run_fingerprint must bind source SHA, model/prompt/search/catalog/schema/config versions. `domain_violations` may attach real downstream violations; absence is not proof that domain gates passed. The report always says `product_gates=not_assessed`.

```sh
python3 evals/scorer.py --cases evals/validation.jsonl --observations PATH_TO_RESPONSES --catalog PATH_TO_CATALOG --expected-hash DATASET_CANONICAL_HASH --mode live --run-fingerprint CONFIG_FINGERPRINT --run-id UNIQUE_RUN_ID --coverage evals/validation-coverage.json
```

Default reports show aggregate counts and hashes only. `--private-details` includes case results and must be sent only to evaluator private artifacts when scoring holdout. Baseline uses dev+validation only. Final frozen best is evaluated on protected holdout once. Earlier failed results are never replaced by later successes.

Scorer self-tests use three explicitly fictional IDs in isolated fixtures. Those IDs are not catalog data and cannot be passed as production evaluation binding. Live model calls and product evaluation remain not_run until N01 and the actual catalog contract are ready.

Each completed model turn must have a successful provider attempt with `status: ok`; timeout-only observations cannot count as live evidence. Use `prior_observations` (transport/schema_valid/response/attempts and optional checked case_id/role) for earlier user turns, not raw prior response placeholders. `expected_prior` holds the evaluator oracle for each earlier turn and must never enter the model prompt. Keep the actual assistant responses in conversation history.

`nl_minimum_pass` describes the supplied subset only. `stage_ready` requires live evidence and exact frozen coverage (hash, count and per-role/split/category counts). CLI exits successfully only for `stage_ready`; `repeat_ready` additionally needs two distinct run IDs with an identical run fingerprint and frozen dataset. The catalog fingerprint uses SHA256 of JSON.stringify(Product[]) in catalog order; dataset fingerprints use canonical sorted keys. Never substitute one for the other.

The manifest is frozen before first model baseline; current 248-SKU binding is catalog-248-v1. Public scenarios are synthetic expansions grounded in the stated source IDs; they are not observed customer quotes. Same SKU-derived phrasing is confined to a single split. Private generation seed and generator remain with the evaluator. Do not reconstruct protected cases from metadata.
