from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.benchmarks.regression_corpus import BenchmarkCorpus, BenchmarkCorpusError


DEFAULT_CORPUS = ROOT / "benchmarks" / "corpus" / "uiux-product-v1.json"


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate the canonical A12 UI/UX benchmark corpus")
    parser.add_argument("--corpus", type=Path, default=DEFAULT_CORPUS)
    parser.add_argument("--manifest", type=Path, default=None)
    args = parser.parse_args()

    try:
        corpus = BenchmarkCorpus.load(args.corpus)
    except (OSError, json.JSONDecodeError, BenchmarkCorpusError) as exc:
        print(f"A12 benchmark corpus validation FAILED: {exc}")
        return 1

    manifest = corpus.manifest()
    print(
        "A12 benchmark corpus passed: "
        f"{manifest['case_count']} cases, hash={manifest['content_hash'][:16]}, version={manifest['version']}"
    )
    for case in manifest["cases"]:
        print(
            f"- {case['id']}: {case['domain']} / {case['product_archetype']} "
            f"human={case['human_review_status']} screenshots={case['screenshot_pack_status']}"
        )

    if args.manifest is not None:
        args.manifest.parent.mkdir(parents=True, exist_ok=True)
        args.manifest.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
