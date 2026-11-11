"""Path length guard: long nested paths silently break clones on Windows."""
import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location('check_path_length', ROOT / 'scripts/check-path-length.py')
check = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(check)


class PathLengthTests(unittest.TestCase):
    def test_flags_only_paths_over_limit(self):
        paths = ['a' * 100, 'b' * 101, 'c' * 150]
        self.assertEqual(check.too_long(paths, 100), ['c' * 150, 'b' * 101])

    def test_repository_paths_within_limit(self):
        self.assertEqual(check.too_long(check.tracked_files(), check.LIMIT), [])


if __name__ == '__main__':
    unittest.main()
