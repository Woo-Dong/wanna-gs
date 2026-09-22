'use client';
import {useCallback,useEffect,useRef,useState} from 'react';
import type {DemoSnapshot,DomainError} from '../../contracts/domain';
import {getDemoClient,scopeFrom,type BrowserDemoClient} from '../../db/client';
import {CustomerView} from '../customer/CustomerView';
import {MerchantView} from '../merchant/MerchantView';
import {DemoControls} from './DemoControls';
import styles from './AppShell.module.css';

export function AppShell(){
 const [client,setClient]=useState<BrowserDemoClient|null>(null);
 const [snapshot,setSnapshot]=useState<DemoSnapshot|null>(null);
 const [loading,setLoading]=useState(true),[busy,setBusy]=useState(false);
 const [error,setError]=useState<DomainError|null>(null),[resetConfirmed,setResetConfirmed]=useState(false);
 const [customerId,setCustomerId]=useState(''),[merchantId,setMerchantId]=useState('');
 const latest=useRef<DemoSnapshot|null>(null),lock=useRef(false),mounted=useRef(false);
 const accept=useCallback((next:DemoSnapshot)=>{
  if(!mounted.current)return;
  const prev=latest.current;
  // An earlier child callback must not restore a previous role or generation.
  if(prev&&prev.session.id===next.session.id){
   if(next.session.generation<prev.session.generation)return;
   if(next.session.generation===prev.session.generation&&(next.roleEpoch<prev.roleEpoch||next.session.revision<prev.session.revision))return;
  }
  latest.current=next;setSnapshot(next);
  if(!prev||prev.actor.id!==next.actor.id||prev.session.generation!==next.session.generation){
   setCustomerId(next.actor.role==='customer'?next.actor.id:next.actors.find(a=>a.role==='customer')?.id??'');
   setMerchantId(next.actor.role==='merchant'?next.actor.id:next.actors.find(a=>a.role==='merchant')?.id??'');
  }
 },[]);
 useEffect(()=>{
  mounted.current=true;let active=true;let unsubscribe=()=>{};
  try{
   const instance=getDemoClient();setClient(instance);unsubscribe=instance.subscribe(accept);
   void instance.initialize().then(result=>{if(!active)return;if(result.ok)accept(result.data);else setError(result.error);setLoading(false)}).catch(()=>{if(active){setError({code:'INITIALIZE_FAILED',message:'시연 데이터를 열지 못했어요. 다시 시도해 주세요.',retryable:true});setLoading(false)}});
  }catch{setError({code:'INITIALIZE_FAILED',message:'이 브라우저에서 시연 저장소를 열지 못했어요.',retryable:true});setLoading(false)}
  return()=>{active=false;mounted.current=false;unsubscribe()};
 },[accept]);
 async function initialize(reset=false){
  if(!client||lock.current||(reset&&!resetConfirmed))return;
  lock.current=true;setBusy(true);setError(null);
  try{const result=reset?await client.resetIncompatible(true):await client.initialize();if(!mounted.current)return;if(result.ok){accept(result.data);setResetConfirmed(false)}else setError(result.error)}catch{if(mounted.current)setError({code:'INITIALIZE_FAILED',message:'데이터를 열지 못했어요. 다시 시도해 주세요.',retryable:true})}
  finally{lock.current=false;if(mounted.current)setBusy(false)}
 }
 async function switchActor(actorId:string){
  const current=latest.current;if(!client||!current||!actorId||lock.current||actorId===current.actor.id)return;
  lock.current=true;setBusy(true);setError(null);
  try{const result=await client.switchRole(actorId,scopeFrom(current));if(!mounted.current)return;if(result.ok)accept(result.data);else setError(result.error)}catch{if(mounted.current)setError({code:'SWITCH_FAILED',message:'역할을 바꾸지 못했어요. 다시 시도해 주세요.',retryable:true})}
  finally{lock.current=false;if(mounted.current)setBusy(false)}
 }
 const incompatible=error?.code==='SNAPSHOT_INCOMPATIBLE'||error?.code==='SNAPSHOT_CORRUPT';
 const store=snapshot?.stores.find(s=>s.id===snapshot.actor.storeId);
 return <div className={styles.shell}>
  {snapshot?.actor.role!=='customer'&&<header className={styles.header}>
   <div className={styles.brand}><strong>원하<span>GS</span></strong><span>‘원하지쓰’라고 읽어요.</span></div>
   <span className={styles.badge}>모의 시연</span>
  </header>}
  <details className={styles.notice} aria-label="시연 안내"><summary>한 PC 모의 시연 · 실제 거래 없음</summary>공개 자료로 확인한 상품·점포 정보를 사용해요. 고객·가격·재고·발주·결제는 모의 데이터이며 실제 점포 거래와 연결되지 않아요. 이 브라우저의 한 탭에서 이어서 시연해 주세요.</details>
  {loading?<div className={styles.status} role="status"><h1>시연을 준비하고 있어요</h1><p>이 브라우저에 저장된 상태를 확인하고 있어요.</p></div>:null}
  {!loading&&!snapshot?<section className={styles.recovery} aria-labelledby="recovery-title">
   <h1 id="recovery-title">{incompatible?'저장된 시연 상태를 확인해 주세요':'시연 데이터를 열 수 없어요'}</h1>
   <p role="alert">{incompatible?'저장된 데이터의 버전이나 상태가 현재 시연과 맞지 않아요. 초기화하면 이 브라우저에 저장된 기존 시연 진행 내역이 사라져요.':error?.message??'잠시 후 다시 시도해 주세요.'}</p>
   {incompatible?<><label className={styles.confirm}><input type="checkbox" checked={resetConfirmed} disabled={busy} onChange={e=>setResetConfirmed(e.target.checked)}/>기존 시연 내역을 지우고 처음부터 시작하는 데 동의해요.</label><button type="button" disabled={busy||!resetConfirmed} onClick={()=>void initialize(true)}>{busy?'초기화 중…':'확인하고 시연 초기화'}</button></>:<button type="button" disabled={busy||!client} onClick={()=>void initialize()}>{busy?'다시 여는 중…':'다시 시도'}</button>}
  </section>:null}
  {snapshot&&client?<>
   <section className={styles.roles} aria-labelledby="role-title">
    <div className={styles.roleHeading}><p id="role-title" aria-live="polite">{snapshot.actor.role==='customer'?snapshot.actor.displayName:`${store?.name??''} 경영주`}</p><button type="button" disabled={busy} onClick={()=>void switchActor(snapshot.actor.role==='customer'?merchantId:customerId)}>{snapshot.actor.role==='customer'?'경영주 화면으로 전환':'고객 화면으로 전환'}</button></div><details className={styles.actorDetails}><summary>합성 고객·시연 점포 선택</summary>
    <div className={styles.roleOptions}>
     <div><label htmlFor="demo-customer">합성 고객 선택</label><select id="demo-customer" value={customerId} onChange={e=>setCustomerId(e.target.value)} disabled={busy}>{snapshot.actors.filter(a=>a.role==='customer').map(a=><option value={a.id} key={a.id}>{a.displayName}</option>)}</select><button type="button" disabled={busy||!customerId||snapshot.actor.id===customerId} onClick={()=>void switchActor(customerId)}>{snapshot.actor.id===customerId?'고객 화면 이용 중':'선택한 고객으로 전환'}</button></div>
     <div><label htmlFor="demo-merchant">경영주 시연 점포 선택</label><select id="demo-merchant" value={merchantId} onChange={e=>setMerchantId(e.target.value)} disabled={busy}>{snapshot.actors.filter(a=>a.role==='merchant').map(a=><option value={a.id} key={a.id}>{snapshot.stores.find(s=>s.id===a.storeId)?.name??a.displayName}</option>)}</select><button type="button" disabled={busy||!merchantId||snapshot.actor.id===merchantId} onClick={()=>void switchActor(merchantId)}>{snapshot.actor.id===merchantId?'경영주 화면 이용 중':'선택한 점포로 전환'}</button></div>
    </div>
    <p className={styles.meta}>역할을 바꿔도 시연 내역은 유지돼요. 시연 시각: <time dateTime={new Date(snapshot.clock.now).toISOString()}>{new Intl.DateTimeFormat('ko-KR',{timeZone:'Asia/Seoul',dateStyle:'medium',timeStyle:'short'}).format(snapshot.clock.now)}</time> (한국 시간)</p></details>
    {busy?<p role="status">화면을 준비하고 있어요…</p>:null}
    {error?<p className={styles.error} role="alert">{error.message}</p>:null}
   </section>
   <div inert={busy} aria-busy={busy}>
    {snapshot.actor.role==='customer'?<CustomerView snapshot={snapshot} client={client} onSnapshot={accept}/>:<MerchantView snapshot={snapshot} client={client} onSnapshot={accept}/>}
    <div className={styles.controls}><DemoControls snapshot={snapshot} client={client} onSnapshot={accept}/></div>
   </div>
  </>:null}
 </div>;
}
