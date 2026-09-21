"""Check exact accepted context inputs and referenced requirement IDs."""
import hashlib
import json
import re
from pathlib import Path
from gate_contract import ROOT
config = json.loads((ROOT / 'quality/gates.json').read_text())
context = json.loads((ROOT / config['context_manifest']).read_text())
errors = []
for name, expected in context['files'].items():
    path = ROOT / name
    if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != expected:
        errors.append('stale/missing context input: ' + name)
core = (ROOT / 'docs/CORE_REQUIREMENTS.md').read_text()
for task in config['tasks']:
    for requirement in task['requirements']:
        if not re.search(r'\b' + re.escape(requirement) + r'\b', core):
            errors.append('unknown core requirement: ' + requirement)
print(json.dumps({'context':context['id'],'status':'FAIL' if errors else 'PASS','errors':errors},ensure_ascii=False))
raise SystemExit(bool(errors))
