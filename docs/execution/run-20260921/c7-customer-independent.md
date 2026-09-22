# C7 고객 prompt 독립 기술 검토

판정: **C7-TECH PASS**, 필수 미해결0. 구현자 preflight_builder/root, 독립 검토 research. 실제 모델 품질·최종 평가·고객 브라우저 QA·G5/G6 PASS가 아니다.

D47 사용자 승인 및 c7-customer-contract를 직접 확인했다. 고객7/경영주6·총13 하나의 고객 추가 슬롯, $20/2400/이전 실패/고정 평가/추가실패 자동확장0을 유지한다. 초기 v16 SHA c086627dee6c087770cfed225ea3c0110d41346b9289207907586ac79b196c9e ACK 후 최종 v16 SHA `a9048d25ecce920ba8d9e2c38d9fc262381abf10c5612d1b02d64a6b00111bc6`의59입력 전부 현재 해시와 다시 대조했다.

## 범위와 의미 검토

최종 prompts.ts SHA `02334ef1e86a4707db47280e607194ccde0de91b817b480c2b5672db4f7d1be4`. 변경은 CUSTOMER_PROMPT의 동일상품 식별→조건 확인→대체 분리 문단과 exact 정의·명시 대체거절·후속 정정 문구, PROMPT_VERSION=customer-identity-v7뿐이다. 특정 case/정답/고유상품명 하드코딩이나 후단 출력 치환이 없다. 새 prompt를 추가한 뒤 다음 인접 정상/실패 경로의 의미가 충돌하지 않는지 직접 읽어 검토했다.

| 경로 | 보존 판단 |
|---|---|
| 실제 X를 찾되 대체는 거절 | X의 식별은 막지 않는다고 명시되어 전후보 일괄거절이 아니다 |
| 별칭·오타·속성 검색 | literal equality 필수 아님, 충분히 식별적인 관측 속성을 허용한다 |
| broad 설명·모호한 맛/크기 | 기존 질문 규칙을 유지하며 넓은 표현만으로 미등록을 단정하지 않는다 |
| 같은 상품의 알레르기/성분 불명 | confirm+unknownConditions를 유지하고 적합성 확정은 금지한다 |
| 다른 이름의 대체 SKU | 공통 분류/맛만으로 exact/confirm에 넣지 않으며 대체허용 시 기존 alternative·차이 표시를 유지한다 |
| 미식별 고유상품+대체거절 | supplied catalog에서 미식별임을 설명하고 다른 후보를 넣지 않는다. 상품 자체의 비실재를 단정하지 않는다 |
| 후속 명시 정정 | 최신 명시 상품이 이전 정체성을 대체하며 앞의 거절을 새 요청에 부당하게 전가하지 않는다 |

위 표는 prompt 계약의 독립 의미 검토이며 실제 모델의 경로별 성공률 표가 아니다. 문구가 길어져 지연/입력비용이나 과도한 보류가 늘 가능성은 이후 원래 dev/validation으로 측정해야 한다. C6의 단 한 회귀가 특정 코드 원인을 증명한다고 주장하지 않는다.

## 경영주/공통 불변과 실제 기술 실행

C6 수정 전에 보존한 prechange-binding과 현재 source를 비교했다. provider/model-profile/packing/retrieval/catalog/schema/assistant/customer-boundary/merchant-grounding/domain engine/domain contract/product data 총12개 바이트 불변. MERCHANT_PROMPT export의 동일 범위 및 실행된 literal 값도 C6와 동일하다. runtime literal SHA `f15910056c822eb7480fa86214f773de853c7d3c6479164fc90713a1958085f9`. 기존 별칭·조건·거래·동의·48시간 코드는 바꾸지 않았다.

- Node22+tsx server unit41 직접 실행 PASS,0fail/skip/cancel. fixture와 SDK mock이며 실제 모델0.
- 별도 SDK mock2: 실제 interpret→liveProvider→OpenAI Responses SDK payload를 가짜키/global fetch 완전 모의로 검사했다. 경영주 policy 초안의 instructions는 C6 literal과 완전동일, 정상 scope/조건 결과 유지. 고객 known product+대체거절 입력은 원문 그대로 전달되고 변경 없는 schema/packing을 통과해 실제 SKU·confirmationRequired=true로 복원됐다.
- 두 요청 모두 모델 snapshot/strict/storefalse/no reasoning/3200 옵션 불변. promptVersion은 공유 메타데이터라 두 응답에서 새 태그로 표시되지만 경영주 instruction/payload생성/schema의 동작 변경은 없다. 최종 실행 config는 새 태그를 사용해야 한다.
- 이 모의 응답은 올바른 응답을 주입한 기술 검사다. 모델이 실제로 새 지시를 따랐다는 증거로 세지 않는다. 실제 네트워크/브라우저/goal 장부/보호 holdout·생성기 접근0.

private c7-independent/prechange-binding.json·sdk-delta.mts/result·server-unit.log에 증거 보존. contracts CLI PASS, aggregate fingerprint `15e1ede83a81eb3e21fbbf2a5a7572f58344d3ab6be3ebb0d9185d37ae019c97` 직접 재계산 일치. 기존 server 수집 glob에 해당 회귀가 포함된다. 새 문구를 그대로 되풀이하는 mirror test는 만들지 않았다.

## 후속 및 한계

정해진 dev 선별→동일 양 역할 validation 두 번→이미 동결된 미실행 새 holdout 최초1회가 필요하다. 역할별95/90·mandatory0·정상회귀0, B0 개선과 C5 대응repeat 회귀, 옛 holdout no-replay/기존 실패·장부를 유지한다. 필수 단계 미달 시 자동 재실험/다음 후보로 진행하지 않는다. 통과해도 UX v3/current 두 역할 실제 QA/G5/G6가 남는다.

quality/reviews/c7-tech.json은 위 기술 범위와 목적 보존의 독립 검토다. 고객 UI 작성자인 research의 검토를 독립 고객 역할 QA로 세지 않는다. unsigned JSON은 신원의 암호학적 증명이 아니다.
