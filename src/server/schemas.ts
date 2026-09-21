import { z } from 'zod';
const identifier=z.string().min(1).max(100).regex(/^[\w:.-]+$/);
const integer=z.number().int().min(0).max(Number.MAX_SAFE_INTEGER);
const envelope={sessionId:identifier,generation:integer,actorId:identifier,roleEpoch:integer,requestId:identifier,conversationId:identifier,inputRevision:integer,catalogHash:z.string().regex(/^[a-f0-9]{64}$/)};
const history=z.array(z.object({role:z.enum(['user','assistant']),content:z.string().min(1).max(5000)}).strict()).max(12);
export const constraintsSchema=z.object({budgetLimitKrw:integer.max(100_000_000).nullable(),excludeCategories:z.array(z.string().min(1).max(60)).max(30),excludeProductIds:z.array(identifier).max(60),maxQuantity:integer.max(10000).nullable(),restorePrevious:z.boolean()}).strict();
export const customerInputSchema=z.object({...envelope,text:z.string().trim().min(1).max(1200),history,clarificationCount:integer.max(2)}).strict();
export const merchantInputSchema=z.object({...envelope,text:z.string().trim().min(1).max(1200),history,state:z.object({storeId:identifier,proposalId:identifier.nullable(),proposalVersion:integer.nullable(),currentProposalVersion:integer.nullable().optional(),stale:z.boolean().optional(),dailyBudgetKrw:integer.max(100_000_000),currentConstraints:constraintsSchema.nullable(),previousConstraints:constraintsSchema.nullable(),groups:z.array(z.object({sku:identifier,requestedQty:integer.max(10000),orderableQty:integer.max(10000),purchaseCostKrw:integer.max(1000000)}).strict()).max(60)}).strict()}).strict();
export const customerOutputSchema=z.object({action:z.enum(['show_candidates','ask_clarification','unidentified']),candidates:z.array(z.object({id:z.string(),kind:z.enum(['exact','confirm','alternative']),sharedEvidence:z.array(z.string()),differences:z.array(z.string()),unknownConditions:z.array(z.string())}).strict()),question:z.string().nullable(),reason:z.string(),confirmationRequired:z.literal(true)}).strict();
export const merchantOutputSchema=z.object({intent:z.enum(['modify','restore','clarify']),scope:z.enum(['current_proposal','policy']).nullable(),constraints:constraintsSchema,question:z.string().nullable(),reason:z.string()}).strict();

// Constrain opaque identifiers at generation time as well as in server verification.
export function modelOutputSchema(role:'customer'|'merchant',ids:string[],categoryNames:string[],staleMerchant=false,grounding:{skuOnlyExclusions?:boolean;customerScopeBoundary?:boolean;clarificationCount?:number}={}){
 if(!ids.length||!categoryNames.length)throw new Error('EMPTY_MODEL_CATALOG');
 const sku=z.enum(ids as [string,...string[]]);
 if(role==='customer'){
  if(grounding.customerScopeBoundary){
   return customerOutputSchema.extend({action:grounding.clarificationCount===2?z.literal('unidentified'):z.enum(['ask_clarification','unidentified']),candidates:z.array(customerOutputSchema.shape.candidates.element.extend({id:sku})).max(0),question:grounding.clarificationCount===2?z.null():z.string().nullable()});
  }
  const candidate=customerOutputSchema.shape.candidates.element.extend({id:sku});
  const grounded=z.union([candidate.extend({kind:z.literal('exact'),unknownConditions:z.array(z.string()).max(0)}),candidate.extend({kind:z.enum(['confirm','alternative'])})]);
  return customerOutputSchema.extend({candidates:z.array(grounded).max(6)});
 }
 // A known stale proposal can only request a fresh review, never draft an edit or undo.
 if(staleMerchant)return merchantOutputSchema.extend({intent:z.literal('clarify'),scope:z.null(),constraints:z.object({budgetLimitKrw:z.null(),excludeCategories:z.array(z.string()).max(0),excludeProductIds:z.array(z.string()).max(0),maxQuantity:z.null(),restorePrevious:z.literal(false)}).strict(),question:z.string().min(1).max(300)});
 return merchantOutputSchema.extend({constraints:constraintsSchema.extend({excludeProductIds:z.array(sku).max(60),excludeCategories:z.array(z.enum(categoryNames as [string,...string[]])).max(grounding.skuOnlyExclusions?0:30)})});
}
