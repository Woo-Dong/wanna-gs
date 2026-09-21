'use client';
import {useEffect,useRef,useState} from 'react';
import type {DemoSnapshot,DemoClient,DemoCommand,CommandContext,CommandReceipt,RequestDetail} from '../../contracts/domain';
import type {AssistantEnvelope,AssistantResponse,CustomerInput,CustomerInterpretation,DialogueTurn,Candidate} from '../../contracts/assistant';
import {Brand} from '../brand';
import {StoreMap} from './StoreMap';
import {TERMS_VERSION,scopeOf,sameScope,currentEnvelope,money,date,remaining,requestState,conditionText,canConfirmCondition,canRetryPayment,distanceKm} from './model';
import styles from './customer.module.css';
export interface CustomerViewProps {snapshot:DemoSnapshot;client:DemoClient;onSnapshot:(s:DemoSnapshot)=>void}
type Page='wish'|'requests'|'pickup'|'notifications';
type Pending={command:DemoCommand;context:CommandContext};
const id=()=>crypto.randomUUID();
export function CustomerView({snapshot,client,onSnapshot}:CustomerViewProps){
 const live=useRef(snapshot);live.current=snapshot;
 const [page,setPage]=useState<Page>('wish');const [input,setInput]=useState('');const [undoInput,setUndoInput]=useState<string|null>(null);
 const revision=useRef(0),conversation=useRef(''),activeSearch=useRef(''),abort=useRef<AbortController|null>(null);
 const [history,setHistory]=useState<DialogueTurn[]>([]);const [displayHistory,setDisplayHistory]=useState<DialogueTurn[]>([]);const [original,setOriginal]=useState('');
 const [interpretation,setInterpretation]=useState<CustomerInterpretation|null>(null);const [mode,setMode]=useState<string|null>(null);
 const [questions,setQuestions]=useState(0);const [searching,setSearching]=useState(false);const [busy,setBusy]=useState(false);const lock=useRef(false);
 const [error,setError]=useState('');const [notice,setNotice]=useState('');const [selected,setSelected]=useState('');const [storeId,setStoreId]=useState('');
 const [qty,setQty]=useState('1');const [consentKey,setConsentKey]=useState('');const [needId,setNeedId]=useState<string|null>(null);
 const [rejected,setRejected]=useState<string[]>([]);const [detailId,setDetailId]=useState<string|null>(null);const [editId,setEditId]=useState<string|null>(null);const [replaceId,setReplaceId]=useState<string|null>(null);
 const [showMap,setShowMap]=useState(false);const [pending,setPending]=useState<Pending|null>(null);const [searchEnvelope,setSearchEnvelope]=useState<AssistantEnvelope|null>(null);
 const inputRef=useRef<HTMLTextAreaElement>(null);const resultRef=useRef<HTMLHeadingElement>(null);
 const currentScope=scopeOf(snapshot);const scopeKey=JSON.stringify(currentScope);
 useEffect(()=>{abort.current?.abort();revision.current++;conversation.current=id();setHistory([]);setDisplayHistory([]);setOriginal('');setInterpretation(null);setSelected('');setStoreId('');setConsentKey('');setNeedId(null);setRejected([]);setQuestions(0);setInput('');setError('');setNotice('');setSearchEnvelope(null);setPending(null);setEditId(null);setReplaceId(null);setDetailId(null);setSearching(false);setMode(null);},[scopeKey]);
 useEffect(()=>()=>abort.current?.abort(),[]);
 const ownRequests=snapshot.requests.filter(r=>r.actorId===snapshot.actor.id);
 const ownNeeds=snapshot.needs.filter(n=>n.actorId===snapshot.actor.id);
 const notifications=snapshot.notifications.filter(n=>n.actorId===snapshot.actor.id);
 const product=snapshot.products.find(p=>p.sku===selected);
 const condition=snapshot.conditions.find(c=>c.storeId===storeId&&c.sku===selected);
 const quantity=Number(qty);const edit=ownRequests.find(r=>r.id===editId);const replacing=ownRequests.find(r=>r.id===replaceId);
 const tuple=JSON.stringify([scopeKey,selected,storeId,quantity,condition?.version,condition?.salePriceKrw,edit?.version,replacing?.version]);
 const accepted=consentKey===tuple;
 const writable=snapshot.persistence.status==='ready'&&snapshot.actor.role==='customer';
 const unavailable=busy||searching||!!pending||!writable;
 const selectedCandidate=interpretation?.candidates.find(c=>c.id===selected);
 const demoLocation=snapshot.stores[0]; // Explicit virtual demo point at the first verified store, not device GPS.
 const stores=[...snapshot.stores].sort((a,b)=>demoLocation?distanceKm(demoLocation,a)-distanceKm(demoLocation,b):0);
 const examples=snapshot.products.filter(p=>/쫀득버터떡빵|라라스윗 망고 쫀득바|혜자로운 단팥크림빵/.test(p.name)).slice(0,3);
 function changeInput(v:string){setInput(v);revision.current++;abort.current?.abort();setSearching(false);setInterpretation(null);setSearchEnvelope(null);setSelected('');setConsentKey('');setNeedId(null);setRejected([]);setError('');}
 function freshConversation(){abort.current?.abort();conversation.current=id();revision.current++;setHistory([]);setDisplayHistory([]);setOriginal('');setQuestions(0);setInterpretation(null);setSearchEnvelope(null);setSelected('');setConsentKey('');setNeedId(null);setRejected([]);setEditId(null);setInput('');setMode(null);setSearching(false);}
 async function search(){
  if(searching||busy||!input.trim()||input.length>2000)return;
  const source=live.current;if(source.actor.role!=='customer')return;
  if(!conversation.current)conversation.current=id();
  const envelope:AssistantEnvelope={...scopeOf(source),requestId:id(),conversationId:conversation.current,inputRevision:revision.current,catalogHash:source.versions.catalogHash};
  const body:CustomerInput={...envelope,text:input.trim(),history,clarificationCount:questions};
  abort.current?.abort();activeSearch.current=envelope.requestId;const controller=new AbortController();abort.current=controller;setSearching(true);setError('');setNotice('');
  try{
   const response=await fetch('/api/product-assistant',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body),signal:controller.signal});
   const data=await response.json() as AssistantResponse<CustomerInterpretation>;
   if(activeSearch.current!==envelope.requestId||!sameScope(envelope,scopeOf(live.current))||envelope.inputRevision!==revision.current||envelope.conversationId!==conversation.current||envelope.catalogHash!==live.current.versions.catalogHash)return;
   if(!response.ok||!data.ok){
    if(!data.ok&&data.error.attempt){const attempt=data.error.attempt;await dispatch({type:'agent.record',requestId:envelope.requestId,mode:attempt.mode,model:attempt.model??'unknown',promptVersion:'unknown',catalogHash:envelope.catalogHash,usage:attempt.usage,providerCalled:attempt.providerCalled,latencyMs:attempt.latencyMs,status:'lookup_error'});}
    throw new Error(data.ok?'상품 찾기 연결을 확인해주세요.':data.error.message);
   }
   if(!currentEnvelope(envelope,data.data,live.current,conversation.current,revision.current))throw new Error('화면이나 상품 정보가 바뀌었어요. 입력은 남겨뒀으니 다시 찾아주세요.');
   const value=data.data.result;
   const validResult=['show_candidates','ask_clarification','unidentified'].includes(value.action)&&value.confirmationRequired===true&&Array.isArray(value.candidates)&&value.candidates.every(c=>live.current.products.some(p=>p.sku===c.id)&&['exact','confirm','alternative'].includes(c.kind));
   const logged=await dispatch({type:'agent.record',requestId:envelope.requestId,mode:data.data.mode,model:data.data.model,promptVersion:data.data.promptVersion,catalogHash:envelope.catalogHash,usage:data.data.usage,providerCalled:data.data.mode==='live',latencyMs:data.data.latencyMs,status:validResult?'ok':'lookup_error'});
   if(!logged||!currentEnvelope(envelope,data.data,live.current,conversation.current,revision.current))return;
   if(!validResult)throw new Error('상품 응답을 확인하지 못했어요. 다시 시도해주세요.');
   if(value.action==='ask_clarification'&&(questions>=2||!value.question?.trim()))throw new Error('추가 질문 한도에 도달했어요. 상품명을 더 자세히 적어 새로 찾아주세요.');
   setOriginal(original||body.text);setHistory([...history,{role:'user',content:body.text},{role:'assistant',content:JSON.stringify(value)}]);setDisplayHistory([...displayHistory,{role:'user',content:body.text},{role:'assistant',content:value.question||value.reason}]);
   if(value.action==='ask_clarification')setQuestions(q=>q+1);
   setInterpretation(value);setSearchEnvelope(envelope);setMode(data.data.mode==='live'?'실제 AI':'시나리오 모드 (fixture)');setSelected('');setConsentKey('');setNeedId(null);
   requestAnimationFrame(()=>resultRef.current?.focus());
  }catch(e){if(!(e instanceof DOMException&&e.name==='AbortError')&&sameScope(envelope,scopeOf(live.current))&&envelope.inputRevision===revision.current)setError(e instanceof Error?e.message:'연결 오류가 발생했어요. 입력을 보존했어요.');}
  finally{if(envelope.requestId===abortRequest(envelope))setSearching(false);}
 }
 function abortRequest(e:AssistantEnvelope){return activeSearch.current===e.requestId&&e.inputRevision===revision.current&&e.conversationId===conversation.current?e.requestId:'';}
 async function dispatch(command:DemoCommand,context?:CommandContext):Promise<CommandReceipt|null>{
  const ctx=context??{...scopeOf(live.current),commandId:id(),correlationId:id()};
  if(!sameScope(ctx,scopeOf(live.current)))return null;
  try{const res=await client.dispatch(command,ctx);if(!sameScope(ctx,scopeOf(live.current)))return null;
   if(!res.ok){setError(`${res.error.message} (${res.error.code})`);setPending(null);return null;}
   if(!sameScope(ctx,scopeOf(res.data.snapshot)))return null;
   live.current=res.data.snapshot;onSnapshot(res.data.snapshot);setPending(null);return res.data;
  }catch{if(sameScope(ctx,scopeOf(live.current))){setPending({command,context:ctx});setError('저장 결과를 아직 확인하지 못했어요. 같은 명령으로 결과를 다시 확인해주세요.');}return null;}
 }
 async function perform(work:()=>Promise<void>){if(lock.current||!writable)return;lock.current=true;setBusy(true);setError('');try{await work();}catch{setError('처리를 완료하지 못했어요. 현재 요청 상태를 확인해주세요.');}finally{lock.current=false;setBusy(false);}}
 async function saveNeed():Promise<string|null>{
  if(needId)return needId;
  if(!interpretation||!searchEnvelope||!storeId||!currentEnvelope(searchEnvelope,searchEnvelope,live.current,conversation.current,revision.current)){setError('상품 찾기 결과와 선택한 점포를 다시 확인해주세요.');return null;}
  const rec=await dispatch({type:'need.record',storeId,originalText:original||input,dialogue:displayHistory.map(h=>`${h.role}: ${h.content}`),extractedClues:[],candidateSkus:interpretation.candidates.map(c=>c.id),identificationStatus:interpretation.action,reason:interpretation.reason,observedAt:live.current.clock.now,sourceRefs:interpretation.candidates.flatMap(c=>live.current.products.find(p=>p.sku===c.id)?.sourceOrigin.sourceIds??[])});
  const nid=rec?.entityIds[0];if(!nid)return null;setNeedId(nid);
  for(const candidate of interpretation.candidates){if(!await dispatch({type:'recommendation.record',needId:nid,candidateSku:candidate.id,kind:candidate.kind==='alternative'?'alternative':'exact',action:'shown'}))return null;if(rejected.includes(candidate.id)&&!await dispatch({type:'recommendation.record',needId:nid,candidateSku:candidate.id,kind:candidate.kind==='alternative'?'alternative':'exact',action:'rejected'}))return null;}
  return nid;
 }
 function selectCandidate(c:Candidate){setSelected(c.id);setConsentKey('');setQty('1');setEditId(null);setNotice('상품을 선택했어요. 수량·점포·가격을 확인한 뒤 동의해주세요.');}
 async function submit(){await perform(async()=>{
  if(!product||!canConfirmCondition(condition)||!Number.isInteger(quantity)||quantity<1||quantity>20||!accepted){setError('상품·점포·수량과 구매 동의를 확인해주세요.');return;}
  const consent={accepted:true as const,termsVersion:TERMS_VERSION};let command:DemoCommand;
  if(edit){command=edit.status==='review_required'||edit.consent.status!=='valid'?{type:'request.reconsent',requestId:edit.id,expectedRequestVersion:edit.version,conditionVersion:condition.version,quantity,acceptedPriceKrw:condition.salePriceKrw,consent}:{type:'request.changeQuantity',requestId:edit.id,expectedRequestVersion:edit.version,quantity,acceptedPriceKrw:condition.salePriceKrw,consent};}
  else {const nid=await saveNeed();if(!nid)return;const newRequest={sku:selected,storeId,quantity,acceptedPriceKrw:condition.salePriceKrw,conditionVersion:condition.version,consent,sourceNeedId:nid};command=replacing?{type:'request.replace',originalRequestId:replacing.id,expectedRequestVersion:replacing.version,newRequest}:{type:'request.create',...newRequest};if(selectedCandidate&&!await dispatch({type:'recommendation.record',needId:nid,candidateSku:selected,kind:selectedCandidate.kind==='alternative'?'alternative':'exact',action:'selected'}))return;}
  const receipt=await dispatch(command);if(receipt){const request=receipt.snapshot.requests.find(r=>receipt.entityIds.includes(r.id)&&r.actorId===receipt.snapshot.actor.id);setDetailId(request?.id??null);setPage('requests');setSelected('');setEditId(null);setReplaceId(null);setConsentKey('');setNotice('요청을 저장했어요. 아래에서 실제 진행 상태를 확인하세요.');}
 });}
 function editRequest(r:RequestDetail){setEditId(r.id);setReplaceId(null);setSelected(r.sku);setStoreId(r.storeId);setQty(String(r.quantity));setConsentKey('');setPage('wish');setError('');}
 function beginReplace(r:RequestDetail){freshConversation();setReplaceId(r.id);setPage('wish');setNotice('원요청은 그대로 유지돼요. 새 상품·가격·동의 확인 후에만 한 번에 전환해요.');inputRef.current?.focus();}
 function requestCard(r:RequestDetail){const p=snapshot.products.find(p=>p.sku===r.sku),store=snapshot.stores.find(s=>s.id===r.storeId),state=requestState(r,snapshot.clock.now),expanded=detailId===r.id;
 return <article className={styles.card} key={r.id}><span className={`${styles.badge} ${state.tone==='caution'?styles.caution:''}`}>{state.title}</span><h3>{p?.name??r.sku}</h3><p>{r.quantity}개 · {store?.name??r.storeId}</p><p className={styles.muted}>{state.description}</p><p><strong>{money(r.acceptedPriceKrw*r.quantity)}</strong> · 모의 결제</p><button type="button" className={styles.secondary} onClick={()=>setDetailId(expanded?null:r.id)} aria-expanded={expanded}>{expanded?'상세 접기':'요청 상세 보기'}</button>{expanded&&<div className={styles.detail}>
 <dl><dt>접수 순번</dt><dd>{r.sequence}번</dd><dt>점포 주소</dt><dd>{store?.address}</dd><dt>동의한 단가</dt><dd>{money(r.acceptedPriceKrw)}</dd><dt>구매 동의 시각</dt><dd>{date(r.consent.consentAt)}</dd><dt>구매 동의 유효기한</dt><dd>{date(r.consent.expiresAt)}<br/>미결제 건에 적용되는 7일 기한</dd><dt>마지막 갱신</dt><dd>{date(r.updatedAt)}</dd></dl>
 <ol className={styles.timeline}><li>요청 접수 · {date(r.createdAt)}</li><li>{r.links.length?'발주 연결 이력 있음':'발주 대기'}</li><li>{r.allocations.length?'공급 배정 이력 있음':'물량 확보 대기'}</li><li>{r.payments.some(p=>p.status==='succeeded')?'모의 결제 성공':r.payments.length?'모의 결제 실패':'모의 결제 전'}</li><li>{r.reservation?.pickupAvailableAt?'입고 후 픽업 안내 생성':'입고·픽업 안내 대기'}</li></ol>
 {r.pendingReason&&<p className={styles.caution}>현재 확인 사유: {r.pendingReason}</p>}
 {r.reservation&&<div className={styles.inset}><strong>모의 예약번호 {r.reservation.code}</strong>{r.reservation.pickupDeadlineAt!==null?<><p>픽업 마감 {date(r.reservation.pickupDeadlineAt)}</p><p>{remaining(r.reservation.pickupDeadlineAt,snapshot.clock.now)} · 픽업 알림부터 48시간</p></>:<p>픽업 48시간은 아직 시작되지 않았어요.</p>}{r.reservation.holdExpiresAt!==null&&r.reservation.status==='payment_failed'&&<p>실패 결제 물량 점유 기한: {date(r.reservation.holdExpiresAt)} · {remaining(r.reservation.holdExpiresAt,snapshot.clock.now)}</p>}</div>}
 <div className={styles.actions}>{canRetryPayment(r,snapshot.clock.now)&&<button disabled={unavailable} onClick={()=>void perform(async()=>{if(await dispatch({type:'payment.retry',requestId:r.id,paymentCycle:r.paymentCycle}))setNotice('모의 결제 결과를 갱신했어요.');})}>모의 결제 다시 시도</button>}
 {(r.status==='review_required'||(r.status==='pending'&&!r.links.some(l=>l.active)))&&<button className={styles.secondary} disabled={unavailable} onClick={()=>editRequest(r)}>{r.status==='review_required'?'현재 조건 확인하고 재동의':'수량 변경'}</button>}
 {r.status!=='cancelled'&&!r.payments.some(p=>p.status==='succeeded')&&<><button className={styles.secondary} disabled={unavailable} onClick={()=>beginReplace(r)}>다른 상품으로 전환 알아보기</button><button className={styles.secondary} disabled={unavailable} onClick={()=>void perform(async()=>{if(await dispatch({type:'request.cancel',requestId:r.id,expectedRequestVersion:r.version}))setNotice('요청을 취소했어요. 이미 제출한 점포 발주는 취소되지 않아요.');})}>이 요청 취소</button></>}</div>
 </div>}</article>;}
 return <section className={styles.customer} aria-label="원하GS 고객 화면"><header className={styles.header}><Brand/><button type="button" className={styles.iconButton} onClick={()=>setPage('notifications')} aria-label={`알림 ${notifications.filter(n=>n.readAt===null).length}개`}>알림 <span>{notifications.filter(n=>n.readAt===null).length}</span></button></header>
 <p className={styles.demo}>고객 · {snapshot.actor.displayName}<br/>모의 GS 데이터 · 실제 청구 없음 · 한 PC 데모</p>
 {!writable&&<p role="alert" className={styles.error}>현재 저장을 사용할 수 없어요. 상단 데모 도구에서 복구 상태를 확인해주세요.</p>}
 <div role="status" aria-live="polite">{notice&&<p className={styles.notice}>{notice}</p>}</div>{error&&<p role="alert" className={styles.error}>{error}</p>}
 {pending&&<button disabled={busy} onClick={()=>void perform(async()=>{if(await dispatch(pending.command,pending.context)){setNotice('같은 명령의 저장 결과를 확인했어요. 내 요청을 확인하세요.');setPage('requests');}})}>저장 결과 다시 확인</button>}
 {page==='wish'&&<>
 {replacing&&<div className={styles.notice}><strong>원요청 대신 전환을 알아보는 중</strong><p>새 동의 전까지 원요청은 유지돼요.</p><button className={styles.secondary} onClick={()=>{setReplaceId(null);setSelected('');setDetailId(replacing.id);setPage('requests');setConsentKey('');}}>전환 그만두고 원요청 보기</button></div>}
 {!selected&&<><div className={styles.hero}><p className={styles.eyebrow}>원하는 말이, 우리 동네 수요가 되니까</p><h1>없으면<br/>말하<span>GS</span></h1><p>찾는 상품의 이름이나 특징을 알려주세요.</p><svg className={styles.mascot} aria-hidden="true" viewBox="0 0 100 100"><path d="M18 48 12 12 39 29Q50 23 61 29L88 12 82 48Q96 90 50 94 4 90 18 48" fill="#f5b569" stroke="#765436" strokeWidth="3"/><path d="M21 57Q50 72 80 57Q89 85 50 88 12 85 21 57" fill="#fff2d5"/><path d="m28 46 11 2m23 0 11-2M45 63l5 5 5-5" fill="none" stroke="#3c4145" strokeWidth="4" strokeLinecap="round"/></svg></div>
 <form className={styles.searchCard} onSubmit={e=>{e.preventDefault();void search();}}><label htmlFor="customer-search">어떤 상품을 찾으세요?</label><textarea ref={inputRef} id="customer-search" value={input} maxLength={2000} rows={3} onChange={e=>changeInput(e.target.value)} placeholder="예: 쫀득버터떡빵을 찾고 있어요" onKeyDown={e=>{if(e.key==='Enter'&&!e.shiftKey&&!e.nativeEvent.isComposing){e.preventDefault();void search();}}}/><button disabled={unavailable||!input.trim()} type="submit">{searching?'상품을 찾고 있어요…':'상품 찾기'}</button><div className={styles.examples}><strong>이렇게 말해보세요</strong>{examples.map(p=><button type="button" key={p.sku} className={styles.example} onClick={()=>{setUndoInput(input);changeInput(`${p.name} 찾고 있어요`);inputRef.current?.focus();}}>{p.name} 찾고 있어요 <span>↗</span></button>)}<small>예시는 입력만 채워요. 상품 취급·재고·가격은 모의예요.</small>{undoInput!==null&&<button type="button" className={styles.link} onClick={()=>{changeInput(undoInput);setUndoInput(null);}}>이전 입력 복구</button>}</div></form></>}
 {mode&&<p className={styles.mode}>{mode}</p>}
 {interpretation&&!selected&&<div className={styles.results}><h2 ref={resultRef} tabIndex={-1}>{interpretation.action==='ask_clarification'?'조금만 더 알려주세요':interpretation.action==='unidentified'?'아직 상품을 찾지 못했어요':'찾으시는 상품이 맞나요?'}</h2><p>{interpretation.question||interpretation.reason}</p>{interpretation.action==='ask_clarification'&&<p className={styles.muted}>추가 확인 {questions}/2회 · 위 입력란에서 답해주세요.</p>}{interpretation.candidates.filter(c=>!rejected.includes(c.id)).map(c=>{const p=snapshot.products.find(p=>p.sku===c.id)!;return <article className={styles.card} key={c.id}><span className={styles.badge}>{c.kind==='alternative'?'찾으신 상품과 다른 대체 상품':'고객 확인이 필요한 상품'}</span><div className={styles.productHeading}><span aria-hidden="true" className={styles.productIcon}>{/김밥|밥/.test(p.category)?'◒':/음료|커피/.test(p.category)?'▤':'◉'}</span><div><small>{p.brand} · {p.category}</small><h3>{p.name}</h3><p>{p.flavor??'맛 상세 미확인'} · {p.size??'용량 미확인'}</p></div></div>{c.sharedEvidence.length>0&&<p>확인 단서: {c.sharedEvidence.join(' · ')}</p>}{c.differences.length>0&&<p>차이: {c.differences.join(' · ')}</p>}{c.unknownConditions.length>0&&<p className={styles.muted}>미확인: {c.unknownConditions.join(' · ')}</p>}<div className={styles.actions}><button disabled={unavailable} onClick={()=>selectCandidate(c)}>{c.kind==='alternative'?'대체 상품 확인하기':'이 상품 선택'}</button><button className={styles.secondary} disabled={unavailable} onClick={()=>{setRejected(r=>[...r,c.id]);setNotice('후보를 제외했어요. 원래 요청과 구매 동의는 바뀌지 않아요.');}}>다른 상품이에요</button></div></article>;})}
 <div className={styles.card}><h3>찾던 말을 남겨두기</h3><p>구매 요청·예약과 별도로 기록해요. 추천을 봤다는 이유로 구매 수요에 더하지 않아요.</p><label htmlFor="need-store">니즈를 남길 점포</label><select id="need-store" value={storeId} onChange={e=>{setStoreId(e.target.value);setNeedId(null);}}><option value="">점포를 선택하세요</option>{stores.map(s=><option key={s.id} value={s.id}>{s.name}</option>)}</select><button className={styles.secondary} disabled={unavailable||!storeId||!!needId} onClick={()=>void perform(async()=>{if(await saveNeed())setNotice('찾던 말을 니즈로 저장했어요. 구매 요청이나 예약은 아니에요.');})}>{needId?'니즈 저장 완료':'찾던 말 그대로 남기기'}</button></div>
 <button className={styles.link} onClick={()=>{freshConversation();inputRef.current?.focus();}}>새 대화로 다시 찾기</button></div>}
 {selected&&product&&<div className={styles.confirm}><button className={styles.link} onClick={()=>{setSelected('');setEditId(null);setConsentKey('');}}>← 상품 다시 확인</button><h1>{edit?'현재 조건 확인':'마지막으로 확인해요'}</h1><article className={styles.card}><span className={styles.badge}>{selectedCandidate?.kind==='alternative'?'대체 상품 · 새 동의 필요':'선택한 상품'}</span><h2>{product.name}</h2><p>{product.brand} · {product.size??'용량 미확인'}</p>{replacing&&<p className={styles.caution}>원요청 “{snapshot.products.find(p=>p.sku===replacing.sku)?.name}” 대신 전환해요. 새 요청 성공 시 원요청을 함께 취소하고 새 접수 순서를 받아요.</p>}<label htmlFor="quantity">수량 (1~20개)</label><input id="quantity" type="number" min={1} max={20} step={1} inputMode="numeric" value={qty} onChange={e=>setQty(e.target.value)}/></article>
 <article className={styles.card}><h2>받을 점포 한 곳</h2><p className={styles.muted}>시연 위치: {demoLocation?.name??'준비 중'} 위치를 기준으로 한 가상 위치. 실제 위치를 수집하지 않아요. 직선거리순이에요.</p>{!edit&&<button className={styles.secondary} onClick={()=>setShowMap(v=>!v)} aria-expanded={showMap}>{showMap?'지도 접기':'지도 보기'}</button>}{showMap&&!edit&&<StoreMap stores={stores} selected={storeId} onSelect={value=>{setStoreId(value);setNeedId(null);}}/>}
 <fieldset className={styles.storeList}><legend>점포 선택</legend>{stores.filter(s=>!edit||s.id===edit.storeId).map((s,i)=><label key={s.id} className={styles.store}><input type="radio" name="pickup-store" value={s.id} checked={storeId===s.id} onChange={()=>{setStoreId(s.id);setNeedId(null);}}/><span><strong>{i+1}. {s.name}</strong><small>{s.address}</small><small>{demoLocation?(distanceKm(demoLocation,s)*1000).toFixed(0)+'m · 직선거리':''}</small></span></label>)}</fieldset></article>
 <article className={styles.card}><h2>가격과 자동 구매 동의</h2><p>{conditionText(condition)}</p>{condition?.observedAt!==null&&condition?.observedAt!==undefined&&<p className={styles.muted}>모의 정보 확인 시각 {date(condition.observedAt)}</p>}{canConfirmCondition(condition)?<><div className={styles.price}><span>모의 판매 단가 {money(condition.salePriceKrw)}</span><strong>총 {money(condition.salePriceKrw*(Number.isInteger(quantity)&&quantity>0?quantity:0))}</strong></div><p>선택한 상품 {quantity||'—'}개를 {snapshot.stores.find(s=>s.id===storeId)?.name}에서 받아요. 물량이 전부 확보되면 동의한 가격으로 자동 모의 결제해요. 실제 청구는 없어요.</p><p>구매 동의는 동의 시각부터 7일간 유효해요. 가격이 달라지면 다시 확인해요. 입고 후 <strong>픽업 알림부터 48시간</strong> 안에 수령해주세요. 결제 성공 뒤 취소는 지원하지 않아요.</p>{edit&&<p className={styles.muted}>유효 요청의 수량 감소는 기존 순번·동의 만료를 유지해요. 증가·재동의는 새 순번·7일 동의로 접수해요.</p>}<label className={styles.consent}><input type="checkbox" checked={accepted} onChange={e=>setConsentKey(e.target.checked?tuple:'')}/><span>상품·한 점포·수량·단가·총액과 자동 모의 결제, 구매 동의 유효기간 및 픽업 알림부터 48시간 수령 조건을 확인하고 동의합니다.{replacing?' 원요청 대신 전환하는 것에 동의합니다.':''}</span></label></>:<p className={styles.caution}>확인된 현재 판매가가 필요해요. 다른 점포를 선택하거나 나중에 다시 확인하세요.</p>}<button disabled={unavailable||!accepted||!canConfirmCondition(condition)||!Number.isInteger(quantity)||quantity<1||quantity>20} onClick={()=>void submit()}>{busy?'안전하게 저장 중…':edit?'변경 내용에 동의하고 저장':replacing?'원요청 대신 전환하기':'요청하기'}</button></article></div>}
 {!interpretation&&!selected&&ownRequests.length>0&&<div className={styles.summary}><h2>내 요청</h2><p>{ownRequests.filter(r=>r.isActive).length}건 진행 중</p><button className={styles.secondary} onClick={()=>setPage('requests')}>내 요청 전체 보기</button></div>}
 </>}
 {(page==='requests'||page==='pickup')&&<><h1>{page==='pickup'?'내 픽업':'내 요청'}</h1><p className={styles.muted}>확보·결제·입고·픽업은 각각 다른 단계예요.</p>{ownRequests.filter(r=>page==='requests'||!!r.reservation).map(requestCard)}{!ownRequests.filter(r=>page==='requests'||!!r.reservation).length&&<div className={styles.empty}><h2>{page==='pickup'?'아직 예약된 상품이 없어요':'아직 요청이 없어요'}</h2><p>원하는 상품을 말하고, 확인 후 요청해보세요.</p><button onClick={()=>setPage('wish')}>상품 찾으러 가기</button></div>}{page==='requests'&&ownNeeds.length>0&&<section><h2>찾던 말 · 구매 요청과 별도</h2>{ownNeeds.map(n=><article key={n.id} className={styles.card}><p>“{n.originalText}”</p><small>{snapshot.stores.find(s=>s.id===n.storeId)?.name} · {date(n.createdAt)}</small><p>{n.reason}</p><span className={styles.badge}>니즈 기록 · 구매 확약 아님</span></article>)}</section>}</>}
 {page==='notifications'&&<><h1>내 알림</h1>{notifications.length?notifications.map(n=><article key={n.id} className={styles.card}><p>{n.body}</p><small>{date(n.createdAt)}</small>{n.readAt===null&&<button className={styles.secondary} disabled={unavailable} onClick={()=>void perform(async()=>{await dispatch({type:'notification.read',notificationId:n.id});})}>읽음 표시</button>}</article>):<p className={styles.empty}>새 알림이 없어요.</p>}</>}
 <nav className={styles.nav} aria-label="고객 메뉴">{([['wish','원하기'],['requests','내 요청'],['pickup','픽업']] as const).map(([key,label])=><button key={key} aria-current={page===key?'page':undefined} onClick={()=>setPage(key)}><span aria-hidden="true">{key==='wish'?'⌂':key==='requests'?'▤':'▱'}</span>{label}</button>)}</nav></section>;
}
