# C2 입력 표현·출력 상한 설계 독립 검토

- 상태: 설계 가설 검토. **시험 가능한 후보이나 품질 개선/채택은 not_run**. 구현·모델 호출·실제장부 변경·holdout/생성기 열람0.
- 검토자 research. C1 candidate의 retrieval/provider/schema/assistant를 읽고, root의 정제 가능한 Vercel 로그와 카탈로그를 대조했다. 현재 C1/B0와 실패 분모는 변경하지 않는다.

## 관측 원인과 주장 범위

`artifacts/private/run-20260921/c1-vercel-logs.jsonl` SHA `8eb8e696f7fe8eedd46c10c80d1f76b1127b501e7ded3ea044f0bb1e3d3f549b`에서 event=model_incomplete/status=incomplete/reason=max_output_tokens, outputTokens1600을 직접 확인했다. inputTokens는19,487/19,501뿐 아니라2,871인 좁은 입력에도 발생했다. 중복 형태의 로그6레코드를 고유 호출6회라고 세지 않았다.

따라서 **출력 상한 도달은 확인된 원인**이다. 전체 카탈로그/enum의 긴 입력이 비용과 맥락 부담을 늘리는 것은 측정 가능한 개선 가설이지만, 그것만이 incomplete의 원인이라고 확정할 수 없다. 이 로그로1600이 모두 최종 JSON 문장인지 내부 추론인지도 분해할 수 없다. 입력 축소만으로 완성률 개선을 보장하지 않는다.

현재 provider는 max_output_tokens1600/45초/SDK재시도0이며 incomplete를 오류로 반환하고 실제usage를 보존한다. 3200 후보에서도 incomplete/refusal/빈output/usage불명은 성공으로 바꾸지 않고, 같은 오류·사용량·예산 기록을 유지해야 한다. 출력 상한 확대는 시간/비용에도 영향을 주므로 전체2400/$15와 필수 예비량은 그대로 대조한다.

## columns+rows: 조건부 지지

동일한8필드(id 또는ref, name, brand, category, size, flavor, aliases, observed)를 고정 columns 순서로 한 번 선언하고 각 row로 전달하는 것은 의미 손실 없이 키 반복을 줄일 수 있다. 모델에 열 설명을 명시하고 모든 row의 길이·타입·null/빈배열을 보존해야 한다. name 안의 성분·맛 표현을 잘라 별도 미검증 속성으로 만들거나, 없는 값의 null을 빈문자열/추정값으로 바꾸지 않는다.

읽기 전용 메모리 직렬화로248개를 비교했다. 원래 objects44,230bytes, columns+rows(긴SKU유지)27,455bytes, columns+rows(짧은ref)24,122bytes였다. UTF-8 JSON bytes이며 **token 수나 실제 API 비용 감소율은 아니다**. 카탈로그만 계산했으며 prompt/context/history/outputschema는 제외했다. 복원한248개 모든 projected field는 원본과 deep-equal이었다. 모델 이해의 동등성은 이 결정적 직렬화 검사만으로 입증되지 않는다.

## 짧은 ref의 필수 경계와 반례

1. **순위가 달라진 다음 턴:** 첫 요청에서 p0=A,p1=B였는데 재검색 후 p0=B,p1=A라면 과거 '첫번째'를 잘못 복원할 수 있다. 클라이언트/SQLite/평가기/assistant 응답history에는 원래 SKU를 계속 저장한다. 각 호출의 모델 전용 표현에서만 현재 map으로 구조화된 과거후보를 remap한다. 이전 짧은ref를 다음 요청의 canonical ID로 보존하지 않는다. 가장 단순한 안정화는 catalogHash에 고정된 전체SKU 순서로 ref를 만들고 shortlist는 해당ref를 그대로 선택하는 방법이다. 두 방식 모두 요청별 map과 outputSchema가 정확히 같은 집합에 묶여야 한다.
2. **병렬 요청 map 섞임:** 요청A의 p0와 요청B의 p0가 다른데 module 전역의 변경 가능한 map으로 decode하면 틀린 실제SKU가 정상검증까지 통과할 수 있다. map은 불변 카탈로그 버전 또는 요청 closure에 묶고, 응답에는 그 호출의 동일map만 사용한다.
3. **자유text의 실제SKU:** 사용자가 원래 `DEMO-…` SKU를 자연어에 넣었을 때 text를 바꾸지 않는 것은 맞다. 그러나 catalog에는 ref만 있고 원래ID 연결이 전혀 없으면 그 상품을 이해할 근거가 사라진다. 문자열에서 정확히 발견한 catalog SKU에 대한 별도 canonicalID↔ref 근거를 모델 입력에 제공하거나, canonicalID를 유지하는 더 단순한 표현을 선택한다. 이는 실제catalog 조회이며 user text를 정답/명령으로 승격하거나 case oracle을 참조하는 것이 아니다.
4. **구조화 history의 범위:** CustomerInterpretation.candidates[].id, MerchantInterpretation.constraints.excludeProductIds, context.state.currentConstraints/previousConstraints.excludeProductIds 및 groups[].sku, matchingHints.exactNameIds를 같은map으로 처리해야 한다. history의 explanation/reason 또는 사용자 자유문자열에 일괄 replace를 하면 상품 설명/부정/의도치 않은 부분문자열이 바뀐다. 지원하는 구조화 응답 JSON만 타입 확인 후 remap하고 일반 텍스트는 보존한다. assistant history 역시 클라이언트 데이터이므로 파싱 성공이 신뢰/권한 승격은 아니다.
5. **누락된 참조:** previousConstraints의 제외SKU가 현재 groups에는 없거나 이전 대체후보가 새 shortlist 밖에 있을 수 있다. merchant는248전체를 유지하고, customer는 C1의 history 참조 보존 규칙을 유지한다. map에 없는 실제SKU를 조용히 삭제/첫상품으로 치환하지 않는다. 기존 동작의 허용 범위 안에서 catalog-valid 값만 remap하고 알 수 없는 값은 같은 안전한 검증 경로로 처리한다.
6. **정확한 출력 역변환:** 먼저 모델 전용schema의 정확ref enum 및 action/constraints 구조를 검증하고, 지정된 ID 필드만 실제SKU로 decode한 뒤 기존 verifyCustomer/verifyMerchant를 실행한다. p01/p-1/p999/p0suffix/실제SKU 직접출력/다른요청ref는 enum 밖이면 거절한다. parseInt·부분일치·fuzzy 복원은 금지한다. Map 조회에 없는 값이나 중복은 그대로 오류로 남기고 실제usage를 기록한다.
7. **빈 경로 보존:** unidentified의 candidates=[], clarification, 거절·대체차이, merchant clarify의 빈constraints, restore의 기본값+restorePrevious는 계속 유효하다. ref decode가 빈배열에 임의 첫SKU를 넣으면 안 된다. confirmationRequired=true·최대6후보·추가질문2·명시정책동의·스코프·수량/금액 도메인검증도 그대로다.

설계가 올바르면 외부 API/클라이언트/SQLite/평가셋의 SKU 계약은 바뀌지 않는다. 모델 내부 표현만 바뀌며 기존 실제 catalogHash를 재생성하거나 정답을 다른SKU로 옮길 이유가 없다. 다만 semantic retrieval 순위나 shortlist를 이 변경과 함께 재조정하면 별도요인이므로 후보기록에서 구별해야 한다.

## 더 단순한 대안

| 대안 | 이점 | 한계/검토 |
|---|---|---|
| A: max_output_tokens3200만 변경 | 확인된1600 상한중단을 직접 다루는 최소요인, remap 위험0 | 입력비용 그대로, 완성률/시간/비용은 live로 확인해야 함 |
| B: A+columns/rows, 원래SKU 유지 | 반복키 대부분을 줄이고 대화/상태 SKU변환 불필요 | 긴ID enum·복사는 유지, 표 형식의 이해 회귀 확인 필요 |
| C: 전체 제안(A+rows+shortref) | 카탈로그·schema enum의 긴ID 비용까지 줄일 가설 | bidirectional mapping/이력/병렬응답 검증 부담과 복합요인 해석 부담이 가장 큼 |

**우선권고는 A 또는 B다.** 로그가 입증한 실패부터 좁게 다루고, shortref는 절감이 추가적으로 필요하거나 별도 개선근거가 있을 때 고려하는 편이 단순하다. 카탈로그-only 계산에서도 키 제거 효과16,775bytes가 ref 추가절감3,333bytes보다 컸다. 다만 enum schema의 절감은 이 수치에 없으므로 실제 전체payload를 측정하기 전 shortref 이득이 작다고 단정하지 않는다. 조정자가 후보한도/비용 때문에 C를 한 번에 선택한다면 복합가설임을 명시하고 성공을 특정한 한 요인의 효과라고 표현하지 않는다.

## 모델0 선별 및 이후 비교

- lossless codec:248 row 복원/nullable·array·순서/중복ID 검사, 모든ref 정확decode, 잘못된ref·중복·다른요청map 거절.
- 대화: 이전2후보→현재순위역전→첫번째/두번째 정정, 거절한후보와 새명시요구, 일반문자열history, 사용자 literalSKU, history 대체후보 유지.
- 경영주: groups밖의 previous 제외SKU, current→policy 복사, undo, category/budget/maxQuantity 불변, stale/권한/동의 검증 보존.
- wrapper: 공급자 mock 입력·schema 검사 후 출력ref→API 실제SKU, 성공/오류 양쪽usage/cost/providerCalled 그대로, input/output 무단원문 로깅0.
- 이후 같은 공개dev/고정validation·동일모델에서 정해진 후보한도와 Budget으로 비교한다. input/output tokens·incomplete·의미오류·대화/후보/merchant scope 정확도를 각각 보고한다. 성공률과 비용의 변화를 서로 상쇄하지 않는다. 후보채택·최종best 검증은 별도 독립평가다.

이 후보의 성공 가능성과 이미 미충족인 B0 전체UX비교는 별개다. C2를 새로운 B0로 쓰거나 이전 실패/분모를 지우는 근거가 되지 않는다.
