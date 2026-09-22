# N02 검색 후보 개선 독립 검토 — 초안

- 상태: **가설 검토 완료, 후보 구현·live 개선 입증·채택은 not_run**. 기준선 실행 중 공개 dev/validation의 부분 실패10건만 읽었다. 전체 오류율이나 최종 범주 성능을 추정하지 않는다.
- 작성자 research; root가 후보 설계/구현 소유. 제품/server 소스 수정0, 모델 호출0, 보호 holdout 및 생성기 열람0.
- 적용 계약: CORE-14/15/17/25/26, ADR003, docs21/23/27, wanna-gs-nl-experiment. context-app-v5 hash `10701ed7619c86fe94cec16a31b6ac8b02a1afa9f2843ffdcce4ec446e952234` 유지.

## 관측과 원인 범위

현재 catalog.ts는 248개 전체를 하나의 JSON 배열로 넣고 id/name/brand/category/size/flavor/aliases/observed를 제공한다. assistant.ts는 요청 및 history와 함께 매번 전체 배열을 보낸다. 실패10건의 input_tokens는 약16,652~16,678이다. 프롬프트는 이미 정확 이름이면 해당 SKU만, 맛·용량·카테고리 전 제약을 확인하라고 명시한다. 단순히 같은 규칙을 더 길게 반복하는 것보다 입력 후보의 관련성과 속성 구별을 개선할 이유가 있다.

정답 SKU 전부가 원본248에 존재하고 모델 입력에서도 빠지지 않으므로 **기준선 검색 누락은 아니다**. 검증 성공 응답5건은 근접 상품 변형으로 치환하거나 추가했다.

| 공개 실패 | 요구 상품 | 유효 응답의 다른 상품 | 확인한 실패 |
|---|---|---|---|
| C01-dev-008 | 빵또아 팥인절미 180ml | 빵또아 부드러운 180ml | 특정 변형 대신 같은 계열 다른 맛 |
| C01-dev-017 | 계란명란마요김밥 | 참치계란김밥 | 이름의 공통 재료보다 차이 제약을 놓침 |
| C01-dev-018 | 소프트새우마요 | 소프트치킨마요+정답 | 정답 포함만으로는 성공 아님; 불필요 primary 추가 |
| C02-dev-002 | UNO 치즈 핫도그 400g | UNO 오리지널 핫도그 400g | 용량/계열 동일, 치즈 제약 누락 |
| C02-dev-007 | 소프트새우마요 | 소프트치킨마요 | 속성 기술에서도 같은 치환 |

나머지5건은 HTTP502 INVALID_MODEL_RESPONSE다. 공급자 호출과 usage는 기록됐지만 raw 응답이 관측파일에 없으므로 허구ID/스키마/행동분기/다른 검증조건 중 어느 것이 실패했는지 알 수 없다. 이들을 이름↔SKU 결합 문제로 확정하거나 transport 성공으로 다시 세면 안 된다. 현재 verifyCustomer는 ID의 전체 catalog 포함 및 구조/행동 모순을 확인하나, 유효한 다른 SKU와 사용자의 이름 불일치를 의미적으로 검증하지 않는다.

**가설:** 전체 목록에서 비슷한 이름·불투명한 내부ID를 선택할 때 구별 속성과 ID 결합이 약해진다. 이 가설은 실제 관측과 부합하지만 작은 모델의 인과나 context 길이 효과를 단독 입증한 것은 아니다. name 안의 맛 표현이 flavor:null이어도 확인 가능한 이름 사실은 남아 있다. flavor 미검증을 임의 영양·성분 사실로 채우지 않는다.

## 관련24 우선 검색안 의견

채택 전 시험할 타당한 후보다. 검색은 모델의 근거를 줄이고 정렬하는 역할로 한정하며 사용자 확인·동의·대체 분류·추가질문2회·미식별 경로를 유지해야 한다. 현재 진행 중인 기준선을 먼저 완주하고 결과를 동결한 뒤 후보1개로 비교한다. 다음은 구현 시 일반적으로 지킬 조건이며 case별 예외표나 oracle 사용을 뜻하지 않는다.

1. 전체 카탈로그의 실제 name/기존 alias/brand/category/size를 인덱싱한다. Unicode 정규화와 공백·문장부호 처리는 검색용으로만 적용하고 모델에는 원문 이름·단위·ID를 한 객체로 유지한다. 숫자와 g/ml, 치즈/오리지널 등의 차이를 지우지 않는다. 정확 name/alias와 여러 명시 속성의 일치를 단순 공통 브랜드 또는 흔한 bigram 점수보다 우선한다. 짧거나 여러 상품에 겹치는 alias를 고유 exact로 취급하지 않는다.
2. 명확 근거가 없는 경우 전체 fallback을 유지한다. 양수 bigram 한 개가 곧 충분한 근거는 아니다. 짧은 일반어·카테고리·광고성 표현에서는 top24가 정답을 임의 제거하지 않도록 낮은 근거/동률 밀집을 감지한다. top1만 남기는 방식은 genuinely ambiguous 변형 비교를 막으므로 피한다. broad intent에 24개를 주더라도 목록 완전성을 모델이 오해해 unidentified로 단정해서는 안 된다.
3. 최신 사용자 발화와 이력의 역할을 구분한다. 이전 assistant 후보 ID는 실제 catalog에 있는 것만 참조 후보로 보존하여 '첫번째/두번째'가 풀리게 한다. 전체 history 문자열을 같은 가중치로 검색하면 거절한 옛 상품이 새 요구보다 우선할 수 있다. 이전 후보를 넣는 것과 지금 확정 정답으로 취급하는 것은 다르다. 최신 명시 정정·부정 제약이 우선하며 history의 지시문/가짜ID는 권한을 갖지 않는다.
4. 정확명 포함을 이유로 모델 출력 자체를 정답으로 강제 교체하지 않는다. 'X 말고 Y', 'X와 Y 중', 범위밖 다상품/명령 주입도 정확명을 포함할 수 있다. 관련24는 검색 근거이며 식별 action/대체차이/동의는 기존 계약을 따른다. 경영주에 함께 적용하면 state.groups 및 기존 constraints의 참조 SKU도 잃지 않아야 한다; 고객 전용 후보로 시작하면 영향범위를 더 명확히 분리할 수 있다.
5. 검색 후보 ID와 점수/선정 이유/전체fallback 여부를 실험 증거로 남겨 recall 손실과 모델 선택 오류를 분리한다. 오답을 runtime 정답표로 고치는 대신 출력 검증 실패의 안전한 사유코드를 관측 가능하게 하는 것은 후속 가설이며, 이번 검색변경에 무단 묶지 않는다.

## 모델0 선별과 이후 평가

- 248SKU 각각의 실제 정확명/ID 검색 포함 검사. 검색 fixture는 최종 자연어 정확도의 대체가 아니다.
- 공개 dev의 이름/별칭/띄어쓰기/Unicode·속성조합 입력에서 required SKU의 retrieval recall과 유효 후보수를 측정. 검색함수 입력은 오직 사용자text/history/catalog이며 case_id/expected/정답파일은 runtime에 전달하지 않는다. 평가 시 정답을 판정에 쓰는 것과 검색 알고리즘에 넣는 것을 구별한다.
- 인접 회귀: 같은 계열 다른 맛·용량, 이름이 짧거나 겹치는 상품, 숫자·단위, 무근거 일반어, 등록되지 않은 정확명, 명시 대체 거절, 앞 후보 순서 참조, 최신 정정, 두 질문 종료, 주입 문자열. 새 synthetic regression은 dev 용도로 표시하며 validation/holdout에 복사하지 않는다.
- live는 기준선 완료 후 사전 예산 안에서 dev 선별과 고정 validation paired 비교를 수행한다. clear composite/모호·미식별/경영주 scope 등 기존 분모·최소 기준을 유지하고, 정상 경로 회귀나 잘못된 primary 추가를 정답 포함으로 상쇄하지 않는다.
- validation2건 오류감소 또는 correctness 유지+P95 15% 개선, 핵심범주·필수정상 회귀0 등 ADR003 채택 기준을 그대로 사용한다. 후보 채택은 독립 evaluator의 평가 후 결정한다. 이 초안은 후보 live 승인이나 출시 통과가 아니다.

## 읽은 자료 동결

부분 분석 파일은 읽은 시점의10건 스냅샷이다. 이후 전체 기준선 결과로 결론을 갱신할 수 있지만 이번 문서를 최종 성능 보고로 사용하지 않는다.
- `src/server/catalog.ts`: `6956ab9d275ae29263d5b4cdc2338dd2519160eed1b0fd3f1b2b9003a1f4f9fb`
- `src/server/prompts.ts`: `62242b67db9a9f3d6f2297e1c54fa349809c5fc305526564e83532f5bf2775b0`
- `src/server/assistant.ts`: `47a0b113a4dbb97781398f7cb28c7ed52e8e4a0fbdda999b690c504f9cc430c4`
- `artifacts/private/run-20260921/n02-baseline-analysis-partial/observed-failures.json`: `c23c154d15a5b559aa941940b6e76752ee35e67fe028bfc7e969e26d11869490`

작성 시각: 2026-09-21T10:15:45.752686+00:00

## C1 설계 delta — 모델0 읽기 검토

context-n02-v6 SHA `0555063cc1bca9224124b2522d9371bf8ec8178ada49083c9bd306ae0d738a3b` 및 입력29개 hash를 직접 ACK했다. root의 offline prototype은 공개 dev만 소비하며 query 정규화/전체이름 포함/bigram 순위와 반환후 recall 측정을 분리한다. 실제전체명 근거가 있는143/180만24개로 축소하고 약한 검색은248개 순서만 바꾸는 방향은 초기 제안보다 recall 위험을 줄인다. root 보고의 recall miss0는 모델 품질 증거가 아니다.

실제 전달 catalogID enum은 허구ID·불투명ID 오타를 구조적으로 막는 타당한 보강이다. 현재 verifyCustomer/verifyMerchant 및 동의/질문 제한을 그대로 유지해야 한다. 다만 유효한 다른 variantID는 enum을 통과하므로 별도의 매핑 정확도 비교가 필요하다. 검색+matchingHints+schema enum은 복합 후보이므로 실험 기록에 세 변화를 명시하고 비용/오류 개선을 특정 한 요인 효과라고 단정하지 않는다.

확인할 좁은 경계는 다음과 같다.

- matchingHints는 이름 문자열 일치라는 사실만 전달하고 exact action/사용자 긍정·의료적 적합성의 증거로 격상하지 않는다. 'X 말고'의X, 겹치는 짧은 이름, 다른 조건을 덧붙인 입력도 full-name evidence가 생긴다. 최신 제약은 모델 판단과 기존검증에 남긴다는 root 설명에 동의한다.
- prototype history는 사용자 이전발화 문자열만 쓴다. 앱은 assistant 전체응답JSON을 보내므로 최종 구현에서 이전 후보의 유효ID/순서를 pin하되 거절한 후보를 강제정답으로 만들지 않는 정상회귀가 필요하다. 공개 dev prototype의 recall0를 앱 대화 recall0로 확대하면 안 된다.
- enum은 array item 값에만 적용하고 unidentified/clarify의 빈 candidates·빈 excludeProductIds는 계속 유효해야 한다. JSON schema 변환 후 실제 허용id집합/nullable scope/질문종료 계약을 fixture로 확인한다. 전달된24 밖의 정답ID가 막히면 안전하더라도 정상실패가 되므로 exact+부정·정정에서도 retrieval recall을 먼저 검사한다.
- merchant category enum은 실제카테고리의 모든 값, SKU enum은 current state.groups·기존/이전 constraints 참조의 카탈로그값을 포함해야 한다. 고객 검색24 제한을 그대로 merchant에 적용하지 않는다.

기준선 완료 전 live 후보 실행·제품기본값 변경은 이번 검토 범위에서 승인하지 않았으며 기존 동결을 유지했다.
