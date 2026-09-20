# 조사·시나리오 기록 템플릿

빈 양식이나 URL 목록은 조사 완료 증거가 아니다. 출처 사실, 미확인 범위, 설계용 합성 확장을 분리하고 독립 검토한다.

## 메타데이터

- brief/task ID / 담당자 / independent reviewer:
- 관련 CORE / AC / ADR / 기능 경계:
- 상태: draft | independently_reviewed | adopted | refresh_required | rejected
- 조사 시작·종료일 / freshness 필요 사유:
- research/catalog/scenario/eval/seed/policy 버전:
- source checksum / split hash / consumed context hash:

## 기능별 조사 요약

- 답할 구체적 질문:
- 고객/경영주/시장·트렌드/UX/공식 기술 중 적용 축:
- 필요한 source 종류와 우선순위:
- 범위 밖이며 되살리지 않을 기능:
- 준비 상태 조건 / 시간·source 한도 / 실패 시 refresh 조건:

## source records

source마다 반복한다.

- source_id:
- URL / title / publisher:
- source_type: official_product | official_store | official_technical | manufacturer | reporting | study | other
- published_at / event_period / checked_at:
- evidence_scope:
- 확인한 사실의 자체 문장 요약:
- 직접 인용 여부·위치·사용 근거:
- limitations / source가 말하지 않는 내용:

## 조사 사례

- research_case_id:
- need_statement:
- observed_friction:
- source_ids와 사실별 연결:
- product_evidence / product_confidence: high | medium | low | unverified
- trend_evidence·기간·시장 범위 / trend_confidence: high | medium | low | unverified
- unknowns / 반례 / 추가 확인 조건:
- privacy_and_quote: 실제 사람 데이터 없음 | 자체 요약 | 허용된 직접 인용 | synthetic_expansion
- review_status / reviewer 판단:

## 근거에서 구현까지 매핑

| evidence/source | design decision·UX copy | catalog/data field | scenario/test | confidence·미확인 |
|---|---|---|---|---|
|  |  |  |  |  |

## 상품 목록 candidate

- catalog_candidate_id / field_origin:
- 이름·브랜드·맛·용량 등 확인된 필드:
- 합성 필드와 표시:
- 실제 점포 사실과 구분할 simulated 가격/availability/재고/공급:
- 채택/기각 상태와 이유:

## 시나리오

- scenario_id / scenario_family_id:
- research_case_ids / catalog_refs / store_refs:
- status: verified_design | hypothetical_unverified | rejected
- roles와 합성 actor ID:
- simulated_preconditions / clock:
- user_goal / friction / entry_state:
- steps:
- allowed_outcomes / forbidden_outcomes:
- DB/event/UI oracle:
- gate_usage: G1 | G2 | G3 | G4 | G5 | G6
- scenario_version / 영향받는 기존 증거:

## eval cases

case마다 반복한다. source에서 새로 확장한 발화는 기사나 실제 고객 인용이 아니라 `synthetic_expansion`으로 표시한다.

- eval_case_id / eval_family_id / scenario_id:
- role / utterance / utterance_origin:
- expected_behavior / allowed_answer_set / forbidden_action:
- scoring / deterministic invariant:
- split_group_id / split: dev | validation | final_holdout
- paraphrase·오타·번역 family 구성원:
- eval_version:

## 분할·holdout 보호

- 의미/패러프레이즈 family 그룹 검사 결과:
- dev/validation/final holdout 범주별 분모:
- holdout curator / 실험자·구현자와 분리 근거:
- 접근·노출 이력 / 오염 시 regression 이동·대체 이력:
- 모든 자연어 검증 범위를 보장하지 않는 미검증 범위:

## 독립 검토와 준비 상태

- source 품질·날짜·product/trend confidence 검토:
- 가상 인물·허구 인용·실제 재고/인기 과장 검사:
- 조사 사례→catalog/scenario→eval 출처·변경 이력 검사:
- 설계·데이터·테스트 매핑 누락:
- 준비 판정: ready | ready_with_hypotheses | refresh_required | rejected
- 잔여 가설 / 구현 중 failure-trigger refresh 조건:
