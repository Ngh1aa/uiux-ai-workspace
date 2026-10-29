"""Routing links cannot silently escape the repository root."""
import subprocess
import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / 'check-links.py'


class LinksTests(unittest.TestCase):
    def test_packet_snapshot_uses_verified_origin_and_still_checks_missing_target(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / 'benchmarks/briefs/01-example.md'
            source.parent.mkdir(parents=True)
            source.write_bytes(b'[route](../../WORKFLOWS.md)\n')
            target = root / 'WORKFLOWS.md'
            target.write_text('# Routing', encoding='utf8')
            packet = root / 'benchmarks/runs/trial/reviews/01'
            packet.mkdir(parents=True)
            snapshot = packet / 'brief.md'
            snapshot.write_bytes(source.read_bytes().replace(b'\n', b'\r\n'))
            (packet / 'manifest.json').write_text(json.dumps({'version':2,'inputs':{'brief.md':hashlib.sha256(snapshot.read_bytes()).hexdigest()}}))
            run = lambda: subprocess.run([sys.executable,str(SCRIPT),str(root)],capture_output=True,encoding='utf8')
            self.assertEqual(run().returncode,0)
            target.unlink()
            self.assertEqual(run().returncode,1)  # Canonical broken routes still fail.

    def test_packet_hash_cannot_exempt_a_modified_snapshot(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'brief.md').write_text('[bad](missing.md)',encoding='utf8')
            (root / 'manifest.json').write_text(json.dumps({'version':2,'inputs':{'brief.md':'a'*64}}))
            run = subprocess.run([sys.executable,str(SCRIPT),str(root)],capture_output=True,encoding='utf8')
            self.assertEqual(run.returncode,1)

    def test_missing_and_escaping_routes_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'START.md').write_text('[bad](missing.md) [escape](../outside.md)', encoding='utf8')
            run = subprocess.run([sys.executable,str(SCRIPT),str(root)], capture_output=True,encoding='utf8')
            self.assertEqual(run.returncode,1)
            self.assertIn('missing.md',run.stdout)
            self.assertIn('outside.md',run.stdout)

    def test_existing_route_and_web_links_accepted(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'START.md').write_text('[local](WORKFLOWS.md) [web](https://example.com)', encoding='utf8')
            (root / 'WORKFLOWS.md').write_text('# Workflow', encoding='utf8')
            run = subprocess.run([sys.executable,str(SCRIPT),str(root)],capture_output=True,encoding='utf8')
            self.assertEqual(run.returncode,0,run.stdout)
