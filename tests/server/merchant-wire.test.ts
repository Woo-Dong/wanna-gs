import {PROMPT_VERSION} from '../../src/server/prompts';
import test from 'node:test';import assert from 'node:assert/strict';import {z}from'zod';
import {modelOutputSchema}from'../../src/server/schemas';import {canonicalMerchant}from'../../src/server/merchant-wire';import {interpret,verifyMerchant}from'../../src/server/assistant';import {catalogContext,catalogHash,categories}from'../../src/server/catalog';import {packIds}from'../../src/server/packing';import {AssistantError}from'../../src/server/provider';import {merchantWireFixture as wire}from'./merchant-wire.fixture';
const empty={budgetLimitKrw:null,excludeCategories:[],excludeProductIds:[],maxQuantity:null,restorePrevious:false};
const restore={intent:'restore' as const,scope:'current_proposal' as const,constraints:{...empty,restorePrevious:true},question:null,reason:'직전 조건 복원'};
const clarify={intent:'clarify' as const,scope:null,constraints:empty,question:'어떤 조건인가요?',reason:'조건 확인'};
const modify={intent:'modify' as const,scope:'current_proposal' as const,constraints:{...empty,budgetLimitKrw:50000,maxQuantity:2},question:null,reason:'변경 제안'};
const schema=()=>modelOutputSchema('merchant',packIds(catalogContext.map(p=>p.id)),categories);
const usage={inputTokens:100,outputTokens:30,totalTokens:130,estimatedCostUsd:0.000088};
const base={sessionId:'s',generation:1,actorId:'a',roleEpoch:1,requestId:'r',conversationId:'c',inputRevision:1,catalogHash,text:'이전 변경 취소',history:[],state:{storeId:'store',proposalId:'proposal',proposalVersion:1,currentProposalVersion:1,stale:false,dailyBudgetKrw:50000,currentConstraints:empty,previousConstraints:{...empty,maxQuantity:2},groups:[]}};
test('restore and clarify cross-field gaps fail generation; no post-output correction',()=>{
 const s=schema();const invalid=[{...restore,scope:'policy'},{...restore,question:'복원할까요?'},{...restore,constraints:{...restore.constraints,maxQuantity:2}},{...restore,constraints:{...restore.constraints,restorePrevious:false}},{...clarify,scope:'current_proposal'},{...clarify,constraints:{...empty,budgetLimitKrw:1}},{...clarify,question:null},{...clarify,question:'   '},{...modify,question:'반영할까요?'},{...modify,scope:null},{...modify,constraints:{...modify.constraints,restorePrevious:true}}];
 for(const v of invalid){const before=JSON.stringify(v);assert(!s.safeParse(wire(v)).success);assert.equal(JSON.stringify(v),before)}assert(!s.safeParse(restore).success);
});
test('normal current, policy, SKU/category/mixed, reference copy and restore remain lossless',()=>{
 for(const v of [restore,clarify,modify,{...modify,scope:'policy' as const},{...modify,constraints:{...empty,excludeProductIds:['p0']}},{...modify,constraints:{...empty,excludeCategories:[categories[0]]}},{...modify,scope:'policy' as const,constraints:{...empty,budgetLimitKrw:50000,maxQuantity:2,excludeProductIds:['p0'],excludeCategories:[categories[0]]}}]){
  const parsed=schema().safeParse(wire(v));assert(parsed.success);assert.deepEqual(canonicalMerchant(wire(v)),v);assert.strictEqual(canonicalMerchant(wire(v)),v);
 }
 const grounded=modelOutputSchema('merchant',['p0'],categories,false,{skuOnlyExclusions:true});assert(grounded.safeParse(wire({...modify,constraints:{...empty,excludeProductIds:['p0']}})).success);assert(!grounded.safeParse(wire({...modify,constraints:{...empty,excludeProductIds:['p0'],excludeCategories:[categories[0]]}})).success);
 const stale=modelOutputSchema('merchant',['p0'],categories,true);assert(stale.safeParse(wire(clarify)).success);assert(!stale.safeParse(wire(restore)).success);assert(!stale.safeParse(wire(modify)).success);
});
test('existing empty-modify, duplicate, unknown and prior-state verification are not weakened',async()=>{
 const emptyModify={...modify,constraints:empty};assert(schema().safeParse(wire(emptyModify)).success);assert.throws(()=>verifyMerchant(emptyModify));
 for(const value of [emptyModify,{...modify,constraints:{...empty,excludeProductIds:['p0','p0']}}])await assert.rejects(interpret('merchant',base,async()=>({value:wire(value),model:'mock',usage})),(e:unknown)=>e instanceof AssistantError&&e.diagnostic==='OUTPUT_CONTRACT'&&e.attempt?.usage===usage);
 assert(!schema().safeParse(wire({...modify,constraints:{...empty,excludeProductIds:['p9999']}})).success);
 await assert.rejects(interpret('merchant',{...base,state:{...base.state,previousConstraints:null}},async()=>({value:wire(restore),model:'mock',usage})),(e:unknown)=>e instanceof AssistantError&&e.diagnostic==='OUTPUT_CONTRACT'&&e.attempt?.usage===usage);
 const result=await interpret('merchant',base,async()=>({value:wire(restore),model:'mock',usage}));assert(result.ok);assert.deepEqual(result.data.result,restore);
 await assert.rejects(interpret('merchant',base,async()=>({value:wire({...restore,question:'아닌 질문'}),model:'mock',usage})),(e:unknown)=>e instanceof AssistantError&&e.diagnostic==='SUPPLIED_CATALOG_SCHEMA'&&e.attempt?.usage===usage);
});
function inspect(value:any):number{if(!value||typeof value!=='object')return 0;let n=Array.isArray(value.enum)?value.enum.length:0;if(value.type==='object'){assert.equal(value.additionalProperties,false);assert.deepEqual([...value.required].sort(),Object.keys(value.properties).sort())}for(const key of ['allOf','not','if','then','else','dependentRequired','dependentSchemas'])assert(!(key in value));for(const child of Object.values(value))if(Array.isArray(child)){for(const item of child)n+=inspect(item)}else n+=inspect(child);return n}
test('full catalog merchant strict nested anyOf stays below enum limit, customer schema stays at996',()=>{
 const j=z.toJSONSchema(schema())as any;assert.equal(j.type,'object');assert(!j.anyOf);assert.equal(j.properties.decision.anyOf.length,3);assert.equal(inspect(j),248+categories.length+2);assert(inspect(j)<1000);
 const c=z.toJSONSchema(modelOutputSchema('customer',packIds(catalogContext.map(p=>p.id)),categories));assert.equal(inspect(c),996);
});
test('actual installed SDK sends nested merchant union and returns untouched canonical restore/mixed policy',async()=>{
 const saved={fetch:globalThis.fetch,key:process.env.OPENAI_API_KEY,mode:process.env.LLM_MODE,model:process.env.OPENAI_MODEL};let calls=0;let answer:any=restore;
 try{process.env.OPENAI_API_KEY='unit-test-key-not-real';process.env.LLM_MODE='live';process.env.OPENAI_MODEL='gpt-4.1-mini-2025-04-14';
  globalThis.fetch=async(_url,init)=>{calls++;const body=JSON.parse(String(init?.body));assert.equal(body.text.format.strict,true);assert.equal(body.text.format.schema.type,'object');assert(body.text.format.schema.properties.decision.anyOf);assert(inspect(body.text.format.schema)<1000);assert.equal(body.store,false);assert.equal(body.max_output_tokens,3200);assert(!('reasoning'in body));return new Response(JSON.stringify({id:'mock',object:'response',created_at:0,status:'completed',model:body.model,output:[{id:'message',type:'message',status:'completed',role:'assistant',content:[{type:'output_text',text:JSON.stringify(wire(answer)),annotations:[]}]}],usage:{input_tokens:100,output_tokens:30,total_tokens:130}}),{status:200,headers:{'Content-Type':'application/json'}})};
  for(const value of [restore,{...modify,scope:'policy',constraints:{...modify.constraints,excludeProductIds:['p0'],excludeCategories:[categories[0]]}}]){answer=value;const result=await interpret('merchant',{...base,text:'앞으로도 이 조건을 유지',history:[{role:'assistant',content:JSON.stringify(modify)}]});assert(result.ok);assert.deepEqual(result.data.result,{...value,constraints:{...value.constraints,excludeProductIds:value.constraints.excludeProductIds.map(id=>id==='p0'?catalogContext[0].id:id)}});assert.equal(result.data.usage.totalTokens,130);assert.equal(result.data.promptVersion,PROMPT_VERSION)}
  assert.equal(calls,2);
 }finally{globalThis.fetch=saved.fetch;for(const[name,value]of[['OPENAI_API_KEY',saved.key],['LLM_MODE',saved.mode],['OPENAI_MODEL',saved.model]]as const){if(value===undefined)delete process.env[name];else process.env[name]=value}}
});
