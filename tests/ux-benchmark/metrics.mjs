import crypto from 'node:crypto';
export const VERSION='UX-BENCHMARK-v2';
export const WORKLOAD_IDS=Object.freeze(['clear-1','clear-2','clear-3','ambiguous','reconsent','batch-10','auto-normal','exception-batch']);
export const hash=v=>crypto.createHash('sha256').update(typeof v==='string'||Buffer.isBuffer(v)?v:JSON.stringify(v)).digest('hex');
export function unionMs(intervals){const sorted=intervals.map(x=>[x.start,x.end]).sort((a,b)=>a[0]-b[0]);let total=0,end=-Infinity;for(const [a,b]of sorted){if(b<a)throw Error('INVALID_INTERVAL');total+=Math.max(0,b-Math.max(a,end));end=Math.max(end,b)}return total}
function fixedWorkloads(workloads){if(!Array.isArray(workloads)||workloads.length!==WORKLOAD_IDS.length||new Set(workloads.map(w=>w.id)).size!==WORKLOAD_IDS.length||workloads.some(w=>!WORKLOAD_IDS.includes(w.id)))throw Error('INVALID_WORKLOAD_SET')}
export function summarize(runs,workloads){
 fixedWorkloads(workloads);if(!Array.isArray(runs)||runs.some(r=>!WORKLOAD_IDS.includes(r.workload)))throw Error('INVALID_RUN_WORKLOAD');
 return workloads.map(w=>{const rows=runs.filter(r=>r.workload===w.id),valid=rows.filter(r=>r.status==='PASS');const repetitions=rows.map(r=>r.repetition),unique=new Set(repetitions.filter(r=>[1,2,3].includes(r)));const duplicateRepetitions=repetitions.length-new Set(repetitions).size,invalidRepetitions=repetitions.filter(r=>![1,2,3].includes(r)).length;
 const median=key=>{const a=valid.map(r=>r[key]).sort((a,b)=>a-b);return a.length?(a.length%2?a[Math.floor(a.length/2)]:(a[a.length/2-1]+a[a.length/2])/2):null};
 return {id:w.id,expected:3,executed:rows.length,passed:valid.length,failed:rows.filter(r=>r.status==='FAIL').length,missing:3-unique.size,duplicateRepetitions,invalidRepetitions,complete:rows.length===3&&valid.length===3&&unique.size===3&&duplicateRepetitions===0&&invalidRepetitions===0,maxActivations:rows.length?Math.max(...rows.map(r=>r.activations)):null,maxScreenTransitions:rows.length?Math.max(...rows.map(r=>r.screenTransitions)):null,medianElapsedMs:median('elapsedMs'),medianModelNetworkMs:median('modelNetworkMs'),medianNonModelMs:median('nonModelMs'),questionsMax:rows.length?Math.max(...rows.map(r=>r.questions)):null}})
}
export function compare(base,best){
 if(base.mode!==best.mode||base.workloadHash!==best.workloadHash||base.seedHash!==best.seedHash||base.clock!==best.clock)throw Error('INCOMPARABLE_RUNS');
 fixedWorkloads(base.workloads);fixedWorkloads(best.workloads);fixedWorkloads(base.summary);fixedWorkloads(best.summary);
 // Recompute from evidence: serialized summaries cannot conceal missing/duplicate runs.
 const aRows=summarize(base.runs,base.workloads),bRows=summarize(best.runs,best.workloads);
 return bRows.map(b=>{const a=aRows.find(x=>x.id===b.id);return {id:b.id,pass:a.complete&&b.complete&&b.maxActivations<=a.maxActivations&&b.maxScreenTransitions<=a.maxScreenTransitions&&b.medianNonModelMs<=a.medianNonModelMs*1.1,baseline:a,best:b}})
}
