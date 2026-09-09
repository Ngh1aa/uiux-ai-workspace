# RepairAgent + regression step

RepairAgent uses ONLY real skills present in skills_UIUX:

- ui-improvement
- ui-craft-and-visual-qa
- frontend-implementation
- ai-agent-coding-guardrails
- visual-taste-calibration
- responsive-and-device-strategy
- accessibility

Run:

```powershell
python -m py_compile .\core\contracts\repair_result_schema.py
python -m py_compile .\core\actions\apply_visual_repairs.py
python -m py_compile .\core\agents\repair_agent.py

python .\scripts\test_repair_agent.py
```

Then run final regression:

```powershell
python .\scripts\test_repair_loop.py
```

RepairAgent v1 is intentionally conservative:
- backs up all HTML before modifying;
- creates assets/factory-repair.css;
- injects the overlay into static pages;
- auto-applies only safe composition/spacing/responsive/typography/accessibility/surface repairs;
- defers brand-direction or generic-AI-feel repairs that would require richer vision/creative generation;
- always requires BrowserQA + VisualCritic regression.
