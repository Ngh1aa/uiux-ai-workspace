from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_factory_entrypoint_keeps_visual_brain_under_creative_director_manager() -> None:
    run_py = (ROOT / "run.py").read_text(encoding="utf-8")
    creative_manager = (
        ROOT / "core" / "manager" / "creative_director_manager.py"
    ).read_text(encoding="utf-8")

    assert "CreativeDirectorDevelopmentManager" in run_py
    assert "VisualBrainDevelopmentManager" in creative_manager
    assert "class CreativeDirectorDevelopmentManager(VisualBrainDevelopmentManager)" in creative_manager
    assert "ProviderIntelligentDevelopmentManager(root=ROOT)" not in run_py
