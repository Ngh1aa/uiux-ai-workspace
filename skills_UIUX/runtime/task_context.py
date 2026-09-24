from __future__ import annotations

import re
from dataclasses import dataclass, asdict
from typing import Iterable


def _contains(text: str, terms: Iterable[str]) -> bool:
    return any(term in text for term in terms)


@dataclass(frozen=True)
class GoalInterpretation:
    intent: str
    website_type: str
    domain: str
    product_archetype: str
    validation_lane: str
    mode: str
    risk: str
    features: list[str]
    confidence: float
    evidence: list[str]

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
            "inference": {
                "confidence": payload["confidence"],
                "evidence": payload["evidence"],
            },
        }


class GoalInterpreter:
    """Conservative first-pass classifier for goal-driven Flow OS."""

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

    def interpret(self, goal: str) -> GoalInterpretation:
        normalized = re.sub(r"\s+", " ", goal.strip().lower())
        evidence: list[str] = []

        if _contains(normalized, ("redesign", "re-design", "thiết kế lại", "làm lại giao diện")):
            intent = "redesign"
        elif _contains(normalized, ("rebuild", "build lại", "xây lại")):
            intent = "rebuild"
        else:
            intent = "build"
        evidence.append(f"intent:{intent}")

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

        if _contains(normalized, ("production", "go live", "deploy production", "lên production", "chạy thật")):
            mode = "production"
        elif _contains(normalized, ("production candidate", "staging", "pre-production", "tiền production")):
            mode = "production-candidate"
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
            confidence=confidence,
            evidence=evidence,
        )
