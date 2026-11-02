"""Ảnh lưu ngoài git chỉ được chấp nhận khi hash khớp bản ghi images-archive.json."""
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


report = load('report', ROOT / 'benchmarks/report.py')
packet = load('review_packet', ROOT / 'scripts/review-packet.py')


class ArchivedImageTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.run = Path(self.tmp.name)
        (self.run / 'images-archive.json').write_text(json.dumps({'files': {'shots/a.png': 'a' * 64}}))

    def tearDown(self):
        self.tmp.cleanup()

    def test_report_accepts_only_matching_archived_hash(self):
        self.assertIsNotNone(report.checked_file(self.run, {'path': 'shots/a.png', 'sha256': 'a' * 64}))
        self.assertIsNone(report.checked_file(self.run, {'path': 'shots/a.png', 'sha256': 'b' * 64}))
        self.assertIsNone(report.checked_file(self.run, {'path': 'shots/b.png', 'sha256': 'a' * 64}))
        self.assertIsNone(report.checked_file(self.run, {'path': 'a.json', 'sha256': 'a' * 64}))

    def test_packet_accepts_only_matching_archived_hash(self):
        self.assertTrue(packet.archived(self.run / 'shots/a.png', 'a' * 64))
        self.assertFalse(packet.archived(self.run / 'shots/a.png', 'b' * 64))

    def test_policy_only_latest_run_keeps_images(self):
        archive = load('archive', ROOT / 'benchmarks/archive.py')
        self.assertEqual(archive.policy(None), 0)


if __name__ == '__main__':
    unittest.main()
