"""Fail closed over executed checks and independent review for the current scope."""
import datetime
import json
import subprocess
import sys
from pathlib import Path
from gate_contract import ROOT, fingerprint, validate
config = json.loads((ROOT / 'quality/gates.json').read_text())
source = fingerprint()
report = {
    'phase': config['phase'], 'fingerprint': source, 'context_manifest': config['context_manifest'],
    'started_at': datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'purpose': 'Preserve customer consent → conservative order → mock payment → 48-hour pickup while refusing invalid evidence.',
    'normal_case': 'Valid bootstrap reports pass; actual product journey remains not_run.',
    'adjacent_regressions': ['OpenAI configuration parsing', 'Next production build', 'source freshness and child coverage'],
    'checks': [],
}
output_dir = ROOT / 'artifacts/raw'
output_dir.mkdir(parents=True, exist_ok=True)
for check in config['checks']:
    counts_file = output_dir / 'python-tests.json'
    if check.get('tests'):
        counts_file.unlink(missing_ok=True)
    process = subprocess.run(check['command'], cwd=ROOT, text=True)
    result = {'id': check['id'], 'fingerprint': source, 'exit_code': process.returncode, 'status': 'PASS' if process.returncode == 0 else 'FAIL', 'mode': 'local'}
    if check.get('tests') and counts_file.exists():
        result.update(json.loads(counts_file.read_text()))
    report['checks'].append(result)
    if process.returncode:
        break
reviews = [json.loads(p.read_text()) for p in (ROOT / 'quality/reviews').glob('*.json')]
errors = validate(config, report, reviews, fingerprint())
report.update({'errors': errors, 'status': 'FAIL' if errors else 'PASS'})
(output_dir / 'gate-report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({'phase': config['phase'], 'status': report['status'], 'fingerprint': source, 'errors': errors}, ensure_ascii=False))
sys.exit(bool(errors))
