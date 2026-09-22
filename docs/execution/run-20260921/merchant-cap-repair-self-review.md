# 경영주 명시 수량 상한 어댑터 복구 자체 검토

상태: 자체 기술/실제 메모리 SQLite 검사 PASS, 독립 재검증 대기. 작성자 preflight_builder. 새로운 자연어 후보나 실제 모델 품질 PASS가 아니다.

## 작업·목적 보존

worktree `/Users/gsr/Desktop/workspace/2026-ralphton-merchant-cap-repair`, branch `codex/merchant-cap-repair`, base `73a364860cb90f9bc9de4e186390411bce9dfd21`. 초기 CTX-MERCHANT-CAP-v17 `cd092b691238136543278f5fe01c6c313aa63d8d2204f1ecf62c88a5cdea1028`의63개 입력 hash 일치 ACK 후 편집했다. card·복구 계약·독립 P1 감사·ADR005를 읽었다.

권한은 원래 GOAL/AGENTS의 필수 구현 결함 복구다. D47의 고객 추가 후보 승인에 경영주 후보를 끼워 넣지 않는다. CORE05/06/07/25·AC07/08/31의 명시 조건과 수요·동의·보수적 실제 발주를 보존한다. root의 실제 C7 평가 앱·prompt/model·평가 데이터·장부에는 쓰지 않았다.

## 원인과 최소 수정

기존 `proposalChange`는 `current.lines`만 순회하고 `Math.min(line.quantity, maxQuantity)`를 제약으로 저장했다. 그래서 예산0으로 보류된 SKU는 신규 예산+상한 수정 시 map에서 누락되었고, 작은 현재 계산량은 실제 설정 상한처럼 잘못 저장됐다.

새 명시 상한이 있으면 현재 실행 lines·deferred·이전 maxQuantities의 알려진 SKU 합집합에 그 값을 그대로 매핑한다. 상한을 생략하면 기존 제약 map을 그대로 유지한다. 기존 SKU cap도 새 공통 상한에 일관되게 맞춰 미래 copy에서 이전 값이 섞이지 않게 한다. 새 SKU나 수요를 만들지 않는다. 실제 실행량은 기존 도메인의 수요/coverage·capacity·예산·활성 정책 상한·MOQ/배수 계산이 결정하며, 도메인 코드는 변경하지 않았다.

원래 단위검사 `quantity cap never increases an existing line`은 모델의 명시 상한10을 line6에 맞춰6으로 저장하도록 기대했다. ADR005 및 독립 감사의 범위 검토에 따라 설정상한10을 저장하도록 정정하고, **실제 SQL 주문은 원수요6만**이라는 별도 회귀를 추가했다. 실제 발주량 초과 금지를 완화한 것이 아니라 제약값과 계산값을 구분했다. 구 코드/기대값은 base Git에 보존되고 이전 P1 실패 원본도 유지된다.

## 수정 전후 재현

독립 원본 `c7-policy-state-audit/repro.mjs`를 같은 상대 import 깊이의 repair worktree private 폴더로 복사해 실행했다. 원본은 변경하지 않았다. 상대 import는 이 격리 worktree의 adapter/engine을 읽고, 현재 작업경로의 public seed를 메모리 SQL로 연다.

- before: 수요5 → 예산0으로 보류 → 예산50000/max2 → mappedCapCount0, proposal5, 실제 승인5. `5 !== 2` AssertionError로 실패. `artifacts/private/run-20260921/merchant-cap-repair/before.log` 보존.
- after: 같은 재현에서 mappedCapCount1, proposal2, 실제 승인2. 원래 기대값 변경 없이 정상 종료. `after.log` 보존.

원본 재현: `node --import tsx artifacts/private/run-20260921/merchant-cap-repair/repro.mjs` (Node22, 반드시 repair workdir).

## 자체 검사

`node --import tsx --test tests/domain/*.mts tests/merchant/*.test.ts`: **46/46 PASS**, 실패0/skip0. 원본 domain 회귀와 수정 merchant 단위, 신규 실제 SQL5검사를 포함하며 raw TAP은 같은 private 폴더 `regression.tap`에 있다. 개별 MOQ/배수/예산/capacity parameter4개를 별도 test개수로 부풀리지 않았다.

추가 SQL 검사는 다음을 확인했다.

- 보류 수요5의 명시 cap2를 승인량2로 보존, 원수요5와 잔여3 유지, 승인 전 주문0.
- 실행1/보류1의 혼합 묶음에 cap2 일괄 적용, 예산만 수정해도 cap 유지, 두 단계 undo가 각 이전 제약을 정확히 복원.
- 현재 cap2→명시10 수정 시 설정10/실제수요6/승인6, 모델 future-copy 제약10. 별도 확인한 비활성 정책 저장도10이며 추가 주문0.
- cap3<MOQ6은 보류, cap5/배수2는4, capacity2는2, 예산1000/원가1000은1. 원수요10 보존.
- 활성 지속 정책 cap2가 이번안 명시8보다 작은 경우 실제2, 명시 승인 전 주문0/승인 후 한 주문2.

`node node_modules/typescript/bin/tsc --noEmit --incremental false`: PASS. 신규 test 경로는 기존 `tests/domain/*.mts` 수집에 포함되며 collector/package 변경은 필요 없다. 전체 앱 CI·브라우저 통합은 root의 다음 단계다.

## 동결 소스와 불변 영역

| 파일 | SHA256 |
|---|---|
| src/components/merchant/model.ts | 0c33f6e127d127731c1891a42b3c774fc5fb52263ee67f173d4a9870126c1a69 |
| tests/merchant/model.test.ts | 6629095dec977c9064945278adab10deeece9d6db8a40cf7c74419c21f7fc64e |
| tests/domain/merchant-cap-regression.mts | cc3a403a3bbf38c41e2853d1ef0cddfd2dcc2877465a8af5f596ef5ec8c4d16c |
| src/domain/engine.ts (불변) | b9ea21cd344c7467cf6d34fb7fa3abfb21a02c9cbcf3bb46d977cf7ed684cff4 |
| src/server/prompts.ts (불변) | 02334ef1e86a4707db47280e607194ccde0de91b817b480c2b5672db4f7d1be4 |

초기 context63 입력 중 기존 파일 변경은 소유 adapter와 merchant unit 두 개뿐이고 신규 SQL test만 추가했다. 서버/provider/schema/catalog/packing/검색/도메인/공통계약/lockfile 변경0. root/shared 장부·실제 모델·보호 원문 접근·브라우저 실행0. 이 자체 보고와 개인 재현 로그 외 공통 문서/Git 상태를 수정하지 않았다.

다음: holdout_revision_review가 독립 원본 반례와 정상/인접 SQL 재검증 → root 최종 context·별도 PR/CI·통합. 최종 runtime이 달라지므로 이후 validation/holdout/UX/G5/G6는 새 정확 source에 묶어야 한다. C7 NL 실패 또는 최종 제품 미완료를 이 기술 PASS로 덮지 않는다.
