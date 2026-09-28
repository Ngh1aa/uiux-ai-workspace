from __future__ import annotations

import re
from dataclasses import asdict, dataclass, field
from typing import Iterable

from runtime.adaptive_surface import classify_change_surface


TASK_CONTRACT_VERSION = "1.0"
AUTHORITY_LEVELS = ("read_only", "branch_write", "external_write", "release")
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


def _unique(values: Iterable[str]) -> list[str]:
    seen: set[str] = set()
    output: list[str] = []
    for value in values:
        cleaned = re.sub(r"\s+", " ", str(value)).strip(" \t\n\r:-–—'\"")
        if cleaned and cleaned not in seen:
            seen.add(cleaned)
            output.append(cleaned)
    return output


def _extract_fragments(text: str, patterns: Iterable[str]) -> list[str]:
    values: list[str] = []
    for pattern in patterns:
        for match in re.finditer(pattern, text, flags=re.IGNORECASE):
            value = match.group(1).strip()
            if value:
                values.append(value)
    return _unique(values)


def _extract_urls(text: str) -> list[str]:
    return _unique(match.rstrip(".,") for match in URL_PATTERN.findall(text))


@dataclass(frozen=True)
class GoalInterpretation:
    """V1 Task Contract plus Flow OS classification and A3 change-surface lane."""

    intent: str
    website_type: str
    domain: str
    product_archetype: str
    validation_lane: str
    mode: str
    risk: str
    features: list[str]
    scope: list[str] = field(default_factory=list)
    change_surface: str = "PRODUCT"
    preserve: list[str] = field(default_factory=list)
    forbidden: list[str] = field(default_factory=list)
    references: list[str] = field(default_factory=list)
    authority: str = "unspecified"
    confidence: float = 0.0
    evidence: list[str] = field(default_factory=list)
    task_contract_version: str = TASK_CONTRACT_VERSION

    def to_context(self) -> dict[str, object]:
        payload = asdict(self)
        return {
            "intent": payload["intent"],
            "website_type": payload["website_type"],
            "domain": payload["domain"],
            "product_archetype": payload["product_archetype"],
            "validation_lane": payload["validation_lane"],
            "mode": payload["mode"],
            "risk": payload["risk"],
            "features": payload["features"],
            "scope": payload["scope"],
            "change_surface": payload["change_surface"],
            "preserve": payload["preserve"],
            "forbidden": payload["forbidden"],
            "references": payload["references"],
            "authority": payload["authority"],
            "task_contract_version": payload["task_contract_version"],
            "inference": {
                "confidence": payload["confidence"],
                "evidence": payload["evidence"],
            },
        }


TaskContract = GoalInterpretation


class GoalInterpreter:
    """Conservative Task Contract compiler with adaptive change-surface classification."""

    WEBSITE_TYPES = (
        ("ecommerce", ("ecommerce", "e-commerce", "online store", "shop", "store", "bán hàng", "giỏ hàng", "checkout", "sản phẩm")),
        ("education", ("school", "university", "college", "education", "academy", "trường học", "giáo dục", "tuyển sinh")),
        ("government", ("government", "public sector", "ministry", "municipal", "chính phủ", "cơ quan nhà nước", "dịch vụ công")),
        ("hospitality", ("hotel", "resort", "restaurant", "hospitality", "booking", "khách sạn", "khu nghỉ dưỡng", "nhà hàng", "đặt phòng")),
        ("news", ("news", "magazine", "publisher", "media site", "tin tức", "tạp chí", "báo điện tử")),
        ("real-estate", ("real estate", "property", "apartment", "building", "bất động sản", "căn hộ", "chung cư", "dự án nhà ở")),
        ("saas", ("saas", "software platform", "web app", "dashboard", "subscription app", "phần mềm", "nền tảng")),
        ("startup", ("startup", "incubator", "accelerator", "khởi nghiệp", "ươm tạo", "tăng tốc")),
        ("portfolio", ("portfolio", "case study site", "creative studio", "hồ sơ năng lực", "showcase")),
        ("nonprofit", ("nonprofit", "ngo", "charity", "foundation", "phi lợi nhuận", "quỹ", "từ thiện")),
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

    FEATURE_TERMS = (
        ("search", ("search", "site search", "tìm kiếm")),
        ("forms", ("form", "contact form", "lead form", "checkout", "đăng ký", "liên hệ", "biểu mẫu", "thanh toán")),
        ("auth", ("login", "sign in", "account", "authentication", "đăng nhập", "tài khoản", "đăng ký tài khoản")),
        ("dashboard", ("dashboard", "admin panel", "analytics", "bảng điều khiển", "trang quản trị")),
        ("motion", ("animation", "motion", "microinteraction", "hiệu ứng", "chuyển động")),
        ("i18n", ("multilingual", "multi-language", "bilingual", "đa ngôn ngữ", "song ngữ", "tiếng anh", "english version")),
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

    PRESERVE_PATTERNS = (
        r"(?:giữ nguyên|giữ lại|giữ|keep|preserve|retain)\s+([^,.;\n]+)",
    )
    FORBIDDEN_PATTERNS = (
        r"(?:đừng|không được|must not|do not|don't|dont|avoid)\s+(?:đụng|sửa|thay đổi|đổi|remove|delete|change|modify)?\s*([^,.;\n]+)",
    )
    SCOPE_PATTERNS = (
        r"(?:scope|phạm vi)\s*[:=-]\s*([^,.;\n]+)",
        r"(?:chỉ|only)\s+(?:sửa|fix|polish|improve|cải thiện|nâng cấp|chỉnh|đổi|thay đổi)\s+([^,.;\n]+)",
    )
    REFERENCE_PATTERNS = (
        r"(?:tham khảo|reference|refer to|inspired by)\s+([^,.;\n]+)",
    )

    @classmethod
    def _intent(cls, text: str) -> str:
        for intent, terms in cls.INTENT_TERMS:
            if _contains_non_negated(text, terms):
                return intent
        return "build"

    @classmethod
    def _scope(cls, text: str, preserve: list[str], forbidden: list[str]) -> list[str]:
        explicit = _extract_fragments(text, cls.SCOPE_PATTERNS)
        if explicit:
            return explicit

        scan_text = re.split(
            r"\b(?:tham khảo|reference|refer to|inspired by)\b",
            text,
            maxsplit=1,
        )[0]
        blocked_text = " ".join(preserve + forbidden)
        inferred: list[str] = []
        for name, terms in cls.SCOPE_TERMS:
            if _contains(scan_text, terms) and not _contains(blocked_text, terms):
                inferred.append(name)
        return _unique(inferred)

    @staticmethod
    def _authority(text: str) -> str:
        if _contains(text, (
            "read only", "read-only", "audit only", "analysis only", "analyze only",
            "review only", "chỉ audit", "chỉ review", "chỉ phân tích", "chỉ kiểm tra",
            "không sửa code", "không thay đổi code", "không chỉnh code",
        )):
            return "read_only"
        if _contains(text, (
            "merge to main", "merge into main", "merge vào main", "deploy production",
            "deploy to production", "go live", "release production", "lên production",
        )):
            return "release"
        if _contains(text, (
            "deploy preview", "preview deployment", "push to vercel", "deploy to vercel",
            "external write", "publish preview",
        )):
            return "external_write"
        if _contains(text, (
            "implement", "sửa code", "chỉnh code", "viết code", "tạo branch", "create branch",
            "open pr", "pull request", "commit", "push code", "apply changes",
        )):
            return "branch_write"
        return "unspecified"

    def interpret(self, goal: str) -> GoalInterpretation:
        normalized = re.sub(r"\s+", " ", goal.strip().lower())
        evidence: list[str] = []

        intent = self._intent(normalized)
        evidence.append(f"intent:{intent}")

        preserve = _extract_fragments(normalized, self.PRESERVE_PATTERNS)
        forbidden = _extract_fragments(normalized, self.FORBIDDEN_PATTERNS)
        references = _extract_urls(goal)
        if not references:
            references = _extract_fragments(normalized, self.REFERENCE_PATTERNS)
        scope = self._scope(normalized, preserve, forbidden)
        authority = self._authority(normalized)
        change_surface = classify_change_surface(normalized, intent, scope)

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
            if _contains(normalized, terms):
                website_type = candidate
                evidence.append(f"website_type:{candidate}")
                break

        domain = "generic"
        for candidate, terms in self.DOMAINS:
            if _contains(normalized, terms):
                domain = candidate
                evidence.append(f"domain:{candidate}")
                break

        product_archetype = "generic"
        if domain == "financial-services":
            for candidate, terms in self.FINANCIAL_ARCHETYPES:
                if _contains(normalized, terms):
                    product_archetype = candidate
                    evidence.append(f"product_archetype:{candidate}")
                    break

        features: list[str] = []
        for feature, terms in self.FEATURE_TERMS:
            if _contains(normalized, terms):
                features.append(feature)
                evidence.append(f"feature:{feature}")

        if _contains(normalized, ("production candidate", "staging", "pre-production", "tiền production")):
            mode = "production-candidate"
        elif _contains(normalized, ("production", "go live", "deploy production", "lên production", "chạy thật")):
            mode = "production"
        elif _contains(normalized, ("mockup", "visual prototype", "prototype hình", "chỉ giao diện")):
            mode = "visual-prototype"
        else:
            mode = "interactive-prototype"
        evidence.append(f"mode:{mode}")

        risk = "standard"
        if website_type == "government" or _contains(normalized, ("high risk", "critical", "compliance", "bảo mật cao", "tuân thủ")):
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

        confidence = 0.95 if website_type != "generic" else 0.65
        return GoalInterpretation(
            intent=intent,
            website_type=website_type,
            domain=domain,
            product_archetype=product_archetype,
            validation_lane=validation_lane,
            mode=mode,
            risk=risk,
            features=features,
            scope=scope,
            change_surface=change_surface,
            preserve=preserve,
            forbidden=forbidden,
            references=references,
            authority=authority,
            confidence=confidence,
            evidence=evidence,
        )