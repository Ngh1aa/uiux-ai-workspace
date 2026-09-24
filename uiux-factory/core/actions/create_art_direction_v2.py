from __future__ import annotations

import re
from typing import ClassVar
from urllib.parse import urlparse

from core.actions.create_art_direction import CreateArtDirection


class CreateArtDirectionV2(CreateArtDirection):
    """
    Direction-aware Art Director.

    The existing deterministic action already creates a safe baseline. V2 keeps
    those rules, but it also treats the explicit direction selected in the Bolt
    workbench as a design commitment instead of silently falling back to the
    same domain template.
    """

    name: str = "CreateArtDirectionV2"

    DIRECTION_MARKER: ClassVar[str] = (
        "## SELECTED DESIGN DIRECTION"
    )

    @classmethod
    def extract_direction(
        cls,
        goal: str,
    ) -> dict[str, str]:
        if cls.DIRECTION_MARKER not in goal:
            return {}

        section = goal.split(
            cls.DIRECTION_MARKER,
            1,
        )[1]

        if "\n## " in section:
            section = section.split(
                "\n## ",
                1,
            )[0]

        result: dict[str, str] = {}

        for raw_line in section.splitlines():
            line = raw_line.strip()

            if ":" not in line:
                continue

            key, value = line.split(
                ":",
                1,
            )

            normalized = (
                key.strip()
                .lower()
                .replace(" ", "_")
            )

            value = value.strip()

            if value:
                result[normalized] = value

        return result

    @staticmethod
    def reference_urls(
        *texts: str,
    ) -> list[str]:
        urls: list[str] = []

        for text in texts:
            for url in re.findall(
                r"https?://[^\s)\]}>\"']+",
                text or "",
            ):
                cleaned = url.rstrip(
                    ".,;:"
                )

                if cleaned not in urls:
                    urls.append(cleaned)

        return urls[:12]

    @staticmethod
    def host_label(
        url: str,
    ) -> str:
        try:
            host = (
                urlparse(url)
                .netloc
                .lower()
            )

            if host.startswith("www."):
                host = host[4:]

            return host or url
        except Exception:
            return url

    @staticmethod
    def replace_between(
        content: str,
        start_marker: str,
        end_marker: str,
        replacement: str,
    ) -> str:
        start = content.find(
            start_marker
        )

        if start < 0:
            return content

        body_start = start + len(
            start_marker
        )

        end = content.find(
            end_marker,
            body_start,
        )

        if end < 0:
            return content

        return (
            content[:body_start]
            + "\n\n"
            + replacement.strip()
            + "\n\n"
            + content[end:]
        )

    @staticmethod
    def insert_before(
        content: str,
        marker: str,
        block: str,
    ) -> str:
        index = content.find(
            marker
        )

        if index < 0:
            return (
                content.rstrip()
                + "\n\n"
                + block.strip()
                + "\n"
            )

        return (
            content[:index]
            + block.strip()
            + "\n\n"
            + content[index:]
        )

    @staticmethod
    def selected_signature(
        direction: dict[str, str],
    ) -> str:
        signature = direction.get(
            "signature",
            "",
        )

        if signature:
            return signature

        name = direction.get(
            "name",
            "Selected Direction",
        )

        intent = direction.get(
            "intent",
            "",
        )

        if intent:
            return (
                f"{name}: {intent}"
            )

        return name

    @classmethod
    def commitment_block(
        cls,
        direction: dict[str, str],
    ) -> str:
        rows = [
            "## Selected Direction Commitment",
            "",
            "Status: `COMMITTED_BY_USER`",
            "",
            (
                "The workbench selected this direction before coding. "
                "It must remain visible in composition unless a usability, "
                "accessibility or evidence conflict requires a documented change."
            ),
            "",
        ]

        labels = (
            ("name", "Name"),
            ("intent", "Intent"),
            ("composition", "Composition"),
            ("typography", "Typography"),
            ("media", "Media"),
            ("avoid", "Avoid"),
            ("signature", "Signature"),
        )

        for key, label in labels:
            value = direction.get(
                key,
                "",
            )

            if value:
                rows.append(
                    f"- **{label}:** {value}"
                )

        return "\n".join(rows)

    @classmethod
    def reference_block(
        cls,
        urls: list[str],
    ) -> str:
        rows = [
            "## External Reference Evidence",
            "",
            (
                "These URLs were supplied or discovered as reference evidence. "
                "They are not templates to copy. Use them to calibrate visual "
                "quality, interaction conventions and market expectations."
            ),
            "",
        ]

        for index, url in enumerate(
            urls,
            start=1,
        ):
            rows.append(
                f"- Reference {index}: `{cls.host_label(url)}` — {url}"
            )

        return "\n".join(rows)

    @classmethod
    def layout_override_block(
        cls,
        direction: dict[str, str],
    ) -> str:
        rules: list[str] = []

        composition = direction.get(
            "composition",
            "",
        )
        typography = direction.get(
            "typography",
            "",
        )
        media = direction.get(
            "media",
            "",
        )
        avoid = direction.get(
            "avoid",
            "",
        )

        if composition:
            rules.append(
                "- Direction composition commitment: "
                + composition
            )

        if typography:
            rules.append(
                "- Direction typography commitment: "
                + typography
            )

        if media:
            rules.append(
                "- Direction media commitment: "
                + media
            )

        if avoid:
            rules.append(
                "- Direction-specific anti-patterns: "
                + avoid
            )

        return "\n".join(
            rules
        )

    async def run(
        self,
        instruction: str,
    ) -> str:
        goal, research, _ux_ia = (
            self.parse_input(
                instruction
            )
        )

        base = await super().run(
            instruction
        )

        direction = self.extract_direction(
            goal
        )

        references = self.reference_urls(
            goal,
            research,
        )

        if direction:
            signature = self.selected_signature(
                direction
            )

            base = self.replace_between(
                base,
                "## Visual Signature",
                "Signature test:",
                signature,
            )

            base = self.insert_before(
                base,
                "## Visual Attributes",
                self.commitment_block(
                    direction
                ),
            )

            override_rules = (
                self.layout_override_block(
                    direction
                )
            )

            if override_rules:
                base = self.insert_before(
                    base,
                    "## Hierarchy",
                    (
                        "### Direction-specific layout commitments\n\n"
                        + override_rules
                    ),
                )

        if references:
            base = self.insert_before(
                base,
                "## Pre-code Visual Gate",
                self.reference_block(
                    references
                ),
            )

            base = base.replace(
                "No external visual reference has been verified yet.",
                (
                    "External reference URLs are present as provisional "
                    "design-calibration evidence; their visual details are "
                    "not automatically treated as verified facts."
                ),
            )

        return base
