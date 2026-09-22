# N08 C7 고객 추가 후보 공개 dev30 독립 평가

판정: **고정 선별 dev30 PASS / validation 진행 근거 충족 / best 또는 최종 제품 PASS 아님**. 30/30 통과, incomplete0·mandatory0, B0 및 C1~6 대비 정상 회귀0이다. `nl_minimum_pass=true`는 선택 표본의 판정이며 `stage_ready=false`이므로 전체 dev·validation·holdout 또는 최종 제품 품질을 대신하지 않는다. 별도 발견된 경영주 UI 조건 전달 P1도 이번 API 평가로 해소되지 않는다.

## 권한·목적·결속

D47 사용자 직접 승인에 따라 고객7/경영주6·총13의 고객 전용 추가 후보 한 번을 평가했다. 정상 상품의 명확·별칭·오타·모호·정정/대체 흐름을 유지하면서, 없는 고유상품과 대체 거절을 다른 실존 상품의 exact 후보로 바꾸지 않는 목적이다. 경영주 동작·공통 모델/검색/catalog·거래 도메인과 동의·48시간은 변경하지 않았다. 과거 후보 실패와 비용을 새 결과로 소급 대체하지 않는다.

- exact source `63614f9663a607373e0c7e9d43cb7e4616406b34`, Preview `dpl_3LzAGaofVNX7DSMUQ1E7KwKe1WH8`, URL `https://wanna-hznkak3p7-beatrain-4635s-projects.vercel.app`, READY/target null. source32개를 현재 파일 및 exact git commit과 각각 대조했고 runtime47 hash `2f296cacd8bdff4dca3286645b51aaae74f2318787c98aa1b51f3d2db6c5d94f`를 확인했다.
- C6 대비 source32 중 변경은 `src/server/prompts.ts` 한 파일이며 SHA `02334ef1e86a4707db47280e607194ccde0de91b817b480c2b5672db4f7d1be4`다. 고객 prompt와 version 변경의 기술 독립 검토는 research의 별도 증거이며 본 평가와 구분한다.
- config SHA `fbda5a765b86a3f095fcfd7c5e968834e4f1aa95f645b5bb58155d878f1aab37`, immutable proof SHA `44a51893ec7a7f1b893958b01e57f7c162a145b8cb89d85aea31583290e01770`. 독립 PLAN_VALID30/34/future984 확인 후 명시 GO로 한 번 실행했다.
- 최종 v16 context SHA `a9048d25ecce920ba8d9e2c38d9fc262381abf10c5612d1b02d64a6b00111bc6` ACK, 입력59개 해시 일치. 초기 준비 context의 작성 중 prompt 불일치는 최종 동결 후 재검증으로 닫았고 초기 값을 실제 결속으로 사용하지 않았다.
- 실제 model `gpt-4.1-mini-2025-04-14`, prompt `customer-identity-v7`, catalog248 hash `f2696abe92521e3ff8f9ab43cb36a1d297a6fd23d272e239605b49fab4343b1e`, SQL 합성 업무 state hash `d1a0845a4f45f44af9698963c700e9dfa24d13bb3a4b8b729b9b15e8a15278e1`. 반환 model/version/envelope는 실행기 검사를 거쳤다.
- 원래 C1 이전 고정 dev30/34 dataset `0d394d463679189b082390219e74725e7a310f5173a5613d0bd87b5af85d26c7`. run_id `6bc31f35-f333-4cd6-b9db-7e10114e04f8`, fingerprint `ab901cec16dab73e7faabd0624cbce976bba671088bfc3531bc4228045f31d5c`.
- private 원본 `n08-c7-dev30`, 채점/비교 `n08-c7-dev30-analysis`, 실행 로그 `n08-c7-dev30-driver.log` 보존. 평가 분석 중 재호출0·보호 원문 접근0. 실행 종료 후 source32 불변을 다시 확인했다.

## 동일 표본 paired 비교

| 지표 | B0 | C1 | C2 | C3 | C4 | C5 | C6 | C7 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 통과/전체 |17/30|22/30|25/30|29/30|30/30|30/30|29/30|30/30|
| 미완료 |3|6|3|0|0|0|0|0|
| mandatory |0|0|0|0|0|0|0|0|
| 실제 호출 |34|33|34|34|34|34|34|34|
| P50(ms) |2337|3138|2720|2838|2368|2173|3034|3176|
| P95(ms) |4483|15560|36624|5024|5384|5766|5747|6237|
| C7 개선 |13|8|5|1|0|0|1|—|
| C7 회귀 |0|0|0|0|0|0|0|—|

고객 명확11/11·불확실7/7, 경영주 명확9/9·불확실3/3, 표본의18범주 모두 통과했다. 공개 `C05-dev-002`의 C6 실패는 이번 C7 실행에서 `unidentified`, 빈 후보, 카탈로그에 없다는 설명으로 통과했다. 이전 C6의 잘못된 exact 추천 원본은 그대로 남긴다. 고객의 다른 정상 경로를 모두 거절한 결과가 아니며 같은 선택 표본의 명확 사례도 전부 통과했다.

작은 반복 노출 표본의 단일 실행이므로 가설의 보편적 정확성이나 변동성 개선을 확정하지 않는다. C7 P95는 B0/C3~6보다 높으며 UX 시간 개선으로 주장하지 않는다. 이전 C4/C5의 validation/holdout 실패를 이번 dev 통과로 덮거나 두 validation 반복을 생략하지 않는다.

## 사용량·예약·범위 밖 실패

34발화 모두34attempt에 완료, retry0·usage unknown0·provider unknown0·pending false·stop null. 토큰396,718, 알려진 추정 비용$0.1634884, 최대 attempt$0.0056828, 최대 input13027/output337이다. 이는 API usage 기반 추정이며 청구 확정액이 아니다.

종료 장부 upper1132calls / known1082 / provider unknown0, 알려진 비용$4.9737925 + prior 계획$2.50 + 이전 validation unknown usage$0.05 = upper$7.5237925다. prior50은 과거 실측이 아니다. 실행 내내 미래984calls/$10.332·다음unknown$.05·총2400calls/$20 상한을 유지했다. 후속 validation은 별도 사전 config/GO로만 진행하며 동일 config의 보수적 중복 예약과 STOP을 임의 완화하지 않는다.

root는 별도 정책 감사에서 경영주 UI adapter가 보류 SKU의 maxQuantity를 누락해 지연 후 수량 상한을 넘길 수 있는 P1을 재현했다고 통보했다. 이번 평가는 원래 SQL 업무 state와 모델 API의 해석을 검증하며 그 UI→거래 경로를 실행하지 않았다. 따라서 P1은 미해결 최종 제품 블로커로 유지하고, 후속 수정·도메인/브라우저 독립 검증과 최종 배포 source 결속을 별도로 요구한다. 이번 고정 소스의 평가 원본을 나중에 고친 UI의 결과로 재표기하지 않는다.

## 다음 조건

양 역할 고정 validation84/92를 동일 설정으로 두 번 각각 최소기준/mandatory/정상 회귀로 판정해야 한다. 별도 GO 전 자동 실행0이다. 이를 통과해 최종 동결한 뒤 이미 데이터 검토 PASS로 동결된 신규 보호84 최초 한 번, ADR007 UX v3, 현재 후보 두 역할 QA·정책/운영 감사·G5/G6가 남는다. 원래 C5 보호 실패·은퇴셋 재호출 금지와 D47 추가 자동 후보/평가 반복 금지를 유지한다.

평가자는 C7 앱 구현자가 아니며 본인 작성 scorer/runner 자체를 독립 검증으로 세지 않는다. 장치의 별도 research/builder 검토와 앱 평가의 독립성을 구분한다. 정답·사례·분모·소스·예산설정 변경0, 모델 출력 사후 교체0, 실패 삭제0이며 작업 공간과 로그를 보존한다.
