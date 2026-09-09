# Browser QA / Playwright

One-time dependency setup:

```powershell
cd C:\Users\LENOVO\uiux-ai-workspace\uiux-factory
.\.venv\Scripts\Activate.ps1

python -m pip install playwright
python -m playwright install chromium
```

Then:

```powershell
python -m py_compile .\core\contracts\browser_qa_schema.py
python -m py_compile .\core\actions\run_browser_qa.py
python -m py_compile .\core\agents\browser_qa_agent.py
python .\scripts\test_browser_qa.py
```

The agent:
- serves the generated root static site over localhost;
- discovers routes from index.html files;
- visits every route at 1440x1000, 768x1024, 390x844;
- captures full-page screenshots;
- records console/page errors;
- detects horizontal overflow;
- checks local static links;
- checks one <main> and one <h1> per page;
- writes browser-report.json.

skills_UIUX:
- testing-strategy
- ui-craft-and-visual-qa
- accessibility
- visual-regression-and-design-drift

This is smoke/runtime/layout QA, not WCAG certification or visual-quality judgment.
