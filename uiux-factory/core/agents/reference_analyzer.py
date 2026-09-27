from core.actions.analyze_references_with_provenance import AnalyzeReferencesWithProvenance
from core.agents.design_system_agent import DesignSystemAgent


class ReferenceAnalyzer(DesignSystemAgent):
    name: str = "Rei"
    profile: str = "ReferenceAnalyzer"
    goal: str = (
        "Extract source-attributed layout, typography, color, motion, interaction and UX evidence "
        "from real reference pages and preserve its provenance lineage."
    )
    constraints: str = (
        "Missing evidence remains unknown. Never promote competitor styles into confirmed brand tokens. "
        "Runtime motion values may be VERIFIED when measured; choreography interpretation must remain INFERRED. "
        "Interaction sampling must be non-destructive. Every deep evidence artifact must retain a content digest."
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_actions([AnalyzeReferencesWithProvenance])
