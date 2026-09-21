import {PLAN,PLAN_HASH,STUDY_ID,RUN_IDS,workloads,trials,HISTORY,canonical} from './plan.mjs';
export {unionMs} from '../metrics.mjs';
const need=(ok,code)=>{if(!ok)throw Error(code)};
export function summarize(runs){
 need(Array.isArray(runs)&&runs.length===56,'V3_TRIAL_DENOMINATOR');
 for(let i=0;i<56;i++){const r=runs[i],p=trials[i];need(r.workload===p.workload&&r.repetition===p.repetition&&['PASS','FAIL','NOT_RUN'].includes(r.status)&&r.attempted===(r.status!=='NOT_RUN'),'V3_ORDER_OR_ATTEMPT_MISMATCH')}
 return workloads.map(w=>{const rows=runs.filter(r=>r.workload===w.id),success=rows.filter(r=>r.status==='PASS');const median=k=>{const v=success.map(r=>r[k]).sort((a,b)=>a-b);return v.length?v.length%2?v[(v.length-1)/2]:(v[v.length/2-1]+v[v.length/2])/2:null};return {id:w.id,planned:7,attempted:rows.filter(r=>r.attempted).length,passed:success.length,failed:rows.filter(r=>r.status==='FAIL').length,notRun:rows.filter(r=>r.status==='NOT_RUN').length,maxActivations:success.length?Math.max(...success.map(r=>r.activations)):null,maxScreenTransitions:success.length?Math.max(...success.map(r=>r.screenTransitions)):null,medianNonModelMs:median('nonModelMs'),medianElapsedMs:median('elapsedMs'),medianModelNetworkMs:median('modelNetworkMs')}})
}
export function readyArm(v,stage){need(v.version===PLAN.version&&v.studyId===STUDY_ID&&v.runId===RUN_IDS[stage]&&v.stage===stage&&v.planHash===PLAN_HASH,'V3_IDENTITY');need(v.stopCode===null&&v.pendingAttempts===0&&v.complete===true,'V3_STUDY_STOP_OR_PENDING');const rows=summarize(v.runs);need(rows.every(r=>r.attempted===7&&r.notRun===0),'V3_UNATTEMPTED');need(rows.every(r=>stage==='best'?r.passed===7:r.passed>=3),'V3_INSUFFICIENT_SUCCESS');return rows}
export function compare(base,best){
 const a=readyArm(base,'baseline'),b=readyArm(best,'best');for(const k of ['mode','workloadHash','seedHash','clock','planHash'])need(base[k]===best[k],'V3_INCOMPARABLE');need(canonical(base.harnessHashes)===canonical(best.harnessHashes),'V3_HARNESS_MISMATCH');
 need(canonical(base.history)===canonical(HISTORY)&&canonical(best.history)===canonical(HISTORY),'V3_HISTORY_BINDING');
 return b.map((row,i)=>({id:row.id,pass:row.maxActivations<=a[i].maxActivations&&row.maxScreenTransitions<=a[i].maxScreenTransitions&&row.medianNonModelMs<=a[i].medianNonModelMs*1.1,baseline:a[i],best:row,scope:'all successful trials conditional convenience; failed trials excluded from time only, never from denominator'}))
}
