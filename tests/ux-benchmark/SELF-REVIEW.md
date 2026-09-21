# UX benchmark 자체 검증 기록

fixture 준비 검증이며 live baseline/best 및 독립 UX QA가 아니다. 실제 모델 호출0, 제품 소스 변경0, 보호 holdout 접근0.

- 최종 실행: fixture-04, 24/24 PASS, 모든 Worker 시각 1789959600000 일치.
- 실제 브라우저 http://localhost:3217, 실제 Worker/sql.js/IndexedDB, fixture HTTP18건.
- metrics unit3 PASS, 해당 .mts 전체 타입 검사 PASS.
- Workload hash: `d77ed05df8ddf169d1243f6ade321f703067f3bd9ffe6a057046474c7a987eeb`
- Seed hash: `4cb10e899c9706bb0a9278b458bd7b70d3c34bf28f649b62ffae0894794a2b45`

| 업무 | 반복 | activation 최대 | 화면 이동 최대 | 비모델 자동화 시간 중앙값(ms) |
|---|---:|---:|---:|---:|
| clear-1 | 3/3 | 5 | 2 | 524.1 |
| clear-2 | 3/3 | 5 | 2 | 480.3 |
| clear-3 | 3/3 | 5 | 2 | 483.6 |
| ambiguous | 3/3 | 6 | 2 | 656.6 |
| reconsent | 3/3 | 5 | 3 | 354.8 |
| batch-10 | 3/3 | 2 | 0 | 211.4 |
| auto-normal | 3/3 | 7 | 4 | 1541.7 |
| exception-batch | 3/3 | 2 | 0 | 239.7 |

시간은 자동화 도구+타이핑+앱 처리 시간이며 사람 수행시간이 아니다. fixture의 모델 대기는 실제 모델 지연 증거가 아니다. 자동정책은 고객5 activation + 역할전환1 + 경영주 요약1, 건별승인0. 변화없는 재검토의 중복발주/알림0을 측정 종료 뒤 검증했다.

초기 장치 오류도 evidence/fixture-01~03에 보존했다. 01은 consent SQL행의 계산 status 오조회로 실패·중단(미실행 분모 유지), 02는 about:blank initScript의 IDB 경고/재동의 상세펼침 누락/자동발주 문구 exact selector 오류, 03은 21PASS/auto3 selectorFAIL였다. 제품 기준을 완화하지 않고 각 장치 오류를 수정한 최종04에서 전체24를 다시 실행했다.

초기 fixture-only 단계 복사 목록은 run.mts, seed.mts, metrics.mjs, metrics.test.mjs, README.md, SELF-REVIEW.md였다. 최종 편입 시 live.mts/live.test.mts/budget_bridge.py/test_budget_bridge.py/seed.test.mts도 포함한다. 대형 원본 evidence는 이 작업 공간에 유지한다. I01 source 동결 후 다음 단계에서만 편입. 실제 모델 baseline/best는 예산 ledger 연결 및 독립검토 후 별도 실행해야 한다.

## live 실행 기능 보완 — 자체 검증

- live 경로와 같은 goal Budget bridge 구현. prior50, 기존 nl-budget.json 고정, 명시적 승인 config/호출수/필수예비량 없으면 실행 거절. 동일 run ID claim 재사용 및 pending 요청 재전송 금지.
- Python 예산 반례7 PASS: 승인 없음/후속예비량2400 및$15/18회상한/pending/unknown/null/모델불일치/승인변경 차단. 임시 가짜 장부만 사용하며 실제 goal 장부에 쓰지 않았다.
- Node 전송 mock2+metrics3 PASS: reserve pending이 실제 fetch 전에 존재, maxRetries0/maxRedirects0, 원응답 객체 그대로 UI전달, 불확실 요청 뒤 실제 fetch 추가0. 실제 네트워크/모델 호출0.
- 전체 신규 .mts 타입 검사 PASS. `--live` 승인 config 미지정 실행은 브라우저 생성 전에 EXPLICIT_BUDGET_CONFIG_REQUIRED로 거절됨.
- live HTTP 대기와 budget bridge 계측비용을 분리했다. model usage/cost/provider 여부가 불명인 실패는 null, 자동재시도0 및 전체실행 중단. UI 평가 경로를 건너뛰지 않는다.
- live-capable fixture-05 전체 회귀는23PASS/1setupFAIL. 한 run에서 정적JS/CSS 미적용 초기SSR 화면으로 Worker snapshot timeout이 발생했고, 그 뒤3run은정상. 같은 시간 다른root build 진행과 관련 가능성은 **추정**이며 확인 전이다. 실패스크린샷/분모 보존, 자동재시도하지 않았다. 안정된 고정 서버에서 최종24 재검증 예정.
- 실제 live baseline/best 실행은0이며 별도 root 승인과 독립 검토 후 진행한다. 초기 fixture-04 24PASS를 새live기능의 최종browserPASS로 재분류하지 않는다.

## 안정 서버 최종 회귀 (live-capable 장치)

- root GO 서버 session43527 / BUILD_ID CUrNHupSVyUb-hT2779kW에서 fixture-07 **24/24 PASS**, 모델0, 실제 goal ledger 쓰기0.
- Worker snapshot clock24회 정확 일치, 고객/경영주/자동정책/예외 묶음 전부 실제 UI→SQLite→IndexedDB 검증.
- fixture-06은 조정자의 서버 재시작 지시에 따라 수동 중단(2PASS/진행중1중단FAIL/나머지미실행). 해당 실행을 완주로 세지 않았다.
- fixture-05 setup실패를 지우지 않고 보존한 뒤 안정 서버에서 전체24회를 다시 실행했다.
- 최종 workload hash: `4c0fe16d19f2e6645e53ba978789f433831bb072dfb23642374799e9b8cc2a65`. baseline/best는 이 코드버전과동일harness/workload/seed/clock이어야 한다.
- 이 준비검사 PASS가 실제 live 측정·독립측정기승인·최종goal완료를 대체하지 않는다.

### 구현 소스 fingerprint

- run.mts: `a80e4e10bd71cea3b98baf33aff45344148540bb643401a2ecc47c4131cb42c1`
- seed.mts: `32b2b97f5bbae393465a0f3c6e85be35748905ac4eb47028ec09d2ce29b832a4`
- metrics.mjs: `ddf1e231d9a861e9831aa041d49c4af01456a78397f83213ae8db85927ae8558`
- live.mts: `55c852d0b9ea695e2a62093511db4adc6c242e00fdd83347220e38756d6853d0`
- budget_bridge.py: `875f22a63091c6a406891b3e55549afd5dc1eff1b61b9f79baf5a505f253fe7b`

## 독립 초검 반례 수정 (v2, 실제 모델0)

- 반복1을3번 넣는 중복이 완료로 판정되던 결함: 고정8종과 반복1·2·3 유일성을 강제하고 duplicateRepetitions/invalidRepetitions/missing 보존.
- 비교시 누락/빈 summary가 통과할 수 있던 결함: 두 summary/workload 집합 모두 고정8종을 강제하며, raw runs로 재계산하여 저장된 complete 필드 조작을 신뢰하지 않는다.
- seed 실행 엔진과 app-root 기록 소스 불일치: 매 prepare 전에 engine/contract 바이트hash 일치가 필수. 다르면 SEED_ENGINE_SOURCE_MISMATCH로 거절하고 실제 binding을 결과에 기록.
- route.fulfill 지연을 예산시간으로 잘못 제외: reserve/finish 호출 구간만 budgetInstrumentationMs로 합산하며 deliveryMs는 nonModel에 남긴다.80ms 모의 전달 지연 반례 회귀 포함.
- 예산 중단 상태가 있으면 전체 complete=false도 명시.
- 자체 Node10 PASS와 신규mts 타입검사 PASS. Python bridge는 변경0(기존7 PASS). 실제 goal ledger 쓰기0, 모델0. fixture07의 v1 24PASS는 v2 결과로 재분류하지 않으며 v2 독립24run을 검토자에게 넘긴다.

### v2 동결 소스
- run.mts: `1242a81bcc40b99b80b5fa4727e5c0f0ee0a899ab80f9d304349c80a01d8b825`
- seed.mts: `a62dde6e62b70f47f870d42b9d4ced35477cfe0bc760a248582e8144adb9ee9e`
- metrics.mjs: `a73ee753ad73804241f64d8315758af736adf03c27a384be752e1189dad4ec54`
- live.mts: `a5b201b949b6d2405e4819fff65a3d54065a9b3a30949ec4a61814b347be9221`
- budget_bridge.py: `875f22a63091c6a406891b3e55549afd5dc1eff1b61b9f79baf5a505f253fe7b`
- metrics.test.mjs: `0004fc04e262c575cb49852ffa70ddeb90a0602b6de4b57118fc293aca074f74`
- live.test.mts: `7ad1705a3d7cd04fbbdc22809cf60605f60300aa9e522231c6ac59c30f22cae6`
- seed.test.mts: `b8affa18d8aa0a209f40eb09f164b731133c5fbf256e759a37b8637efc8aa6a5`
