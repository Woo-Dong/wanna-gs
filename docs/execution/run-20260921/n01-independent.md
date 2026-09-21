# N01 독립 G1/G2 경계 검토

- 검증자 `/root/method_auditor`; 구현자 root와 별개. wanna-gs-verify 적용, card/CORE-03/05/11/15/21/23/25 및 docs05/09/13/25/27/29 기준.
- consumed context APP-v3 `e8d6eb6ffef8765544e3aeeeb9c27b1e98f0c7cb5131202712ec4d32d806ea99`. 현재 N01 미커밋 소스 검토, base HEAD `04a2a3f274c0f0d0917801d7f625f2036ac32331`. 정확 소스 hash는 아래 표.
- 목적: 정상 상품/경영주 지시를 구조화 제안으로 보존하고 고객동의/거래권한과 분리한다. 오류를 미식별 니즈로 만들지 않는다.
- 판정: **G1/G2 부분 검사 PASS, N01 전체 독립 승인은 FAIL/복구 대기**. 모델404 오류구분 및 오래된 제안 입력계약 공백, 정상 경영주 live smoke 실패가 남는다. 앱 G3~G6/정식baseline/holdout은 not_run.

## 실행 증거

1. 별도 프로세스 Node22로 기존 `tests/server/*.test.ts` 9/9 PASS, typecheck PASS. 기존 작성자 테스트의 단순 재실행과 아래 독립 반례를 구분한다.
2. 독립 작성한 private SDK harness는 실제 installed OpenAI SDK를 사용하되 global fetch만 교체해 외부모델호출0/가짜HTTP응답9건을 주입했다. 성공 구조화응답, incomplete(사용량존재), refusal, invalid JSON,401,403,404,429 rate,429 quota를 실행했다. fake key marker는 응답/오류객체에 유출되지 않았다. `store:false`, strict JSONschema,1600 token cap,tools없는 요청을 확인했다.
3. incomplete/refusal/invalidJSON은 성공/미식별로 바뀌지 않았고 usage10+20=30을 attempt에 보존했다.401/403은 nonretry auth오류, quota는 nonretry, rate는retryable. 키없을때 SDK fetch0. fixture provider의 늦은성공 응답에 원래 session/generation/actor/roleEpoch/request/conversation/inputRevision/catalogHash 모두 보존.
4. 독립 live smoke2회: 정확일반바나나240ml 단일primary PASS, 현재제안조건을 ‘앞으로도 이렇게’ 정책으로 복사하는 merchant 정상경로 INVALID_MODEL_RESPONSE. 각각 gpt-5-mini-2025-08-07,16,726/16,817 total tokens,2669/3047ms,추정$0.00441775/$0.00454375. 실패 usage보존은PASS이나 정상성공은FAIL. prompt hash `94ec92f57503fe320fce0047368b9eccc9547e7f9a48e8a510a182489da7185d`. formal eval/holdout이 아닌 공개기능 smoke다.

## 수정 요청

- **N01-01**: 실제 SDK mock404/model_not_found가 `LLM_UNAVAILABLE`,retryable=true로 반환된다. docs25의 모델/경로 오류 구분에 맞춰 구성오류는 별도 nonretry로 분류하고 정상응답·rate429회복은 보존해야 한다. timeout도 현재 catch에서 일반unavailable과합쳐져있다.401/403원문이나키는 노출하지 않는다.
- **N01-02**: merchant state schema는 proposalVersion하나만 받고 strict다. E01의 stale 케이스가 필요로 하는 requested/observed version과current version 비교근거를 전달할 수 없다. 독립으로 currentRevision/stale를 제공하면 입력검사FAIL이 재현된다. 실제브라우저 최신상태검사는 별도 필수이며, 모델제안평가에도 필요한업무맥락을 전달하는 명확한adapter/schema계약을 작성해야 한다. oracle/정답을 모델에보내서 해결하지 않는다.
- **N01-03**: 현재조건의policy복사 정상live가 INVALID_MODEL_RESPONSE. 추가 1회 원응답 capture로 원인을 확인 중이며 총live4회한도를 넘지 않는다. 거절을 늘리는 복구는 정상흐름을 대체하지 못한다.
- 관측: 모든 제약이빈 modify/current_proposal도 validator가 허용한다. 실행권한은없으므로독립거래위반으로세지는않지만 승인요청을빈변경으로포장하거나no-op확인을반복시키지않는 UI/domain회귀가 필요하다.
- 관측: HTTP error log의 requestId는성공후에만할당되어실패에서는undefined다. 입력검증후안전한requestId를로그와연결하면실패attempt대조가쉬워진다. 오류 응답의새로운권한필드가필요하다는의미는아니다.

## 경계와 미실행

서버모듈에 DB/거래실행도구가없으며 provider/model/key는요청에서바꿀수없다. strict output에unknown SKU/중복/자동확정추가필드를주입하면거절된다. 그러나 알려진SKU의잘못된설명·차이·유사SKU선택은schema만으로진실성을보증하지않는다. 고정품질평가와브라우저최종확인에남긴다. late응답envelope보존은확인했지만실제reset후UI쓰기차단/role전환/SQLite는N01범위에서not_run. 실제browserbundle 키비노출과Vercel동작은G4/G6에서확인한다. protectedholdout본문/정답은모델입력이나문서에노출하지않았고호출0이다.

## 소스 지문

- `src/server/schemas.ts`: `f5196ab691f73d69dc08ed038e356b06c362c3ad6319445770b244d014f117c7`
- `src/server/prompts.ts`: `a736b43a7d55fd47660bfc24337dc9cb20e466b2ac5d7871e677415ffcd11212`
- `src/server/assistant.ts`: `47a0b113a4dbb97781398f7cb28c7ed52e8e4a0fbdda999b690c504f9cc430c4`
- `src/server/provider.ts`: `3f742ed158ba17bf2764e10465c150c584ac0020777e48822a59aadfcc502b2b`
- `src/server/catalog.ts`: `6956ab9d275ae29263d5b4cdc2338dd2519160eed1b0fd3f1b2b9003a1f4f9fb`
- `src/contracts/assistant.ts`: `a482963843722dcd469d220ed41b391c3bc776eab5a79983adb8c1016b59815b`
- `app/api/product-assistant/route.ts`: `92f206e113475dbc0e5f407b2989994d6263894a09a2bc2ac3477e8e7da810c9`
- `app/api/merchant-assistant/route.ts`: `d4fe6b9ea51106fef261551414118ae06026eae3c9b3a3857f34f24c71b3fbb0`

## 2차 복구 검증 — live 추가 호출 중지

구현자가 N01-01/02 및 empty-modify 경계를 보완한 후 독립 SDK harness를13모의HTTP경로로 재실행했다(실모델0).400→LLM_CONFIGURATION/nonretry,404→LLM_MODEL_UNAVAILABLE/nonretry,실제SDK AbortError 경로→LLM_TIMEOUT/504/retry를 확인했다. 음수usage·합계불일치usage가 INVALID_MODEL_RESPONSE로 거절되고 정상usage/incomplete/401/403/rate/quota 경계는 유지됐다. currentProposalVersion/stale 필드를 포함한 상태입력이 정상수용되고 빈 modify는거절된다. 기존정상9tests도재실행9PASS. 따라서 **N01-01/N01-02 수정 검증 PASS**다. 실제stale모델행동/브라우저state검사는후속평가에남긴다.

독립live 세번째1회는앞선경영주실패의원응답만추적했다. 응답은현재예산50000과제외SKU를정확히읽었으나 intent=clarify/scope=policy로반환하고같은조건을정책으로고정할지재질문했다. 이는불필요질문과clarify.scope계약위반이고서버거절자체는옳다. 세번째총16,838tokens/4644ms/$0.00450875,실패사용량보존PASS. 호출중prompt보완이병행되었으므로세번째를정식paired/frozen평가로표현하지않는다. raw는private/n01-merchant-diagnose.json,holdout과무관한공개정상smoke다.

독립 live 누적3회/50,381tokens/추정$0.01347025,성공customer1/실패merchant2. 구현자사전smoke와합산은조정자가goal사용량원장에반영한다. 지시받은추가호출중지를준수해네번째는실행하지않는다. **현재N01-03 정상경영주모델경로 FAIL 미해소**이며이후prompt수정은정상성공재검증이필요하다. 기술경계G1/G2 bounded PASS를N01품질/정식eval/G5/G6 PASS로확대하지않는다.

수정후소스지문:
- `src/server/provider.ts`: `3f742ed158ba17bf2764e10465c150c584ac0020777e48822a59aadfcc502b2b`
- `src/server/schemas.ts`: `f5196ab691f73d69dc08ed038e356b06c362c3ad6319445770b244d014f117c7`
- `src/server/assistant.ts`: `47a0b113a4dbb97781398f7cb28c7ed52e8e4a0fbdda999b690c504f9cc430c4`
- `src/server/prompts.ts`: `62242b67db9a9f3d6f2297e1c54fa349809c5fc305526564e83532f5bf2775b0`
- `src/contracts/assistant.ts`: `a482963843722dcd469d220ed41b391c3bc776eab5a79983adb8c1016b59815b`

## 최종 bounded 판정

조정자가 UI의승인과모델의제안생성을분리하는prompt를보완한뒤,명시요청에따라허용한마지막4번째동일merchant smoke를실행했다. intent=modify,scope=policy,budgetLimitKrw=50000,excludeProductIds=정확한현재조건SKU하나,question=null로정상반환됐다.사용량16,859tokens/2369ms/추정$0.004416,gpt-5-mini-2025-08-07. **N01-03 정상복구PASS, N01 G1/G2 기술경계와두역할제한된live smoke에대해독립 bounded PASS**다. 이전2건실패를삭제하거나최종성공으로대체하지않는다.

독립전체4calls/67,240tokens/추정$0.01788625. 추가모델호출중지. 최종품질은고정baseline336·검증반복·protectedholdout84및브라우저상태연결을통과해야하며아직not_run다. 이소량smoke는최소95%/90%성능근거가아니다. 최종정식평가버전은baseline실행전에prompt/source를다시freeze해야한다.

최종prompt hash: `62242b67db9a9f3d6f2297e1c54fa349809c5fc305526564e83532f5bf2775b0`.

## N01 phase 실행기 추가 검토

context-app-v4 hash `0788c0e5ed96f22adc527f3cd30dc4830a5e43138cd5da992a734e0b06559997` ACK,20원본hash전수일치. phase는assistant-foundation으로N01만필수이며제품전체완료가아니다. counts_file별리포트분리·기존count삭제후실행·0/skip/todo/cancel/중복count거절을읽고독립8TAP반례및실제Node9/Python68테스트를실행했다. source_patterns에tests/server와공개evalJSON/JSONL누락을지적해추가한것을확인했다. `quality/reviews/N01.json`을검증자직접작성했으며fingerprint는 `ef8c2a8af96d66405a1681f536d1b6b4c4ad76b02b55f0d6c941f3cb000dfb99`다. fullgate/build/CI는조정자실행결과와별도이다.
