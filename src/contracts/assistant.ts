import type { Scope } from './domain';
export interface AssistantEnvelope extends Scope { requestId:string; conversationId:string; inputRevision:number; catalogHash:string }
export interface DialogueTurn { role:'user'|'assistant'; content:string }
export interface CustomerInput extends AssistantEnvelope { text:string; history:DialogueTurn[]; clarificationCount:number }
export interface Candidate { id:string; kind:'exact'|'confirm'|'alternative'; sharedEvidence:string[]; differences:string[]; unknownConditions:string[] }
export interface CustomerInterpretation { action:'show_candidates'|'ask_clarification'|'unidentified'; candidates:Candidate[]; question:string|null; reason:string; confirmationRequired:true }
export interface MerchantConstraints { budgetLimitKrw:number|null; excludeCategories:string[]; excludeProductIds:string[]; maxQuantity:number|null; restorePrevious:boolean }
export interface MerchantInterpretation { intent:'modify'|'restore'|'clarify'; scope:'current_proposal'|'policy'|null; constraints:MerchantConstraints; question:string|null; reason:string }
export interface MerchantInput extends AssistantEnvelope { text:string; history:DialogueTurn[]; state:{ storeId:string; proposalId:string|null; proposalVersion:number|null; currentProposalVersion?:number|null; stale?:boolean; dailyBudgetKrw:number; currentConstraints:MerchantConstraints|null; previousConstraints:MerchantConstraints|null; groups:{sku:string;requestedQty:number;orderableQty:number;purchaseCostKrw:number}[] } }
export interface ModelUsage { inputTokens:number; outputTokens:number; totalTokens:number; estimatedCostUsd:number|null }
export type AssistantResponse<T> = {ok:true; data:AssistantEnvelope & {mode:'live'|'fixture';model:string;promptVersion:string;catalogVersion:string;result:T;usage:ModelUsage;latencyMs:number}} | {ok:false; error:{code:string;message:string;retryable:boolean;attempt?:{providerCalled:boolean;model:string|null;usage:ModelUsage|null;latencyMs:number;mode:'live'}}};
export const EMPTY_CONSTRAINTS:MerchantConstraints={budgetLimitKrw:null,excludeCategories:[],excludeProductIds:[],maxQuantity:null,restorePrevious:false};
