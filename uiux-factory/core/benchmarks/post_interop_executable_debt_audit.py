from __future__ import annotations

import ast
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable


class ExecutableDebtAuditError(RuntimeError):
    pass


@dataclass(frozen=True)
class ShimCheck:
    path: str
    module: str
    canonical_module: str
    clear: bool
    reasons: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ConsumerRef:
    path: str
    modules: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class PostInteropExecutableDebtAuditReport:
    schema_version: str
    decision: str
    next_package: str | None
    scope: str
    source_truth_clear: bool
    provider_default_migration_blocked: bool
    provider_live_receipt_count: int
    lifecycle_mutation_blocked: bool
    lifecycle_blockers: tuple[str, ...]
    lifecycle_interop_observation_only: bool
    genai_nist_expansion_blocked: bool
    vector_semantic_retrieval_deferred: bool
    shim_count: int
    shim_contract_clear: bool
    shim_checks: tuple[ShimCheck, ...]
    internal_consumer_file_count: int
    internal_consumer_import_count: int
    internal_consumers: tuple[ConsumerRef, ...]
    known_consumer_contract_clear: bool
    governance_boundary_clear: bool
    runtime_mutation_allowed: bool
    shim_deletion_allowed: bool
    provider_default_change_allowed: bool
    lifecycle_state_owner_change_allowed: bool
    genai_promotion_allowed: bool
    vector_search_change_allowed: bool
    product_evidence: bool
    execution_effect: str
    authority_effect: str
    gate_effect: str
    evidence_effect: str
    release_effect: str

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["shim_checks"] = [item.to_dict() for item in self.shim_checks]
        payload["internal_consumers"] = [item.to_dict() for item in self.internal_consumers]
        return payload


def _read_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ExecutableDebtAuditError(f"cannot read JSON {path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise ExecutableDebtAuditError(f"expected JSON object at {path}")
    return payload


def _runtime_module(name: str, shim_modules: set[str]) -> str | None:
    candidate = str(name).strip()
    if candidate.startswith("skills_UIUX.runtime."):
        candidate = candidate[len("skills_UIUX.") :]
    if candidate in shim_modules:
        return candidate
    return None


def _modules_from_tree(tree: ast.AST, shim_modules: set[str]) -> set[str]:
    found: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                normalized = _runtime_module(alias.name, shim_modules)
                if normalized:
                    found.add(normalized)
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            normalized = _runtime_module(module, shim_modules)
            if normalized:
                found.add(normalized)
            elif module in {"runtime", "skills_UIUX.runtime"}:
                for alias in node.names:
                    candidate = _runtime_module(f"runtime.{alias.name}", shim_modules)
                    if candidate:
                        found.add(candidate)
        elif isinstance(node, ast.Call):
            # Cover explicit importlib.import_module("runtime.x") style compatibility use.
            func = node.func
            is_import_module = (
                isinstance(func, ast.Attribute)
                and isinstance(func.value, ast.Name)
                and func.value.id == "importlib"
                and func.attr == "import_module"
            )
            if is_import_module and node.args and isinstance(node.args[0], ast.Constant):
                normalized = _runtime_module(str(node.args[0].value), shim_modules)
                if normalized:
                    found.add(normalized)
    return found


def discover_runtime_shim_consumers(
    repo_root: Path,
    scan_roots: Iterable[str],
    shim_modules: Iterable[str],
    shim_paths: Iterable[str] = (),
) -> tuple[ConsumerRef, ...]:
    repo_root = Path(repo_root).resolve()
    module_set = set(shim_modules)
    excluded = {str(item).replace("\\", "/") for item in shim_paths}
    consumers: list[ConsumerRef] = []

    for raw_root in scan_roots:
        root = (repo_root / raw_root).resolve()
        if not root.exists():
            raise ExecutableDebtAuditError(f"scan root missing: {raw_root}")
        for path in sorted(root.rglob("*.py")):
            relative = path.relative_to(repo_root).as_posix()
            if relative in excluded or "__pycache__" in path.parts:
                continue
            try:
                tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
            except (OSError, SyntaxError) as exc:
                raise ExecutableDebtAuditError(f"cannot parse first-party Python source {relative}: {exc}") from exc
            modules = tuple(sorted(_modules_from_tree(tree, module_set)))
            if modules:
                consumers.append(ConsumerRef(path=relative, modules=modules))
    return tuple(consumers)


def _allowed_shim_if(node: ast.If) -> bool:
    try:
        expression = ast.unparse(node.test)
    except Exception:
        return False
    return expression in {
        "str(_FACTORY_ROOT) not in sys.path",
        "__name__ == '__main__'",
        '__name__ == "__main__"',
    }


def validate_compatibility_shim(path: Path, expected_canonical_module: str) -> tuple[bool, tuple[str, ...]]:
    reasons: list[str] = []
    try:
        source = path.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(path))
    except (OSError, SyntaxError) as exc:
        return False, (f"unreadable_or_invalid_python:{exc}",)

    doc = ast.get_docstring(tree) or ""
    if "Deprecated" not in doc:
        reasons.append("missing_deprecated_marker")

    canonical_imports = [
        node.module
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and str(node.module or "").startswith("core.")
    ]
    if expected_canonical_module not in canonical_imports:
        reasons.append("missing_expected_canonical_import")
    unexpected_core = sorted({item for item in canonical_imports if item != expected_canonical_module})
    if unexpected_core:
        reasons.append("unexpected_core_import:" + ",".join(unexpected_core))

    forbidden_types = (
        ast.FunctionDef,
        ast.AsyncFunctionDef,
        ast.ClassDef,
        ast.For,
        ast.AsyncFor,
        ast.While,
        ast.Try,
        ast.With,
        ast.AsyncWith,
        ast.Match,
    )
    if any(isinstance(node, forbidden_types) for node in ast.walk(tree)):
        reasons.append("contains_independent_control_or_definition_logic")

    for node in tree.body:
        if isinstance(node, ast.Assign):
            names = [target.id for target in node.targets if isinstance(target, ast.Name)]
            if names != ["_FACTORY_ROOT"]:
                reasons.append("unexpected_top_level_assignment")
        elif isinstance(node, ast.AnnAssign):
            reasons.append("unexpected_top_level_assignment")
        elif isinstance(node, ast.If) and not _allowed_shim_if(node):
            reasons.append("unexpected_top_level_if")

    return not reasons, tuple(dict.fromkeys(reasons))


def _required_known_consumers_clear(
    required: list[dict[str, Any]],
    consumers: tuple[ConsumerRef, ...],
) -> bool:
    by_path = {item.path: set(item.modules) for item in consumers}
    for item in required:
        path = str(item.get("path", ""))
        modules = {str(value) for value in item.get("modules", [])}
        if not modules.issubset(by_path.get(path, set())):
            return False
    return True


def evaluate_post_interop_executable_debt_audit(audit_path: Path) -> PostInteropExecutableDebtAuditReport:
    audit_path = Path(audit_path).resolve()
    audit = _read_json(audit_path)
    repo_root = audit_path.parents[2]

    if audit.get("scope") != "architecture_debt_selection_only_no_runtime_mutation":
        raise ExecutableDebtAuditError("A52.3 audit scope drifted from audit-only contract")

    sources = dict(audit.get("source_contracts") or {})
    required_source_keys = {
        "provider_readiness",
        "provider_live_receipts",
        "lifecycle_mutation_readiness",
        "lifecycle_event_interop",
        "genai_freshness",
        "knowledge_canonical_state",
    }
    if set(sources) != required_source_keys:
        raise ExecutableDebtAuditError("A52.3 source-contract set drifted")

    provider_readiness = _read_json(repo_root / sources["provider_readiness"])
    provider_receipts = _read_json(repo_root / sources["provider_live_receipts"])
    lifecycle = _read_json(repo_root / sources["lifecycle_mutation_readiness"])
    interop = _read_json(repo_root / sources["lifecycle_event_interop"])
    genai = _read_json(repo_root / sources["genai_freshness"])
    knowledge = _read_json(repo_root / sources["knowledge_canonical_state"])

    debts = dict(audit.get("blocked_or_deferred_debts") or {})
    provider_expect = dict(debts.get("provider_default_migration") or {})
    receipt_list = list(provider_receipts.get("receipts") or [])
    provider_blocked = all(
        (
            provider_readiness.get("current_default_lane") == provider_expect.get("expected_default_lane"),
            provider_receipts.get("collection_status") == provider_expect.get("expected_collection_status"),
            len(receipt_list) == int(provider_expect.get("expected_live_receipt_count", -1)),
            provider_readiness.get("governance", {}).get("default_change_allowed_in_this_task") is False,
        )
    )

    lifecycle_expect = dict(debts.get("lifecycle_mutation_convergence") or {})
    expected_blockers = tuple(str(item) for item in lifecycle_expect.get("expected_blockers", []))
    actual_blockers = tuple(str(item) for item in lifecycle.get("current_semantic_blockers", []))
    lifecycle_blocked = all(
        (
            actual_blockers == expected_blockers,
            lifecycle.get("governance", {}).get("explicit_mutation_governance_opt_in") is False,
            lifecycle.get("governance", {}).get("runtime_transition_change_allowed_in_this_task") is False,
        )
    )
    interop_observation_only = interop.get("scope") == "observation_only_no_lifecycle_mutation"

    genai_expect = dict(debts.get("genai_nist_expansion") or {})
    genai_blocked = all(
        (
            genai.get("decision") == genai_expect.get("expected_decision"),
            genai.get("governance", {}).get("promotion_allowed") is False,
            genai.get("governance", {}).get("draft_creation_allowed") is False,
        )
    )

    vector_expect = dict(debts.get("vector_semantic_retrieval") or {})
    vector_deferred = (
        knowledge.get("governance", {}).get("vector_search_change_allowed")
        is vector_expect.get("expected_vector_search_change_allowed")
        is False
    )

    compatibility = dict(audit.get("compatibility_shims") or {})
    expected_shims = list(compatibility.get("expected_shims") or [])
    if len(expected_shims) != 8:
        raise ExecutableDebtAuditError("A52.3 must audit exactly the eight declared compatibility shims")

    shim_checks: list[ShimCheck] = []
    shim_modules: list[str] = []
    shim_paths: list[str] = []
    for item in expected_shims:
        relative = str(item.get("path", ""))
        module = str(item.get("module", ""))
        canonical_module = str(item.get("canonical_module", ""))
        if not relative or not module or not canonical_module:
            raise ExecutableDebtAuditError("invalid compatibility-shim declaration")
        clear, reasons = validate_compatibility_shim(repo_root / relative, canonical_module)
        shim_checks.append(
            ShimCheck(
                path=relative,
                module=module,
                canonical_module=canonical_module,
                clear=clear,
                reasons=reasons,
            )
        )
        shim_modules.append(module)
        shim_paths.append(relative)

    shim_contract_clear = all(item.clear for item in shim_checks)
    consumers = discover_runtime_shim_consumers(
        repo_root,
        [str(item) for item in compatibility.get("scan_roots", [])],
        shim_modules,
        shim_paths,
    )
    known_consumer_clear = _required_known_consumers_clear(
        list(compatibility.get("required_known_internal_consumers") or []),
        consumers,
    )

    source_truth_clear = all(
        (
            provider_blocked,
            lifecycle_blocked,
            interop_observation_only,
            genai_blocked,
            vector_deferred,
        )
    )

    selection_policy = dict(compatibility.get("selection_policy") or {})
    decision_policy = dict(audit.get("decision_policy") or {})
    if not shim_contract_clear:
        decision = str(decision_policy.get("shim_contract_regression"))
        next_package = None
    elif not source_truth_clear:
        decision = str(decision_policy.get("source_truth_drift"))
        next_package = None
    elif not known_consumer_clear:
        decision = str(decision_policy.get("consumer_census_drift"))
        next_package = None
    elif consumers:
        decision = str(selection_policy.get("internal_consumers_present"))
        next_package = "A53.1 — Runtime Compatibility Shim Retirement Readiness"
    else:
        decision = str(selection_policy.get("no_internal_consumers"))
        next_package = "A53.1 — Runtime Compatibility Shim Removal Governance"

    governance = dict(audit.get("governance") or {})
    false_keys = (
        "runtime_mutation_allowed",
        "shim_deletion_allowed",
        "provider_default_change_allowed",
        "lifecycle_state_owner_change_allowed",
        "routing_change_allowed",
        "genai_promotion_allowed",
        "vector_search_change_allowed",
        "product_evidence",
    )
    effect_keys = (
        "execution_effect",
        "authority_effect",
        "gate_effect",
        "evidence_effect",
        "release_effect",
    )
    governance_boundary_clear = all(governance.get(key) is False for key in false_keys) and all(
        governance.get(key) == "none" for key in effect_keys
    )

    return PostInteropExecutableDebtAuditReport(
        schema_version="post-interop-executable-debt-audit.v1",
        decision=decision,
        next_package=next_package,
        scope=str(audit["scope"]),
        source_truth_clear=source_truth_clear,
        provider_default_migration_blocked=provider_blocked,
        provider_live_receipt_count=len(receipt_list),
        lifecycle_mutation_blocked=lifecycle_blocked,
        lifecycle_blockers=actual_blockers,
        lifecycle_interop_observation_only=interop_observation_only,
        genai_nist_expansion_blocked=genai_blocked,
        vector_semantic_retrieval_deferred=vector_deferred,
        shim_count=len(shim_checks),
        shim_contract_clear=shim_contract_clear,
        shim_checks=tuple(shim_checks),
        internal_consumer_file_count=len(consumers),
        internal_consumer_import_count=sum(len(item.modules) for item in consumers),
        internal_consumers=consumers,
        known_consumer_contract_clear=known_consumer_clear,
        governance_boundary_clear=governance_boundary_clear,
        runtime_mutation_allowed=bool(governance.get("runtime_mutation_allowed")),
        shim_deletion_allowed=bool(governance.get("shim_deletion_allowed")),
        provider_default_change_allowed=bool(governance.get("provider_default_change_allowed")),
        lifecycle_state_owner_change_allowed=bool(governance.get("lifecycle_state_owner_change_allowed")),
        genai_promotion_allowed=bool(governance.get("genai_promotion_allowed")),
        vector_search_change_allowed=bool(governance.get("vector_search_change_allowed")),
        product_evidence=bool(governance.get("product_evidence")),
        execution_effect=str(governance.get("execution_effect")),
        authority_effect=str(governance.get("authority_effect")),
        gate_effect=str(governance.get("gate_effect")),
        evidence_effect=str(governance.get("evidence_effect")),
        release_effect=str(governance.get("release_effect")),
    )
