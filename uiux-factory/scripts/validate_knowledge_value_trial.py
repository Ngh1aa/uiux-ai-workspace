from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.benchmarks.knowledge_value_trial import evaluate_knowledge_value_trial


BENCHMARKS = ROOT / "benchmarks"


def main() -> int:
    result = evaluate_knowledge_value_trial(
        trial_path=BENCHMARKS / "knowledge-value-trial-v1.json",
        mapping_path=BENCHMARKS / "knowledge-value-trial-mapping-v1.json",
        reviews_path=BENCHMARKS / "knowledge-value-human-reviews-v1.json",
    )

    if result.case_count != 3:
        raise SystemExit("A50.5 trial must contain exactly three representative project cases")
    if result.expansion_recommendation != "HOLD_PENDING_HUMAN":
        raise SystemExit(
            "checked-in A50.5 baseline must remain HOLD_PENDING_HUMAN until independent human reviews are committed"
        )
    if result.expand_allowed is not False or result.auto_mutation_allowed is not False:
        raise SystemExit("A50.5 must not directly allow corpus expansion or mutation")
    if result.current_run_evidence is not False or result.product_evidence is not False:
        raise SystemExit("A50.5 model-assisted samples are not runtime/product evidence")

    print(
        "knowledge value trial PASSED: "
        f"cases={result.case_count} reviewed={result.reviewed_case_count} "
        f"recommendation={result.expansion_recommendation} "
        "expand_allowed=false auto_mutation_allowed=false"
    )
    print("scope=model_assisted_blind_pair_trial_not_human_or_product_evidence")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
