from __future__ import annotations

import re
from dataclasses import asdict, dataclass, field
from typing import Iterable

from core.runtime.flow_os.adaptive_surface import classify_change_surface
from core.runtime.flow_os.specialist_taxonomy import assess_domain_ambiguity, contains_terms, infer_specialist_context


TASK_CONTRACT_VERSION = "1.0"
DEFAULT_DELIVERY_POLICY_ID = "adaptive-prompt-os-v4"
DEFAULT_FACTORY_DELIVERY_LANE = "full_prompt_os"
AUTHORITY_LEVELS = ("read_only", "branch_write", "external_write", "release")
NON_MUTATING_INTENTS = frozenset({"audit", "review", "research", "validate", "qa"})
URL_PATTERN = re.compile(r"https?://[^\s,;)\]}>]+", re.IGNORECASE)
NEGATION_PREFIX = r"\b(?:không(?:\s+(?:được|cần|có))?|đừng|do not|don't|dont|must not|without|no)\s+"
CLAUSE_END = (
    r"(?=[,.;\n]|$|\b(?:but|however|nhưng|sau đó|then)\b|"
    r"\b(?:and|và)\s+(?:fix|sửa|improve|cải thiện|build|implement|review|audit|run|kiểm thử)\b)"
)
NEGATED_CLAUSE = re.compile(NEGATION_PREFIX + r"(?!chỉ\b)(.+?)" + CLAUSE_END, re.IGNORECASE)


def requested_text(text: str) -> str:
    """Exclude prohibitions/absent features and deferred repairs from action inference.

    The original request remains the source for preserved/forbidden constraints.
    Positive clauses and real project context stay available to routing and advice.
    """
    active = NEGATED_CLAUSE.sub(" ", text)
    active = re.sub(
        r"\bto (?:fix|repair|implement|deploy)\b[^,.;]*?\b(?:later|in future)\b",
        " ", active, flags=re.IGNORECASE,
    )
    if contains_terms(active, ("list", "backlog", "danh sách")):
        active = re.sub(
            r"\b(?:tasks? (?:to )?(?:fix|repair)|task sửa lỗi)\b.*?" + CLAUSE_END,
            "tasks ", active, flags=re.IGNORECASE,
        )
    return active


def _contains(text: str, terms: Iterable[str]) -> bool:
    return contains_terms(text, terms)


def _contains_token(text: str, terms: Iterable[str]) -> bool:
    """Match semantic scope/feature terms as tokens, not arbitrary substrings."""
    return contains_terms(text, (re.sub(r"\s+", " ", str(term).strip()) for term in terms))


def _contains_non_negated(text: str, terms: Iterable[str]) -> bool:
    return _contains_token(requested_text(text), terms)


def _best_taxonomy_match(
    text: str,
    candidates: Iterable[tuple[str, Iterable[str]]],
) -> tuple[str, list[str]]:
    """Prefer multiple and more-specific evidence over first substring match."""
    best_name = "generic"
    best_matches: list[str] = []
    best_score = (0, 0, 0)
    for name, terms in candidates:
        matches = [term for term in terms if _contains_token(text, (term,))]
        if not matches:
            continue
        score = (
            sum(1 + term.count(" ") for term in matches),
            len(matches),
            max(len(term) for term in matches),
        )
        if score > best_score:
            best_name = name
            best_matches = matches
            best_score = score
    return best_name, best_matches


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
    """Canonical natural-language Task Contract for every Factory execution surface."""

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
    routing_status: str = "resolved"
    candidate_domains: list[str] = field(default_factory=list)
    resolution_source: str = "canonical"
    delivery_policy: str = DEFAULT_DELIVERY_POLICY_ID
    delivery_lane: str = DEFAULT_FACTORY_DELIVERY_LANE
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
            "delivery": {
                "policy": payload["delivery_policy"],
                "lane": payload["delivery_lane"],
            },
            "inference": {
                "confidence": payload["confidence"],
                "evidence": payload["evidence"],
                "routing_status": payload["routing_status"],
                "candidate_domains": payload["candidate_domains"],
                "resolution_source": payload["resolution_source"],
            },
        }

    def to_dict(self) -> dict[str, object]:
        return self.to_context()


TaskContract = GoalInterpretation
GoalProfile = GoalInterpretation


class GoalInterpreter:
    """Single canonical compiler for intent, scope, lifecycle and change surface."""

    WEBSITE_TYPES = (
        ("ecommerce", ("ecommerce", "e-commerce", "online store", "shop", "store", "bán hàng", "giỏ hàng", "checkout", "sản phẩm")),
        ("education", ("school", "university", "college", "education", "academy", "trường học", "giáo dục", "tuyển sinh")),
        ("government", ("government", "public sector", "ministry", "municipal", "chính phủ", "cơ quan nhà nước", "dịch vụ công")),
        ("hospitality", ("hotel", "resort", "restaurant", "hospitality", "booking", "khách sạn", "khu nghỉ dưỡng", "nhà hàng", "đặt phòng")),
        ("news", ("news", "magazine", "publisher", "media site", "tin tức", "tạp chí", "báo điện tử")),
        ("real-estate", ("real estate", "property", "apartment", "building", "bất động sản", "căn hộ", "chung cư", "dự án nhà ở")),
        ("saas", ("saas", "software platform", "web app", "dashboard", "operations console", "fraud console", "admin console", "subscription app", "phần mềm", "nền tảng")),
        ("startup", ("startup", "incubator", "accelerator", "khởi nghiệp", "ươm tạo", "tăng tốc")),
        ("portfolio", ("portfolio website", "portfolio site", "portfolio", "personal portfolio", "designer portfolio", "case study site", "creative studio", "hồ sơ năng lực", "showcase")),
        ("nonprofit", ("nonprofit", "ngo", "charity", "foundation", "phi lợi nhuận", "quỹ", "từ thiện")),
        ("landing", ("landing page", "campaign page", "microsite", "trang đích", "landing")),
        ("corporate", ("corporate", "company website", "business website", "doanh nghiệp", "công ty", "tập đoàn", "website giới thiệu")),
    )

    DOMAINS = (
        ("financial-services", (
            "fintech", "financial", "banking", "bank", "payment", "payments", "settlement",
            "treasury", "ledger", "payout", "remittance", "cross-border", "money movement",
            "mto", "psp", "kyc", "aml", "sanctions", "reconciliation", "subledger",
            "wealth", "brokerage", "investment", "card issuing", "acquiring", "fraud",
            "chargeback", "dispute", "3ds", "3-d secure", "risk operations", "transaction risk",
        )),
        ("art-culture", (
            "museum", "art museum", "art gallery", "exhibition", "artwork", "art collection",
            "cultural heritage", "visual archive", "artist discovery", "museum experience",
            "bảo tàng", "phòng tranh", "triển lãm", "tác phẩm nghệ thuật", "di sản văn hóa",
        )),
        ("travel-tourism", (
            "travel guide", "city guide", "destination guide", "tourism", "tourist", "itinerary",
            "travel itinerary", "visitor guide", "travel destination", "local attractions",
            "du lịch", "điểm đến", "cẩm nang du lịch", "lịch trình du lịch", "địa điểm tham quan",
        )),
        ("industrial-services", (
            "industrial", "manufacturing", "engineering service", "engineering services",
            "industrial maintenance", "industrial repair", "motor repair", "electric motor repair",
            "machinery repair", "plant maintenance", "factory maintenance", "industrial equipment",
            "công nghiệp", "sản xuất công nghiệp", "bảo trì công nghiệp", "sửa chữa động cơ", "nhà máy",
        )),
        ("mobility-ev", (
            "smart mobility", "electric vehicle", "electric vehicles", "ev charging", "charging station",
            "charging network", "vehicle charging", "fleet mobility", "automotive mobility",
            "xe điện", "trạm sạc", "mạng lưới sạc", "di chuyển thông minh", "giao thông thông minh",
        )),
        ("ai-software", (
            "artificial intelligence", "generative ai", "ai-native", "ai native", "ai product",
            "ai platform", "ai saas", "machine learning", "large language model", "llm platform",
            "ai copilot", "trí tuệ nhân tạo", "sản phẩm ai", "nền tảng ai",
        )),
        ("education-edtech", (
            "edtech", "learning platform", "learning management system", "lms platform",
            "online learning", "course platform", "digital classroom", "student learning",
            "nền tảng học tập", "học trực tuyến", "lớp học số", "công nghệ giáo dục",
        )),
    )

    FINANCIAL_ARCHETYPES = (
        ("trust-safety-risk", (
            "fraud operations", "fraud ops", "fraud", "risk operations", "risk review",
            "transaction risk", "risk score", "case review", "case management", "manual review",
            "review queue", "case queue", "chargeback", "dispute", "disputes", "3ds",
            "3-d secure", "suspicious transaction", "investigation workflow",
        )),
        ("payments-infrastructure", (
            "settlement", "payment rail", "payment rails", "multi-rail", "payout", "remittance",
            "cross-border", "money movement", "treasury", "clearing", "acquiring", "psp", "mto",
            "payment orchestration", "ledger", "card issuing",
        )),
        ("compliance-operations", ("kyc", "aml", "sanctions", "pep", "onboarding", "enhanced due diligence", "edd")),
        ("financial-operations", ("reconciliation", "reconcile", "general ledger", "gl ", "subledger", "month-end", "fund admin", "fund accounting", "exception report")),
        ("consumer-banking", ("personal finance", "spending", "saving", "savings", "budget", "banking app", "debit card", "credit card", "consumer bank", "money goals")),
        ("investment-wealth", ("wealth", "investment portfolio", "wealth portfolio", "brokerage", "investment", "advisor", "asset management")),
    )

    FEATURE_TERMS = (
        ("search", ("search", "site search", "tìm kiếm")),
        ("forms", ("form", "contact form", "lead form", "checkout", "đăng ký", "liên hệ", "biểu mẫu", "thanh toán")),
        ("auth", ("login", "sign in", "account", "authentication", "đăng nhập", "tài khoản", "đăng ký tài khoản")),
        ("dashboard", ("dashboard", "admin panel", "analytics", "operations console", "fraud console", "admin console", "bảng điều khiển", "trang quản trị")),
        ("data-tables", ("data table", "case queue", "review queue", "transaction table", "transaction list", "case list")),
        ("motion", ("animation", "motion", "microinteraction", "hiệu ứng", "chuyển động")),
        ("i18n", ("multilingual", "multi-language", "bilingual", "đa ngôn ngữ", "song ngữ", "tiếng anh", "english version")),
        ("agentic-workflow", ("multi-agent", "multiagent", "subagent", "sub-agent", "agent workflow", "agentic workflow", "autonomous agent", "ai copilot", "ai assistant", "agent orchestration", "ai orchestration", "agent orchestrator")),
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
        ("dashboard", ("dashboard", "operations console", "fraud console", "bảng điều khiển")),
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
        ("fix", ("fix", "bugfix", "sửa lỗi", "khắc phục", "sửa")),
        ("polish", ("polish", "trau chuốt", "tinh chỉnh", "hoàn thiện giao diện")),
        ("improve", ("improve", "enhance", "refine", "cải thiện", "nâng cấp", "tối ưu giao diện")),
        ("audit", ("audit-only", "audit only", "audit existing", "audit this", "audit the", "run an audit", "ui audit", "ux audit", "chỉ audit")),
        ("review", ("review only", "review this", "review the", "design review", "code review", "chỉ review")),
        ("research", ("research only", "research this", "research the", "research into", "do research", "nghiên cứu", "khảo sát")),
        ("validate", ("validation only", "validate only", "run validation", "chỉ validate", "chỉ kiểm chứng")),
        ("qa", ("qa only", "run qa", "perform qa", "visual qa", "quality assurance", "kiểm thử")),
    )

    PRESERVE_PATTERNS = (r"(?:giữ nguyên|giữ lại|giữ|keep|preserve|retain)\s+([^,.;\n]+)",)
    FORBIDDEN_PATTERNS = (
        r"\b(?:đừng|không được|must not|do not|don't|dont|avoid)\s+(?:đụng|sửa|thay đổi|đổi|remove|delete|change|modify)?\s*(.+?)" + CLAUSE_END,
        r"\bkhông\s+(?:đụng|sửa|thay đổi|đổi|xóa|xoá|remove|delete|change|modify)\s+(.+?)" + CLAUSE_END,
        r"\bkhông\s+((?:deploy|lên production|publish|release|merge|push)\b.*?)" + CLAUSE_END,
        r"\b(?:no|without)\s+((?:deploy|deployment|release|publish|go live)\b.*?)" + CLAUSE_END,
    )
    SCOPE_PATTERNS = (
        r"(?:scope|phạm vi)\s*[:=-]\s*([^,.;\n]+)",
        r"(?:chỉ|only)\s+(?:sửa|fix|polish|improve|cải thiện|nâng cấp|chỉnh|đổi|thay đổi)\s+([^,.;\n]+)",
    )
    REFERENCE_PATTERNS = (r"(?:tham khảo|reference|refer to|inspired by)\s+([^,.;\n]+)",)

    @classmethod
    def _intent(cls, text: str) -> str:
        if cls._authority(text) == "read_only":
            for intent, terms in cls.INTENT_TERMS:
                if intent in NON_MUTATING_INTENTS and _contains_non_negated(text, terms):
                    return intent
            return "audit"
        active = requested_text(text)
        for intent, terms in cls.INTENT_TERMS:
            if _contains_token(active, terms):
                return intent
        leading_intent = re.match(r"^(audit|review|research|validate|qa)\b", text)
        if leading_intent:
            return leading_intent.group(1)
        if _contains_token(active, ("đọc repo", "đọc repository", "read the repo", "read repository", "list bugs", "list tasks", "danh sách lỗi", "danh sách task")):
            return "audit"
        return "build"

    @classmethod
    def _scope(cls, text: str, preserve: list[str], forbidden: list[str]) -> list[str]:
        explicit = _extract_fragments(text, cls.SCOPE_PATTERNS)
        if explicit:
            # Keep explicit scope bounded, but use the same canonical aliases in both languages.
            canonical = [name for name, terms in cls.SCOPE_TERMS if _contains_token(" ".join(explicit), terms)]
            return canonical or explicit
        scan_text = re.split(r"\b(?:tham khảo|reference|refer to|inspired by)\b", text, maxsplit=1)[0]
        blocked_text = " ".join(preserve + forbidden)
        inferred: list[str] = []
        for name, terms in cls.SCOPE_TERMS:
            if _contains_token(scan_text, terms) and not _contains_token(blocked_text, terms):
                inferred.append(name)
        return _unique(inferred)

    @staticmethod
    def _authority(text: str) -> str:
        if _contains(text, (
            "read only", "read-only", "audit only", "audit-only", "analysis only", "analyze only",
            "review only", "research only", "validation only", "qa only", "chỉ audit", "chỉ review",
            "chỉ phân tích", "chỉ kiểm tra", "chỉ đọc", "không sửa code", "không thay đổi code", "không chỉnh code",
            "do not change code", "don't change code", "dont change code", "no code changes",
        )):
            return "read_only"
        active = requested_text(text)
        if _contains(active, (
            "merge to main", "merge into main", "merge vào main", "deploy production",
            "deploy to production", "go live", "release production", "lên production",
        )):
            return "release"
        if _contains(active, (
            "deploy preview", "preview deployment", "push to vercel", "deploy to vercel",
            "external write", "publish preview",
        )):
            return "external_write"
        if _contains(active, (
            "implement", "sửa code", "chỉnh code", "viết code", "tạo branch", "create branch",
            "open pr", "pull request", "commit", "push code", "apply changes",
        )):
            return "branch_write"
        # An explicit deployment prohibition caps a mutating request even with a release caller.
        if any(_contains(match.group(1), ("deploy", "deployment", "go live", "lên production", "publish", "release", "merge", "push")) for match in NEGATED_CLAUSE.finditer(text)):
            return "branch_write"
        return "unspecified"

    def _archetype_for_domain(self, text: str, domain: str) -> str:
        if domain == "financial-services":
            for candidate, terms in self.FINANCIAL_ARCHETYPES:
                if _contains(text, terms):
                    return candidate
            return "generic"
        _, archetype, _ = infer_specialist_context(text, domain, "generic")
        return archetype

    def interpret(
        self,
        goal: str,
        target_truth: dict[str, str] | None = None,
    ) -> GoalInterpretation:
        original = re.sub(r"[^\S\n]+", " ", goal.strip().lower())
        normalized = re.sub(r"\s+", " ", requested_text(original))
        evidence: list[str] = []

        intent = self._intent(original)
        evidence.append(f"intent:{intent}")

        preserve = _extract_fragments(original, self.PRESERVE_PATTERNS)
        forbidden = _extract_fragments(original, self.FORBIDDEN_PATTERNS)
        references = _extract_urls(goal)
        if not references:
            references = _extract_fragments(normalized, self.REFERENCE_PATTERNS)
        scope = self._scope(normalized, preserve, forbidden)
        authority = self._authority(original)
        if intent in NON_MUTATING_INTENTS:
            authority = "read_only"
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

        website_type, website_evidence = _best_taxonomy_match(normalized, self.WEBSITE_TYPES)
        if website_type == "landing":
            non_landing = tuple(item for item in self.WEBSITE_TYPES if item[0] != "landing")
            specific_type, specific_evidence = _best_taxonomy_match(normalized, non_landing)
            if specific_type != "generic":
                website_type, website_evidence = specific_type, specific_evidence
        if website_type != "generic":
            evidence.append(f"website_type:{website_type}")
            evidence.append("website_type_evidence:" + "|".join(website_evidence))

        domain, domain_evidence = _best_taxonomy_match(normalized, self.DOMAINS)
        if domain != "generic":
            evidence.append(f"domain:{domain}")
            evidence.append("domain_evidence:" + "|".join(domain_evidence))

        product_archetype = "generic"
        if domain == "financial-services":
            product_archetype, archetype_evidence = _best_taxonomy_match(normalized, self.FINANCIAL_ARCHETYPES)
            if product_archetype != "generic":
                evidence.append(f"product_archetype:{product_archetype}")
                evidence.append("product_archetype_evidence:" + "|".join(archetype_evidence))

        initial_domain = domain
        initial_archetype = product_archetype
        domain, product_archetype, specialist_evidence = infer_specialist_context(
            normalized,
            domain,
            product_archetype,
        )
        if domain != initial_domain:
            evidence = [item for item in evidence if not item.startswith("domain:")]
        if product_archetype != initial_archetype:
            evidence = [item for item in evidence if not item.startswith("product_archetype:")]
        evidence.extend(item for item in specialist_evidence if item not in evidence)

        ambiguity_status, ambiguity_candidates, ambiguity_evidence = assess_domain_ambiguity(normalized)
        routing_status = "resolved"
        candidate_domains: list[str] = []
        resolution_source = "canonical"

        if ambiguity_status == "ambiguous":
            candidate_domains = list(ambiguity_candidates)
            truth = dict(target_truth or {})
            truth_domain = str(truth.get("domain", "")).strip()
            truth_archetype = str(truth.get("product_archetype", "")).strip()
            truth_source = str(truth.get("source", "target-project")).strip() or "target-project"

            evidence = [
                item
                for item in evidence
                if not item.startswith(("domain:", "product_archetype:", "secondary_domain:"))
            ]
            conflict_evidence = [
                item
                for item in ambiguity_evidence
                if item.startswith("domain_conflict:")
            ]
            evidence.extend(item for item in conflict_evidence if item not in evidence)

            if truth_domain and truth_domain in ambiguity_candidates:
                domain = truth_domain
                product_archetype = truth_archetype or self._archetype_for_domain(normalized, truth_domain)
                routing_status = "resolved"
                resolution_source = "target-project-truth"
                evidence.append(f"domain:{domain}")
                if product_archetype != "generic":
                    evidence.append(f"product_archetype:{product_archetype}")
                evidence.append(f"routing_status:resolved")
                evidence.append(f"routing_resolution:target-truth->{domain}")
                evidence.append(f"target_truth_source:{truth_source}")
            else:
                domain = "unresolved"
                product_archetype = "unresolved"
                routing_status = "ambiguous"
                resolution_source = "needs-evidence"
                evidence.extend(
                    item
                    for item in ambiguity_evidence
                    if item not in evidence and not item.startswith("domain_conflict:")
                )
                if truth_domain:
                    evidence.append(f"target_truth_mismatch:{truth_domain}")

        features: list[str] = []
        for feature, terms in self.FEATURE_TERMS:
            if _contains_token(normalized, terms):
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
        if (
            website_type == "government"
            or product_archetype in {"trust-safety-risk", "compliance-operations"}
            or _contains(normalized, ("high risk", "critical", "compliance", "bảo mật cao", "tuân thủ"))
        ):
            risk = "high"
        elif mode == "production":
            risk = "production"
        evidence.append(f"risk:{risk}")

        lifecycle_features = {"user-validation", "outcome-measurement", "stakeholder-governance", "experimentation", "live-learning"}
        if mode in {"production", "production-candidate"}:
            validation_lane = "production-learning"
        elif risk == "high" or lifecycle_features.intersection(features):
            validation_lane = "evidence-led"
        else:
            validation_lane = "prototype"
        evidence.append(f"validation_lane:{validation_lane}")
        evidence.append(f"delivery_policy:{DEFAULT_DELIVERY_POLICY_ID}")
        evidence.append(f"delivery_lane:{DEFAULT_FACTORY_DELIVERY_LANE}")

        if routing_status == "ambiguous":
            confidence = 0.35 if len(candidate_domains) >= 3 else 0.45
        elif resolution_source == "target-project-truth":
            confidence = 0.90
        else:
            confidence = 0.95 if website_type != "generic" or domain != "generic" else 0.65

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
            routing_status=routing_status,
            candidate_domains=candidate_domains,
            resolution_source=resolution_source,
        )
