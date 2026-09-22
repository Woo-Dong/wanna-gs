import test from 'node:test';import assert from 'node:assert/strict';import fs from 'node:fs';import initSqlJs from 'sql.js';
import {needCandidateClues} from '../../src/components/customer/model';
import {DomainEngine} from '../../src/domain/engine';
import type {Candidate} from '../../src/contracts/assistant';
import type {DemoCommand} from '../../src/contracts/domain';

test('empty unidentified, normal exact, uncertain original and alternative preserve separate model labels',()=>{
 assert.deepEqual(needCandidateClues([]),[]);
 const candidates:Candidate[]=[{id:'synthetic-exact',kind:'exact',sharedEvidence:['이름 일치'],differences:[],unknownConditions:[]},{id:'synthetic-original',kind:'confirm',sharedEvidence:['관측 이름'],differences:[],unknownConditions:['원재료 근거 없음']},{id:'synthetic-other',kind:'alternative',sharedEvidence:['공통 맛'],differences:['용량 다름'],unknownConditions:['식이 조건 미확인']}];
 const before=structuredClone(candidates),clues=needCandidateClues(candidates);assert.deepEqual(candidates,before);
 for(const candidate of candidates){const own=clues.filter(c=>c.includes(`후보 SKU ${candidate.id} ·`));assert(own.length);assert(own.every(c=>c.includes('모델 해석 (사용자 확정 아님)')&&c.includes(`종류 ${candidate.kind}`)));for(const evidence of [...candidate.sharedEvidence,...candidate.differences,...candidate.unknownConditions])assert(own.some(c=>c.endsWith(evidence)));}
 assert(!clues.filter(c=>c.includes('synthetic-exact')).some(c=>c.includes('미확인 조건:')));
 assert(clues.some(c=>c.includes('synthetic-other')&&c.includes('요청과의 차이: 용량 다름')));
});
test('actual saveNeed body persists evidence through SQLite export/import without turning a need into demand',async()=>{
 const source=fs.readFileSync('src/components/customer/CustomerView.tsx','utf8');
 const start=source.indexOf(' async function saveNeed():Promise<string|null>{'),end=source.indexOf('\n function selectCandidate',start);assert(start>=0&&end>start);
 const body=source.slice(start,end).slice(source.slice(start,end).indexOf('{')+1).trim().replace(/\}$/, '');
 const AsyncFunction=Object.getPrototypeOf(async function(){}).constructor;
 const saveNeed=new AsyncFunction('needId','interpretation','searchEnvelope','storeId','currentEnvelope','live','conversation','revision','setError','dispatch','original','input','displayHistory','setNeedId','rejected','needCandidateClues',body);
 const SQL=await initSqlJs();const engine=new DomainEngine(new SQL.Database(new Uint8Array(fs.readFileSync('public/demo/seed.sqlite'))),()=>Date.UTC(2026,8,22,3));const snapshot=engine.snapshot(engine.scope()),products=snapshot.products.slice(0,2),store=snapshot.stores[0].id;
 const candidates:Candidate[]=[{id:products[0].sku,kind:'confirm',sharedEvidence:['관측된 상품 이름'],differences:[],unknownConditions:['원재료 목록 근거가 없어 알레르기 조건 미확인']},{id:products[1].sku,kind:'alternative',sharedEvidence:['공통 분류'],differences:['원상품과 다른 SKU'],unknownConditions:[]}];
 const original='합성 고객의 원래 요청과 알레르기 조건',reason='상품을 확인해 주세요.',dialogue=[{role:'user',content:original},{role:'assistant',content:reason}],interpretation={action:'show_candidates',candidates,question:null,reason,confirmationRequired:true};let needId:string|null=null;let serial=0;
 const dispatch=async(cmd:DemoCommand)=>engine.dispatch(cmd,{...engine.scope(),commandId:`need-fixture-${++serial}`,correlationId:'synthetic-no-model'});
 try{
  const id=await saveNeed(null,interpretation,{},store,()=>true,{current:snapshot},{current:'fixture-conversation'},{current:1},(error:string)=>assert.fail(error),dispatch,original,original,dialogue,(value:string)=>needId=value,[products[1].sku],needCandidateClues);assert.equal(id,needId);
  const imported=new DomainEngine(new SQL.Database(engine.db.export()),()=>Date.UTC(2026,8,22,3));
  try{const restored=imported.switchRole('DEMO-MERCHANT-'+store,imported.scope()),need=restored.needs.find(n=>n.id===id)!;assert(need);assert.equal(need.originalText,original);assert.equal(need.reason,reason);assert.deepEqual(need.dialogue,dialogue.map(h=>`${h.role}: ${h.content}`));assert.deepEqual(need.candidateSkus,candidates.map(c=>c.id));assert.deepEqual(need.sourceRefs,products.flatMap(p=>p.sourceOrigin.sourceIds));
   for(const c of candidates)for(const detail of [...c.sharedEvidence,...c.differences,...c.unknownConditions])assert(need.extractedClues.some(text=>text.includes(c.id)&&text.endsWith(detail)));
   assert(need.extractedClues.every(text=>text.includes('모델 해석 (사용자 확정 아님)')));assert.equal(restored.requests.length,0);assert.equal(restored.demand.length,0);assert.equal(restored.orders.length,0);
   const recs=imported.all('recommendation_events');assert.equal(recs.length,3);assert.equal(recs.filter(r=>r.action==='rejected').length,1);assert(recs.every(r=>r.followup_request_id===null));assert.equal(imported.rows('PRAGMA integrity_check')[0].integrity_check,'ok');
  }finally{imported.db.close()}
 }finally{engine.db.close()}
});
