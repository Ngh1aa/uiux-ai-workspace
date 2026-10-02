from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.benchmarks.knowledge_value_trial import evaluate_knowledge_value_trial


BENCHMARKS = ROOT / "benchmarks"


def _evaluate(version: int):
    return evaluate_knowledge_value_trial(
        trial_path=BENCHMARKS / f"knowledge-value-trial-v{version}.json",
        mapping_path=BENCHMARKS / f"knowledge-value-trial-mapping-v{version}.json",
        reviews_path=BENCHMARKS / f"knowledge-value-human-reviews-v{version}.json",
    )


def main() -> int:
    historical = _evaluate(1)
    if historical.case_count != 3:
        raise SystemExit("A50.5 round one must contain exactly three representative project cases")
    if historical.human_review_complete is not True or historical.reviewed_case_count != 3:
        raise SystemExit("A50.5 round-one human review must remain complete")
    if historical.expansion_recommendation != "REVISE_BEFORE_EXPANSION":
        raise SystemExit("A50.5 round-one governance history must remain REVISE_BEFORE_EXPANSION")
    if (
        historical.knowledge_preferred_count != 2
        or historical.baseline_preferred_count != 0
        or historical.tie_count != 1
        or historical.material_regression_count != 0
    ):
        raise SystemExit("A50.5 round-one human-review counts drifted")

    revision = _evaluate(2)
    if revision.case_count != 3:
        raise SystemExit("A50.5R round two must contain exactly three representative project cases")
    if revision.human_review_complete is not True or revision.reviewed_case_count != 3:
        raise SystemExit("A50.5R round-two human review must remain complete")
    if revision.expansion_recommendation != "CONSIDER_EXPANSION":
        raise SystemExit("A50.5R completed round-two review must derive CONSIDER_EXPANSION")
    if (
        revision.knowledge_preferred_count != 3
        or revision.baseline_preferred_count != 0
        or revision.tie_count != 0
        or revision.material_regression_count != 0
    ):
        raise SystemExit("A50.5R round-two human-review counts drifted")
    if revision.joint_usefulness_win_count != 3:
        raise SystemExit("A50.5R round two must preserve three specificity+decision-usefulness wins")

    for result in (historical, revision):
        if result.expand_allowed is not False or result.auto_mutation_allowed is not False:
            raise SystemExit("knowledge value trials must not directly allow corpus expansion or mutation")
        if result.current_run_evidence is not False or result.product_evidence is not False:
            raise SystemExit("knowledge value trial samples are not runtime/product evidence")

    print(
        "knowledge value trials PASSED: "
        f"v1={historical.expansion_recommendation} reviewed={historical.reviewed_case_count}/3; "
        f"v2={revision.expansion_recommendation} reviewed={revision.reviewed_case_count}/3 "
        f"knowledge_preferred={revision.knowledge_preferred_count}/3 "
        f"joint_usefulness_wins={revision.joint_usefulness_win_count}/3; "
        "expand_allowed=false auto_mutation_allowed=false"
    )
    print("scope=versioned_model_assisted_blind_pair_trials_not_product_evidence")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
