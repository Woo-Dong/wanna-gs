import test from 'node:test';
import assert from 'node:assert/strict';
import { interpret,verifyCustomer,verifyMerchant,handleAssistant } from '../../src/server/assistant';
import { catalogHash,products } from '../../src/server/catalog';
import { AssistantError,type ModelProvider } from '../../src/server/provider';
const envelope={sessionId:'s1',generation:1,actorId:'a1',roleEpoch:1,requestId:'r1',conversationId:'c1',inputRevision:1,catalogHash};
const input={...envelope,text:products[0].name,history:[],clarificationCount:0};
const candidate={id:products[0].sku,kind:'exact',sharedEvidence:[products[0].name],differences:[],unknownConditions:[]};
const output={action:'show_candidates',candidates:[candidate],question:null,reason:'상품을 확인해 주세요.',confirmationRequired:true};
const fixture:ModelProvider=async()=>({value:{...output,candidates:[{...candidate,id:'p0'}]},model:'explicit-test-fixture',usage:{inputTokens:0,outputTokens:0,totalTokens:0,estimatedCostUsd:null}});
const empty={budgetLimitKrw:null,excludeCategories:[],excludeProductIds:[],maxQuantity:null,restorePrevious:false};
test('normal identification is a candidate requiring customer confirmation; no transaction operation',async()=>{
 const r=await interpret('customer',input,fixture,'fixture');assert(r.ok);assert.equal(r.data.mode,'fixture');assert.deepEqual(r.data.result,output);assert.equal(r.data.requestId,'r1');
});
test('invalid/catalog-stale/provider override rejected before a paid call',async()=>{
 let calls=0;const provider:ModelProvider=async(...args)=>{calls++;return fixture(...args)};
 for(const value of [{...input,catalogHash:'0'.repeat(64)},{...input,provider:'fake'},{...input,text:''},{...input,generation:NaN}])await assert.rejects(interpret('customer',value,provider),AssistantError);
 assert.equal(calls,0);
});
test('fake SKU, duplicate SKU and arbitrary model confirmation rejected',()=>{
 for(const value of [{...output,candidates:[{...candidate,id:'invented'}]},{...output,candidates:[candidate,candidate]},{...output,confirmationRequired:false},{...output,execute:true}])assert.throws(()=>verifyCustomer(value,0),AssistantError);
});
test('unidentified cannot carry original identification and alternatives cannot masquerade as primary',()=>{
 assert.throws(()=>verifyCustomer({...output,action:'unidentified'},0));
 assert.throws(()=>verifyCustomer({...output,candidates:[{...candidate,kind:'alternative'}]},0));
 assert.equal(verifyCustomer({...output,action:'unidentified',candidates:[{...candidate,kind:'alternative'}]},0).action,'unidentified');
});
test('clarification cap is enforced without rejecting a valid uncertain candidate',()=>{
 assert.throws(()=>verifyCustomer({...output,action:'ask_clarification',question:'어떤 맛인가요?'},2));
 assert.equal(verifyCustomer({...output,candidates:[{...candidate,kind:'confirm',unknownConditions:['비건 여부']} ]},2).action,'show_candidates');
 assert.throws(()=>verifyCustomer({...output,candidates:[{...candidate,unknownConditions:['비건 여부']}]},0));
});
test('provider failures stay operational errors, never unknown needs',async()=>{
 await assert.rejects(interpret('customer',input,async()=>{throw new AssistantError('RATE_LIMITED','later',true,429)}),e=>e instanceof AssistantError&&e.code==='RATE_LIMITED');
});
test('merchant scope and exact constraints are preserved as proposal only',()=>{
 const r=verifyMerchant({intent:'modify',scope:'current_proposal',constraints:{...empty,budgetLimitKrw:50000},question:null,reason:'이번 묶음에만 적용해요.'});assert.equal(r.constraints.budgetLimitKrw,50000);
 assert.equal(verifyMerchant({...r,scope:'policy'}).scope,'policy');
 assert.throws(()=>verifyMerchant({...r,constraints:empty}));
 assert.throws(()=>verifyMerchant({...r,constraints:{...empty,excludeProductIds:['fake']}}));
 assert.throws(()=>verifyMerchant({...r,intent:'clarify',question:'무엇을 바꿀까요?'}));
});
test('restore needs prior history and cannot sneak extra restrictions',async()=>{
 const restore={intent:'restore',scope:'current_proposal',constraints:{...empty,restorePrevious:true},question:null,reason:'이전 변경을 되돌려요.'};
 assert.throws(()=>verifyMerchant({...restore,constraints:{...restore.constraints,budgetLimitKrw:1}}));
 const state={storeId:'store',proposalId:'proposal',proposalVersion:1,dailyBudgetKrw:100000,currentConstraints:empty,previousConstraints:null,groups:[]};
 await assert.rejects(interpret('merchant',{...envelope,text:'아까 뺀 것 다시',history:[],state},async()=>({...(await fixture('','',{} as never,'')),value:restore})),AssistantError);
});
test('HTTP malformed/oversized input fails with sanitized errors and no model',async()=>{
 for(const [body,status] of [['{',400],['x'.repeat(70000),413]] as const){const r=await handleAssistant('customer',new Request('http://localhost/api/product-assistant',{method:'POST',body}));assert.equal(r.status,status);assert.equal(r.headers.get('cache-control'),'no-store');const data=await r.json();assert.equal(data.ok,false);assert(!JSON.stringify(data).includes('OPENAI_API_KEY'))}
});
