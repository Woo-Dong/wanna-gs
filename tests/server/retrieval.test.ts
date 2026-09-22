import {customerWireFixture as wire} from './customer-wire.fixture';
import test from 'node:test';import assert from 'node:assert/strict';import {z} from 'zod';
import {retrieveCatalog,normalizeCatalogText} from '../../src/server/retrieval';
import {catalogContext,categories} from '../../src/server/catalog';
import {modelOutputSchema} from '../../src/server/schemas';
import {verifyCustomer} from '../../src/server/assistant';
import {AssistantError} from '../../src/server/provider';
test('all 248 exact catalog names keep their ID and related variants distinct',()=>{
 assert.equal(catalogContext.length,248);for(const product of catalogContext){const result=retrieveCatalog(product.name+' 찾고 있어요.');assert(result.catalog.some(p=>p.id===product.id));assert(result.matchingHints.exactNameIds.includes(product.id));assert.equal(new Set(result.catalog.map(p=>p.id)).size,result.catalog.length)}
});
test('weak semantics preserve the complete catalog; Unicode and punctuation normalize',()=>{
 assert.equal(retrieveCatalog('아침에 간단히 먹고 싶어요').catalog.length,248);
 assert.equal(normalizeCatalogText('Ｘ.Ｏ. 교자 ３２４ｇ'),normalizeCatalogText('X.O. 교자 324g'));
});
test('latest literal request preserves previous candidate IDs for corrections without forcing a choice',()=>{
 const target=catalogContext[0],previous=catalogContext.at(-1)!;const r=retrieveCatalog(target.name+'는 비건인가요?',[{role:'assistant',content:JSON.stringify({candidates:[{id:previous.id,kind:'alternative'}]})}]);assert(r.catalog.some(p=>p.id===previous.id));assert(r.matchingHints.exactNameIds.includes(target.id));assert(!('action' in r));assert(!('confirmedSku' in r));
});
test('generated schema admits only supplied SKU IDs; empty unidentified remains valid',()=>{
 const ids=catalogContext.slice(0,2).map(p=>p.id),schema=modelOutputSchema('customer',ids,categories);const value={action:'show_candidates',candidates:[{id:ids[0],kind:'exact',sharedEvidence:[],differences:[],unknownConditions:[]}],question:null,reason:'확인',confirmationRequired:true};assert(schema.safeParse(wire(value)).success);assert(!schema.safeParse(wire({...value,candidates:[{...value.candidates[0],id:catalogContext[2].id}]})).success);assert(schema.safeParse(wire({...value,action:'unidentified',candidates:[]})).success);assert(JSON.stringify(z.toJSONSchema(schema)).includes(ids[0]));
});
test('merchant SKU and category enums preserve budget-only and policy changes',()=>{
 const schema=modelOutputSchema('merchant',catalogContext.map(p=>p.id),categories);const value={intent:'modify',scope:'policy',constraints:{budgetLimitKrw:50000,excludeCategories:[],excludeProductIds:[],maxQuantity:null,restorePrevious:false},question:null,reason:'제안'};assert(schema.safeParse(value).success);assert(!schema.safeParse({...value,constraints:{...value.constraints,excludeProductIds:['invented']}}).success);assert(!schema.safeParse({...value,constraints:{...value.constraints,excludeCategories:['invented-category']}}).success);
});
test('failure diagnostic identifies a rule without recording model content',()=>{
 const value={action:'show_candidates',candidates:[{id:'invented',kind:'exact',sharedEvidence:[],differences:[],unknownConditions:[]}],question:null,reason:'private input must not become a diagnostic',confirmationRequired:true};assert.throws(()=>verifyCustomer(value,0),error=>error instanceof AssistantError&&error.diagnostic==='CANDIDATE_UNKNOWN_ID'&&!error.message.includes('private'));
});

test('rejected named items and unknown extra conditions retain other product categories',()=>{
 for(const text of ['오뚜기밥 210g 말고 유제품으로 추천해 주세요','짜슐랭 145g는 싫고 아이스크림 먹고 싶어요','오뚜기밥 210g와 비교할 유제품','오뚜기밥 210g 비건인가요?'])assert.equal(retrieveCatalog(text).catalog.length,248);
 assert.equal(retrieveCatalog('오뚜기밥 210g 찾아주세요').catalog.length,24);assert.equal(retrieveCatalog('오뚜기밥 210g 찾아주세요').fullCatalog.length,248);
});
