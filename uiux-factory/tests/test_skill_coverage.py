import json
from pathlib import Path

from core.skills.compiler import SkillInstructionCompiler
from core.skills.execution_context import SkillSelection


def test_mandatory_rule_sections_are_prioritized_and_coverage_is_recorded(tmp_path: Path) -> None:
    skills_root = tmp_path / "skills"
    skill_dir = skills_root / "sample"
    skill_dir.mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text(
        """# Sample Skill
Introductory context.

## Background
This is intentionally verbose background that should not outrank policy.

## Hard Rules
- Must preserve verified project truth.
- Never invent testimonials or metrics.

## Acceptance Criteria
- Verify the rendered result before claiming success.

## Optional Notes
Decorative secondary guidance.
""",
        encoding="utf-8",
    )
    selection = SkillSelection(
        stage="visual_qa",
        domain="generic",
        goal="test",
        relative_paths=["sample/SKILL.md"],
        mandatory_paths=["sample/SKILL.md"],
        reasons={"sample/SKILL.md": "test policy"},
    )
    compiler = SkillInstructionCompiler(skills_root, max_chars_per_skill=800, max_total_chars=800)
    context = compiler.build(selection=selection, run_dir=tmp_path / "run")

    source = context.sources[0]
    assert source.mandatory is True
    assert "Hard Rules" in source.selected_sections
    assert "Acceptance Criteria" in source.selected_sections
    assert source.rule_lines
    assert source.full_source_preserved is True
    assert context.mandatory_skill_count == 1

    coverage = json.loads((tmp_path / "run" / "skill-context" / "visual_qa" / "coverage.json").read_text(encoding="utf-8"))
    assert coverage["all_full_sources_preserved"] is True
    assert coverage["mandatory_skill_count"] == 1
    assert coverage["sources"][0]["mandatory"] is True
