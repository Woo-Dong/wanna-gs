"""Run collected Python checks and persist actual unittest counts for the gate."""
import json
import sys
import unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
if __name__ == "__main__":
    suite = unittest.TestSuite()
    collection = {}
    missing = []
    for directory in ('scripts', 'tests/gates', 'evals/tests', 'tests/eval-runner', 'tests/ux-benchmark', 'tests/ux-benchmark/v3', 'tests/release'):
        collected = unittest.TestLoader().discover(str(ROOT / directory), pattern='test_*.py')
        collection[directory] = collected.countTestCases()
        if not collection[directory]: missing.append(directory)
        suite.addTests(collected)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    output = ROOT / 'artifacts/raw/python-tests.json'
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps({'tests': result.testsRun, 'skipped': len(result.skipped), 'failures': len(result.failures), 'errors': len(result.errors) + len(missing), 'collection': collection, 'missing_suites': missing}))
    sys.exit(0 if result.wasSuccessful() and result.testsRun and not result.skipped and not missing else 1)
