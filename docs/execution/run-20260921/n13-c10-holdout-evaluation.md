# N13 C10 신규 보호 holdout 최초1회 독립 평가

**76/84 FAIL. 고객 불확실 입력12/20(60%)로90% 최소에 미달했다.** 고객 명확40/40, 경영주 명확15/15·불확실9/9은 통과했고 incomplete0·mandatory0이다. 전체 통과율로 역할별 미달을 상쇄하지 않는다. 역할QA·UX·G5·G6 후속 실행은0이며 이 실패를 재실행해 통과 결과로 교체하지 않는다.

## 목적·독립성·실행 경계

새 데이터는 C5 원래 보호셋의 실패 이후 docs21/23·기존 복구 계약에 따라 만든 독립 replacement다. revision01/02 데이터 검토FAIL과 revision03 독립DATA-REVIEW PASS를 보존했고, 작성자와 다른 데이터 검토자의 전수 검토를 거쳤다. 데이터 검토PASS는 모델 품질PASS가 아니다. C10 구현자/root는 보호 원문·정답·사례ID를 읽지 않았으며 이 보고서는 집계만 공유한다. 평가자는 앱 비구현자다. 자신이 작성한 scorer/runner를 자기 독립 검증으로 세지 않으며 기존 별도 research/builder 장치 검토를 구분한다.

- 신규 dataset `18f2a373dc48b372f166e6dd6f51fd97687a406e33f8f601fe814bbeafd6c305`,84case/92turn,고객60·경영주24. public manifest-v2 SHA `3670b985b0189b4e7609af0acbce7bba792a4263a31ac62a246ad64e7d32ab60`, 독립 데이터 review SHA `cfb44b7a0a74411a658a2ed467b9ca6faaec3faf850a95bd3c4ef8e55d29a41c`.
- C10 best freeze `2026-09-22T02:21:20.770504+00:00`, private freeze SHA `f9bf6afd1c92cb26e8964490c536671490669a481c6f99c72f870188144eccda`. 공개 validation 두 반복84/84 및 각각의 최소/회귀 기준 통과 뒤 root가 동결했다. 그 뒤 평가자가 source/runtime/동일 config와 고유 validation run/보고를 재확인했다.
- source `a7adafc0381e9ad069030b1cd13b181790763e89`, source35/runtime50, runtime hash `c66d01832a9f86a63d86ff4ab0ed616cb46f267d74ecb8a2cc0018d0c041cdec`, context 최종v20 ACK76. 실행 종료 source/runtime도 불변이다.
- Production `dpl_64GFUovXy4nSD8xgNVxhJDQoWy6a`, 정확 불변URL `https://wanna-21x18bnmi-beatrain-4635s-projects.vercel.app`, READY/target production/exact source. model `gpt-4.1-mini-2025-04-14`, prompt `customer-size-grounded-v10`, catalog248 hash `f2696abe92521e3ff8f9ab43cb36a1d297a6fd23d272e239605b49fab4343b1e`.
- holdout config SHA `3a7be79eef1f9d5822c60e0dde27eac5fa7ff0426a9e0e73116f987e1cc0147f`, 보호 SQL state SHA `14a7c12ddacf3624dab6370c9f22421bf3ac6b488594606241b63f9c74108935`.
- run `0c70f6af-a17c-4cad-a150-a5d638267c0f`, fingerprint `9312b209f57768b0920b25b7815843ce19dba37a5a738ce402dcd8f8bf493b97`.

명시GO 뒤 최초 미사용 dataset claim·실장부·PLAN_VALID84/92/96을 확인하고 한 번 실행했다. 실행 시작 claim은 이 run에 연결됐고 이전 retired 보호셋을 재호출하지 않았다. 이번 셋은 현재 후보의 튜닝/후보비교에 사용하지 않은 최초 평가다. 과거 retired셋 실패 후 수행한 복구 이력이 없었다고 주장하지 않는다.

## 역할·범주·관측 오류

| 역할/입력 | 통과/전체 | 응답 완료 | 최소 | 판정 |
|---|---:|---:|---:|---|
| 고객 명확 |40/40|40/40|95%|PASS|
| 고객 불확실 |12/20|20/20|90%|FAIL 60%|
| 경영주 명확 |15/15|15/15|95%|PASS|
| 경영주 불확실 |9/9|9/9|90%|PASS|

고객 C01 9/9, C02 8/8, C03 8/8, C04 5/7, C05 2/6, C06 6/6, C07 6/6, C08 3/5, C09 5/5. 경영주 M01~M06 각각3/3, M07~M09 각각2/2. 최악범주 C05 33.33%다.

오류8건은 모두 구조화 응답과 실제 존재 ID를 반환했지만 해당 요청에 적절한 행동 대신 candidate를 제시한 `wrong_action`이다. 범주별 C04 모호/다후보2, C05 미등록/미식별4, C08 범위밖2다. 불필요한 추가 질문이나 HTTP/schema 실패가 이번8건의 직접 채점 이유는 아니다. 허구 SKU·무권한 거래 등 mandatory 오류로 분류된 건은0이며 의미 행동 실패를 성공으로 바꾸지 않는다.

보호 텍스트·정답·상품·사례ID 및 구체 정답 조건은 공개하지 않았다. 이 집계만으로 모델의 내부 원인을 확정하거나 데이터/oracle 결함이라고 자동 주장하지 않는다. 현재 독립 직접 증거에 의해 새 oracle-integrity 결함이 확인된 것은 없고, 원래 기대 행동·라벨·분모·점수를 그대로 적용했다. 원본 개발/validation에서 조사한500ml 표시 모호성을 이번 보호 오류의 면제로 전용하지 않는다.

## 실제 사용량·종료

92계획turn/92outbound, HTTP200 전부, retry0·이번 usage unknown0·provider unknown0·pending0·stop null. 전체84를 완료한 실행 성공과 품질FAIL은 구별한다. 토큰1,352,033, 추정비용$0.5568236, 최대attempt $0.0066628/input15552/output374. P50 2457/P95 4155ms. 비용은 공급자 청구 확정액이 아니다.

종료 공유 upper1786/$11.0094737 = known1736/$8.4594737 + prior50/$2.50 + 이전 unknown usage$.05. prior는 실측이 아니다. ledger SHA `7cfce2906a5e56814e65614eb9a4657504316a1426e5ccf3d45aaf172eb60fad`. 실행 동안 후속96/$1.008, 현재stage 잔여turn×3, 총2400/$20·다음unknown$.05 가드를 유지했다. 실제 후속 검사 미실행을 예산 잔량만으로 PASS로 간주하지 않는다.

## 증거와 후속 중단

공개 `quality/release/evidence/c10-holdout/`에 sanitized report/execution/binding/independent-report/bundle을 발급했다. independent-report status FAIL, aggregate check not_ready다. bundle SHA `6fa71fefbde045635525d220c5e86b8752acd27d37a67b0999425e3d7c67ae9e`. 공개 증거에서 source/run/freeze/시각/원본해시·분모·token·비용을 대조하고 보호 원문을 제외했다. private `n13-c10-holdout-01/`와 `n13-c10-holdout-01-analysis/`에 전체 실행·정답 대조·진단을 보존한다.

보호셋의 동일 실행 반복0, root/구현자 원문 제공0, 사후 정답/라벨/점수 변경0. 이전 C5 보호FAIL 및 새셋 생성 중 두 FAIL 이력도 보존한다. C10은 validation 선행조건을 충족했지만 최종 보호 최소 미달로 출시 가능한 best가 아니다. 역할QA/UX의 준비물은 미실행으로 남기고 후속 자동실행·G5/G6·최종 완료 선언을 하지 않는다. 추가 복구는 root의 별도 근거·독립 검토·남은 예산 판단을 필요로 하며, 이 결과를 보고 다시 튜닝한다면 현재 보호셋을 계속 미노출 최종검사로 사용할 수 없다.
