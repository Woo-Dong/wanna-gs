"""Evidence freshness/coverage checks. Signed identity is outside this local demo gate."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def fingerprint(root: Path = ROOT) -> str:
    config = json.loads((root / 'quality/gates.json').read_text())
    paths = set()
    for pattern in config['source_patterns']:
        paths.update(p for p in root.glob(pattern) if p.is_file() and not any(x in p.parts for x in ('__pycache__', 'node_modules', '.next')))
    digest = hashlib.sha256()
    for p in sorted(paths):
        digest.update(p.relative_to(root).as_posix().encode() + b'\0' + p.read_bytes() + b'\0')
    return digest.hexdigest()


def validate(config: dict, report: dict, reviews: list[dict], current: str) -> list[str]:
    errors = []
    if report.get('fingerprint') != current:
        errors.append('execution source fingerprint is stale')
    if report.get('phase') != config['phase']:
        errors.append('execution phase mismatch')
    for field in ('purpose', 'normal_case', 'adjacent_regressions'):
        value = report.get(field)
        if not ((isinstance(value, str) and value.strip()) or (field == 'adjacent_regressions' and isinstance(value, list) and value and all(isinstance(x, str) and x.strip() for x in value))):
            errors.append('missing purpose preservation: ' + field)
    expected_context = config.get('context_manifest')
    if expected_context and report.get('context_manifest') != expected_context:
        errors.append('execution context mismatch')
    results = {r['id']: r for r in report.get('checks', []) if 'id' in r}
    if len(results) != len(report.get('checks', [])):
        errors.append('duplicate check IDs')
    for check in config['checks']:
        result = results.get(check['id'])
        if result is None:
            errors.append('missing required check: ' + check['id'])
            continue
        if result.get('status') != 'PASS' or result.get('exit_code') != 0:
            errors.append('failed/incomplete check: ' + check['id'])
        if result.get('fingerprint') != current:
            errors.append('stale child check: ' + check['id'])
        counts_valid = all(type(result.get(k)) is int and result[k] >= 0 for k in ('tests', 'skipped', 'failures', 'errors'))
        if check.get('tests') and (not counts_valid or result['tests'] <= 0 or any(result[k] for k in ('skipped', 'failures', 'errors'))):
            errors.append('zero/skipped/failed tests: ' + check['id'])
        if check.get('live') and result.get('mode') != 'live':
            errors.append('live evidence required: ' + check['id'])
    review_by_id = {r.get('task'): r for r in reviews}
    if len(review_by_id) != len(reviews):
        errors.append('duplicate review task IDs')
    for task in config['tasks']:
        review = review_by_id.get(task['id'], {})
        if review.get('status') != 'PASS' or review.get('fingerprint') != current:
            errors.append('missing/failed/stale independent review: ' + task['id'])
        if not review.get('reviewer') or review.get('reviewer') in task['implementers']:
            errors.append('reviewer must be independent: ' + task['id'])
        if expected_context and review.get('context_manifest') != expected_context:
            errors.append('review context ACK mismatch: ' + task['id'])
        evidence = review.get('evidence')
        if not (isinstance(evidence, list) and evidence and all(isinstance(x, str) and x.strip() for x in evidence)) or review.get('purpose_preserved') is not True:
            errors.append('review evidence/purpose missing: ' + task['id'])
        if set(review.get('requirements', [])) != set(task['requirements']):
            errors.append('review coverage mismatch: ' + task['id'])
    return errors

if __name__ == '__main__':
    print(fingerprint())
