# D-46 goal API 비용 상한 $20 변경 독립 검토

판정: **좁은 예산 실행기 변경 PASS**. 사용자 직접 승인 D-46을 확인했다. 구현자는 preflight_builder, 검토자는 method_auditor다. 실제 장부 수정·모델 호출·holdout 본문 접근0이며 이 PASS는 C5/UX 실제 실행 승인이 아니다.

## 변경과 보존

`scripts/run_nl_eval.py`는 `GOAL_API_COST_SOFT_LIMIT_USD=20.0`과 승인 근거 주석을 추가하고 기존 reserve의 `>=15` 비교값만 이 상수로 바꿨다. $20는 로컬 goal 추정비용의 소프트 중단 기준이며 크레딧 구매나 공급자 hard cap이 아니다. 2400호출, prior50, unknown$.05, 현재·미래 필수 예약, 과거 실패·사용량·holdout claim·pending 처리 로직은 동일하다. 서버 provider의 인스턴스별15 제한은 별도이고 변경되지 않았다.

| 검토 파일 | SHA256 |
|---|---|
| scripts/run_nl_eval.py |3eed146c30ddb822be416f69009a422c4fb2ae0646ca1c3394b6fca4dacd152d|
| tests/eval-runner/test_nl_transport.py |4bd2b5188d59ef1a852f839469e38a365950eaed0958e70a061b31fb5f1933bd|
| tests/ux-benchmark/test_budget_bridge.py |46cfb1a289e4b9e94440cd197a7fa830a3057a538e07ab263a9a3a51577a5c5b|

## 실제 독립 검증

- 기존 전송 suite30개와 UX budget bridge7개를 비구현자가 실행해 모두 PASS했다. 과거15 초과 fixture의 기대를20 경계에 맞춘 변경은 D-46 근거가 있으며 제품 품질 기대값을 바꾼 것이 아니다.
- 별도 임시 디렉터리 장부로 독립9검사를 만들었다. 합계15 허용,19.999 허용,20 정각 거절,20 초과 거절, 과거 paid failure/unknown 이력 불변, provider=false 반환의 예약 해제, pending의 다음 호출 비용 점유,2400 정각 허용/2401 거절, 미래 호출예약·prior/unknown 설정 결속을 검사했다. 모두 기대대로였다.
- 20 이상 거절 시 새 attempt가 없고, 허용 시 pending1개만 생성됐다. 과거 실패/unknown 레코드와 보호 claim은 바뀌지 않았다. 모의 ledger의 `prior_actual_calls=unknown`을 실측으로 바꾸지 않았다.
- 실제 goal 장부는 바이트 hash `9b4ff740edfb5be0aa2cea4edaa4c2f61c8b7fafc717a1f6c5247dcd82616cf7`로 읽기 전후 동일하다. 보호 본문이 아닌 ledger의 기존 claim 보존만 임시 데이터에서 시험했다.

증거: private `budget20-independent.py`, `budget20-independent.json`, `budget20-tests.log`, `budget20-ux-tests.log`. 독립9검사와 구현자 suite 재실행37개를 구분한다. 검토자 소유였던 기존 runner 전체를 자기 독립 검증으로 재분류한 것이 아니라, 다른 구현자가 작성한 이번 단일 상한 변경 및 인접 계약을 검토한 범위다.

## 후속 실행 경계

이전 C5 차단 계산$15.8495333은 과거$15 계약에서는 올바른 STOP이었다. D-46이 상한을20으로 바꾼 뒤 동일 산술은 비용 조건만으로 막히지 않지만, ADR007의 새 UX 예약96 등 후속 계약이 채택되면 미래 예약을 다시 산정해야 한다. 과거 동결 config의 runner hash를 바꾸거나 예전 실패를 소급 PASS로 수정하지 않는다. 새 source/hash/config·실제 배포·별도 GO가 필요하다. 자연어 최소·두 반복·holdout·UX·G5/G6 기준은 그대로다.
