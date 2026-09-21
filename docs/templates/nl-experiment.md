# 자연어 품질 실험 템플릿

빈 양식과 비교 불가능한 단일 결과는 개선 증거가 아니다. 역할별 ADR을 기준선 전에 채택한다.

## 사전 계약

- experiment ID / 역할: customer | merchant
- 상태 / 담당자 / 독립 평가자 / DBA·domain·UX 검토자:
- CORE·active ADR / context hash / task·branch·base SHA:
- 출시 최소 기준 / 개선 목표 / 회귀 금지 / 의미 있는 개선폭:
- 후보 한도(역할 기본 6, 전체 기본 12) / 연속 무개선 중단(기본 3):
- 표본·반복수·호출/token/비용·시간 budget / 실제 quota:
- 허용 종료 이유: achieved | plateau | budget-stop | rejected-regression | external-blocked

## 데이터·출처·누수 통제

- 시장 조사 revision / goal 실행 시각 / 모든 적용 기능 영역 검증 범위:
- 조사 요약 질문 / URL·`checked_at` / 확인 결과·한계 / decision·시나리오·test ID:
- source-backed 사실·트렌드·표현 / synthetic utterance·persona 구분:
- catalog/seed 출처 이력·license·수집/변환 시각·hash:
- eval manifest/version/hash / label 스키마·annotator·판정 규칙:
- dev / validation / final holdout 규모·범주별 분모·hash:
- 의미·패러프레이즈·상품/intent family group ID와 split 규칙:
- 중복/근접중복/가족 간 누수 검사 명령·결과:
- holdout 접근자 / 노출 여부 / regression 이동·교체 이력:

## 비교 고정값

| 항목 | 기준선 | candidate |
|---|---|---|
| parent / version / content hash |  |  |
| app model / provider / parameters |  |  |
| 프롬프트 / tool 스키마 version |  |  |
| search / alias / embedding config |  |  |
| DB 스키마 / 마이그레이션 / seed |  |  |
| eval set / repeats / clock / mode |  |  |
| run command / run ID / 산출물 |  |  |

## 후보

- candidate ID / 시도 번호 / 현재 최선 버전 ID:
- 실패 case ID·분류 / failure hypothesis / 예상 개선:
- 기존 조사로 설명되지 않는 실패 여부 / 추가 조사 질문·revision·새 scenario/test:
- 변경 범주: 프롬프트 | search | 스키마 | data | model | tool-output
- 단일 변경 / 복합이면 이유·ablation:
- data 변경 출처 이력 / 스키마 마이그레이션·호환·복구·DBA 담당자:
- dev 선별·고정 regression·로컬 도메인 불변식 결과:
- validation paired 비교 / 범주별 numerator·denominator·CI 또는 변동:
- 잘못된 확정·과도한 거절 / 스키마·tool 오류 / P50·P95 / usage·cost:
- 독립 평가자 판정 / 관련 역할 검토 / G1~G4 증거:
- 결정: adopt-best | reject | inconclusive | blocked
- 채택 뒤 최선 버전 ID·version / 이전 best 보존·복구 위치:

## 최종 확인·종료

- 선택 최선 버전 / 기준선 대비 최종 차이:
- 독립 final holdout 결과 / 노출·교체 확인:
- 고객 actual-browser QA / 경영주 actual-browser QA:
- 제출 deployment의 model/prompt/search/schema/data version / G6 증거:
- end reason / 사용 후보 수(고객·경영주·전체) / 연속 무개선 수:
- 알려진 실패 범주·미검증 / 다음 가설·후속 과제:
- 출시 최소 기준 충족 여부 / 필수 gate 상태:

중단 시에도 이전 최선 버전을 유지한다. 예산·plateau·외부 차단은 허구 SKU, 동의·권한·거래 불변식, 출시 최소 기준, 필수 G1~G6를 면제하지 않는다. fixture와 live 결과를 분리한다.

- OpenAI 모델 ID·설정 / 묶음 token usage·사용량 한도·확인 시각:
- 전환 여부·새 비교 조건 / 남은 필수 평가·데모 예비량:
