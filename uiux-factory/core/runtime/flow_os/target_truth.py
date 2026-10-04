from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from core.runtime.flow_os.task_context import GoalInterpreter


ROUTING_FIELDS = (
    "website_type",
    "domain",
    "product_archetype",
    "validation_lane",
    "mode",
    "risk",
    "features",
)

ROUTING_PRECEDENCE = ("explicit_override", "target_project_truth", "goal_inference")
ROUTING_OVERRIDE_FIELDS = frozenset((*ROUTING_FIELDS, "intent", "change_surface"))
_STABLE_TRUTH_FIELDS = {"website_type", "domain", "product_archetype"}
_LIFECYCLE_DEFAULTS = {
    "mode": "interactive-prototype",
    "risk": "standard",
    "validation_lane": "prototype",
}
_LIFECYCLE_FEATURES = {
    "user-validation",
    "outcome-measurement",
    "stakeholder-governance",
    "experimentation",
    "live-learning",
}

PROFILE_PATH = ".uiux-profile.json"
CONTEXT_PATHS = ("PROJECT-CONTEXT.md", "PROJECT_CONTEXT.md")
FALLBACK_PATHS = ("package.json", "README.md")
MAX_SOURCE_CHARS = 20000

_ALLOWED_VALIDATION_LANES = {"prototype", "evidence-led", "production-learning"}
_ALLOWED_MODES = {"visual-prototype", "interactive-prototype", "production-candidate", "production"}
_ALLOWED_RISKS = {"standard", "high", "production"}
_FEATURES = {name for name, _terms in GoalInterpreter.FEATURE_TERMS}
_WEBSITE_TYPES = {name for name, _terms in GoalInterpreter.WEBSITE_TYPES}
_DOMAINS = {name for name, _terms in GoalInterpreter.DOMAINS}
_FINANCIAL_ARCHETYPES = {name for name, _terms in GoalInterpreter.FINANCIAL_ARCHETYPES}
_ARCHETYPE_DOMAIN_REQUIREMENTS = {
    archetype: "financial-services" for archetype in _FINANCIAL_ARCHETYPES
}


class TargetTruthProbeError(RuntimeError):
    """Raised when a declared target-truth source is unsafe or structurally invalid."""


def _compact(value: object) -> str:
    return re.sub(r"\s+", " ", str(value or "")).strip()


def _scan_text(value: object) -> str:
    text = _compact(value).lower().replace("_", " ").replace("/", " ").replace("-", " ")
    return re.sub(r"\s+", " ", text).strip()


def _slug(value: object) -> str:
    text = _scan_text(value)
    return re.sub(r"[^a-z0-9]+", "-", text).strip("-")


def _is_unknown(value: object) -> bool:
    if value is None:
        return True
    if isinstance(value, (list, tuple, set)):
        return not any(not _is_unknown(item) for item in value)
    text = _compact(value)
    if not text:
        return True
    lowered = text.lower().strip()
    if lowered in {"unknown", "n/a", "na", "none", "null", "tbd", "todo", "unspecified", "...", "-"}:
        return True
    return (lowered.startswith("[") and lowered.endswith("]")) or lowered.startswith("<unknown")


def _contains(text: str, terms: tuple[str, ...]) -> bool:
    return any(term in text for term in terms)


def _required_domain_for_archetype(value: object) -> str | None:
    return _ARCHETYPE_DOMAIN_REQUIREMENTS.get(_slug(value))


def _canonical_website_type(value: object) -> str | None:
    if _is_unknown(value):
        return None
    slug = _slug(value)
    if slug in _WEBSITE_TYPES:
        return slug
    text = _scan_text(value)
    for candidate, terms in GoalInterpreter.WEBSITE_TYPES:
        if _contains(text, tuple(term.lower() for term in terms)):
            return candidate
    # Project templates often use broad type labels rather than Factory website-type names.
    aliases = {
        "web": "generic",
        "website": "generic",
        "web-app": "saas",
        "web-application": "saas",
        "application": "saas",
        "app": "saas",
    }
    resolved = aliases.get(slug)
    return None if resolved == "generic" else resolved


def _canonical_domain(value: object) -> str | None:
    if _is_unknown(value):
        return None
    slug = _slug(value)
    if slug in _DOMAINS:
        return slug
    text = _scan_text(value)
    for candidate, terms in GoalInterpreter.DOMAINS:
        if _contains(text, tuple(term.lower() for term in terms)):
            return candidate
    return None


def _canonical_product_archetype(value: object, *, domain_hint: object = None) -> str | None:
    if _is_unknown(value) and _is_unknown(domain_hint):
        return None
    combined = _scan_text(" ".join(part for part in (_compact(value), _compact(domain_hint)) if part))
    raw_slug = _slug(value) if not _is_unknown(value) else ""
    if raw_slug in _FINANCIAL_ARCHETYPES:
        return raw_slug
    for candidate, terms in GoalInterpreter.FINANCIAL_ARCHETYPES:
        if _contains(combined, tuple(term.lower() for term in terms)):
            return candidate
    # Common project-profile vocabulary can be more specific than the canonical financial archetype.
    if ("consumer" in combined or "personal" in combined) and ("bank" in combined or "banking" in combined):
        return "consumer-banking"
    if raw_slug:
        return raw_slug
    return None


def _canonical_validation_lane(value: object) -> str | None:
    if _is_unknown(value):
        return None
    slug = _slug(value)
    aliases = {
        "evidence-led": "evidence-led",
        "evidence": "evidence-led",
        "production-learning": "production-learning",
        "production": "production-learning",
        "prototype": "prototype",
    }
    resolved = aliases.get(slug)
    return resolved if resolved in _ALLOWED_VALIDATION_LANES else None


def _canonical_mode(value: object) -> str | None:
    if _is_unknown(value):
        return None
    slug = _slug(value)
    aliases = {
        "visual": "visual-prototype",
        "visual-prototype": "visual-prototype",
        "interactive": "interactive-prototype",
        "interactive-prototype": "interactive-prototype",
        "prototype": "interactive-prototype",
        "production-candidate": "production-candidate",
        "staging": "production-candidate",
        "production": "production",
    }
    resolved = aliases.get(slug)
    return resolved if resolved in _ALLOWED_MODES else None


def _canonical_risk(value: object) -> str | None:
    if _is_unknown(value):
        return None
    slug = _slug(value)
    aliases = {
        "low": "standard",
        "medium": "standard",
        "standard": "standard",
        "high": "high",
        "critical": "high",
        "production": "production",
    }
    resolved = aliases.get(slug)
    return resolved if resolved in _ALLOWED_RISKS else None


def _canonical_features(value: object) -> list[str]:
    if _is_unknown(value):
        return []
    if isinstance(value, (list, tuple, set)):
        raw_values = list(value)
    else:
        raw_values = re.split(r"[,;|\n]+", str(value))
    output: list[str] = []
    for raw in raw_values:
        slug = _slug(raw)
        if slug in _FEATURES and slug not in output:
            output.append(slug)
    return output


def _normalize_field(field_name: str, value: object, *, raw_doc: dict[str, Any] | None = None) -> object | None:
    if field_name == "website_type":
        return _canonical_website_type(value)
    if field_name == "domain":
        return _canonical_domain(value)
    if field_name == "product_archetype":
        domain_hint = (raw_doc or {}).get("domain")
        return _canonical_product_archetype(value, domain_hint=domain_hint)
    if field_name == "validation_lane":
        return _canonical_validation_lane(value)
    if field_name == "mode":
        return _canonical_mode(value)
    if field_name == "risk":
        return _canonical_risk(value)
    if field_name == "features":
        features = _canonical_features(value)
        return features or None
    return None


@dataclass(frozen=True)
class TargetTruthReport:
    status: str
    target_root: str | None
    fields: dict[str, Any] = field(default_factory=dict)
    provenance: dict[str, dict[str, Any]] = field(default_factory=dict)
    sources: list[str] = field(default_factory=list)
    diagnostics: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class TargetTruthProbe:
    """Read bounded target-project routing truth without granting any authority.

    The probe intentionally owns only routing metadata. It never reads or emits authority,
    release authorization, gate results, evidence verdicts or provider selection.
    """

    def __init__(self, target_root: Path | str | None, *, max_source_chars: int = MAX_SOURCE_CHARS) -> None:
        self.target_root = Path(target_root).resolve() if target_root is not None else None
        self.max_source_chars = int(max_source_chars)
        if self.max_source_chars <= 0:
            raise ValueError("max_source_chars must be positive")

    def _safe_path(self, relative: str) -> Path | None:
        assert self.target_root is not None
        candidate = self.target_root / relative
        if not candidate.exists():
            return None
        resolved = candidate.resolve()
        try:
            resolved.relative_to(self.target_root)
        except ValueError as exc:
            raise TargetTruthProbeError(f"target truth source escapes target root: {relative}") from exc
        if not resolved.is_file():
            return None
        return resolved

    def _read_text(
        self,
        relative: str,
        *,
        overflow: str = "truncate",
        diagnostics: list[str] | None = None,
    ) -> str | None:
        """Read at most limit+1 chars so overflow is detected without loading unbounded input.

        `truncate` is reserved for bounded unstructured sources such as README/context text.
        `error` is used by declared structured truth where truncation would corrupt syntax.
        `ignore` is used by optional structured fallback metadata such as package.json.
        """

        if overflow not in {"truncate", "error", "ignore"}:
            raise ValueError(f"unknown overflow policy: {overflow}")
        path = self._safe_path(relative)
        if path is None:
            return None
        with path.open("r", encoding="utf-8-sig", errors="strict") as handle:
            text = handle.read(self.max_source_chars + 1)
        if len(text) <= self.max_source_chars:
            return text

        if overflow == "error":
            raise TargetTruthProbeError(
                f"target truth source exceeds size limit ({self.max_source_chars} chars): {relative}"
            )
        if overflow == "ignore":
            if diagnostics is not None:
                diagnostics.append(f"ignored_oversized_fallback:{relative}")
            return None
        return text[: self.max_source_chars]

    @staticmethod
    def _record(
        fields: dict[str, Any],
        provenance: dict[str, dict[str, Any]],
        diagnostics: list[str],
        *,
        source: str,
        field_name: str,
        raw_value: object,
        raw_doc: dict[str, Any] | None = None,
    ) -> None:
        if field_name in fields or _is_unknown(raw_value):
            return
        normalized = _normalize_field(field_name, raw_value, raw_doc=raw_doc)
        if normalized is None:
            diagnostics.append(f"ignored_unrecognized:{source}:{field_name}")
            return
        fields[field_name] = normalized
        provenance[field_name] = {
            "source": source,
            "raw": raw_value,
            "normalized": normalized,
            "authority_effect": "none",
            "evidence_effect": "none",
            "release_effect": "none",
        }

    @staticmethod
    def _cohere_identity(
        fields: dict[str, Any],
        provenance: dict[str, dict[str, Any]],
        diagnostics: list[str],
    ) -> None:
        """Keep domain-bound archetypes coherent without increasing target-truth authority."""

        archetype = fields.get("product_archetype")
        required_domain = _required_domain_for_archetype(archetype)
        if required_domain is None:
            return

        archetype_provenance = provenance.get("product_archetype", {})
        current_domain = fields.get("domain")
        if current_domain in {None, "", "generic"}:
            fields["domain"] = required_domain
            provenance["domain"] = {
                "source": archetype_provenance.get("source", "derived:product_archetype"),
                "raw": archetype,
                "normalized": required_domain,
                "derived_from": "product_archetype",
                "authority_effect": "none",
                "evidence_effect": "none",
                "release_effect": "none",
            }
            if archetype_provenance.get("confidence") == "fallback_inference":
                provenance["domain"]["confidence"] = "fallback_inference"
            diagnostics.append(
                f"derived_domain_from_archetype:{archetype}:{required_domain}"
            )
            return

        if current_domain == required_domain:
            return

        if archetype_provenance.get("confidence") == "fallback_inference":
            fields.pop("product_archetype", None)
            provenance.pop("product_archetype", None)
            diagnostics.append(
                "ignored_incoherent_fallback:product_archetype:"
                f"{archetype}:requires:{required_domain}:got:{current_domain}"
            )
            return

        domain_source = provenance.get("domain", {}).get("source", "unknown")
        archetype_source = archetype_provenance.get("source", "unknown")
        raise TargetTruthProbeError(
            "incoherent target truth: product_archetype "
            f"{archetype} requires domain {required_domain}, got {current_domain} "
            f"(domain source: {domain_source}; archetype source: {archetype_source})"
        )

    def _profile(
        self,
        fields: dict[str, Any],
        provenance: dict[str, dict[str, Any]],
        diagnostics: list[str],
        sources: list[str],
    ) -> None:
        text = self._read_text(PROFILE_PATH, overflow="error")
        if text is None:
            return
        sources.append(PROFILE_PATH)
        try:
            payload = json.loads(text)
        except json.JSONDecodeError as exc:
            raise TargetTruthProbeError(f"malformed {PROFILE_PATH}: {exc.msg}") from exc
        if not isinstance(payload, dict):
            raise TargetTruthProbeError(f"{PROFILE_PATH} must contain a JSON object")

        aliases: dict[str, tuple[str, ...]] = {
            "website_type": ("website_type", "site_type", "project_type"),
            "domain": ("domain",),
            "product_archetype": ("product_archetype", "archetype"),
            "validation_lane": ("validation_lane",),
            "mode": ("mode",),
            "risk": ("risk",),
            "features": ("features",),
        }
        for field_name, keys in aliases.items():
            raw = next((payload[key] for key in keys if key in payload and not _is_unknown(payload[key])), None)
            self._record(
                fields,
                provenance,
                diagnostics,
                source=PROFILE_PATH,
                field_name=field_name,
                raw_value=raw,
                raw_doc=payload,
            )

        # A specific project profile may encode archetype semantics inside `domain` only.
        if "product_archetype" not in fields and not _is_unknown(payload.get("domain")):
            derived = _canonical_product_archetype(None, domain_hint=payload.get("domain"))
            if derived:
                fields["product_archetype"] = derived
                provenance["product_archetype"] = {
                    "source": PROFILE_PATH,
                    "raw": payload.get("domain"),
                    "normalized": derived,
                    "derived_from": "domain",
                    "authority_effect": "none",
                    "evidence_effect": "none",
                    "release_effect": "none",
                }

    def _project_context(
        self,
        fields: dict[str, Any],
        provenance: dict[str, dict[str, Any]],
        diagnostics: list[str],
        sources: list[str],
    ) -> None:
        label_map = {
            "website type": "website_type",
            "site type": "website_type",
            "project type": "website_type",
            "domain": "domain",
            "product archetype": "product_archetype",
            "validation lane": "validation_lane",
            "runtime mode": "mode",
            "mode": "mode",
            "risk": "risk",
            "features": "features",
        }
        pattern = re.compile(r"^\s*-\s*\*\*([^*]+):\*\*\s*(.*?)\s*$", re.IGNORECASE)
        for relative in CONTEXT_PATHS:
            text = self._read_text(relative, overflow="truncate")
            if text is None:
                continue
            sources.append(relative)
            for line in text.splitlines():
                match = pattern.match(line)
                if not match:
                    continue
                field_name = label_map.get(_compact(match.group(1)).lower())
                if not field_name:
                    continue
                self._record(
                    fields,
                    provenance,
                    diagnostics,
                    source=relative,
                    field_name=field_name,
                    raw_value=match.group(2),
                )

    def _fallback_metadata(
        self,
        fields: dict[str, Any],
        provenance: dict[str, dict[str, Any]],
        diagnostics: list[str],
        sources: list[str],
    ) -> None:
        fragments: list[str] = []
        package_text = self._read_text("package.json", overflow="ignore", diagnostics=diagnostics)
        if package_text is not None:
            sources.append("package.json")
            try:
                package = json.loads(package_text)
            except json.JSONDecodeError:
                diagnostics.append("ignored_malformed_fallback:package.json")
            else:
                if isinstance(package, dict):
                    fragments.extend(
                        _compact(package.get(key))
                        for key in ("name", "description", "keywords")
                        if not _is_unknown(package.get(key))
                    )

        readme = self._read_text("README.md", overflow="truncate")
        if readme is not None:
            sources.append("README.md")
            fragments.append(readme[:12000])

        combined = "\n".join(fragment for fragment in fragments if fragment).strip()
        if not combined:
            return
        inferred = GoalInterpreter().interpret(combined).to_context()
        for field_name in ("website_type", "domain", "product_archetype"):
            value = inferred.get(field_name)
            if field_name in fields or value in {None, "", "generic"}:
                continue
            fields[field_name] = value
            provenance[field_name] = {
                "source": "fallback:package.json+README.md",
                "raw": "bounded_project_metadata",
                "normalized": value,
                "confidence": "fallback_inference",
                "authority_effect": "none",
                "evidence_effect": "none",
                "release_effect": "none",
            }

    def probe(self) -> TargetTruthReport:
        if self.target_root is None:
            return TargetTruthReport(
                status="NOT_PROVIDED",
                target_root=None,
                diagnostics=["routing_uses_goal_inference_without_target_root"],
            )
        if not self.target_root.is_dir():
            raise TargetTruthProbeError(f"target root does not exist or is not a directory: {self.target_root}")

        fields: dict[str, Any] = {}
        provenance: dict[str, dict[str, Any]] = {}
        diagnostics: list[str] = []
        sources: list[str] = []

        self._profile(fields, provenance, diagnostics, sources)
        self._project_context(fields, provenance, diagnostics, sources)
        self._cohere_identity(fields, provenance, diagnostics)
        self._fallback_metadata(fields, provenance, diagnostics, sources)
        self._cohere_identity(fields, provenance, diagnostics)

        return TargetTruthReport(
            status="PROBED" if fields else "NO_USABLE_TRUTH",
            target_root=str(self.target_root),
            fields=fields,
            provenance=provenance,
            sources=list(dict.fromkeys(sources)),
            diagnostics=diagnostics,
        )


def _unique_routing_values(values: list[str]) -> list[str]:
    seen: set[str] = set()
    output: list[str] = []
    for raw in values:
        value = str(raw).strip()
        if value and value not in seen:
            seen.add(value)
            output.append(value)
    return output


def _is_fallback_truth(truth: dict[str, Any], field_name: str) -> bool:
    provenance = truth.get("provenance", {}).get(field_name, {})
    return provenance.get("confidence") == "fallback_inference"


def _apply_target_truth(
    context: dict[str, Any],
    truth: dict[str, Any],
    field_sources: dict[str, str],
    merge_diagnostics: list[str],
) -> None:
    """Merge bounded target truth without granting authority or evidence.

    Structured identity truth beats goal inference. Structured lifecycle truth acts as
    a project default and does not erase a non-default lifecycle request inferred from
    the task. README/package fallback only fills generic identity gaps. Features are
    additive unless an explicit caller override later replaces them.
    """

    initial_domain = str(context.get("domain", "generic"))
    fields = dict(truth.get("fields", {}))

    for field_name, value in fields.items():
        if field_name not in ROUTING_FIELDS:
            continue

        if _is_fallback_truth(truth, field_name):
            if field_name not in _STABLE_TRUTH_FIELDS:
                continue
            if field_name == "product_archetype":
                fallback_domain = fields.get("domain")
                final_domain = context.get("domain")
                if fallback_domain not in {None, "", "generic"} and final_domain != fallback_domain:
                    merge_diagnostics.append("fallback_not_applied:product_archetype:domain_mismatch")
                    continue
            if context.get(field_name) not in {None, "", "generic"}:
                merge_diagnostics.append(f"fallback_not_applied:{field_name}:goal_inference_is_specific")
                continue
            context[field_name] = value
            field_sources[field_name] = "target_project_truth_fallback"
            continue

        if field_name in _STABLE_TRUTH_FIELDS:
            context[field_name] = value
            field_sources[field_name] = "target_project_truth"
            continue

        if field_name == "features":
            current = [str(item) for item in context.get("features", [])]
            target_values = [str(item) for item in value]
            merged = _unique_routing_values(current + target_values)
            if merged != current:
                context[field_name] = merged
                field_sources[field_name] = (
                    "target_project_truth" if not current else "goal_inference+target_project_truth"
                )
            continue

        default_value = _LIFECYCLE_DEFAULTS.get(field_name)
        current_value = context.get(field_name)
        if current_value == value:
            continue
        if default_value is not None and current_value != default_value:
            merge_diagnostics.append(f"structured_default_not_applied:{field_name}:task_inference_is_non_default")
            continue
        context[field_name] = value
        field_sources[field_name] = "target_project_truth"

    if (
        str(context.get("domain", "generic")) != initial_domain
        and field_sources.get("product_archetype") == "goal_inference"
    ):
        context["product_archetype"] = "generic"
        field_sources["product_archetype"] = "derived_from_final_contract"
        merge_diagnostics.append("product_archetype_reset_after_domain_change")


def _cohere_final_context(
    context: dict[str, Any],
    field_sources: dict[str, str],
    explicit_fields: set[str],
    initial_context: dict[str, Any],
    derived_fields: dict[str, str],
) -> None:
    """Recompute defaults only when upstream routing changed and the task had no stronger signal."""

    initial_risk = str(initial_context.get("risk", "standard"))
    if "risk" not in explicit_fields and field_sources.get("risk") == "goal_inference" and initial_risk == "standard":
        website_type = str(context.get("website_type", "generic"))
        mode = str(context.get("mode", "interactive-prototype"))
        risk = "high" if website_type == "government" else ("production" if mode == "production" else "standard")
        if risk != context.get("risk"):
            context["risk"] = risk
            field_sources["risk"] = "derived_from_final_contract"
            derived_fields["risk"] = "website_type+mode"

    initial_lane = str(initial_context.get("validation_lane", "prototype"))
    if (
        "validation_lane" not in explicit_fields
        and field_sources.get("validation_lane") == "goal_inference"
        and initial_lane == "prototype"
    ):
        mode = str(context.get("mode", "interactive-prototype"))
        risk = str(context.get("risk", "standard"))
        features = {str(item) for item in context.get("features", [])}
        if mode in {"production", "production-candidate"}:
            lane = "production-learning"
        elif risk == "high" or _LIFECYCLE_FEATURES.intersection(features):
            lane = "evidence-led"
        else:
            lane = "prototype"
        if lane != context.get("validation_lane"):
            context["validation_lane"] = lane
            field_sources["validation_lane"] = "derived_from_final_contract"
            derived_fields["validation_lane"] = "mode+risk+features"


def build_truth_aware_context(
    goal: str,
    *,
    target_root: Path | str | None,
    overrides: dict[str, Any] | None = None,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Compile canonical routing context for every Flow OS entrypoint.

    Precedence is explicit override > bounded target-project truth > goal inference.
    Target truth never grants authority, gate evidence, provider access, or release power.
    """

    context = GoalInterpreter().interpret(goal).to_context()
    initial_context = {
        field_name: list(context[field_name]) if field_name == "features" else context.get(field_name)
        for field_name in ROUTING_FIELDS
    }
    field_sources = {field_name: "goal_inference" for field_name in ROUTING_FIELDS}
    merge_diagnostics: list[str] = []
    derived_fields: dict[str, str] = {}

    truth_report = TargetTruthProbe(target_root).probe()
    truth = truth_report.to_dict()
    _apply_target_truth(context, truth, field_sources, merge_diagnostics)

    explicit_fields: set[str] = set()
    domain_before_override = context.get("domain")
    for key, value in dict(overrides or {}).items():
        if key not in ROUTING_OVERRIDE_FIELDS or value is None or value == "":
            continue
        context[key] = value
        explicit_fields.add(key)
        if key in ROUTING_FIELDS:
            field_sources[key] = "explicit_override"

    if (
        "domain" in explicit_fields
        and "product_archetype" not in explicit_fields
        and context.get("domain") != domain_before_override
    ):
        context["product_archetype"] = "generic"
        field_sources["product_archetype"] = "derived_from_final_contract"
        derived_fields["product_archetype"] = "domain_override"

    _cohere_final_context(context, field_sources, explicit_fields, initial_context, derived_fields)

    context["target_truth"] = truth
    context["routing_provenance"] = {
        "precedence": list(ROUTING_PRECEDENCE),
        "field_sources": field_sources,
        "explicit_override_fields": sorted(explicit_fields),
        "derived_fields": derived_fields,
        "merge_diagnostics": merge_diagnostics,
        "target_truth_applied_before_flow_resolution": True,
    }
    return context, truth

