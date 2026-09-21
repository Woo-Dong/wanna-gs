'use client';
import type { CommandContext,CommandReceipt,DemoClient,DemoCommand,DemoQuery,DemoSnapshot,Result,Scope } from '../contracts/domain';
import type { WorkerOperation } from './runtime';
export class BrowserDemoClient implements DemoClient {
  private worker:Worker;private pending=new Map<string,(v:Result<unknown>)=>void>();private listeners=new Set<(s:DemoSnapshot)=>void>();
  constructor(){this.worker=new Worker(new URL('./worker.ts',import.meta.url));this.worker.onmessage=(event:MessageEvent)=>{const {messageId,result}=event.data;const resolve=this.pending.get(messageId);if(resolve){this.pending.delete(messageId);resolve(result)}};this.worker.onerror=()=>{for(const resolve of this.pending.values())resolve({ok:false,error:{code:'WORKER_FAILED',message:'데모 저장소 연결이 중단됐습니다. 새로고침해 주세요.',retryable:true}});this.pending.clear()}}
  private async call<T>(request:WorkerOperation|{operation:'resetIncompatible';confirmed:boolean}):Promise<Result<T>>{const messageId=crypto.randomUUID();const result=await new Promise<Result<unknown>>(resolve=>{this.pending.set(messageId,resolve);this.worker.postMessage({messageId,request})}) as Result<T>;if(result.ok){const data=result.data as unknown as DemoSnapshot|CommandReceipt;const snapshot=data&&typeof data==='object'?('snapshot' in data?data.snapshot:'contractVersion' in data?data:null):null;if(snapshot)for(const listener of this.listeners)listener(snapshot)}return result}
  initialize(){return this.call<DemoSnapshot>({operation:'initialize'})}
  snapshot(scope:Scope){return this.call<DemoSnapshot>({operation:'snapshot',scope})}
  dispatch(command:DemoCommand,context:CommandContext){return this.call<CommandReceipt>({operation:'command',command,context})}
  query(query:DemoQuery,scope:Scope){return this.call<unknown>({operation:'query',query,scope})}
  switchRole(actorId:string,scope:Scope){return this.call<DemoSnapshot>({operation:'switchRole',actorId,scope})}
  resetIncompatible(confirmed:boolean){return this.call<DemoSnapshot>({operation:'resetIncompatible',confirmed})}
  subscribe(listener:(snapshot:DemoSnapshot)=>void){this.listeners.add(listener);return ()=>{this.listeners.delete(listener)}}
  dispose(){this.worker.terminate();this.listeners.clear();for(const resolve of this.pending.values())resolve({ok:false,error:{code:'CLIENT_CLOSED',message:'화면을 닫았습니다.',retryable:false}});this.pending.clear()}
}
let singleton:BrowserDemoClient|undefined;
export function getDemoClient(){if(typeof window==='undefined')throw Error('Browser only');return singleton??=new BrowserDemoClient()}
export function scopeFrom(snapshot:DemoSnapshot):Scope{return {sessionId:snapshot.session.id,generation:snapshot.session.generation,actorId:snapshot.actor.id,roleEpoch:snapshot.roleEpoch}}
export function commandContext(snapshot:DemoSnapshot,commandId=crypto.randomUUID()):CommandContext{return {...scopeFrom(snapshot),commandId,correlationId:commandId}}
