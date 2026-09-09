from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
import re


@dataclass
class SkillPolicy:
    name: str
    relative_path: str
    sha256: str
    excerpt: str
    rule_lines: list[str]


class SkillPolicyResolver:
    FRONTEND_REQUIRED = [
        "frontend-implementation/SKILL.md",
        "ai-agent-coding-guardrails/SKILL.md",
        "design-system-and-components/SKILL.md",
        "responsive-and-device-strategy/SKILL.md",
        "accessibility/SKILL.md",
        "ecommerce-website/SKILL.md",
        "ui-craft-and-visual-qa/SKILL.md",
        "visual-taste-calibration/SKILL.md",
    ]

    RULE_HEADINGS = {
        "coding rules",
        "decision rules",
        "hard rules",
        "acceptance criteria",
        "anti-patterns",
        "ui/system guardrails",
        "catalogue ux",
        "search",
        "product detail page",
        "cart/checkout",
    }

    def __init__(
        self,
        skills_root: Path | None = None,
    ) -> None:
        workspace_root = Path(
            __file__
        ).resolve().parents[3]

        self.skills_root = (
            Path(skills_root).resolve()
            if skills_root
            else workspace_root / "skills_UIUX"
        )

    def validate_root(self) -> None:
        if not self.skills_root.exists():
            raise FileNotFoundError(
                "skills_UIUX clone is required but was not found: "
                f"{self.skills_root}"
            )

    @staticmethod
    def skill_name(
        content: str,
        fallback: str,
    ) -> str:
        match = re.search(
            r"^name:\s*(.+?)\s*$",
            content,
            flags=re.MULTILINE,
        )

        if match:
            return match.group(1).strip()

        return fallback

    @classmethod
    def extract_rule_lines(
        cls,
        content: str,
    ) -> list[str]:
        rules = []
        active = False

        for line in content.splitlines():
            stripped = line.strip()

            if stripped.startswith("## "):
                heading = stripped[3:].strip().lower()
                active = heading in cls.RULE_HEADINGS
                continue

            if stripped.startswith("# "):
                active = False
                continue

            if not active:
                continue

            if stripped.startswith("- "):
                cleaned = stripped[2:].strip()

                if cleaned:
                    rules.append(cleaned)

        return rules[:80]

    def load(
        self,
        relative_path: str,
    ) -> SkillPolicy:
        self.validate_root()

        path = (
            self.skills_root
            / relative_path
        ).resolve()

        if not path.is_relative_to(
            self.skills_root.resolve()
        ):
            raise PermissionError(
                "Skill path escapes skills_UIUX."
            )

        if not path.exists():
            raise FileNotFoundError(
                f"Required UIUX skill missing: {path}"
            )

        content = path.read_text(
            encoding="utf-8",
            errors="ignore",
        )

        return SkillPolicy(
            name=self.skill_name(
                content,
                path.parent.name,
            ),
            relative_path=relative_path,
            sha256=sha256(
                content.encode("utf-8")
            ).hexdigest(),
            excerpt=content[:1800].strip(),
            rule_lines=self.extract_rule_lines(
                content
            ),
        )

    def load_frontend_required(
        self,
    ) -> list[SkillPolicy]:
        return [
            self.load(relative_path)
            for relative_path
            in self.FRONTEND_REQUIRED
        ]
