from core.actions.create_design_system_v3 import CreateDesignSystemV3
from core.agents.design_system_agent import DesignSystemAgent


class DesignSystemArchitect(DesignSystemAgent):
    profile: str = "DesignSystemArchitect"
    goal: str = "Translate supplied Brand DNA and measured references into a reusable, source-attributed design system."

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_actions([CreateDesignSystemV3])
