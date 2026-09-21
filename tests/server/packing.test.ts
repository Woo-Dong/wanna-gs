import test from 'node:test';
import assert from 'node:assert/strict';
import {catalogContext,catalogHash} from '../../src/server/catalog';
import {packCatalog,packHistory,packContext,packIds,unpackResult,literalSkuReferences} from '../../src/server/packing';
import {interpret} from '../../src/server/assistant';
import {modelOutputSchema} from '../../src/server/schemas';
const empty={budgetLimitKrw:null,excludeCategories:[],excludeProductIds:[],maxQuantity:null,restorePrevious:false};
const base={sessionId:'s',generation:1,actorId:'a',roleEpoch:1,requestId:'r',conversationId:'c',inputRevision:1,catalogHash};
const usage={inputTokens:0,outputTokens:0,totalTokens:0,estimatedCostUsd:null};
test('complete table preserves every source attribute and references remain stable under ranking/narrowing',()=>{
 const packed=packCatalog(catalogContext), reverse=packCatalog([...catalogContext].reverse());
 assert.equal(packed.rows.length,248);
 for(const [i,p] of catalogContext.entries()){
  const row=Object.fromEntries(packed.columns.map((k,j)=>[k,packed.rows[i][j]]));
  assert.deepEqual({...row,id:p.id},p);assert.equal(row.id,`p${i}`);
  assert.deepEqual(reverse.rows[247-i],packed.rows[i]);
  assert.deepEqual(packCatalog([p]).rows[0],packed.rows[i]);
 }
 assert(JSON.stringify(packed).length<JSON.stringify(catalogContext).length*.8);
});
test('structured identifiers remap but user prose and descriptive strings remain byte exact',()=>{
 const sku=catalogContext[0].id,prose=`${sku} 말고 다른 맛 주세요`;
 const history=[{role:'user' as const,content:prose},{role:'assistant' as const,content:JSON.stringify({candidates:[{id:sku,sharedEvidence:[sku]}]})},{role:'assistant' as const,content:'not-json '+sku}];
 const result=packHistory(history);assert.deepEqual(result[0],history[0]);assert.deepEqual(result[2],history[2]);assert.deepEqual(JSON.parse(result[1].content),{candidates:[{id:'p0',sharedEvidence:[sku]}]});
 assert.deepEqual(packContext({groups:[{sku}],currentConstraints:{...empty,excludeProductIds:[sku]}}),{groups:[{sku:'p0'}],currentConstraints:{...empty,excludeProductIds:['p0']}});
 assert.deepEqual(literalSkuReferences(prose,[]),[{sku,ref:'p0'}]);assert.deepEqual(packIds([sku]),['p0']);
});
test('customer model reference returns canonical SKU; unknown refs fail before domain/UI',async()=>{
 const output={action:'show_candidates',candidates:[{id:'p0',kind:'exact',sharedEvidence:[catalogContext[0].name],differences:[],unknownConditions:[]}],question:null,reason:'확인해 주세요',confirmationRequired:true};
 const input={...base,text:catalogContext[0].name,history:[],clarificationCount:0};
 const result=await interpret('customer',input,async(_p,raw)=>{
  const data=JSON.parse(raw);assert(data.catalog.columns.includes('id'));assert(data.catalog.rows.some((r:unknown[])=>r[0]==='p0'));
  return {value:output,model:'test',usage};
 },'fixture');assert(result.ok);assert.equal((result.data.result as any).candidates[0].id,catalogContext[0].id);
 await assert.rejects(interpret('customer',input,async()=>({value:{...output,candidates:[{...output.candidates[0],id:'p999999'}]},model:'test',usage})),/INVALID_MODEL_RESPONSE/);
});
test('merchant retains full catalog and returns original exclusion IDs without changing scope/budget',async()=>{
 const input={...base,text:`${catalogContext[2].name} 제외`,history:[],state:{storeId:'store',proposalId:'proposal',proposalVersion:1,dailyBudgetKrw:50000,currentConstraints:empty,previousConstraints:null,groups:[{sku:catalogContext[2].id,requestedQty:2,orderableQty:2,purchaseCostKrw:1000}]}};
 const output={intent:'modify',scope:'current_proposal',constraints:{...empty,excludeProductIds:['p2']},question:null,reason:'제외해요'};
 const result=await interpret('merchant',input,async(_p,raw)=>{const data=JSON.parse(raw);assert.equal(data.catalog.rows.length,248);assert.equal(data.context.state.groups[0].sku,'p2');return {value:output,model:'test',usage}},'fixture');assert(result.ok);assert.deepEqual(result.data.result,{...output,constraints:{...empty,excludeProductIds:[catalogContext[2].id]}});
 assert.deepEqual(unpackResult('merchant',output),result.data.result);assert.deepEqual(output.constraints.excludeProductIds,['p2']);
});

test('generation schema enforces existing exact-vs-unknown contract without rejecting confirm',()=>{
 const s=modelOutputSchema('customer',['p0'],['빵']);
 const c={id:'p0',kind:'exact',sharedEvidence:[],differences:[],unknownConditions:['미확인 원재료']};
 const output={action:'show_candidates',candidates:[c],question:null,reason:'확인',confirmationRequired:true};
 assert(!s.safeParse(output).success);assert(s.safeParse({...output,candidates:[{...c,kind:'confirm'}]}).success);
});
