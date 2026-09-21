import fs from 'node:fs';import {spawnSync} from 'node:child_process';import {fileURLToPath} from 'node:url';
export class LiveBudget {
 config:any;token='';authorizationHash='';attempts=0;stopped:string|null=null;observations:any[]=[];
 constructor(readonly root:string,readonly configPath:string,readonly origin:string){if(!configPath)throw Error('EXPLICIT_BUDGET_CONFIG_REQUIRED');this.config=JSON.parse(fs.readFileSync(configPath,'utf8'));if(this.config.origin!==origin)throw Error('AUTHORIZED_ORIGIN_MISMATCH')}
 call(operation:string,payload:any){const process=spawnSync('python3',[fileURLToPath(new URL('./budget_bridge.py',import.meta.url))],{input:JSON.stringify({root:this.root,config:this.configPath,operation,payload:{token:this.token,...payload}}),encoding:'utf8',maxBuffer:1_000_000});let result:any;try{result=JSON.parse(process.stdout)}catch{throw Error('BUDGET_BRIDGE_FAILED')};if(process.status!==0||!result.ok)throw Error(result.code??'BUDGET_BRIDGE_FAILED');return result.data}
 begin(output:string,workloadHash:string){const authorization=this.call('begin',{output,workloadHash});this.token=authorization.token;this.authorizationHash=authorization.configHash}
 async forward(route:any){if(this.stopped){await route.abort();return null}let attemptId:string;const reservedAt=performance.now();
  try{attemptId=this.call('reserve',{}).attemptId;this.attempts++}catch(error:any){this.stopped=error.message;await route.abort();return null}
  const networkStart=performance.now();let response:any,body:any=null,httpStatus=0;
  try{response=await route.fetch({maxRedirects:0,maxRetries:0,timeout:45000});httpStatus=response.status();body=await response.json()}catch{this.stopped='HTTP_TRANSPORT_UNKNOWN'}
  const networkEnd=performance.now();const finishStarted=performance.now();let result:any;
  try{result=this.call('finish',{attemptId,response:body,httpStatus});this.observations.push({attemptId,httpStatus,...result.observation});if(!result.continue)this.stopped=result.stopCode}catch{this.stopped='UNCERTAIN_LEDGER_FINISH_STOP';this.observations.push({attemptId,httpStatus,status:'unknown',usage:null,provider_called:null,cost_usd:null,pending:true})}
  const finishEnded=performance.now();const budgetInstrumentationMs=(networkStart-reservedAt)+(finishEnded-finishStarted);const deliveryStarted=performance.now();
  // Real server response is passed unchanged to the UI; the harness never substitutes a candidate.
  if(response&&((httpStatus>=200&&httpStatus<300)||httpStatus>=400))await route.fulfill({response});else await route.abort();return {attemptId,httpStatus,networkStart,networkEnd,budgetInstrumentationMs,deliveryMs:performance.now()-deliveryStarted,mode:'live',observation:result?.observation??{usage:null,provider_called:null,cost_usd:null},stopped:this.stopped};
 }
 complete(success:boolean){return this.call('complete',{success:success&&!this.stopped})}
}
