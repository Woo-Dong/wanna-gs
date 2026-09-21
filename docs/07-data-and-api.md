# 데이터 모델과 API 계약 초안

논리 모델이다. 테이블·필드·URL의 최종 이름은 구현에서 일관되게 조정할 수 있다. 의미·업무 불변 조건은 유지한다.

## 공통

- 식별자: UUID 또는 충돌 없는 서버 생성 ID.
- 금액: 원 단위 정수. 수량: 양의 정수.
- 시간: UTC `timestamptz`, 화면 표시는 Asia/Seoul.
- 변경 레코드: `created_at`, `updated_at`, 필요한 경우 `version`.
- 거래 데이터: `demo_session_id`. 쿼리·쓰기·초기화 모두 범위를 검증한다.
- 중복 방지 키는 사용자/세션/동작 범위로 고유하게 한다. 같은 키에 다른 요청 본문을 보내면 오류로 처리한다.

## 논리 데이터 묶음

| 모델 | 주요 필드 | 비고 |
|---|---|---|
| `products` | code, name, aliases, category, brand, flavor, size, description, source_type, source_url | 가상/웹 참고 출처 구분 |
| `stores` | name, location_label, latitude, longitude, coordinate_source, accuracy, 출처 이력 | 실제 점포·좌표 확인, 거래/재고는 모의 |
| `store_product_conditions` | store_id, product_id, price_krw, minimum_order_qty, order_multiple, available_order_qty, supply_status, assortment_status, stock_qty, observation_status, observed_at, reason, version | 시뮬레이션 조건임을 표시 |
| `demo_sessions` | seed_version, clock_offset, status | 고객·경영주가 공유할 시연 단위 |
| `demo_actors` | session_id, role, store_id, display_name | 서버가 역할·범위를 확인 |
| `purchase_requests` | actor_id, product_id, store_id, quantity, accepted_price_krw, consent_version, consent_at, sequence, status, pending_reason | 배정·발주된 수량은 별도 연결과 정합성 유지 |
| `unidentified_requests` | original_text, dialogue, extracted_clues, candidate_ids, reason, store_id | 본부용 기능은 만들지 않음 |
| `order_policies` | store_id, enabled, categories, budget_krw, budget_period, allow_extra_quantity=false, approved_by, version | 기간·초기값 O-08 |
| `order_proposals` | constraints, source_snapshot_version, summary, status, version | 모델 설명과 계산 결과 분리 |
| `orders` / `order_lines` | approval_type, policy_version, product_id, ordered_qty, confirmed_qty, received_qty, cost_krw, status | approval_type: manual/policy |
| `request_order_links` | request_id, order_line_id, committed_qty | 진행 중 발주에 수요가 중복 포함되는 것 방지 |
| `allocations` | request_id, order_line_id, quantity, status | FIFO·확보량 검사 |
| `reservations` | allocation_id, total_krw, status, pickup_available_at, pickup_deadline_at, collected_at | 시작·마감 재설정 금지 |
| `mock_payments` | reservation_id, status, amount_krw, attempt_key | 실제 결제수단 저장 안 함 |
| `notifications` | actor_id, event_id, type, body, created_at, read_at | 앱 내 생성은 실제 푸시 전달과 다름 |
| `agent_runs` | role, mode, model_id, input_ref, tool_results, output, status, usage, latency, error | 비밀값·내부 추론 전문 제외 |
| `events` | event_key, entity_type, entity_id, actor_type, previous_state, next_state, reason | 상태·중복·인계 증거 |
| `product_embeddings` | product_id, model_id, dimensions, text_hash, vector, generated_at | 선택 실험 |

경영주 고객 상세 조회는 새 생명주기 테이블을 만들지 않고 `demo_actors` → `purchase_requests` → `request_order_links` → `allocations` → `mock_payments`/`reservations`의 기존 연결을 읽는다. `actor_id`는 데모 세션 안에서만 유효하며 실제 개인정보를 뜻하지 않는다.

발주 비용과 고객 판매 가격은 원래 다른 개념이다. 테스트 데이터에도 명시적으로 구분할지 결정하고, 발주 예산 계산에 판매가를 조용히 대신 사용하지 않는다. 초기 단순화가 필요하면 사용한 가격 기준을 UI·seed에 명시한다.

## 제약과 인덱스

- 상품코드 고유, 점포-상품 조건 고유.
- 수량·금액의 유효 범위 CHECK, 상태 enum 또는 검증된 문자열.
- 세션/점포/상품/접수 순서의 대기열 조회 인덱스.
- 주문·결제·알림 이벤트 고유 키로 재실행 안전성 확보.
- 공급 확정량 초과 배정과 동시 예산 초과는 트랜잭션/조건부 갱신으로 방지.
- 다른 세션의 외래 키를 연결하지 않도록 서버 및 데이터 제약을 설계.
- 상태만 `expired`로 바뀌길 기다리지 말고 마감 시각을 직접 조회.

## API 경계

모든 URL은 제안이다. 요청의 세션·사용자·점포 범위를 서버에서 검증한다. DB 자격증명을 브라우저에 전달하지 않는다.

| API | 역할 | 주요 처리 |
|---|---|---|
| `POST /api/demo/sessions` | 데모 시작 | seed 버전에 맞는 격리 세션 |
| `POST /api/product-assistant` | 고객 | 후보 탐색·구분 질문 |
| `GET /api/products/:id/store-options` | 고객 | 점포·가격 확인 |
| `POST /api/requests` | 고객 | 상품 확인·동의 조건·중복 검증 후 저장 |
| `GET /api/requests` | 고객 | 본인 요청·예약 상태 |
| `POST /api/unidentified-requests` | 고객 | 원문·사유 저장 |
| `POST /api/requests/:id/cancel` | 고객 | O-04 확정 후 지원 |
| `GET /api/merchant/demand` | 경영주 | 상품별 미확보 수요·사유·기존 발주 연결·고객 상세 진입 키 |
| `GET /api/merchant/demand/:product_id/requests` | 경영주 | 현재 점포·세션의 해당 상품 고객별 요청 상세와 상태 |
| `GET /api/merchant/requests/:request_id` | 경영주 | 허용된 단일 고객 요청의 동의·순번·발주·이행 상세 |
| `POST /api/merchant/reviews` | 경영주/이벤트 | 에이전트 검토 실행 |
| `POST /api/merchant/proposals/:id/instructions` | 경영주 | 자연어 제안 수정 |
| `POST /api/merchant/proposals/:id/approve` | 경영주 | 제안 버전·최신 조건 검사 후 발주 |
| `PUT /api/merchant/order-policy` | 경영주 | 정책 설정·버전·승인 기록 |
| `POST /api/merchant/auto-order-runs` | 경영주/허용된 이벤트 | 활성 정책 안에서만 자동발주 |
| `POST /api/demo/orders/:id/confirm-supply` | 데모 경영주 | 확보량 시뮬레이션·배정·모의 결제 연결 |
| `POST /api/demo/orders/:id/receive` | 데모 경영주 | 입고·픽업 가능·알림 생성 |
| `POST /api/merchant/reservations/:id/collect` | 경영주 | O-09 방식 및 마감 검사 |
| `GET /api/notifications` | 고객/경영주 | 본인 앱 내 알림 |
| `POST /api/demo/advance-time` | 데모 권한 | 현재 세션의 시계만 이동 |
| `POST /api/demo/reset` | 데모 권한 | 현재 세션만 초기화 |

## 오류 계약

응답은 `code`, 사용자 안내 `message`, 필요한 경우 `details`, `retryable`을 가진다. 예: `INVALID_INPUT`, `STALE_PROPOSAL`, `CONSENT_MISMATCH`, `INSUFFICIENT_SUPPLY`, `PICKUP_EXPIRED`, `LLM_UNAVAILABLE`, `RATE_LIMITED`.

서버 오류·비밀정보·원문 DB 예외를 사용자에게 그대로 노출하지 않는다. 오류가 났는데 완료 카피를 보여주지 않는다.

상품 집계 응답은 최소한 `product_id`, `requested_qty`, `uncommitted_qty`, `committed_qty`, `allocated_qty`, `reserved_qty`, `pending_reason`과 고객 상세 조회 가능 여부를 제공한다. 고객 상세 응답은 `actor_id`/`display_name`, `request_id`, `product_id`, `quantity`, `accepted_price_krw`, `consent_version`, `consent_at`, `sequence`, `request_status`, 연결된 `order_id`/`order_line_id`/`committed_qty`, allocation 상태·수량, mock payment 상태, reservation 상태·`pickup_available_at`·`pickup_deadline_at`·`collected_at`을 제공한다. 아직 존재하지 않는 후속 상태는 `null`과 명시적 상태로 구분한다.

이 조회는 읽기 전용이며 고객별 발주·동의·결제 상태를 임의로 변경하지 않는다. 원문/대화는 기본 고객 상세에 포함하지 않고, D-43의 접근 범위와 개인정보 보호 계약이 별도로 허용한 경우에만 제한적으로 제공한다. 다른 세션·점포의 `actor_id`, 요청, 주문, 예약을 조회하면 안 된다.

## seed 데이터

D-26에 따라 약 200개 다양한 상품과 실제 점포·좌표를 준비한다. 8~12개 점포·합성 고객/경영주 구성은 [19번](19-data-research-and-seeding.md)의 초기안이다. [24번](24-market-research-and-scenario-design.md)의 사용자 니즈·트렌드 조사를 선행하고 seed와 평가 사례를 함께 생성한다. 기존 20개/가상 점포 3개 제안은 대체됐다.

필수 상황: 유사 상품명, 맛·용량 차이, 미등록 표현, 최소 발주량 미달, 발주 제한, 공급 종료, 공급량 부족, 자동발주 예산 초과, 예약 입고 대기, 픽업 가능, 기한 초과.

- 재현 가능한 고정 ID/seed 버전을 사용한다.
- API 키·실제 개인정보 없이 만든다.
- 웹 참고 상품은 출처와 확인일을 기록한다. 가격·취급·공급 값은 모의 조건으로 표시한다.
- 실험용 입력을 모두 프롬프트 예시로 노출하지 않는다. 최종 평가용 사례는 분리한다.
- 데이터 생성 후 FK·수량·가격·타임라인의 일관성을 검증한다.

## 스키마/API 확정 전 보완 목록

DB를 구현하기 전에 다음 계약을 확정한다.

| 대상 | 필요한 보완 | 추적 |
|---|---|---|
| products/stores와 가변 조건 | 공통 읽기 전용 마스터와 세션별 가격/공급/정책/예산/대화 분리, 교차 세션 참조 차단 | R-18 |
| request_order_links | 활성/해제/실패 수량, 부족 확정 시 복귀, FIFO와의 관계 | R-01/R-02 |
| order_lines/공급 이벤트 | available_order_qty 의미, 누적/증분, 공급 회차, 헤더 집계 | R-03 |
| allocations/reservations | allocation_id 단일 연결로 충분한지, 부분/회차 합산 정책 선결 | O-01/R-05 |
| 가격/예산 | 매입가/판매가, 예산 기간·점유·사용·반납, 관련 시각 | O-08/R-07 |
| session/actor/실행 | 연결·역할·generation, reset 후 늦은 쓰기 거절 | R-17/R-19 |
| 재동의/상태 API | review_required 복귀와 동의 버전, 지원 여부 | O-05/R-25 |
| 실행 결과·알림 | correlation/idempotency key, 부분 성공 조회·재개, 최초 픽업 시각 보존 | R-24/R-27 |
| 경영주 상품↔고객 상세 조회 | 상품 집계 합계와 고객 행의 수량·상태 일치, actor/session/store 권한, 동의·발주·이행 연결 | D-43/CORE-26/AC-32 |

입출력 필드뿐 아니라 오류 code·HTTP 상태·retryable·필드 단위·서버 권한을 소비자와 함께 고정한다. 정책이 정해지기 전 테스트 기대값을 스키마 설계로 대신 결정하지 않는다.

## 출처·실험 데이터 계약

상품/점포 마스터는 필드별 reference_verified / synthetic / simulated를 구분하고 source URL·사건/게시/확인일·버전을 저장한다. 점포 좌표는 WGS84와 주소 정합성을 확인한다. 가격·공급·재고는 실제값으로 주장하지 않는다. research_case_id → scenario_id → eval_case_id와 catalog/seed/policy 버전을 연결한다. 평가 정답·holdout은 앱 조회용 테이블/alias에 넣지 않는다. 평가 실행기의 보호된 산출물에서 관리하고 제출 서비스에 노출하지 않는다. 상세 스키마는 DBA와 평가자가 19/21/24번을 따라 확정한다.

## 니즈·추천과 상품 상태의 의미 계약

D-37·[27번](27-service-values-and-guardrails.md). 필드명과 물리 테이블은 초안이나 다음 구별은 유지한다.

- `assortment_status`: 점포 취급/미취급/unknown. 조건 레코드 누락은 unknown이다.
- `stock_qty`: 모의 점포 재고. null/unknown과 0을 구별하며 발주 가능 수량과 다르다.
- `observation_status`, `observed_at`: 조회 성공/오류/미확인과 근거 시각. timeout을 품절로 저장하지 않는다.
- 카탈로그 존재 여부와 검색 식별 결과는 별개다. 검색 0건만으로 미등록을 확정하지 않는다.
- `need_records` 또는 동등한 확장: 세션·actor·점포·원문 참조, 정제 단서/근거/불확실성, 식별 상태·확인된 미충족 사유·관측 시각·source/research 참조. 미식별 기록과 이중 생성하지 않도록 사건 키를 공유하거나 연결한다.
- `recommendation_events` 또는 동등한 이벤트: 원 니즈 ID, 후보 SKU, 정확/대체 구분, 노출/선택/거절, 후속 요청 ID. 구매 요청과 별도로 저장하고 노출·클릭이 발주 수량을 만들지 않는다.

원문/대화는 기존 접근 범위 안에서 보존하며 모델 추정과 사용자 확인 속성을 구분한다. 운영 오류는 agent_runs 등 오류 기록으로 남기고 니즈 통계에서 제외한다. 재시도 중복·다른 점포/세션 조회·대체 선택 후 동의 전 거래 불변·전환 시 중복 수요를 DB 통합 검사에 포함한다. 본부용 API나 화면은 추가하지 않는다.

## D-41/42/43이 요구하는 데이터·API 의미

`minimum_order_qty`와 `order_multiple`은 발주 조건이다. 수요 총량의 저장 상한이나 `POST /api/requests`의 MOQ 초과 거절 조건으로 쓰지 않는다. 유효 요청량·진행 중 발주 연결량·미발주량을 구분하고 동일 요청을 중복 계산하지 않는다.

발주 가능 기한, O-03에서 정할 구매 동의 유효기간, `pickup_available_at`/`pickup_deadline_at`을 단일 `deadline`이나 하나의 만료 이벤트로 대체하지 않는다. 입고 대기에는 픽업 마감을 미리 생성하지 않는다. 동의 유효성을 저장·검증할 필드와 재동의 상태는 O-03 결정 후 구체화한다. 현재 `consent_at`만으로 무기한 유효 동의라고 가정하지 않는다. 회차 테이블·새 모집 기한은 이번 결정으로 추가하지 않는다.
