// Test responses only. Values (including intentional invalid ones) are not repaired.
export function customerWireFixture(value:any):any{
 const {candidates,...decision}=value;
 const wrap=(c:any)=>c===undefined?undefined:({id:c.id,assessment:Object.fromEntries(Object.entries(c).filter(([key])=>key!=='id'))});
 return {decision:value.action==='show_candidates'?{...decision,primaryCandidate:wrap(candidates[0]),additionalCandidates:candidates.slice(1).map(wrap)}:{...decision,candidates:candidates.map(wrap)}};
}
