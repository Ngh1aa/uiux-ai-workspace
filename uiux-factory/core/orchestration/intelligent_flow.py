from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable

from core.orchestration.adaptive_surface import classify_change_surface


DEFAULT_DELIVERY_POLICY_ID = "adaptive-prompt-os-v4"
DEFAULT_FACTORY_DELIVERY_LANE = "full_prompt_os"
TASK_CONTRACT_VERSION = "1.0"
ANTHROPIC_SKILL_ROOT = "upstream/anthropic-skills/skills"
ANTHROPIC_FRONTEND_DESIGN = f"{ANTHROPIC_SKILL_ROOT}/frontend-design"
ANTHROPIC_WEBAPP_TESTING = f"{ANTHROPIC_SKILL_ROOT}/webapp-testing"
ANTHROPIC_SKILL_CREATOR = f"{ANTHROPIC_SKILL_ROOT}/skill-creator"
ANTHROPIC_WEB_ARTIFACTS = f"{ANTHROPIC_SKILL_ROOT}/web-artifacts-builder"
MOTION_COMPONENT_INTELLIGENCE = "motion-component-intelligence"
URL_PATTERN = re.compile(r"https?://[^\s,;)\]}>]+", re.IGNORECASE)


def _contains(text: str, terms: Iterable[str]) -> bool:
    return any(term in text for term in terms)


def _contains_non_negated(text: str, terms: Iterable[str]) -> bool:
    negative_prefix = re.compile(
        r"(?:không|đừng|do not|don't|dont|without)\s+(?:được\s+)?$",
        re.IGNORECASE,
    )
    for term in terms:
        start = 0
        while True:
            index = text.find(term, start)
            if index < 0:
                break
            prefix = text[max(0, index - 28):index]
            if not negative_prefix.search(prefix):
                return True
            start = index + max(1, len(term))
    return False


def _unique(values: Iterable[str]) -> tuple[str, ...]:
    seen: set[str] = set()
    output: list[str] = []
    for value in values:
        cleaned = re.sub(r"\s+", " ", str(value)).strip(" \t\n\r:-–—'\"")
        if cleaned and cleaned not in seen:
            seen.add(cleaned)
            output.append(cleaned)
    return tuple(output)


def _extract_fragments(text: str, patterns: Iterable[str]) -> tuple[str, ...]:
    values: list[str] = []
    for pattern in patterns:
        for match in re.finditer(pattern, text, flags=re.IGNORECASE):
            value = match.group(1).strip()
            if value:
                values.append(value)
    return _unique(values)


def _extract_urls(text: str) -> tuple[str, ...]:
    return _unique(match.rstrip(".,") for match in URL_PATTERN.findall(text))


@dataclass(frozen=True)
class GoalProfile:
    """Canonical Factory goal profile plus Task Contract and A3 change surface."""

    intent: str
    website_type: str
    domain: str
    product_archetype: str
    validation_lane: str
    mode: str
    risk: str
    features: tuple[str, ...] = field(default_factory=tuple)
    scope: tuple[str, ...] = field(default_factory=tuple)
    change_surface: str = "PRODUCT"
    preserve: tuple[str, ...] = field(default_factory=tuple)
    forbidden: tuple[str, ...] = field(default_factory=tuple)
    references: tuple[str, ...] = field(default_factory=tuple)
    authority: str = "unspecified"
    confidence: float = 0.0
    evidence: tuple[str, ...] = field(default_factory=tuple)
    delivery_policy: str = DEFAULT_DELIVERY_POLICY_ID
    delivery_lane: str = DEFAULT_FACTORY_DELIVERY_LANE
    task_contract_version: str = TASK_CONTRACT_VERSION

    def to_dict(self) -> dict:
        return {
            "intent": self.intent,
            "website_type": self.website_type,
            "domain": self.domain,
            "product_archetype": self.product_archetype,
            "validation_lane": self.validation_lane,
            "mode": self.mode,
            "risk": self.risk,
            "features": list(self.features),
            "scope": list(self.scope),
            "change_surface": self.change_surface,
            "preserve": list(self.preserve),
            "forbidden": list(self.forbidden),
            "references": list(self.references),
            "authority": self.authority,
            "task_contract_version": self.task_contract_version,
            "delivery": {
                "policy": self.delivery_policy,
                "lane": self.delivery_lane,
            },
            "inference": {
                "confidence": self.confidence,
                "evidence": list(self.evidence),
            },
        }


TaskContract = GoalProfile


class GoalInterpreter:
    """Conservative task interpreter aligned with skills_UIUX Flow Agent OS."""

    WEBSITE_TYPES = (
        ("ecommerce", ("ecommerce", "e-commerce", "online store", "shop", "store", "bán hàng", "giỏ hàng", "checkout", "sản phẩm")),
        ("education", ("school", "university", "college", "education", "academy", "trường học", "giáo dục", "tuyển sinh")),
        ("government", ("government", "public sector", "ministry", "municipal", "chính phủ", "cơ quan nhà nước", "dịch vụ công")),
        ("hospitality", ("hotel", "resort", "restaurant", "hospitality", "booking", "khách sạn", "khu nghỉ dưỡng", "nhà hàng", "đặt phòng")),
        ("news", ("news", "magazine", "publisher", "media site", "tin tức", "tạp chí", "báo điện tử")),
        ("real-estate", ("real estate", "property", "apartment", "building", "bất động sản", "căn hộ", "chung cư")),
        ("saas", ("saas", "software platform", "web app", "dashboard", "subscription app", "phần mềm", "nền tảng")),
        ("startup", ("startup", "incubator", "accelerator", "khởi nghiệp", "ươm tạo", "tăng tốc")),
        ("portfolio", ("portfolio", "case study site", "creative studio", "hồ sơ năng lực", "showcase")),
        ("nonprofit", ("nonprofit", "ngo", "charity", "foundation", "phi lợi nhuận", "từ thiện")),
        ("landing", ("landing page", "campaign page", "microsite", "trang đích", "landing")),
        ("corporate", ("corporate", "company website", "business website", "doanh nghiệp", "công ty", "tập đoàn", "website giới thiệu")),
    )

    DOMAINS = (
        ("financial-services", (
            "fintech", "financial", "banking", "bank", "payment", "payments", "settlement",
            "treasury", "ledger", "payout", "remittance", "cross-border", "money movement",
            "mto", "psp", "kyc", "aml", "sanctions", "reconciliation", "subledger",
            "wealth", "brokerage", "investment", "card issuing", "acquiring"
        )),
    )

    FINANCIAL_ARCHETYPES = (
        ("payments-infrastructure", (
            "settlement", "payment rail", "payment rails", "multi-rail", "payout", "remittance",
            "cross-border", "money movement", "treasury", "clearing", "acquiring", "psp", "mto",
            "payment orchestration", "ledger", "card issuing"
        )),
        ("compliance-operations", ("kyc", "aml", "sanctions", "pep", "onboarding", "enhanced due diligence", "edd")),
        ("financial-operations", ("reconciliation", "reconcile", "general ledger", "gl ", "subledger", "month-end", "fund admin", "fund accounting", "exception report")),
        ("consumer-banking", ("personal finance", "spending", "saving", "savings", "budget", "banking app", "debit card", "credit card", "consumer bank", "money goals")),
        ("investment-wealth", ("wealth", "portfolio", "brokerage", "investment", "advisor", "asset management")),
    )

    FEATURES = (
        ("search", ("search", "site search", "tìm kiếm")),
        ("forms", ("form", "contact form", "lead form", "checkout", "đăng ký", "liên hệ", "biểu mẫu", "thanh toán")),
        ("auth", ("login", "sign in", "account", "authentication", "đăng nhập", "tài khoản")),
        ("dashboard", ("dashboard", "admin panel", "analytics", "bảng điều khiển", "trang quản trị")),
        ("motion", ("animation", "motion", "microinteraction", "hiệu ứng", "chuyển động")),
        ("i18n", ("multilingual", "multi-language", "bilingual", "đa ngôn ngữ", "song ngữ")),
        ("agentic-workflow", ("multi-agent", "multiagent", "subagent", "sub-agent", "agent workflow", "agentic workflow", "autonomous agent", "orchestrator", "orchestration")),
        ("user-validation", ("real users", "real user", "user research", "usability test", "usability testing", "moderated testing", "concept test", "concept testing", "user validation", "test with users", "research participants", "sponsor user", "interview users")),
        ("outcome-measurement", ("outcome metric", "outcome metrics", "success metric", "success metrics", "kpi", "analytics instrumentation", "instrumentation", "measurement plan", "measure success", "baseline metric", "product analytics")),
        ("stakeholder-governance", ("stakeholder", "playback", "governance", "decision owner", "approval gate", "cross-functional", "cross functional", "release approval")),
        ("experimentation", ("a/b test", "a/b testing", "ab test", "split test", "experiment", "feature flag", "gradual rollout", "staged rollout")),
        ("live-learning", ("post-launch", "post launch", "after launch", "live learning", "continuous research", "support tickets", "production analytics", "live monitoring", "product health")),
    )

    SCOPE_TERMS = (
        ("mobile-nav", ("mobile navigation", "mobile nav", "mobile menu")),
        ("navigation", ("navigation", "navbar", "nav bar")),
        ("hero", ("hero section", "hero")),
        ("header", ("header",)),
        ("footer", ("footer",)),
        ("landing-page", ("landing page", "trang đích")),
        ("homepage", ("homepage", "home page", "trang chủ")),
        ("dashboard", ("dashboard", "bảng điều khiển")),
        ("checkout", ("checkout",)),
        ("pricing", ("pricing", "bảng giá")),
        ("cards", ("cards", "các card", "các thẻ")),
        ("card", ("card", "thẻ")),
        ("button", ("button", "cta", "nút")),
        ("icon", ("icon", "biểu tượng")),
        ("logo", ("logo",)),
        ("input", ("input", "field", "ô nhập")),
        ("form", ("form", "biểu mẫu")),
        ("modal", ("modal", "dialog")),
        ("sidebar", ("sidebar",)),
        ("thumbnail", ("thumbnail",)),
        ("image", ("image", "ảnh")),
        ("banner", ("banner",)),
        ("typography", ("typography", "kiểu chữ")),
        ("content", ("content", "copy", "nội dung")),
        ("animation", ("animation", "motion", "hiệu ứng", "chuyển động")),
    )

    INTENT_TERMS = (
        ("redesign", ("redesign", "re-design", "thiết kế lại", "làm lại giao diện")),
        ("rebuild", ("rebuild", "build lại", "xây lại")),
        ("fix", ("fix", "repair", "bugfix", "sửa lỗi", "khắc phục", "sửa")),
        ("polish", ("polish", "trau chuốt", "tinh chỉnh", "hoàn thiện giao diện")),
        ("improve", ("improve", "enhance", "refine", "cải thiện", "nâng cấp", "tối ưu giao diện")),
    )

    PRESERVE_PATTERNS = (r"(?:giữ nguyên|giữ lại|giữ|keep|preserve|retain)\s+([^,.;\n]+)",)
    FORBIDDEN_PATTERNS = (r"(?:đừng|không được|must not|do not|don't|dont|avoid)\s+(?:đụng|sửa|thay đổi|đổi|remove|delete|change|modify)?\s*([^,.;\n]+)",)
    SCOPE_PATTERNS = (
        r"(?:scope|phạm vi)\s*[:=-]\s*([^,.;\n]+)",
        r"(?:chỉ|only)\s+(?:sửa|fix|polish|improve|cải thiện|nâng cấp|chỉnh|đổi|thay đổi)\s+([^,.;\n]+)",
    )
    REFERENCE_PATTERNS = (r"(?:tham khảo|reference|refer to|inspired by)\s+([^,.;\n]+)",)

    @classmethod
    def _intent(cls, text: str) -> str:
        for intent, terms in cls.INTENT_TERMS:
            if _contains_non_negated(text, terms):
                return intent
        return "build"

    @classmethod
    def _scope(cls, text: str, preserve: tuple[str, ...], forbidden: tuple[str, ...]) -> tuple[str, ...]:
        explicit = _extract_fragments(text, cls.SCOPE_PATTERNS)
        if explicit:
            return explicit
        scan_text = re.split(r"\b(?:tham khảo|reference|refer to|inspired by)\b", text, maxsplit=1)[0]
        blocked_text = " ".join(preserve + forbidden)
        inferred: list[str] = []
        for name, terms in cls.SCOPE_TERMS:
            if _contains(scan_text, terms) and not _contains(blocked_text, terms):
                inferred.append(name)
        return _unique(inferred)

    @staticmethod
    def _authority(text: str) -> str:
        if _contains(text, ("read only", "read-only", "audit only", "analysis only", "analyze only", "review only", "chỉ audit", "chỉ review", "chỉ phân tích", "chỉ kiểm tra", "không sửa code", "không thay đổi code", "không chỉnh code")):
            return "read_only"
        if _contains(text, ("merge to main", "merge into main", "merge vào main", "deploy production", "deploy to production", "go live", "release production", "lên production")):
            return "release"
        if _contains(text, ("deploy preview", "preview deployment", "push to vercel", "deploy to vercel", "external write", "publish preview")):
            return "external_write"
        if _contains(text, ("implement", "sửa code", "chỉnh code", "viết code", "tạo branch", "create branch", "open pr", "pull request", "commit", "push code", "apply changes")):
            return "branch_write"
        return "unspecified"

    def interpret(self, goal: str) -> GoalProfile:
        text = re.sub(r"\s+", " ", goal.strip().lower())
        evidence: list[str] = []
        intent = self._intent(text)
        evidence.append(f"intent:{intent}")

        preserve = _extract_fragments(text, self.PRESERVE_PATTERNS)
        forbidden = _extract_fragments(text, self.FORBIDDEN_PATTERNS)
        references = _extract_urls(goal)
        if not references:
            references = _extract_fragments(text, self.REFERENCE_PATTERNS)
        scope = self._scope(text, preserve, forbidden)
        authority = self._authority(text)
        change_surface = classify_change_surface(text, intent, scope)

        if scope:
            evidence.append("scope:" + "|".join(scope))
        evidence.append(f"change_surface:{change_surface}")
        if preserve:
            evidence.append("preserve:" + "|".join(preserve))
        if forbidden:
            evidence.append("forbidden:" + "|".join(forbidden))
        if references:
            evidence.append("references:" + "|".join(references))
        if authority != "unspecified":
            evidence.append(f"authority:{authority}")

        website_type = "generic"
        for candidate, terms in self.WEBSITE_TYPES:
            if _contains(text, terms):
                website_type = candidate
                evidence.append(f"website_type:{candidate}")
                break

        domain = "generic"
        for candidate, terms in self.DOMAINS:
            if _contains(text, terms):
                domain = candidate
                evidence.append(f"domain:{candidate}")
                break

        product_archetype = "generic"
        if domain == "financial-services":
            for candidate, terms in self.FINANCIAL_ARCHETYPES:
                if _contains(text, terms):
                    product_archetype = candidate
                    evidence.append(f"product_archetype:{candidate}")
                    break

        features: list[str] = []
        for name, terms in self.FEATURES:
            if _contains(text, terms):
                features.append(name)
                evidence.append(f"feature:{name}")

        if _contains(text, ("staging", "production candidate", "pre-production")):
            mode = "production-candidate"
        elif _contains(text, ("production", "go live", "lên production", "chạy thật")):
            mode = "production"
        elif _contains(text, ("mockup", "visual prototype", "chỉ giao diện")):
            mode = "visual-prototype"
        else:
            mode = "interactive-prototype"
        evidence.append(f"mode:{mode}")

        risk = "standard"
        if website_type == "government" or _contains(text, ("high risk", "critical", "compliance", "tuân thủ")):
            risk = "high"
        elif mode == "production":
            risk = "production"
        evidence.append(f"risk:{risk}")

        validation_lane = "prototype"
        lifecycle_features = {"user-validation", "outcome-measurement", "stakeholder-governance", "experimentation", "live-learning"}
        if mode in {"production", "production-candidate"}:
            validation_lane = "production-learning"
        elif risk == "high" or lifecycle_features.intersection(features):
            validation_lane = "evidence-led"
        evidence.append(f"validation_lane:{validation_lane}")
        evidence.append(f"delivery_policy:{DEFAULT_DELIVERY_POLICY_ID}")
        evidence.append(f"delivery_lane:{DEFAULT_FACTORY_DELIVERY_LANE}")

        return GoalProfile(
            intent=intent,
            website_type=website_type,
            domain=domain,
            product_archetype=product_archetype,
            validation_lane=validation_lane,
            mode=mode,
            risk=risk,
            features=tuple(features),
            scope=scope,
            change_surface=change_surface,
            preserve=preserve,
            forbidden=forbidden,
            references=references,
            authority=authority,
            confidence=0.95 if website_type != "generic" else 0.65,
            evidence=tuple(evidence),
            delivery_policy=DEFAULT_DELIVERY_POLICY_ID,
            delivery_lane=DEFAULT_FACTORY_DELIVERY_LANE,
        )


class ProfessionalWebsiteFlow:
    """Read the declarative flow and default delivery policy shipped by skills_UIUX."""

    FACTORY_TO_FLOW_STAGE = {
        "reference_analysis": "research", "research": "research", "ux_ia": "research",
        "art_direction": "design", "design_contract": "design", "design_system": "design",
        "implementation_plan": "implementation", "visual_composition": "design",
        "specification_compile": "implementation", "implementation": "implementation",
        "browser_qa": "qa", "visual_qa": "qa", "repair": "qa",
    }

    EXTRA_BY_FACTORY_STAGE = {
        "reference_analysis": ("reference-extraction-and-design-audit",),
        "ux_ia": ("ux-research-and-journey", "journey-driven-content-and-layout"),
        "art_direction": ("visual-taste-calibration", "brand-guidelines", "motion-and-microinteractions", MOTION_COMPONENT_INTELLIGENCE, ANTHROPIC_FRONTEND_DESIGN),
        "design_system": ("responsive-and-device-strategy", "accessibility"),
        "implementation_plan": ("frontend-architecture-and-refactoring",),
        "visual_composition": ("visual-taste-calibration", "responsive-and-device-strategy", "motion-and-microinteractions", MOTION_COMPONENT_INTELLIGENCE, ANTHROPIC_FRONTEND_DESIGN),
        "specification_compile": ("prompt-compiler", "accessibility", "testing-strategy"),
        "implementation": ("accessibility", "motion-and-microinteractions", MOTION_COMPONENT_INTELLIGENCE, ANTHROPIC_FRONTEND_DESIGN),
        "browser_qa": ("visual-regression-and-design-drift", ANTHROPIC_WEBAPP_TESTING),
        "visual_qa": ("visual-taste-calibration", "visual-regression-and-design-drift", ANTHROPIC_FRONTEND_DESIGN, ANTHROPIC_WEBAPP_TESTING),
        "repair": ("ui-improvement", "visual-taste-calibration", "responsive-and-device-strategy", "motion-and-microinteractions", MOTION_COMPONENT_INTELLIGENCE, ANTHROPIC_FRONTEND_DESIGN),
    }

    COMPLEX_PROTOTYPE_FEATURES = frozenset({"auth", "dashboard", "forms", "search"})

    def __init__(self, skills_root: Path) -> None:
        self.skills_root = Path(skills_root).resolve()
        self.flow_path = self.skills_root / "flows" / "professional-website-redesign.json"
        if not self.flow_path.is_file():
            raise FileNotFoundError(f"Professional website flow missing: {self.flow_path}")
        self.document = json.loads(self.flow_path.read_text(encoding="utf-8"))
        self._stages = {stage["id"]: stage for stage in self.document.get("stages", [])}
        self.delivery_policy_path = self.skills_root / "policies" / f"{DEFAULT_DELIVERY_POLICY_ID}.json"
        if not self.delivery_policy_path.is_file():
            raise FileNotFoundError(f"Default website delivery policy missing: {self.delivery_policy_path}")
        self.delivery_policy = json.loads(self.delivery_policy_path.read_text(encoding="utf-8"))
        if self.delivery_policy.get("id") != DEFAULT_DELIVERY_POLICY_ID:
            raise ValueError(f"Unexpected default delivery policy id: {self.delivery_policy.get('id')!r}; expected {DEFAULT_DELIVERY_POLICY_ID!r}")
        phase_ids = [phase.get("id") for phase in self.delivery_policy.get("full_prompt_os", {}).get("phases", [])]
        if phase_ids != [0, 1, 2, 3, 4]:
            raise ValueError(f"Default delivery policy must define Prompt OS phases 0→4, got {phase_ids!r}")
        self.interpreter = GoalInterpreter()

    @staticmethod
    def _condition_matches(condition: dict, profile: GoalProfile) -> bool:
        values = profile.to_dict()
        for key, expected in condition.items():
            actual = values.get(key)
            allowed = {str(item) for item in expected} if isinstance(expected, list) else {str(expected)}
            if key == "features":
                if not allowed.intersection({str(item) for item in profile.features}):
                    return False
            elif str(actual) not in allowed:
                return False
        return True

    @staticmethod
    def _unique(items: list[str]) -> list[str]:
        return list(dict.fromkeys(item for item in items if item))

    def resolve_skill_names(self, factory_stage: str, goal: str) -> tuple[GoalProfile, list[str], list[str]]:
        flow_stage_id = self.FACTORY_TO_FLOW_STAGE.get(factory_stage)
        if not flow_stage_id or flow_stage_id not in self._stages:
            raise ValueError(f"No declarative flow mapping for Factory stage: {factory_stage}")
        profile = self.interpreter.interpret(goal)
        stage = self._stages[flow_stage_id]
        mandatory = list(stage.get("required_skills", []))
        selected = list(mandatory)
        for rule in stage.get("conditional_skills", []):
            if self._condition_matches(rule.get("when", {}), profile):
                selected.extend(rule.get("skills", []))
        selected.extend(self.EXTRA_BY_FACTORY_STAGE.get(factory_stage, ()))
        if factory_stage == "implementation" and profile.mode == "interactive-prototype" and self.COMPLEX_PROTOTYPE_FEATURES.intersection(profile.features):
            selected.append(ANTHROPIC_WEB_ARTIFACTS)
        if factory_stage == "repair":
            selected.extend(("web-ui-code-review", "state-feedback-and-error-recovery"))
        return profile, self._unique(selected), self._unique(mandatory)

    def resolve_paths(self, factory_stage: str, goal: str) -> tuple[GoalProfile, list[str], list[str]]:
        profile, selected, mandatory = self.resolve_skill_names(factory_stage, goal)
        missing = [name for name in selected if not (self.skills_root / name / "SKILL.md").is_file()]
        if missing:
            submodule_hint = ""
            if any(name.startswith("upstream/anthropic-skills/") for name in missing):
                submodule_hint = " Run: git submodule update --init --recursive."
            raise FileNotFoundError("Declarative flow references missing skills: " + ", ".join(missing) + submodule_hint)
        return profile, [f"{name}/SKILL.md" for name in selected], [f"{name}/SKILL.md" for name in mandatory]
