from pathlib import Path

import pytest

from core.runtime.workspace_writer import WorkspaceWriter


def test_writer_creates_file_inside_project(tmp_path: Path) -> None:
    writer = WorkspaceWriter(tmp_path)

    target = writer.write_text(
        "demo-project",
        "src/index.html",
        "<h1>Hello</h1>",
    )

    assert target == (tmp_path / "generated" / "demo-project" / "src" / "index.html").resolve()
    assert target.read_text(encoding="utf-8") == "<h1>Hello</h1>"


@pytest.mark.parametrize(
    "slug",
    ["../escape", "UPPERCASE", "bad_slug", "", "-leading"],
)
def test_writer_rejects_invalid_project_slug(tmp_path: Path, slug: str) -> None:
    writer = WorkspaceWriter(tmp_path)

    with pytest.raises(ValueError):
        writer.project_root(slug)


def test_writer_rejects_path_escape(tmp_path: Path) -> None:
    writer = WorkspaceWriter(tmp_path)

    with pytest.raises(PermissionError):
        writer.safe_path("demo-project", "../../outside.txt")
