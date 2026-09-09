# VisualCritic step

One-time dependency:

```powershell
python -m pip install pillow
```

Then:

```powershell
python -m py_compile .\core\contracts\visual_critic_schema.py
python -m py_compile .\core\actions\evaluate_visual_quality.py
python -m py_compile .\core\agents\visual_critic.py

python .\scripts\test_visual_critic.py
```

VisualCritic consumes BrowserQA screenshots and browser-report.json.

Scores:
- visual
- hierarchy
- typography
- spacing
- responsive
- brand fidelity
- accessibility
- generic AI feel
- overall

Threshold:
- overall >= 90 and no P0/P1 issue => pass
- otherwise => repair_required

Important:
VisualCritic v1 is deterministic/heuristic because the current factory has
no paid LLM/vision provider. It is suitable for regression routing and repair
triggering, but it is not equivalent to human creative-director judgment.
