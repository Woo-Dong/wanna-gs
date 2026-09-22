"""Execute Node's real TAP runner; fail on zero, skip, todo or cancelled tests."""
import glob
import json
import re
import subprocess
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def counts_from_tap(output):
    fields={}
    for field in ('tests','fail','cancelled','skipped','todo'):
        matches=re.findall(r'^# '+field+r' (\d+)\s*$',output,re.M)
        if len(matches)!=1: raise ValueError('missing/ambiguous TAP count: '+field)
        fields[field]=int(matches[0])
    return {'tests':fields['tests'],'failures':fields['fail'],'errors':fields['cancelled'],'skipped':fields['skipped']+fields['todo']}

if __name__=='__main__':
    if len(sys.argv)<3: raise SystemExit('usage: run_node_tests.py output-name tests-glob [tests-glob]')
    name=sys.argv[1]
    if not re.fullmatch(r'[a-z0-9-]+',name): raise SystemExit('invalid output name')
    destination=ROOT/'artifacts/raw';destination.mkdir(parents=True,exist_ok=True)
    (destination/(name+'.json')).unlink(missing_ok=True)
    collected={pattern:[f for f in glob.glob(pattern,root_dir=ROOT) if (ROOT/f).is_file()] for pattern in sys.argv[2:]}
    missing=[pattern for pattern,files in collected.items() if not files]
    if missing: raise SystemExit('zero collected files for required patterns: '+', '.join(missing))
    files=sorted(set(f for files in collected.values() for f in files))
    process=subprocess.run(['npx','--no-install','tsx','--test','--test-reporter=tap',*files],cwd=ROOT,capture_output=True,text=True)
    destination=ROOT/'artifacts/raw';destination.mkdir(parents=True,exist_ok=True)
    (destination/(name+'.tap')).write_text(process.stdout+process.stderr)
    try: counts=counts_from_tap(process.stdout)
    except ValueError as error: print(str(error));raise SystemExit(1)
    (destination/(name+'.json')).write_text(json.dumps(counts)+'\n')
    print(json.dumps({'runner':name,'exit_code':process.returncode,**counts}))
    if process.returncode: print(process.stdout[-6000:]+process.stderr[-2000:])
    raise SystemExit(0 if process.returncode==0 and counts['tests']>0 and not any(counts[x] for x in ('failures','errors','skipped')) else 1)
