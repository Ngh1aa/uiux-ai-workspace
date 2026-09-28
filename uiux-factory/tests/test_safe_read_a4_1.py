from __future__ import annotations

from pathlib import Path

import pytest

from core.runtime.flow_os.agent import ToolRegistry, build_context_manifest
from core.runtime.flow_os.provider import load_context_documents
from core.runtime.flow_os.safe_read import SafeReadError, SafeReader


def _symlink(link: Path, target: Path) -> None:
    try:
        link.symlink_to(target, target_is_directory=target.is_dir())
    except (OSError, NotImplementedError) as exc:
        pytest.skip(f"symlink creation is unavailable in this environment: {exc}")


def test_a4_1_safe_reader_reads_bounded_utf8_and_env_template(tmp_path: Path) -> None:
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "app.ts").write_text("export const ok = true;\n", encoding="utf-8")
    (tmp_path / ".env.example").write_text("API_URL=https://example.test\n", encoding="utf-8")

    reader = SafeReader(tmp_path)
    loaded = reader.read_text("src/app.ts")
    template = reader.read_text(".env.example")

    assert loaded.relative_path == "src/app.ts"
    assert loaded.content == "export const ok = true;\n"
    assert loaded.bytes_read == len(loaded.content.encode("utf-8"))
    assert "API_URL" in template.content


def test_a4_1_safe_reader_rejects_escape_secret_internal_and_binary_paths(tmp_path: Path) -> None:
    project = tmp_path / "project"
    project.mkdir()
    outside = tmp_path / "outside.txt"
    outside.write_text("outside", encoding="utf-8")
    (project / ".env").write_text("TOKEN=secret", encoding="utf-8")
    (project / ".git").mkdir()
    (project / ".git" / "config").write_text("secret-ish", encoding="utf-8")
    (project / "node_modules").mkdir()
    (project / "node_modules" / "pkg.js").write_text("generated", encoding="utf-8")
    (project / "binary.bin").write_bytes(b"abc\x00def")
    (project / "invalid.txt").write_bytes(b"\xff\xfe")
    (project / "private.txt").write_text(
        "-----BEGIN PRIVATE KEY-----\nnot-a-real-key\n",
        encoding="utf-8",
    )

    reader = SafeReader(project)
    for raw in (
        "../outside.txt",
        ".env",
        ".git/config",
        "node_modules/pkg.js",
        "binary.bin",
        "invalid.txt",
        "private.txt",
    ):
        with pytest.raises(SafeReadError):
            reader.read_text(raw)


def test_a4_1_safe_reader_rejects_symlink_even_when_target_is_inside_root(tmp_path: Path) -> None:
    target = tmp_path / "real.txt"
    target.write_text("truth", encoding="utf-8")
    link = tmp_path / "linked.txt"
    _symlink(link, target)

    with pytest.raises(SafeReadError, match="symlink"):
        SafeReader(tmp_path).read_text("linked.txt")


def test_a4_1_safe_reader_enforces_per_file_byte_budget(tmp_path: Path) -> None:
    (tmp_path / "large.txt").write_text("0123456789", encoding="utf-8")
    reader = SafeReader(tmp_path, max_bytes=8)

    with pytest.raises(SafeReadError, match="byte limit"):
        reader.read_text("large.txt")


def test_a4_1_read_tool_and_listing_share_safe_read_policy(tmp_path: Path) -> None:
    (tmp_path / "visible.txt").write_text("visible", encoding="utf-8")
    (tmp_path / ".env.local").write_text("SECRET=x", encoding="utf-8")
    (tmp_path / ".git").mkdir()
    (tmp_path / ".git" / "config").write_text("x", encoding="utf-8")
    registry = ToolRegistry(tmp_path, tmp_path)

    read = registry.execute("read_text", {"path": "visible.txt"})
    listing = registry.execute("list_files", {"path": "."})

    assert read["content"] == "visible"
    assert read["encoding"] == "utf-8"
    assert read["bytes"] == 7
    assert "visible.txt" in listing["items"]
    assert ".env.local" not in listing["items"]
    assert ".git" not in listing["items"]
    with pytest.raises(SafeReadError):
        registry.execute("read_text", {"path": ".env.local"})


def test_a4_1_context_manifest_records_trusted_read_root_and_rejects_secret_source(tmp_path: Path) -> None:
    project = tmp_path / "project"
    library = tmp_path / "skills"
    (project / "docs").mkdir(parents=True)
    library.mkdir()
    (project / "docs" / "truth.md").write_text("# Project truth\n", encoding="utf-8")
    (project / ".env").write_text("TOKEN=secret", encoding="utf-8")

    manifest = build_context_manifest(
        project,
        library,
        explicit_sources=["docs/truth.md"],
    )
    item = next(entry for entry in manifest["items"] if entry["kind"] == "source_of_truth")

    assert item["read_root"] == str(project.resolve())
    assert item["bytes"] == len("# Project truth\n".encode("utf-8"))
    assert manifest["totals"]["bytes"] >= item["bytes"]

    with pytest.raises(SafeReadError):
        build_context_manifest(project, library, explicit_sources=[".env"])


def test_a4_1_provider_context_revalidates_root_and_supports_safe_old_checkpoint(tmp_path: Path) -> None:
    project = tmp_path / "project"
    library = tmp_path / "skills"
    project.mkdir()
    library.mkdir()
    source = project / "truth.md"
    source.write_text("truth-v1", encoding="utf-8")

    current_item = {
        "kind": "source_of_truth",
        "path": str(source),
        "read_root": str(project.resolve()),
    }
    current = load_context_documents(
        [current_item],
        {"source_of_truth"},
        allowed_roots=(project, library),
    )
    assert current[0]["content"] == "truth-v1"

    old_checkpoint_item = {
        "kind": "source_of_truth",
        "path": str(source),
    }
    migrated = load_context_documents(
        [old_checkpoint_item],
        {"source_of_truth"},
        allowed_roots=(project, library),
    )
    assert migrated[0]["content"] == "truth-v1"

    tampered = dict(current_item, read_root=str(tmp_path.resolve()))
    with pytest.raises(ValueError, match="not allowlisted"):
        load_context_documents(
            [tampered],
            {"source_of_truth"},
            allowed_roots=(project, library),
        )


def test_a4_1_provider_context_rechecks_symlink_after_manifest_time(tmp_path: Path) -> None:
    project = tmp_path / "project"
    project.mkdir()
    source = project / "truth.md"
    source.write_text("truth-before-swap", encoding="utf-8")
    outside = tmp_path / "outside.md"
    outside.write_text("outside-secret", encoding="utf-8")
    item = {
        "kind": "source_of_truth",
        "path": str(source),
        "read_root": str(project.resolve()),
    }

    source.unlink()
    _symlink(source, outside)

    with pytest.raises(SafeReadError, match="symlink"):
        load_context_documents(
            [item],
            {"source_of_truth"},
            allowed_roots=(project,),
        )
