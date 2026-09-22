# N13 C10 공개 dev30 독립 평가

**30/30 PASS, incomplete0·mandatory0·B0/C1~9 정상 회귀0.** 원래 선택30개의 최소 기준 통과이며 전체 dev가 아니므로 stage_ready=false다. validation/holdout/UX/G5/G6를 대신하지 않는다.

## 목적·결속

D48/D49에 따라 고객의 확실한 긍정 단일 규격만 생성 enum에 반영하는 C10을 앱 비구현자가 평가했다. 부정/모호/정정/대안/복수규격·미지원 표기에서 전체 후보를 유지하는 경계, 경영주v9·거래 동의·원래 고정 평가 기준을 보존한다. 기술검토에서 발견된1,500ml/47,5g 및Unicode 부호 반례를 수리한 최종 소스로 평가했다. 이전 준비 source/초안은 폐기하지 않고 실행불가 기록으로 보존한다.

두500ml 상품의 출처 차이와 고정 정답의 보수적 한계는 C10계약에 따라 공개하되 catalog/정답 변경·SKU우선 특례·사후 판정 면제 없이 같은 게이트를 적용한다. C9의83/84 최소PASS·채택FAIL은 소급 변경하지 않는다.

- source `a7adafc0381e9ad069030b1cd13b181790763e89`, PR21 CI35678079901/35678073862 SUCCESS 및 mergeCI35678227688 PASS 통보. Production `dpl_64GFUovXy4nSD8xgNVxhJDQoWy6a`, 불변URL `https://wanna-21x18bnmi-beatrain-4635s-projects.vercel.app`, READY/target production/exact source 확인.
- 최종 context v20 SHA `6fffa1419a57a7c12e5b641251a0cec741e31dccad0369fee447f21533ba3e31` ACK76. source35/runtime50 현재 및 exact git 바이트 전수 비교, runtime hash `c66d01832a9f86a63d86ff4ab0ed616cb46f267d74ecb8a2cc0018d0c041cdec`. 종료 source35 불변.
- model `gpt-4.1-mini-2025-04-14`, prompt `customer-size-grounded-v10`, catalog248 hash `f2696abe92521e3ff8f9ab43cb36a1d297a6fd23d272e239605b49fab4343b1e`, 공개 SQL 업무state hash `d1a0845a4f45f44af9698963c700e9dfa24d13bb3a4b8b729b9b15e8a15278e1` 불변.
- dev config `2e48c86d260fe48e696beb298be83a0bc47b1c8d78501cc3e920d0fb4ef07f73`, 불변 proof `4fb7ddfa2e3b14c5bc5f9063e774583fd1118df238cd8db0fb0723fc4a01ca68`.
- dataset `0d394d463679189b082390219e74725e7a310f5173a5613d0bd87b5af85d26c7`, run `21241914-95d4-4bab-a293-8b975876de72`, fingerprint `1da8d818892f0665c1b2a10883e68a9a65dd40412712321d849037062cac65c7`.

PLAN_VALID30/34/648 뒤 명시GO로 최초1회 실행했다. 첫 정규 호출 HTTP200/provider true/input3512/output124/$0.0016032에서 실제 모델·형식·envelope를 확인했다. 별도 smoke0, 첫 호출도 정규 분모/비용에 포함했다.

## 동일 표본과 비용

고객 명확11/11·불확실7/7, 경영주 명확9/9·불확실3/3,18범주 전부 통과했다.

| 비교 | 이전 통과 | 개선 | 회귀 |
|---|---:|---:|---:|
| B0 |17/30|13|0|
| C1 |22/30|8|0|
| C2 |25/30|5|0|
| C3 |29/30|1|0|
| C4 |30/30|0|0|
| C5 |30/30|0|0|
| C6 |29/30|1|0|
| C7 |30/30|0|0|
| C8 |30/30|0|0|
| C9 |30/30|0|0|

34turn/34attempt,실패0·retry0·이번 usage unknown0·provider unknown0·pending0·stop null. 토큰439,169,추정비용$0.1804604,최대attempt $0.0065048/input15298/output275. P50 2798/P95 5681ms로 B0 P95 4483ms보다 느리며 시간 개선을 주장하지 않는다.

종료 upper1510/$9.4720305 = known1460/$6.9220305 + prior50/$2.50 + 이전 unknown usage$.05. prior는 실측이 아니며 비용은 계정 청구액과 다르다. dev후속648/$6.804·현재stage 남은turn×3·총2400/$20을 유지했다. 미래NL turn당 필수1회+선택retry여유1회로 예약했지만 실제 현재단계 retry상한3은 불변이며, 이후 진입 시 부족하면 STOP한다. 모든단계 최대retry 완주를 보장하지 않는다.

## 후속과 보존

원본 private `n13-c10-dev30`, 분석 `n13-c10-dev30-analysis`, driver로그/모든준비초안 보존. candidate-report SHA `590de25a400ac891d73ce32fb973ca4e61a36ee13da6b4710b78edeafd96e6ef`. 이 분석기의 자체 실행을 독립 평가 장치 검증으로 세지 않는다. 보호 원문 접근0·정답/분모/기준 수정0·출력 보정0·분석 재호출0.

원래dev 선행 기준 통과 뒤 조건부GO에 따라 validation config `0b36f1d804be4da87cd4940f6cdc80420d6afac14af4bb74bb10b9e65fde8bb6`로 첫84/92를 시작했다. 두 번째는 첫 반복 최소/불완전/mandatory/B0 및 C5 핵심·필수정상 회귀 기준을 통과할 때만 같은config/새run으로 실행한다. 두validation 후속464/$4.872를 고정한다. 신규 holdout은 freeze와 별도GO 전 실행하지 않으며 Production 배포는 최종 제품 완료가 아니다.
