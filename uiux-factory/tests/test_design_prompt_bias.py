"""Guard against global aesthetics overriding a project's static design direction."""
import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def constant(path, name):
    tree = ast.parse((ROOT / path).read_text(encoding="utf-8"))
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(isinstance(target, ast.Name) and target.id == name for target in node.targets):
            value = node.value
            if isinstance(value, ast.Call) and isinstance(value.func, ast.Attribute) and value.func.attr == "strip":
                value = value.func.value
            return ast.literal_eval(value)
    raise AssertionError(f"Missing prompt constant {name}")


def test_static_project_is_not_forced_to_animate_or_blur_navigation():
    prompt = constant("core/actions/generate_ai_frontend.py", "CODER_CONTRACT")
    assert "Include at least one CSS animation" not in prompt
    assert "Navigation should have backdrop-filter blur" not in prompt
    assert "Cards and elevated surfaces should have subtle borders + shadows" not in prompt
    assert "approved" in prompt.lower()
    assert "keyboard" in prompt.lower()
    assert "reduced-motion" in prompt.lower()


def test_universal_policy_does_not_choose_trends_before_project_truth():
    prompt = constant("core/skills/frontend_design_policy.py", "FRONTEND_DESIGN_POLICY")
    assert "Elevate visual craft with intentional modern patterns:" not in prompt
    assert "dark-mode-ready color systems" not in prompt
    assert "No aesthetic family" in prompt
    assert "evidence" in prompt


def test_art_direction_task_requires_numeric_roles_and_alternatives():
    prompt = constant("core/skills/frontend_design_policy.py", "ART_DIRECTION_TASK")
    for decision in ("type sizes", "line heights", "spacing", "density", "two", "mobile", "source"):
        assert decision in prompt


def test_design_brain_uses_canonical_tasks_without_private_trend_prompt():
    source = (ROOT / "core/orchestration/design_brain.py").read_text(encoding="utf-8")
    assert 'self.ask("art_direction", ART_DIRECTION_TASK,' in source
    assert 'self.ask("research", DESIGN_RESEARCH_TASK,' in source
    assert "premium visual effects (glassmorphism, mesh gradients, luminous accents)" not in source
