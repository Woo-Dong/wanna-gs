"""Private stdin/stdout bridge to the existing goal Budget. Never performs HTTP."""
import contextlib,fcntl,hashlib,importlib.util,json,math,sys,uuid
from pathlib import Path

def run(root,config_path,operation,payload):
    root=Path(root).resolve();config=json.loads(Path(config_path).read_text())
    sys.path.insert(0,str(root/'evals'))
    spec=importlib.util.spec_from_file_location('ux_goal_budget',root/'scripts/run_nl_eval.py');r=importlib.util.module_from_spec(spec);spec.loader.exec_module(r)
    if config.get('approved') is not True or config.get('prior_call_reserve')!=50:raise ValueError('EXPLICIT_COORDINATOR_AUTHORIZATION_REQUIRED')
    rid=config.get('run_id');cap=config.get('authorized_calls');reserve=config.get('mandatory_reserve');cost=config.get('mandatory_cost_reserve_usd')
    if not isinstance(rid,str) or not rid.strip() or len(rid)>100 or config.get('stage') not in ['baseline','best']:raise ValueError('INVALID_UX_RUN_IDENTITY')
    if type(cap) is not int or cap<18 or cap>2400:raise ValueError('AUTHORIZED_CALL_LIMIT_REQUIRED')
    if not isinstance(reserve,dict) or not reserve or any(type(n) is not int or n<0 for n in reserve.values()):raise ValueError('MANDATORY_RESERVE_REQUIRED')
    if isinstance(cost,bool) or not isinstance(cost,(int,float)) or not math.isfinite(cost) or cost<0:raise ValueError('MANDATORY_COST_RESERVE_REQUIRED')
    for key in ['origin','model','prompt_version','catalog_hash']:
        if not isinstance(config.get(key),str) or not config[key]:raise ValueError('EXPECTED_MODEL_CONFIG_REQUIRED')
    ledger=root/'artifacts/private/run-20260921/nl-budget.json'
    if not ledger.is_file():raise ValueError('EXISTING_GOAL_LEDGER_REQUIRED')
    budget=r.Budget(ledger,prior_reserve=50);identity='UX-'+rid;cfg_hash=r.fingerprint(config)
    guard=ledger.parent/('ux-'+hashlib.sha256(rid.encode()).hexdigest()+'.lock')
    with open(guard,'a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX)
        with budget.locked() as state:
            claims=state.setdefault('ux_claims',{});claim=claims.get(rid)
            if operation=='begin':
                if claim is not None:raise ValueError('UX_RUN_ALREADY_CLAIMED_NO_REPLAY')
                claim={'config_hash':cfg_hash,'token':str(uuid.uuid4()),'status':'active','output':payload['output'],'workload_hash':payload['workloadHash']};claims[rid]=claim
            else:
                if not claim or claim['config_hash']!=cfg_hash or claim['token']!=payload.get('token'):raise ValueError('UX_AUTHORIZATION_CHANGED')
            attempts={aid:a for aid,a in state['attempts'].items() if a['run_id']==identity}
            if operation=='reserve':
                if claim['status']!='active':raise ValueError('UX_STOPPED_NO_REPLAY')
                if any(a['status']=='pending' for a in attempts.values()):raise ValueError('UNCERTAIN_PENDING_NO_REPLAY')
                if len(attempts)>=cap:raise ValueError('UX_AUTHORIZED_CALL_LIMIT')
            if operation=='finish' and payload.get('attemptId') not in attempts:raise ValueError('ATTEMPT_NOT_OWNED')
        if operation=='begin':return {'token':claim['token'],'configHash':cfg_hash,'authorizedCalls':cap}
        if operation=='reserve':
            # Reserve every remaining authorized UX call and all future mandatory stages.
            aid=budget.reserve(identity,sum(reserve.values())+cap-len(attempts)-1,cost+(cap-len(attempts)-1)*.05)
            return {'attemptId':aid}
        if operation=='finish':
            raw=payload.get('response');status=payload.get('httpStatus');data=raw.get('data',{}) if isinstance(raw,dict) else {};error=raw.get('error',{}) if isinstance(raw,dict) else {};attempt=error.get('attempt',{}) if isinstance(error,dict) else {}
            if not isinstance(data,dict):data={}
            if not isinstance(attempt,dict):attempt={}
            success=isinstance(raw,dict) and raw.get('ok') is True and status==200
            mode=data.get('mode') if success else attempt.get('mode');called=(True if mode=='live' else False if mode=='fixture' else None) if success else attempt.get('providerCalled');called=called if type(called) is bool else None
            usage,cost_usd=r.usage_record(data.get('usage') if success else attempt.get('usage'))
            valid=success and mode=='live' and data.get('model')==config['model'] and data.get('promptVersion')==config['prompt_version'] and data.get('catalogHash')==config['catalog_hash'] and usage is not None and cost_usd is not None
            observation={'status':'ok' if valid else 'unknown' if called is None or usage is None else 'failed','provider_called':called,'usage':usage,'cost_usd':cost_usd}
            budget.finish(payload['attemptId'],observation)
            if not valid:
                with budget.locked() as state:state['ux_claims'][rid]['status']='stopped'
            return {'continue':valid,'observation':observation,'stopCode':None if valid else 'HTTP_MODEL_ERROR_OR_UNKNOWN_USAGE_STOP'}
        if operation=='complete':
            with budget.locked() as state:
                unresolved=any(a['run_id']==identity and a['status']=='pending' for a in state['attempts'].values())
                state['ux_claims'][rid]['status']='complete' if payload.get('success') is True and not unresolved and state['ux_claims'][rid]['status']=='active' else 'stopped'
            return {'budget':budget.snapshot(),'pending':unresolved}
        raise ValueError('UNKNOWN_OPERATION')

if __name__=='__main__':
    try:
        request=json.load(sys.stdin);result=run(request['root'],request['config'],request['operation'],request.get('payload',{}));print(json.dumps({'ok':True,'data':result}))
    except Exception as exc:
        # No remote body, auth content, path or exception text escapes the bridge.
        safe={'EXPLICIT_COORDINATOR_AUTHORIZATION_REQUIRED','INVALID_UX_RUN_IDENTITY','AUTHORIZED_CALL_LIMIT_REQUIRED','MANDATORY_RESERVE_REQUIRED','MANDATORY_COST_RESERVE_REQUIRED','EXPECTED_MODEL_CONFIG_REQUIRED','EXISTING_GOAL_LEDGER_REQUIRED','UX_RUN_ALREADY_CLAIMED_NO_REPLAY','UX_AUTHORIZATION_CHANGED','UX_STOPPED_NO_REPLAY','UNCERTAIN_PENDING_NO_REPLAY','UX_AUTHORIZED_CALL_LIMIT','ATTEMPT_NOT_OWNED','CALL_RESERVE_STOP','COST_SOFT_STOP','BUDGET_RESERVE_CONFIG_CHANGED'}
        code=str(exc) if str(exc) in safe else 'BUDGET_BRIDGE_INVALID_INPUT_OR_IO';print(json.dumps({'ok':False,'code':code}));sys.exit(2)
