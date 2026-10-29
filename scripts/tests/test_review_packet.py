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

    def test_changed_brief_and_rubric_are_detected(self):
        for name in ("brief.md", "rubric.md"):
            with self.subTest(name=name):
                file = self.packet / name
                original = file.read_bytes()
                file.write_bytes(original + b"changed")
                self.assertEqual(self.verify(self.good_review()).returncode, 1)
                file.write_bytes(original)

    def test_empty_images_and_boolean_scores_rejected(self):
        review = self.good_review()
        review["scores"]["1"] = True
        self.assertEqual(self.verify(review).returncode, 1)
        manifest = json.loads((self.packet / "manifest.json").read_text())
        manifest["images"] = {}
        (self.packet / "manifest.json").write_text(json.dumps(manifest))
        self.assertEqual(self.verify(self.good_review()).returncode, 1)


    def test_same_basename_in_nested_folders_is_kept(self):
        shots = self.tmp / "nested"
        for d in ("a", "b", "c"):
            (shots / d / "common").mkdir(parents=True)
            (shots / d / "common" / "home.png").write_bytes(PNG + d.encode())
        out = self.tmp / "nested-packet"
        result = run("make", "--shots", str(shots), "--brief", str(self.tmp / "brief.md"), "--out", str(out))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(len(list((out / "images").iterdir())), 3)
        self.assertEqual(len(json.loads((out / "manifest.json").read_text())["images"]), 3)

    def test_force_removes_previous_review(self):
        (self.packet / "review.json").write_text("{}")
        result = run("make", "--shots", str(self.tmp / "shots"), "--brief", str(self.tmp / "brief.md"), "--out", str(self.packet), "--force")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse((self.packet / "review.json").exists())

    def test_force_refuses_non_packet_folder(self):
        other = self.tmp / "other"
        other.mkdir()
        (other / "keep.txt").write_text("x")
        result = run("make", "--shots", str(self.tmp / "shots"), "--brief", str(self.tmp / "brief.md"), "--out", str(other), "--force")
        self.assertNotEqual(result.returncode, 0)
        self.assertTrue((other / "keep.txt").exists())

    def test_xl_requires_dimension_six_at_four(self):
        out = self.tmp / "xl"
        run("make", "--shots", str(self.tmp / "shots"), "--brief", str(self.tmp / "brief.md"), "--size", "XL", "--out", str(out))
        tpl = json.loads((out / "review.template.json").read_text())
        tpl["reviewer"] = {"id": "cold-1", "kind": "agent-heuristic", "independent": True}
        for answers in tpl["cold"].values():
            for q in answers:
                answers[q] = "trả lời"
        tpl["hard_fails"] = []
        tpl["scores"] = {str(i): 4.5 for i in range(1, 11)}
        tpl["scores"]["6"] = 3.5
        tpl["observations"] = [{"dimension": "6", "image": "home-390-light.png", "element": "card", "fix": "sửa"}]
        (out / "review.json").write_text(json.dumps(tpl))
        result = run("verify", str(out))
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertIn("CHƯA ĐẠT", result.stdout)


if __name__ == "__main__":
    unittest.main()
