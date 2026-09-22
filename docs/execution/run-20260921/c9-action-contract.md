# C9 — 추가 후보 절제와 경영주 행동 계약 복구

상태: D48에 따른 구현 승인, 실제 평가 미실행. 기반 integration92cfb4bb. root통합/공통문서, preflight_builder구현, research독립기술검증, method_auditor독립live평가. CORE02/03/05/11/17/18/21/23/25와 기존 AC·ADR003 기준을 유지한다.

## 목적 보존

고객이 특정 상품을 명확히 말하면 해당SKU를 확인하고 요청까지 갈 수 있어야 한다. 모호하면 유용한 질문/후보를 보여주고, 대체품은 원상품과 구별해야 한다. 경영주의 정상 수정·되돌리기·정책 초안은 고객 동의나 발주 실행으로 오인하지 않고 기존 UI확인과 SQLite 거래 검증으로 이어져야 한다.

C8 dev30/30 PASS와 validation01 79/84 FAIL을 모두 보존한다. 고객C02 세 건 및 C06 이전턴은 정답 포함에도 불필요한 primary가 추가됐다. C06의500ml중복표기행은 catalog/oracle모호성 가능성도 함께 기록하며 점수·데이터를 수정하지 않는다. 경영주M04undo는502 OUTPUT_CONTRACT, 원응답이 없어 실제 위반 필드는 미확정이다. 생성 schema가 허용하지만 verifyMerchant가 거절하는 restore/clarify 조합은 합성 재현 가능한 별도 구조 간극이다.

## 수정 경계

- 고객 wire/schema는 유지. wire설명에서 additionalCandidates기본[]를 명시하고 실제 정체성/변형 모호함일 때 추가 primary를 허용한다. 기존 자발적 관련대안·모호다후보·count2/거절/알레르기확인 동작을 축소하지 않는다. SKU/평가문장 특례는 만들지 않는다.
- 경영주 생성형식 root decision의 modify/restore/clarify별 nestedunion. restore는 current scope·nullquestion·restorePrevious외default제약, clarify는nullscope·비어있는제약·질문, modify는현재제약·non-nullscope·nullquestion·restorePreviousfalse. stale는clarify만. 기존grounding과 이전제약 존재검사 유지. 변환은decision무손실언랩만.
- verifyCustomer/verifyMerchant 본문, provider/model/packing/retrieval/catalog/domain/UI/공통외부API는 유지한다. 새 merchantwire helper와 관련서버테스트/fixture만 추가한다. modifyempty 제약은 기존verify에 남기고 이 후보의 범위를 확대하지 않는다.

## 검증·중단

수정전생성accept/서버reject 반례보존→동일기대수리→정상수정/되돌리기/현재·미래/모순/stale/SKU-only/category/mixed 회귀→실제SDK mock·enum한도·기술게이트·독립검증→정확한배포/모델binding dev30→고정validation84두회→rootfreeze→새holdout84최초1→ADR007실제UX양arm/두역할QA→최종정책/G5/G6. 실제호출없이mock만으로품질PASS를발급하지 않는다. D49에따라후속배포target은production, 정확한불변deployment를평가에사용하며 제출alias는최종G6에서검증한다.

## 예산

공유장부 upper1350/$8.6217717, prior50/$2.50·기존unknownusage$.05 보존. 실제 필수 UX42+42=84, QA3+3/G6두호출=8과 고정NL두validation/holdout 분모를 유지한다. 이전계획의 미배정여유를 현재실행계획으로 재산정하되, 모든호출전실제장부/단계별예약을검사하고 $20/2400 또는 unknown/auth/pending이면STOP한다. 계산표·독립대조후설정을고정하며, 최악의재시도완주를보장한다고주장하지않는다.

### C9 사전 예약 확정

실제 고정 harness의 UX42+42=84, 고객QA3/경영주QA3/G6두호출=8 및 추가복구여유4를 반영한다. 이전UX96/G5G660은 미배정여유 포함계획이며 실제분모가 아니었다. dev후속924=validation552+holdout276+UX84+G5G612, 두validation 동일config후속648=validation276+holdout276+UX84+G5G612, holdout후속96=UX84+G5G612. NL현재stage는모든잔여turn×3을예약하므로정상dev34/val0192후val02첫호출에서1476+276+648=2400. 이전672를사용하면2424로실제첫호출이차단됨을임시Budget으로재현했다. 첫dev예약은1350+102+924=2376이고비용상한은8.6217717+(102+924)×.0105+.05=$19.4447717이다. 실제추가retry/단가/usage에따라후속STOP은여전히가능하다. 장부·호출한도를늘리거나재시도횟수·평가분모를변경하지 않는다. 사용자기능검증외추가live연동smoke는이계획에자동추가하지 않으며, 필요시같은한도안에서새범위·잔여예약을재계산한다.
