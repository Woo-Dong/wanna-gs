import type { DemoClient,DemoCommand,DemoSnapshot,Result } from '../contracts/domain';
export type DemoScenario='normal'|'minimum'|'shortage'|'paymentFailure'|'pickupReady'|'pickupExpired';
/** Explicit demo reset/preset, implemented through the same validated commands as UI. */
export async function loadDemoScenario(client:DemoClient,initial:DemoSnapshot,scenario:DemoScenario,confirmed:boolean):Promise<Result<DemoSnapshot>>{
  if(!confirmed||initial.actor.role!=='merchant')return {ok:false,error:{code:'FORBIDDEN',message:'경영주 데모 도구에서 초기화를 확인해 주세요.',retryable:false}};
  let snapshot=initial;
  const scope=()=>({sessionId:snapshot.session.id,generation:snapshot.session.generation,actorId:snapshot.actor.id,roleEpoch:snapshot.roleEpoch});
  async function send(command:DemoCommand){const id=crypto.randomUUID();const result=await client.dispatch(command,{...scope(),commandId:id,correlationId:id});if(!result.ok)throw result.error;snapshot=result.data.snapshot;return result.data}
  async function role(actor:string){const result=await client.switchRole(actor,scope());if(!result.ok)throw result.error;snapshot=result.data}
  try{const merchant=initial.actor.id,storeId=initial.actor.storeId!;await send({type:'demo.reset',confirmed:true});const condition=snapshot.conditions.find(c=>c.storeId===storeId)!;
    if(scenario==='minimum')await send({type:'demo.updateCondition',storeId,sku:condition.sku,expectedConditionVersion:condition.version,patch:{minimumOrderQty:6,orderMultiple:6}});
    const customer=snapshot.actors.find(a=>a.role==='customer')!;
    if(scenario==='paymentFailure')await send({type:'demo.setPaymentOutcome',actorId:customer.id,outcomes:['failure','success']});
    await role(customer.id);const c=snapshot.conditions.find(c=>c.storeId===storeId&&c.sku===condition.sku)!;
    await send({type:'request.create',sku:c.sku,storeId,quantity:scenario==='shortage'?3:1,acceptedPriceKrw:c.salePriceKrw,conditionVersion:c.version,consent:{accepted:true,termsVersion:'demo-terms-v1'}});
    await role(merchant);await send({type:'merchant.review',storeId});
    if(scenario==='normal'||scenario==='minimum')return {ok:true,data:snapshot};
    const proposal=snapshot.proposals.filter(p=>p.status==='draft').at(-1)!;await send({type:'proposal.approve',proposalId:proposal.id,expectedProposalVersion:proposal.version,confirmed:true});const line=snapshot.orders.at(-1)!.lines[0];
    await send({type:'demo.confirmSupply',lineId:line.id,confirmedQty:scenario==='shortage'?2:line.orderedQty});
    if(scenario==='pickupReady'||scenario==='pickupExpired')await send({type:'demo.receive',lineId:line.id,receivedQty:line.orderedQty});
    if(scenario==='pickupExpired')await send({type:'demo.advanceTime',deltaMs:172800000});
    return {ok:true,data:snapshot};
  }catch(error){return {ok:false,error:error as {code:string;message:string;retryable:boolean}}}
}
