from __future__ import annotations

import json
from pathlib import Path

from metagpt.actions import Action

from core.actions.create_spec_first_prompt_pack import CreateSpecFirstPromptPack
from core.contracts.prompt_pack_schema import PromptPack
from core.contracts.spec_profile import SpecProfile, infer_spec_profile


class CreateProfileAwarePromptPack(Action):
    """Wrap the universal baseline with a deterministic project-specific spec profile."""

    name: str = "CreateProfileAwarePromptPack"
    desc: str = (
        "Compile the universal spec-first baseline, classify the target into a specialized "
        "spec profile, and carry that profile into implementation and QA lineage."
    )

    @staticmethod
    def _profile_contract(profile: SpecProfile) -> str:
        contracts = {
            "pixel_faithful": (
                "Reference evidence dominates; creativity is constrained. Preserve exact values "
                "only when evidence proves them and keep perceptual choreography separate from code mechanics."
            ),
            "preserve_and_extend": (
                "Classify preservation strength per owner, isolate extension boundaries, and allow "
                "VERIFIED preserved behavior to coexist with PROPOSED new design decisions."
            ),
            "redesign": (
                "Preserve product/data/journey truth where required; do not protect incidental DOM/CSS "
                "or visual debt merely because it exists."
            ),
            "original_design": (
                "New design values are PROPOSED, not ASSUMED; use research and the adaptive prototype "
                "rubric when applicable."
            ),
        }
        return contracts[profile]

    @staticmethod
    def _profile_rules(profile: SpecProfile) -> str:
        workspace_root = Path(__file__).resolve().parents[3]
        compiler_root = workspace_root / "skills_UIUX" / "prompt-compiler"
        filename = {
            "pixel_faithful": "pixel-faithful.md",
            "preserve_and_extend": "preserve-and-extend.md",
            "redesign": "redesign.md",
            "original_design": "original-design.md",
        }[profile]
        profile_path = compiler_root / "profiles" / filename
        rules = profile_path.read_text(encoding="utf-8") if profile_path.is_file() else ""
        if profile == "original_design":
            rubric_path = compiler_root / "PROTOTYPE-QUALITY-RUBRIC.md"
            if rubric_path.is_file():
                rules += "\n\n# Adaptive prototype rubric\n\n" + rubric_path.read_text(encoding="utf-8")
        return rules

    async def run(self, instruction: str) -> str:
        payload = json.loads(instruction)
        if not isinstance(payload, dict):
            raise ValueError("Spec compiler input must be a JSON object.")

        baseline_raw = await CreateSpecFirstPromptPack().run(instruction)
        pack = PromptPack.model_validate_json(baseline_raw)
        profile = infer_spec_profile(payload)
        pack.spec_profile = profile

        contract = self._profile_contract(profile)
        active_rules = self._profile_rules(profile)
        profile_block = (
            "## Specification profile\n\n"
            f"- Profile: `{profile}`\n"
            f"- Contract: {contract}\n"
            "- Evidence vocabulary: VERIFIED / INFERRED / ASSUMED / UNKNOWN / PROPOSED / N/A_JUSTIFIED.\n"
            "- A deliberate new design decision is PROPOSED, not ASSUMED.\n"
            "- Example projects are resolution examples only, never requirement sources.\n"
            "\n### Active profile rules\n\n"
            + (active_rules or "UNKNOWN — profile rules file could not be loaded; do not invent substitute requirements.")
            + "\n"
        )

        pack.project_context = f"# Spec profile\n- `{profile}`\n\n" + pack.project_context
        mission_marker = "## 0. Mission"
        pack.full_build_spec = pack.full_build_spec.replace(
            mission_marker,
            profile_block + "\n" + mission_marker,
            1,
        )
        pack.implementation_prompt = (
            f"SPEC PROFILE: `{profile}`\n{contract}\n\n"
            "The frozen Full Build Spec contains the active profile rules. Follow that spec; do not "
            "reclassify the project during implementation.\n\n"
            + pack.implementation_prompt
        )
        pack.qa_remediation_prompt = (
            f"SPEC PROFILE: `{profile}`\n"
            "Evaluate fidelity/change boundaries according to the active rules embedded in the frozen spec.\n\n"
            + pack.qa_remediation_prompt
        )

        return pack.model_dump_json(indent=2)
