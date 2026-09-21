# N07 C6 공개 dev30 독립 평가

판정: **선별 dev30 FAIL / validation 진행 근거 미충족 / best 승격 불가**. 29/30 통과, incomplete0·mandatory0이지만 고객 불확실 6/7=85.71%로 90% 최소에 미달했다. B0와 C1~5 각각에서 통과했던 공개 미식별 사례1개가 회귀했다. 이 표본의 `nl_minimum_pass=false`, `stage_ready=false`이며 전체 dev·validation·새 holdout 또는 출시 품질을 통과했다고 주장하지 않는다.

## 결속과 목적 보존

고객이 원하는 상품을 정확히 확인하고, 모르는 상품은 보수적인 질문·미식별로 연결하며, 경영주의 명시한 수정 범위를 유지하는 목적을 평가했다. 고객 확인·동의, 경영주 승인·정책, 48시간·한 PC SQLite 계약은 변경하지 않았다. 카드와 C6 복구계획의 마지막 후보·원래 holdout 재호출 금지·B0 및 C5 비교 기준을 재확인했다.

- exact source `8397048e4b327db1433f2b1ea76c1e042a45adf4`, Preview `dpl_6nYrqPgj3Y9Rj161ZHQkPdLkN8Ro` / `https://wanna-bzrcj9uf8-beatrain-4635s-projects.vercel.app`, target null/READY. source_files32개를 현재 파일 및 exact Git commit과 각각 대조해 불일치0을 확인했다. runtime47 hash `8cb057d7fde489a2cf1586c70de5bce9c662bd9a03e947b6804556b15997b9e7`도 일치했다.
- config SHA `3f1bf45c2294c1bc28e551880cb40f363388fd50f4a6eb536df0308ef82c0b1b`, proof SHA `30d77b6fb93b1ce751439339ed91d2c507ec15c53ecf3e19800c1538629fe96a`. 독립 PLAN_VALID 30/34/future984 뒤 명시 GO로 한 번 실행했다.
- context v15 SHA `2be3757da9a1d1d35f47e77c314402854f87ca8220f22e95201f1000dfc5454b` ACK, 입력58개 현재 해시 모두 일치했다.
- 실제 모델 `gpt-4.1-mini-2025-04-14`, prompt `grounded-boundaries-v6`, prompt SHA `a55def5f4841ea2fb313bbeafbac0ae830df4794632bfc9837952b7298cd3b0d`, catalog248 SHA `f2696abe92521e3ff8f9ab43cb36a1d297a6fd23d272e239605b49fab4343b1e`, state SHA `d1a0845a4f45f44af9698963c700e9dfa24d13bb3a4b8b729b9b15e8a15278e1`. 실행기는 반환 envelope의 model/version을 검사했다.
- C1 이전 고정 dev30/34 dataset `0d394d463679189b082390219e74725e7a310f5173a5613d0bd87b5af85d26c7`. run_id `c03080fd-a2ba-45fa-b9e1-26ffb3133f21`, run fingerprint `e7499a29f50e502b7112dd4965b4bd5308267b4c205ba35597d6ee843d9702e1`.
- 원본은 private `n07-c6-dev30`, 전체 채점·실패·비교·장부 스냅샷은 `n07-c6-dev30-analysis`, 실행 로그는 `n07-c6-dev30-driver.log`에 보존했다. 분석 중 재호출0, 이 작업의 validation/holdout/UX 호출0·보호 원문 접근0이다.

## 동일 표본 비교

| 지표 | B0 | C1 | C2 | C3 | C4 | C5 | C6 |
|---|---:|---:|---:|---:|---:|---:|---:|
| 통과/전체 |17/30|22/30|25/30|29/30|30/30|30/30|29/30|
| 미완료 |3|6|3|0|0|0|0|
| mandatory |0|0|0|0|0|0|0|
| 실제 호출 |34|33|34|34|34|34|34|
| P50(ms) |2337|3138|2720|2838|2368|2173|3034|
| P95(ms) |4483|15560|36624|5024|5384|5766|5747|
| C6에서 개선 |13|8|5|1|0|0|—|
| C6에서 회귀 |1|1|1|1|1|1|—|

고객 명확11/11·불확실6/7, 경영주 명확9/9·불확실3/3이다. C05는1/2, 나머지17범주는 모두 통과했다. B0 대비 순개선12가 있어도 정상 회귀1 및 해당 역할 최소 미달이므로 채택 근거가 되지 않는다. 전체 통과율96.67%로 역할별 기준을 대체하지 않는다. B0 미완료3과 이전 후보 실패는 그대로 보존했다. 소규모 선택 표본의 지연 수치를 UX 조작·시간 개선이나 전체 품질로 일반화하지 않는다.

## 실패의 실제 근거

공개 `C05-dev-002`는 카탈로그에 없는 고유 상품명을 찾으며 다른 상품으로 바꾸지 말라는 요청이다. 허용 결과는 질문 또는 미식별이다. 실제 HTTP200/스키마 정상 응답은 다른 실존 SKU를 `exact` 후보로 표시했다. 응답 자체도 상품명이 일치하지 않는다는 evidence와 원래 상품이 카탈로그에 없다는 이유를 함께 담았으므로, 사용자 요청에 맞지 않는 후보 표시라는 의미 오류가 확인된다. 없는 SKU를 발명한 오류는 아니며 실제 확인·동의가 완료되거나 거래가 실행된 것은 아니다.

scorer의 원래 `wrong_action` 판정을 변경하지 않았다. 모델 출력·실패 분모·정답을 바꾸거나 오류를 재호출로 덮지 않았다. 직접 원인인 이 응답은 확인했지만 단 한 번의 확률적 결과로 특정 코드 분기가 원인이라고 확정하지 않는다. 같은 사례는 B0 및 C1~5 모두 통과했고, C6의 새로운 가설과 인접한 미식별 정상 기능의 회귀로 기록한다.

## 비용과 종료

34발화/34attempt, 재시도0·unknown usage0·unknown provider0·pending false·stop null이다. 토큰390,599, 알려진 추정 비용$0.1607252, 최대 attempt$0.0055132, 최대 input12826/output303이다. 실제 청구 확정값은 아니다.

종료 장부는 upper1098calls / known1048 / provider unknown0, 알려진 비용$4.8103041 + prior 계획$2.50 + 이전 validation의 unknown usage 예약$0.05 = upper$7.3603041이다. prior50은 과거 실측값이 아니다. 실행 내내 미래984calls/$10.332·다음 unknown$.05·총2400calls/$20 한도를 유지했다. 비용 여유는 품질 기준 면제나 추가 후보·재호출 권한이 아니다.

독립성은 root/builder 작성 C6 앱의 실제 평가에 해당한다. 평가자가 작성한 scorer/runner 자체를 독립 검증으로 세지 않으며 별도 research/builder 평가장치 검토를 구분한다. 공개 및 보호 평가 정답 변경0, 실행 중 앱·모델·prompt·데이터 변경0이다.

C6는 승인된 마지막 후보이며 선별 실패로 자동 validation·새 holdout·UX·C7을 시작하지 않는다. 기존 C5 final holdout FAIL, 새 보호셋 데이터 검토 PASS와 실제 평가 not_run, ADR007 UX v3 not_run, 최종 G5/G6 미완료를 함께 유지한다. 소스/세션/원본/보고서와 보호 파일은 보존한다.
