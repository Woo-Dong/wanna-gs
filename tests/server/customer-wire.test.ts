import test from 'node:test';import assert from 'node:assert/strict';import {z} from 'zod';
import {modelOutputSchema}from'../../src/server/schemas';import {canonicalCustomer,type CustomerWire}from'../../src/server/customer-wire';import {interpret,verifyCustomer}from'../../src/server/assistant';
import {catalogContext,catalogHash,categories}from'../../src/server/catalog';import {packIds}from'../../src/server/packing';import {AssistantError}from'../../src/server/provider';import {customerWireFixture as wire}from'./customer-wire.fixture';
const ids=packIds(catalogContext.map(p=>p.id));const schema=(count=0,boundary=false)=>modelOutputSchema('customer',ids,categories,false,{clarificationCount:count,customerScopeBoundary:boundary});
const candidate=(i=0,kind='exact')=>({id:ids[i],kind,sharedEvidence:['실제 관측 속성'],differences:kind==='alternative'?['다른 상품']:[],unknownConditions:kind==='confirm'?['알레르기 성분 미확인']:[]});
const show={action:'show_candidates',candidates:[candidate()],question:null,reason:'확인해 주세요.',confirmationRequired:true};
const usage={inputTokens:120,outputTokens:50,totalTokens:170,estimatedCostUsd:.000128};
const base={sessionId:'wire-session',generation:1,actorId:'customer',roleEpoch:1,requestId:'wire-request',conversationId:'wire-conversation',inputRevision:1,catalogHash,text:'간식 상품을 찾아요',history:[],clarificationCount:0};

test('generation rejects all three C7 action mismatches without repairing any fields',()=>{
 for(const canonical of [{...show,question:'고르실래요?'},{...show,question:''},{...show,candidates:[]},{...show,candidates:[candidate(0,'alternative')]}])assert(!schema().safeParse(wire(canonical)).success);
 assert(!schema().safeParse(show).success,'old outer format is not silently accepted');
});
test('normal single/multiple primary, uncertain conditions, clarification and unidentified are lossless',()=>{
 const cases=[show,{...show,candidates:[candidate(0,'confirm')]},{...show,candidates:[candidate(),candidate(1,'confirm'),candidate(2,'alternative')]},{...show,candidates:Array.from({length:6},(_,i)=>candidate(i,i===5?'alternative':'confirm'))},{...show,action:'ask_clarification',question:'어떤 맛을 원하세요?',candidates:[candidate(0,'confirm'),candidate(1,'confirm')]},{...show,action:'unidentified',candidates:[]},{...show,action:'unidentified',candidates:[candidate(0,'alternative'),candidate(1,'alternative')]}];
 for(const canonical of cases){const w=wire(canonical),before=structuredClone(w);assert(schema().safeParse(w).success);assert.deepEqual(canonicalCustomer(w),canonical);assert.deepEqual(w,before)}
 assert(!schema().safeParse(wire({...show,candidates:Array.from({length:7},(_,i)=>candidate(i))})).success);
});
test('question bounds and scope branches preserve ordinary candidates but do not allow third questions',()=>{
 const ask={...show,action:'ask_clarification',question:'맛을 알려주세요.',candidates:[]},unknown={...show,action:'unidentified',candidates:[]};
 for(const count of [0,1,2]){assert.equal(schema(count).safeParse(wire(ask)).success,count<2);assert(schema(count).safeParse(wire(show)).success);assert(schema(count).safeParse(wire(unknown)).success);assert(!schema(count,true).safeParse(wire(show)).success);assert.equal(schema(count,true).safeParse(wire(ask)).success,count<2);assert(schema(count,true).safeParse(wire(unknown)).success)}
 for(const question of [null,'','   ','x'.repeat(301)])assert(!schema().safeParse(wire({...ask,question})).success);
 assert(!schema().safeParse(wire({...unknown,candidates:[candidate()]})).success);assert(!schema().safeParse(wire({...unknown,question:'질문'})).success);
});
test('exact unknowns and unknown IDs fail at generation; duplicate IDs still fail canonical verification with paid usage',async()=>{
 assert(!schema().safeParse(wire({...show,candidates:[{...candidate(),unknownConditions:['미확인']}]})).success);
 assert(!schema().safeParse(wire({...show,candidates:[{...candidate(),id:'p99999'}]})).success);
 const duplicate=wire({...show,candidates:[candidate(),candidate()]});assert(schema().safeParse(duplicate).success);
 await assert.rejects(interpret('customer',base,async()=>({value:duplicate,model:'fixture-model',usage})),(e:unknown)=>e instanceof AssistantError&&e.diagnostic==='CANDIDATE_DUPLICATE'&&e.attempt?.usage===usage&&e.attempt.providerCalled===true);
 for(const value of [wire({...show,question:'invalid'}),wire({...show,candidates:[]})])await assert.rejects(interpret('customer',base,async()=>({value,model:'fixture-model',usage})),(e:unknown)=>e instanceof AssistantError&&e.diagnostic==='SUPPLIED_CATALOG_SCHEMA'&&e.attempt?.usage===usage);
 assert.throws(()=>verifyCustomer({...show,candidates:[{...candidate(),id:catalogContext[0].id}],question:'still invalid'},0),(e:unknown)=>e instanceof AssistantError&&e.diagnostic==='CANDIDATE_ACTION_CONTRACT');
});
test('ordinary history and multiple candidate order survive the wire round trip and actual interpret ID unpacking',async()=>{
 const prior={...show,candidates:[{...candidate(),id:catalogContext[0].id}]};
 const expected={...show,candidates:[candidate(2,'confirm'),candidate(1,'alternative'),candidate(0,'confirm')]};
 const result=await interpret('customer',{...base,history:[{role:'assistant',content:JSON.stringify(prior)},{role:'user',content:'다른 맛을 비교해 주세요'}]},async(_p,input,s)=>{const data=JSON.parse(input);assert.deepEqual(JSON.parse(data.history[0].content),show);const value=wire(expected);assert(s.safeParse(value).success);return {value,model:'fixture-model',usage}},'fixture');assert(result.ok);
 assert.deepEqual(result.data.result,{...expected,candidates:expected.candidates.map(c=>({...c,id:catalogContext[ids.indexOf(c.id)].id}))});assert.deepEqual(result.data.usage,usage);
});
function inspect(value:any,counts={enums:0,objects:0}){if(!value||typeof value!=='object')return counts;if(value.enum)counts.enums+=value.enum.length;if(value.type==='object'){counts.objects++;assert.equal(value.additionalProperties,false);assert.deepEqual([...value.required].sort(),Object.keys(value.properties).sort())}for(const key of ['allOf','not','if','then','else','dependentRequired','dependentSchemas'])assert(!(key in value));for(const child of Object.values(value))if(Array.isArray(child))for(const item of child)inspect(item,counts);else if(child&&typeof child==='object')inspect(child,counts);return counts}
test('full248 schema serializes with strict object root, nested anyOf and total enums below1000',()=>{
 const json=z.toJSONSchema(schema()) as any;assert.equal(json.type,'object');assert(!('anyOf'in json));assert(Array.isArray(json.properties.decision.anyOf));const counts=inspect(json);assert.equal(counts.enums,996);assert(counts.enums<=1000);assert(counts.objects>4);
});
test('installed SDK sends exact nested schema with unchanged provider and returns canonical output through mocked fetch',async()=>{
 const saved={fetch:globalThis.fetch,key:process.env.OPENAI_API_KEY,mode:process.env.LLM_MODE,model:process.env.OPENAI_MODEL};let calls=0;let sent:any;
 try{process.env.OPENAI_API_KEY='unit-test-key-not-real';process.env.LLM_MODE='live';process.env.OPENAI_MODEL='gpt-4.1-mini-2025-04-14';
  globalThis.fetch=async(_url,init)=>{calls++;sent=JSON.parse(String(init?.body));const value=wire({...show,candidates:[candidate(0,'confirm'),candidate(1,'alternative')]});return new Response(JSON.stringify({id:'test',object:'response',created_at:0,status:'completed',model:sent.model,output:[{id:'test-message',type:'message',status:'completed',role:'assistant',content:[{type:'output_text',text:JSON.stringify(value),annotations:[]}]}],usage:{input_tokens:120,output_tokens:50,total_tokens:170}}),{status:200,headers:{'Content-Type':'application/json'}})};
  const result=await interpret('customer',base);assert(result.ok);assert.equal(calls,1);assert.equal(sent.text.format.strict,true);assert.equal(sent.text.format.schema.type,'object');assert(!sent.text.format.schema.anyOf);assert(sent.text.format.schema.properties.decision.anyOf);assert.equal(inspect(sent.text.format.schema).enums,996);assert.equal(sent.store,false);assert.equal(sent.max_output_tokens,3200);assert(!('reasoning'in sent));assert('action' in result.data.result);assert.equal(result.data.result.action,'show_candidates');assert.equal((result.data.result as any).candidates.length,2);assert.equal((result.data.result as any).candidates[0].id,catalogContext[0].id);assert.equal(result.data.usage.totalTokens,170);
 }finally{globalThis.fetch=saved.fetch;for(const [key,value]of [['OPENAI_API_KEY',saved.key],['LLM_MODE',saved.mode],['OPENAI_MODEL',saved.model]]as const){if(value===undefined)delete process.env[key];else process.env[key]=value}}
});
