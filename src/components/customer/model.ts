import type { DemoSnapshot, RequestDetail, Scope, Condition } from '../../contracts/domain';
import type { AssistantEnvelope } from '../../contracts/assistant';
export const TERMS_VERSION='wanna-gs-consent-v1';
export const scopeOf=(s:DemoSnapshot):Scope=>({sessionId:s.session.id,generation:s.session.generation,actorId:s.actor.id,roleEpoch:s.roleEpoch});
export const sameScope=(a:Scope,b:Scope)=>a.sessionId===b.sessionId&&a.generation===b.generation&&a.actorId===b.actorId&&a.roleEpoch===b.roleEpoch;
export function currentEnvelope(sent:AssistantEnvelope, received:AssistantEnvelope, snapshot:DemoSnapshot, conversationId:string,inputRevision:number){return sameScope(sent,scopeOf(snapshot))&&sameScope(sent,received)&&sent.requestId===received.requestId&&sent.conversationId===received.conversationId&&sent.conversationId===conversationId&&sent.inputRevision===received.inputRevision&&sent.inputRevision===inputRevision&&sent.catalogHash===received.catalogHash&&sent.catalogHash===snapshot.versions.catalogHash;}
export const money=(v:number)=>new Intl.NumberFormat('ko-KR').format(v)+'원';
export const date=(v:number|null)=>v===null?'아직 시작되지 않았어요':new Intl.DateTimeFormat('ko-KR',{timeZone:'Asia/Seoul',year:'numeric',month:'long',day:'numeric',hour:'2-digit',minute:'2-digit',hour12:false}).format(v)+' (KST)';
export function remaining(deadline:number,now:number){const minutes=Math.ceil((deadline-now)/60000);return minutes<=0?'기한 종료':minutes>=60?`${Math.floor(minutes/60)}시간 ${minutes%60}분 남음`:`${minutes}분 남음`;}
export function requestState(r:RequestDetail,now:number):{title:string;description:string;tone:'normal'|'caution'|'success'}{
 const v=r.reservation;
 if(r.status==='cancelled')return {title:'요청 취소',description:'이 요청은 수요에서 제외됐어요.',tone:'normal'};
 if(v?.status==='collected')return {title:'수령 완료',description:'점포에서 모의 수령 처리를 완료했어요.',tone:'success'};
 if(v?.status==='pickup_expired'||(v?.status==='pickup_ready'&&v.pickupDeadlineAt!==null&&now>=v.pickupDeadlineAt))return {title:'수령 기한이 지났어요',description:'수령할 수 없어요. 자동 환불이나 재판매는 진행하지 않아요.',tone:'caution'};
 if(v?.status==='pickup_ready')return {title:'여기 있GS · 픽업 가능',description:'점포 경영주에게 아래 모의 예약번호를 보여주세요.',tone:'success'};
 if(v?.status==='confirmed')return {title:'담아두GS · 예약 확정',description:'모의 결제를 마쳤어요. 아직 입고 대기 중이며 지금 수령할 수 없어요.',tone:'success'};
 if(r.status==='review_required')return {title:'다시 동의가 필요해요',description:'현재 상품·가격·수량을 확인하면 새 접수 순서로 요청을 이어가요.',tone:'caution'};
 if(v?.status==='payment_failed')return {title:'모의 결제 실패',description:'예약은 확정되지 않았어요. 점유 기한 안에서 한 번 다시 시도할 수 있어요.',tone:'caution'};
 if(r.status==='allocated'||v?.status==='payment_pending')return {title:'물량 확보 · 결제 처리 중',description:'배정됐지만 아직 예약 확정 전이에요.',tone:'normal'};
 if(r.links.some(l=>l.active))return {title:'점포에서 발주를 진행했어요',description:'아직 공급 확보·예약 확정 전이에요.',tone:'normal'};
 return {title:'요청 접수 · 물량 확보 전',description:'점포에 수요를 남겼어요. 확보 전에는 결제하지 않아요.',tone:'normal'};
}
export function conditionText(c:Condition|undefined){
 if(!c)return '점포 조건을 확인하지 못했어요. 미취급으로 단정할 수 없어요.';
 if(c.observationStatus!=='observed')return '점포 조건 확인이 필요해요. 조회 오류는 품절이 아니에요.';
 const stock=c.stockQty===null?'재고 미확인':`모의 점포 재고 ${c.stockQty}개`;
 const assortment=c.assortmentStatus==='not_listed'?'현재 점포 미취급':c.assortmentStatus==='unknown'?'취급 여부 미확인':'모의 취급 상품';
 const supply=c.supplyStatus==='available'?`추가 발주 접수 가능 ${c.availableOrderQty}개`:c.supplyStatus==='restricted'?'모의 공급 제한':c.supplyStatus==='discontinued'?'모의 공급 종료':'공급 상태 미확인';
 return `${assortment} · ${stock} · ${supply}${c.reason?' · '+c.reason:''}`;
}
export const canConfirmCondition=(c:Condition|undefined):c is Condition=>!!c&&c.observationStatus==='observed'&&Number.isInteger(c.salePriceKrw)&&c.salePriceKrw>=0;
export function canRetryPayment(r:RequestDetail,now:number){return r.status!=='review_required'&&r.consent.status==='valid'&&r.reservation?.status==='payment_failed'&&r.reservation.holdExpiresAt!==null&&now<r.reservation.holdExpiresAt&&r.payments.filter(p=>p.cycle===r.paymentCycle).length<2;}
export function distanceKm(a:{lat:number;lng:number},b:{lat:number;lng:number}){const rad=Math.PI/180;const dlat=(b.lat-a.lat)*rad,dlng=(b.lng-a.lng)*rad;return 6371*2*Math.asin(Math.sqrt(Math.sin(dlat/2)**2+Math.cos(a.lat*rad)*Math.cos(b.lat*rad)*Math.sin(dlng/2)**2));}
