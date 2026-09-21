# ADR-007 — 실패를 보존하는 UX 비교 측정 재설계

- status: adopted; 기구 구현·독립 검증 및 새 실제 실행 전
- authority: user-delegated; D-46 사용자 직접 승인에 따른 세부 절차 위임. 사용자 승인 범위를 벗어난 최종 품질 완화 금지.
- proposer: root, 2026-09-21
- depends_on: D-46, ADR003, ADR006, CORE17/18/21/25, docs21/23/27
- supersedes: 새 UX-v3 연구에 한해서 ADR003의 arm별3반복 및 ADR006의 추가 실행 금지/비교용 baseline 전체24PASS 요건. 과거 결과/판정은 대체하지 않음.
- policy_keys: ux.comparison_protocol_v3; conflicts_with: 기존 규칙과의 변경을 아래에 명시
- purpose: 최종 고객·경영주 정상 성공과 편의성을 보존하면서, 이미 품질이 나쁜 기준선을 개선 비교의 대상으로 측정한다. 실패한 기준선을 정상 제품으로 승인하지 않는다.

## 왜 변경하는가

B0 두 실행은2/24와11/24 성공으로 중단됐다. 기존 모든-baseline-성공 조건은 실패가 있던 기준선을 비교 대상으로도 완료할 수 없게 했다. 원본48의13PASS/2FAIL/33미실행과 전체 비교 NOT_READY는 영구 보존한다. 사용자 D-46 승인 후 새 절차를 **새 결과를 보기 전에** 정하고 두 독립 검토한다. 기준선 실패를 숨기거나 빠른 성공만 선택하지 않는다.

## 한 번의 사전 고정 비교 연구

1. ID `ux-study-v3-01`, baseline run `ux-baseline-b0-v3-01`, best run `ux-best-v3-01`을 사전 지정한다. 추가 자동 재실행/성공 조각 합치기/중도 반복수 변경은 금지한다.
2. 기존 동일8 workload·같은 선택상품·seed·clock·viewport를 각각 **7회**, arm당56회 실행한다. B0 원본 source/model/prompt와 최종 NL 통과 후 동결한 best를 비교한다. 두 arm 모두 같은 v3 기구/순서/준비 방식이다. 모델 재시도0, 사례별 새 독립 브라우저/SQLite 상태를 쓴다.
3. 알려진 사용량이 있는 모델 응답 실패나 해당 trial의 UI/SQL 단정 실패는 그 trial FAIL로 기록하고 다음 사전 계획 trial을 수행한다. 중단된 trial의 남은 단계/모델 호출은 NOT_RUN으로 남긴다. 실패를 재시도하거나 성공으로 바꾸지 않는다. 두 arm에 같은 규칙을 적용한다.
4. 미확정 provider/usage·pending/장부쓰기 불확실·auth/quota·모델/프롬프트/카탈로그/소스/비밀전달 계약 불일치·비용/호출 한도는 전체 연구 중단이다. 새로운 run ID로 우회하지 않는다. 비교 READY의 선행조건은 두 arm 모두 전체연구 stopCode=null, pending0, 실제 시도 trial56개, trial-level NOT_RUN0이다. 충분한 성공 수나 다른 arm의 성공 여부와 무관하게 전체연구 STOP은 항상 비교 NOT_READY가 우선한다. 기록 행56개만으로 실제 시도를 대신하지 않는다. 알려진 실패 trial 내부의 후속 단계 NOT_RUN은 실패의 일부로 보존하되 trial 자체를 미시도와 혼동하지 않는다.
5. 정상 고정 흐름은 arm당42모델 호출(명확3×7=21, 모호2×7=14, 자동정책7), 두 arm 최대84회다. UI/SQL trial 실패로 이후 호출이 줄면 미실행을 남긴다. goal 단일 Budget50 장부·전체2400회·사용자 승인$20·unknown$.05·남은 필수 평가/QA/G6 예약은 유지한다. 신규 candidate의 UX 예약은96회로 보수 설정한다(84모델 계획+12여유이며 추가실행 허가가 아님).

## 판정: 최종 제품 기준은 유지·강화

- **best는56/56 최초 시도 정상 PASS, 필수/의미/SQL 오류0이어야 한다.** 알려진 오류 뒤 나머지를 진단용으로 실행해도 실패를 지우지 않는다. 고객 결정≤7·질문≤2, 경영주10SKU 검토1화면/승인1회, 자동정책 건별승인0/중복0, 모든 동의/수량/가격/48시간 조건은 유지한다.
- baseline의 모든56 planned/attempted/PASS/FAIL/NOT_RUN·응답실패·모델/비용을 공개한다. baseline는 비교 대상이지 release 후보가 아니므로 일부 실패를 baseline 품질 PASS로 쓰지 않는다.
- 각8 workload에서 baseline의 **정상 완료가 최소3개** 있어야 편의성 비교가 가능하다. 없으면 전체 비교 NOT_READY이며 자동 추가 실행하지 않는다. 실패/누락 실행을 시간0이나 임의 큰 시간으로 바꾸지 않는다.
- 완료한 정상 경로의 조건부 편의성을 비교한다: baseline과best 각각 **모든 정상 완료 trial**의 최대 필수 조작/화면 이동과 비모델 완료시간 중앙값을 사용한다. 빠른/느린 일부 선택이나 첫3개만 선택은 금지한다. 성공수(3~7 대7)·실패수·시도 전체 분모를 지표 옆에 항상 표시한다. 이는 전체 입력의 무조건 완료시간 또는 인간의 사고시간 측정이 아니다.
- best 최대 조작/이동은 baseline 이하, 비모델 시간 중앙값은 baseline의110% 이하여야 한다. 모델 HTTP/네트워크·계측 Budget 대기는 따로 보고하며 원래 시간 분리 방식을 유지한다. 실제SQL correctness/필수정보/정상성공 우선, 안전 확인을 삭제하여 조작 수를 줄이지 않는다.
- 이 설계는 실패를 포함한 baseline 품질과, 성공적으로 완료한 동일 정상 경로의 편의성을 분리해 정직하게 비교한다. 정확도 개선은 독립 NL336/validation84×2/holdout84 기준으로 별도 평가한다. baseline 실패 때문에 best 성능을 무조건 우수하다고 가정하지 않는다.

## 출처·기구·과거 이력

원래 B0 source10c00723d0b64ea47a06dcbd00e2b671e7c62daf와 model gpt-5-mini-2025-08-07/prompt baseline-v1을 별도 보존 worktree에서 build한다. best는 source/model/prompt/catalog/schema/runtime를 동결한다. UI/domain/seed 일치와 차이를 실행 전에 확인한다. 동일 기구의 app-root(각 앱)와 budget-root(공유 goal 장부)를 분리하여 옛 앱 코드가 새 장부 상한을 임의로 바꾸지 않게 한다.

v2 원본 기구/결과는 그대로 남긴다. 새 v3 source/hash·고정 plan·출력 schema·metrics·release checker 변경에 정상/반례 시험과 별도 독립 검토를 요구한다. 구현자가 자체 시험을 독립 검증으로 세지 않는다. 기존 장부/실패/SDK 오류/소스 stale·0/skip·분모 누락의 fail-closed 검사는 유지한다.

새 release 증거는 옛 두 baseline 결과/해시/분모와 새 두 arm 결과를 함께 요구한다. 옛48과 새112의 총 계획160(기준선104, best56)을 명확히 분리한다. 옛 미실행을 새 성공으로 소급 대체하지 않는다. 최종 두 역할 live QA·정책/운영 감사·G5/G6는 별개 필수다.

## 검토·채택

동일 최종 초안 SHA `7334ff761f47b697518051b771df85a2a6c57ffb024647596daa6d013b890e72`에 제품/UX research와 측정/상태 method_auditor가 별도로 채택 동의했다. [제품 검토](../execution/run-20260921/adr007-product-review.md)·[상태 검토](../execution/run-20260921/adr007-state-review.md). 조정자 root가 2026-09-21 위임 채택한다. 채택 메타데이터 외 검토된 절차는 변경하지 않았다. 구현·실행기 독립 검증을 별도로 요구하며 이 문서만으로 v3 실제 실행을 허가하지 않는다.
