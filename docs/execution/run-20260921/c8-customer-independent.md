# C8 고객 생성 응답 계약 독립 기술 검토

판정: **C8-TECH PASS, 중대한 미해결 반례 0**. 실제 모델 품질·최종 고객 UX·G5/G6 판정은 아니다. 검토자 research는 이 C8 서버 코드 작성에 참여하지 않았다. 과거 고객 UI 작성 경력이 있으므로 이 검토를 독립 고객 UI QA로 계산하지 않는다.

D48 사용자 위임과 c8-customer-contract/card/CORE02·03·11·17·18·21·25 및 docs09/14를 읽었다. source는 builder commit `e0b078b335df1dc939869af2676a90806d5f7138`에서 root에 통합된 서버/테스트 바이트와 같다. 최종 context `context-n11-v18.json` SHA `b2d55452e0dd9b4efe9f72082f7e5c41618c486ecc4e710de640de3a3217644f`의 **68개 입력 해시**를 직접 대조했다. aggregate fingerprint는 `d12d41220c759bd6482c6eefab714b89ad23226e56dd34b78279b7e881ce1079`다.

## 목적 보존과 직접 검사

수정 전 기존 schema/verify를 독립 실행해 show_candidates의 질문 비null·빈 후보·alternative만 있는 후보 3형태가 생성 schema에서는 허용되고 서버에서 거절되는 차이를 재현했다. C7 provider 원문은 없으므로 실제 C7 실패가 어느 형태였는지는 여전히 미확정이다.

새 wire의 show는 exact/confirm primary 한 개를 필수로 하고 추가 후보 최대5개·question=null을 제한한다. clarify는 유효 질문과 후보를 유지하며 질문 한도2 뒤에는 분기를 제거한다. unidentified는 alternative 또는 빈 목록·question=null을 유지한다. 외부 실행 요청에 대한 기존 범위 certificate는 질문 한도와 결합해 후보0을 유지한다. primary는 구매 선택/동의가 아니라 고객이 확인할 후보다.

독립 작성한 12개 검사 그룹에서 위 3반례 차단과 정상 exact/unknown조건 confirm/복수 primary+alternative/총6후보/clarify후보/미식별대체·빈목록을 확인했다. 후보 순서·근거·차이·unknown조건·reason·question·confirmationRequired가 wire→canonical→실제 SKU 변환에서 보존된다. 불명 ID·범위 밖 ID·잘못된 exact unknown·위조 confirmation·추가 assessment id·7후보·빈/공백/과대 질문은 거절된다. 중복 ID/과대 설명처럼 기존 verifier가 담당하는 오류는 그대로 실패하며 후보 삭제나 질문 삭제로 성공 처리하지 않는다. verifyCustomer 함수 본문 바이트는 수정 전과 동일하다.

실제 설치된 OpenAI SDK 경로를 가짜 키와 global fetch mock으로 호출했다. 고객 SDK mock5회에서 object root/nested anyOf/strict/store=false/3200 및 full248 카탈로그·enum 합계996을 직접 확인했다. API의 정상 응답은 기존 공개 candidates 계약이고 새 decision 구조가 UI에 누출되지 않는다. schema 오류의 known usage, incomplete의 known usage, usage 불명의 null 및 providerCalled=true가 보존됐다. 이는 실제 HTTP/API 지원이나 모델 정확도 증거가 아니다.

별도 경영주 SDK mock2회에서 정상 예산 변경과 stale clarify-only를 확인했다. 경영주 literal과 normal/stale/SKU-only 생성 JSONschema는 수정 전과 정확히 같다. 실제 payload의 full248·현재제약·SKU packing·원문도 유지된다. provider/model-profile/packing/retrieval/catalog/공통 계약·거래 도메인·고객/경영주 UI는 사전 바이트 지문과 일치한다. 공동 promptVersion 메타데이터만 C8 버전으로 갱신되며 경영주 instruction 내용은 불변이다.

## 실행 증거

- 동결 worktree의 서버 전체 **48/48 PASS**, fail/skip/cancel0를 독립 실행했다. 구현자가 실행한 48개를 독립 결과로 대체 인용하지 않았다.
- research 별도 **12개 반례/정상/SDK 검사 그룹 PASS**, 내부 고객 SDK mock5회. 별도 경영주 SDK 정상·stale **2개 PASS**. 이 mock 호출 수는 모델 사용량 장부나 제품 eval 분모가 아니다.
- 새 wire fixture helper는 의도적 invalid값도 그대로 감싸고, 기존 네 테스트 파일의 기대 정답을 완화하지 않고 새 생성 형식만 반영하는 것을 diff로 확인했다.
- root와 builder commit의 production/test diff0, 최종 source4 지문 및 context68/aggregate 지문 직접 대조.

private 증거: `artifacts/private/run-20260921/c8-independent/`의 baseline.mts/json/binding, contract-probes.mts/contract-results.json, merchant-sdk-delta.mts/result, server-48.log, context-ack.json. 소스4 SHA: customer-wire `24069afb53af5e5478848e294409d5a8a7b6d329f63b9d0475ed424eed2bbaca`; schemas `195292f9d7e5fd0cbd2b8cfbe00ba4b31242428af74caf72c961927bae104756`; assistant `94d87a177b6a02960d280dcc0baef19bf2db3dbd03856a90a1af380660376438`; prompts `b263e389554d15e42f2d7cf23f951d88eae2b86ddddaff1f60d4ae4e7a4a36e1`.

## 남는 한계

실제 모델·HTTP·배포·브라우저·공유장부·보호 holdout 본문/생성기 접근0. 명확/별칭/오타/모호/정정이 실제 한국어에서 잘 선택되는지는 고정 live dev/validation 두 반복 및 최종 동결된 새 holdout에서 검증해야 한다. enum996은 현재248 기준이며 카탈로그 확장 시 기존 한도 검사를 다시 통과해야 한다. SDK 직렬화 성공을 원격 모델의 schema 수용/품질로 주장하지 않는다.

C5/C6/C7 실패와 분모·비용·은퇴 holdout은 보존하며 $20/2400·예약/STOP·95/90·mandatory0/incomplete0·정상 회귀 기준을 바꾸지 않았다. ADR007 실제 UX, 현재 후보 두 역할 QA·미완료 정책 감사·G5·main/Production·익명 제출 G6는 별도 필수다. 이 기술 리뷰의 unsigned JSON은 검토자 신원의 암호학적 증명이 아니다.
