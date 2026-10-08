"""Bounded page-job knowledge, shared by CLI and agent packets. No provider calls."""
from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
from typing import Any
from core.runtime.flow_os.safe_read import SafeReader

KNOWLEDGE_PATH = "visual-design-direction/data/design-knowledge.json"
CHECKER_PATH = "skills_UIUX/visual-design-direction/scripts/check-design-decisions.py"
REFERENCE_PATH = "visual-design-direction/data/reference-anatomies.json"
COMPARISON_PATH = "skills_UIUX/visual-design-direction/scripts/evaluate-design-comparison.py"


def retrieve_design_knowledge(skills_root: Path, context: dict[str, Any], page_role: str = "") -> dict[str, Any]:
    raw = SafeReader(Path(skills_root)).read_text(KNOWLEDGE_PATH).content.encode('utf-8')
    data = json.loads(raw)
    if data.get("schema_version") != "1.0":
        raise ValueError("unsupported design knowledge version")
    role = str(page_role or "").strip().lower()
    role = data["role_aliases"].get(role, role)
    if role and role not in data["roles"]:
        raise ValueError(f"unknown page role: {role}; choose {', '.join(data['roles'])}")
    identity = {key: str(context.get(key, "")).strip().lower() for key in ("website_type", "domain", "product_archetype")}
    profiles = []
    conflicts = []
    for profile in data["domain_profiles"]:
        supplied = [key for key, value in identity.items() if value and value != "unresolved"]
        # A website label alone is too broad to infer subject matter. One semantic
        # identity is required, and every supplied identity must agree with the card.
        semantic_match = any(identity[key] in profile["match"][key] for key in ("domain", "product_archetype"))
        if not semantic_match:
            continue
        if all(identity[key] in profile["match"][key] for key in supplied):
            profiles.append({key: value for key, value in profile.items() if key != "match"})
        else:
            conflicts.append(profile["id"])
    selected = data["roles"].get(role)
    source_ids = selected["sources"] if selected else []
    reference_raw = SafeReader(Path(skills_root)).read_text(REFERENCE_PATH).content.encode('utf-8')
    reference_data = json.loads(reference_raw)
    if reference_data.get('schema_version') != '1.0':
        raise ValueError('unsupported reference anatomy version')
    profile_ids = {item['id'] for item in profiles}
    anatomy = [card for card in reference_data['cards']
               if role and card['profile_id'] in profile_ids and card['page_role'] == role]
    reference_ids = {ref for card in anatomy for ref in card['reference_ids']}
    return {
        "schema_version": data["schema_version"],
        "source": "skills_UIUX/" + KNOWLEDGE_PATH,
        "source_sha256": sha256(raw).hexdigest(),
        "identity": identity,
        "domain_status": "CONTEXT_MATCHED_CANDIDATE" if profiles else "IDENTITY_CONFLICT" if conflicts else "NO_CURATED_DOMAIN_PROFILE",
        "conflicting_profile_ids": conflicts,
        "domain_profiles": profiles,
        "page_role": role or None,
        "available_roles": list(data["roles"]),
        "role_card": selected,
        "foundations": data["foundations"],
        "sources": {key: data["sources"][key] for key in source_ids},
        "numeric_status": data["numeric_status"],
        "reference_anatomy": {
            "status": 'CONTEXT_MATCHED_CANDIDATES' if anatomy else 'ROLE_NOT_REQUESTED' if not role else 'NO_CURATED_REFERENCE_ANATOMY',
            "source": 'skills_UIUX/' + REFERENCE_PATH,
            "source_sha256": sha256(reference_raw).hexdigest(),
            "cards": anatomy,
            "sources": {key: reference_data['sources'][key] for key in sorted(reference_ids)},
            "rule": reference_data['gap_policy'],
            "adopted": False,
        },
        "adopted": False,
        "fit_status": "UNVALIDATED",
        "aesthetic_quality": "UNKNOWN",
        "rule": "Cards and ranges are candidates, not a preset or exhaustive catalog. Create another grounded composition when these examples do not fit. Choose from real content, constraints and renders; do not adopt lexical upstream matches as project truth.",
    }


def design_workflow_packet(context: dict[str, Any], skill_names: list[str] | set[str], gates: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    active = "visual-design-direction" in skill_names
    checks = [gate.get('design_phase', 'design') for gate in (gates or []) if 'design_contract_check' in gate.get('evidence_types', [])]
    required = bool(checks) or active and context.get("change_surface") in {"PAGE", "REDESIGN", "PRODUCT"}
    lookup = ['python', '-B', 'skills_UIUX/design-intelligence-retrieval/scripts/query.py', '<focused-domain-query>', '--design-system', '--json']
    for key, flag in [('website_type', '--website-type'), ('domain', '--project-domain'), ('product_archetype', '--product-archetype')]:
        if context.get(key):
            lookup.extend([flag, str(context[key])])
    lookup.extend(['--page-role', '<active-page-role>'])
    return {
        "active": active,
        "decision_contract_required": required,
        "required_check_phases": checks,
        "knowledge_source": "skills_UIUX/" + KNOWLEDGE_PATH if active else None,
        "lookup_tool": "retrieve_design_knowledge" if active else None,
        "lookup_argv_template": lookup if active else None,
        "check_tool": "check_design_decisions" if required else None,
        "checker": CHECKER_PATH if required else None,
        "contract_output": "docs/uiux/design-decisions.json" if required else None,
        "contract_version": '2.0' if required else None,
        "comparison_tool": COMPARISON_PATH if active else None,
        "comparison_protocol": {
            "hold_constant": ['audience', 'content', 'claims', 'cta', 'state', 'assets', 'viewports'],
            "vary_free_axes": ['typography', 'density', 'visual_object'],
            "evaluate": ['comprehension', 'distinctiveness'],
            "boundary": 'Material declared differences and recorded judgments are inspectable; neither proves beauty, authentic human participation or a causal Factory upgrade.',
        } if active else None,
        "sequence": ["load project truth and classify hard/suggested/free axes", "lookup identity + one page role + reference anatomy", "ADOPT/ADAPT/REJECT reference properties with reasons", "declare numeric type/density and object anatomy for alternatives", "compare distinct topologies and every free direction axis on representative pages", "predeclare comprehension/distinctiveness questions and constant inputs", "check v2 decision contract", "render/inspect representative desktop/mobile", "prepare counterbalanced review and record observations", "repair before rollout"] if active else [],
        "structural_rule": "Two representative alternatives must differ in the decision object's anatomy, region relationships or mobile grouping. Renaming anchors, skin changes or only swapping unchanged sections do not count. Rollout pages may inherit a representative decision owner." if active else None,
        "authority_effect": "none",
        "gate_effect": "none",
        "evidence_effect": "none",
        "aesthetic_quality": "UNKNOWN",
    }
