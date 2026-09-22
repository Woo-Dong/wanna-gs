# N13 C10 공개 validation 두 반복 독립 평가

**첫 반복84/84, 둘째84/84 PASS.** 각 반복의 역할별 최소·incomplete0·mandatory0, B0 대비26개 개선/정상회귀0 및 C5 대응 반복 핵심·필수정상 회귀0를 각각 확인했다. 동일 설정을 새 run으로 독립 실행했으며 결과를 합쳐 실패를 상쇄하지 않았다. validation 선행조건 통과이지 최종 holdout/UX/G5/G6 완료는 아니다.

## 목적·실행 결속

고객의 확실한 단일 규격 요청에서 다른 규격을 primary로 제시하는 문제를 일반 규칙으로 수리한 C10을 앱 비구현자가 평가했다. 고객 모호함·정정·대안·경영주 현재/미래/undo와 원래 확인·동의·거래검증을 유지한다. 숫자 구두점/Unicode 부호의 합성 반례 수리 후 기술·독립검증/CI를 거친 소스다. 본인 작성 분석기/내보내기 작업을 독립 평가 장치 검증으로 세지 않는다.

- source `a7adafc0381e9ad069030b1cd13b181790763e89`, Production `dpl_64GFUovXy4nSD8xgNVxhJDQoWy6a`, 불변URL `https://wanna-21x18bnmi-beatrain-4635s-projects.vercel.app`, READY/target production/exact source 확인. PR21 CI35678079901/35678073862·mergeCI35678227688 PASS 통보.
- 최종 context v20 SHA `6fffa1419a57a7c12e5b641251a0cec741e31dccad0369fee447f21533ba3e31` ACK76. source35/runtime50 현재 및 exact git 바이트 일치, runtime hash `c66d01832a9f86a63d86ff4ab0ed616cb46f267d74ecb8a2cc0018d0c041cdec`. 각 실행 종료 source35 불변.
- model `gpt-4.1-mini-2025-04-14`, prompt `customer-size-grounded-v10`, catalog248 hash `f2696abe92521e3ff8f9ab43cb36a1d297a6fd23d272e239605b49fab4343b1e`. 정답/범주/분모/SQL 업무state/채점기 변경0.
- 두 반복 모두 config SHA `0b36f1d804be4da87cd4940f6cdc80420d6afac14af4bb74bb10b9e65fde8bb6`, 불변 deployment proof SHA `4fb7ddfa2e3b14c5bc5f9063e774583fd1118df238cd8db0fb0723fc4a01ca68`.
- 동일 공개84case/92turn, dataset `180e1ef3890bbde535e4be29a75698b5fa42d9e77a915da9d3d3646c9e486f46`, run fingerprint `9b014d81a543196d131b3f6c0745d19158809c62382ca3e7f294152e81d6b484`.
- run01 `a56deb49-aa47-4581-8554-1abc3ce06c2c`, run02 `aa50fbab-c7de-408c-b66c-fb98f190e2e9`. 고유run·전체새실행·동일fingerprint를 repeat_ready와 원래 채택 조건으로 확인했다.

dev30 PASS 뒤 root 조건부GO와 PLAN_VALID로 첫 반복을 실행하고, 첫 반복 모든 조건을 확인한 뒤 같은 config의 둘째를 실행했다. 별도 smoke/선별 재호출/출력 수정0이다.

## 각 반복 결과와 비교

| 역할/입력 | 첫 반복 | 둘째 반복 | 최소 |
|---|---:|---:|---:|
| 고객 명확 |40/40|40/40|95%|
| 고객 불확실 |20/20|20/20|90%|
| 경영주 명확 |15/15|15/15|95%|
| 경영주 불확실 |9/9|9/9|90%|

18범주 모두 각각100%: 고객 C01 9, C02 8, C03 8, C04 7, C05 6, C06 6, C07 6, C08 5, C09 5개; 경영주 M01~M06 각각3개, M07~M09 각각2개. 각 반복 incomplete0·mandatory0·fatal 오류0, stage_ready/nl_minimum_pass=true다.

| 비교 | 첫 반복 개선/회귀 | 둘째 반복 개선/회귀 |
|---|---:|---:|
| 고정 B0 동일84(58통과) |26/0|26/0|
| C5 대응 repeat01(84)/02(83) |0/0|1/0|
| C7 첫 반복(83) |1/0|1/0|
| C8 첫 반복(79) |5/0|5/0|
| C9 첫 반복(83) |1/0|1/0|

C5 둘째의 C08-validation-002가 개선됐고 핵심범주·필수정상 회귀는 두 번 모두0이다. B0 incomplete10과 과거 모든 후보 실패를 보존하며, compare_candidate의 invalid_baseline을 PASS로 바꾸지 않는다. 사전 계약의 고정B0 paired 개선 수와 정상회귀0 및 별도C5 대응회귀 조건을 직접 대조했다.

C9에서340ml가500ml 요청 primary에 포함됐던 C02-validation-007도 두 번 모두 원래 oracle을 통과했다. 출처의 두500ml/포장구분 누락은 기존 평가의 보수적 한계로 계속 공개한다. 그 한계 때문에 허용 정답을 넓히거나 과거 실패를 성공으로 바꾸거나 특정SKU 우선 특례를 두지 않았다. 이번 결과로 catalog의 모든 동등성/포장 정보를 완전히 검증했다고 주장하지 않는다.

## 실제 사용량·지연

| 항목 | 첫 반복 | 둘째 반복 |
|---|---:|---:|
| outbound/계획turn |92/92|92/92|
| retry·실패attempt·이번unknownusage |0·0·0|0·0·0|
| 알려진 token |1,189,287|1,189,410|
| 추정비용USD |0.4903584|0.4902612|
| 최대attempt USD |0.0065800|0.0066964|
| 최대input/output token |15357/321|15342/393|
| P50/P95 ms |2768/4413|2708/4144|

각 반복 provider unknown0·pending0·stop null. P95는 B0 4052ms보다 느려서 속도 개선에 의한 채택으로 설명하지 않는다. 총184calls/$0.9806196이며 공급자 청구 확정액과 다르다.

둘째 종료 공유 upper1694/$10.4526501 = known1644/$7.9026501 + prior50/$2.50 + 이전 unknown usage$.05. prior는 실측이 아니다. ledger SHA `014864cfc0b546bd7deb2c4d72b70612651c1c22d5269d8aed0bf4120e392a6a`. 두 반복의 후속464/$4.872와 현재stage 잔여turn×3, 전체2400/$20 및 다음unknown$.05 STOP을 고정했다. 앞단 정상 실행 후 둘째 진입2342를 충족했고 설정을 중간 축소하지 않았다. 미래 예약은 필수1+선택retry여유1이며 모든 단계 최대retry 완주 보장은 아니다.

## 공개 증거와 남은 게이트

공개 집계 bundle은 `quality/release/evidence/c10-validation-01/` 및 `c10-validation-02/`의 report/execution/binding/bundle이다. 비공개 원본은 `n13-c10-validation-01/`, `-02/` 및 각각의 analysis/driver로그다. 집계의 token/cost/분모/run/source/runtime와 원본 해시를 대조했고 원문·정답·키·보호내용을 내보내지 않았다. 원래 baseline bundle은 변경하지 않았다.

원본 candidate-report SHA: 첫 `503ce00a4ab998bbaee302abfc9f75ff3dc11a2b94962ba8e21ae6885039d69e`, 둘째 `9659374ec73a53491f68835434c117349febd584412a4c7e18d6e619fff67320`.

평가자는 validation 선행조건 PASS를 root에 전달했다. 아직 신규 holdout 원문 접근/실행0이며 root의 best freeze·별도GO를 기다린다. 보호셋 최초평가·ADR007 실제 UX·고객/경영주 최종QA·최종정책감사·G5·main/제출Production G6는 별도 남은 단계다. 중간 Production READY나 validation PASS를 목표 완료로 기록하지 않는다.
