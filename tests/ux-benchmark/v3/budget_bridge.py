"""ADR007 private bridge. Shared current goal root only; no HTTP or provider calls."""
import fcntl,hashlib,importlib.util,json,math,sys,uuid
from pathlib import Path
STUDY='ux-study-v3-01'
RUNS={'baseline':'ux-baseline-b0-v3-01','best':'ux-best-v3-01'}
BUDGET_SOURCES=('scripts/run_nl_eval.py','evals/adapter.py','evals/scorer.py')
FATAL={'LLM_AUTH_ERROR','LLM_QUOTA','LLM_CONFIGURATION','LLM_MODEL_UNAVAILABLE','LOCAL_CALL_LIMIT','CONNECTION_NOT_READY','CATALOG_MISMATCH','INVALID_INPUT'}
def fp(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()
def run(root,config_path,operation,payload):
 root=Path(root).resolve();c=json.loads(Path(config_path).read_text());rid=c.get('run_id');stage=c.get('stage')
 if c.get('approved') is not True or c.get('study_id')!=STUDY or stage not in RUNS or rid!=RUNS[stage] or c.get('authorized_calls')!=42 or c.get('prior_call_reserve')!=50:raise ValueError('V3_AUTHORIZATION_REQUIRED')
 if str(root)!=c.get('budget_root'):raise ValueError('V3_BUDGET_ROOT_MISMATCH')
 script=root/'scripts/run_nl_eval.py'
 if hashlib.sha256(script.read_bytes()).hexdigest()!=c.get('budget_runner_hash') or c.get('budget_source_files')!={f:hashlib.sha256((root/f).read_bytes()).hexdigest() for f in BUDGET_SOURCES}:raise ValueError('V3_BUDGET_SOURCE_MISMATCH')
 sys.path.insert(0,str(root/'evals'));s=importlib.util.spec_from_file_location('goal_budget_v3',script);r=importlib.util.module_from_spec(s);s.loader.exec_module(r)
 if r.GOAL_API_COST_SOFT_LIMIT_USD!=20:raise ValueError('V3_BUDGET_LIMIT_MISMATCH')
 reserve=c.get('mandatory_reserve');cost=c.get('mandatory_cost_reserve_usd')
 if not isinstance(reserve,dict) or not reserve or any(type(x)!=int or x<0 for x in reserve.values()) or type(cost) not in (int,float) or not math.isfinite(cost) or cost<0:raise ValueError('V3_RESERVE_REQUIRED')
 for key in ['origin','model','prompt_version','catalog_hash','plan_hash','workload_hash']:
  if not isinstance(c.get(key),str) or not c[key]:raise ValueError('V3_EXPECTED_BINDING_REQUIRED')
 ledger=root/'artifacts/private/run-20260921/nl-budget.json'
 if not ledger.is_file():raise ValueError('V3_EXISTING_LEDGER_REQUIRED')
 budget=r.Budget(ledger,prior_reserve=50);identity='UX3-'+rid;cfg=fp(c)
 with open(str(ledger)+'.ux-v3.lock','a') as lock:
  fcntl.flock(lock,fcntl.LOCK_EX)
  with budget.locked() as state:
   study=state.setdefault('ux_v3_studies',{}).setdefault(STUDY,{'status':'active','arms':{},'workload_hash':c['workload_hash'],'plan_hash':c['plan_hash']})
   if study['status']=='stopped' and operation!='complete':raise ValueError('V3_STUDY_STOPPED_NO_REPLAY')
   if study['workload_hash']!=c['workload_hash'] or study['plan_hash']!=c['plan_hash']:raise ValueError('V3_STUDY_BINDING_MISMATCH')
   claim=study['arms'].get(stage)
   if operation=='begin':
    if payload.get('output')!=c.get('output') or payload.get('workloadHash')!=c['workload_hash']:raise ValueError('V3_CLAIM_BINDING_MISMATCH')
    if claim is not None:raise ValueError('V3_RUN_ALREADY_CLAIMED')
    if stage=='best' and study['arms'].get('baseline',{}).get('status')!='complete':raise ValueError('V3_BASELINE_NOT_COMPLETE')
    claim={'config_hash':cfg,'token':str(uuid.uuid4()),'status':'active','output':payload['output'],'trials':[],'active_trial':None};study['arms'][stage]=claim
   else:
    if not claim or claim['config_hash']!=cfg or claim['token']!=payload.get('token'):raise ValueError('V3_AUTHORIZATION_CHANGED')
   attempts={k:a for k,a in state['attempts'].items() if a['run_id']==identity};pending=any(a['status']=='pending' for a in attempts.values())
   if operation=='trial.begin':
    if claim['status']!='active' or claim['active_trial'] is not None or pending or payload.get('index')!=len(claim['trials']) or len(claim['trials'])>=56:raise ValueError('V3_TRIAL_SEQUENCE')
    claim['active_trial']={'index':payload['index'],'failed':False,'attempts':0}
   if operation=='reserve':
    trial=claim['active_trial'];i=trial['index'] if trial else -1;maximum=2 if 21<=i<28 else 1 if i<21 or 42<=i<49 else 0
    if claim['status']!='active' or not trial or trial['failed'] or pending or len(attempts)>=42 or trial['attempts']>=maximum:raise ValueError('V3_RESERVE_STOP')
   if operation=='finish' and payload.get('attemptId') not in attempts:raise ValueError('V3_ATTEMPT_NOT_OWNED')
   if operation=='trial.end':
    if not claim['active_trial'] or pending or payload.get('status') not in ('PASS','FAIL'):raise ValueError('V3_TRIAL_END_INVALID')
    if payload['status']=='PASS' and claim['active_trial']['failed']:raise ValueError('V3_FAILED_TRIAL_CANNOT_PASS')
    claim['trials'].append({'index':claim['active_trial']['index'],'status':payload['status']});claim['active_trial']=None
   if operation=='stop':study['status']='stopped';claim['status']='stopped'
   if operation=='complete':
    complete=study['status']=='active' and len(claim['trials'])==56 and claim['active_trial'] is None and not pending
    claim['status']='complete' if complete else 'stopped'
    if not complete:study['status']='stopped'
  if operation=='begin':return {'token':claim['token'],'configHash':cfg}
  if operation=='reserve':
   try:aid=budget.reserve(identity,sum(reserve.values())+41-len(attempts),cost+(41-len(attempts))*.05)
   except Exception:
    with budget.locked() as state:state['ux_v3_studies'][STUDY]['status']='stopped'
    raise
   with budget.locked() as state:state['ux_v3_studies'][STUDY]['arms'][stage]['active_trial']['attempts']+=1
   return {'attemptId':aid}
  if operation=='finish':
   raw=payload.get('response');http=payload.get('httpStatus');good=isinstance(raw,dict) and raw.get('ok') is True and http==200
   data=raw.get('data',{}) if good else raw.get('error',{}).get('attempt',{}) if isinstance(raw,dict) and isinstance(raw.get('error'),dict) else {}
   if not isinstance(data,dict):data={}
   called=(True if data.get('mode')=='live' else False if data.get('mode')=='fixture' else None) if good else data.get('providerCalled');called=called if type(called)==bool else None
   usage,usd=r.usage_record(data.get('usage'));code=raw.get('error',{}).get('code') if isinstance(raw,dict) and isinstance(raw.get('error'),dict) else None
   mismatch=data.get('mode')!='live' or data.get('model')!=c['model'] or (good and (data.get('promptVersion')!=c['prompt_version'] or data.get('catalogHash')!=c['catalog_hash']))
   stop=called is None or usage is None or usd is None or mismatch or code in FATAL or http in (401,403)
   valid=good and not stop
   observation={'status':'ok' if valid else 'unknown' if called is None or usage is None else 'failed','provider_called':called,'usage':usage,'cost_usd':usd}
   budget.finish(payload['attemptId'],observation)
   with budget.locked() as state:
    study=state['ux_v3_studies'][STUDY];claim=study['arms'][stage]
    if not valid:claim['active_trial']['failed']=True
    if stop:study['status']='stopped';claim['status']='stopped'
   return {'trialFailed':not valid,'stopCode':'V3_UNKNOWN_FATAL_OR_CONTRACT_STOP' if stop else None,'observation':observation}
  if operation=='complete':return {'complete':complete,'pending':pending,'budget':budget.snapshot()}
  if operation in ('trial.begin','trial.end','stop'):return {'ok':True}
  raise ValueError('V3_UNKNOWN_OPERATION')
if __name__=='__main__':
 try:
  q=json.load(sys.stdin);print(json.dumps({'ok':True,'data':run(q['root'],q['config'],q['operation'],q.get('payload',{}))}))
 except Exception as e:
  code=str(e);safe=code if code.startswith('V3_') or code in ('CALL_RESERVE_STOP','COST_SOFT_STOP','BUDGET_RESERVE_CONFIG_CHANGED','ATTEMPT_LEDGER_CONFLICT') else 'V3_BRIDGE_INPUT_OR_IO';print(json.dumps({'ok':False,'code':safe}));sys.exit(2)
