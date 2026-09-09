from __future__ import annotations

from pathlib import Path

from core.manager.intelligent_manager import IntelligentDevelopmentManager
from core.orchestration.intelligent_flow import ProfessionalWebsiteFlow
from core.orchestration.reference_intelligence import ReferenceIntelligencePlanner
from core.orchestration.skill_governance import FlowReplanner, SkillGovernanceSnapshot
from core.team.intelligent_team_runner import IntelligentTeamRunner


class ProviderIntelligentDevelopmentManager(IntelligentDevelopmentManager):
    """Intelligent manager with skills_UIUX provider-managed observation loops enabled."""

    def __init__(self, root: Path):
        super().__init__(root)

        # Replace only the execution bridge; all sequencing, contracts, reference
        # intelligence and root-cause replanning continue to come from the proven
        # IntelligentDevelopmentManager implementation.
        self.team_runner = IntelligentTeamRunner(root=self.root)
        self.flow = ProfessionalWebsiteFlow(self.team_runner.skills_root)
        self.reference_planner = ReferenceIntelligencePlanner()
        self.replanner = FlowReplanner(self.flow.document)
        self.governance = SkillGovernanceSnapshot(self.team_runner.skills_root)
        self._root_replan_count = 0
