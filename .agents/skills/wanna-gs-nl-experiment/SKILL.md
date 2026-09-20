---
name: wanna-gs-nl-experiment
description: Run bounded WANNA GS natural-language prompt, search, schema, and data experiments against versioned dev, validation, and holdout sets with independent evaluation. Use to improve customer or merchant interpretation and mapping while preserving the best known release-safe version and mandatory product gates.
---

# 원하GS 자연어 실험

[실험 루프](../../../docs/23-nl-experiment-loop.md), [품질·분할 기준](../../../docs/21-ux-and-natural-language-quality.md), [최신 시장 조사](../../../docs/24-market-research-and-scenario-design.md), [핵심 요구](../../../docs/CORE_REQUIREMENTS.md)을 읽고 [조사 시나리오](../../../docs/templates/research-scenario.md)와 [실험 기록](../../../docs/templates/nl-experiment.md)을 사용한다.

## 시작 계약

기준선 실행 전에 역할별 출시 최소 기준·개선 목표·회귀 금지·의미 있는 개선폭, 데이터/반복수/호출량/후보 한도를 ADR로 채택한다. 기본 한도는 고객·경영주 각각 기준선 이후 후보 6개, 합계 12개이며 같은 역할의 연속 3개 후보가 개선 기준을 못 채우면 조기 중단한다. 결과를 본 뒤 기준을 낮추거나 이름을 바꿔 예산을 다시 시작하지 않는다.

goal 실행 시 모든 적용 기능 영역에 대해 최신 조사를 수행해 현실적인 사용자 필요·최근 트렌드·표현·상품 관심을 실패 시나리오와 평가 사례로 만든다. 몇 개의 고정 예시로 전체 영역을 대신하지 않는다. 조사 요약의 질문·출처·`checked_at`·결과·연결한 결정/테스트 ID를 남기고, source-backed 사실/발화와 연구자가 만든 synthetic utterance/persona를 구분한다. 새 실패가 기존 근거로 설명되지 않으면 해당 실패 범위를 대상으로 새 조사를 수행하고 데이터·가설 버전을 갱신한다. 외부 사례를 앱 성능 증거로 쓰지 않는다.

dev/validation/final holdout은 의미·패러프레이즈·상품/의도 가족 단위로 묶어 분할하고 manifest/hash를 고정한다. holdout 정답·표현을 prompt/few-shot/별칭/검색 데이터에 복사하지 않는다. 노출된 holdout은 regression으로 이동하고 독립 holdout으로 교체해 이력을 남긴다.

## 반복

1. 동일 데이터·모드·모델 설정에서 현재 최선 버전 기준선의 검색, intent/fields, 대화, 불변식, 지연·사용량을 측정한다.
2. 실패를 검색 누락, 오분류, 미확인 모호함, 맥락 손실, 스키마 위반, 도구 오류, 사실/데이터 결함으로 분해하고 구체적인 실패 집합과 개선 가설을 세운다.
3. prompt/search/schema/data 중 가능한 한 한 요인만 바꾼 후보를 격리한다. 복합 변경은 이유와 ablation을 기록한다. schema/data 변경은 출처 이력과 DBA 단일 작성자, 마이그레이션·호환·복구·영향 검사를 포함한다.
4. dev 표본·고정 regression·서버 불변식으로 빠르게 거른 뒤 통과 후보만 동일 validation 사례·반복수·설정에서 기준선과 paired 비교한다.
5. 실험자와 다른 평가자가 정답·분모·범주별 회귀·잘못된 확정/과도한 거절·지연/사용량을 판정한다. 후보 작성자는 자기 후보를 승인하지 않는다.
6. 사전 기준을 만족하고 중대한 회귀가 없는 후보만 관련 역할 검토와 G1~G4를 거쳐 최선 버전으로 승격한다. 실패 후보도 버전·가설·결과·기각 이유를 보존한다. 다음 후보는 항상 현재 최선 버전과 비교한다.
7. 최종 선정 후보에 final holdout과 고객/경영주 각각의 실제 브라우저 QA를 수행한다. holdout에 노출된 뒤 다시 튜닝하는 경우에만 독립 holdout으로 교체하고 이력을 남긴다. G6에서 제출 deployment의 실제 model/prompt/search/schema/data 버전을 확인한다.

개선 목표 달성, plateau, 예산 소진, 회귀 기각, 외부 차단을 구분해 종료한다. 추가 최적화는 선택적으로 중단할 수 있고 그때도 이전 최선 버전을 유지한다. 허구 SKU, 동의·권한·수량·금액 위반, 출시 최소 기준 미달, 필수 G1~G6는 중단이나 예산 소진으로 면제할 수 없다. fixture 결과를 live 품질로 바꾸지 않으며 유료 구매나 한도 확장은 별도 권한 없이 실행하지 않는다.

## 제공자별 예산

[25번](../../../docs/25-model-budget-and-fallback.md)에 따라 평가 묶음 전후 잔량과 최종 검증·데모 예비량을 확인한다. Gateway가 부족하면 검증한 Gemini 직접 호출로 전환한다. 제공자가 바뀐 결과는 분리하고 같은 데이터·조건에서 다시 평가한다. 모델 전환으로 후보 한도를 초기화하거나 기존 모델의 PASS를 재사용하지 않는다.
