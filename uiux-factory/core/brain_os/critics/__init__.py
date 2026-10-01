"""Advisory Brain OS critics.

Critics may emit observations and repair inputs, but they do not own runtime gates,
evidence trust, provider execution, merge or release authority.
"""

from core.brain_os.critics.core_design import (
    VISUAL_BRAIN_OWNER,
    AccessibilityCritic,
    CoreCriticReport,
    DesignSystemCritic,
    UXIACritic,
    VisualBrainCriticAdapter,
)
from core.brain_os.critics.product_truth import (
    EVIDENCE_INTEGRITY_OWNER,
    LINEAGE_INTEGRITY_OWNER,
    RUNTIME_EVIDENCE_OWNER,
    EvidenceTruthCritic,
    ProductCritic,
    ProductTruthCriticReport,
    RuntimeCritic,
)

__all__ = [
    "EVIDENCE_INTEGRITY_OWNER",
    "LINEAGE_INTEGRITY_OWNER",
    "RUNTIME_EVIDENCE_OWNER",
    "VISUAL_BRAIN_OWNER",
    "AccessibilityCritic",
    "CoreCriticReport",
    "DesignSystemCritic",
    "EvidenceTruthCritic",
    "ProductCritic",
    "ProductTruthCriticReport",
    "RuntimeCritic",
    "UXIACritic",
    "VisualBrainCriticAdapter",
]
