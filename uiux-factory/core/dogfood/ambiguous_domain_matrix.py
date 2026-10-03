from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class AmbiguousDomainCase:
    case_id: str
    family: str
    order_pair: str
    goal: str
    expected_candidates: tuple[str, ...]
    expected_status: str
    target_truth_domain: str = ""
    target_truth_archetype: str = ""
    required_stage_skills: tuple[tuple[str, tuple[str, ...]], ...] = ()

    @property
    def target_truth(self) -> dict[str, str] | None:
        if not self.target_truth_domain:
            return None
        return {
            "domain": self.target_truth_domain,
            "product_archetype": self.target_truth_archetype,
            "source": f"p1.3:{self.case_id}",
        }

    def validate(self) -> None:
        if not self.case_id.strip() or not self.family.strip():
            raise ValueError("P1.3 case id and family are required")
        if not self.goal.strip():
            raise ValueError(f"{self.case_id} goal is required")
        if "primary product" in self.goal.lower() or "main product" in self.goal.lower() or "core product" in self.goal.lower():
            raise ValueError(f"{self.case_id} must not declare explicit product ownership")
        if len(self.expected_candidates) < 2:
            raise ValueError(f"{self.case_id} must declare at least two domain candidates")
        if self.expected_status not in {"ambiguous", "resolved"}:
            raise ValueError(f"{self.case_id} has invalid expected status")
        if self.expected_status == "resolved":
            if not self.target_truth_domain or not self.target_truth_archetype:
                raise ValueError(f"{self.case_id} resolved case requires target truth")
            if self.target_truth_domain not in self.expected_candidates:
                raise ValueError(f"{self.case_id} target truth must match a declared candidate")
            if not self.required_stage_skills:
                raise ValueError(f"{self.case_id} resolved case requires specialist checks")


def _ambiguous(
    *,
    case_id: str,
    family: str,
    order_pair: str,
    goal: str,
    candidates: tuple[str, str],
) -> AmbiguousDomainCase:
    return AmbiguousDomainCase(
        case_id=case_id,
        family=family,
        order_pair=order_pair,
        goal=goal,
        expected_candidates=tuple(sorted(candidates)),
        expected_status="ambiguous",
    )


def _resolved(
    *,
    case_id: str,
    family: str,
    goal: str,
    candidates: tuple[str, str],
    domain: str,
    archetype: str,
    skills: tuple[tuple[str, tuple[str, ...]], ...],
) -> AmbiguousDomainCase:
    return AmbiguousDomainCase(
        case_id=case_id,
        family=family,
        order_pair="",
        goal=goal,
        expected_candidates=tuple(sorted(candidates)),
        expected_status="resolved",
        target_truth_domain=domain,
        target_truth_archetype=archetype,
        required_stage_skills=skills,
    )


CASES: tuple[AmbiguousDomainCase, ...] = (
    _ambiguous(
        case_id="ai-fintech-order-a1",
        family="ai-fintech",
        order_pair="ai-fintech-order-1",
        goal=(
            "Build the whole product: an AI workspace with AI copilot and automation for banking treasury teams, "
            "including settlement and payment operations."
        ),
        candidates=("ai-software", "financial-services"),
    ),
    _ambiguous(
        case_id="ai-fintech-order-b1",
        family="ai-fintech",
        order_pair="ai-fintech-order-1",
        goal=(
            "Build the whole product for banking treasury teams with settlement and payment operations, "
            "using an AI workspace with AI copilot and automation."
        ),
        candidates=("ai-software", "financial-services"),
    ),
    _ambiguous(
        case_id="ai-fintech-order-a2",
        family="ai-fintech",
        order_pair="ai-fintech-order-2",
        goal="Design a generative AI assistant and workspace for a fintech treasury and payment orchestration product.",
        candidates=("ai-software", "financial-services"),
    ),
    _ambiguous(
        case_id="ai-fintech-order-b2",
        family="ai-fintech",
        order_pair="ai-fintech-order-2",
        goal="Design a fintech treasury and payment orchestration product with a generative AI assistant and workspace.",
        candidates=("ai-software", "financial-services"),
    ),
    _resolved(
        case_id="ai-fintech-truth-ai",
        family="ai-fintech",
        goal="Build an AI workspace with AI copilot for banking treasury, settlement and payment operations.",
        candidates=("ai-software", "financial-services"),
        domain="ai-software",
        archetype="ai-workspace",
        skills=(
            ("research", ("saas-website", "product-discovery")),
            ("design", ("complex-workflow-and-progress-ux",)),
        ),
    ),
    _resolved(
        case_id="ai-fintech-truth-fintech",
        family="ai-fintech",
        goal="Build an AI workspace with AI copilot for a fintech treasury, settlement and payment orchestration product.",
        candidates=("ai-software", "financial-services"),
        domain="financial-services",
        archetype="payments-infrastructure",
        skills=(
            ("research", ("financial-product-intelligence", "trust-credibility-and-transparency")),
            ("design", ("trust-credibility-and-transparency",)),
        ),
    ),
    _ambiguous(
        case_id="saas-commerce-order-a1",
        family="saas-commerce",
        order_pair="saas-commerce-order-1",
        goal=(
            "Build the whole product: an enterprise SaaS operations platform for merchants with admin workflows and approvals, "
            "plus ecommerce catalog, cart and checkout."
        ),
        candidates=("enterprise-software", "commerce-retail"),
    ),
    _ambiguous(
        case_id="saas-commerce-order-b1",
        family="saas-commerce",
        order_pair="saas-commerce-order-1",
        goal=(
            "Build the whole product with ecommerce catalog, cart and checkout plus an enterprise SaaS operations platform "
            "for merchants with admin workflows and approvals."
        ),
        candidates=("enterprise-software", "commerce-retail"),
    ),
    _ambiguous(
        case_id="saas-commerce-order-a2",
        family="saas-commerce",
        order_pair="saas-commerce-order-2",
        goal="Design an admin workspace and enterprise operations dashboard connected to an ecommerce storefront with cart and checkout.",
        candidates=("enterprise-software", "commerce-retail"),
    ),
    _ambiguous(
        case_id="saas-commerce-order-b2",
        family="saas-commerce",
        order_pair="saas-commerce-order-2",
        goal="Design an ecommerce storefront with cart and checkout connected to an admin workspace and enterprise operations dashboard.",
        candidates=("enterprise-software", "commerce-retail"),
    ),
    _resolved(
        case_id="saas-commerce-truth-enterprise",
        family="saas-commerce",
        goal="Build an enterprise SaaS operations platform with admin workflows for ecommerce catalog, cart and checkout teams.",
        candidates=("enterprise-software", "commerce-retail"),
        domain="enterprise-software",
        archetype="enterprise-operations",
        skills=(
            ("research", ("product-discovery",)),
            ("design", ("complex-workflow-and-progress-ux", "data-tables-and-enterprise-ux")),
        ),
    ),
    _resolved(
        case_id="saas-commerce-truth-commerce",
        family="saas-commerce",
        goal="Build an ecommerce storefront with catalog, cart and checkout plus an enterprise admin workspace for merchant operations.",
        candidates=("enterprise-software", "commerce-retail"),
        domain="commerce-retail",
        archetype="checkout-commerce",
        skills=(
            ("research", ("ecommerce-website", "conversion-and-content")),
            ("design", ("interaction-patterns-and-form-ux", "trust-credibility-and-transparency")),
        ),
    ),
    _ambiguous(
        case_id="edtech-enterprise-order-a1",
        family="edtech-enterprise",
        order_pair="edtech-enterprise-order-1",
        goal=(
            "Build the whole product: an EdTech LMS and learning platform with course management, student records, "
            "enterprise admin workflows, approvals and data tables."
        ),
        candidates=("education-edtech", "enterprise-software"),
    ),
    _ambiguous(
        case_id="edtech-enterprise-order-b1",
        family="edtech-enterprise",
        order_pair="edtech-enterprise-order-1",
        goal=(
            "Build the whole product with enterprise admin workflows, approvals and data tables around an EdTech LMS and "
            "learning platform with course management and student records."
        ),
        candidates=("education-edtech", "enterprise-software"),
    ),
    _ambiguous(
        case_id="edtech-enterprise-order-a2",
        family="edtech-enterprise",
        order_pair="edtech-enterprise-order-2",
        goal="Design a learning management system with instructor dashboard, learning analytics and enterprise operations workflows.",
        candidates=("education-edtech", "enterprise-software"),
    ),
    _ambiguous(
        case_id="edtech-enterprise-order-b2",
        family="edtech-enterprise",
        order_pair="edtech-enterprise-order-2",
        goal="Design enterprise operations workflows with instructor dashboard and learning analytics for a learning management system.",
        candidates=("education-edtech", "enterprise-software"),
    ),
    _resolved(
        case_id="edtech-enterprise-truth-edtech",
        family="edtech-enterprise",
        goal="Build an EdTech LMS with course management, learning analytics, admin workflows, approvals and enterprise data tables.",
        candidates=("education-edtech", "enterprise-software"),
        domain="education-edtech",
        archetype="learning-operations",
        skills=(
            ("research", ("education-website", "product-discovery")),
            ("design", ("data-tables-and-enterprise-ux", "data-visualization-and-dashboard-ux")),
        ),
    ),
    _resolved(
        case_id="edtech-enterprise-truth-enterprise",
        family="edtech-enterprise",
        goal="Build an enterprise operations platform with admin workflows and approvals for an EdTech LMS, courses and student records.",
        candidates=("education-edtech", "enterprise-software"),
        domain="enterprise-software",
        archetype="enterprise-operations",
        skills=(
            ("research", ("product-discovery",)),
            ("design", ("complex-workflow-and-progress-ux", "data-tables-and-enterprise-ux")),
        ),
    ),
)


def validate_matrix() -> None:
    ids: set[str] = set()
    pairs: dict[str, int] = {}
    for case in CASES:
        case.validate()
        if case.case_id in ids:
            raise ValueError(f"duplicate P1.3 case id: {case.case_id}")
        ids.add(case.case_id)
        if case.order_pair:
            pairs[case.order_pair] = pairs.get(case.order_pair, 0) + 1
    malformed = {pair: count for pair, count in pairs.items() if count != 2}
    if malformed:
        raise ValueError(f"P1.3 order pairs must contain exactly two cases: {malformed}")
