import unittest
from run_node_tests import counts_from_tap
class NodeCounts(unittest.TestCase):
    def test_actual_summary(self):
        self.assertEqual(counts_from_tap('# tests 9\n# fail 0\n# cancelled 0\n# skipped 0\n# todo 0\n'),dict(tests=9,failures=0,errors=0,skipped=0))
    def test_missing_or_duplicate_count_rejected(self):
        for out in ('', '# tests 9\n', '# tests 2\n# tests 9\n# fail 0\n# cancelled 0\n# skipped 0\n# todo 0\n'):
            with self.assertRaises(ValueError): counts_from_tap(out)
    def test_todo_and_cancelled_are_not_success(self):
        self.assertEqual(counts_from_tap('# tests 4\n# fail 1\n# cancelled 1\n# skipped 1\n# todo 1\n'),dict(tests=4,failures=1,errors=1,skipped=2))
