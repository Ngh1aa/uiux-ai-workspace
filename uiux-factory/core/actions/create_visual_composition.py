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


class CreateVisualComposition(Action):
    name: str = "CreateVisualComposition"

    desc: str = (
        "Convert page roles and visual direction into page-specific "
        "composition specifications before frontend implementation."
    )

    @staticmethod
    def home_sections() -> list[SectionSpec]:
        return [
            SectionSpec(
                type="commerce-header",
                purpose="Global orientation and shopping entry.",
                priority="P0",
                composition="three-zone-header",
                visual_anchor="brand + product navigation + cart",
                density="low",
                mobile_behavior=[
                    "Collapse secondary navigation.",
                    "Keep brand and cart/search access visible.",
                ],
            ),
            SectionSpec(
                type="editorial-product-hero",
                purpose="Create a memorable first impression and lead into shopping.",
                priority="P0",
                composition="editorial-copy-plus-product-stage",
                visual_anchor="featured product object",
                density="medium",
                mobile_behavior=[
                    "Copy first, product visual second.",
                    "Keep the primary CTA visible early.",
                    "Reduce display scale without breaking heading rhythm.",
                ],
                notes=[
                    "Do not use a generic black rectangle with placeholder text.",
                    "Visual object must feel product-led, not SaaS/dashboard-led.",
                ],
            ),
            SectionSpec(
                type="category-navigation",
                purpose="Provide fast product discovery.",
                priority="P0",
                composition="horizontal-category-strip",
                visual_anchor="category labels",
                density="medium",
                mobile_behavior=[
                    "Wrap or horizontally scroll without hiding labels.",
                ],
            ),
            SectionSpec(
                type="featured-products",
                purpose="Merchandise a small curated product set.",
                priority="P0",
                composition="asymmetric-product-grid",
                visual_anchor="large lead product + two supporting products",
                density="medium",
                mobile_behavior=[
                    "Stack lead product first.",
                    "Keep product name and price visible.",
                ],
            ),
            SectionSpec(
                type="brand-proof",
                purpose="Explain selection philosophy and build trust.",
                priority="P1",
                composition="inverse-editorial-story",
                visual_anchor="signature abstract product/material motif",
                density="low",
                mobile_behavior=[
                    "Stack copy before visual.",
                ],
            ),
        ]

    @staticmethod
    def browse_sections() -> list[SectionSpec]:
        return [
            SectionSpec(
                type="browse-header",
                purpose="Establish category/search context and result count.",
                priority="P0",
                composition="compact-context-header",
                visual_anchor="category title + count/sort state",
                density="low",
                mobile_behavior=[
                    "Keep title and result count visible.",
                ],
            ),
            SectionSpec(
                type="browse-results",
                purpose="Support filtering and comparison.",
                priority="P0",
                composition="filter-rail-plus-dense-product-grid",
                visual_anchor="product results",
                density="high",
                mobile_behavior=[
                    "Transform filter rail into drawer.",
                    "Preserve active filter count.",
                    "Use one or two product columns on small viewports.",
                ],
            ),
        ]

    @staticmethod
    def product_sections() -> list[SectionSpec]:
        return [
            SectionSpec(
                type="product-decision",
                purpose="Help the user evaluate and purchase one product.",
                priority="P0",
                composition="media-gallery-plus-purchase-panel",
                visual_anchor="product media",
                density="medium",
                mobile_behavior=[
                    "Media first.",
                    "Keep price, variants and action close to product identity.",
                    "Use sticky purchase action only when validated.",
                ],
            ),
            SectionSpec(
                type="product-evidence",
                purpose="Support the decision with specs, delivery and trust.",
                priority="P1",
                composition="editorial-specification-sections",
                visual_anchor="specification and evidence",
                density="medium",
                mobile_behavior=[
                    "Stack evidence into readable blocks.",
                ],
            ),
        ]

    @staticmethod
    def transaction_sections(role: str) -> list[SectionSpec]:
        return [
            SectionSpec(
                type=role,
                purpose="Complete the transaction with minimal friction.",
                priority="P0",
                composition="transaction-form-plus-summary",
                visual_anchor="order summary and completion action",
                density="medium",
                mobile_behavior=[
                    "Stack form and summary.",
                    "Keep totals and primary action understandable.",
                ],
                notes=[
                    "Reduce decorative effects compared with discovery pages.",
                ],
            ),
        ]

    @classmethod
    def sections_for(
        cls,
        path: str,
        page_role: str,
    ) -> list[SectionSpec]:
        role = page_role.lower()
        route = path.lower()

        if path == "/" or "home" in role:
            return cls.home_sections()

        if (
            "category" in role
            or "search" in role
            or "category" in route
            or "search" in route
        ):
            return cls.browse_sections()

        if "product" in role or "/product/" in route:
            return cls.product_sections()

        if "checkout" in role or "checkout" in route:
            return cls.transaction_sections("checkout")

        if "cart" in role or "cart" in route:
            return cls.transaction_sections("cart")

        return [
            SectionSpec(
                type="content",
                purpose="Serve the primary page task.",
                priority="P0",
                composition="content-led",
                visual_anchor="page-specific decision object",
                density="medium",
                mobile_behavior=[
                    "Stack content according to reading priority.",
                ],
            )
        ]

    async def run(
        self,
        instruction: str,
    ) -> str:
        payload = json.loads(instruction)

        contract = DesignContract.model_validate_json(
            payload.get("design_contract_content", "")
        )

        design_system = DesignSystemContract.model_validate_json(
            payload.get("design_system_content", "")
        )

        plan = ImplementationPlan.model_validate_json(
            payload.get("implementation_plan_content", "")
        )

        pages = []

        for route in plan.routes:
            sections = self.sections_for(
                route.path,
                route.page_role,
            )

            pages.append(
                PageSpec(
                    path=route.path,
                    page_role=route.page_role,
                    composition_family=route.composition_family,
                    first_visual_anchor=(
                        sections[0].visual_anchor
                        if sections
                        else "UNKNOWN"
                    ),
                    sections=sections,
                    anti_monotony_rules=[
                        "Do not reuse one hero shell across materially different page roles.",
                        "Do not convert every section into centered heading plus three cards.",
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
            and page.first_visual_anchor != "UNKNOWN"
            for page in pages
        )

        visual_signature = (
            contract.visual.signature
            or (
                "Product-first commerce interface with deliberate "
                "brand wayfinding and page-specific composition."
            )
        )

        composition = VisualComposition(
            status="provisional",
            domain=contract.project.domain,
            project_slug=plan.project_slug,
            visual_signature=visual_signature,
            composition_principles=[
                "Product and evidence objects lead decoration.",
                "Discovery pages may be expressive; transaction pages remain quieter.",
                "Typography, spacing and composition create hierarchy together.",
                "Brand color is a role, not wallpaper.",
                "Mobile transformations are explicit design decisions.",
            ],
            pages=pages,
            unresolved_items=list(
                design_system.unresolved_items
            ),
            gates=VisualCompositionGate(
                page_roles_mapped=bool(pages),
                composition_families_diverse=(
                    len(families) >= 3
                ),
                mobile_transformations_defined=mobile_defined,
                visual_anchors_defined=anchors_defined,
                ready_for_frontend_engineer=(
                    bool(pages)
                    and len(families) >= 3
                    and mobile_defined
                    and anchors_defined
                ),
            ),
        )

        return composition.model_dump_json(
            indent=2
        )
