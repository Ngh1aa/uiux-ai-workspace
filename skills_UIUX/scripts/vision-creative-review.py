from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


WORKSPACE_ROOT = Path(__file__).resolve().parents[2]
FACTORY_ROOT = WORKSPACE_ROOT / "uiux-factory"
SKILLS_ROOT = WORKSPACE_ROOT / "skills_UIUX"
if str(FACTORY_ROOT) not in sys.path:
    sys.path.insert(0, str(FACTORY_ROOT))

from core.runtime.flow_os.browser_evidence import PlaywrightBrowserEvidenceAdapter  # noqa: E402
from core.runtime.flow_os.vision_director import (  # noqa: E402
    VisionCreativeDirectorAdapter,
    configured_vision_creative_analyzer,
)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run advisory multi-screen Vision Creative Director review over trusted BrowserQA artifacts."
    )
    parser.add_argument(
        "--artifacts-dir",
        required=True,
        help="BrowserQA artifact directory; relative paths are resolved below uiux-factory/qa.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    qa_root = (FACTORY_ROOT / "qa").resolve()
    artifacts = Path(args.artifacts_dir)
    if not artifacts.is_absolute():
        artifacts = qa_root / artifacts
    policy = json.loads((SKILLS_ROOT / "runtime" / "runtime-policy.json").read_text(encoding="utf-8"))
    browser = PlaywrightBrowserEvidenceAdapter(qa_root, policy)
    records = browser.collect(artifacts, stage_id="visual_qa")
    analyzer = configured_vision_creative_analyzer(policy)
    result = VisionCreativeDirectorAdapter(artifacts, policy).review(records, analyzer)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
