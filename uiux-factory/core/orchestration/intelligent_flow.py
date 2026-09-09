from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path


DEFAULT_DELIVERY_POLICY_ID = "adaptive-prompt-os-v4"
DEFAULT_FACTORY_DELIVERY_LANE = "full_prompt_os"


@dataclass(frozen=True)
class GoalProfile:
    intent: str
    website_type: str
    mode: str
    risk: str
    features: tuple[str, ...] = field(default_factory=tuple)
    confidence: float = 0.0
    evidence: tuple[str, ...] = field(default_factory=tuple)
    delivery_policy: str = DEFAULT_DELIVERY_POLICY_ID
    delivery_lane: str = DEFAULT_FACTORY_DELIVERY_LANE

    def to_dict(self) -> dict:
        return {
            "intent": self.intent,
            "website_type": self.website_type,
            "mode": self.mode,
            "risk": self.risk,
            "features": list(self.features),
            "delivery": {
                "policy": self.delivery_policy,
                "lane": self.delivery_lane,
            },
            "inference": {
                "confidence": self.confidence,
                "evidence": list(self.evidence),
            },
        }


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

    FEATURES = (
        ("search", ("search", "site search", "tìm kiếm")),
        ("forms", ("form", "contact form", "lead form", "checkout", "đăng ký", "liên hệ", "biểu mẫu", "thanh toán")),
        ("auth", ("login", "sign in", "account", "authentication", "đăng nhập", "tài khoản")),
        ("dashboard", ("dashboard", "admin panel", "analytics", "bảng điều khiển", "trang quản trị")),
        ("motion", ("animation", "motion", "microinteraction", "hiệu ứng", "chuyển động")),
        ("i18n", ("multilingual", "multi-language", "bilingual", "đa ngôn ngữ", "song ngữ")),
    )

    @staticmethod
    def _contains(text: str, terms: tuple[str, ...]) -> bool:
        return any(term in text for term in terms)

    def interpret(self, goal: str) -> GoalProfile:
        text = re.sub(r"\s+", " ", goal.strip().lower())
        evidence: list[str] = []

        if self._contains(text, ("redesign", "re-design", "thiết kế lại", "làm lại giao diện")):
            intent = "redesign"
        elif self._contains(text, ("rebuild", "build lại", "xây lại")):
            intent = "rebuild"
        else:
            intent = "build"
        evidence.append(f"intent:{intent}")

        website_type = "generic"
        for candidate, terms in self.WEBSITE_TYPES:
            if self._contains(text, terms):
                website_type = candidate
                evidence.append(f"website_type:{candidate}")
                break

        features: list[str] = []
        for name, terms in self.FEATURES:
            if self._contains(text, terms):
                features.append(name)
                evidence.append(f"feature:{name}")

        if self._contains(text, ("production", "go live", "lên production", "chạy thật")):
            mode = "production"
        elif self._contains(text, ("staging", "production candidate", "pre-production")):
            mode = "production-candidate"
        elif self._contains(text, ("mockup", "visual prototype", "chỉ giao diện")):
            mode = "visual-prototype"
        else:
            mode = "interactive-prototype"
        evidence.append(f"mode:{mode}")

        risk = "standard"
        if website_type == "government" or self._contains(text, ("high risk", "critical", "compliance", "tuân thủ")):
            risk = "high"
        elif mode == "production":
            risk = "production"
        evidence.append(f"risk:{risk}")
        evidence.append(f"delivery_policy:{DEFAULT_DELIVERY_POLICY_ID}")
        evidence.append(f"delivery_lane:{DEFAULT_FACTORY_DELIVERY_LANE}")

        return GoalProfile(
            intent=intent,
            website_type=website_type,
            mode=mode,
            risk=risk,
            features=tuple(features),
            confidence=0.95 if website_type != "generic" else 0.65,
            evidence=tuple(evidence),
            delivery_policy=DEFAULT_DELIVERY_POLICY_ID,
            delivery_lane=DEFAULT_FACTORY_DELIVERY_LANE,
        )


class ProfessionalWebsiteFlow:
    """Read the declarative flow and default delivery policy shipped by skills_UIUX."""

    FACTORY_TO_FLOW_STAGE = {
        "reference_analysis": "research",
        "research": "research",
        "ux_ia": "research",
        "art_direction": "design",
        "design_contract": "design",
        "design_system": "design",
        "implementation_plan": "implementation",
        "visual_composition": "design",
        "implementation": "implementation",
        "browser_qa": "qa",
        "visual_qa": "qa",
        "repair": "qa",
    }

    EXTRA_BY_FACTORY_STAGE = {
        "reference_analysis": ("reference-extraction-and-design-audit",),
        "ux_ia": ("ux-research-and-journey", "journey-driven-content-and-layout"),
        "art_direction": ("visual-taste-calibration", "brand-guidelines"),
        "design_system": ("responsive-and-device-strategy", "accessibility"),
        "implementation_plan": ("frontend-architecture-and-refactoring",),
        "visual_composition": ("visual-taste-calibration", "responsive-and-device-strategy"),
        "implementation": ("accessibility",),
        "browser_qa": ("visual-regression-and-design-drift",),
        "visual_qa": ("visual-taste-calibration", "visual-regression-and-design-drift"),
        "repair": ("ui-improvement", "visual-taste-calibration", "responsive-and-device-strategy"),
    }

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
            raise ValueError(
                f"Unexpected default delivery policy id: {self.delivery_policy.get('id')!r}; "
                f"expected {DEFAULT_DELIVERY_POLICY_ID!r}"
            )
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
        if factory_stage == "repair":
            selected.extend(("web-ui-code-review", "state-feedback-and-error-recovery"))
        return profile, self._unique(selected), self._unique(mandatory)

    def resolve_paths(self, factory_stage: str, goal: str) -> tuple[GoalProfile, list[str], list[str]]:
        profile, selected, mandatory = self.resolve_skill_names(factory_stage, goal)
        missing = [name for name in selected if not (self.skills_root / name / "SKILL.md").is_file()]
        if missing:
            raise FileNotFoundError("Declarative flow references missing skills: " + ", ".join(missing))
        return (
            profile,
            [f"{name}/SKILL.md" for name in selected],
            [f"{name}/SKILL.md" for name in mandatory],
        )
