"""Negative cases protect benchmark provenance and prevent empty or contradictory PASS records."""
import copy
import unittest
from pathlib import Path

import report


class ReportTests(unittest.TestCase):
    def setUp(self):
        self.run = Path("trial")
        self.scores = {
            "run": "trial", "repo_commit": "a" * 40, "reviewer": "agent-heuristic",
            "protocol": {
                "kind": "fresh", "parent_run": None, "author_id": "author",
                "reviewer_id": "cold-reviewer", "independent_review": True,
            },
            "briefs": {brief: {
                "size": "M", "hard_fails": [], "scores": {str(i): 4 for i in range(1, 11)},
            } for brief in report.BRIEFS},
        }
        self.checks = {"run": "trial", "briefs": {
            brief: {"status": "PASS", "errors": 0, "warnings": 0, "checker_exit_code": 0} for brief in report.BRIEFS
        }, "source": {"repo_commit": "a" * 40, "dirty": False, "checker_sha256": "b" * 64}}

    def errors(self):
        return report.validate(self.run, self.scores, self.checks)

    def test_fresh_run_with_exact_source_and_distinct_reviewer(self):
        self.assertEqual(self.errors(), [])

    def test_independent_panel_records_actual_reviewer_for_each_brief(self):
        self.scores["protocol"]["reviewer_ids"] = {b: "reviewer-" + b for b in report.BRIEFS}
        self.assertEqual(self.errors(), [])
        self.scores["protocol"]["reviewer_ids"][next(iter(report.BRIEFS))] = "author"
        self.assertTrue(self.errors())

    def test_partial_reviewer_panel_is_rejected(self):
        self.scores["protocol"]["reviewer_ids"] = {next(iter(report.BRIEFS)): "reviewer"}
        self.assertTrue(self.errors())

    def test_missing_or_non_sha_source_rejected(self):
        for value in (None, "vòng cải tiến 1", "cc0276e"):
            with self.subTest(value=value):
                self.scores["repo_commit"] = value
                self.assertTrue(self.errors())

    def test_legacy_unknown_source_is_explicit(self):
        self.scores["repo_commit"] = None
        self.scores["protocol"].update(kind="iterative-repair", parent_run="previous", legacy_note="SHA not recorded")
        self.checks.pop("source")
        self.assertEqual(self.errors(), [])

    def test_self_review_cannot_claim_independence(self):
        self.scores["protocol"]["reviewer_id"] = "author"
        self.assertTrue(self.errors())

    def test_fresh_run_cannot_have_a_parent(self):
        self.scores["protocol"]["parent_run"] = "previous"
        self.assertTrue(self.errors())

    def test_repair_requires_a_parent(self):
        self.scores["protocol"]["kind"] = "iterative-repair"
        self.assertTrue(self.errors())

    def test_empty_or_partial_results_rejected(self):
        original = copy.deepcopy(self.scores["briefs"])
        self.scores["briefs"] = {}
        self.assertTrue(self.errors())
        self.scores["briefs"] = original
        self.scores["briefs"].pop(next(iter(report.BRIEFS)))
        self.assertTrue(self.errors())

    def test_brief_added_after_a_run_is_not_required_for_it(self):
        newest = max(report.BRIEFS)
        original = dict(report.BRIEF_SINCE)
        try:
            report.BRIEF_SINCE[newest] = "2099-01-01"
            self.run = Path("2026-10-24-v1")
            self.scores["run"] = self.checks["run"] = "2026-10-24-v1"
            self.scores["briefs"].pop(newest)
            self.checks["briefs"].pop(newest)
            self.assertEqual(self.errors(), [])
            report.BRIEF_SINCE[newest] = "2000-01-01"
            self.assertTrue(self.errors())
        finally:
            report.BRIEF_SINCE.clear()
            report.BRIEF_SINCE.update(original)

    def test_fresh_run_requires_checker_provenance(self):
        self.checks.pop("source")
        self.assertTrue(self.errors())

    def test_source_sha_mismatch_rejected(self):
        self.checks["source"]["repo_commit"] = "c" * 40
        self.assertTrue(self.errors())

    def test_failed_checker_cannot_be_a_pass(self):
        next(iter(self.checks["briefs"].values()))["checker_exit_code"] = 2
        self.assertTrue(self.errors())

    def test_pass_with_errors_rejected(self):
        next(iter(self.checks["briefs"].values()))["errors"] = 1
        self.assertTrue(self.errors())

    def test_invalid_score_types_rejected(self):
        entry = next(iter(self.scores["briefs"].values()))
        for value in (True, float("nan"), 6, "4"):
            with self.subTest(value=value):
                entry["scores"]["1"] = value
                self.assertTrue(self.errors())

    def test_wrong_run_identity_rejected(self):
        self.checks["run"] = "stale-run"
        self.assertTrue(self.errors())

    def test_rendered_table_labels_repair_and_self_review(self):
        brief, entry = next(iter(self.scores["briefs"].items()))
        protocol = {"kind": "iterative-repair", "independent_review": False}
        row = report.row("trial", brief, entry, self.checks["briefs"][brief], protocol)
        self.assertIn("| Sửa tiếp | Không |", row)

    def test_hard_fail_still_blocks_high_scores(self):
        brief, entry = next(iter(self.scores["briefs"].items()))
        entry["hard_fails"] = ["HF-5"]
        row = report.row("trial", brief, entry, self.checks["briefs"][brief], self.scores["protocol"])
        self.assertIn("Chưa đạt", row)


if __name__ == "__main__":
    unittest.main()
