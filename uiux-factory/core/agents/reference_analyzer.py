from core.actions.analyze_references import AnalyzeReferences
from core.agents.design_system_agent import DesignSystemAgent


class ReferenceAnalyzer(DesignSystemAgent):
    name: str = "Rei"
    profile: str = "ReferenceAnalyzer"
    goal: str = "Extract source-attributed layout, typography, color, motion and UX evidence from real reference pages."
    constraints: str = "Missing evidence remains unknown. Never promote competitor styles into confirmed brand tokens."

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_actions([AnalyzeReferences])
