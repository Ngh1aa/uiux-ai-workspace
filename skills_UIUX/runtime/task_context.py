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
            "mode": payload["mode"],
            "risk": payload["risk"],
            "features": payload["features"],
            "inference": {
                "confidence": payload["confidence"],
                "evidence": payload["evidence"],
            },
        }


class GoalInterpreter:
    """Deterministic first-pass task classifier for goal-driven Flow OS.

    Explicit CLI/config values should override this interpretation. The interpreter
    is deliberately conservative: when a domain cannot be inferred safely it uses
    ``generic`` instead of pretending to know the business type.
    """

    WEBSITE_TYPES: tuple[tuple[str, tuple[str, ...]], ...] = (
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

    FEATURE_TERMS: tuple[tuple[str, tuple[str, ...]], ...] = (
        ("search", ("search", "site search", "tìm kiếm")),
        ("forms", ("form", "contact form", "lead form", "checkout", "đăng ký", "liên hệ", "biểu mẫu", "thanh toán")),
        ("auth", ("login", "sign in", "account", "authentication", "đăng nhập", "tài khoản", "đăng ký tài khoản")),
        ("dashboard", ("dashboard", "admin panel", "analytics", "bảng điều khiển", "trang quản trị")),
        ("motion", ("animation", "motion", "microinteraction", "hiệu ứng", "chuyển động")),
        ("i18n", ("multilingual", "multi-language", "bilingual", "đa ngôn ngữ", "song ngữ", "tiếng anh", "english version")),
    )

    def interpret(self, goal: str) -> GoalInterpretation:
        normalized = re.sub(r"\s+", " ", goal.strip().lower())
        evidence: list[str] = []

        if _contains(normalized, ("redesign", "re-design", "thiết kế lại", "làm lại giao diện")):
            intent = "redesign"
            evidence.append("intent:redesign")
        elif _contains(normalized, ("rebuild", "build lại", "xây lại")):
            intent = "rebuild"
            evidence.append("intent:rebuild")
        else:
            intent = "build"
            evidence.append("intent:build(default)")

        website_type = "generic"
        for candidate, terms in self.WEBSITE_TYPES:
            if _contains(normalized, terms):
                website_type = candidate
                evidence.append(f"website_type:{candidate}")
                break

        features: list[str] = []
        for feature, terms in self.FEATURE_TERMS:
            if _contains(normalized, terms):
                features.append(feature)
                evidence.append(f"feature:{feature}")

        if _contains(normalized, ("production", "go live", "deploy production", "lên production", "chạy thật")):
            mode = "production"
            evidence.append("mode:production")
        elif _contains(normalized, ("production candidate", "staging", "pre-production", "tiền production")):
            mode = "production-candidate"
            evidence.append("mode:production-candidate")
        elif _contains(normalized, ("mockup", "visual prototype", "prototype hình", "chỉ giao diện")):
            mode = "visual-prototype"
            evidence.append("mode:visual-prototype")
        else:
            mode = "interactive-prototype"
            evidence.append("mode:interactive-prototype(default)")

        risk = "standard"
        if website_type == "government" or _contains(normalized, ("high risk", "critical", "compliance", "bảo mật cao", "tuân thủ")):
            risk = "high"
            evidence.append("risk:high")
        elif mode == "production":
            risk = "production"
            evidence.append("risk:production")

        confidence = 0.95 if website_type != "generic" else 0.65
        return GoalInterpretation(
            intent=intent,
            website_type=website_type,
            mode=mode,
            risk=risk,
            features=features,
            confidence=confidence,
            evidence=evidence,
        )
