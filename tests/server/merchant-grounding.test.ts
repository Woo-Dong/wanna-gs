import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {certifySkuOnlyExclusions as certify}from'../../src/server/merchant-grounding';
import {catalogContext}from'../../src/server/catalog';
import stores from '../../data/seed/stores.json';
const catalog=[
  {id:'SKU-MILK',name:'바나나맛우유 240ml',category:'커피·우유·요거트'},
  {id:'SKU-LIGHT',name:'바나나맛우유 Light 240ml',category:'커피·우유·요거트'},
  {id:'SKU-BREAD',name:'빙그레 생크림빵 우유 95g',category:'빵·디저트'},
  {id:'SKU-SNACK',name:'과자',category:'스낵·과자·초콜릿'},
];
test('complete canonical name and explicit SKU exclusion produce a consumed certificate',()=>{
  for(const text of ['바나나맛우유 240ml은 빼 주세요.','이번 발주안에서 바나나맛우유 240ml은 빼 주세요. 다른 상품은 그대로 검토할게요.','SKU-MILK 제외해 주세요','빙그레 생크림빵 우유 95g만 빼줘']){
    const result=certify(text,catalog);assert(result,text);assert.equal(result.onlySkuExclusions,true);assert.equal(result.exactSkuIds.length,1);
    for(const span of result.consumedSpans)assert.equal(result.normalizedText.slice(span.start,span.end),span.matchedText);
  }
});
test('multiple exact SKU atoms and complete variants do not acquire categories',()=>{
  const r=certify('바나나맛우유 240ml과 빙그레 생크림빵 우유 95g은 제외해 주세요',catalog);assert.deepEqual(r?.exactSkuIds,['SKU-MILK','SKU-BREAD']);
  assert.deepEqual(certify('바나나맛우유 Light 240ml 제외',catalog)?.exactSkuIds,['SKU-LIGHT']);
  assert.equal(certify('바나나맛우유 240ml 초코맛은 빼 주세요',catalog),null);
});
test('category-only, mixed, copy, fresh undo and unknown language retain the unrestricted schema',()=>{
  for(const text of ['과자는 빼 주세요','우유 전체를 빼 주세요','바나나맛우유 240ml과 과자는 빼 주세요','바나나맛우유 240ml을 빼고 빵은 전부 제외해 주세요','앞으로도 이렇게 유지해 주세요','앞으로도 이 제외 조건을 그대로 써요','아까 바나나맛우유 240ml을 뺀 것을 취소해 주세요','바나나맛우유 240ml 빼 주세요. 나머지는 알아서 좋은 것으로'])assert.equal(certify(text,catalog),null,text);
});
test('negation, exceptions, contrast, quotation, hypothetical and embedded names never certify',()=>{
  for(const text of ['바나나맛우유 240ml은 제외하지 마세요','바나나맛우유 240ml 말고 우유는 빼 주세요','바나나맛우유 240ml만 남기고 빼 주세요','바나나맛우유 240ml 빼 주세요라는 말은 취소','"바나나맛우유 240ml 빼 주세요"','바나나맛우유 240ml 빼 주면 좋을까요?','초코바나나맛우유 240ml 빼 주세요','바나나맛우유 240ml 제외 대신 음료 모두','바나나맛우유 240ml 빼고 싶지 않아요'])assert.equal(certify(text,catalog),null,text);
});
test('unambiguous budgets, quantity limits, literal store scopes and future edits are consumed together',()=>{
  for(const text of ['이번 발주안 예산은 50,000원 이하, 최대 수량은 2개로 제한하고 바나나맛우유 240ml은 제외해 주세요.','이번 GS25테스트점 발주안 예산은 21000원 이하, 최대 수량은 2개로 제한하고 바나나맛우유 240ml은 제외해 주세요.','앞으로의 자동발주 정책에 계속 바나나맛우유 240ml 제외 조건을 적용하고 예산은 22000원으로 제한해 주세요.','이번 발주안에만 바나나맛우유 240ml 제외 조건을 적용하고 예산은 오만원으로 제한해 주세요.'])assert(certify(text,catalog,['GS25테스트점']),text);
  assert.equal(certify('이번 모르는점 발주안 바나나맛우유 240ml 빼 주세요',catalog,['GS25테스트점']),null);
  assert.equal(certify('바나나맛우유 240ml 빼고 예산은 넘어도 괜찮아요',catalog),null);
});
test('aliases, duplicate canonical names and partial variant prefixes cannot prove a SKU',()=>{
  assert.equal(certify('바나나우유 빼 주세요',catalog),null);
  assert.equal(certify('바나나맛우유 빼 주세요',catalog),null);
  assert.equal(certify('바나나맛우유 240ml 빼 주세요',[...catalog,{...catalog[0],id:'DUPLICATE'}]),null);
  assert.equal(certify('과자 빼 주세요',catalog),null);
});
test('normalization preserves exact variant identity and offsets without accepting new prose',()=>{
  const r=certify('  이번  발주안에서 ＳＫＵ－ＭＩＬＫ은 빼 주세요.  ',catalog);
  assert.deepEqual(r?.exactSkuIds,['SKU-MILK']);
  assert.equal(certify('바나나맛우유 240ml 빼 주세요. \uE0000\uE001 제외',catalog),null);
  assert.equal(certify('바나나맛우유 240ml 빼 주세요. 다른 상품은 그대로 하되 음료 전부도 빼요',catalog),null);
});
test('public dev/validation certificates preserve exact explicit targets; all uncovered language falls back',()=>{
  let certified=0,fallback=0;
  // Public splits only; never discover or open any private/holdout input.
  for(const file of ['dev.jsonl','validation.jsonl']){
    const rows=fs.readFileSync(new URL('../../evals/'+file,import.meta.url),'utf8').trim().split('\n').map(line=>JSON.parse(line));
    for(const row of rows.filter(r=>r.role==='merchant')){
      const result=certify(row.turns.at(-1).text,catalogContext,stores.map(store=>store.name));
      if(!result){fallback++;continue}
      certified++;const command=row.expected.command;
      assert.equal(command.intent,'modify',row.id);
      assert.deepEqual([...result.exactSkuIds].sort(),[...(command.constraints.excludeProductIds??[])].sort(),row.id);
      assert.equal(command.constraints.excludeCategories?.length??0,0,row.id);
    }
  }
  assert(certified>0);assert(fallback>0);
});
