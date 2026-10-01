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

__all__ = [
    "VISUAL_BRAIN_OWNER",
    "AccessibilityCritic",
    "CoreCriticReport",
    "DesignSystemCritic",
    "UXIACritic",
    "VisualBrainCriticAdapter",
]
