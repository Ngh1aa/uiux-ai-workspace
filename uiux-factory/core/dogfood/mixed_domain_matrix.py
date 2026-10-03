from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class MixedDomainCase:
    case_id: str
    family: str
    order_pair: str
    goal: str
    expected_domain: str
    expected_archetype: str
    expected_change_surface: str
    expected_flow_id: str
    expected_secondary_domains: tuple[str, ...]
    required_stage_skills: tuple[tuple[str, tuple[str, ...]], ...]

    def validate(self) -> None:
        if not self.case_id.strip() or not self.family.strip() or not self.order_pair.strip():
            raise ValueError("P1.2 case id, family and order pair are required")
        if not self.goal.strip():
            raise ValueError(f"{self.case_id} goal is required")
        if not self.expected_domain.strip() or not self.expected_archetype.strip():
            raise ValueError(f"{self.case_id} must declare expected domain + archetype")
        if not self.expected_flow_id.strip():
            raise ValueError(f"{self.case_id} must declare expected flow")
        if not self.expected_secondary_domains:
            raise ValueError(f"{self.case_id} must declare at least one secondary domain")
        if not self.required_stage_skills:
            raise ValueError(f"{self.case_id} must declare specialist stage checks")


def _case(
    *,
    case_id: str,
    family: str,
    order_pair: str,
    goal: str,
    expected_domain: str,
    expected_archetype: str,
    secondary: str,
    skills: tuple[tuple[str, tuple[str, ...]], ...],
) -> MixedDomainCase:
    return MixedDomainCase(
        case_id=case_id,
        family=family,
        order_pair=order_pair,
        goal=goal,
        expected_domain=expected_domain,
        expected_archetype=expected_archetype,
        expected_change_surface="PRODUCT",
        expected_flow_id="professional-website-redesign",
        expected_secondary_domains=(secondary,),
        required_stage_skills=skills,
    )


CASES: tuple[MixedDomainCase, ...] = (
    _case(
        case_id="ai-fintech-ai-primary-a",
        family="ai-fintech",
        order_pair="ai-fintech-ai-primary",
        goal=(
            "Build the whole product. Primary product is an AI workspace for financial analysts. "
            "Banking and treasury data are supporting domain content; include an AI copilot, chat, and workflow automation."
        ),
        expected_domain="ai-software",
        expected_archetype="ai-workspace",
        secondary="financial-services",
        skills=(
            ("research", ("saas-website", "product-discovery")),
            ("design", ("complex-workflow-and-progress-ux",)),
            ("implementation", ("state-feedback-and-error-recovery",)),
        ),
    ),
    _case(
        case_id="ai-fintech-ai-primary-b",
        family="ai-fintech",
        order_pair="ai-fintech-ai-primary",
        goal=(
            "Banking and treasury data are supporting domain content for financial analysts. "
            "Build the whole product: the primary product is an AI workspace with an AI copilot, chat, and workflow automation."
        ),
        expected_domain="ai-software",
        expected_archetype="ai-workspace",
        secondary="financial-services",
        skills=(
            ("research", ("saas-website", "product-discovery")),
            ("design", ("complex-workflow-and-progress-ux",)),
            ("implementation", ("state-feedback-and-error-recovery",)),
        ),
    ),
    _case(
        case_id="ai-fintech-fintech-primary-a",
        family="ai-fintech",
        order_pair="ai-fintech-fintech-primary",
        goal=(
            "Build the whole product. Primary product is a fintech treasury platform for payment operations. "
            "An AI copilot and workflow automation are supporting capabilities."
        ),
        expected_domain="financial-services",
        expected_archetype="payments-infrastructure",
        secondary="ai-software",
        skills=(
            ("research", ("financial-product-intelligence", "trust-credibility-and-transparency")),
            ("design", ("trust-credibility-and-transparency",)),
            ("implementation", ("state-feedback-and-error-recovery",)),
        ),
    ),
    _case(
        case_id="ai-fintech-fintech-primary-b",
        family="ai-fintech",
        order_pair="ai-fintech-fintech-primary",
        goal=(
            "An AI copilot and workflow automation support the team. Build the whole product: "
            "the primary product is a fintech payment orchestration and treasury platform."
        ),
        expected_domain="financial-services",
        expected_archetype="payments-infrastructure",
        secondary="ai-software",
        skills=(
            ("research", ("financial-product-intelligence", "trust-credibility-and-transparency")),
            ("design", ("trust-credibility-and-transparency",)),
            ("implementation", ("state-feedback-and-error-recovery",)),
        ),
    ),
    _case(
        case_id="saas-commerce-saas-primary-a",
        family="saas-commerce",
        order_pair="saas-commerce-saas-primary",
        goal=(
            "Build the whole product. Primary product is an enterprise SaaS operations platform for merchants. "
            "Ecommerce catalog, cart and checkout are supporting modules; include admin workflows and approvals."
        ),
        expected_domain="enterprise-software",
        expected_archetype="enterprise-operations",
        secondary="commerce-retail",
        skills=(
            ("research", ("product-discovery",)),
            ("design", ("complex-workflow-and-progress-ux", "data-tables-and-enterprise-ux")),
            ("implementation", ("complex-forms-and-wizards", "state-feedback-and-error-recovery")),
        ),
    ),
    _case(
        case_id="saas-commerce-saas-primary-b",
        family="saas-commerce",
        order_pair="saas-commerce-saas-primary",
        goal=(
            "Ecommerce catalog, cart and checkout are supporting modules for merchants. Build the whole product: "
            "the primary product is an enterprise SaaS operations platform with admin workflows and approvals."
        ),
        expected_domain="enterprise-software",
        expected_archetype="enterprise-operations",
        secondary="commerce-retail",
        skills=(
            ("research", ("product-discovery",)),
            ("design", ("complex-workflow-and-progress-ux", "data-tables-and-enterprise-ux")),
            ("implementation", ("complex-forms-and-wizards", "state-feedback-and-error-recovery")),
        ),
    ),
    _case(
        case_id="saas-commerce-commerce-primary-a",
        family="saas-commerce",
        order_pair="saas-commerce-commerce-primary",
        goal=(
            "Build the whole product. Primary product is an ecommerce storefront for merchants with catalog, cart and checkout. "
            "A SaaS admin workspace is a supporting operations tool."
        ),
        expected_domain="commerce-retail",
        expected_archetype="checkout-commerce",
        secondary="enterprise-software",
        skills=(
            ("research", ("ecommerce-website", "conversion-and-content")),
            ("design", ("interaction-patterns-and-form-ux", "trust-credibility-and-transparency")),
            ("implementation", ("complex-forms-and-wizards", "state-feedback-and-error-recovery")),
        ),
    ),
    _case(
        case_id="saas-commerce-commerce-primary-b",
        family="saas-commerce",
        order_pair="saas-commerce-commerce-primary",
        goal=(
            "A SaaS admin workspace supports merchant operations. Build the whole product: "
            "primary product is an ecommerce storefront with catalog, cart and checkout."
        ),
        expected_domain="commerce-retail",
        expected_archetype="checkout-commerce",
        secondary="enterprise-software",
        skills=(
            ("research", ("ecommerce-website", "conversion-and-content")),
            ("design", ("interaction-patterns-and-form-ux", "trust-credibility-and-transparency")),
            ("implementation", ("complex-forms-and-wizards", "state-feedback-and-error-recovery")),
        ),
    ),
    _case(
        case_id="edtech-enterprise-edtech-primary-a",
        family="edtech-enterprise",
        order_pair="edtech-enterprise-edtech-primary",
        goal=(
            "Build the whole product. Primary product is an EdTech LMS for instructors and students. "
            "Enterprise admin workflows and approvals support course management, grading, student management and learning analytics."
        ),
        expected_domain="education-edtech",
        expected_archetype="learning-operations",
        secondary="enterprise-software",
        skills=(
            ("research", ("education-website", "product-discovery")),
            ("design", ("data-tables-and-enterprise-ux", "data-visualization-and-dashboard-ux")),
            ("implementation", ("complex-forms-and-wizards", "state-feedback-and-error-recovery")),
        ),
    ),
    _case(
        case_id="edtech-enterprise-edtech-primary-b",
        family="edtech-enterprise",
        order_pair="edtech-enterprise-edtech-primary",
        goal=(
            "Enterprise admin workflows and approvals support operations. Build the whole product: "
            "primary product is an EdTech LMS with instructor dashboard, course management, grading, student management and learning analytics."
        ),
        expected_domain="education-edtech",
        expected_archetype="learning-operations",
        secondary="enterprise-software",
        skills=(
            ("research", ("education-website", "product-discovery")),
            ("design", ("data-tables-and-enterprise-ux", "data-visualization-and-dashboard-ux")),
            ("implementation", ("complex-forms-and-wizards", "state-feedback-and-error-recovery")),
        ),
    ),
    _case(
        case_id="edtech-enterprise-enterprise-primary-a",
        family="edtech-enterprise",
        order_pair="edtech-enterprise-enterprise-primary",
        goal=(
            "Build the whole product. Primary product is an enterprise operations platform for an education provider. "
            "An EdTech learning platform, its courses, lessons and student records are managed content; include admin workflows, approvals and data tables."
        ),
        expected_domain="enterprise-software",
        expected_archetype="enterprise-operations",
        secondary="education-edtech",
        skills=(
            ("research", ("product-discovery",)),
            ("design", ("complex-workflow-and-progress-ux", "data-tables-and-enterprise-ux")),
            ("implementation", ("complex-forms-and-wizards", "state-feedback-and-error-recovery")),
        ),
    ),
    _case(
        case_id="edtech-enterprise-enterprise-primary-b",
        family="edtech-enterprise",
        order_pair="edtech-enterprise-enterprise-primary",
        goal=(
            "An EdTech learning platform, its courses, lessons and student records are managed content for an education provider. "
            "Build the whole product: primary product is an enterprise operations platform with admin workflows, approvals and data tables."
        ),
        expected_domain="enterprise-software",
        expected_archetype="enterprise-operations",
        secondary="education-edtech",
        skills=(
            ("research", ("product-discovery",)),
            ("design", ("complex-workflow-and-progress-ux", "data-tables-and-enterprise-ux")),
            ("implementation", ("complex-forms-and-wizards", "state-feedback-and-error-recovery")),
        ),
    ),
)


def validate_matrix() -> None:
    ids: set[str] = set()
    for case in CASES:
        case.validate()
        if case.case_id in ids:
            raise ValueError(f"duplicate P1.2 case id: {case.case_id}")
        ids.add(case.case_id)
