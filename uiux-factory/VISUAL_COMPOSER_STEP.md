# VisualComposer step

This step creates a page-specific visual composition contract before
FrontendEngineer writes or regenerates UI.

Files:
- core/contracts/visual_composition_schema.py
- core/actions/create_visual_composition.py
- core/agents/visual_composer.py
- scripts/test_visual_composer.py

Run:

python -m py_compile .\core\contracts\visual_composition_schema.py
python -m py_compile .\core\actions\create_visual_composition.py
python -m py_compile .\core\agents\visual_composer.py
python .\scripts\test_visual_composer.py
