**후속 사용자 결정 D48(2026-09-22):** 사용자가 후보 실패 시 자동 추가 금지를 포함한 잔여 판단을 위임했다. 아래 미승인/후속자동금지는 당시 제안 이력이며 현재 실행은 [C8 계약](c8-customer-contract.md)을 따른다. 품질·실패·비용 경계는 유지한다.

# C7 응답 계약 실패의 고객 전용 복구 제안

상태: 2026-09-22 재개 진단. **사용자 미승인 제안이며 후보 구현·새 모델 호출은 0**이다. 기존 D47의 고객 추가 한 번은 C7에서 소진됐다. 이 문서는 후보 한도나 제품 기준을 변경하지 않는다.

## 확인한 사실과 한계

C7 전체 validation01은83/84이며 CANDIDATE_ACTION_CONTRACT 한 건으로 incomplete0 조건을 충족하지 못했다. provider 원문이 없어 실제 오류 분기는 미확정이다. 현재 모델 생성 schema는 show_candidates의 question 비null·빈 후보·alternative만 있는 후보를 모두 허용하지만 verifyCustomer는 세 형태를 거절한다.

root가 실제 schema/verifyCustomer를 불러 수행한 합성 로컬 probe에서 세 불일치가 모두 재현됐다. 정상 show/clarify는 양쪽에서 허용됐다. private `c7-resume-contract-probe.mts/.json`에 보존했다. 이는 C7 원응답 재현이나 실제 모델 검증이 아니다. 독립 preflight_builder의 읽기 검토도 구조적 차이를 확인했고, 기존 prompt에는 이미 question=null·primary≥1 지시가 있음을 확인했다. 해당 검토자는 probe를 직접 실행하지 않았다.

## 요청할 한정 범위

고객 후보 **C8 하나만** 추가하는 제안이다(고객8/경영주6, 총14). 생성 단계에서 고객 행동별 구조를 제한한다. show_candidates는 필수 exact/confirm 하나와 추가 후보 최대5개·question=null, ask_clarification은 유효 질문과 현재 질문 한도, unidentified는 primary 없음·question=null을 보장한다. 고객 내부 응답을 검증한 뒤 기존 고객 계약으로 무손실 변환하고 기존 verifyCustomer를 그대로 적용한다.

예상 수정 파일: 고객 wire helper 신규 파일, src/server/schemas.ts의 고객 분기, src/server/assistant.ts의 고객 응답 변환, src/server/prompts.ts의 고객 설명·버전 및 관련 서버 테스트. 공통 파일은 단일 작성자로 배정하며 경영주 literal/schema/payload·공통 provider/model/catalog/retrieval/packing·거래 도메인은 변경하지 않는다. 형식 변환으로 질문 삭제·후보 삭제·alternative의 primary 승격·가짜 SKU 생성·오류의 성공 치환을 하지 않는다. 원래 명확·별칭·오타·모호 다후보·조건 미확인 confirm·미식별·대체 허용/거절·후속 정정·동의 경계를 보존한다.

내부 형식은 provider가 지원하는 JSON Schema subset을 확인하고 SDK 직렬화와 실제 승인된 호출로 검증해야 한다. 현재 읽기/합성 probe만으로 API 형식 지원이나 품질 개선을 보장하지 않는다. 기존 C7 실패를 특정 필드 오류로 단정하거나 정답/사례 이름을 prompt에 하드코딩하지 않는다.

## 검증과 종료

구현자 자체 검사와 별도 독립 검증을 분리한다. 세 불일치·정상 단일/다후보·clarify·unidentified·질문 한도·외부요청 경계·ID/중복/unknownCondition·사용량/오류 보존 및 경영주 불변을 검사한다. 승인 후 기술검증/PR/CI/정확한 Preview를 거쳐 고정 dev30 → 같은 validation84 두 반복 → source 동결 후 신규 보호84 최초1회 → ADR007 UX·현재 두 역할 QA·최종 감사·G5 → main/Production·익명 제출URL G6 순서를 유지한다.

95/90·mandatory0·incomplete0·정상 회귀0·B0/C5 고정 비교·원래 분모를 유지한다. 과거 C5/C6/C7 실패와 은퇴 holdout 재호출 금지를 유지한다. 어느 필수 단계에서든 다시 실패하면 자동 후보 추가나 같은 평가 재실행 없이 종료한다. 기술 PASS는 실제 모델/UX/배포 PASS가 아니다.

## 비용 검토

method_auditor가 원래 공유 장부와 guard를 읽기 대조했다. 현재 upper1224회/$7.9577773, known1174회/$5.4077773, prior50/$2.50 및 과거 unknown usage$0.05, pending0을 유지한다.

추가 dev최대102와 필수 후속984를 예약하면 총2310/2400회다. 기존 attempt계획$0.0105에서 남은 전체 예약과 다음 unknown$0.05를 포함한 계획합계는$19.4107773이다. 이는 실제 청구의 최대값이나 완주 보장이 아니다. 동일 validation config의 보수적 미래708 예약까지 유지하면 최대 재시도 경로에서2586회/$22.3087773의 guard 요구가 생길 수 있으므로 기존 STOP이 우선한다. 장부 초기화·예약 축소·우회·새 크레딧 구매·자동 충전은 하지 않는다.

## 승인 경계

새 한 후보와 그 통과 후 원래 최종 검증 절차만 요청한다. 추가 승인이 필요한 이유는 스킬의 권고가 아니라 **사용자 D47의 ‘다시 실패하면 자동 추가하지 않는다’는 한도**다. 목표 재개 자체를 후보 한도 확대 승인으로 해석하지 않는다. 승인 전에는 제품 소스 수정·추가 평가·배포를 시작하지 않는다.
