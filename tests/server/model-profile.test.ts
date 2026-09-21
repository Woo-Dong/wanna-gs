import test from 'node:test';
import assert from 'node:assert/strict';
import {estimateModelCost,reasoningOptions} from '../../src/server/model-profile';
test('known model snapshots have separately verified conservative uncached estimates',()=>{
 assert.equal(estimateModelCost('gpt-5-mini-2025-08-07',1_000_000,1_000_000),2.25);
 assert.equal(estimateModelCost('gpt-4.1-mini-2025-04-14',1_000_000,1_000_000),2);
 assert.equal(estimateModelCost('gpt-4.1-mini',0,0),0);
});
test('unknown models and invalid usage never masquerade as free known usage',()=>{
 for(const model of ['other','gpt-4.1','gpt-4.1-miniature','gpt-5-minimum'])assert.equal(estimateModelCost(model,10,10),null);
 for(const [input,output] of [[NaN,1],[-1,1],[1,Infinity],[1,.5]])assert.equal(estimateModelCost('gpt-4.1-mini',input,output),null);
});
test('nonreasoning GPT-4.1 request omits reasoning and baseline GPT-5 settings remain unchanged',()=>{
 assert.deepEqual(reasoningOptions('gpt-4.1-mini-2025-04-14'),{});
 assert.deepEqual(reasoningOptions('gpt-5-mini-2025-08-07'),{reasoning:{effort:'minimal'}});
});
test('SDK requests preserve strict structured output and account actual returned model for both profiles',async()=>{
 const {liveProvider}=await import('../../src/server/provider');
 const {z}=await import('zod');
 const saved={fetch:globalThis.fetch,key:process.env.OPENAI_API_KEY,mode:process.env.LLM_MODE,model:process.env.OPENAI_MODEL};
 let received:Record<string,unknown>[]=[];
 try{
  process.env.OPENAI_API_KEY='unit-test-key-not-real';process.env.LLM_MODE='live';
  globalThis.fetch=async(_url,init)=>{
   const body=JSON.parse(String(init?.body));received.push(body);
   return new Response(JSON.stringify({id:'test-response',object:'response',created_at:0,status:'completed',model:body.model,output:[{id:'test-message',type:'message',status:'completed',role:'assistant',content:[{type:'output_text',text:'{"ok":true}',annotations:[]}]}],usage:{input_tokens:1000,output_tokens:100,total_tokens:1100}}),{status:200,headers:{'Content-Type':'application/json'}});
  };
  for(const model of ['gpt-4.1-mini-2025-04-14','gpt-5-mini-2025-08-07']){
   process.env.OPENAI_MODEL=model;
   const result=await liveProvider('test instruction','test input',z.object({ok:z.boolean()}).strict(),'test_schema');
   assert.equal(result.model,model);assert.equal(result.usage.estimatedCostUsd,estimateModelCost(model,1000,100));assert.deepEqual(result.value,{ok:true});
  }
  assert.equal(received.length,2);assert(!('reasoning' in received[0]));assert.deepEqual(received[1].reasoning,{effort:'minimal'});
  for(const request of received){assert.equal(request.store,false);assert.equal(request.max_output_tokens,3200);assert.equal((request.text as any).format.strict,true);assert.equal((request.text as any).format.schema.additionalProperties,false)}
 }finally{
  globalThis.fetch=saved.fetch;
  for(const [name,value] of [['OPENAI_API_KEY',saved.key],['LLM_MODE',saved.mode],['OPENAI_MODEL',saved.model]] as const){if(value===undefined)delete process.env[name];else process.env[name]=value}
 }
});
