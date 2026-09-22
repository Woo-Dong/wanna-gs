import fs from 'node:fs';import initSqlJs from 'sql.js';import {DomainEngine} from '../../src/domain/engine.ts';
export async function prepareMerchantSeed(kind='batch'){
 const SQL=await initSqlJs();const e=new DomainEngine(new SQL.Database(fs.readFileSync('public/demo/seed.sqlite')),()=>Date.now());
 const merchant=e.all('actors',"AND role='merchant'")[0];const cs=e.all('conditions','AND store_id=? ORDER BY sku',[merchant.store_id]).slice(0,kind==='batch'?10:1);
 // Setup only: synthetic valid customer demand, no merchant review/approval/supply/payment/receipt.
 for(let i=0;i<cs.length;i++){const c=cs[i];e.switchRole(`DEMO-CUSTOMER-${String(i+1).padStart(3,'0')}`,e.scope());const id=crypto.randomUUID();e.dispatch({type:'request.create',sku:c.sku,storeId:c.store_id,quantity:kind==='shortage'?3:2,acceptedPriceKrw:c.sale_price_krw,conditionVersion:c.version,consent:{accepted:true,termsVersion:'independent-seed-setup'}},{...e.scope(),commandId:id,correlationId:id});}
 e.switchRole(merchant.id,e.scope());const snapshot=e.snapshot(e.scope());const bytes=e.db.export();e.db.close();
 return {envelope:{bytes:Array.from(bytes),versions:snapshot.versions,sessionId:snapshot.session.id,generation:snapshot.session.generation,actorId:snapshot.actor.id,roleEpoch:snapshot.roleEpoch,revision:snapshot.session.revision},setup:{kind,storeId:merchant.store_id,actorId:merchant.id,products:snapshot.products.filter(p=>cs.some(c=>c.sku===p.sku)),conditions:snapshot.conditions.filter(c=>cs.some(v=>v.sku===c.sku)),requestCount:cs.length,quantity:kind==='shortage'?3:2}};
}
