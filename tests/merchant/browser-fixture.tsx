import {useState} from 'react';import {createRoot} from 'react-dom/client';
import {MerchantView} from '../../src/components/merchant/MerchantView';
import type {DemoClient,DemoCommand,DemoSnapshot,CommandContext,ProposalChange} from '../../src/contracts/domain';
import type {MerchantInterpretation} from '../../src/contracts/assistant';
import {fixtureSnapshot,NOW} from './fixture';
let state=fixtureSnapshot();const commands:{command:DemoCommand;context:CommandContext}[]=[];let prior:ProposalChange|null=null;
const control={commands,searches:0,scenario:'normal',requests:[] as unknown[],update:null as null|((s:DemoSnapshot)=>void),snapshot:()=>state,patch(patch:Partial<DemoSnapshot>){state={...state,...structuredClone(patch)};this.update?.(state)}};
Object.assign(window,{merchantFixture:control});
window.fetch=async(_url,init)=>{control.searches++;const b=JSON.parse(String(init?.body));control.requests.push(b);if(control.scenario==='slow')await new Promise(r=>setTimeout(r,300));if(control.scenario==='error')return new Response(JSON.stringify({ok:false,error:{code:'TIMEOUT',message:'모의 공급자 시간 초과',retryable:true,attempt:{providerCalled:true,model:'mock-provider',usage:null,latencyMs:10000,mode:'live'}}}),{status:503});
 const result:MerchantInterpretation={intent:b.text.includes('되돌')?'restore':'modify',scope:b.text.includes('앞으로')?'policy':'current_proposal',constraints:{budgetLimitKrw:b.text.includes('5만')?50000:null,excludeCategories:b.text.includes('음료')?['음료']:[],excludeProductIds:[],maxQuantity:b.text.includes('3개')?3:null,restorePrevious:b.text.includes('되돌')},question:null,reason:'독립 검증용 합성 해석'};
 return new Response(JSON.stringify({ok:true,data:{...b,result,mode:'fixture',model:'fixture',promptVersion:'independent-fixture-v1',catalogVersion:'fixture10',usage:{inputTokens:0,outputTokens:0,totalTokens:0,estimatedCostUsd:0},latencyMs:5}}),{status:200})};
const client:DemoClient={initialize:async()=>({ok:true,data:state}),snapshot:async()=>({ok:true,data:state}),query:async()=>({ok:true,data:[]}),switchRole:async()=>({ok:true,data:state}),subscribe:()=>()=>{},dispatch:async(command,context)=>{
 commands.push({command,context});state=structuredClone(state);const p=state.proposals[0];
 if(command.type==='merchant.review'){p.version++;p.sourceFingerprint='reviewed'}
 if(command.type==='proposal.revise'){prior=p.constraints;p.constraints=command.change;p.version++;}
 if(command.type==='proposal.undo'){p.constraints=prior??{scope:'once'};p.version++;}
 if(command.type==='proposal.approve'){p.status='approved';p.orderId='order0';state.orders.push({id:'order0',storeId:'s0',status:'submitted',approvalType:'manual',policyVersion:1,budgetDay:'fixture',createdAt:NOW,lines:p.lines.map((l,i)=>({id:`line${i}`,sku:l.sku,orderedQty:l.quantity,confirmedQty:null,receivedQty:null,salePriceKrw:l.salePriceKrw,purchaseCostKrw:l.purchaseCostKrw,conditionVersion:1,supplyConfirmedAt:null,receivedAt:null}))});}
 if(command.type==='policy.update'){Object.assign(state.policies[0],command,{version:state.policies[0].version+1,approvedBy:'m0',approvedAt:NOW})}
 if(command.type==='demo.confirmSupply'){const l=state.orders.flatMap(o=>o.lines).find(l=>l.id===command.lineId)!;l.confirmedQty=command.confirmedQty;l.supplyConfirmedAt=NOW;state.orders[0].status='supply_confirmed';const r=state.requests.find(r=>r.sku===l.sku)!;r.status='reserved';r.reservation={id:'reservation0',code:'FIXTURE-0001',status:'confirmed',quantity:r.quantity,totalKrw:r.quantity*r.acceptedPriceKrw,holdExpiresAt:null,pickupAvailableAt:null,pickupDeadlineAt:null,collectedAt:null};r.payments=[{id:'payment0',cycle:1,attempt:1,status:'succeeded',amountKrw:r.quantity*r.acceptedPriceKrw,createdAt:NOW}];r.consent.status='not_applicable_paid';}
 if(command.type==='demo.receive'){const l=state.orders.flatMap(o=>o.lines).find(l=>l.id===command.lineId)!;l.receivedQty=command.receivedQty;l.receivedAt=NOW;const r=state.requests.find(r=>r.sku===l.sku)!;if(r.reservation){r.reservation.status='pickup_ready';r.reservation.pickupAvailableAt=NOW;r.reservation.pickupDeadlineAt=NOW+48*3600000;}}
 if(command.type==='merchant.collect'){const r=state.requests.find(r=>r.reservation?.code===command.reservationCode);if(r?.reservation){r.reservation.status='collected';r.reservation.collectedAt=NOW;}}
 state.session.revision++;return {ok:true,data:{commandId:context.commandId,effect:'applied',revision:state.session.revision,entityIds:[],eventIds:[],snapshot:state}};
}};
function App(){const [value,setValue]=useState(state);control.update=setValue;return <main><div className="fixture-banner">M01 독립 브라우저 fixture · 모델/DB/거래 합성 · 앱 shell 아님</div><MerchantView snapshot={value} client={client} onSnapshot={setValue}/></main>}
createRoot(document.getElementById('root')!).render(<App/>);
