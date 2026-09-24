from dataclasses import dataclass
from pathlib import Path


@dataclass
class SkillDocument:
    path: Path
    relative_path: str
    score: int
    excerpt: str


class SkillLoader:
    def __init__(self, skills_root: Path | None = None):
        workspace_root = Path(__file__).resolve().parents[3]

        self.skills_root = (
            Path(skills_root).resolve()
            if skills_root
            else workspace_root / "skills_UIUX"
        )

    def validate(self) -> None:
        if not self.skills_root.exists():
            raise FileNotFoundError(
                f"skills_UIUX not found: {self.skills_root}"
            )

    def discover(self) -> list[Path]:
        self.validate()

        return sorted(
            path
            for path in self.skills_root.rglob("SKILL.md")
            if path.is_file()
        )

    def select(
        self,
        keywords=(
            "research",
            "reference",
            "competitor",
            "website",
            "ux",
            "ui",
            "design",
        ),
        limit: int = 6,
    ) -> list[SkillDocument]:

        scored = []

        for path in self.discover():
            try:
                content = path.read_text(
                    encoding="utf-8",
                    errors="ignore",
                )
            except OSError:
                continue

            relative = str(
                path.relative_to(self.skills_root)
            ).replace("\\", "/")

            searchable = (
                relative + "\n" + content[:6000]
            ).lower()

            score = sum(
                searchable.count(keyword.lower())
                for keyword in keywords
            )

            if score <= 0:
                continue

            scored.append(
                SkillDocument(
                    path=path,
                    relative_path=relative,
                    score=score,
                    excerpt=content[:1200].strip(),
                )
            )

        scored.sort(
            key=lambda item: (
                -item.score,
                item.relative_path,
            )
        )

        return scored[:limit]

    def stats(self) -> dict:
        files = self.discover()

        return {
            "skills_root": str(self.skills_root),
            "skill_count": len(files),
        }