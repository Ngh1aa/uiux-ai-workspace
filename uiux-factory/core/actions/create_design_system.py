import hashlib
import json

from metagpt.actions import Action

from core.contracts.design_system_schema import (
    ComponentContract,
    DesignSystemContract,
    DesignSystemGate,
    FoundationTokens,
    PatternContract,
    TokenValue,
)
from core.contracts.schema import DesignContract
from core.skills.loader import SkillLoader


class CreateDesignSystem(Action):
    name: str = "CreateDesignSystem"

    desc: str = (
        "Convert the canonical Design Contract into reusable "
        "tokens, component contracts and composition patterns."
    )

    @staticmethod
    def sha256_text(content: str) -> str:
        return hashlib.sha256(
            content.encode("utf-8")
        ).hexdigest()

    @staticmethod
    def token(
        value,
        status: str,
        source: str,
    ) -> TokenValue:
        return TokenValue(
            value=value,
            status=status,
            source=source,
        )

    @classmethod
    def build_foundations(
        cls,
        contract: DesignContract,
    ) -> FoundationTokens:
        requested_color = (
            contract.project.requested_primary_color
            or "UNKNOWN"
        )

        colors = {
            "color.brand.family": cls.token(
                requested_color,
                "confirmed"
                if requested_color != "UNKNOWN"
                else "unresolved",
                "design-contract.project.requested_primary_color",
            ),
            "color.brand.primary": cls.token(
                None,
                "unresolved",
                "Exact brand HEX/token has not been supplied.",
            ),
            "color.neutral.0": cls.token(
                "#FFFFFF",
                "factory_default",
                "UIUX Factory neutral fallback",
            ),
            "color.neutral.50": cls.token(
                "#F7F7FA",
                "factory_default",
                "UIUX Factory neutral fallback",
            ),
            "color.neutral.200": cls.token(
                "#E8E8EE",
                "factory_default",
                "UIUX Factory neutral fallback",
            ),
            "color.neutral.600": cls.token(
                "#666672",
                "factory_default",
                "UIUX Factory neutral fallback",
            ),
            "color.neutral.950": cls.token(
                "#111116",
                "factory_default",
                "UIUX Factory neutral fallback",
            ),
            "color.state.success": cls.token(
                "#168A4A",
                "factory_default",
                "Semantic fallback; verify contrast in rendered UI.",
            ),
            "color.state.warning": cls.token(
                "#A66300",
                "factory_default",
                "Semantic fallback; verify contrast in rendered UI.",
            ),
            "color.state.danger": cls.token(
                "#C83232",
                "factory_default",
                "Semantic fallback; verify contrast in rendered UI.",
            ),
        }

        semantic_colors = {
            "surface.page": "color.neutral.0",
            "surface.subtle": "color.neutral.50",
            "surface.inverse": "color.neutral.950",
            "text.primary": "color.neutral.950",
            "text.muted": "color.neutral.600",
            "text.on-inverse": "color.neutral.0",
            "border.default": "color.neutral.200",
            "action.primary": "color.brand.primary",
            "state.success": "color.state.success",
            "state.warning": "color.state.warning",
            "state.danger": "color.state.danger",
        }

        typography = {
            "font.family.body": cls.token(
                None,
                "unresolved",
                "Final font family has not been selected.",
            ),
            "font.family.display": cls.token(
                None,
                "unresolved",
                "Use body family unless a justified display family is selected.",
            ),
            "font.size.meta": cls.token(
                "0.75rem",
                "factory_default",
                "UIUX Factory type fallback",
            ),
            "font.size.body-sm": cls.token(
                "0.875rem",
                "factory_default",
                "UIUX Factory type fallback",
            ),
            "font.size.body": cls.token(
                "1rem",
                "factory_default",
                "UIUX Factory type fallback",
            ),
            "font.size.h3": cls.token(
                "1.25rem",
                "factory_default",
                "UIUX Factory type fallback",
            ),
            "font.size.h2": cls.token(
                "clamp(1.75rem, 3vw, 2.5rem)",
                "factory_default",
                "Responsive type fallback",
            ),
            "font.size.h1": cls.token(
                "clamp(2.25rem, 5vw, 4.5rem)",
                "factory_default",
                "Responsive type fallback",
            ),
            "font.line.body": cls.token(
                "1.6",
                "factory_default",
                "Readable body fallback",
            ),
            "font.line.heading": cls.token(
                "1.08",
                "factory_default",
                "Heading fallback",
            ),
        }

        spacing_values = {
            "space.0": "0",
            "space.1": "0.25rem",
            "space.2": "0.5rem",
            "space.3": "0.75rem",
            "space.4": "1rem",
            "space.6": "1.5rem",
            "space.8": "2rem",
            "space.12": "3rem",
            "space.16": "4rem",
            "space.24": "6rem",
            "space.32": "8rem",
        }

        spacing = {
            name: cls.token(
                value,
                "factory_default",
                "UIUX Factory 4px-based spacing fallback",
            )
            for name, value in spacing_values.items()
        }

        radius_values = {
            "radius.none": "0",
            "radius.sm": "0.375rem",
            "radius.md": "0.625rem",
            "radius.lg": "0.875rem",
            "radius.pill": "9999px",
        }

        radius = {
            name: cls.token(
                value,
                "factory_default",
                "Restrained radius fallback; pill only when semantics require it.",
            )
            for name, value in radius_values.items()
        }

        border = {
            "border.width.default": cls.token(
                "1px",
                "factory_default",
                "UIUX Factory border fallback",
            ),
            "border.style.default": cls.token(
                "solid",
                "factory_default",
                "UIUX Factory border fallback",
            ),
        }

        elevation = {
            "elevation.none": cls.token(
                "none",
                "factory_default",
                "Default flat surface",
            ),
            "elevation.overlay": cls.token(
                "0 12px 40px rgba(17, 17, 22, 0.12)",
                "factory_default",
                "Use only for overlays / floating hierarchy.",
            ),
        }

        motion = {
            "motion.duration.fast": cls.token(
                "120ms",
                "factory_default",
                "UIUX Factory motion fallback",
            ),
            "motion.duration.base": cls.token(
                "180ms",
                "factory_default",
                "UIUX Factory motion fallback",
            ),
            "motion.duration.slow": cls.token(
                "280ms",
                "factory_default",
                "UIUX Factory motion fallback",
            ),
            "motion.easing.standard": cls.token(
                "cubic-bezier(0.2, 0, 0, 1)",
                "factory_default",
                "UIUX Factory easing fallback",
            ),
        }

        layout = {
            "layout.max.page": cls.token(
                "1440px",
                "factory_default",
                "Page canvas fallback",
            ),
            "layout.max.content": cls.token(
                "1200px",
                "factory_default",
                "Content container fallback",
            ),
            "layout.max.reading": cls.token(
                "720px",
                "factory_default",
                "Readable text measure fallback",
            ),
            "layout.gutter.mobile": cls.token(
                "16px",
                "factory_default",
                "Mobile gutter fallback",
            ),
            "layout.gutter.tablet": cls.token(
                "24px",
                "factory_default",
                "Tablet gutter fallback",
            ),
            "layout.gutter.desktop": cls.token(
                "32px",
                "factory_default",
                "Desktop gutter fallback",
            ),
        }

        return FoundationTokens(
            colors=colors,
            semantic_colors=semantic_colors,
            typography=typography,
            spacing=spacing,
            radius=radius,
            border=border,
            elevation=elevation,
            motion=motion,
            layout=layout,
        )

    @staticmethod
    def common_components() -> list[ComponentContract]:
        return [
            ComponentContract(
                name="Button",
                priority="P0",
                purpose="Primary and secondary user actions.",
                variants=[
                    "primary",
                    "secondary",
                    "ghost",
                    "danger",
                ],
                states=[
                    "default",
                    "hover",
                    "focus-visible",
                    "active",
                    "disabled",
                    "loading",
                ],
                responsive_behavior=[
                    "Minimum touch target remains usable on mobile.",
                    "Full-width is allowed only when composition requires it.",
                ],
                accessibility=[
                    "Visible focus state.",
                    "Accessible name is mandatory.",
                    "Loading state preserves understandable label/state.",
                ],
                surface_contract=[
                    "Own background, foreground, border and icon color for every state.",
                    "Never rely on accidental inherited foreground.",
                ],
            ),
            ComponentContract(
                name="TextLink",
                priority="P0",
                purpose="Inline or navigational text action.",
                variants=[
                    "default",
                    "muted",
                    "inverse",
                ],
                states=[
                    "default",
                    "hover",
                    "focus-visible",
                    "visited",
                ],
                responsive_behavior=[
                    "Do not reduce target size below practical touch usage when used as navigation.",
                ],
                accessibility=[
                    "Must remain identifiable without color alone when context is ambiguous.",
                    "Visible focus state.",
                ],
                surface_contract=[
                    "Foreground role must match page/light/inverse surface.",
                ],
            ),
            ComponentContract(
                name="Input",
                priority="P0",
                purpose="Single-line user input.",
                variants=[
                    "default",
                    "with-leading-icon",
                    "with-trailing-action",
                ],
                states=[
                    "default",
                    "hover",
                    "focus",
                    "disabled",
                    "error",
                    "success",
                ],
                responsive_behavior=[
                    "Use viewport-appropriate width without page-specific CSS patches.",
                ],
                accessibility=[
                    "Programmatic label.",
                    "Error/help text relationship.",
                    "Focus indicator.",
                ],
                surface_contract=[
                    "Own field surface, text, placeholder, border and state colors.",
                ],
            ),
            ComponentContract(
                name="Header",
                priority="P0",
                purpose="Global orientation and primary navigation.",
                variants=[
                    "default",
                    "compact",
                    "overlay-only-when-validated",
                ],
                states=[
                    "default",
                    "scrolled",
                    "mobile-open",
                ],
                responsive_behavior=[
                    "Desktop navigation transforms into deliberate mobile navigation.",
                    "Primary conversion remains reachable.",
                ],
                accessibility=[
                    "Keyboard-operable navigation.",
                    "Semantic nav landmarks.",
                    "Mobile menu controls expose expanded state.",
                ],
                surface_contract=[
                    "Light and inverse surface contexts require explicit foreground contracts.",
                ],
            ),
        ]

    @staticmethod
    def ecommerce_components() -> list[ComponentContract]:
        return [
            ComponentContract(
                name="ProductCard",
                priority="P0",
                purpose="Support product recognition, comparison and entry to detail.",
                variants=[
                    "grid",
                    "compact",
                ],
                states=[
                    "default",
                    "hover",
                    "focus-within",
                    "unavailable",
                ],
                responsive_behavior=[
                    "Image ratio and information order remain stable across breakpoints.",
                    "Do not hide decision-critical price/title information on mobile.",
                ],
                accessibility=[
                    "Product name has clear accessible destination.",
                    "Image alt follows actual media/content truth.",
                ],
                surface_contract=[
                    "Card may be flat; elevation is not required by default.",
                    "Foreground must not depend on parent section theme accidentally.",
                ],
            ),
            ComponentContract(
                name="SearchInput",
                priority="P0",
                purpose="Capture explicit product-finding intent.",
                variants=[
                    "header",
                    "page",
                ],
                states=[
                    "idle",
                    "focus",
                    "typing",
                    "loading",
                    "results",
                    "no-results",
                    "error",
                ],
                responsive_behavior=[
                    "Mobile search may become a focused full-width search experience.",
                ],
                accessibility=[
                    "Search landmark/role where appropriate.",
                    "Loading/result state announced when needed.",
                ],
                surface_contract=[
                    "Own input surface and all text/icon states.",
                ],
            ),
            ComponentContract(
                name="FilterControl",
                priority="P0",
                purpose="Refine browse/search results.",
                variants=[
                    "sidebar",
                    "toolbar",
                    "mobile-drawer-trigger",
                ],
                states=[
                    "default",
                    "selected",
                    "disabled",
                    "expanded",
                ],
                responsive_behavior=[
                    "Desktop sidebar/toolbar may transform into controlled mobile drawer.",
                    "Active filter count remains discoverable.",
                ],
                accessibility=[
                    "Selected state is programmatically exposed.",
                    "Drawer focus is managed.",
                ],
                surface_contract=[
                    "Selected state keeps text/icon contrast intact.",
                ],
            ),
            ComponentContract(
                name="ProductGallery",
                priority="P0",
                purpose="Present product media as a primary decision object.",
                variants=[
                    "grid",
                    "carousel-on-small-viewports",
                ],
                states=[
                    "default",
                    "zoom-or-expanded-when-supported",
                ],
                responsive_behavior=[
                    "Preserve focal subject and stable aspect ratio.",
                    "Mobile interaction does not hide purchase context unnecessarily.",
                ],
                accessibility=[
                    "Media controls are keyboard-operable when interactive.",
                    "Alt text is based on real content.",
                ],
                surface_contract=[
                    "Media surface does not force inherited text behavior.",
                ],
            ),
            ComponentContract(
                name="AddToCart",
                priority="P0",
                purpose="Primary product purchase action.",
                variants=[
                    "default",
                    "sticky-mobile-when-validated",
                ],
                states=[
                    "default",
                    "hover",
                    "focus-visible",
                    "loading",
                    "success",
                    "disabled",
                    "error",
                ],
                responsive_behavior=[
                    "Keep action near product decision context.",
                    "Sticky mobile behavior only when it improves completion.",
                ],
                accessibility=[
                    "State changes are understandable.",
                    "Disabled reason is available when needed.",
                ],
                surface_contract=[
                    "Own CTA background/foreground/icon for every state.",
                ],
            ),
            ComponentContract(
                name="CartLineItem",
                priority="P0",
                purpose="Review and modify one selected product.",
                variants=[
                    "default",
                    "compact",
                ],
                states=[
                    "default",
                    "updating",
                    "error",
                    "removed",
                ],
                responsive_behavior=[
                    "On mobile, product identity, price and quantity remain easy to scan.",
                ],
                accessibility=[
                    "Quantity/remove controls have clear names.",
                    "Update feedback is exposed.",
                ],
                surface_contract=[
                    "Transactional surface remains visually quiet and readable.",
                ],
            ),
            ComponentContract(
                name="OrderSummary",
                priority="P0",
                purpose="Summarize financial decision before checkout completion.",
                variants=[
                    "cart",
                    "checkout",
                ],
                states=[
                    "default",
                    "updating",
                    "error",
                ],
                responsive_behavior=[
                    "Summary remains discoverable on narrow viewports without obscuring form tasks.",
                ],
                accessibility=[
                    "Totals use semantic text structure.",
                    "Price changes are understandable.",
                ],
                surface_contract=[
                    "High-contrast summary without decorative overload.",
                ],
            ),
        ]

    @staticmethod
    def build_patterns(
        domain: str,
    ) -> list[PatternContract]:
        patterns = [
            PatternContract(
                name="PageContainer",
                purpose="Shared page alignment without forcing identical compositions.",
                rules=[
                    "Use semantic layout widths/gutters.",
                    "Allow intentional full-bleed or grid-breaking sections.",
                    "Do not use container reuse to create page-role monotony.",
                ],
            ),
            PatternContract(
                name="SectionRhythm",
                purpose="Create predictable but non-mechanical vertical rhythm.",
                rules=[
                    "Use spacing tokens rather than page-specific arbitrary gaps.",
                    "Density may differ by page role.",
                    "Do not repeat identical heading/card structure across every section.",
                ],
            ),
            PatternContract(
                name="SurfacePairing",
                purpose="Keep background/foreground semantics intact.",
                rules=[
                    "Every shared surface explicitly pairs foreground and border/icon roles.",
                    "Inverse contexts never rely on inherited colors.",
                ],
            ),
        ]

        if domain == "ecommerce":
            patterns.extend(
                [
                    PatternContract(
                        name="BrowsePattern",
                        purpose="Coordinate category context, filters and product results.",
                        rules=[
                            "Results remain the primary visual object.",
                            "Filter placement transforms intentionally on mobile.",
                            "Count/sort/filter state stays visible.",
                        ],
                    ),
                    PatternContract(
                        name="ProductDecisionPattern",
                        purpose="Coordinate product media, core information and purchase action.",
                        rules=[
                            "Media and purchase information remain spatially related.",
                            "Trust/delivery information supports rather than competes with the CTA.",
                            "Do not replace product evidence with generic decorative UI.",
                        ],
                    ),
                    PatternContract(
                        name="TransactionPattern",
                        purpose="Keep cart/checkout focused and low-friction.",
                        rules=[
                            "Reduce decorative density.",
                            "Keep totals and primary completion action clear.",
                            "Error/recovery state is part of the pattern contract.",
                        ],
                    ),
                ]
            )

        return patterns

    async def run(
        self,
        instruction: str,
    ) -> str:
        payload = json.loads(
            instruction
        )

        source_path = payload.get(
            "design_contract_path",
            "",
        )

        source_content = payload.get(
            "design_contract_content",
            "",
        )

        if not source_content:
            raise ValueError(
                "design_contract_content is required."
            )

        contract = DesignContract.model_validate_json(
            source_content
        )

        loader = SkillLoader()

        selected_skills = loader.select(
            keywords=(
                "design system",
                "component",
                "semantic token",
                "responsive",
                "accessibility",
                "state",
                "surface",
                "foreground",
            ),
            limit=8,
        )

        relevant_skills = [
            skill.relative_path
            for skill in selected_skills
        ]

        foundations = self.build_foundations(
            contract
        )

        components = self.common_components()

        if contract.project.domain == "ecommerce":
            components.extend(
                self.ecommerce_components()
            )

        patterns = self.build_patterns(
            contract.project.domain
        )

        unresolved = list(
            contract.constraints.unresolved_items
        )

        required_unresolved = [
            "Exact primary brand color token / HEX.",
            "Final body typography family with Vietnamese coverage verification.",
        ]

        for item in required_unresolved:
            if item not in unresolved:
                unresolved.append(item)

        p0_components = [
            component
            for component in components
            if component.priority == "P0"
        ]

        p0_states_defined = all(
            bool(component.states)
            for component in p0_components
        )

        responsive_defined = all(
            bool(component.responsive_behavior)
            for component in p0_components
        )

        accessibility_defined = all(
            bool(component.accessibility)
            for component in p0_components
        )

        system = DesignSystemContract(
            status="provisional",
            domain=contract.project.domain,
            source_design_contract_path=source_path,
            source_design_contract_sha256=self.sha256_text(
                source_content
            ),
            relevant_skills=relevant_skills,
            foundations=foundations,
            components=components,
            patterns=patterns,
            unresolved_items=unresolved,
            gates=DesignSystemGate(
                semantic_tokens_defined=True,
                p0_component_states_defined=p0_states_defined,
                responsive_contracts_defined=responsive_defined,
                accessibility_contracts_defined=accessibility_defined,
                implementation_ready_with_fallbacks=True,
                final_visual_lock=False,
            ),
        )

        return system.model_dump_json(
            indent=2
        )
