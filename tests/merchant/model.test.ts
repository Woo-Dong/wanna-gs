import test from 'node:test';import assert from 'node:assert/strict';
import {proposalChange,toModelConstraints} from '../../src/components/merchant/model';
import type {ProposalView} from '../../src/contracts/domain';
const p:ProposalView={id:'p',storeId:'s',version:1,status:'draft',sourceFingerprint:'v',constraints:{scope:'once',budgetCapKrw:90000,excludeSkus:['a']},lines:[{sku:'b',quantity:6,purchaseCostKrw:1000,salePriceKrw:1500,conditionVersion:1,totalKrw:6000}],deferred:[],totalKrw:6000,orderId:null};
test('model keys explicitly map to domain keys while prior constraints survive',()=>{const c=proposalChange(p,{budgetLimitKrw:50000,excludeCategories:['bread'],excludeProductIds:['c'],maxQuantity:3,restorePrevious:false});assert.deepEqual(c,{scope:'once',budgetCapKrw:50000,excludeSkus:['a','c'],excludeCategories:['bread'],maxQuantities:{b:3}});assert(!('budgetLimitKrw'in c));assert.deepEqual(p.constraints,{scope:'once',budgetCapKrw:90000,excludeSkus:['a']})});
test('ADR005 stores explicit cap independently of current line quantity; nullable fields preserve prior proposal',()=>{const c=proposalChange(p,{budgetLimitKrw:null,excludeCategories:[],excludeProductIds:[],maxQuantity:10,restorePrevious:false});assert.equal(c.maxQuantities?.b,10);assert.equal(c.budgetCapKrw,90000)});
test('a missing proposal is not invented as a previous command',()=>{assert.equal(toModelConstraints(null),null);assert.equal(toModelConstraints(p)?.budgetLimitKrw,90000)});

test('active, deferred and previously capped SKUs receive the explicit cap without mutating proposal',()=>{
 const current:ProposalView={...p,constraints:{...p.constraints,maxQuantities:{old:2}},deferred:[{sku:'c',reason:'budget_insufficient',nextAction:'review'}]};
 const before=structuredClone(current);const changes={budgetLimitKrw:50000,excludeCategories:[],excludeProductIds:[],maxQuantity:10,restorePrevious:false};
 const c=proposalChange(current,changes);assert.deepEqual(c.maxQuantities,{b:10,c:10,old:10});assert.deepEqual(current,before);
 assert.equal(toModelConstraints({...current,constraints:c})?.maxQuantity,10);
 const budgetOnly=proposalChange({...current,constraints:c},{...changes,budgetLimitKrw:60000,maxQuantity:null});assert.deepEqual(budgetOnly.maxQuantities,c.maxQuantities);assert.equal(budgetOnly.budgetCapKrw,60000);
});
test('deferred-only proposal still maps cap; no demand invents no SKU or quantity',()=>{
 const changes={budgetLimitKrw:50000,excludeCategories:[],excludeProductIds:[],maxQuantity:2,restorePrevious:false};
 assert.deepEqual(proposalChange({...p,lines:[],deferred:[{sku:'c',reason:'budget_insufficient',nextAction:'review'}]},changes).maxQuantities,{c:2});
 assert.deepEqual(proposalChange({...p,lines:[],deferred:[]},changes).maxQuantities,{});
});
