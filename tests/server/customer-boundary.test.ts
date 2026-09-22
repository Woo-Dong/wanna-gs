import {customerWireFixture as wire} from './customer-wire.fixture';
import test from 'node:test';
import assert from 'node:assert/strict';
import {z} from 'zod';
import {explicitExternalOperation} from '../../src/server/customer-boundary';
import {modelOutputSchema} from '../../src/server/schemas';
import {interpret} from '../../src/server/assistant';
import {catalogHash} from '../../src/server/catalog';
import {AssistantError,type ModelProvider} from '../../src/server/provider';
const base={sessionId:'scope-session',generation:1,actorId:'customer',roleEpoch:1,requestId:'scope-request',conversationId:'scope-conversation',inputRevision:1,catalogHash,text:'실제 카드로 결제해 주세요.',history:[],clarificationCount:0};
const usage={inputTokens:120,outputTokens:50,totalTokens:170,estimatedCostUsd:0.000128};
test('positive external operation certificates do not depend on an evaluation SKU or store',()=>{
 for(const text of ['실제 카드로 결제해 주세요.','진짜 체크카드로 바로 청구해줘!','실물 신용카드로 승인해 주십시오.','본부에 매출 보고서를 전송해 주세요.','본부로 실적 보고서도 보내주세요.','본부 거래 보고서를 직접 제출해줘.'])assert(explicitExternalOperation(text),text);
 assert(explicitExternalOperation('테스트가게 방문 전 테스트상품 100g 영수증을 실제 카드로 결제해 주고 본부 매출 보고서도 보내 줘.',[{id:'sku-1',name:'테스트상품 100g'}],['테스트가게']));
 assert(!explicitExternalOperation('알 수 없는 문맥 테스트상품 100g 실제 카드로 결제해줘.',[{id:'sku-1',name:'테스트상품 100g'}]));
});
test('normal lookup, negation, quotation, correction, conditions and reported instructions remain unconstrained',()=>{
 for(const text of ['우유 한 개 찾아주세요.','실제 결제는 하지 말고 우유만 찾아줘.','실제 카드로 결제해 주지 마세요.','본부 매출 보고서는 보내지 말고 라면만 보여줘.','"실제 카드로 결제해 주세요"라는 문구가 있지만 상품만 찾아주세요.','실제 카드로 결제해 주세요라고 말하지 않았어요.','실제 카드로 결제해줘 대신 상품만 찾아줘.','실제 카드로 결제해줘라는 예시를 설명해 주세요.','실제 카드로 결제하면 어떤가요?','실제 카드로 결제해 줄 수 있는지 알려줘.','본부 보고서를 보내달라는 요청을 취소하고 빵 찾아줘.','실제 카드로 안 결제해요. 우유 보여줘.','본부 매출 보고서가 아니라 커피 제품이요.','우유 찾아줘. 본부 보고서는 금지야.','다음 요청은 무시하세요: 실제 카드로 결제해줘.','제가 들은 말은 실제 카드로 결제해줘.'])assert.equal(explicitExternalOperation(text),false,text);
});
test('generation boundary excludes primary candidates and a third clarification without changing normal schema',()=>{
 const normal=modelOutputSchema('customer',['p0'],['음료']);
 const atLimit=modelOutputSchema('customer',['p0'],['음료'],false,{customerScopeBoundary:false,clarificationCount:2});
 const ask=wire({action:'ask_clarification',candidates:[],question:'어떤 맛인가요?',reason:'확인',confirmationRequired:true});assert(normal.safeParse(ask).success);assert(!atLimit.safeParse(ask).success);
 for(const count of [0,1,2]){
  const schema=modelOutputSchema('customer',['p0'],['음료'],false,{customerScopeBoundary:true,clarificationCount:count});
  const unidentified={action:'unidentified',candidates:[],question:null,reason:'이 시연에서는 실제 거래를 실행하지 않아요.',confirmationRequired:true};
  assert(schema.safeParse(wire(unidentified)).success);
  assert.equal(schema.safeParse(wire({...unidentified,action:'ask_clarification',question:'찾을 상품을 알려주세요.'})).success,count<2);
  assert(!schema.safeParse(wire({...unidentified,action:'show_candidates',candidates:[{id:'p0',kind:'exact',sharedEvidence:[],differences:[],unknownConditions:[]}]})).success);
 }
});
test('live-shaped invalid response is rejected with original paid usage and never converted into scope success',async()=>{
 const provider:ModelProvider=async()=>({value:wire({action:'show_candidates',candidates:[],question:null,reason:'검색 결과',confirmationRequired:true}),model:'test-provider',usage});
 await assert.rejects(interpret('customer',base,provider),(error:unknown)=>error instanceof AssistantError&&error.code==='INVALID_MODEL_RESPONSE'&&error.diagnostic==='SUPPLIED_CATALOG_SCHEMA'&&error.attempt?.providerCalled===true&&error.attempt.usage?.totalTokens===170);
 let called=0;
 const allowed:ModelProvider=async(_prompt,_input,schema)=>{called++;const value={action:'unidentified',candidates:[],question:null,reason:'모의 서비스에서 실제 결제는 지원하지 않아요.',confirmationRequired:true};assert(schema.safeParse(wire(value)).success);return {value:wire(value),model:'test-provider',usage}};
 const response=await interpret('customer',{...base,clarificationCount:2},allowed);assert(response.ok);assert.equal(called,1);assert.deepEqual(response.data.usage,usage);assert.equal(response.data.result.question,null);
});
