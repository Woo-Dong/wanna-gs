"""Run collected Python checks and persist actual unittest counts for the gate."""
import json
import sys
import unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
if __name__ == "__main__":
    suite = unittest.TestSuite()
    for directory in ('scripts', 'tests/gates', 'evals/tests'):
        suite.addTests(unittest.TestLoader().discover(str(ROOT / directory), pattern='test_*.py'))
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    output = ROOT / 'artifacts/raw/python-tests.json'
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps({'tests': result.testsRun, 'skipped': len(result.skipped), 'failures': len(result.failures), 'errors': len(result.errors)}))
    sys.exit(0 if result.wasSuccessful() and result.testsRun and not result.skipped else 1)
