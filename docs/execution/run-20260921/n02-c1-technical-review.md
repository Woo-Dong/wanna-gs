# N02 C1 독립 기술 검토

판정: **수정 필요 — 실제 품질 채택 아님**. evaluator는 후보를 구현하지 않았다. 대상은 별도 nl-candidate worktree의 retrieval-enum-v2이며 baseline exact10c0072 배포/실행과 분리했다. 소비 컨텍스트는 CTX-N02-v6 `0555063cc1bca9224124b2522d9371bf8ec8178ada49083c9bd306ae0d738a3b`(29 원본 hash 일치), 제품 계약은 APPv5와 동일하다. 후보 소스 hash는 private c1-review/source-hashes.json에 동결했다.

독립 실행: Node22의 기존 server15tests 전부 PASS. 추가 private retrieval/schema probe 실행. 실제 모델 호출0. 타입/build는 이 검토에서 재실행하지 않았고 구현자의 PASS와 구분한다.

## C1-R01 — 거절한 literal이 다른 범주 후보를 제거

`retrieveCatalog`는 query에 complete 상품명이 포함되면 긍정/거절을 구별하지 않고 상위24개로 자른다. “오뚜기밥 210g 말고 유제품으로 추천해 주세요.”의 exactNameIds는 거절한 밥이며 원본 유제품26개가 전부 제거된다. “짜슐랭 145g는 싫고 아이스크림 먹고 싶어요.”도 원본 디저트·아이스크림30개 중 반환0이다. dynamic enum까지 좁힌 집합으로 제한하므로 모델은 올바른 다른 범주 후보를 낼 수 없다. 고객의 거절·대체 정상 흐름에 영향을 준다.

반례 증거는 private c1-review/retrieval-probe.jsonl 및 schema-probe.jsonl. 개선은 명확한 긍정 exact 검색의 이익을 보존하면서 거절/교정/비교/불확실 새조건에서 full-catalog fallback을 유지해야 한다. 특정 평가 발화별 예외나 답안 하드코딩을 요구하지 않는다. 동일 반례와 기존 exact248/이전후보 보존을 함께 재검증할 것.

## 보존된 계약과 범위

후보는 confirmationRequired=true·거래 없음·서버 verifyCustomer/verifyMerchant 재검증을 유지한다. unknown 조건의 exact 금지, unidentified의 primary 금지, clarification cap, 중복/허구SKU 차단도 기존15tests에서 확인했다. 진단은 정해진 rule ID만 반환하며 모델 원문/키를 노출하지 않는다. weak match에서는248을 모두 보존하고 history에 나온 ID도 남긴다. 그러나 이런 정상 경로 PASS가 C1-R01 회귀를 상쇄하지 않는다.

생성한 두 역할 JSON schema를 독립 순회하여 모든 object의 additionalProperties=false/모든 property required, 금지 composition 없음, 총 enum customer254/merchant270(<1000)을 확인했다. [OpenAI 공식 Structured Outputs 문서](https://developers.openai.com/api/docs/guides/structured-outputs)는 enum과 array maxItems를 지원한다. 이 정적 검사와 문서 대조는 지정 gpt-5-mini snapshot의 실제 API 수락/품질을 대신하지 않는다. live acceptance는 baseline 후 별도 bounded 실행이 필요하다.

## C1-R01 수정 후 독립 재검증

작성자가 named exact를 제거한 나머지가 흔한 긍정 요청·수량 표현뿐일 때만 축소하도록 수정했다. 그 외 조건은248 전체를 유지한다. evaluator가 동일 두 반례를 다시 실행해 유제품26/26·아이스크림30/30 보존을 확인했다. 독립 기존+추가 server16tests PASS: exact248 정상 검색, history 후보, 거절/비교/추가조건, 동의/unknown/대체 경계 포함. JSON schema 정적 검사를 다시 실행해 PASS. private schema-probe-after.jsonl와 source-hashes-after.json으로 최신 소스를 결속한다.

최종 bounded 판정: **C1 기술 검토 PASS, 실제 API 수락/모델 품질 not_run, 후보 채택 보류**. 회귀를 고친 사실이 전체 자연어 품질 통과를 뜻하지 않으며 다음 live smoke/dev 평가가 필요하다. 이 검토 중 후보 실제 모델 호출0, baseline 실행은 계속 보존했다.

## 경영주 prompt delta 추가 검토

후보는 constraints를 현재상태 복사가 아닌 수정 delta로 명시하고, stale/금지실행/모순지시의 clarify 기본값을 우선하며 restore의 다른조건 기본값과 개별SKU 제외를 category로 확대하지 않는 규칙을 추가했다. 이는 기존 unspecified null/empty 계약과 일치하며 평가정답 자체를 변경하지 않는다. 독립 server16tests 재실행 PASS. 모델이 실제로 따르는지는 live not_run이다.

정적 관찰: 최신 assistant.ts의 suppliedCatalog=retrieved.catalog는 merchant에도 plain literal이면24개를 전달한다. 작성자 설명의 ‘merchant 전체 유지’와 달라 보수적 역할분리 확인을 요청했다. 예산/정책 지시는 대부분 full fallback이지만 명시 계약을 그대로 보존해야 한다.

## 후속 예비비 계획 독립 계산

조정자는 이전 $.01/attempt의 미래 비용 추정을 $.008로 갱신 제안했다. baseline 실측 평균1.659112/367≈$.0045207의약1.77배이다. 1032×$.008=$8.256, 현재계상4.159112+미래8.256+다음unknown.05=12.465112<$15이며 선택실험 여유는$2.534888이다. 전체2400/$15/unknownattempt.05의실제중단로직은불변이다. 이 값은 미래실비/최악보장이아닌계획추정으로 조건부수용한다. C1출력1600token최대에서는입력19,200token만으로$.008에도달하므로 enum/context증가 및unknown실패발생을실측하고상향필요시선택실험을먼저중단해야한다. 기존baseline config/ledger실측을소급수정하지않는다.
