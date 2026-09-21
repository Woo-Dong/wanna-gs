# N03 C2 독립 기술 검토

판정: **기술 PASS / 실제 모델 수락·품질·채택 not_run**. 후보 작성자 root와 독립인 method_auditor가 server21tests와 별도 private9 검사를 직접 실행했다. 실제 모델 호출0이다.

소비 컨텍스트 N03-v8 SHA `b46df3e009cb79bf222dd350cc2b477c3c1b39558bcdda21d9b8bd4dfe125600`. 검토 결과는 해당 manifest 및 candidate source fingerprint에 결속한다.

## 검증한 계약

- 전역 catalog 순서에 고정된 pN 참조 248개의 유일성·왕복 변환·원본 불변을 검증했다. 검색 결과의 표시 순서나 부분집합에서 참조가 달라지지 않고 기존 catalogContext의 모든 속성값을 table rows에 보존한다.
- user text/history는 그대로 유지한다. assistant JSON의 구조화 후보 ID와 typed state의 sku/excludeProductIds를 변환하며 설명·차이 문장의 문자열은 바꾸지 않는다. 현재/이전 제한, revision/stale, 수량·예산을 보존했다.
- 과거 대체 후보가 현재 exact 검색 범위 밖이어도 history를 통해 유지되고 canonical SKU로 복원되는 것을 mocked-provider interpret 실제 경로에서 확인했다. merchant는 전체248과 이전 복원 상태를 보존한다.
- 출력은 supplied-ref schema 검증→canonical 복원→기존 verify 순서다. 임의 참조, canonical ID 직접 출력, 중복 후보, 확인 거짓값, exact+unknown을 거절하며 실패 usage도 보존한다. 모델에 거래·동의 권한을 추가하지 않았다.
- nested anyOf와 maxItems0는 기존 exact/unknown 불변식을 생성 단계에도 적용한다. confirm/alternative의 미확인 조건은 유지한다. 독립 JSON schema 순회에서 모든 object의 required/additionalProperties=false, 금지 composition 없음, customer enum501/merchant270(<1000)을 확인했다. [OpenAI 공식 Structured Outputs 문서](https://developers.openai.com/api/docs/guides/structured-outputs)의 nested anyOf·enum·maxItems 지원 범위와 일치한다. 실제 지정 모델의 API 수락과는 구분한다.

## 목적·증거·한계

상충 지시를 임의의 일부 명령으로 바꾸지 않는 merchant prompt는 기존 clarify 계약을 명확히 한다. 평가 정답이나 데이터셋을 변경하지 않았다. max_output_tokens3200은 고정 출력 여유이며 retry·45초 timeout·global budget 확장이 아니다. C1 출력 상한 실패 해결은 동일 dev30 실제 관측이 필요하다.

독립 server21 PASS와 추가9 검사 원본은 root의 `artifacts/private/run-20260921/c2-server-independent-tap.log`, `c2-review/probe.mts`, `probe.json`, `source-hashes.json`에 보존한다. 이번 범위에서 새로운 반례를 발견하지 않았다. type/build는 root 검증과 구분한다.

출력 상한이 두 배로 늘어 다음 필수 비용 예약은 이전 $.008 예측을 자동 재사용하지 않고 실제 input/output과 대조해야 한다. 본 리뷰는 실제 응답 품질·최소 기준·UX 비교·G5/G6 완료를 의미하지 않는다. B0/C1 실패와 holdout 미실행을 유지한다.
