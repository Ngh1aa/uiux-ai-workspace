"""Hồ sơ duyệt độc lập: chỉ chứa ảnh, brief, rubric; kết quả phải đủ vòng đọc lạnh và có bằng chứng."""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "review-packet.py"
PNG = bytes.fromhex("89504e470d0a1a0a0000000d4948445200000001000000010806000000"
                    "1f15c4890000000d49444154789c6360000002000154a24f5d0000000049454e44ae426082")


def run(*args):
    return subprocess.run([sys.executable, str(SCRIPT), *args], capture_output=True, text=True)


class ReviewPacketTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        shots = self.tmp / "shots"
        shots.mkdir()
        (shots / "home-390-light.png").write_bytes(PNG)
        (shots / "page.html").write_text("<p>code must not leak</p>")
        (self.tmp / "brief.md").write_text("# Brief\n")
        self.packet = self.tmp / "packet"
        result = run("make", "--shots", str(shots), "--brief", str(self.tmp / "brief.md"), "--size", "M", "--out", str(self.packet))
        self.assertEqual(result.returncode, 0, result.stderr)

    def good_review(self):
        tpl = json.loads((self.packet / "review.template.json").read_text())
        tpl["reviewer"] = {"id": "cold-1", "kind": "agent-heuristic", "independent": True}
        for answers in tpl["cold"].values():
            for q in answers:
                answers[q] = "trả lời"
        tpl["hard_fails"] = []
        tpl["scores"] = {str(i): 4 for i in range(1, 11)}
        tpl["observations"] = []
        return tpl

    def verify(self, review):
        (self.packet / "review.json").write_text(json.dumps(review, ensure_ascii=False))
        return run("verify", str(self.packet))

    def test_packet_contains_only_images_brief_and_rubric(self):
        names = {p.name for p in self.packet.rglob("*") if p.is_file()}
        self.assertNotIn("page.html", names)
        self.assertTrue({"brief.md", "rubric.md", "REVIEWER.md", "manifest.json", "home-390-light.png"} <= names)

    def test_complete_review_passes(self):
        result = self.verify(self.good_review())
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertIn("ĐẠT", result.stdout)

    def test_missing_cold_read_is_rejected(self):
        review = self.good_review()
        next(iter(review["cold"].values()))["Màn này để làm gì?"] = ""
        self.assertEqual(self.verify(review).returncode, 1)

    def test_low_score_needs_an_observation_with_fix(self):
        review = self.good_review()
        review["scores"]["2"] = 3
        self.assertEqual(self.verify(review).returncode, 1)
        review["observations"] = [{"dimension": "2", "image": "home-390-light.png", "element": "tiêu đề", "fix": "tăng cỡ"}]
        self.assertEqual(self.verify(review).returncode, 0)

    def test_changed_image_is_detected(self):
        (self.packet / "images" / "home-390-light.png").write_bytes(PNG + b"x")
        self.assertEqual(self.verify(self.good_review()).returncode, 1)


if __name__ == "__main__":
    unittest.main()
