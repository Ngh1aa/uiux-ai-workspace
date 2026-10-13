#!/usr/bin/env python3
"""Stable local adapter for the pinned vendored UI UX Pro Max search engine."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SEARCH = ROOT / "vendor" / "ui-ux-pro-max" / "engine" / "scripts" / "search.py"


def review_boundary(design_system: dict) -> dict:
    """Expose upstream provenance; lexical retrieval is not a verified domain fit."""
    identities = design_system.get("source_identities", {})
    if not identities.get("product"):
        status = "NO_VERIFIED_PRODUCT_MATCH"
    elif design_system.get("reasoning_default") or not identities.get("reasoning"):
        status = "NO_CATEGORY_REASONING_PROFILE"
    else:
        status = "MATCHED_CANDIDATE"
    return {
        "status": status,
        "category": design_system.get("category"),
        "reasoning_default": design_system.get("reasoning_default"),
        "source_identities": identities,
        "fit_status": "UNVALIDATED",
        "adopted": False,
        "next_action": "Verify product/category and page-role fit; record ADOPT / ADAPT / REJECT in the project Design Contract. A fallback is not domain-specific knowledge.",
    }


def requested_format(arguments: list[str]) -> str:
    for index, argument in enumerate(arguments):
        if argument in {"--format", "-f"} and index + 1 < len(arguments):
            return arguments[index + 1]
        if argument.startswith("--format="):
            return argument.split("=", 1)[1]
    return "ascii"


def main() -> int:
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    if not SEARCH.exists():
        print(f"Vendored search engine not found: {SEARCH}", file=sys.stderr)
        return 2
    factory_parser = argparse.ArgumentParser(add_help=False, allow_abbrev=False)
    factory_parser.add_argument('--website-type', default='')
    factory_parser.add_argument('--project-domain', default='')
    factory_parser.add_argument('--product-archetype', default='')
    factory_parser.add_argument('--page-role', default='')
    factory_args, arguments = factory_parser.parse_known_args(sys.argv[1:])
    context_requested = any(vars(factory_args).values())
    if context_requested and not any(flag in arguments for flag in ('--design-system', '-ds')):
        factory_parser.error('structured project context requires --design-system; focused --domain queries retain their original contract')
    if any(flag in arguments for flag in ('--help', '-h')):
        print('Factory context: --website-type TYPE --project-domain DOMAIN --product-archetype TYPE --page-role ROLE (with --design-system). Numeric choices remain hypotheses, not adopted brand tokens.', flush=True)
    knowledge = None
    if context_requested and not any(flag in arguments for flag in ('--help', '-h')):
        sys.path.insert(0, str(ROOT.parent / 'uiux-factory'))
        from core.skills.design_knowledge import retrieve_design_knowledge
        try:
            knowledge = retrieve_design_knowledge(ROOT, {'website_type': factory_args.website_type, 'domain': factory_args.project_domain, 'product_archetype': factory_args.product_archetype}, factory_args.page_role)
        except ValueError as error:
            print(str(error), file=sys.stderr)
            return 2
    command = [sys.executable, "-B", str(SEARCH), *arguments]
    if not any(flag in arguments for flag in ("--design-system", "-ds")) or any(flag in arguments for flag in ("--help", "-h")):
        return subprocess.call(command, cwd=str(SEARCH.parent))

    # Generate once, including persistence. Keep the immutable vendor snapshot intact.
    wants_json = "--json" in arguments
    if not wants_json:
        command.append("--json")
    result = subprocess.run(command, cwd=str(SEARCH.parent), capture_output=True, text=True, encoding="utf-8")
    if result.stderr:
        print(result.stderr, end="", file=sys.stderr)
    if result.returncode:
        print(result.stdout, end="")
        return result.returncode
    payload = json.loads(result.stdout)
    boundary = review_boundary(payload["design_system"])
    if knowledge is not None:
        payload['factory_design_knowledge'] = knowledge
        boundary['context_fit'] = 'REQUIRES_REVIEW_AGAINST_STRUCTURED_IDENTITY'
        boundary['upstream_candidate_adopted'] = False
    payload["factory_retrieval_review"] = boundary
    if wants_json:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        return 0

    sys.path.insert(0, str(SEARCH.parent))
    from design_system import format_ascii_box, format_markdown
    # The upstream import configures UTF-8 stdout; emit our header afterward.
    print(f"FACTORY RETRIEVAL: {boundary['status']} | category={boundary['category']} | fit=UNVALIDATED")
    print("Source identities: " + json.dumps(boundary["source_identities"], ensure_ascii=False))
    print(boundary["next_action"] + "\n")
    if knowledge is not None:
        print('FACTORY PAGE-JOB KNOWLEDGE: ' + json.dumps(knowledge, ensure_ascii=False, indent=2))
        print('\nUPSTREAM LEXICAL CANDIDATE BELOW: diagnostic candidate only; compare identity before adoption.\n')
    formatter = format_markdown if requested_format(arguments) == "markdown" else format_ascii_box
    print(formatter(payload["design_system"]))
    if payload.get("persistence"):
        print("\nCandidate persistence: " + json.dumps(payload["persistence"], ensure_ascii=False))
        print("Persisted MASTER/page overrides remain subordinate to the adopted project Design Contract.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
