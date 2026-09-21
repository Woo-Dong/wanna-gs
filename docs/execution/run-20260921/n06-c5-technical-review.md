# N06 C5 stale 출력 스키마 독립 기술 검토

판정: **해당 코드·모의 SDK 경계 기술 PASS. 실제 모델 수락·품질은 미실행이며 비용 차단 유지**. 작성자 root와 별개인 method_auditor가 candidate worktree `codex/n06-stale-candidate`를 검토했다. 제품 소스 수정0, 실제 provider 네트워크0, 장부 쓰기0, 보호 holdout 접근0이다.

## 목적·변경 범위

ADR002의 오래된 제안은 재검토하고 명확한 현재 제안은 수정/복원을 허용한다는 기존 규칙을 생성 스키마에 연결한다. state.stale=true 또는 양쪽 버전이 존재하면서 서로 다를 때만 clarify/null scope/빈 constraints/비어 있지 않은 question을 허용한다. null·생략 버전만으로 오래됐다고 추정하지 않는다. 문자열 발화·특정 평가상품·case ID로 정답을 하드코딩하지 않는다.

assistant는 실제 provider를 먼저 호출하고 반환 값을 해당 스키마로 검증한다. 잘못된 restore/modify를 clarify 결과로 교체하지 않는다. 오류는 INVALID_MODEL_RESPONSE 및 기존 paid usage를 보존한다. prompt/model/profile/provider/customer/도메인·UI·예산은 이번 코드 변경에 포함되지 않았다. state는 클라이언트 데모 요약이므로 이를 서버 거래 인증이나 실제 재고의 신뢰 증명으로 표현하지 않는다.

## 검증 소스·컨텍스트

- assistant.ts SHA `721f9c3568c50803639719752b3e8acfd0afaf7d9ca74e1cb836d09395c1b364`.
- schemas.ts SHA `bef149c7c7b48995976b07344cf35c22873c404dc2e2998c4525e13789fe4ea6`.
- 작성자 회귀 stale-schema.test.ts SHA `a3f374965921b3a0867561033fed0156f7034bfa8b9418915d454d7728ee3cbe`.
- context-n06-v12 SHA `73a96eadf045ee56d68f0aab0cc45c9d2fa8028690da45199e498673dac9f2b0` ACK. 원본40파일 hash 모두 독립 대조 일치, 목적·소유권·제외범위·비용/UX 차단 확인.
- scripts/gate_contract.py를 실제 실행해 aggregate fingerprint `a15cacf8908aed8c52561bd2205a7c3ee209d5b0e9a218b20cfc65a30ee0849a`를 재계산했다. N06-C5-SERVER의 요구 CORE-05/06/17/21/23/25와 일치한다.

## 실행한 독립 검사

1. Node22에서 기존 server 전체 시험을 비구현자가 재실행해 **29/29 PASS**, skip/todo/cancel0을 확인했다. root private `c5-server-independent-tap.log` 보존. 이는 작성자 시험 재실행이며 다음 별도 독립 probe와 구분한다.
2. 독립 `c5-independent/probe.mts`: stale flag(생략/false/true) × proposalVersion(null/0/3/4) × currentVersion(생략/null/0/3/4)의 **60 상태 조합**, 정상 상태에서는 edit와 undo를 각각 확인해 **88회 주입 provider 실행**을 검사했다. false여도 버전 불일치면 stale, true면 같은 버전·null 버전에도 stale, 둘 중 하나가 미지정이면 true flag가 없는 한 기존 정상 schema를 유지했다. 모든 기대 통과.
3. 다른 문맥의 입력에서도 flag=true인 요청은 stale schema를 provider에 전달했다. restore/modify·policy scope·maxQuantity 추가·공백 question·null question **6개 오류**는 성공 결과로 변환되지 않았고 providerCalled=true/150tokens/비용0.00012를 보존했다. 공백 question은 minLength만이 아닌 후단 trim 검증에서 거절됨을 확인했다.
4. 실제 설치 OpenAI SDK를 통과시키되 global fetch를 완전히 교체한 **10회 모의 전송**을 실행했다. stale3개 정상 clarify, fresh/생략/null 경계의 edit/undo6개, stale 잘못된 restore1개를 확인했다. 외부 호출0이며 모의 API key만 사용하고 환경/fetch를 finally에서 복원했다.
5. SDK가 보내는 요청에서 gpt-4.1-mini snapshot, reasoning 속성 부재, store=false, 출력3200, strict=true를 확인했다. 모든 object는 required가 properties 전체와 같고 additionalProperties=false다. stale schema의 intent const clarify, null scope, 배열 maxItems0, restorePrevious=false를 직접 확인했다. 고객 schema는 stale 인수 true/false에서 완전히 같았다. 응답에 사용량이 있는 잘못된 stale 결과는 실제 SDK 경로 뒤에도 비용과 함께 오류 처리됐다.

private `c5-independent/result.json`에 60/88/6/10 결과와 실제호출0·장부쓰기0를 보존했다. 이 모의 결과를 실제 모델이 새로운 schema를 수락하거나 자연어 최소 기준을 통과했다는 증거로 세지 않는다. 대화의 설명 문장 품질은 여전히 live 평가 대상이다.

## Structured Outputs 계약 대조

[OpenAI 공식 Structured Outputs 문서](https://developers.openai.com/api/docs/guides/structured-outputs)를 2026-09-21 확인했다. 모든 object의 additionalProperties=false 요구에 맞고, minLength/maxLength 및 maxItems의 추가 미지원 안내는 fine-tuned 모델에 관한 것이다. 현재 후보는 명시된 일반 snapshot이며 새 schema는 object/필수키/null/단일 literal/배열 길이 제약으로 구성된다. 코드가 SDK에서 직렬화됨을 실제 모의 fetch로 확인한 것과 OpenAI 서버의 실제 수락은 분리한다. unsupported schema가 실제 반환되면 기존 400 설정 오류·사용량/null 정책을 유지해야 한다.

## 최종 범위와 남은 차단

독립 반례에서 정상 현재 수정/undo·미지정 버전·고객 경로를 막는 회귀는 발견하지 않았다. 기존 stale 정책을 좁게 강제하며 모든 요청을 거절하는 복구가 아니다. source 변경 없이 검토를 완료해 candidate `quality/reviews/n06-c5-server.json`에 기술 판정을 기록한다.

[C5 예산 감사](n06-c5-budget-audit.md)의 첫 호출 전 $15.8495333 비용 비교와 COST_SOFT_STOP 조건은 별개로 그대로다. C4 validation 두 번째83/84 실패를 C5 성공으로 전환하지 않으며, 새 C5 live dev·두 validation·holdout은 미실행이다. 기존 UX 비교 NOT_READY·G5/G6 미완료 또한 이 기술 PASS로 해소되지 않는다.
