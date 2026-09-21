/** Model-input state only. Case text, expected answers and labels are never copied. */
import fs from 'node:fs';
import crypto from 'node:crypto';
import initSqlJs from 'sql.js';
import {DomainEngine} from '../src/domain/engine';
import type {DemoCommand} from '../src/contracts/domain';
const input=process.argv[2],output=process.argv[3];
if(!input||!output)throw Error('cases and output path required');
const cases=fs.readFileSync(input,'utf8').trim().split('\n').map(line=>JSON.parse(line));
if(cases.some(c=>c.split==='holdout')&&!process.argv.includes('--independent-holdout'))throw Error('Protected holdout requires independent evaluator');
const SQL=await initSqlJs(),seed=new Uint8Array(fs.readFileSync('public/demo/seed.sqlite'));
const states:Record<string,unknown>={};const trace:unknown[]=[];
for(const item of cases){
 if(item.role!=='merchant')continue;
 const db=new SQL.Database(seed),e=new DomainEngine(db,()=>Date.UTC(2026,8,21,3));
 const context=item.context||{},store=context.storeId;
 if(!e.rows('SELECT id FROM stores WHERE id=?',[store]).length)throw Error('Unknown evaluation store');
 const skus:string[]=context.proposalProductIds||[],syntheticAdded:string[]=[];
 const send=(command:DemoCommand)=>{const commandId=crypto.randomUUID();return e.dispatch(command,{...e.scope(),commandId,correlationId:commandId})};
 for(const sku of skus){
  if(!e.rows('SELECT sku FROM products WHERE sku=?',[sku]).length)throw Error('Unknown evaluation SKU');
  if(!e.all('conditions','AND store_id=? AND sku=?',[store,sku]).length){
   const template=e.all('conditions','AND store_id=?',[store])[0];
   e.insert('conditions',{...template,sku,reason:'명시적인 합성 평가 조건. 실제 점포 사실 아님.'});syntheticAdded.push(sku);
  }
  const c=e.condition(store,sku);
  send({type:'request.create',sku,storeId:store,quantity:12,acceptedPriceKrw:c.sale_price_krw,conditionVersion:c.version,consent:{accepted:true,termsVersion:'eval-synthetic-v1'}});
 }
 e.switchRole('DEMO-MERCHANT-'+store,e.scope());send({type:'merchant.review',storeId:store});
 const snapshot=e.snapshot(e.scope());e.assertInvariants();
 states[item.id]={storeId:store,proposalId:null,proposalVersion:null,currentProposalVersion:null,stale:false,dailyBudgetKrw:snapshot.policies[0].dailyBudgetKrw,currentConstraints:null,previousConstraints:null,groups:snapshot.demand.map(row=>({sku:row.sku,requestedQty:row.validPendingQty,orderableQty:row.newOrderNeedQty,purchaseCostKrw:snapshot.conditions.find(c=>c.storeId===store&&c.sku===row.sku)!.purchaseCostKrw}))};
 trace.push({caseId:item.id,storeId:store,source:'actual SQLite synthetic evaluation snapshot',syntheticAddedConditions:syntheticAdded,requestCount:snapshot.requests.length,originalCaseContextOverrides:'proposal identity/revision/constraints supplied by the frozen public context; no expected labels used'});db.close();
}
fs.writeFileSync(output,JSON.stringify(states,null,2)+'\n',{mode:0o600});fs.writeFileSync(output+'.trace.json',JSON.stringify({seedHash:crypto.createHash('sha256').update(seed).digest('hex'),cases:trace},null,2)+'\n',{mode:0o600});
console.log(JSON.stringify({merchantStates:Object.keys(states).length,modelCalls:0,outputHash:crypto.createHash('sha256').update(fs.readFileSync(output)).digest('hex')}));
