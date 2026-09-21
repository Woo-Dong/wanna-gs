'use client';
import { useEffect, useRef, useState } from 'react';
type State={writable:boolean;generation:number;foreignKeys:number;notes:{id:string;actor:string;body:string}[]};
export default function Page(){
 const worker=useRef<Worker|null>(null);
 const current=useRef<State|null>(null);
 const modelRequest=useRef(0);
 const [state,setState]=useState<State|null>(null);
 const [role,setRole]=useState('customer');
 const [text,setText]=useState('');
 const [busy,setBusy]=useState(true);
 const [message,setMessage]=useState('SQLite를 준비하고 있어요.');
 const [accessToken,setAccessToken]=useState('');
 const [modelText,setModelText]=useState('');
 const [modelBusy,setModelBusy]=useState(false);
 const [modelMessage,setModelMessage]=useState('실제 모델 연결은 별도 검사입니다.');
 useEffect(()=>{
   const w=new Worker('/probe/worker.js'); worker.current=w;
   w.onmessage=({data})=>{
     setBusy(false);
     if(data.state){current.current=data.state;setState(data.state);}
     setMessage(data.ok?'저장 완료 · 같은 탭에서 역할을 바꾸거나 새로고침해 보세요.':`${data.error}: 저장하지 못했어요. 마지막 저장 상태를 유지합니다. 재시도하거나 점검 데이터를 초기화하세요.`);
     if(data.ok)setText('');
   };
   w.onerror=()=>{setBusy(false);setMessage('초기화 실패: 페이지를 새로고침해 다시 시도하세요.');};
   w.postMessage({id:crypto.randomUUID(),type:'init'});
   return()=>{modelRequest.current++;w.terminate();};
 },[]);
 const send=(type:string,fail=false)=>{
   if(type==='reset'){modelRequest.current++;setModelMessage('이전 모델 응답은 초기화된 데이터에 적용하지 않습니다.');}
   setBusy(true);setMessage('처리 중…');
   worker.current?.postMessage({id:crypto.randomUUID(),type,fail,payload:{id:crypto.randomUUID(),actor:role,body:text,generation:state?.generation}});
 };
 const runModel=async()=>{
   const generation=current.current?.generation;
   if(generation===undefined||!current.current?.writable)return;
   const requestId=++modelRequest.current;
   const actor=role;
   setModelBusy(true);setModelMessage('서버에서 실제 모델 응답을 기다리고 있어요.');
   try{
     const response=await fetch('/api/model-probe',{method:'POST',headers:{'Content-Type':'application/json','x-probe-token':accessToken},body:JSON.stringify({text:modelText}),signal:AbortSignal.timeout(55000)});
     const result=await response.json();
     if(requestId!==modelRequest.current||current.current?.generation!==generation){setModelMessage('초기화 전 응답을 버렸어요. 새 점검을 실행하세요.');return;}
     if(!response.ok)throw new Error(typeof result.error==='string'?result.error:'MODEL_REQUEST_FAILED');
     if(result.mode!=='live'||result.result?.ok!==true||typeof result.result.message!=='string'||!result.result.message.trim()||result.result.message.length>80)throw new Error('MODEL_OUTPUT_INVALID');
     setModelMessage('실제 모델 응답을 확인했어요. SQLite 저장 결과는 아래 상태에서 확인하세요.');
     setBusy(true);
     worker.current?.postMessage({id:crypto.randomUUID(),type:'add',payload:{id:crypto.randomUUID(),actor,body:result.result.message,generation}});
   }catch(error){
     if(requestId===modelRequest.current)setModelMessage(`${error instanceof Error?error.message:'MODEL_REQUEST_FAILED'}: 모델 결과를 저장하지 않았어요. 입력과 접근 권한을 확인하고 재시도하세요.`);
   }finally{setModelBusy(false);}
 };
 return <main>
   <header><span className="tag">20260921 · 사전점검 전용</span><h1>원하GS</h1><p>‘원하지쓰’라고 읽어요.</p></header>
   <section>
     <h2>한 탭 저장·복원 점검</h2>
     <p>제품 기능 구현 전 연결 검사입니다. 모의 메모만 저장합니다. 실제 거래·결제·인증 기능이 아닙니다.</p>
     <nav aria-label="점검 역할"><button onClick={()=>setRole('customer')} aria-pressed={role==='customer'}>고객</button><button onClick={()=>setRole('merchant')} aria-pressed={role==='merchant'}>경영주</button></nav>
     <h3>{role==='customer'?'고객':'경영주'} 화면</h3>
     <form onSubmit={e=>{e.preventDefault();send('add');}}>
       <label htmlFor="note">점검 메모 (1~80자)</label>
       <input id="note" maxLength={80} value={text} onChange={e=>setText(e.target.value)} disabled={busy}/>
       <button disabled={busy||!state?.writable||!text.trim()}>메모 저장</button>
     </form>
     <div className="controls"><button disabled={busy||!state?.writable||!text.trim()} onClick={()=>send('add',true)}>다음 저장 실패 시험</button><button disabled={busy} onClick={()=>send('reset')}>점검 데이터 초기화</button></div>
     <p role="status" className="status">{message}</p>
     <p>세대: <b data-testid="generation">{state?.generation??'—'}</b> · 외래 키: {state?.foreignKeys===1?'켜짐':'확인 중'}</p>
     <p>저장된 메모: <b data-testid="count">{state?.notes.length??0}</b>개</p>
     <ul>{state?.notes.map(note=><li key={note.id}><span>{note.actor==='customer'?'고객':'경영주'}</span> {note.body}</li>)}</ul>
     <hr/><h3>실제 모델 연결 점검</h3>
     <p>접근 토큰은 이 화면의 메모리에만 두며 새로고침하면 지워집니다. 서버 인스턴스당 최대 6회 호출 제한은 계정 전체 비용 한도가 아닙니다.</p>
     <form onSubmit={e=>{e.preventDefault();void runModel();}} autoComplete="off">
       <label htmlFor="probe-token">점검 접근 토큰</label>
       <input id="probe-token" type="password" autoComplete="off" value={accessToken} onChange={e=>setAccessToken(e.target.value)}/>
       <label htmlFor="model-text">모델 점검 입력 (1~80자)</label>
       <input id="model-text" maxLength={80} value={modelText} onChange={e=>setModelText(e.target.value)}/>
       <button disabled={busy||modelBusy||!state?.writable||!accessToken||!modelText.trim()}>실제 모델 응답 저장</button>
     </form>
     <p role="status" className="status">{modelMessage}</p>
   </section>
   <footer>SQLite probe-v1 · seed 20260921-v1 · sql.js 1.14.2<br/>이 배포의 한 브라우저 탭에서만 시연하세요.</footer>
 </main>;
}
