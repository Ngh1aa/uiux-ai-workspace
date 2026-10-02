#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.benchmarks.compatibility_surface_governance import (
    evaluate_compatibility_surface_governance,
)


def main() -> int:
    contract = ROOT / "benchmarks" / "compatibility-surface-governance-v1.json"
    report = evaluate_compatibility_surface_governance(contract)

    print(f"Flow 2 compatibility surface governance: decision={report.decision}")
    print(f"scope={report.scope}")
    print(f"flow1_clear={report.flow1_clear}")
    print(f"zero_internal_consumers={report.zero_internal_consumers}")
    print(f"shim_count={report.shim_count}")
    print(f"retain_indefinitely={report.retain_indefinitely_count}")
    print(f"deprecate_with_sunset={report.deprecate_with_sunset_count}")
    print(f"open_removal_governance={report.open_removal_governance_count}")
    print(f"public_notice_clear={report.public_notice_clear}")
    print(f"canonical_public_guidance_only={report.canonical_public_guidance_only}")
    print(f"external_usage_status={report.external_usage_status}")
    print(f"public_code_search_hits={report.public_code_search_hits}")
    print(f"zero_search_hits_prove_zero_external_users={report.zero_search_hits_prove_zero_external_users}")
    print(f"observation_window_days={report.observation_window_days}")
    print(f"earliest_removal_review_date={report.earliest_removal_review_date}")
    print(f"observation_window_elapsed={report.observation_window_elapsed}")
    print(f"external_usage_audit_complete={report.external_usage_audit_complete}")
    print(f"no_known_supported_downstream_dependency={report.no_known_supported_downstream_dependency}")
    print(f"explicit_owner_removal_task={report.explicit_owner_removal_task}")
    print(f"removal_requirements_clear={report.removal_requirements_clear}")
    print(f"removal_governance_open={report.removal_governance_open}")
    print(f"shim_deletion_allowed={report.shim_deletion_allowed}")
    print(f"external_removal_safety_inferred={report.external_removal_safety_inferred}")
    print(f"governance_boundary_clear={report.governance_boundary_clear}")

    expected = "DEPRECATE_WITH_SUNSET_REMOVAL_GOVERNANCE_CLOSED"
    ok = all(
        (
            report.decision == expected,
            report.flow1_clear,
            report.zero_internal_consumers,
            report.shim_count == 8,
            report.retain_indefinitely_count == 0,
            report.deprecate_with_sunset_count == 8,
            report.open_removal_governance_count == 0,
            report.public_notice_clear,
            report.canonical_public_guidance_only,
            report.external_usage_status == "UNKNOWN",
            report.zero_search_hits_prove_zero_external_users is False,
            report.observation_window_days >= 90,
            report.observation_window_elapsed is False,
            report.external_usage_audit_complete is False,
            report.no_known_supported_downstream_dependency is False,
            report.explicit_owner_removal_task is False,
            report.removal_requirements_clear is False,
            report.removal_governance_open is False,
            report.shim_deletion_allowed is False,
            report.external_removal_safety_inferred is False,
            report.governance_boundary_clear,
            report.execution_effect == "none",
            report.authority_effect == "none",
            report.gate_effect == "none",
            report.evidence_effect == "none",
            report.release_effect == "none",
        )
    )
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
