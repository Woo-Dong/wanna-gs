# C7 고객 전용 최종 추가 후보 계약

D47 사용자 직접 승인. C6 실패를 보존하며 고객7/경영주6·총13 한정이다. 고객의 미등록 고유상품과 대체 거절을 다른 상품으로 확정하지 않되 정상 명확/별칭/오타/속성·모호/후속정정·대체허용 흐름은 유지한다(CORE02/03/11/17/18/21/25).

- builder 단일 작성: src/server/prompts.ts의 CUSTOMER_PROMPT와 PROMPT_VERSION, 필요한 tests/server/customer-c7.test.ts 및 자체 검토. 고객 instruction 한 요인 후보를 우선한다. 고객 confirm은 불확실 조건을 가진 같은 요청 후보이고 다른 상품 대체와 구분해야 한다.
- 연구 검토자 research: 별도 fixture/SDK mock·동일 merchant instruction/payload/schema 불변 및 정상 예외 검토, 실제 성능과 구분.
- root: D47/공통 context·게이트·config/Git/CI/Preview. schema·catalog·공통모델·packing/retrieval·merchant 동작·도메인 수정0. 필요한 새 변경이 범위를 벗어나면 구현하지 않는다.
- method_auditor: 원래 고정 dev30/34 → 동일 validation84/92 두 반복 → candidate freeze 후 이미 독립 승인·동결된 새 holdout84/92 최초1회. 단계별 선행PASS와 budget 검증 뒤 별도 GO로 실행. 정답/원문/공개split/scorer 변경0.

특정 테스트 문구·고유명/정답을 prompt에 넣지 않는다. 출력 정답 덮어쓰기·과도한 거절·동의 없는 대체 금지. 원래95/90·mandatory0·정상회귀0, B0 paired2개 이상 개선과 C5 대응repeat 핵심/필수정상 회귀0 유지. merchant 평가 분모를 줄이지 않는다. C6/C5/이전 실패와 비용을 모두 보존한다.

$20/2400 단일 장부와 prior50/unknown·후속 예약/STOP 불변. 추가 dev34 계획(최대102attempt), 후속984예약. 최악중복예약은 완주를 보장하지 않으며 예약 부족은 STOP이다. 새 후보가 필수 단계에서 실패하면 추가 후보·같은 평가 재실행을 자동 시작하지 않는다. 통과 시 고정 UX v3·현재 후보 두 역할 QA·두 관점 정책/운영 감사·G5·main/CI·Production READY·익명 제출 URL G6가 남는다.

기술시험 PASS는 실제 모델 PASS가 아니다. 소스·평가 설정은 exact commit/Preview·hash로 결속하며 private 키와 보호 원문은 공개하지 않는다. 사용자 요청에 따라 모든 작업 공간과 실행/실패 로그를 유지한다.
