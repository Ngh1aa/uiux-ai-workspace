from __future__ import annotations

from pathlib import Path

from core.contracts.design_system_schema import DesignSystemContract
from core.contracts.schema import DesignContract
from core.contracts.visual_composition_schema import VisualComposition
from core.manager.provider_intelligent_manager import ProviderIntelligentDevelopmentManager
from core.orchestration.visual_brain import VisualBrain


class VisualBrainDevelopmentManager(ProviderIntelligentDevelopmentManager):
    """Provider-aware Factory manager with a skills-driven pre-code visual gate."""

    def __init__(self, root: Path):
        super().__init__(root)
        self.visual_brain = VisualBrain(self.team_runner.skills_root)

    async def _run_visual_composition(self, context) -> None:
        await super()._run_visual_composition(context)

        contract_path = self._require(context, "design_contract")
        system_path = self._require(context, "design_system")
        composition_path = self._require(context, "visual_composition")

        contract = DesignContract.model_validate_json(
            contract_path.read_text(encoding="utf-8")
        )
        system = DesignSystemContract.model_validate_json(
            system_path.read_text(encoding="utf-8")
        )
        composition = VisualComposition.model_validate_json(
            composition_path.read_text(encoding="utf-8")
        )

        report = self.visual_brain.evaluate(
            contract=contract,
            design_system=system,
            composition=composition,
        )
        report_path = self._write(
            context,
            "visual_brain",
            "visual-brain.json",
            report.model_dump_json(indent=2),
        )

        calibrated = self.visual_brain.apply_calibration(composition, report)
        composition_path.write_text(
            calibrated.model_dump_json(indent=2),
            encoding="utf-8",
        )
        context.add_artifact("visual_composition", composition_path)

        self.team_runner.event_bus(context).emit(
            "visual_brain.calibrated",
            stage="visual_composition",
            data={
                "status": report.status,
                "score": report.score.model_dump(),
                "gates": report.gates.model_dump(),
                "artifact": str(report_path),
                "generic_tells": report.generic_tells,
            },
        )

        if report.status == "blocked":
            raise RuntimeError(
                "Visual Brain blocked implementation because the composition is still materially generic. "
                f"score={report.score.overall}; artifact={report_path}"
            )
