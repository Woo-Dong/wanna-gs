import type { MerchantConstraints } from '../../contracts/assistant';
import type { ProposalChange,ProposalView } from '../../contracts/domain';
export function proposalChange(current:ProposalView,changes:MerchantConstraints):ProposalChange{
 // ADR005: a configured cap is not the current computed line quantity.
 // Include deferred/prior capped SKUs so a budget edit cannot restore them uncapped.
 const cappedSkus=new Set([...current.lines.map(line=>line.sku),...current.deferred.map(line=>line.sku),...Object.keys(current.constraints.maxQuantities||{})]);
 return { ...current.constraints,scope:'once',
 ...(changes.budgetLimitKrw!==null?{budgetCapKrw:changes.budgetLimitKrw}:{}),
 ...(changes.excludeCategories.length?{excludeCategories:[...new Set([...(current.constraints.excludeCategories||[]),...changes.excludeCategories])]}:{}),
 ...(changes.excludeProductIds.length?{excludeSkus:[...new Set([...(current.constraints.excludeSkus||[]),...changes.excludeProductIds])]}:{}),
 ...(changes.maxQuantity!==null?{maxQuantities:Object.fromEntries([...cappedSkus].map(sku=>[sku,changes.maxQuantity!]))}:{})};
}
export function toModelConstraints(proposal:ProposalView|null):MerchantConstraints|null{
 if(!proposal)return null;const q=Object.values(proposal.constraints.maxQuantities||{});
 return {budgetLimitKrw:proposal.constraints.budgetCapKrw??null,excludeCategories:proposal.constraints.excludeCategories||[],excludeProductIds:proposal.constraints.excludeSkus||[],maxQuantity:q.length&&new Set(q).size===1?q[0]:null,restorePrevious:false};
}
export const krw=(n:number)=>new Intl.NumberFormat('ko-KR').format(n)+'원';
export const date=(n:number|null)=>n===null?'아직 없음':new Intl.DateTimeFormat('ko-KR',{timeZone:'Asia/Seoul',month:'numeric',day:'numeric',hour:'2-digit',minute:'2-digit',hour12:false}).format(n);
