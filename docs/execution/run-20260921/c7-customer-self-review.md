# C7 고객 동일성 프롬프트 자체 검토

상태: 구현·자체 기술검사 PASS, 독립 기술검토 대기, 실제 모델 품질 NOT_RUN. 작성자 preflight_builder. 자기 검사를 독립 QA로 세지 않는다.

## 목적과 권한

D-47 사용자 직접 승인에 따라 고객 후보 7번째 하나를 추가한다. 경영주 6/전체13, $20/2400 단일 장부·prior50·unknown/후속 예약, 원래 출시 최소·양 역할 validation2·새 holdout 최초1·UX/역할 QA/G5/G6는 유지한다. C6 공개 dev29/30 실패 및 이전 실패를 바꾸지 않는다. 다시 필수 기준에 미달하면 자동 추가 후보·재평가를 하지 않는다.

card·CORE02/03/11/17/18/21/25·03/13/15/21/23/27·D46/D47와 c7-customer-contract를 확인했다. codex/n08-customer-recovery, base311b934f54b6b3b160154589c2ad3fd6816033f9, 초기 CTX-N08-v16 SHA c086627dee6c087770cfed225ea3c0110d41346b9289207907586ac79b196c9e의 59개 입력 hash 일치 ACK. 이 초기 context의 prompt hash는 구현 전 값이며 최종 source context 갱신은 root 소유다.

## 관찰, 가설, 한 요인 변경

공개 C6 C05-dev-002의 보고된 오류는 미등록 고유상품과 대체 거절 요청에 다른 실존 SKU를 exact로 제시한 것이다. SKU가 실제 존재한다는 검증만으로 요청한 상품과의 동일성까지 보장하지 못한다. 모델 내부 원인은 확인하지 않았다. 가설은 동일상품의 불확실 조건과 다른 상품의 공통 속성을 분리하는 판단 순서가 부족하다는 것이다. 단일 사례가 이 원인을 입증한다고 주장하지 않는다.

변경은 src/server/prompts.ts의 CUSTOMER_PROMPT와 PROMPT_VERSION=customer-identity-v7뿐이다. 일반 판정 순서 한 문단을 추가하고 exact 정의와 미식별/대체 거절 문장을 명확히 했다.

1. 최신 명시적 정정과 원래 찾는 상품을 해석한다.
2. 같은 상품이라는 근거를 먼저 확인한다. 정확명뿐 아니라 알아볼 수 있는 별칭/오타 및 충분히 식별적인 관측 속성을 허용한다. 특정 고유명·브랜드를 무시하거나 가짜 별칭을 만들어 공통 분류/맛/질감/용도만 같은 상품으로 바꾸지 않는다.
3. 같은 상품 후보에서 조건만 미확인된 경우 confirm/unknownConditions를 유지한다. 다른 상품은 alternative이며 confirm으로 바꾸어 원상품으로 제시하지 않는다.
4. 대체 거절은 대체 후보를 막는다. 같은 요청 상품의 정상 식별까지 막지 않는다. 식별되지 않는 특정 상품+대체 거절은 unidentified/candidates=[]로 제공 카탈로그 범위만 설명한다. 상품 자체가 실재하지 않는다고 단정하지 않는다. 후속 명시 정정은 새 상품을 정상적으로 찾을 수 있다.

특정 case/상품명/SKU/정답을 프롬프트에 넣지 않았다. schema·검색·packing·모델·catalog·후단 출력/거래 코드는 바꾸지 않았다. 모든 입력을 거절하거나 원상품 확인/동의를 생략하는 규칙도 없다.

OpenAI Docs의 [GPT-4.1 공식 가이드](https://developers.openai.com/api/docs/guides/latest-model?model=gpt-4.1)를 직접 확인했다(2026-09-21). 구체적인 지시·모순 검토·경험적 평가를 권하는 자료이며 이 후보의 품질 성공 근거는 아니다. 모델 변경이나 추론 출력 요구를 추가하지 않았다.

## 목적 보존과 남은 live 검증

| 경로 | 유지한 계약 / 실제 모델에서 확인할 사항 |
|---|---|
| 명확한 상품·대체 거절 | 해당 상품 자체는 정상 후보. 거절을 전체 후보 차단으로 확대하지 않음 |
| 별칭·오타·띄어쓰기 | literal equality 필수 아님. 실제 동등 표현 식별 유지 |
| 속성으로 상품 표현 | 충분히 식별적인 관측 속성은 근거. 넓은 표현은 구분 질문 |
| 알레르기·성분 불확실 | 같은 상품 조건 미확인은 confirm+unknownConditions. 인증/적합성 확정 금지 |
| 미등록 고유상품 | 공통 속성의 다른 SKU를 exact/confirm으로 대체 금지 |
| 대체 허용 | 기존 공통점·차이와 alternative 표시, 고객 확인 유지 |
| 모호함·후속 정정 | 질문 한도2 및 최신 명시적 정정 우선 유지 |
| 경영주·거래 | merchant instruction·공통 코드·동의/SQL/48시간 그대로 |

위 표는 보존할 계약과 평가 대상이며 실모델 통과 표가 아니다. 프롬프트가 길어져 토큰/지연이 늘거나 모델이 과도하게 보류하는 위험은 후속 동일 dev/validation에서 관측해야 한다.

## 자체 기술검사와 바이트 증거

- Node22 `node --import tsx --test tests/server/*.test.ts`: 기존41/41 PASS, 실패0/skip0. 명확 후보/확인, 허구·중복 SKU 거절, 미식별과 대체 primary 구분, 조건 불확실 confirm, 질문 한도, provider 실패, 실제 catalog248 정확명 유지, 정정 검색, 경영주 scope/undo/분류/schema, SDK mock strict출력 검사를 포함한다. 실제 provider 모델 호출0; fixture/SDK mock 기술검사다.
- Node22 `node node_modules/typescript/bin/tsc --noEmit --incremental false`: PASS.
- `git show HEAD:src/server/prompts.ts`와 현재 MERCHANT_PROMPT export부터 EOF까지5984 UTF-8 bytes 완전일치. 양쪽 SHA256 c86b81dc242cd583bb2767e7e67f31f7dd49459fce0746d8dbf203c99235e956. 템플릿 literal 내부 값만의 SHA256 f15910056c822eb7480fa86214f773de853c7d3c6479164fc90713a1958085f9. hash 범위를 명시해 export/value 지문 혼동을 피한다.
- 초기 context의 prompt 제외 src11개 hash 전부 일치. `git diff --name-only -- src tests/server`는 src/server/prompts.ts만 반환한다. 소스 전체 파일 SHA256 02334ef1e86a4707db47280e607194ccde0de91b817b480c2b5672db4f7d1be4.
- 문구 존재만 검사하는 새 단위테스트는 추가하지 않았다. 기존 실제 함수·fixture/SDK mock 검사를 사용했으며 자연어 품질은 독립 실모델 평가로만 확인한다.

실제 모델·브라우저·장부 쓰기·환경 변경·보호 holdout 원문 접근0. 공개 실패 보고 외 새 평가 정답을 작성하거나 바꾸지 않았다. 다음: research 독립 delta 검토 → root 최종 context/정확 source·CI/Preview → method_auditor 별도 GO의 원래 유효 평가. C7 best 승격 및 제품/goal 완료는 아직 아니다.
