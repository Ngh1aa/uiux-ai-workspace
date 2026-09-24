import json
import re

from metagpt.actions import Action

from core.contracts.design_system_schema import DesignSystemContract
from core.contracts.implementation_plan_schema import (
    ComponentPlan,
    FilePlan,
    ImplementationGate,
    ImplementationPlan,
    RoutePlan,
)
from core.contracts.schema import DesignContract


class CreateImplementationPlan(Action):
    name: str = "CreateImplementationPlan"

    desc: str = (
        "Create a deterministic frontend implementation plan from "
        "the canonical Design Contract and Design System."
    )

    @staticmethod
    def slugify(value: str) -> str:
        text = value.lower().strip()
        text = re.sub(r"[^a-z0-9]+", "-", text)
        text = re.sub(r"-+", "-", text).strip("-")
        return text or "generated-site"

    @staticmethod
    def route_for_page(name: str) -> str:
        key = name.lower().strip()

        mapping = {
            "home": "/",
            "homepage": "/",
            "category": "/category",
            "search": "/search",
            "product detail": "/product/[slug]",
            "product": "/product/[slug]",
            "cart": "/cart",
            "checkout": "/checkout",
            "contact": "/contact",
        }

        if key in mapping:
            return mapping[key]

        slug = re.sub(r"[^a-z0-9]+", "-", key).strip("-")
        return "/" + (slug or "page")

    @staticmethod
    def composition_for_page(name: str) -> str:
        key = name.lower()

        if "home" in key:
            return "discovery-editorial"

        if "category" in key or "search" in key:
            return "browse-utility"

        if "product" in key:
            return "product-decision"

        if "cart" in key or "checkout" in key:
            return "transactional"

        if "contact" in key:
            return "conversion-focused"

        return "content-led"

    @staticmethod
    def components_for_page(name: str, domain: str) -> list[str]:
        key = name.lower()

        common = ["Header", "Button", "TextLink"]

        if domain != "ecommerce":
            return common

        if "home" in key:
            return common + ["SearchInput", "ProductCard"]

        if "category" in key:
            return common + ["FilterControl", "ProductCard"]

        if "search" in key:
            return common + ["SearchInput", "FilterControl", "ProductCard"]

        if "product" in key:
            return common + ["ProductGallery", "AddToCart"]

        if "cart" in key:
            return common + ["CartLineItem", "OrderSummary"]

        if "checkout" in key:
            return common + ["Input", "OrderSummary"]

        return common

    @staticmethod
    def data_needs_for_page(name: str, domain: str) -> list[str]:
        if domain != "ecommerce":
            return ["page_content"]

        key = name.lower()

        if "home" in key:
            return [
                "featured_categories",
                "featured_products",
                "campaign_content",
            ]

        if "category" in key:
            return [
                "category",
                "products",
                "filters",
                "sort_options",
            ]

        if "search" in key:
            return [
                "query",
                "search_results",
                "filters",
                "sort_options",
            ]

        if "product" in key:
            return [
                "product",
                "media",
                "variants",
                "price",
                "availability",
                "delivery_info",
            ]

        if "cart" in key:
            return [
                "cart_items",
                "pricing_summary",
            ]

        if "checkout" in key:
            return [
                "checkout_form",
                "order_summary",
                "shipping_options",
            ]

        return ["page_content"]

    async def run(self, instruction: str) -> str:
        payload = json.loads(instruction)

        design_contract_path = payload.get(
            "design_contract_path",
            "",
        )

        design_system_path = payload.get(
            "design_system_path",
            "",
        )

        design_contract_content = payload.get(
            "design_contract_content",
            "",
        )

        design_system_content = payload.get(
            "design_system_content",
            "",
        )

        if not design_contract_content:
            raise ValueError(
                "design_contract_content is required."
            )

        if not design_system_content:
            raise ValueError(
                "design_system_content is required."
            )

        contract = DesignContract.model_validate_json(
            design_contract_content
        )

        design_system = (
            DesignSystemContract.model_validate_json(
                design_system_content
            )
        )

        domain = contract.project.domain

        goal = contract.project.goal

        if "ecommerce" in domain.lower():
            project_slug = "ecommerce-purple"
        else:
            project_slug = self.slugify(goal)[:48]

        output_dir = f"generated/{project_slug}"

        routes = []

        for index, page_role in enumerate(
            contract.ux.page_roles
        ):
            name = page_role.name

            route = RoutePlan(
                path=self.route_for_page(name),
                page_role=name,
                priority="P0" if index < 6 else "P1",
                composition_family=(
                    self.composition_for_page(name)
                ),
                primary_components=(
                    self.components_for_page(
                        name,
                        domain,
                    )
                ),
                data_needs=(
                    self.data_needs_for_page(
                        name,
                        domain,
                    )
                ),
                notes=[
                    page_role.role,
                    (
                        "Preserve page-role composition diversity "
                        "from Design Contract."
                    ),
                ],
            )

            routes.append(route)

        if not routes and domain == "ecommerce":
            fallback_pages = [
                "Home",
                "Category",
                "Search",
                "Product Detail",
                "Cart",
                "Checkout",
            ]

            for index, name in enumerate(
                fallback_pages
            ):
                routes.append(
                    RoutePlan(
                        path=self.route_for_page(name),
                        page_role=name,
                        priority="P0",
                        composition_family=(
                            self.composition_for_page(name)
                        ),
                        primary_components=(
                            self.components_for_page(
                                name,
                                domain,
                            )
                        ),
                        data_needs=(
                            self.data_needs_for_page(
                                name,
                                domain,
                            )
                        ),
                        notes=[
                            (
                                "Fallback page role because "
                                "UX page-role extraction was empty."
                            )
                        ],
                    )
                )

        component_plans = []

        for component in design_system.components:
            component_plans.append(
                ComponentPlan(
                    name=component.name,
                    source_contract=component.name,
                    priority=component.priority,
                    implementation_path=(
                        "src/components/ui/"
                        + self.slugify(component.name)
                        + ".tsx"
                    ),
                    dependencies=[],
                )
            )

        token_mapping = {
            "design-system.foundations.colors":
                "src/styles/tokens.css",
            "design-system.foundations.typography":
                "src/styles/tokens.css",
            "design-system.foundations.spacing":
                "src/styles/tokens.css",
            "design-system.foundations.radius":
                "src/styles/tokens.css",
            "design-system.foundations.motion":
                "src/styles/tokens.css",
            "design-system.semantic_colors":
                "src/styles/tokens.css",
        }

        files = [
            FilePlan(
                path="package.json",
                purpose="Frontend package manifest.",
            ),
            FilePlan(
                path="src/app/layout.tsx",
                purpose="Root layout and global shell.",
            ),
            FilePlan(
                path="src/app/page.tsx",
                purpose="Home route.",
            ),
            FilePlan(
                path="src/styles/tokens.css",
                purpose=(
                    "Generated token bridge from design-system.json."
                ),
            ),
            FilePlan(
                path="src/app/globals.css",
                purpose="Global resets and shared page rules.",
            ),
            FilePlan(
                path="src/lib/mock-data.ts",
                purpose=(
                    "Deterministic placeholder content until "
                    "real CMS/API data is connected."
                ),
            ),
        ]

        implementation_order = [
            "Scaffold Next.js project",
            "Generate token bridge",
            "Implement P0 primitives",
            "Implement global Header",
            "Implement Home composition",
            "Implement Category and Search",
            "Implement Product Detail",
            "Implement Cart and Checkout",
            "Run TypeScript/build checks",
            "Hand off to Browser QA",
        ]

        unresolved = list(
            design_system.unresolved_items
        )

        plan = ImplementationPlan(
            status="provisional",
            source_design_contract_path=(
                design_contract_path
            ),
            source_design_system_path=(
                design_system_path
            ),
            project_slug=project_slug,
            output_dir=output_dir,
            routes=routes,
            components=component_plans,
            token_mapping=token_mapping,
            files=files,
            implementation_order=implementation_order,
            unresolved_items=unresolved,
            gates=ImplementationGate(
                routes_defined=bool(routes),
                component_mapping_defined=bool(
                    component_plans
                ),
                token_mapping_defined=True,
                implementation_order_defined=True,
                ready_for_frontend_engineer=bool(
                    routes and component_plans
                ),
            ),
        )

        return plan.model_dump_json(
            indent=2
        )
