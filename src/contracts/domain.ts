export type Id = string;
export type Role = 'customer' | 'merchant';
export type RequestStatus = 'pending' | 'review_required' | 'allocated' | 'reserved' | 'cancelled';
export type ReservationStatus = 'payment_pending' | 'payment_failed' | 'confirmed' | 'pickup_ready' | 'collected' | 'pickup_expired';
export interface Scope { sessionId: Id; generation: number; actorId: Id; roleEpoch: number }
export interface CommandContext extends Scope { commandId: Id; correlationId: Id; expectedRevision?: number }
export interface SourceOrigin { kind: 'reference_verified' | 'synthetic'; sourceIds: string[]; sourceUrls: string[]; checkedAt: string | null; publishedAt: string | null; productConfidence: string; trendConfidence: string; fieldOrigin: Record<string,string>; researchCaseIds: string[]; trendEvidence?: string|null; evidenceScope?: string|null; launchDate?: string|null }
export interface Product { sku: Id; name: string; category: string; brand: string; size: string | null; flavor: string | null; aliases: string[]; attributes: { observedNameTerms: string[] }; sourceOrigin: SourceOrigin }
export interface Store { id: Id; name: string; address: string; lat: number; lng: number; sourceOrigin: SourceOrigin; coordinateSource: string; coordinateAccuracy: string; operatingStatus: 'unverified' }
export interface Actor { id: Id; role: Role; displayName: string; storeId: Id | null }
export interface Versions { schema: string; seed: string; catalog: string; catalogHash: string; policy: string }
export interface Condition { storeId: Id; sku: Id; version: number; salePriceKrw: number; purchaseCostKrw: number; minimumOrderQty: number; orderMultiple: number; availableOrderQty: number; assortmentStatus: 'listed'|'not_listed'|'unknown'; stockQty: number|null; observationStatus: 'observed'|'error'|'unknown'; observedAt: number|null; supplyStatus: 'available'|'restricted'|'discontinued'|'unknown'; reason: string|null; orderableUntil: number|null; simulated: true }
export interface ConsentView { accepted: true; version: number; termsVersion: string; sku: Id; storeId: Id; quantity: number; unitPriceKrw: number; consentAt: number; expiresAt: number; status: 'valid'|'expired'|'mismatch'|'not_applicable_paid'|'cancelled' }
export interface AllocationView { id: Id; lineId: Id; quantity: number; status: 'held'|'paid'|'released'; received: boolean }
export interface PaymentView { id: Id; cycle: number; attempt: number; status: 'succeeded'|'failed'; amountKrw: number; createdAt: number }
export interface ReservationView { id: Id; code: string; status: ReservationStatus; quantity: number; totalKrw: number; holdExpiresAt: number|null; pickupAvailableAt: number|null; pickupDeadlineAt: number|null; collectedAt: number|null }
export interface RequestDetail { id: Id; actorId: Id; displayName: string; sku: Id; storeId: Id; quantity: number; acceptedPriceKrw: number; sequence: number; status: RequestStatus; isActive: boolean; pendingReason: string|null; consent: ConsentView; createdAt: number; updatedAt: number; version: number; paymentCycle: number; links: { orderId: Id; lineId: Id; quantity: number; active: boolean; releasedReason: string|null }[]; allocations: AllocationView[]; payments: PaymentView[]; reservation: ReservationView|null; quantitySummary: { validPending: number; activeLinked: number; allocatedHeld: number; paid: number; collected: number; pickupExpired: number } }
export interface OrderLineView { id: Id; sku: Id; orderedQty: number; confirmedQty: number|null; receivedQty: number|null; salePriceKrw: number; purchaseCostKrw: number; conditionVersion: number; supplyConfirmedAt: number|null; receivedAt: number|null }
export interface OrderView { id: Id; storeId: Id; status: 'submitted'|'supply_confirmed'|'received'; approvalType: 'manual'|'policy'; policyVersion: number; budgetDay: string; createdAt: number; lines: OrderLineView[] }
export interface PolicyView { id: Id; storeId: Id; enabled: boolean; skuScope: Id[]; categoryScope: string[]; dailyBudgetKrw: number; version: number; approvedBy: Id|null; approvedAt: number|null }
export interface BudgetView { storeId: Id; budgetDay: string; reservedKrw: number; securedKrw: number; usedKrw: number; limitKrw: number }
export interface PoolView { sourceLineId: Id; storeId: Id; sku: Id; salePriceKrw: number; confirmedQty: number; unallocatedQty: number; heldQty: number; paidQty: number; receivedAt: number|null }
export interface DemandRow { sku: Id; storeId: Id; requestedQty: number; validPendingQty: number; activeLinkedQty: number; pendingOrderCoverageQty: number; unallocatedPoolQty: number; newOrderNeedQty: number; allocatedHeldQty: number; paidQty: number; deferredReasons: string[]; customerDetailAvailable: boolean }
export interface ProposalChange { excludeSkus?: Id[]; excludeCategories?: string[]; budgetCapKrw?: number; maxQuantities?: Record<Id,number>; scope: 'once' }
export interface ProposalLine { sku: Id; quantity: number; purchaseCostKrw: number; salePriceKrw: number; conditionVersion: number; totalKrw: number }
export interface ProposalView { id: Id; storeId: Id; version: number; status: 'draft'|'approved'; sourceFingerprint: string; constraints: ProposalChange; lines: ProposalLine[]; deferred: { sku: Id; reason: string; nextAction: string }[]; totalKrw: number; orderId: Id|null }
export interface NeedView { id: Id; actorId: Id; storeId: Id; originalText: string; dialogue: string[]; extractedClues: string[]; candidateSkus: Id[]; identificationStatus: string; reason: string; observedAt: number; sourceRefs: string[]; createdAt: number }
export interface NotificationView { id: Id; actorId: Id; type: string; body: string; createdAt: number; readAt: number|null }
export interface DemoSnapshot { contractVersion: 'domain-v1'; versions: Versions; session: { id: Id; generation: number; revision: number; createdAt: number }; actor: Actor; actors: Actor[]; roleEpoch: number; clock: { now: number; offsetMs: number; timeZone: 'Asia/Seoul' }; products: Product[]; stores: Store[]; conditions: Condition[]; requests: RequestDetail[]; orders: OrderView[]; policies: PolicyView[]; proposals: ProposalView[]; needs: NeedView[]; notifications: NotificationView[]; demand: DemandRow[]; budgets: BudgetView[]; supplyPools: PoolView[]; persistence: { status: 'ready'|'read_only'|'recovery_required'; durableRevision: number } }
export interface DomainError { code: string; message: string; retryable: boolean; details?: { field?: string; currentRevision?: number; entityId?: Id; reason?: string } }
export type Result<T> = { ok: true; data: T } | { ok: false; error: DomainError };
export interface CommandReceipt { commandId: Id; effect: 'applied'|'replayed'; revision: number; entityIds: Id[]; eventIds: Id[]; snapshot: DemoSnapshot }
export interface CreateRequest { sku: Id; storeId: Id; quantity: number; acceptedPriceKrw: number; conditionVersion: number; consent: { accepted: true; termsVersion: string }; sourceNeedId?: Id }
type EditRequest = { requestId: Id; quantity: number; acceptedPriceKrw: number; consent: { accepted: true; termsVersion: string }; expectedRequestVersion: number };
export type DemoCommand =
 | ({type:'request.create'} & CreateRequest)
 | ({type:'request.changeQuantity'} & EditRequest)
 | ({type:'request.reconsent';conditionVersion:number} & EditRequest)
 | {type:'request.cancel';requestId:Id;expectedRequestVersion:number}
 | {type:'request.replace';originalRequestId:Id;newRequest:CreateRequest;expectedRequestVersion:number}
 | {type:'need.record';storeId:Id;originalText:string;dialogue:string[];extractedClues:string[];candidateSkus:Id[];identificationStatus:string;reason:string;observedAt:number;sourceRefs:string[]}
 | {type:'recommendation.record';needId:Id;candidateSku:Id;kind:'exact'|'alternative';action:'shown'|'selected'|'rejected'}
 | {type:'merchant.review';storeId:Id}
 | {type:'proposal.revise';proposalId:Id;expectedProposalVersion:number;change:ProposalChange}
 | {type:'proposal.undo';proposalId:Id;expectedProposalVersion:number}
 | {type:'proposal.approve';proposalId:Id;expectedProposalVersion:number;confirmed:true}
 | {type:'policy.update';storeId:Id;expectedPolicyVersion:number;enabled:boolean;skuScope:Id[];categoryScope:string[];dailyBudgetKrw:number;confirmed:true}
 | {type:'autoOrder.run';storeId:Id}
 | {type:'demo.confirmSupply';lineId:Id;confirmedQty:number}
 | {type:'demo.receive';lineId:Id;receivedQty:number}
 | {type:'payment.retry';requestId:Id;paymentCycle:number}
 | {type:'merchant.collect';reservationCode:string}
 | {type:'notification.read';notificationId:Id}
 | {type:'demo.updateCondition';storeId:Id;sku:Id;expectedConditionVersion:number;patch:Partial<Omit<Condition,'storeId'|'sku'|'version'|'simulated'>>}
 | {type:'demo.setPaymentOutcome';actorId:Id;outcomes:('success'|'failure')[]}
 | {type:'demo.advanceTime';deltaMs:number}
 | {type:'demo.reconcile';reason:'reopen'|'manual'}
 | {type:'demo.reset';confirmed:true}
 | {type:'agent.record';requestId:Id;mode:'live'|'fixture';model:string;promptVersion:string;catalogHash:string;usage:{inputTokens:number;outputTokens:number;totalTokens:number};latencyMs:number;status:'ok'|'lookup_error'};
export type DemoQuery = {type:'requests.list'|'merchant.demand'|'notifications.list'|'needs.list'} | {type:'requests.detail'|'merchant.requestDetail';requestId:Id} | {type:'merchant.productRequests'|'catalog.storeOptions';sku:Id} | {type:'recommendations.list';needId:Id} | {type:'commands.result';commandId:Id};
export interface DemoClient { initialize(): Promise<Result<DemoSnapshot>>; snapshot(scope:Scope):Promise<Result<DemoSnapshot>>; dispatch(command:DemoCommand,context:CommandContext):Promise<Result<CommandReceipt>>; query(query:DemoQuery,scope:Scope):Promise<Result<unknown>>; switchRole(targetActorId:Id,scope:Scope):Promise<Result<DemoSnapshot>>; subscribe(listener:(snapshot:DemoSnapshot)=>void):()=>void }
