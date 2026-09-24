import hashlib
import json
import re

from metagpt.actions import Action

from core.contracts.schema import (
    ArtifactSource,
    DesignContract,
    EvidenceStatus,
    ImplementationConstraints,
    ProjectContract,
    UXContract,
    UXPageRole,
    VisualContract,
)


class CreateDesignContract(Action):
    name: str = "CreateDesignContract"

    desc: str = (
        "Convert research, UX/IA and art direction artifacts "
        "into a validated machine-readable Design Contract."
    )

    @staticmethod
    def sha256_text(content: str) -> str:
        return hashlib.sha256(
            content.encode("utf-8")
        ).hexdigest()

    @staticmethod
    def section(
        content: str,
        heading: str,
    ) -> str:
        marker = f"## {heading}"

        if marker not in content:
            return ""

        after = content.split(
            marker,
            1,
        )[1]

        if "\n## " in after:
            after = after.split(
                "\n## ",
                1,
            )[0]

        return after.strip()

    @staticmethod
    def clean_bullet(
        value: str,
    ) -> str:
        value = value.strip()

        value = re.sub(
            r"^\d+\.\s*",
            "",
            value,
        )

        value = re.sub(
            r"^-\s*",
            "",
            value,
        )

        value = value.replace(
            "**",
            "",
        )

        return value.strip()

    @classmethod
    def extract_list(
        cls,
        content: str,
        heading: str,
    ) -> list[str]:
        body = cls.section(
            content,
            heading,
        )

        if not body:
            return []

        items = []

        for line in body.splitlines():
            stripped = line.strip()

            if not stripped:
                continue

            if re.match(
                r"^(-|\d+\.)\s+",
                stripped,
            ):
                cleaned = cls.clean_bullet(
                    stripped
                )

                if cleaned:
                    items.append(
                        cleaned
                    )

        return items

    @staticmethod
    def extract_backtick_value(
        content: str,
        label: str,
    ) -> str:
        pattern = (
            re.escape(label)
            + r"\s*`([^`]+)`"
        )

        match = re.search(
            pattern,
            content,
        )

        if not match:
            return "UNKNOWN"

        return match.group(1).strip()

    @classmethod
    def extract_gate(
        cls,
        content: str,
        heading: str,
    ) -> str:
        body = cls.section(
            content,
            heading,
        )

        if not body:
            return "UNKNOWN"

        match = re.search(
            r"Status:\s*`([^`]+)`",
            body,
            re.IGNORECASE,
        )

        if match:
            return match.group(1).strip()

        backtick = re.search(
            r"`([^`]+)`",
            body,
        )

        if backtick:
            return backtick.group(1).strip()

        return "UNKNOWN"

    @classmethod
    def extract_page_roles(
        cls,
        ux_ia: str,
    ) -> list[UXPageRole]:
        body = cls.section(
            ux_ia,
            "Provisional Page Roles",
        )

        if not body:
            return []

        results = []

        pattern = re.compile(
            r"^-\s+\*\*(.+?)\*\*\s+[—-]\s+(.+)$"
        )

        for line in body.splitlines():
            match = pattern.match(
                line.strip()
            )

            if not match:
                continue

            results.append(
                UXPageRole(
                    name=match.group(1).strip(),
                    role=match.group(2).strip(),
                )
            )

        return results

    @classmethod
    def extract_signature(
        cls,
        art_direction: str,
    ) -> str:
        body = cls.section(
            art_direction,
            "Visual Signature",
        )

        if not body:
            return ""

        paragraphs = []

        for line in body.splitlines():
            text = line.strip()

            if not text:
                continue

            if text.lower().startswith(
                "signature test:"
            ):
                break

            paragraphs.append(text)

        return " ".join(
            paragraphs
        ).strip()

    @classmethod
    def extract_journey(
        cls,
        ux_ia: str,
    ) -> list[str]:
        heading = (
            "Ecommerce Journey"
            if "## Ecommerce Journey" in ux_ia
            else "Critical Journey"
        )

        body = cls.section(
            ux_ia,
            heading,
        )

        if not body:
            return []

        inside_code = False
        journey = []

        for line in body.splitlines():
            text = line.strip()

            if text.startswith("```"):
                if inside_code:
                    break

                inside_code = True
                continue

            if not inside_code:
                continue

            if not text:
                continue

            if text == "↓":
                continue

            journey.append(
                text
            )

        return journey

    @classmethod
    def build_sources(
        cls,
        artifacts: dict,
    ) -> dict[str, ArtifactSource]:
        result = {}

        for name, data in artifacts.items():
            content = data.get(
                "content",
                "",
            )

            result[name] = ArtifactSource(
                path=data.get(
                    "path",
                    "",
                ),
                sha256=cls.sha256_text(
                    content
                ),
            )

        return result

    async def run(
        self,
        instruction: str,
    ) -> str:
        payload = json.loads(
            instruction
        )

        goal = payload.get(
            "goal",
            "",
        )

        artifacts = payload.get(
            "artifacts",
            {},
        )

        research = artifacts.get(
            "research",
            {},
        ).get(
            "content",
            "",
        )

        ux_ia = artifacts.get(
            "ux_ia",
            {},
        ).get(
            "content",
            "",
        )

        art_direction = artifacts.get(
            "art_direction",
            {},
        ).get(
            "content",
            "",
        )

        domain = self.extract_backtick_value(
            art_direction,
            "- Detected domain:",
        )

        if domain == "UNKNOWN":
            domain = self.extract_backtick_value(
                ux_ia,
                "- Detected domain:",
            )

        primary_color = (
            self.extract_backtick_value(
                art_direction,
                "- Requested primary color:",
            )
        )

        research_gate = self.extract_gate(
            research,
            "Evidence gate",
        )

        ux_gate = self.extract_gate(
            ux_ia,
            "UX / IA Gate",
        )

        art_gate = self.extract_gate(
            art_direction,
            "Pre-code Visual Gate",
        )

        ux_principles = self.extract_list(
            ux_ia,
            "UX Principles",
        )

        page_roles = self.extract_page_roles(
            ux_ia
        )

        journey = self.extract_journey(
            ux_ia
        )

        visual_signature = (
            self.extract_signature(
                art_direction
            )
        )

        visual_attributes = self.extract_list(
            art_direction,
            "Visual Attributes",
        )

        layout_rules = self.extract_list(
            art_direction,
            "Layout Grammar",
        )

        color_roles = self.extract_list(
            art_direction,
            "Color Role Map",
        )

        typography_rules = self.extract_list(
            art_direction,
            "Typography Direction",
        )

        media_rules = self.extract_list(
            art_direction,
            "Media / Image Direction",
        )

        motion_rules = self.extract_list(
            art_direction,
            "Motion Direction",
        )

        composition_matrix = self.extract_list(
            art_direction,
            "Page-role Composition Matrix",
        )

        unresolved = self.extract_list(
            art_direction,
            "Still blocking FINAL visual lock:",
        )

        if not unresolved:
            gate_body = self.section(
                art_direction,
                "Pre-code Visual Gate",
            )

            marker = (
                "Still blocking FINAL visual lock:"
            )

            if marker in gate_body:
                unresolved_text = gate_body.split(
                    marker,
                    1,
                )[1]

                unresolved = []

                for line in unresolved_text.splitlines():
                    line = line.strip()

                    if line.startswith("- "):
                        unresolved.append(
                            line[2:].strip()
                        )

        evidence_level = "provisional"

        contract = DesignContract(
            status="provisional",
            project=ProjectContract(
                goal=goal,
                domain=domain,
                requested_primary_color=primary_color,
                evidence_level=evidence_level,
            ),
            ux=UXContract(
                principles=ux_principles,
                page_roles=page_roles,
                primary_journey=journey,
                assumptions=[
                    "Audience is not yet externally validated.",
                    "Top tasks are provisional.",
                    "External reference research is pending.",
                ],
            ),
            visual=VisualContract(
                signature=visual_signature,
                attributes=visual_attributes,
                layout_rules=layout_rules,
                color_roles=color_roles,
                typography_rules=typography_rules,
                media_rules=media_rules,
                motion_rules=motion_rules,
                composition_matrix=composition_matrix,
            ),
            constraints=ImplementationConstraints(
                preserve_page_role_diversity=True,
                avoid_generic_card_grid=True,
                avoid_shared_hero_everywhere=True,
                mobile_requires_explicit_transformation=True,
                do_not_invent_evidence=True,
                unresolved_items=unresolved,
            ),
            gates=EvidenceStatus(
                research=research_gate,
                ux_ia=ux_gate,
                art_direction=art_gate,
            ),
            sources=self.build_sources(
                artifacts
            ),
        )

        return contract.model_dump_json(
            indent=2
        )