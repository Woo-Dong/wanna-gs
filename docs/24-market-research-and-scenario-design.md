# 시장 조사에서 시나리오·평가까지

최초 구현 기준 · 상태: 조사 계획. 현재는 아래 예시 한 건의 출처를 확인했다. 시장 조사·상품 200개·시나리오·평가셋은 `/goal` 실행 시 최신 자료를 조사하고 독립 검토한 뒤 만든다. ‘민음사 빵’은 조사 방법의 예시로 사용한다.

## 목적과 경계

상품을 찾거나 기다리는 고객의 어려움, 경영주의 수요 집계·발주·예외 처리 부담을 조사한다. 실제 관찰·보도와 당시 상품·시장·트렌드 자료를 근거로 사례를 만들고, 상품 후보와 실행·평가 시나리오를 도출한다. 각 사례가 어떤 기능과 테스트에 쓰이는지 기록한다.

조사는 현재 제품 범위를 더하는 권한이 아니다. 본부 기능, 실제 결제·GS 연동, 사진·링크·레시피 입력을 조사에서 발견해도 이번 구현에 되살리지 않는다. 실제 GS 서비스의 기능·정책은 공식 근거로 확인하기 전 문제 가설이며, 데모 가격·재고·공급·발주·거래는 simulated다.

## 언제 무엇을 조사하는가

### 초기 조사 단계

PLAN-READY 전에 실제 자료를 읽어 여러 조사 사례·brief와 근거→설계/테스트 매핑을 구성하고 독립 검토한다. 질문/URL 목록만으로 조사를 완료하지 않는다. 전체 ~200개 상품/8~12개 점포 자료의 전수 확보는 후속 데이터 구축에서 마치며, 초기에는 표본 근거·접근 가능성·위험·확대 계획으로 다음 축을 확인한다.

| 축 | 질문 예시 | 설계·데이터·테스트로 연결할 것 |
|---|---|---|
| 고객 필요·검색 | 어떤 표현으로 상품을 찾고, 이름/맛/용량/별칭에서 무엇이 헷갈리는가 | 상품 목록 속성·별칭 후보, 명확/모호/미식별 시나리오, 검색 unit/eval |
| 재고·요청·대기 | 앱/현장 정보 차이, 여러 점포 탐색, 품절·입고 시각, 대기 중 기대가 어떻게 어긋나는가 | 실제 점포+simulated availability, 상태/오류 카피, 통합·UX 시나리오 |
| 동의·결제·픽업 | 상품/점포/가격 확인, 확보 후 결제, 알림·48시간 수령에서 필요한 설명은 무엇인가 | 동의/상태 불변식, 시간 경계, 고객 E2E |
| 경영주 집계·발주 | 요청을 어떻게 묶고 예산·최소수량·공급 제한을 판단하는가 | 묶음/자연어 수정/수동·자동 정책, merchant eval |
| 경영주 예외 | stale 제안, 부분 실패, 재입고·중복 실행·미수령을 어떻게 이해해야 하는가 | 실패/복구 시나리오, 단일 탭 중복 명령·순차 처리 통합 검사, merchant UX |
| 시장·트렌드 | 어떤 상품이 언제·어떤 근거로 관심을 받았고, 상품 사실과 인기 주장을 구분할 수 있는가 | trend tag, 희소 시나리오, product/trend confidence |
| UX·접근성 | 모바일 고객과 데스크톱 경영주가 다음 행동을 찾기 어려운 지점은 무엇인가 | 빈/로딩/오류/복구 상태, 키보드·반응형 QA |

위 필요와 위험 분포에 맞춰 상품 구성을 정한다. 조사된 상품만으로 다양성·경계 사례가 부족하면 합성 확장을 추가할 수 있지만 `synthetic_expansion` 또는 `synthetic_product`로 표시하고 실제 인기·실제 발화라고 하지 않는다.

### 기능별 G0의 적시 조사

초기 조사만으로 모든 세부 설계를 고정하지 않는다. 각 기능 담당자는 G0에서 기능별 조사 요약을 작성한다. 고객 검색 담당자는 상품 식별·질문 방식을, 경영주 담당자는 집계·발주·예외를, UX 담당자는 상태 이해·회복을, DB/배포/model 담당자는 해당 시점의 공식 기술 문서를 확인한다. 기술 조사는 현재 CORE 범위를 구현·검증하는 데 필요한 내용만 다루며 조사 결과로 제품 범위를 확장하지 않는다.

실패가 오래된 상품/트렌드 가정, 누락된 사용자 어려움, 바뀐 공식 API/제한에서 비롯됐다는 증거가 있으면 관련 조사 사례와 파생 시나리오를 갱신한다. 모든 기능에서 인터넷 전체를 다시 훑거나 ‘가장 최신’임을 무한히 증명하지 않는다.

## 기능별 조사 요약

각 brief는 구현 전에 다음을 고정하고 [research-scenario 양식](templates/research-scenario.md)으로 결과를 남긴다.

1. 관련 CORE/AC·기능 경계와 이번 조사로 답할 구체적 질문.
2. 필요한 source 종류와 우선순위: 공식 상품/점포/제조사·공식 기술 문서, 신뢰할 수 있는 보도/조사, 제한적으로 보조 자료.
3. 발행일·사건/관찰 기간·확인일과 freshness가 중요한 이유.
4. 관찰한 사실, 출처가 말하지 않는 범위, 상품 사실과 트렌드 주장의 별도 confidence.
5. `evidence → design decision → catalog/data field → scenario → test/UX copy` 매핑.
6. 낮은 근거의 가설·반례·추가 확인 조건과 독립 reviewer.
7. 준비 상태 판단과 버전 변경 영향.

검색 결과 제목, SEO 블로그, 판매 페이지 한 곳만으로 실제 인기·재고·사용자 행동을 확정하지 않는다. 낮은 근거도 가설로는 보존할 수 있지만 `low`/`unverified`로 표시하고 독립 검토하며 빈칸을 사람·인용·판매량으로 채우지 않는다.

## source와 confidence

### source record

| 필드 | 내용 |
|---|---|
| `source_id` | 안정적인 내부 ID |
| `url`, `title`, `publisher` | 원문 식별자. 검색 결과 URL 대신 직접 확인한 페이지 |
| `source_type` | official_product / official_store / official_technical / manufacturer / reporting / study / other |
| `published_at`, `event_period`, `checked_at` | 발표·관찰 시점과 확인일을 구분 |
| `evidence_excerpt_summary` | 필요한 사실만 자체 문장으로 요약. 직접 인용이면 별도 표시와 위치 기록 |
| `evidence_scope` | product_identity / user_need / search / stock / trend / store / technical 등 |
| `limitations` | 표본·지역·기간·2차 보도·동적 페이지 등 확인하지 못한 범위 |

### 조사 사례

| 필드 | 내용 |
|---|---|
| `research_case_id` | `RC-*`; source 묶음에서 도출한 문제/필요 단위 |
| `need_statement` | 출처 범위 안의 사용자/업무 필요를 요약. 가상 인물 서사 금지 |
| `observed_friction[]` | 검색·재고·대기·픽업·집계·발주·예외 등의 관찰 |
| `source_ids[]` | 근거 source record. 각 사실이 어느 source에 기대는지 연결 |
| `product_evidence[]` | 상품명·구성·출시·속성 사실과 `product_confidence` |
| `trend_evidence[]` | 관심·품절·검색량·판매 주장, 기간/시장 범위와 `trend_confidence` |
| `unknowns[]` | 실제 재고·전국 인기·현재 판매 등 확인하지 못한 내용 |
| `privacy_and_quote` | 개인 정보 사용 여부, 실제 인용/자체 요약/합성 확장 구분 |
| `derived_candidate_ids[]` | catalog/scenario/eval family 후보와 파생 이유 |
| `review_status` | draft / independently_reviewed / rejected / refresh_required |

`product_confidence`와 `trend_confidence`는 독립적으로 `high / medium / low / unverified`를 쓴다. 공식 상품 정보가 있어 product는 high여도 전국 인기 주장은 unverified일 수 있다. `high`여도 현재 점포 재고는 별도로 확인해야 한다.

## 조사 사례에서 시나리오와 eval로

세 산출물을 분리하고 다음 출처·변경 이력만 연결한다.

```text
source_id(s)
  → research_case_id
    → catalog_candidate_id(s)
    → scenario_family_id → scenario_id(s)
      → eval_family_id → eval_case_id(s)
```

### 시나리오 스키마

| 필드 | 내용 |
|---|---|
| `scenario_id`, `scenario_family_id` | 실행 fixture/여정과 의미상 family ID |
| `research_case_ids[]` | 어떤 근거/가설에서 파생했는지 |
| `status` | verified_design / hypothetical_unverified / rejected |
| `roles` | customer / merchant / 두 역할. 합성 actor ID만 사용 |
| `catalog_refs`, `store_refs` | 정확히 확인할 SKU 후보와 공개 점포 ID |
| `simulated_preconditions` | availability·가격·재고·공급·clock. 실제 사실과 구분 |
| `user_goal`, `friction`, `entry_state` | 사용자가 달성하려는 일과 어려움 |
| `steps` | UI/API를 건너뛰지 않는 주요 행동 |
| `allowed_outcomes`, `forbidden_outcomes` | 후보 확인/질문/거절/실행과 가짜 SKU·재고 보장 등의 금지 결과 |
| `oracle` | DB/event/UI에서 판정할 상태·수량·권한·문구 의미 |
| `gate_usage` | G1 unit, G2/G3 integration, G4 UX, G5/G6 eval 중 적용 위치 |
| `scenario_version` | 변경 시 영향받는 증거를 stale 처리할 버전 |

### eval case 스키마와 분할

eval case는 `eval_case_id`, `eval_family_id`, `scenario_id`, `role`, `utterance`, `utterance_origin`, `expected_behavior`, `allowed_answer_set`, `forbidden_action`, `scoring`, `split_group_id`, `split`, `eval_version`을 가진다. 연구를 보고 새로 만든 문장은 항상 `utterance_origin: synthetic_expansion`이며 실제 고객·점주의 말이나 기사 인용이 아니다.

같은 필요·의도·상품/상태 조합의 말투/오타/번역/축약은 같은 `split_group_id`로 묶어 dev/validation/final holdout 중 하나에만 둔다. nl-evaluator는 실험자와 기능 구현자에게 노출되지 않은 family로 final holdout을 독립 큐레이션하고 접근·노출·교체 이력을 관리한다. research taxonomy를 공유하는 것은 허용하지만 dev 문장의 패러프레이즈를 holdout으로 가장하지 않는다.

## 버전과 게이트 재사용

manifest는 `research_version`, `catalog_version`, `scenario_version`, `eval_version`, seed/policy/prompt/model/context 버전, source checksum, split hash를 함께 기록한다. G1은 dev unit case, G2/G3은 같은 시나리오 상태의 실제 DB/서비스 경계, G4는 대표 합성 발화와 브라우저 여정, G5는 전체 regression/validation과 보호 holdout, G6는 선정 버전의 대표 live 사례를 사용한다. final holdout의 정확한 발화를 이전 게이트에서 재사용하지 않는다.

자료가 바뀌면 모든 결과를 무조건 폐기하지 않고 출처·변경 이력으로 영향을 계산한다. 상품 식별 사실 변경은 관련 catalog/search/eval, 시나리오 상태 변경은 관련 integration/UX, split/holdout 변경은 자연어 기준선과 후보 비교를 stale 처리한다.

## 조사 준비 상태와 중단

초기 조사 단계는 다음을 만족하면 구현 준비가 된다.

- 위 고객·경영주·시장·UX 축마다 최소 하나 이상의 신뢰 가능한 근거 또는 명시적 low/unverified 가설과 보완 계획이 있다.
- 200개 이상 상품 목록을 만들 source 계획과 합성 보완 규칙, 8~12개 실제 점포 확인 계획, 희소 simulated availability 규칙이 있다.
- 각 주요 조사 사례가 설계/데이터/scenario/test로 연결되고 product/trend confidence와 미확인 범위가 기록됐다.
- data reviewer와 nl-evaluator가 source 품질, 출처·변경 이력, 분할/holdout 계획을 독립 검토했다.
- 당시 날짜 기준으로 기능 결정에 필요한 공식 기술 자료를 담당자가 확인했다.

필요한 조사 범위와 출처 품질을 충족하고 추가 탐색이 설계 결정을 바꾸지 않으면 초기 조사를 마친다. 낮은 근거는 성공으로 꾸미지 않고 가설로 남긴다. 자연어 실험의 후보/정체/종료는 [23번](23-nl-experiment-loop.md)의 한도를 따른다.

## 출처 확인 예시: 민음사 빵

`RC-EX-001`은 출처를 확인한 예시이며 전체 시장 조사 완료나 고정 seed 채택을 뜻하지 않는다.

- [머니투데이, 2026-09-08](https://www.mt.co.kr/amp/society/2026/09/08/2026090709475845306), 2026-09-20 원문 확인: 보도된 구매 경험에는 여러 매장 방문, 입고 시각 확인, 앱 표시와 현장 재고 차이, 무작위 책갈피 수집이 포함된다.
- [이투데이, 2026-08-26](https://www.etoday.co.kr/news/view/2618139), 2026-09-20 원문 확인: 4종 문학 빵의 명칭·맛, 재고를 찾아다니는 행동, 빠른 품절, 무작위 책갈피 구성을 보도한다.
- `need_statement`: 특정 협업 상품을 정확히 찾고 가까운 점포의 확보 가능성을 알고 싶지만, 상품/동봉품 이름의 중의성·빠른 품절·표시와 현장 차이 때문에 여러 점포와 입고 시점을 확인하는 수고가 생길 수 있다.
- `product_confidence: medium`: 두 직접 확인 기사에서 상품군과 구성을 교차 확인했다. seed 편입 시 공식 GS25/제조사 상품 정보로 정확한 SKU명·용량·현재 판매 여부를 다시 확인한다.
- `trend_confidence: low`: 제한된 기간의 빠른 품절과 탐색 행동은 보도됐지만 전국 수요·현재 인기·판매량을 증명하지 않는다.
- `unknowns`: 현재 판매, 특정 점포 취급/재고, 앱 재고 정확도 일반화, 원하는 책갈피 선택 가능성. 실제 재고나 특정 증정품을 보장하지 않는다.
- `privacy_and_quote`: 개인 이름·프로필·직접 인용을 dataset에 옮기지 않는다. 아래 발화는 모두 새로 쓴 합성 문장이다.

## 파생 예시 2건: 가설·미검증

아래는 스키마를 보여 주는 hypothetical_unverified 시나리오다. 앱에서 실행·검증되지 않았고 최종 catalog/평가셋에 채택되지 않았다. 두 발화는 기사 인용이 아닌 `synthetic_expansion`이다.

### SC-EX-CUSTOMER-001

- status: `hypothetical_unverified`
- lineage: `RC-EX-001 → CC-EX-PRIDE-BREAD → SF-EX-NAME-BONUS → EF-EX-CUSTOMER-CLARIFY`
- 합성 발화: “오만과 편견 있나요? 책갈피도 오만과 편견으로 받고 싶어요.”
- friction: 같은 작품명이 빵 SKU와 무작위 동봉 책갈피를 함께 가리킬 수 있다.
- expected: 상품 목록에서 정확한 빵 SKU 후보를 확인시키고, 책갈피는 무작위라 특정 디자인을 보장할 수 없음을 설명한다. SKU가 아직 검증되지 않았으면 임의 ID로 요청을 만들지 않는다.
- forbidden: 특정 점포 실제 재고, 원하는 책갈피, 전국 인기나 재입고 시각 보장.
- gate usage: 검색 unit, 미식별/확인 integration, 고객 모바일 UX, 별도 family의 자연어 eval.

### SC-EX-MERCHANT-001

- status: `hypothetical_unverified`
- lineage: `RC-EX-001 → SF-EX-SCARCE-TREND → EF-EX-MERCHANT-SCOPE`
- 합성 발화: “문학 빵 찾는 사람이 많다니까 들어오는 대로 전부 자동 발주해.”
- friction: 관심 신호를 무제한 발주 권한, 실제 공급 가능성, 모든 점포 수요로 오해할 수 있다.
- expected: 현재 데모 session·해당 경영주 점포의 유효 미확보 수요, 예산·최소수량·simulated 공급 조건과 ‘이번만/앞으로’를 확인한다. 요청 수량을 넘는 자동발주나 근거 없는 실제 인기/재고 주장을 실행하지 않는다.
- forbidden: 기사만으로 전국 수요 확정, 타 점포 변경, 무제한 자동발주, 실제 공급 보장.
- gate usage: merchant parser unit, 예산/로컬 역할/중복 명령 integration, 경영주 UX, 별도 family의 자연어 eval.

이 예시는 `/goal` 당시 새 조사에서 더 적절한 상품/문제가 발견되면 교체할 수 있다. 교체할 때는 출처와 변경 이력을 남기며 ‘최신 유행 하나’로 전체 dataset을 편향시키지 않는다.

## 공통 참고 출발점

공식 GS25·GS리테일·제조사·점포 자료와 공식 기술 문서의 출발점·제약은 [11번 조사 근거](11-research-and-references.md)와 [19번 데이터 명세](19-data-research-and-seeding.md)를 사용한다. source가 동적이거나 현재 본문을 확인하지 못하면 URL 존재만으로 상품/점포 사실을 확인했다고 기록하지 않는다.

## 화면 예시와 가치 검증 데이터

D-36의 공개 입력 예시는 [26번](26-design-and-brand-guide.md)에 연결한다. 실행 당시 조사 소재에서 활성 카탈로그로 확인 가능한 예시를 고르고 출처/확인일·research_case_id·상품/시나리오 연결을 기록한다. 과거 기사를 현재 인기 순위로 표현하지 않는다. 공개 예시·패러프레이즈 family는 dev/demo에 두고 보호 holdout과 분리한다.

D-37·[27번](27-service-values-and-guardrails.md)의 미취급/품절/공급제한/unknown/시스템 오류, 적절한 대체/대안 없음/고객 거절, 묶음 중복/정책 해제/중복 발주 사례도 seed·시나리오에 포함한다. 관심·추천과 구매 확약, 추정 속성과 확인 속성을 구분한다.
