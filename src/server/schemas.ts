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
export function modelOutputSchema(role:'customer'|'merchant',ids:string[],categoryNames:string[]){
 if(!ids.length||!categoryNames.length)throw new Error('EMPTY_MODEL_CATALOG');
 const sku=z.enum(ids as [string,...string[]]);
 if(role==='customer')return customerOutputSchema.extend({candidates:z.array(customerOutputSchema.shape.candidates.element.extend({id:sku})).max(6)});
 return merchantOutputSchema.extend({constraints:constraintsSchema.extend({excludeProductIds:z.array(sku).max(60),excludeCategories:z.array(z.enum(categoryNames as [string,...string[]])).max(30)})});
}
