import test from 'node:test';
import assert from 'node:assert/strict';
import {z} from 'zod';
import {interpret} from '../../src/server/assistant';
import {catalogHash} from '../../src/server/catalog';
import {AssistantError,type ModelProvider} from '../../src/server/provider';
import {modelOutputSchema} from '../../src/server/schemas';
const empty={budgetLimitKrw:null,excludeCategories:[],excludeProductIds:[],maxQuantity:null,restorePrevious:false};
const clarify={intent:'clarify',scope:null,constraints:empty,question:'최신 검토안을 다시 확인해 주세요.',reason:'검토안이 변경되었어요.'};
const restore={intent:'restore',scope:'current_proposal',constraints:{...empty,restorePrevious:true},question:null,reason:'이전 변경을 복원하는 제안이에요.'};
const modify={intent:'modify',scope:'current_proposal',constraints:{...empty,budgetLimitKrw:40000},question:null,reason:'이번 검토 예산만 변경해요.'};
const usage={inputTokens:123,outputTokens:45,totalTokens:168,estimatedCostUsd:0.0001212};
const base={sessionId:'test-session',generation:1,actorId:'merchant',roleEpoch:1,requestId:'stale-check',conversationId:'test-conversation',inputRevision:1,catalogHash,text:'이전 검토안을 그대로 적용해 주세요',history:[],state:{storeId:'test-store',proposalId:'test-proposal',proposalVersion:7,currentProposalVersion:7,stale:false,dailyBudgetKrw:100000,currentConstraints:empty,previousConstraints:{...empty,budgetLimitKrw:50000},groups:[]}};
test('stale metadata restricts generation to clarification with no editable constraints',async()=>{
 for(const delta of [{stale:true},{currentProposalVersion:8},{stale:true,proposalVersion:null,currentProposalVersion:null},{stale:true,currentProposalVersion:7}]){
  let called=0;
  const provider:ModelProvider=async(_prompt,_input,schema)=>{called++;assert(schema.safeParse(clarify).success);assert(!schema.safeParse(restore).success);assert(!schema.safeParse(modify).success);for(const constraints of [{...empty,budgetLimitKrw:1},{...empty,maxQuantity:1},{...empty,excludeCategories:['음료']},{...empty,excludeProductIds:['p0']},{...empty,restorePrevious:true}])assert(!schema.safeParse({...clarify,constraints}).success);return {value:clarify,model:'test-live-provider',usage}};
  const response=await interpret('merchant',{...base,state:{...base.state,...delta}},provider);
  assert(response.ok);assert.deepEqual(response.data.result,clarify);assert.deepEqual(response.data.usage,usage);assert.equal(called,1);
 }
});
test('fresh and unspecified versions preserve normal undo and edits',async()=>{
 for(const delta of [{},{stale:false},{currentProposalVersion:undefined},{proposalVersion:null,currentProposalVersion:8},{currentProposalVersion:null}]){
  for(const value of [restore,modify]){
   const provider:ModelProvider=async(_prompt,_input,schema)=>{assert(schema.safeParse(restore).success);assert(schema.safeParse(modify).success);return {value,model:'test-live-provider',usage}};
   const response=await interpret('merchant',{...base,state:{...base.state,...delta}},provider);assert(response.ok);assert.deepEqual(response.data.result,value);
  }
 }
});
test('a nonconforming stale model answer is rejected with its paid usage, never silently rewritten',async()=>{
 const provider:ModelProvider=async()=>({value:restore,model:'test-live-provider',usage});
 await assert.rejects(interpret('merchant',{...base,state:{...base.state,stale:true}},provider),(e:unknown)=>e instanceof AssistantError&&e.code==='INVALID_MODEL_RESPONSE'&&e.diagnostic==='SUPPLIED_CATALOG_SCHEMA'&&e.attempt?.providerCalled===true&&e.attempt.usage?.totalTokens===168);
});
test('stale merchant schema is strict JSON schema; customer generation is unchanged',()=>{
 const s=modelOutputSchema('merchant',['p0'],['음료'],true);const j=z.toJSONSchema(s) as any;
 assert.equal(j.properties.intent.const,'clarify');assert.equal(j.properties.scope.type,'null');assert.equal(j.properties.constraints.properties.restorePrevious.const,false);assert.equal(j.properties.constraints.additionalProperties,false);assert.deepEqual(j.required,['intent','scope','constraints','question','reason']);
 assert(!s.safeParse({...clarify,question:null}).success);assert(!s.safeParse({...clarify,question:''}).success);
 assert.deepEqual(z.toJSONSchema(modelOutputSchema('customer',['p0'],['음료'],false)),z.toJSONSchema(modelOutputSchema('customer',['p0'],['음료'],true)));
});
