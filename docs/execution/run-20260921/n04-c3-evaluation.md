# N04 C3 공개 dev30 독립 평가

판정: **측정 완료 / 현재 best 승격 불가 / validation 보류 권고**. 응답 불완료는 없어졌고 동일 표본에서 29/30을 맞혔으나 경영주 명확 지시 8/9로 최소95%에 미달한다. 특정 상품 제외를 상품군 전체 제외로 확장한 오류를 정상으로 바꾸지 않는다. 선별 dev30 결과는 full dev252나 validation84의 통과가 아니다.

## 동결과 실행

- Preview `dpl_EK3hT5PniMZihubk9Z3csF7VUxGx`, `https://wanna-krv43ok6h-beatrain-4635s-projects.vercel.app`, target null/READY. exact source `55f92fe107694d0e570135362321d35d47131343`의 28개 결속 파일을 root `6e580c5ee4622810847ff3b1d49ad3000dae9162`와 바이트 대조해 동일 확인.
- model `gpt-4.1-mini-2025-04-14`, prompt `packed-refs-v4`, catalog248 SHA `f2696abe92521e3ff8f9ab43cb36a1d297a6fd23d272e239605b49fab4343b1e`.
- config `n04-c3-config.json` SHA `cab463f9ef1fb699a1390519e1939a58546a79dc4032ea15708de25bfc44798a`; 불변 READY proof SHA `8536da33bbb8024b090b8be5dc399823174c987ccdf417246d6997b80f52dcfd`.
- context-v9 SHA `39ab8976cced9628e0df3cf5fd44fbd435ad16717445347fb8c94d97455e3fa8`를 읽었다. 원본37파일 중 root INDEX만 실행상태·ADR006 링크 후속 갱신으로 달랐다. 해당 diff를 별도 ACK했고 모델/제품 정책 변경이 아님을 확인했다. 원 manifest를 수정하지 않았다.
- C1 전에 고정한 같은30개/34발화, dataset SHA `0d394d463679189b082390219e74725e7a310f5173a5613d0bd87b5af85d26c7`. PLAN_VALID 후 명시 GO 범위만 실행했다. validation/holdout 호출0, holdout 본문 접근0.
- run_id `eee7ecd2-f8e3-4382-96d1-41879441972f`, fingerprint `455d82eae4fd2934d079765b88ce31a68fdbca34c8a51b31219e1c948a3bfb01`. private `n04-c3-dev30` 원본과 `n04-c3-dev30-analysis` 채점·실패·paired 비교를 보존했다.

실행기는 각 정상 envelope의 반환 model/mode/prompt/catalog를 동결 config와 정확 비교한다. 첫 실제 응답부터 전부 이 검사를 통과했다. 최초 input2377/output112, 추정비용$0.00113이었다. 전체 HTTP envelope 전문을 따로 저장한 것은 아니며, 검증 후 observation과 실제 result·usage를 남기는 기존 실행기 계약이다. API 자체 source attestation은 없고 exact immutable deployment 증거로 결속했다.

## 같은30개 저장 관측 비교

| 지표 | B0 | C1 | C2 | C3 |
|---|---:|---:|---:|---:|
| 통과/전체 |17/30|22/30|25/30|29/30|
| 응답 미완료 |3|6|3|0|
| mandatory 오류 |0|0|0|0|
| 실제 호출 |34|33|34|34|
| P50(ms) |2337|3138|2720|2838|
| P95(ms) |4483|15560|36624|5024|

B0 대비 개선12/회귀0, C1 대비 개선8/회귀1, C2 대비 개선5/회귀1이다. C1/C2 대비 회귀는 모두 M03-dev-002다. 과거 관측은 저장본만 읽었고 재호출하지 않았다. 모델과 prompt가 함께 바뀐 제한된 복합 후보이므로 모델 교체만의 인과 효과를 주장하지 않는다. 서로 다른 설정의 실행을 best 동일 설정 validation 반복으로 세지 않는다.

고객 명확11/11·불확실7/7, 경영주 명확8/9·불확실3/3이다. 경영주 명확 정확도88.89%는95% 미달이다. stage_ready 및 nl_minimum_pass는 false이고 표본 전체96.67%로 역할별 실패를 상쇄하지 않는다.

## 유일 실패와 목적 보존

M03-dev-002의 공개 합성 발화는 앞으로의 자동발주 정책에서 특정 SKU를 제외하고 예산12,000원으로 제한하는 지시다. 실제 응답은 intent modify/scope policy, budgetLimitKrw12000, excludeProductIds에 올바른 `DEMO-10644269FA7E`를 반환했지만 **excludeCategories에 `간편조리·냉동식`을 추가**했다. 명시하지 않은 상품군 전체 제외는 구매 수요를 과도하게 차단하므로 command_composite_mismatch다. HTTP200·strictschema 성공과 의미 정확도를 구분한다.

해당 호출 input12472/output101, latency4966ms, 추정비용$0.0051504. 실제 모델이 이 오류를 반환한 기록을 유지하며, 평가 정답을 넓히거나 앱 확인이 뒤에 있다는 이유로 성공 처리하지 않았다. 고객 동의·경영주 명시 범위·정상 성공·업무 부담 기준을 유지한다. C2의 불필요한 최신 제안 확인과 범위 밖 입력/미완료 사례는 이번 표본에서 정상화됐지만 그 개선이 새 범위 확장 오류를 면제하지 않는다.

## 호출·예산·다음 단계

30개 모두 기록, 계획34발화 모두 실행, 재시도0·usage unknown0·pending false·stop null이다. 389,491 tokens, 사용량 기반 추정비용 **$0.1604032**, 최대 attempt **$0.005542**, 최대 input12691이다. 공급자 청구 확정 금액이 아니다. goal 장부는 upper535calls/known485/unknown0, 측정비용$2.2035897+prior계획$2.50=upper$4.7035897. prior50/$2.50은 과거 실측으로 바꾸지 않는다.

실행 내내 미래 필수960회/$10.08, unknown$.05, 전체2400회/$15 중단을 유지했다. 별도 validation684회/$7.182 계획은 아직 실행 config나 GO가 아니며 이번에 호출하지 않았다. 원본 B0/C1/C2 config와 실패 기록은 불변이다.

현재 후보는 명확 경영주 표본의 최소 기준 미달이므로 validation 통과를 찾아 실행하거나 best로 승격하지 않는 것이 독립 권고다. 이후 조정자는 ADR003의 후보 한도·연속 non-improving 종료 규칙과 필수 복구 경계를 먼저 판단해야 한다. 후보 이름/모델 변경으로 한도를 재시작하거나 사례를 제거하지 않는다. 기존 UX 비교 NOT_READY 및 holdout/G5/G6 미완료는 그대로이며 추가 실험 종료가 필수 품질 면제는 아니다.
