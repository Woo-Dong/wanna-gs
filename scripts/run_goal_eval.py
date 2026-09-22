"""Coordinator/evaluator entry point using a conservative 50-call pre-baseline reserve.
No keys or bypass data are copied into output. Holdout remains evaluator-only.
"""
import sys,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import run_nl_eval as r
import argparse
p=argparse.ArgumentParser();p.add_argument('--config',required=True);p.add_argument('--states',required=True);p.add_argument('--cases',required=True);p.add_argument('--coverage',required=True);p.add_argument('--output',required=True);p.add_argument('--execute',action='store_true');p.add_argument('--resume',action='store_true');p.add_argument('--holdout',action='store_true');p.add_argument('--frozen-best');a=p.parse_args()
try:
 cases_path=(r.ROOT/a.cases).resolve()
 if any('holdout' in part.lower() for part in cases_path.parts) and not a.holdout:raise r.RunnerError('PROTECTED_HOLDOUT_NOT_AUTHORIZED')
 config=r.load_json(r.ROOT/a.config);cases=r.read_jsonl(cases_path);states=r.load_json(r.ROOT/a.states)
 if type(config.get('prior_call_reserve')) is not int or config['prior_call_reserve']!=50:raise r.RunnerError('BUDGET_RESERVE_CONFIG_CHANGED')
 config,ids,protected=r.check_inputs(cases,config,r.load_json(r.ROOT/a.coverage),r.ROOT/'data/seed/products.json',states,a.holdout,r.load_json(r.ROOT/a.frozen_best) if a.frozen_best else None)
 output=(r.ROOT/a.output).resolve()
 if not output.is_relative_to(r.ROOT/'artifacts/private'):raise r.RunnerError('EVAL_OUTPUT_MUST_BE_PRIVATE')
 budget=r.Budget(r.ROOT/'artifacts/private/run-20260921/nl-budget.json',prior_reserve=50)
 if not a.execute:
  print(json.dumps({'status':'PLAN_VALID','cases':len(cases),'user_turns':sum(len(c['turns']) for c in cases),'prior_call_reserve':50,'prior_actual_calls':'unknown','future_reserved_calls':sum(config['mandatory_reserve'].values()),'model_calls':0}));sys.exit(0)
 runner=r.Runner(cases,config,output,budget,r.HttpTransport(config['origin'],r.ROOT/'artifacts/private/run-20260921/vercel-bypass.json'),states)
 result=runner.run(ids,resume=a.resume);print(json.dumps(result,ensure_ascii=False));sys.exit(0 if result['complete'] and not result['stop_code'] else 2)
except r.RunnerError as e:
 print(json.dumps({'status':'STOPPED','code':str(e)}));sys.exit(2)

except Exception:
 print(json.dumps({'status':'STOPPED','code':'INVALID_LOCAL_INPUT_OR_IO'}));sys.exit(2)
