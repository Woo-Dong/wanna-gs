import test from 'node:test';
import assert from 'node:assert/strict';
import {interpret} from '../../src/server/assistant';
import {catalogContext,catalogHash} from '../../src/server/catalog';
import {CUSTOMER_PROMPT,PROMPT_VERSION} from '../../src/server/prompts';
import {customerWireFixture as wire} from './customer-wire.fixture';
import type {CustomerInterpretation} from '../../src/contracts/assistant';

// Synthetic branch-compatibility checks: the response is injected, so these do
// not measure whether a live model correctly classifies any of these inputs.
const base={sessionId:'classification-fixture',generation:1,actorId:'synthetic-customer',roleEpoch:1,requestId:'fixture-request',conversationId:'fixture-dialogue',inputRevision:1,catalogHash,history:[],clarificationCount:0};
const usage={inputTokens:100,outputTokens:30,totalTokens:130,estimatedCostUsd:.000088};
const known=catalogContext[0];
type Scenario={name:string;text:string;action:CustomerInterpretation['action'];kinds:('exact'|'confirm'|'alternative')[];count?:number;history?:{role:'user'|'assistant';content:string}[]};
const scenarios:Scenario[]=[
 {name:'clear known identity',text:known.name+' 찾아주세요',action:'show_candidates',kinds:['exact']},
 {name:'recognizable typo branch remains available',text:known.name+' 찾어주세요',action:'show_candidates',kinds:['exact']},
 {name:'known identity with unverified allergy condition',text:known.name+' 땅콩 알레르기가 있어도 먹을 수 있나요?',action:'show_candidates',kinds:['confirm']},
 {name:'broad description needs a useful question',text:'시원하게 마실 걸 찾는데 어떤 종류인지는 아직 모르겠어요',action:'ask_clarification',kinds:[]},
 {name:'plausible multiple identities remain available',text:'두 맛 중 어떤 것이었는지 기억이 안 나요',action:'ask_clarification',kinds:['confirm','confirm']},
 {name:'named original unknown and substitutes refused',text:'합성테스트 전용 별마을 가상과자를 찾는데 다른 상품은 싫어요',action:'unidentified',kinds:[]},
 {name:'explicit alternatives preserve labelled alternatives',text:'합성테스트 전용 별마을 가상과자가 없으면 비슷한 다른 상품도 알려주세요',action:'unidentified',kinds:['alternative']},
 {name:'real operation cannot become a transaction',text:'실제 카드로 결제해 주세요',action:'ask_clarification',kinds:[]},
 {name:'noise clarifies without an invented product',text:'ㅁㄴㅇ ㄱㅂㅈ ㅌㅋ',action:'ask_clarification',kinds:[]},
 {name:'question limit retains plausible uncertainty',text:'두 맛 중 어떤 것이었는지 아직 모르겠어요',action:'show_candidates',kinds:['confirm','confirm'],count:2},
 {name:'question limit with no identity',text:'합성테스트 전용 별마을 가상과자만 원해요',action:'unidentified',kinds:[],count:2},
 {name:'question limit with external operation',text:'실제 카드로 결제해 주세요',action:'unidentified',kinds:[],count:2},
 {name:'latest explicit correction remains usable',text:'아니요, '+known.name+' 제품으로 정정할게요',action:'show_candidates',kinds:['exact'],history:[{role:'user',content:'합성테스트 전용 별마을 가상과자를 찾고 다른 상품은 싫어요'}]},
];
test('synthetic action matrix preserves legal branches, uncertainty, alternatives and corrections losslessly',async()=>{
 for(const scenario of scenarios){let calls=0;let expected:CustomerInterpretation|undefined;
  const result=await interpret('customer',{...base,text:scenario.text,clarificationCount:scenario.count??0,history:scenario.history??[]},async(prompt,input,schema)=>{
   calls++;assert.equal(prompt,CUSTOMER_PROMPT);const payload=JSON.parse(input);assert.equal(payload.text,scenario.text);assert.equal(payload.context.clarificationCount,scenario.count??0);
   assert.equal(payload.history.length,scenario.history?.length??0);
   const candidates=scenario.kinds.map((kind,i)=>({id:payload.catalog.rows[i][0] as string,kind,sharedEvidence:['합성 응답의 관측 근거'],differences:kind==='alternative'?['원래 요청과 다른 상품']:[],unknownConditions:kind==='confirm'?['합성 응답의 미확인 조건']:[]}));
   const canonical={action:scenario.action,candidates,question:scenario.action==='ask_clarification'?'어떤 종류나 맛을 원하세요?':null,reason:'분류 계약을 검사하는 합성 응답입니다.',confirmationRequired:true as const};
   const response=wire(canonical);assert(schema.safeParse(response).success,scenario.name);
   expected={...canonical,candidates:candidates.map(c=>({...c,id:catalogContext[Number(c.id.slice(1))].id}))};
   return {value:response,model:'injected-fixture',usage};
  },'fixture');
  assert(result.ok,scenario.name);assert.equal(calls,1,scenario.name);assert.equal(result.data.mode,'fixture');assert.equal(result.data.promptVersion,PROMPT_VERSION);assert.deepEqual(result.data.result,expected,scenario.name);assert.deepEqual(result.data.usage,usage);
 }
});
test('actual SDK carries one customer instruction and one structured response without a classification side call',async()=>{
 const saved={fetch:globalThis.fetch,key:process.env.OPENAI_API_KEY,mode:process.env.LLM_MODE,model:process.env.OPENAI_MODEL};let calls=0;
 try{
  process.env.OPENAI_API_KEY='unit-test-key-not-real';process.env.LLM_MODE='live';process.env.OPENAI_MODEL='gpt-4.1-mini-2025-04-14';
  globalThis.fetch=async(_url,init)=>{calls++;const sent=JSON.parse(String(init?.body));assert.equal(sent.instructions,CUSTOMER_PROMPT);assert.equal(sent.store,false);assert.equal(sent.text.format.strict,true);assert.equal(sent.max_output_tokens,3200);assert(!('reasoning'in sent));assert.deepEqual(Object.keys(sent.text.format.schema.properties),['decision']);
   const value=wire({action:'unidentified',candidates:[],question:null,reason:'합성 응답: 식별할 수 없습니다.',confirmationRequired:true});
   return new Response(JSON.stringify({id:'mock',object:'response',created_at:0,status:'completed',model:sent.model,output:[{id:'message',type:'message',status:'completed',role:'assistant',content:[{type:'output_text',text:JSON.stringify(value),annotations:[]}]}],usage:{input_tokens:100,output_tokens:30,total_tokens:130}}),{status:200,headers:{'Content-Type':'application/json'}});
  };
  const result=await interpret('customer',{...base,text:'합성테스트 전용 별마을 가상과자만 원해요'});assert(result.ok);assert.equal(calls,1);assert('action' in result.data.result);assert.equal(result.data.result.action,'unidentified');assert.equal(result.data.usage.totalTokens,130);assert.equal(result.data.promptVersion,PROMPT_VERSION);
 }finally{globalThis.fetch=saved.fetch;for(const[name,value]of[['OPENAI_API_KEY',saved.key],['LLM_MODE',saved.mode],['OPENAI_MODEL',saved.model]]as const){if(value===undefined)delete process.env[name];else process.env[name]=value}}
});
