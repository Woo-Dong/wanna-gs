# N02 baseline 독립 평가 결과

판정: **기준선 평가 실행 완료 / 자연어 최소 품질 FAIL / 출시 후보 채택 불가**. 실행 완료는 정상 응답 또는 실패 결과가336개 전부 기록됐다는 뜻이며,51건의 응답 실패를 완료 성공으로 계산하지 않는다. 추가 모델 호출로 실패를 덮지 않았다.

독립 evaluator method_auditor가 exact Preview `10c00723d0b64ea47a06dcbd00e2b671e7c62daf`, prompt baseline-v1, model gpt-5-mini-2025-08-07, catalog248/f2696…에서 한 번 실행했다. run_id `214fba09-c781-43e6-94aa-bec437f305b2`, fingerprint `80f9a9a1e7106ae84dd3797d2ca45f825a3f3eef4a2623d8ac3083e400e5f11b`. config SHA `0f0ecca371e26561ba660997a544485955c77958bfb1783d2985417c4e9d754f`. 원격 API 자체의 source SHA/prompt hash attestation은 없으며, READY immutable deployment artifact와24개 tracked source byte 대조로 결속했다.

## 분모와 결과

- 공개 baseline336: PASS227/336(67.56%), 고객196/240, 경영주31/96. dev169/252, validation58/84. 각 보고서는 같은 run_id의 분할이며 독립 repeat2개가 아니다.
- 285개 사례는 schema-valid 응답까지 완료, 그중58개는 의미/이전턴 정답 실패. 51개는 INVALID_MODEL_RESPONSE. 전체109개 실패를 분모에 유지했다. mandatory_errors0은 관측된 필수 오류가 없다는 제한된 결과이며 실패51개나 최소기준 미달을 면제하지 않는다.
- 계획368 user turns 중 실제367호출. C06-dev-017 첫턴 실패로 두번째턴을 호출하지 않았다. 그 사례 전체는 실패이며 분모336은 불변. 367시도 전부 provider_called=true/usage확인, 성공응답316turn/실패51turn, retries0, pending0, stop_code=null.
- input6,147,352/output61,137/total6,208,489 tokens. 실제 추정요금 $1.659112. HTTP attempt latency P50 2420ms/P95 4460ms, validation P95 4052ms. 이는 화면 업무시간/UX p95가 아니다.

| 역할/분할/분류 | 성공/전체 | 정확도 | 최소 | 판정 |
|---|---:|---:|---:|---|
| customer/dev/clear | 98/119 | 82.35% | 95% | FAIL |
| customer/validation/clear | 34/40 | 85.00% | 95% | FAIL |
| customer/dev/uncertain | 48/61 | 78.69% | 90% | FAIL |
| customer/validation/uncertain | 16/20 | 80.00% | 90% | FAIL |
| merchant/dev/clear | 15/45 | 33.33% | 95% | FAIL |
| merchant/validation/clear | 7/15 | 46.67% | 95% | FAIL |
| merchant/dev/uncertain | 8/27 | 29.63% | 90% | FAIL |
| merchant/validation/uncertain | 1/9 | 11.11% | 90% | FAIL |

## 실패 분석

reason별 횟수는 서로 겹친다: transport_failure51, incorrect_candidate14, correct_sku_missing6, command_composite_mismatch27, wrong_action10, earlier_turn_oracle_failure8. 실패별 원문 공개 발화/expected/응답/attempt는 private n02-baseline-analysis/public-failures.json에 보존했다. 보호 holdout은 읽거나 호출하지 않았다.

고객: 정확 상품명에서 팥인절미→부드러운맛, 명란마요김밥→참치계란김밥처럼 이름과SKU연결이 틀린 관측이 있다. 불확실 다후보 C04는15/28 실패(dev12+validation3)로 낮다. 후보 표면 유사성만으로 정확판정을 대체할 수 없다. INVALID_MODEL_RESPONSE는 여러 서버 계약검사가 공유하는 오류로 원모델 raw가 없으므로 하위원인을 확정하지 않는다.

경영주: M01 제외12개 전부 실패. 대표 M01-dev-001은 제외SKU 자체는 맞지만 현재상태의 예산50000/수량12를 불필요하게 복사했다. API prompt는 명시되지 않은 조건을 null/empty로 반환하도록 하고 있어 expected composite와 다르다. M03의 잘못된 SKU/불필요조건, M05의 상충지시를 clarify 대신 modify로 만든 관측, M06 stale 명령의502실패, M09의최종응답은 맞아도 이전턴 오류가 남은 경우를 구분했다. 기준을 느슨하게 바꾸지 않는다.

## 예산·후속 경계

공유 ledger는 actual367 + 보수적 prior50 = accounted upper417, measured cost1.659112 + prior planning2.50 =4.159112이다. prior는 실제 사용량 주장이 아니다. future1032 calls/$10.32 reserve는 이번 단계 내내 유지했다. 총2400/$15 softstop을 확장하지 않았다. 다음 단계는 실제 실행별 예약구조를 검토하며 같은 ledger를 유지해야 한다.

최소기준 미달이므로 baseline을 best로 지정하거나 holdout을 실행할 수 없다. 별도 C1 후보는 거절범주 recall 회귀를 수정한 뒤 기술16tests/schema정적검사만 PASS했으며, 실제 API 수락/정식dev·validation 반복/UX48/G5/G6는 이 보고서로 통과하지 않는다.
