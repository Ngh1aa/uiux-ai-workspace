from __future__ import annotations

from core.actions.evaluate_visual_quality_v3 import EvaluateVisualQualityV3
from core.contracts.visual_critic_schema import SemanticVisualReview, VisualIssue, VisualScore
from core.semantic_visual_policy import merge_semantic_score, semantic_issues


class EvaluateVisualQualitySemantic(EvaluateVisualQualityV3):
    """Runtime adapter that binds VisualCritic v3 to the independently tested policy."""

    name: str = "EvaluateVisualQualitySemantic"

    @staticmethod
    def _semantic_issues(review: SemanticVisualReview) -> list[VisualIssue]:
        return semantic_issues(review)

    @classmethod
    def _merge_semantic_score(
        cls,
        base: VisualScore,
        review: SemanticVisualReview,
        issues: list[VisualIssue],
    ) -> VisualScore:
        return merge_semantic_score(base, review, issues)
