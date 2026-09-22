# N11 C8 공개 validation 첫 반복 독립 평가

**79/84 FAIL, incomplete1·mandatory0. 두 번째 validation·신규 holdout·UX 후속 실행0.** 고객 명확36/40와 경영주 명확14/15가 각각95% 최소에 미달한다. 전체 실행 프로세스의 정상 종료와 제품 품질 통과를 구분한다. 데이터 중복 의심을 발견했지만 동결 정답·분모·점수는 변경하지 않았다.

## 목적과 결속

D48의 구체 복구 위임에 따라 C8의 고객 생성 계약 수리가 정상 탐색/질문/미식별/정정과 경영주 업무에 미치는 영향을 공개 고정 validation에서 독립 평가했다. 평가자는 앱 수리 비구현자다. 본인이 작성한 평가 장치의 자체 분석은 장치의 독립 검증으로 세지 않으며 기존 research/builder의 별도 검증과 구분한다.

- source `bb2ab8056716c6d32669c1f8c6103a4a2ca397dd`, PR19 CI35672436354/35672452291 PASS, Preview `dpl_ALPxiLtpYPN3xSLMb1bKsri5cLe9`, READY/target null. 모델 `gpt-4.1-mini-2025-04-14`, prompt `customer-action-wire-v8`.
- context v18 SHA `b2d55452e0dd9b4efe9f72082f7e5c41618c486ecc4e710de640de3a3217644f` ACK. source33 현재/git 바이트 결속 및 실행 종료 후 불변 확인. runtime48 hash `66c63fad2b53398b1ffaa3d4230e1c0d5bae551f876daa91e94e88ed41573ec0`.
- 불변 config SHA `091b56c38acbbee03cc3ee0761e725c1dcbef098ab6f8d304465df3217b74441`, proof SHA `878f379e03246374db362fe5db6c573c09f229320c852ed95c2682a082a0dbcd`.
- 공개 고정84case/92turn, dataset hash `180e1ef3890bbde535e4be29a75698b5fa42d9e77a915da9d3d3646c9e486f46`, 기존 SQL 합성 업무 state hash `d1a0845a4f45f44af9698963c700e9dfa24d13bb3a4b8b729b9b15e8a15278e1`. catalog248·scorer·정답 불변.
- run `740c1f22-f0fb-49a5-91a2-f741436f15c3`, fingerprint `6c636045248f3c8a2e83622ffb996f5a8ee6ed14bbf91039d7f723ba65c28c12`. dev30 PASS 뒤 사전 조건부 GO와 PLAN_VALID 확인으로 한 번 실행했다. 첫 반복 FAIL이므로 두 번째 실행 조건은 충족하지 않았다.

## 역할·범주와 실패

| 역할/입력 | 전체 분모 통과 | 응답 완료 분모 통과 | 최소 | 판정 |
|---|---:|---:|---:|---|
| 고객 명확 |36/40|36/40|95%|FAIL|
| 고객 불확실 |20/20|20/20|90%|PASS|
| 경영주 명확 |14/15|14/14|95%|FAIL|
| 경영주 불확실 |9/9|9/9|90%|PASS|

범주별 고객 C01 9/9, C02 5/8, C03 8/8, C04 7/7, C05 6/6, C06 5/6, C07 6/6, C08 5/5, C09 5/5. 경영주 M01~M03 각각3/3, M04 2/3, M05~M06 각각3/3, M07~M09 각각2/2. 최악범주 C02 62.5%. 응답 없는 경영주1건을 분모에서 제외하지 않았다.

| 공개 사례 | 관측한 실패 |
|---|---|
| C02-validation-002 | 명시한 오리지널40g 정답 외 다른 맛/규격 상품을 confirm 후보로 추가 |
| C02-validation-004 | 명시한730ml 정답 외235ml를 confirm 후보로 추가 |
| C02-validation-007 | 명시한500ml 외340ml와 중복표기500ml ID를 confirm 후보로 추가 |
| C06-validation-006 | 최종 상품 정정은 성공. 이전 turn의 추가500ml ID 때문에 earlier_turn_oracle_failure |
| M04-validation-001 | 현재안 undo에서 HTTP502 INVALID_MODEL_RESPONSE, 허용 진단 OUTPUT_CONTRACT. 원문 응답은 없어 특정 필드 원인 미확정 |

카탈로그 점검 한계: C06에서 추가된 `DEMO-6AFC6A69B100`과 동결 정답 `DEMO-778B67C87CCC`는 브랜드/500ml 규격/sourceURL이 같고 이름의 규격 중복표기가 다르다. 따라서 이 건은 상품 중복 또는 정답 집합의 모호성 가능성을 별도 조사해야 한다. 현재 frozen oracle의 실패를 성공으로 바꾸지 않았다. C02-validation-007에는 별도340ml 추가도 있으므로 이 모호성만으로 해당 실패가 해소되지는 않는다. 이번 분석에서 출처 웹 원문을 다시 조회하지 않았으며 제품 동일성 확정으로 표현하지 않는다. 카탈로그·정답·평가 기준 변경0이다.

경영주 오류는 provider_called=true, input12694/output83, 알려진 비용$0.0052104다. 진단 코드만으로 출력의 어느 필드가 틀렸는지나 고객 wire 변경이 경영주 오류를 유발했는지 확정하지 않는다. 오류를 복구하기 위한 실제 재호출은 하지 않았다.

## Paired 비교와 채택 판정

| 동일84 비교 | 이전 통과 | C8 개선 | C8 회귀 |
|---|---:|---:|---:|
| B0 |58/84|25|4|
| C5 첫 반복 |84/84|0|5|
| C7 첫 반복 |83/84|1|5|

B0 정상 회귀는 C02-validation-002/004, C06-validation-006, M04-validation-001이다. C7에서 실패했던 C04-validation-001은 통과했지만 다른5건 회귀를 상쇄하지 않는다. 두 명확 역할 최소 미달, incomplete1, 정상 회귀 때문에 채택 불가이며 `nl_minimum_pass=false`, `stage_ready=false`다. dev30 성공이나 순증21건으로 최소·회귀 기준을 면제하지 않는다. 과거 모든 후보 실패와 C5 보호셋 실패는 보존한다.

## 실제 사용량과 종료

92attempt/92계획turn, HTTP200 91·실패1, retry0, 이번 usage unknown0·provider unknown0·pending0·stop null. 토큰1,175,988, 추정 비용$0.485232, 최대attempt $0.0066944/input15209/output440. P50 2849ms/P95 4847ms. 청구 확정액이나 계정 잔액을 뜻하지 않는다.

종료 공유 장부 upper1350calls/$8.6217717 = known1300calls/$6.0717717 + prior50/$2.50 + 이전 unknown usage$.05. prior는 실측이 아니다. ledger SHA `d5378e4562e8f681b242d89c9d4a603e36c57937b57aee636d55d1a05045c6ab`. 실행 동안 미래708/$7.434·다음unknown$.05·전체2400/$20 및 보수적 중복예약 STOP을 유지했다. 종료 후 실제 호출/장부 변경0.

원본은 private `n11-c8-validation-01/checkpoint.json`·observations·driver 로그, 분석은 `n11-c8-validation-01-analysis/`에 보존했다. candidate-report SHA `535313a5ef36d4c2b78ca88400db7a623a42120ebecc621f27e2d3fec4bb7a2f`; 공개 사례만 포함한 private diagnostic-summary SHA `cf5d6468558936eeb1e6ec36248bc242e427e3680ffc1562fd014678b78ef534`. 구현자에게 전달한 진단에 보호셋 원문/정답은 없다.

두 번째 validation은 미실행84/92, 신규 보호84/92도 미실행이며 접근0이다. UX-v3·양 역할 최종QA·G5·G6는 이 결과로 통과하지 않았다. D48의 다음 bounded 복구 판단은 root 담당이며 새 source/config/정확배포/GO 전 추가 평가하지 않는다.
