# D02 G0 — 브라우저 도메인·SQLite·typed client 계약

상태: **G0 contract accepted by coordinator / code not started**. 작성자 preflight_builder, 2026-09-21. CTX-APP-v3 SHA `e8d6eb6ffef8765544e3aeeeb9c27b1e98f0c7cb5131202712ec4d32d806ea99` ACK. card·CORE·DECISION_INDEX 및 docs03/04/06/07/09/13/29·ADR002를 읽었다. 해당 문서의 O/R ‘미정’ 표기보다 채택 ADR002의 같은 policy key를 우선한다. 새 제품 정책을 이 문서만으로 채택하지 않는다.

목적: 고객이 명확한 상품을 확인하고 동의해 요청하면, 경영주가 상품별 묶음을 검토·승인하고, 실제 SQLite에 공급·FIFO·모의 결제·입고·48시간 수령이 일관되게 남는다. 정상 성공과 재동의/재시도 복귀를 모두 구현한다. 관련 CORE02~11/13/17/25/26, AC04~17/20/22/31/32. 단일 Worker/sql.js·한 탭이며 서버 거래 API/외부 DB는 없다.

현재 소유는 이 문서 하나다. schema/types/seed/domain/Worker 코드 소유권 및 격리 branch는 조정자의 후속 배정 후 확정한다. package/lockfile은 root 단일 작성. B01 독립 PASS 이전에 제품 코드를 쓰지 않는다.

## 1. 공통 표현과 FE 소비 경계

DTO·command는 camelCase, SQL column은 snake_case. 금액은 원 단위 안전 정수, 수량은 정수, 시간은 UTC epoch milliseconds. TypeScript의 number라도 runtime safe integer 검사를 한다. 모든 mutable id 참조는 sessionId+generation 범위로 검사한다. 데이터 원장은 SQLite이며 FE가 배열을 직접 수정해 업무 상태를 만들 수 없다.

```ts
type Id = string;
type Role = 'customer' | 'merchant';
type RequestStatus = 'pending' | 'review_required' | 'allocated' | 'reserved' | 'cancelled';
type ReservationStatus = 'payment_pending' | 'payment_failed' | 'confirmed' |
  'pickup_ready' | 'collected' | 'pickup_expired';
type OrderStatus = 'draft' | 'approved' | 'submitted' | 'supply_confirmed' | 'received' | 'blocked';
type ConsentStatus = 'valid' | 'expired' | 'mismatch' | 'not_applicable_paid' | 'cancelled';
interface Scope {
  sessionId: Id; generation: number; actorId: Id;
  roleEpoch: number; // role/actor switch invalidates in-flight client work
}
interface CommandContext extends Scope {
  commandId: Id; correlationId: Id;
  expectedRevision?: number; // optional strict snapshot guard; entity/source versions remain mandatory
}
interface SourceOrigin {
  kind: 'reference_verified' | 'synthetic'; sourceIds: string[]; sourceUrls: string[];
  checkedAt: string | null; publishedAt: string | null;
  productConfidence: string; trendConfidence: string;
  fieldOrigin: Record<string, string>; researchCaseIds: string[];
}
interface Product {
  sku: Id; name: string; category: string; brand: string; size: string | null;
  flavor: string | null; aliases: string[];
  attributes: { observedNameTerms: string[] }; sourceOrigin: SourceOrigin;
}
interface Store {
  id: Id; name: string; address: string; lat: number; lng: number;
  sourceOrigin: SourceOrigin; coordinateSource: string; coordinateAccuracy: string;
  operatingStatus: 'unverified'; // reported location is not a current inventory claim
}
interface Actor { id: Id; role: Role; displayName: string; storeId: Id | null; }
interface Versions { schema: string; seed: string; catalog: string; catalogHash: string; policy: string; }
interface Condition {
  storeId: Id; sku: Id; version: number;
  salePriceKrw: number; purchaseCostKrw: number;
  minimumOrderQty: number; orderMultiple: number; availableOrderQty: number;
  assortmentStatus: 'listed' | 'not_listed' | 'unknown'; stockQty: number | null;
  observationStatus: 'observed' | 'error' | 'unknown'; observedAt: number | null;
  supplyStatus: 'available' | 'restricted' | 'discontinued' | 'unknown';
  reason: string | null; orderableUntil: number | null; simulated: true;
}
interface DemoSnapshot {
  contractVersion: 'domain-v1'; versions: Versions;
  session: { id: Id; generation: number; revision: number; createdAt: number };
  actor: Actor; actors: Actor[]; roleEpoch: number;
  clock: { now: number; offsetMs: number; timeZone: 'Asia/Seoul' };
  products: Product[]; stores: Store[]; conditions: Condition[];
  requests: RequestDetail[]; orders: OrderView[];
  policies: PolicyView[]; proposals: ProposalView[];
  needs: NeedView[]; notifications: NotificationView[];
  demand: DemandRow[]; budgets: BudgetView[]; supplyPools: PoolView[];
  persistence: { status: 'ready' | 'read_only' | 'recovery_required'; durableRevision: number };
}
interface DomainError {
  code: string; message: string; retryable: boolean;
  details?: { field?: string; currentRevision?: number; entityId?: Id; reason?: string };
}
type Result<T> = { ok: true; data: T } | { ok: false; error: DomainError };
interface CommandReceipt {
  commandId: Id; effect: 'applied' | 'replayed'; revision: number;
  entityIds: Id[]; eventIds: Id[]; snapshot: DemoSnapshot;
}
interface DemoClient {
  initialize(): Promise<Result<DemoSnapshot>>;
  snapshot(scope: Scope): Promise<Result<DemoSnapshot>>;
  dispatch(command: DemoCommand, context: CommandContext): Promise<Result<CommandReceipt>>;
  query(query: DemoQuery, scope: Scope): Promise<Result<unknown>>; // implementation uses discriminated overloads
  switchRole(targetActorId: Id, scope: Scope): Promise<Result<DemoSnapshot>>;
  subscribe(listener: (snapshot: DemoSnapshot) => void): () => void;
}
```

`source_origin` 요청은 DTO `sourceOrigin`으로 고정하고 원시 data/research의 snake_case를 importer가 변환한다. Product.sku는 raw 후보의 DEMO 내부 ID를 보존한다. 서버 catalog와 SQLite 제품 집합·정렬 canonical hash가 반드시 같다. 실제 GS상품코드로 표시하지 않는다.

제안 승인 여부는 해당 수요·조건·정책·예산 fingerprint로 판단한다. 알림 읽기처럼 실행 조건과 무관한 session revision 변경만으로 제안을 stale로 만들지 않는다.

Snapshot 범위: products/stores는 공개 마스터 전체, actors는 합성 선택기용 기본 필드만 전체 제공. 고객 requests/needs/notifications는 본인만, 주문은 본인 요청에 연결된 허용 필드만 노출(다른 고객 상세 없음). 경영주는 자기 store 조건·요청·주문·정책·니즈만 노출한다. 고객은 점포 선택용 공개 조건을 읽을 수 있다. demand/budget/policy/proposal은 경영주만. 그 외 배열은 빈 배열로 표현한다. 존재하지 않는 후속 상태는 null, 수량0, 미관측 null을 서로 바꾸지 않는다.

switchRole은 합성 actor의 역할 선택 UI용이며 실제 인증이 아니다. 현재 세션에 속한 actor만 선택할 수 있고 업무 요청을 만들거나 seed를 재삽입하지 않는다. roleEpoch를 올리고 이전 모델/클라이언트 query 표시를 무효화한다. business revision은 역할 변경만으로 올리지 않는다. 현재 role/actor를 durable envelope에 저장할지 여부는 Worker 구현 상세이며 거래 불변식과 분리한다.

## 2. 조회 DTO와 D-43 상세

```ts
interface ConsentView {
  accepted: true; version: number; termsVersion: string;
  sku: Id; storeId: Id; quantity: number; unitPriceKrw: number;
  consentAt: number; expiresAt: number; status: ConsentStatus;
}
interface RequestDetail {
  id: Id; actorId: Id; displayName: string; sku: Id; storeId: Id;
  quantity: number; acceptedPriceKrw: number; sequence: number;
  status: RequestStatus; isActive: boolean; pendingReason: string | null; consent: ConsentView;
  createdAt: number; updatedAt: number; version: number; paymentCycle: number;
  links: { orderId: Id; lineId: Id; quantity: number; active: boolean; releasedReason: string | null }[];
  allocations: { id: Id; lineId: Id; quantity: number; status: 'held' | 'paid' | 'released'; received: boolean }[];
  payments: { id: Id; cycle: number; attempt: number; status: 'succeeded' | 'failed'; amountKrw: number; createdAt: number }[];
  reservation: null | { id: Id; code: string; status: ReservationStatus; quantity: number;
    totalKrw: number; holdExpiresAt: number | null; pickupAvailableAt: number | null;
    pickupDeadlineAt: number | null; collectedAt: number | null };
  quantitySummary: { validPending: number; activeLinked: number; allocatedHeld: number;
    paid: number; collected: number; pickupExpired: number };
}
interface DemandRow {
  sku: Id; storeId: Id; requestedQty: number; validPendingQty: number;
  activeLinkedQty: number; pendingOrderCoverageQty: number; unallocatedPoolQty: number;
  newOrderNeedQty: number; allocatedHeldQty: number; paidQty: number;
  deferredReasons: string[]; customerDetailAvailable: boolean;
}
```

OrderView는 header id/store/status/approvalType/policyVersion/budgetDay/createdAt 및 lines 배열을 가진다. Line은 sku/orderedQty/confirmedQty(null이면미확정)/receivedQty(null이면미입고)/salePriceKrw/purchaseCostKrw/conditionVersion/supplyConfirmedAt/receivedAt을 제공한다. header 상태는 모든 라인의 사실로 산출한다. 혼합 상태에서 개별 line 상태를 감추지 않는다.

PolicyView: id/store/enabled/skuScope/categoryScope/dailyBudgetKrw/version/approvedBy/approvedAt. BudgetView: storeId/budgetDay/reservedKrw/securedKrw/usedKrw(앞 둘 합)/limitKrw. PoolView: sourceLineId/storeId/sku/salePriceKrw/confirmedQty/unallocatedQty/heldQty/paidQty/receivedAt. paidQty 내부 단계는 예약 조회로 구분하고 재고로 다시 합산하지 않는다.

NeedView: id/actorId/storeId/originalText/dialogue/extractedClues/candidateSkus/identificationStatus/reason/observedAt/sourceRefs/createdAt. 고객은 본인 원문, 경영주는 현재 점포에 고객이 명시적으로 남긴 니즈만 읽는다. 일반 RequestDetail에 원문·대화는 넣지 않는다. RecommendationView는 별도 이벤트 조회로 needId/candidateSku/kind(exact|alternative)/action(shown|selected|rejected)/followupRequestId를 제공한다. 니즈·추천은 requestedQty에 포함하지 않는다.

읽기 query: `requests.list`, `requests.detail{requestId}`, `merchant.demand`, `merchant.productRequests{sku}`, `merchant.requestDetail{requestId}`, `catalog.storeOptions{sku}`, `notifications.list`, `needs.list`, `recommendations.list{needId}`, `commands.result{commandId}`. 각 query overload의 반환은 위 typed DTO 배열/개별 객체다. 상세를 request_id별로 먼저 집계한 뒤 join하여 복수 링크×배정×결제 시도로 합계가 증폭되지 않게 한다. 집계와 고객 행은 같은 SQLite read transaction과 동일 effective-consent 필터를 쓴다. 불일치가 있으면 `INVARIANT_VIOLATION`이고 승인 금지다.

## 3. 명령 계약

모든 명령은 `type` discriminant와 아래 camelCase payload를 가진다. FE가 임의 SQL·금액 합계·순번·상태값을 전달하지 않는다. 고객 확인 command의 acceptedPriceKrw는 확인 tuple이며 서버/LLM 계산이 아니라 현재 SQLite condition과 비교한다. 모든 명시 confirm/consent boolean은 true literal을 요구하고 기본 체크하지 않는다.

| type / payload | 주체 | 적용·실패 |
|---|---|---|
| `request.create {sku,storeId,quantity,acceptedPriceKrw,conditionVersion,consent:{accepted:true,termsVersion},sourceNeedId?}` | 고객 | 현재 상품/가격/점포 확인·수량1~20·동의기록·새순번. 활성중복은 ACTIVE_REQUEST_EXISTS. MOQ는 접수 상한이 아님 |
| `request.changeQuantity {requestId,quantity,acceptedPriceKrw,consent:{accepted:true,termsVersion},expectedRequestVersion}` | 본인 고객 | 미연결 pending만. 유효 감소는 순번/원동의시각/만료 유지·revision증가, 증가/부적합 재동의는 새순번/동의시각 |
| `request.reconsent {requestId,quantity,acceptedPriceKrw,conditionVersion,consent:{accepted:true,termsVersion},expectedRequestVersion}` | 본인 고객 | 현재 tuple 재확인, 이전 payment cycle 종료·hold해제·새cycle/순번. 이미 성공결제면 불가 |
| `request.cancel {requestId,expectedRequestVersion}` | 본인 고객 | 결제성공 전만. 링크/held해제, 제출발주/승인예산은 유지 |
| `request.replace {originalRequestId,newRequest:{...request.create},expectedRequestVersion}` | 본인 고객 | 취소 가능 원요청 취소+새동의요청 생성 원자적. 하나 실패하면 둘 다 불변 |
| `need.record {storeId,originalText,dialogue,extractedClues,candidateSkus,identificationStatus,reason,observedAt,sourceRefs}` | 고객 | 명시 남기기만. operationalError reason불가, 존재 candidate만. 수요/요청 생성0 |
| `recommendation.record {needId,candidateSku,kind,action}` | 본인 고객 | 추천 이력만. 선택해도 request.create 별도 동의 필요 |
| `merchant.review {storeId}` | 해당 경영주 | 최신 수요/조건/예산에서 proposal 생성/재사용. 같은 state는 중복 proposal/알림0 |
| `proposal.revise {proposalId,expectedProposalVersion,change}` | 해당 경영주 | allowlist: excludeSkus,excludeCategories,budgetCapKrw,maxQuantities,scope:'once'; 금액재계산·새version·history. 모델결과 자체 실행없음 |
| `proposal.undo {proposalId,expectedProposalVersion}` | 해당 경영주 | 같은 제안의 직전 유효 초안 복원, 최신 data로 재검증 |
| `proposal.approve {proposalId,expectedProposalVersion,confirmed:true}` | 해당 경영주 | 실행lines 전체 최신검사 후 단일 transaction; 하나 stale면0실행. policy·condition·demand·budget fingerprint 검사 |
| `policy.update {storeId,expectedPolicyVersion,enabled,skuScope,categoryScope,dailyBudgetKrw,confirmed:true}` | 해당 경영주 | ‘앞으로’ 별도 승인. 현재일사용액 미만 예산거절. 새정책 이후에만 적용 |
| `autoOrder.run {storeId}` | 해당 경영주/내부 허용 이벤트 | 현재 활성 사전승인정책 범위만. 새요청·조건/정책변경·재진입·명시검토 이벤트에서 호출 |
| `demo.confirmSupply {lineId,confirmedQty}` | 해당 경영주 | 0..orderedQty 1회최종값; link모두해제·pool기록·예산원장정산·FIFO·모의결제 |
| `demo.receive {lineId,receivedQty}` | 해당 경영주 | 공급확정후 receivedQty===confirmedQty,1회. 모든source입고충족 예약만 픽업전환 |
| `payment.retry {requestId,paymentCycle}` | 본인 고객 | 알려진 최초실패만,10분미만,동의재검사,두번째최종시도. 결과미확인은 command result조회 |
| `merchant.collect {reservationCode}` | 해당 경영주 | 해당store+전량+pickup_ready+now<deadline,1회 |
| `notification.read {notificationId}` | 본인 actor | readAt최초기록, 픽업시각불변 |
| `demo.updateCondition {storeId,sku,expectedConditionVersion,patch}` | 해당 경영주 | allowlist 조건만; observed/error/unknown·0재고 차이 보존; 바뀐가격은 기존 미결제동의review |
| `demo.setPaymentOutcome {actorId,outcomes:('success'|'failure')[]}` | 경영주 데모도구 | 합성 결제 결과 queue,외부결제0,기존 결제결과 변조불가 |
| `demo.advanceTime {deltaMs}` | 경영주 데모도구 | 0보다크고30일이하 정수, 현재session clock만 순방향; expiry sweep |
| `demo.reconcile {reason:'reopen'|'manual'}` | 내부 trusted lifecycle / 해당 경영주 | 기한검사·hold해제·FIFO·승인정책재검토. 닫힌탭 실행 주장금지 |
| `demo.reset {confirmed:true}` | 경영주 데모도구 | 현재session만 seed기준 재생성·generation+1·내구저장. 다른session 삭제금지 |
```

정확한 unknown/미취급 요청 가능성은 ADR003의 점포 선택 계약과 일치시킨다. condition 누락은 unknown이며 0재고/미취급으로 추정하지 않는다. 신규 요청이 있어도 공급제한/MOQ미달이면 pending reason으로 보존한다. supply 종료/동의부적합은 review_required가 되며 자동 구매되지 않는다.

모델 응답 적용 envelope는 sessionId/generation/actorId/roleEpoch/conversationId/requestId/inputRevision/catalogHash를 전부 비교한다. 불일치는 STALE_RESPONSE로 버리고 DB변경/미식별저장0. 서버 API가 성공했다는 사실은 domain command 성공이 아니다. 모델 호출은 SQLite transaction 밖에서 수행한다.

## 4. SQL 구조와 제약

읽기 전용: `products(sku PK,name,category,brand,size,flavor,aliases_json,attributes_json,source_origin_json)`, `stores(id PK,name,address,lat,lng,source_origin_json)`, `schema_meta`.

모든 mutable table에 session_id,generation을 두며 `(session_id,generation,id)` unique/복합FK를 사용한다. `sessions(id PK,generation,revision,next_sequence,clock_offset_ms,created_at)`가 현재 generation을 소유하고 old generation 참조는 서비스에서 먼저 거절한다.

| 테이블 | 핵심 내용/제약 |
|---|---|
| actors | role/customer·merchant enum,merchant store_id 필수, 합성30고객+점포별1경영주 |
| conditions | unique(session,generation,store,sku), 판매/매입가>=0정수·MOQ/배수>=1·공급량>=0,stock_qty NULL또는>=0, enum/관측시각 |
| purchase_requests | actor/store/sku/qty1..20/sequence/status/is_active/consent_current_version/payment_cycle/version; is_active=1의 actor/store/sku partial unique. 취소·수령완료·픽업만료시 비활성, 예약이력은 보존 |
| consent_revisions | request/version unique,확인tuple·terms_version·consent_at·expires_at; 기존 revision 수정금지 |
| policies | store unique,enabled boolean,scope_json 검증,daily_budget_krw,version,approved actor/time |
| proposals / proposal_versions | store·constraints·lines/deferred·source fingerprint·version·previous_version·status; approved실행id 기록 |
| orders / order_lines | header/sku/ordered/confirmed/received/승인시판매·매입단가/조건version/budget_day, 0<=confirmed<=ordered,received NULL또는confirmed |
| request_order_links | request+line+linkid,qty>0,active boolean,release reason/time,복합FK,이력삭제없음 |
| allocation_cycles / allocation_sources | request/cycle unique,hold/state; cycle+source_line unique·qty>0, 여러source허용 |
| reservations | request/cycle unique,code unique,qty/amount/status,hold_deadline,pickup_available/deadline,collected; 픽업pair NULL또는deadline=start+172800000 |
| mock_payments | cycle/attempt(1또는2) unique,amount,known success/failure,attempt command FK; 실제결제수단없음 |
| budget_ledger | order_line당 reserve/settle unique events,승인일/매입단가불변,현재일재환산금지 |
| need_records / recommendation_events | 사건key unique,원문/정제단서/사유/관측출처/별도추천행동; 요청수량없음 |
| notifications | recipient actor+source_event+type unique,body/created/read,픽업알림최초시각보존 |
| command_results | scope+command_id unique,payload fingerprint,result_json,event IDs,committed_revision |
| events | unique scope+event_key,entity/type/from/to/reason/clock/correlation; raw secret·내부추론없음 |
| demo_payment_outcomes | actor별명시된synthetic결과queue,한attempt에서한번소비 |
```

SQL은 실제 행·FK·CHECK·조회·transaction을 사용한다. 업무전체를 단일 JSON blob이나 JS 배열에 보관하지 않는다. 제한된 constraints/source/audit JSON만 검증 후 TEXT로 저장한다. bool0/1,INTEGER에 typeof/integer CHECK, 필수 FK 인덱스·대기열(session,generation,store,sku,sequence), active link/line 조회 인덱스를 둔다. cross-session FK와 서비스 권한검사를 함께 검사한다. reopen/export뒤 `PRAGMA foreign_keys=ON` 재적용·조회한다.

## 5. 상태·수량·발주 산식

동의유효는 now<consentAt+7일 AND 현재상품/점포/수량/판매단가 tuple일치 AND 미결제. 이미 성공결제는 동의만료를 소급 적용하지 않는다. pending 유효수량에 review/cancelled/held/payment_failed/paid/reserved/collected/expired/needs/recommendation은0이다. FE표시에서는 request와reservation/order상태를 함께 보이며 request.status=reserved만으로 픽업가능을 말하지 않는다.

동일 호환가격 그룹에서 `newOrderNeedQty=max(0,validPendingQty-unallocatedConfirmedPoolQty-pendingUnconfirmedOrderQty)`. pendingUnconfirmedOrderQty는 전체 미확정 orderedQty를1회 차감하며 active links와 더해서 차감하지 않는다. 취소로 link가 사라져도 이미 제출한 미확정 주문coverage는 남는다. source salePrice와 현재동의가 다른 pool은 해당요청 자동결제에 쓰지 않으며 잔량으로 보존한다.

SKU오름차순으로 availableOrderQty·예산의 매입가한도·필요량의 최소값을 orderMultiple로 내림한다. 결과가 MOQ미만이면 보류하고 올림/초과보충하지 않는다. proposal는 executableLines와deferred(reason,nextAction)를 분리한다. 제한이없는 정상lines는 예외때문에 막지 않고, 실행집합 자체의 stale/불법은 전부rollback한다. aggregate하위요청 합과 다르면 승인하지 않는다.

FIFO는 세션/점포/SKU의 유효pending 순번. 선두전량에 물량이 모자라면 뒤요청을 건너뛰지 않는다. 확보source는 공급확정event순서와lineId로 결정적 차감하고 source별trace를 남긴다. 공급1회최종확정시에 line active links를 전부해제하고 confirmedQty를 pool에 넣는다. 여러회차source를 합쳐 선두전량을 확보할 수 있다.

각 source line에서 `confirmedQty=unallocatedPoolQty+heldAllocationQty+paidAttributedQty`. paidAttributedQty는 confirmed(입고대기)/pickup_ready/collected/pickup_expired의 상호배타합이다. events·reservation·receivedQty를 별도재고로 더하지 않는다. 취소/최종결제실패·hold만료는 held를pool로 돌리고, paid픽업만료는pool로 돌리지 않는다.

예약결제: 배정 transaction에 최초 모의결제 결과·금액·예약/알림이 같이 기록된다. 실패는 payment_failed+holdExpiresAt=최초실패now+10분, 성공알림0. retry직전에동의/currentprice/cycle/generation/time을재검사한다. 첫실패이후 고객명시retry1회만, now>=hold deadline 또는2회실패면 release1회→review_required. 재동의는 새cycle/newsequence. 응답유실은 기존command조회이며 새attempt생성금지.

입고: 모든 allocation source가 received AND paid면 최초trigger에서 pickup_available_at=now,deadline=now+48h,notification을 같이 생성한다. 늦은배정/이미입고pool/실패retry성공도 같은predicate를검사한다. 기존deadline을어떤trigger도갱신하지않는다. 수령은해당점포경영주·번호·전량·now<deadline. 정각은만료,실환불/재판매/폐기없음.

예산: 승인transaction에서 KST일·원매입단가·ordered액 점유. 최종공급확정은 승인일장부에서 미확보액해제·확보액유지. 다음날현재가격으로옮기지않는다. policy 예산변경은현재/미래승인만,현재일used보다낮으면거절. 주문초과·음수·NaN·unsafeinteger·이중settle은실패한다.

## 6. Worker·내구저장·오류

Worker 요청 `{messageId,operation:'initialize'|'snapshot'|'query'|'command'|'switchRole',payload,context}`; 응답은 같은messageId의 Result. 한개의 Promise queue가 initialize/query/command/reset의완료경계를직렬화한다. 거래transaction 중 LLM await 금지. UI는응답이아닌subscribe이벤트로중복성공을표시하지않도록commandId로처리중상태를관리한다.

command 순서: scope/role/generation검사→현재durablecommand 재사용검사→payload검증→BEGIN→현재clock한번확정·관련expiry/최신조건검사→업무SQL/필요한내부policy event→불변식검사·result/events기록→COMMIT→export→FK재설정→IndexedDB 단일tx에bytes+versions+generation+revision저장→oncomplete후receipt/snapshot/notification공개. failure면rollback 또는마지막durablebytes복원·FK재설정, 다음업무command차단/복구안내. 메모리commit만으로성공/다음결제/발주공개하지않는다.

동일commandId·동일fingerprint는 저장result 재사용(업무event0), 다른payload는 IDEMPOTENCY_CONFLICT. fingerprint는 command type+canonicalpayload+actor/session/generation;roleEpoch는응답적용guard이고영속업무키가아니다. 재사용전역할/세션/generation 경계검사. 저장실패는command도이전snapshot에없으므로동일key재시도가능, 성공한command의응답유실은query로확인한다.

reset은현재sessionmutable행만재생성,타session보존,현재generation+1. 오래된scope/modelresponse/query표시를거절. 스냅샷손상/seed-schema불일치는자동초기화하지않고명시적 reset 안내. 최초저장실패는read_only이며정상준비PASS아님. 외부사본import/export는제품필수명령으로추가하지않으며테스트에서실제bytes검사한다.

오류 allowlist: INVALID_INPUT,NOT_FOUND,FORBIDDEN,STALE_GENERATION,STALE_ROLE,STALE_RESPONSE,STALE_PROPOSAL,VERSION_CONFLICT,ACTIVE_REQUEST_EXISTS,CONSENT_REQUIRED,CONSENT_MISMATCH,CONSENT_EXPIRED,REQUEST_LINKED,CANCELLATION_NOT_ALLOWED,INSUFFICIENT_SUPPLY,BUDGET_EXCEEDED,SUPPLY_ALREADY_CONFIRMED,RECEIPT_ALREADY_RECORDED,PAYMENT_RETRY_NOT_ALLOWED,PICKUP_NOT_READY,PICKUP_EXPIRED,ALREADY_COLLECTED,IDEMPOTENCY_CONFLICT,INVARIANT_VIOLATION,PERSISTENCE_FAILED,SNAPSHOT_INCOMPATIBLE,SNAPSHOT_CORRUPT. message는 한국어 짧은 안내이며 raw SQL·예외·비밀값을 반환하지 않는다. retryable은 저장·전송 일시 장애에만 true다. validation 오류는 수정할 행동을 표시한다. stale은 최신 조건을 재조회하고 확인해야 하므로 같은 payload 자동 재시도를 하지 않는다.

## 7. 최소 seed → 전체 seed와 검증 경계

D04A minimum은 같은 schema/importer로 대표 12 SKU·공개 9점포·합성 고객 30명·합성 경영주 9명을 사용할 수 있다. 정상 성공, 비슷한 맛/규격, MOQ 미달, 공급 0, 가격 변경, 결제 실패, 48시간을 domain factory로 생성한다. 구조·Worker 검증용 최소 seed에서 AC-22 전체 상품 조건을 PASS로 주장하지 않는다.

D04B 첫 full 후보는 220 SKU를 권장한다: 밥 19 / 면 30 / 스낵 29 / 디저트 30 / 빵 19 / 커피·유제품 26 / 음료 23 / 간편식 44. raw 414 고정 SHA `0a148016ae38dd23d2dadf9e1757b8125e6e992eadc36caae493064aec6c1dd0`에서 선택하며 최근 자료 20개를 더하면 240개다. selected SKU 목록은 조정자의 데이터 파일 소유 계약 후 고정하고 evaluator에 공개한다. 최근 자료를 기다리느라 D02를 중단하지 않는다. 공개 aliases는 dev 자료로만 만들고 보호 holdout 발화·정답은 읽지 않는다. 조건은 20~35% 희소 행렬, 가격·재고·공급은 simulated, 자동발주는 초기 off다. seed/database/catalog/manifest는 같은 원본·버전·hash로 build에서 생성한다.

G1/G2 필수 검증: 정상 전체 흐름, 13요청·MOQ6 → 12발주+1pending, 기존 6개 연결 후 중복 발주0, 3요청/2pool → 추가 필요1, FIFO 건너뛰기0, 공급0/부족 연결 해제, 취소 후 미확정 발주 coverage 보존, 동의 불일치/7일 정각, 수량 감소·증가 순번, 결제2회 실패/10분 경계/재동의 cycle, 여러 source 입고, 픽업48시간 직전·정각·직후, 예산 일자 이동/원단가/반납, 제안10중1stale → 0실행, 정책 off 후 신규 자동발주0, 고객 상세 합계·교차범위 거절, FK/rollback/export/import, 같은/다른 payload의 멱등성, 저장 실패 복원/reset 후 늦은 응답. 다른 담당자의 독립 판정 후 G3/4/5/6으로 진행한다. 구현자의 자체 PASS는 독립 QA가 아니다.

## 8. 계약 검토가 필요한 기술 의미 1건

`availableOrderQty`의 소진 단위는 docs13 R03에서 보완 대상으로 남았다. 제안: 조건 revision별 남은 모의 주문가능 capacity이며 승인시 감소, 공급최종 shortfall은 자동복원하지 않고 명시적 simulator 조건 변경으로 보충한다. 이는 supply0가 열린 앱의 auto event마다 재발주되는 루프를 막으며 pending 수요를 보존한다. 조정자가 ADR-004 초안으로 제품/상태 두 검토를 진행 중이다. ADR-004가 두 독립 검토 후 adopted되었으므로 해당 capacity 계약을 적용한다. 나머지 schema/type/Worker 구현 준비는 독립 진행한다.
