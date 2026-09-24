from __future__ import annotations

import json

from metagpt.actions import Action

from core.contracts.design_system_schema import DesignSystemContract
from core.contracts.implementation_plan_schema import ImplementationPlan
from core.contracts.schema import DesignContract
from core.contracts.visual_composition_schema import (
    PageSpec,
    SectionSpec,
    VisualComposition,
    VisualCompositionGate,
)


class CreateVisualCompositionV2(Action):
    """
    Domain-aware, direction-aware visual composition.

    V1 was intentionally ecommerce-heavy. V2 makes page composition depend on
    the actual project domain and the explicit art direction selected in the
    workbench, while keeping the output contract deterministic and zero-cost.
    """

    name: str = "CreateVisualCompositionV2"

    @staticmethod
    def direction_profile(
        goal: str,
    ) -> str:
        text = goal.lower()

        if any(
            token in text
            for token in (
                "editorial commerce",
                "editorial authority",
                "academic editorial",
                "work first",
            )
        ):
            return "editorial"

        if any(
            token in text
            for token in (
                "immersive market",
                "creative system",
                "future learning",
                "systems confidence",
            )
        ):
            return "immersive"

        if any(
            token in text
            for token in (
                "precision retail",
                "quiet confidence",
                "strategic minimal",
            )
        ):
            return "precision"

        if "human campus" in text:
            return "human"

        return "balanced"

    @staticmethod
    def section(
        section_type: str,
        purpose: str,
        composition: str,
        visual_anchor: str,
        *,
        priority: str = "P1",
        density: str = "medium",
        mobile: list[str] | None = None,
        notes: list[str] | None = None,
    ) -> SectionSpec:
        return SectionSpec(
            type=section_type,
            purpose=purpose,
            priority=priority,
            composition=composition,
            visual_anchor=visual_anchor,
            density=density,
            mobile_behavior=(
                mobile
                or [
                    "Stack according to reading and decision priority.",
                    "Preserve the primary visual anchor without horizontal overflow.",
                ]
            ),
            notes=(
                notes
                or []
            ),
        )

    @classmethod
    def hero_composition(
        cls,
        profile: str,
        noun: str,
    ) -> str:
        if profile == "editorial":
            return (
                "asymmetric-editorial-"
                + noun
                + "-stage"
            )

        if profile == "immersive":
            return (
                "layered-full-bleed-"
                + noun
                + "-stage"
            )

        if profile == "precision":
            return (
                "precision-grid-"
                + noun
                + "-stage"
            )

        if profile == "human":
            return (
                "human-story-"
                + noun
                + "-stage"
            )

        return (
            "purpose-led-"
            + noun
            + "-stage"
        )

    @classmethod
    def ecommerce_sections(
        cls,
        path: str,
        page_role: str,
        profile: str,
    ) -> list[SectionSpec]:
        role = page_role.lower()
        route = path.lower()

        if path == "/" or "home" in role:
            return [
                cls.section(
                    "commerce-header",
                    "Orient shoppers and expose discovery utilities.",
                    "three-zone-commerce-header",
                    "brand + categories + search/cart",
                    priority="P0",
                    density="low",
                    mobile=[
                        "Collapse secondary navigation.",
                        "Keep brand, search and cart access visible.",
                    ],
                ),
                cls.section(
                    "product-hero",
                    "Create a memorable storefront and lead into shopping.",
                    cls.hero_composition(
                        profile,
                        "product",
                    ),
                    "featured product/campaign object",
                    priority="P0",
                    notes=[
                        "The selected direction must be visible without relying on logo or color alone.",
                        "Do not use a generic SaaS hero shell.",
                    ],
                ),
                cls.section(
                    "category-discovery",
                    "Let users scan shopping entry points quickly.",
                    "editorial-category-navigation",
                    "category names + representative product/media",
                    priority="P0",
                ),
                cls.section(
                    "merchandising",
                    "Merchandise a curated set instead of a wall of equal cards.",
                    "asymmetric-merchandising-grid",
                    "one lead product + supporting products",
                    priority="P0",
                ),
                cls.section(
                    "commerce-proof",
                    "Build trust with selection philosophy, service or material evidence.",
                    "inverse-editorial-proof",
                    "real product/service evidence",
                    density="low",
                ),
            ]

        if (
            "category" in role
            or "search" in role
            or "category" in route
            or "search" in route
        ):
            return [
                cls.section(
                    "browse-context",
                    "Keep query/category context, count, sorting and filters understandable.",
                    "compact-browse-command-bar",
                    "category/query + result count",
                    priority="P0",
                    density="low",
                ),
                cls.section(
                    "browse-results",
                    "Support scanning, filtering and comparison.",
                    "filter-rail-plus-product-grid",
                    "product results",
                    priority="P0",
                    density="high",
                    mobile=[
                        "Transform persistent filters into a controlled drawer/sheet.",
                        "Keep result count and active filter count visible.",
                        "Use one or two product columns according to available width.",
                    ],
                ),
            ]

        if "product" in role or "/product/" in route:
            return [
                cls.section(
                    "product-decision",
                    "Help users evaluate and buy one product.",
                    "media-gallery-plus-purchase-panel",
                    "product media + price + variants + action",
                    priority="P0",
                    mobile=[
                        "Product identity and primary media first.",
                        "Keep price, variants and primary action close to the decision object.",
                    ],
                ),
                cls.section(
                    "product-evidence",
                    "Support the decision with specification, delivery and trust evidence.",
                    "editorial-product-evidence",
                    "specification and real evidence",
                    priority="P1",
                ),
            ]

        if "cart" in role or "checkout" in role or "cart" in route or "checkout" in route:
            return [
                cls.section(
                    "transaction",
                    "Complete the transaction with minimal visual friction.",
                    "transaction-form-plus-summary",
                    "order summary + completion action",
                    priority="P0",
                    notes=[
                        "Keep this page visually quieter than discovery pages.",
                    ],
                )
            ]

        return [
            cls.section(
                "commerce-content",
                "Serve the page-specific shopping task.",
                "commerce-content-led",
                "page-specific decision object",
                priority="P0",
            )
        ]

    @classmethod
    def corporate_sections(
        cls,
        path: str,
        page_role: str,
        profile: str,
    ) -> list[SectionSpec]:
        role = (
            page_role
            + " "
            + path
        ).lower()

        if path == "/" or "home" in role:
            return [
                cls.section(
                    "corporate-header",
                    "Orient users around company, offering and proof.",
                    "quiet-global-header",
                    "brand + primary navigation + high-value CTA",
                    priority="P0",
                    density="low",
                ),
                cls.section(
                    "corporate-hero",
                    "State the business value and establish a distinctive first impression.",
                    cls.hero_composition(
                        profile,
                        "evidence",
                    ),
                    "primary business evidence or domain artifact",
                    priority="P0",
                    notes=[
                        "Use a real proof object, domain artifact, project or system visual as the anchor.",
                        "Do not default to generic abstract technology decoration.",
                    ],
                ),
                cls.section(
                    "credibility-rail",
                    "Establish scale and trust early without a meaningless logo wall.",
                    "metric-and-client-evidence-rail",
                    "metrics + named evidence",
                    priority="P0",
                    density="low",
                ),
                cls.section(
                    "capability-map",
                    "Explain the offering as a system of capabilities, not equal cards.",
                    "capability-map-with-featured-path",
                    "primary capability + supporting relationships",
                    priority="P0",
                ),
                cls.section(
                    "proof-story",
                    "Show a real outcome, project or customer transformation.",
                    "editorial-case-study-story",
                    "case-study media + outcome",
                    priority="P0",
                ),
                cls.section(
                    "executive-cta",
                    "Convert high-intent visitors with a clear next action.",
                    "focused-conversion-band",
                    "single next step",
                    density="low",
                ),
            ]

        if any(
            token in role
            for token in (
                "service",
                "solution",
                "capability",
                "offering",
                "product",
            )
        ):
            return [
                cls.section(
                    "offering-intro",
                    "Frame the problem, outcome and offer before details.",
                    cls.hero_composition(
                        profile,
                        "capability",
                    ),
                    "customer problem + outcome evidence",
                    priority="P0",
                ),
                cls.section(
                    "offering-architecture",
                    "Explain how the capability works and how parts relate.",
                    "system-diagram-plus-explanation",
                    "capability architecture",
                    priority="P0",
                ),
                cls.section(
                    "offering-proof",
                    "Prove delivery with projects, metrics or technical evidence.",
                    "proof-led-case-module",
                    "project/customer evidence",
                    priority="P0",
                ),
            ]

        if any(
            token in role
            for token in (
                "case",
                "project",
                "customer",
                "evidence",
            )
        ):
            return [
                cls.section(
                    "case-study-hero",
                    "Make the outcome and context clear immediately.",
                    cls.hero_composition(
                        profile,
                        "case-study",
                    ),
                    "project/customer artifact + outcome",
                    priority="P0",
                ),
                cls.section(
                    "challenge-response",
                    "Explain challenge, response and delivered system.",
                    "editorial-before-after-narrative",
                    "challenge + response evidence",
                    priority="P0",
                ),
                cls.section(
                    "outcomes",
                    "Close the proof loop with measurable or concrete outcomes.",
                    "outcome-metric-composition",
                    "verified results",
                    priority="P0",
                ),
            ]

        if "contact" in role:
            return [
                cls.section(
                    "contact-conversion",
                    "Reduce friction for a high-intent business inquiry.",
                    "focused-contact-split",
                    "contact path + short proof",
                    priority="P0",
                )
            ]

        return [
            cls.section(
                "corporate-content",
                "Serve the page-specific corporate decision.",
                "editorial-content-led",
                "page-specific evidence",
                priority="P0",
            ),
            cls.section(
                "supporting-proof",
                "Reinforce credibility without repeating the homepage.",
                "contextual-proof-band",
                "relevant proof",
            ),
        ]

    @classmethod
    def education_sections(
        cls,
        path: str,
        page_role: str,
        profile: str,
    ) -> list[SectionSpec]:
        role = (
            page_role
            + " "
            + path
        ).lower()

        if path == "/" or "home" in role:
            return [
                cls.section(
                    "school-header",
                    "Serve parent/student orientation and admissions access.",
                    "program-aware-global-header",
                    "brand + program navigation + admissions CTA",
                    priority="P0",
                    density="low",
                ),
                cls.section(
                    "school-hero",
                    "Create emotional relevance while making the school's promise concrete.",
                    cls.hero_composition(
                        profile,
                        "learning",
                    ),
                    "real campus/student/learning evidence",
                    priority="P0",
                ),
                cls.section(
                    "program-pathways",
                    "Help families understand age/program entry points quickly.",
                    "journey-pathway-composition",
                    "program stages + next-step cues",
                    priority="P0",
                ),
                cls.section(
                    "learning-model",
                    "Explain what learning actually feels like and how it differs.",
                    "learning-model-story-plus-diagram",
                    "curriculum/learning evidence",
                    priority="P0",
                ),
                cls.section(
                    "campus-proof",
                    "Make facilities, people and culture tangible.",
                    "immersive-campus-proof",
                    "authentic campus media",
                    priority="P0",
                ),
                cls.section(
                    "outcomes-admissions",
                    "Connect outcomes and trust to a clear inquiry/application path.",
                    "outcomes-plus-admissions-cta",
                    "student outcomes + inquiry CTA",
                    priority="P0",
                ),
            ]

        if any(
            token in role
            for token in (
                "admission",
                "enrol",
                "apply",
                "tuyển sinh",
            )
        ):
            return [
                cls.section(
                    "admissions-intro",
                    "Explain fit, process and next step without ambiguity.",
                    "admissions-command-center",
                    "application journey",
                    priority="P0",
                ),
                cls.section(
                    "admissions-steps",
                    "Make the admissions process and requirements scannable.",
                    "stepwise-process-with-evidence",
                    "process + requirements",
                    priority="P0",
                ),
                cls.section(
                    "inquiry-action",
                    "Provide a focused inquiry or application action.",
                    "focused-form-conversion",
                    "form/action",
                    priority="P0",
                ),
            ]

        if any(
            token in role
            for token in (
                "program",
                "curriculum",
                "learning",
                "academic",
            )
        ):
            return [
                cls.section(
                    "program-hero",
                    "Frame the learner, pathway and educational outcome.",
                    cls.hero_composition(
                        profile,
                        "program",
                    ),
                    "student work / curriculum evidence",
                    priority="P0",
                ),
                cls.section(
                    "curriculum-map",
                    "Explain subjects, competencies and progression as a system.",
                    "curriculum-pathway-map",
                    "curriculum structure",
                    priority="P0",
                ),
                cls.section(
                    "learning-evidence",
                    "Show real projects, classrooms, labs or student outcomes.",
                    "evidence-led-learning-gallery",
                    "real learning evidence",
                    priority="P0",
                ),
            ]

        return [
            cls.section(
                "education-content",
                "Serve the primary family/student information task.",
                "education-editorial-content",
                "page-specific learning/campus evidence",
                priority="P0",
            ),
            cls.section(
                "next-step",
                "Keep the relevant admissions or discovery path reachable.",
                "contextual-next-step-band",
                "next action",
            ),
        ]

    @classmethod
    def agency_sections(
        cls,
        path: str,
        page_role: str,
        profile: str,
    ) -> list[SectionSpec]:
        role = (
            page_role
            + " "
            + path
        ).lower()

        if path == "/" or "home" in role:
            return [
                cls.section(
                    "agency-header",
                    "Keep navigation quiet so the work remains dominant.",
                    "minimal-global-header",
                    "brand + work/services/contact",
                    priority="P0",
                    density="low",
                ),
                cls.section(
                    "agency-hero",
                    "State a point of view and immediately prove it through work.",
                    cls.hero_composition(
                        profile,
                        "work",
                    ),
                    "signature case-study media / creative artifact",
                    priority="P0",
                    notes=[
                        "The portfolio or proof should carry more visual weight than service claims.",
                    ],
                ),
                cls.section(
                    "selected-work",
                    "Show a small number of projects with different composition rhythms.",
                    "variable-case-study-sequence",
                    "large project media + outcome",
                    priority="P0",
                ),
                cls.section(
                    "capability-positioning",
                    "Explain capabilities as a strategic system, not a card menu.",
                    "capability-editorial-map",
                    "capability relationships",
                    priority="P0",
                ),
                cls.section(
                    "proof-and-point-of-view",
                    "Combine outcomes, methods and a strong opinion about the work.",
                    "proof-plus-manifesto",
                    "outcome + point of view",
                ),
                cls.section(
                    "contact-cta",
                    "Invite the right client conversation with minimal friction.",
                    "large-editorial-contact-cta",
                    "single conversation CTA",
                    density="low",
                ),
            ]

        if any(
            token in role
            for token in (
                "work",
                "case",
                "project",
                "portfolio",
            )
        ):
            return [
                cls.section(
                    "project-hero",
                    "Lead with the project object and outcome, not agency boilerplate.",
                    cls.hero_composition(
                        profile,
                        "project",
                    ),
                    "project media + result",
                    priority="P0",
                ),
                cls.section(
                    "project-story",
                    "Explain challenge, idea, execution and outcome with changing visual rhythm.",
                    "chaptered-case-study-story",
                    "project artifacts",
                    priority="P0",
                ),
                cls.section(
                    "project-outcomes",
                    "Close with credible outcomes and contribution.",
                    "result-led-proof",
                    "outcome evidence",
                    priority="P0",
                ),
            ]

        if any(
            token in role
            for token in (
                "service",
                "capability",
            )
        ):
            return [
                cls.section(
                    "capability-intro",
                    "Frame the capability through the client problem and desired change.",
                    cls.hero_composition(
                        profile,
                        "capability",
                    ),
                    "client problem + proof",
                    priority="P0",
                ),
                cls.section(
                    "capability-system",
                    "Show how disciplines combine around outcomes.",
                    "interlocking-capability-system",
                    "discipline relationships",
                    priority="P0",
                ),
                cls.section(
                    "relevant-work",
                    "Prove the capability through selected projects.",
                    "project-proof-sequence",
                    "relevant work",
                    priority="P0",
                ),
            ]

        return [
            cls.section(
                "agency-content",
                "Serve the page-specific proof or information task.",
                "agency-editorial-content",
                "work/proof object",
                priority="P0",
            ),
            cls.section(
                "agency-next-step",
                "Connect the page to relevant work or contact.",
                "contextual-editorial-cta",
                "next action",
            ),
        ]

    @classmethod
    def generic_sections(
        cls,
        path: str,
        page_role: str,
        profile: str,
    ) -> list[SectionSpec]:
        if path == "/" or "home" in page_role.lower():
            return [
                cls.section(
                    "purpose-hero",
                    "Establish value and the primary page task.",
                    cls.hero_composition(
                        profile,
                        "purpose",
                    ),
                    "primary evidence object",
                    priority="P0",
                ),
                cls.section(
                    "primary-paths",
                    "Expose the main journeys without equal-card monotony.",
                    "hierarchical-pathway-composition",
                    "top tasks",
                    priority="P0",
                ),
                cls.section(
                    "proof",
                    "Support the proposition with credible evidence.",
                    "editorial-proof-composition",
                    "real evidence",
                    priority="P0",
                ),
            ]

        return [
            cls.section(
                "purpose-content",
                "Serve the page role with a page-specific composition.",
                "content-led",
                "page-specific decision object",
                priority="P0",
            )
        ]

    @classmethod
    def sections_for(
        cls,
        domain: str,
        path: str,
        page_role: str,
        profile: str,
    ) -> list[SectionSpec]:
        normalized = domain.lower()

        if "ecommerce" in normalized or "commerce" in normalized:
            return cls.ecommerce_sections(
                path,
                page_role,
                profile,
            )

        if "education" in normalized or "school" in normalized:
            return cls.education_sections(
                path,
                page_role,
                profile,
            )

        if "agency" in normalized or "studio" in normalized:
            return cls.agency_sections(
                path,
                page_role,
                profile,
            )

        if any(
            token in normalized
            for token in (
                "corporate",
                "company",
                "b2b",
                "technology",
                "enterprise",
            )
        ):
            return cls.corporate_sections(
                path,
                page_role,
                profile,
            )

        return cls.generic_sections(
            path,
            page_role,
            profile,
        )

    @staticmethod
    def principles(
        domain: str,
        profile: str,
    ) -> list[str]:
        baseline = [
            "The selected art direction must be recognizable without the logo.",
            "Page purpose and evidence determine composition before decorative components.",
            "Do not convert every section into centered heading plus equal rounded cards.",
            "Typography, spacing, media and layout carry hierarchy together.",
            "Mobile is a deliberate transformation, not a squeezed desktop layout.",
        ]

        if "ecommerce" in domain.lower():
            baseline.append(
                "Discovery may be expressive; transaction surfaces remain quieter and faster."
            )
        elif "education" in domain.lower():
            baseline.append(
                "Real learning, campus and student evidence must dominate generic institutional decoration."
            )
        elif "agency" in domain.lower():
            baseline.append(
                "The work and outcomes must carry more visual weight than service claims."
            )
        else:
            baseline.append(
                "Credibility comes from proof, outcomes and domain artifacts rather than generic technology decoration."
            )

        baseline.append(
            f"Direction profile: {profile}."
        )

        return baseline

    async def run(
        self,
        instruction: str,
    ) -> str:
        payload = json.loads(
            instruction
        )

        contract = DesignContract.model_validate_json(
            payload.get(
                "design_contract_content",
                "",
            )
        )

        design_system = DesignSystemContract.model_validate_json(
            payload.get(
                "design_system_content",
                "",
            )
        )

        plan = ImplementationPlan.model_validate_json(
            payload.get(
                "implementation_plan_content",
                "",
            )
        )

        profile = self.direction_profile(
            contract.project.goal
        )

        pages: list[PageSpec] = []

        for route in plan.routes:
            sections = self.sections_for(
                contract.project.domain,
                route.path,
                route.page_role,
                profile,
            )

            pages.append(
                PageSpec(
                    path=route.path,
                    page_role=route.page_role,
                    composition_family=(
                        route.composition_family
                    ),
                    first_visual_anchor=(
                        sections[0].visual_anchor
                        if sections
                        else "UNKNOWN"
                    ),
                    sections=sections,
                    anti_monotony_rules=[
                        "Do not reuse one hero shell across materially different page roles.",
                        "Do not convert every section into centered heading plus equal cards.",
                        "Preserve the selected direction through typography, composition and media role.",
                        "Keep decision-critical content visually stronger than decoration.",
                    ],
                )
            )

        families = {
            page.composition_family
            for page in pages
        }

        mobile_defined = all(
            all(
                bool(section.mobile_behavior)
                for section in page.sections
            )
            for page in pages
        )

        anchors_defined = all(
            page.first_visual_anchor
            and page.first_visual_anchor
            != "UNKNOWN"
            for page in pages
        )

        required_family_count = min(
            3,
            max(
                1,
                len(pages),
            ),
        )

        families_diverse = (
            len(families)
            >= required_family_count
        )

        composition = VisualComposition(
            status="provisional",
            domain=contract.project.domain,
            project_slug=plan.project_slug,
            visual_signature=(
                contract.visual.signature
                or (
                    "Purpose-led website with page-specific composition "
                    "and one recognizable visual signature."
                )
            ),
            composition_principles=(
                self.principles(
                    contract.project.domain,
                    profile,
                )
            ),
            pages=pages,
            unresolved_items=list(
                design_system.unresolved_items
            ),
            gates=VisualCompositionGate(
                page_roles_mapped=bool(
                    pages
                ),
                composition_families_diverse=(
                    families_diverse
                ),
                mobile_transformations_defined=(
                    mobile_defined
                ),
                visual_anchors_defined=(
                    anchors_defined
                ),
                ready_for_frontend_engineer=(
                    bool(pages)
                    and families_diverse
                    and mobile_defined
                    and anchors_defined
                ),
            ),
            generated_by=(
                "VisualComposerV2"
            ),
        )

        if design_system.brand.personality:
            composition.composition_principles.append("Brand personality: " + ", ".join(design_system.brand.personality))
        for page in composition.pages:
            page.anti_monotony_rules.extend("Brand constraint: " + rule for rule in design_system.brand.avoid)
        composition.composition_principles.extend(design_system.brand.reference_patterns)

        return composition.model_dump_json(
            indent=2
        )
