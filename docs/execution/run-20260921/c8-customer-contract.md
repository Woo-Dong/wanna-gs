# C8 고객 생성 응답 계약 수리

D48 직접 사용자 위임. 고객이 정상 상품을 탐색·비교·확인하고 모호한 요청은 질문/후보로 해결하도록 유지하면서, 생성 schema가 서버에서 거절되는 action/question/primary 조합을 허용하는 차이를 수리한다. 실제 C7 원응답이 없어 어느 조건이 발생했는지는 미확정이고 합성 local probe3건은 구조적 가설 근거다.

- CORE02/03/11/17/18/21/25·AC01/02/03/24/26/28/29. D44/45의 한탭SQLite·서버OpenAI, 동의/48시간·거래 불변.
- 구현 preflight_builder: 격리 codex/c8-contract-impl, 고객 wire helper·schemas.ts 고객분기·assistant.ts 고객변환·prompts.ts 고객설명/version·관련 서버tests만. provider/model/catalog/retrieval/packing/merchant/domain 불변. wire를 검증 후 canonical로 무손실 변환하며 기존 verifyCustomer는 유지한다. 출력 오류 보정·ID/정답 하드코딩 금지.
- research 독립 서버검증: 생성 제약3종, 정상 단일/다후보·confirm·명확/오타/별칭·clarify·unidentified/대체·질문2회·외부scope·ID/중복·SDK형식/usage/error·merchant byte/schema/payload 불변. 독립 private probes 소유, 최종root context/fp ACK 후 report/review. 기존 고객UI작성경력과 C8 서버 독립성을 구분.
- root 단일작성: 사용자결정·작업/context/gates·Git/CI/Preview·통합. source/key/실행 증거 결속. 공유 문서/게이트를 builder가 수정하지 않는다.
- method_auditor 독립평가·단일비용장부: exactsource/CI/Preview 및 명시GO 후 dev30/34→validation84/92두반복→freeze→독립신규holdout84/92최초1. 보호 원문은 평가자만 접근. 이어서 ADR007 UX·독립양역할QA·최종정책/운영감사·G5·main/Production·익명제출G6.

선별 dev 원래30과 평가 정답/범주/분모/95·90/mandatory0/incomplete0/정상회귀0/B0 및 C5 고정비교 유지. C7 정상 사례 회귀도 공개한다. schema+wire설명은 한 생성계약 변경이며 prompt 의미정책 튜닝을 섞지 않는다. 형식의 반례/정상 검사를 모델 없는 단계에서 분리하고 실제 품질은 고정 live 평가로 판단한다.

API $20/2400, 현재 upper1224/$7.9577773·prior50/$2.50·unknown$.05·후속예약/STOP 유지. dev최대102+필수984 예약총2310회/$19.4107773 계획(다음unknown$.05포함). 기존 보수 중복예약으로 더 일찍 STOP할 수 있고 완주나 실제청구의 상한을 보장하지 않는다. D48은 후보 한도 판단을 위임했으므로 새 실패가 있으면 원인·새가설·독립검증·필수예약에 따라 조정자가 후속 복구를 결정한다. 무한 반복/기준완화/실패소거 금지.

가용4슬롯, 상속모델 사용·중요검증 high capability, 관리 depth1. 자체검사→독립검사→전체gate→PR/CI→Preview live 순으로 진행한다. 기술PASS를 live/G5/G6로 재사용하지 않으며 파일/원본/실패/작업공간을 보존한다.
