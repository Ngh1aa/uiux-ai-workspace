from pathlib import Path
import re


class WorkspaceWriter:
    def __init__(self, factory_root: Path) -> None:
        self.factory_root = Path(factory_root).resolve()
        self.generated_root = (
            self.factory_root / "generated"
        ).resolve()
        self.generated_root.mkdir(
            parents=True,
            exist_ok=True,
        )

    @staticmethod
    def validate_slug(project_slug: str) -> str:
        if not re.fullmatch(
            r"[a-z0-9][a-z0-9-]{0,63}",
            project_slug,
        ):
            raise ValueError(
                "Invalid project slug. "
                "Use lowercase letters, digits and hyphens only."
            )
        return project_slug

    def project_root(self, project_slug: str) -> Path:
        slug = self.validate_slug(project_slug)
        root = (
            self.generated_root / slug
        ).resolve()

        if not root.is_relative_to(
            self.generated_root
        ):
            raise PermissionError(
                "Project root escapes generated directory."
            )

        root.mkdir(
            parents=True,
            exist_ok=True,
        )
        return root

    def safe_path(
        self,
        project_slug: str,
        relative_path: str,
    ) -> Path:
        project_root = self.project_root(
            project_slug
        )
        relative = Path(relative_path)

        if relative.is_absolute():
            raise PermissionError(
                "Absolute paths are not allowed."
            )

        target = (
            project_root / relative
        ).resolve()

        if not target.is_relative_to(
            project_root
        ):
            raise PermissionError(
                f"Path escapes project workspace: "
                f"{relative_path}"
            )

        return target

    def write_text(
        self,
        project_slug: str,
        relative_path: str,
        content: str,
    ) -> Path:
        target = self.safe_path(
            project_slug,
            relative_path,
        )
        target.parent.mkdir(
            parents=True,
            exist_ok=True,
        )
        target.write_text(
            content,
            encoding="utf-8",
        )
        return target
