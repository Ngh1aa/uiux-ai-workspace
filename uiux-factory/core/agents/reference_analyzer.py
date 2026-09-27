from core.actions.analyze_references_with_motion import AnalyzeReferencesWithMotion
from core.agents.design_system_agent import DesignSystemAgent


class ReferenceAnalyzer(DesignSystemAgent):
    name: str = "Rei"
    profile: str = "ReferenceAnalyzer"
    goal: str = (
        "Extract source-attributed layout, typography, color, motion, interaction and UX evidence "
        "from real reference pages."
    )
    constraints: str = (
        "Missing evidence remains unknown. Never promote competitor styles into confirmed brand tokens. "
        "Runtime motion values may be VERIFIED when measured; choreography interpretation must remain INFERRED. "
        "Interaction sampling must be non-destructive."
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_actions([AnalyzeReferencesWithMotion])
