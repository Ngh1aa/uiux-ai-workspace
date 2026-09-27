from __future__ import annotations

import json

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
                "Use `skills_UIUX/prompt-compiler/profiles/pixel-faithful.md`. "
                "Reference evidence dominates; creativity is constrained. Preserve exact values "
                "only when evidence proves them and keep perceptual choreography separate from code mechanics."
            ),
            "preserve_and_extend": (
                "Use `skills_UIUX/prompt-compiler/profiles/preserve-and-extend.md`. "
                "Classify preservation strength per owner, isolate extension boundaries, and allow "
                "VERIFIED preserved behavior to coexist with PROPOSED new design decisions."
            ),
            "redesign": (
                "Use `skills_UIUX/prompt-compiler/profiles/redesign.md`. Preserve product/data/journey "
                "truth where required; do not protect incidental DOM/CSS or visual debt merely because it exists."
            ),
            "original_design": (
                "Use `skills_UIUX/prompt-compiler/profiles/original-design.md`. New design values are "
                "PROPOSED, not ASSUMED; use research and the adaptive prototype rubric when applicable."
            ),
        }
        return contracts[profile]

    async def run(self, instruction: str) -> str:
        payload = json.loads(instruction)
        if not isinstance(payload, dict):
            raise ValueError("Spec compiler input must be a JSON object.")

        baseline_raw = await CreateSpecFirstPromptPack().run(instruction)
        pack = PromptPack.model_validate_json(baseline_raw)
        profile = infer_spec_profile(payload)
        pack.spec_profile = profile

        contract = self._profile_contract(profile)
        profile_block = (
            "## Specification profile\n\n"
            f"- Profile: `{profile}`\n"
            f"- Contract: {contract}\n"
            "- Evidence vocabulary: VERIFIED / INFERRED / ASSUMED / UNKNOWN / PROPOSED / N/A_JUSTIFIED.\n"
            "- A deliberate new design decision is PROPOSED, not ASSUMED.\n"
            "- Example projects are resolution examples only, never requirement sources.\n"
        )

        pack.project_context = f"# Spec profile\n- `{profile}`\n\n" + pack.project_context
        mission_marker = "## 0. Mission"
        pack.full_build_spec = pack.full_build_spec.replace(
            mission_marker,
            profile_block + "\n" + mission_marker,
            1,
        )
        pack.implementation_prompt = (
            f"SPEC PROFILE: `{profile}`\n{contract}\n\n" + pack.implementation_prompt
        )
        pack.qa_remediation_prompt = (
            f"SPEC PROFILE: `{profile}`\n"
            "Evaluate fidelity/change boundaries according to this profile.\n\n"
            + pack.qa_remediation_prompt
        )

        return pack.model_dump_json(indent=2)
