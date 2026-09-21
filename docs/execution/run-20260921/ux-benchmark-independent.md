# UX benchmark v2 독립 검토

- 판정: **PASS — 측정 장치·fixture 준비 범위**. live baseline/best는 not_run이며 최종 UX 회귀/GOAL 완료를 뜻하지 않는다.
- 검토자: research. 구현자: preflight_builder. 제품 C01은 본인 구현이므로 이 실행을 독립 고객 제품 QA로 재분류하지 않는다. 독립 대상은 타 작성자의 측정·예산·비교 장치다.
- consumed context: context-app-v5.json / `10701ed7619c86fe94cec16a31b6ac8b02a1afa9f2843ffdcce4ec446e952234`; ADR003 사전 고정 기준을 유지했다.
- 실제 모델 0회, outbound 0회, 보호 holdout 열람 0, 실제 goal ledger 쓰기 0. 검토 중 실제 `nl-budget.json`은 없었으며 fixture는 생성하지 않았다. 이후 live는 E02가 초기화한 동일 장부와 명시적 승인 config를 요구한다.

## 발견 반례와 보완 재검증

1. 반복1을 세 번 복사하면 완료로 판정되던 오류. 고정8종 및 반복1·2·3 유일성, 누락·중복·범위 밖 기록으로 보완됐다.
2. best summary 누락 또는 빈 배열이 비교 통과를 숨기던 오류. 고정8종 집합 강제와 raw rows 재계산으로 보완됐다. 실제24 결과를 복제한 독립 변조 검사에서 정상비교8PASS, 중복반복FAIL, 빈summary거절, raw runs0일 때8FAIL, 한 반복FAIL 유지가 모두 확인됐다.
3. 80ms UI 응답 전달 지연이 budgetInstrumentation으로 빠져 nonModel을 낮추던 오류. reserve/finish 구간만 따로 재고 delivery는 nonModel에 남기도록 보완됐다. 독립 초기 mock 재현 및 수정 후 Node 회귀 PASS.
4. seed는 로컬 engine을 실행하면서 app-root engine만 기록하던 지문 공백. 실제 로컬 engine/contract와 app-root 바이트 hash가 다르면 prepare 전에 거절하고 seedEngineBinding을 기록한다. 현재 실제바이트 일치와 불일치 거절 selftest를 독립 실행했다.

실패한 초기 장치 관측을 삭제하지 않으며, builder v1 fixture07의 PASS를 v2 결과로 쓰지 않았다. 위 보완은 목적·분모·제품안전 확인을 유지했다.

## 실제 실행

- Python budget tests 7/7 PASS; Node transport·timing·metrics·seed binding tests 10/10 PASS. 테스트는 임시 fake ledger만 사용.
- 독립 실제 결과 변조 회귀 5/5 PASS.
- Chromium/Worker/sql.js/IndexedDB 실제 UI fixture **24/24 PASS**, 8업무×각3회. 누락0·중복0·pageerror0. 각 최초 Worker clock 정확 일치, 모든 SQLite integrity/FK 검사 통과.
- 실행: `node --import tsx tests/ux-benchmark/run.mts --app-root /Users/gsr/Desktop/workspace/2026-ralphton --url http://localhost:3217 --output /Users/gsr/Desktop/workspace/2026-ralphton/artifacts/private/run-20260921/ux-independent-v2`, PLAYWRIGHT_MODULE/CHROMIUM_EXECUTABLE은 로컬 설치를 지정. `--live` 미사용.
- 앱 BUILD_ID `bonXY08NoEJJMwCDR3WAs`; root I01 commit `10c00723d0b64ea47a06dcbd00e2b671e7c62daf` 고정 서버. 종료 시 결과의 모든 제품 sourceFiles15개와 현재 파일 hash 일치, harness5개도 동결본 일치.
- 실제 조작 경로의 거래는 UI로 수행하고, seed 준비만 도메인/SQL 주입했다. 이후 IDB SQLite를 읽어 요청·SKU·수량·단가·동의버전·기한·발주행·예외보류를 확인했다. 자동정책은 고객요청부터 경영주 요약까지 측정하고 종료 뒤 변화없는 재검토에서 중복발주/알림0을 확인했다.
- 고객 완료·10SKU 승인 완료 PNG를 별도 직접 시각 확인했다. 이 장치는 360/768 및 확대/접근성 전체 QA를 대체하지 않는다.

| 업무 | 성공/예정 | 최대 activation | 최대 화면 이동 | 비모델 중앙값 ms |
|---|---:|---:|---:|---:|
| clear-1 | 3/3 | 5 | 2 | 491.9 |
| clear-2 | 3/3 | 5 | 2 | 481.4 |
| clear-3 | 3/3 | 5 | 2 | 491.0 |
| ambiguous | 3/3 | 6 | 2 | 585.5 |
| reconsent | 3/3 | 5 | 3 | 364.0 |
| batch-10 | 3/3 | 2 | 0 | 225.4 |
| auto-normal | 3/3 | 7 | 4 | 1625.8 |
| exception-batch | 3/3 | 2 | 0 | 256.7 |

수치는 자동화·타이핑·앱 처리시간이며 사람 사용성 연구가 아니다. 명확 요청은 자연어 제출 포함5회(제출 뒤4회), 추가질문0; 모호 workload 질문1회. 경영주 검토1화면/승인1회이며 자동정책 건별승인0이다. fixture의 네트워크 대기는 실제 모델 지연 증거가 아니다.

## live 경로 정적·mock 확인

기존 scripts/run_nl_eval.py Budget을 app-root에서 가져오고 prior reserve50·전체2400회/$15·후속 필수 예비량을 유지한다. 명시 approved config/고유run ID/최대calls 없이 live를 시작하지 않는다. 각 outbound 전에 durable reserve, 응답 뒤 finish이며 known usage만 숫자다. unknown usage/cost/provider 여부는 null과 보수적 hold로 남기고 후속호출 중단. maxRetries0/maxRedirects0, pending 재전송·동일run ID 재개 거절을 실제 mock tests로 확인했다. 원응답을 UI로 전달하며 실패를 fixture로 바꾸지 않는다. prior50을 실측50회라고 주장하지 않는다.

live 승인·실행, 실제 provider 지연/오류, baseline/best 비교, 배포 source attestation은 미실행이다. 정적 파일 hash와 BUILD_ID만으로 원격 배포 일치를 보장하지 않는다. 조정자가 live 전 정확한 빌드·같은 장치/seed/workload·예산 예약을 묶어야 한다.

## 증거와 동결

- 원본: `artifacts/private/run-20260921/ux-independent-v2/result.json`, PNG24개. 결과 SHA256 `a9ad669e0a3bcf7ea3291e78272a980648bd60d12b0e231571219ab50a5e0384`.
- workload `613bbb701a155913f02f2de4bf6f45fef793b1d3fa5e61cd5a5211a25e32d71d`; seed `4cb10e899c9706bb0a9278b458bd7b70d3c34bf28f649b62ffae0894794a2b45`.
- run.mts: `1242a81bcc40b99b80b5fa4727e5c0f0ee0a899ab80f9d304349c80a01d8b825`
- seed.mts: `a62dde6e62b70f47f870d42b9d4ced35477cfe0bc760a248582e8144adb9ee9e`
- metrics.mjs: `a73ee753ad73804241f64d8315758af736adf03c27a384be752e1189dad4ec54`
- live.mts: `a5b201b949b6d2405e4819fff65a3d54065a9b3a30949ec4a61814b347be9221`
- budget_bridge.py: `875f22a63091c6a406891b3e55549afd5dc1eff1b61b9f79baf5a505f253fe7b`

검토 시각: 2026-09-21T10:12:27.646065+00:00
