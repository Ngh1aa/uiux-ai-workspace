from datetime import datetime

from metagpt.actions import Action

from core.skills.loader import SkillLoader


class CreateArtDirection(Action):
    name: str = "CreateArtDirection"

    desc: str = (
        "Transform UX/IA into a provisional visual direction "
        "with implementable visual grammar."
    )

    @staticmethod
    def parse_input(
        instruction: str,
    ) -> tuple[str, str, str]:
        goal = ""
        research = ""
        ux_ia = ""

        if "## GOAL" in instruction:
            content = instruction.split(
                "## GOAL",
                1,
            )[1]

            if "## RESEARCH" in content:
                goal, content = content.split(
                    "## RESEARCH",
                    1,
                )
            else:
                goal = content
                content = ""

            if "## UX_IA" in content:
                research, ux_ia = content.split(
                    "## UX_IA",
                    1,
                )
            else:
                research = content

        return (
            goal.strip(),
            research.strip(),
            ux_ia.strip(),
        )

    @staticmethod
    def detect_domain(
        goal: str,
        ux_ia: str,
    ) -> str:
        text = (
            goal + "\n" + ux_ia
        ).lower()

        if any(
            term in text
            for term in (
                "ecommerce",
                "e-commerce",
                "thương mại điện tử",
                "product detail",
                "checkout",
            )
        ):
            return "ecommerce"

        if any(
            term in text
            for term in (
                "education",
                "school",
                "admissions",
                "giáo dục",
            )
        ):
            return "education"

        if any(
            term in text
            for term in (
                "agency",
                "case studies",
                "digital agency",
            )
        ):
            return "agency"

        if any(
            term in text
            for term in (
                "corporate",
                "company",
                "doanh nghiệp",
            )
        ):
            return "corporate"

        return "generic-website"

    @staticmethod
    def detect_primary_color(
        goal: str,
    ) -> str:
        text = goal.lower()

        colors = (
            ("tím", "purple"),
            ("purple", "purple"),
            ("cam", "orange"),
            ("orange", "orange"),
            ("đỏ", "red"),
            ("red", "red"),
            ("xanh lá", "green"),
            ("green", "green"),
            ("xanh dương", "blue"),
            ("blue", "blue"),
            ("đen", "black"),
            ("black", "black"),
        )

        for keyword, color in colors:
            if keyword in text:
                return color

        return "UNKNOWN"

    @staticmethod
    def visual_signature(
        domain: str,
        primary_color: str,
    ) -> str:
        if domain == "ecommerce":
            return (
                "A product-first commerce interface where "
                "strong editorial scale, deliberate purple wayfinding "
                "and product media carry the hierarchy instead of "
                "repetitive rounded-card grids."
            )

        if domain == "agency":
            return (
                "A proof-driven editorial system where project outcomes "
                "and work samples become the primary visual anchors."
            )

        if domain == "education":
            return (
                "A structured institutional experience where programs, "
                "learning journeys and campus evidence drive composition."
            )

        return (
            "A content-led visual system where page purpose determines "
            "composition rather than one reusable hero template."
        )

    @staticmethod
    def get_composition_matrix(
        domain: str,
    ) -> list[tuple[str, str]]:
        if domain == "ecommerce":
            return [
                (
                    "Home",
                    "Brand / discovery → What can I shop here? → "
                    "product/campaign anchor → editorial discovery composition",
                ),
                (
                    "Category",
                    "Browse / compare → What options match my need? → "
                    "product grid + filters → utility-first composition",
                ),
                (
                    "Search",
                    "Explicit intent → Can I find this quickly? → "
                    "query/results → search-led composition",
                ),
                (
                    "Product Detail",
                    "Decision → Is this the right product? → "
                    "product media + price + variants → product-object composition",
                ),
                (
                    "Cart / Checkout",
                    "Transaction → Can I complete safely and quickly? → "
                    "order summary + form → low-decoration transactional composition",
                ),
            ]

        return [
            (
                "Home",
                "Overview → What is this? → primary value → overview composition",
            ),
            (
                "Primary Offering",
                "Evaluation → Is this relevant? → decision object → evidence composition",
            ),
            (
                "Evidence",
                "Trust → Can I believe this? → proof → editorial/data composition",
            ),
            (
                "Contact",
                "Conversion → What do I do next? → form/action → focused composition",
            ),
        ]

    async def run(
        self,
        instruction: str,
    ) -> str:
        goal, research, ux_ia = self.parse_input(
            instruction
        )

        domain = self.detect_domain(
            goal,
            ux_ia,
        )

        primary_color = self.detect_primary_color(
            goal
        )

        loader = SkillLoader()

        stats = loader.stats()

        skills = loader.select(
            keywords=(
                "visual design direction",
                "visual grammar",
                "visual taste",
                "art direction",
                "typography",
                "color",
                "imagery",
                "layout",
                "responsive",
                "design reference",
                "brand",
            ),
            limit=10,
        )

        if skills:
            skills_markdown = "\n".join(
                f"- `{skill.relative_path}` (score: {skill.score})"
                for skill in skills
            )
        else:
            skills_markdown = (
                "- No matching visual-direction skill found."
            )

        matrix_rows = self.get_composition_matrix(
            domain
        )

        matrix_markdown = "\n".join(
            f"- **{page}** — {rule}"
            for page, rule in matrix_rows
        )

        signature = self.visual_signature(
            domain,
            primary_color,
        )

        created_at = datetime.now().isoformat(
            timespec="seconds"
        )

        research_status = (
            "received"
            if research
            else "missing"
        )

        ux_status = (
            "received"
            if ux_ia
            else "missing"
        )

        lines = [
            "# Art Direction",
            "",
            "## Goal",
            "",
            goal,
            "",
            "## Execution",
            "",
            "- Mode: `mock`",
            f"- Created: `{created_at}`",
            "- LLM API used: `no`",
            f"- Detected domain: `{domain}`",
            f"- Requested primary color: `{primary_color}`",
            f"- Research input: `{research_status}`",
            f"- UX / IA input: `{ux_status}`",
            f'- skills_UIUX root: `{stats["skills_root"]}`',
            f'- Skills discovered: `{stats["skill_count"]}`',
            "",
            "## Relevant Skills",
            "",
            skills_markdown,
            "",
            "## Evidence Status",
            "",
            "`PROVISIONAL`",
            "",
            "This visual direction is generated from the project goal,",
            "the provisional research artifact and UX / IA artifact.",
            "",
            "No external visual reference has been verified yet.",
            "",
            "Therefore this direction may guide exploration,",
            "but it is not yet the final locked Design Contract.",
            "",
            "## Visual Signature",
            "",
            signature,
            "",
            "Signature test:",
            "",
            "If the logo is removed, the project should still be",
            "recognizable through composition, product/media treatment,",
            "wayfinding, hierarchy and interaction language.",
            "",
            "## Visual Attributes",
            "",
            "1. **Product-first** — important decision objects dominate decoration.",
            "2. **Editorial hierarchy** — typography and composition establish rhythm.",
            "3. **Structured** — spacing and alignment communicate organization.",
            "4. **Premium without excess** — restraint before decorative effects.",
            "5. **Distinctive but predictable** — memorable visual devices must not reduce usability.",
            "",
            "## Layout Grammar",
            "",
            "- Use a consistent max-width system, but allow selected sections to break the container.",
            "- Use asymmetric composition only when it strengthens hierarchy.",
            "- Avoid turning every section into heading + description + three rounded cards.",
            "- Alternate density intentionally rather than using identical vertical spacing everywhere.",
            "- Product and decision objects may interrupt the grid when they are the primary evidence.",
            "- Different page roles should not receive the same hero shell by default.",
            "",
            "## Hierarchy",
            "",
            "- Display: campaign or high-impact brand statement only.",
            "- H1: one primary page-level statement.",
            "- H2: major information transitions.",
            "- H3: group or component-level hierarchy.",
            "- Body: readable content with controlled line length.",
            "- Meta: secondary information, labels and supporting facts.",
            "- Action: visually distinct from descriptive text.",
            "",
            "Hierarchy rule:",
            "",
            "Size alone must not carry hierarchy; use spacing, placement,",
            "contrast and content role together.",
            "",
            "## Color Role Map",
            "",
            f"- Primary brand role: `{primary_color}` from user request.",
            "- Exact primary HEX: `UNKNOWN` until explicitly selected or supplied.",
            "- Primary color should be used for meaningful wayfinding, CTA emphasis and active states.",
            "- Neutral surfaces should carry most content density.",
            "- Destructive / error color must remain semantically separate from brand color.",
            "- Success / warning / information states require semantic tokens.",
            "- Do not fill every section with the primary color merely to appear branded.",
            "",
            "## Typography Direction",
            "",
            "- Primary type family: `UNKNOWN`.",
            "- Secondary type family: use only if a real editorial or brand role exists.",
            "- Vietnamese character coverage must be verified.",
            "- Display styles may be expressive; transactional and product information must remain highly readable.",
            "- Avoid choosing typography only because it is currently fashionable.",
            "- Final font selection belongs to the Design Contract.",
            "",
            "## Media / Image Direction",
            "",
            "- Product imagery or domain evidence should be treated as decision content, not decoration.",
            "- Preserve subject focal points across responsive crops.",
            "- Avoid generic stock visuals when real product/domain media is available.",
            "- Do not invent 3D/video requirements if project assets cannot support them.",
            "- Icons should communicate function or category, not merely decorate empty space.",
            "",
            "## Depth, Border & Radius",
            "",
            "- Use elevation only for hierarchy, overlay or interactive separation.",
            "- Default to restrained shadow usage.",
            "- Radius must form one coherent language.",
            "- Avoid large-radius cards everywhere.",
            "- Borders may carry structure where shadows would add unnecessary visual weight.",
            "",
            "## Motion Direction",
            "",
            "- Motion purpose: feedback, hierarchy, orientation or controlled delight.",
            "- Avoid applying the same reveal animation to every section.",
            "- Transactional flows should prioritize speed and stability.",
            "- Product media may use subtle focus or transition behavior.",
            "- Reduced-motion behavior is mandatory.",
            "",
            "## Page-role Composition Matrix",
            "",
            matrix_markdown,
            "",
            "## Composition Proof 1 — Home / Discovery",
            "",
            "```text",
            "Navigation",
            "────────────────────────────────────────",
            "Editorial message        Product / campaign media",
            "Primary CTA              Context / secondary proof",
            "────────────────────────────────────────",
            "Category / discovery navigation",
            "────────────────────────────────────────",
            "Featured decision objects",
            "```",
            "",
            "Mobile transformation:",
            "",
            "- message first",
            "- primary CTA visible early",
            "- media follows without losing focal subject",
            "- discovery controls remain reachable",
            "",
            "## Composition Proof 2 — Category / Browse",
            "",
            "```text",
            "Category context + count",
            "────────────────────────────────────────",
            "Filters            Product results",
            "                   Product results",
            "                   Product results",
            "────────────────────────────────────────",
            "Pagination / progressive loading",
            "```",
            "",
            "Mobile transformation:",
            "",
            "- filter becomes controlled drawer / sheet",
            "- result count remains visible",
            "- product comparison hierarchy survives smaller viewport",
            "",
            "## Composition Proof 3 — Product Detail",
            "",
            "```text",
            "Product media      Product information",
            "Product media      Price / variants",
            "Product media      Primary purchase action",
            "                   Delivery / trust information",
            "────────────────────────────────────────",
            "Specification / evidence / related content",
            "```",
            "",
            "Mobile transformation:",
            "",
            "- product identity and primary media first",
            "- purchase information remains close to decision object",
            "- sticky action only when it improves task completion",
            "",
            "## Anti-template Calibration",
            "",
            "Generic tells to challenge:",
            "",
            "- identical centered hero across every page",
            "- repeated three-card sections",
            "- excessive pill-shaped UI",
            "- gradients with no hierarchy role",
            "- decorative badges with no information value",
            "- every section using the same reveal animation",
            "- stock dashboard-like UI unrelated to ecommerce decisions",
            "",
            "KEEP:",
            "",
            "- familiar commerce interaction patterns where predictability matters",
            "- clear product hierarchy",
            "- readable transactional UI",
            "",
            "REVISE:",
            "",
            "- generic hero shells",
            "- repetitive card-heavy compositions",
            "- decoration without subject-matter rationale",
            "",
            "REMOVE:",
            "",
            "- visual devices that could move unchanged to an unrelated industry",
            "",
            "## Do",
            "",
            "- let product and evidence determine composition",
            "- preserve page-role differences",
            "- use brand color as a role, not wallpaper",
            "- treat mobile transformations as design decisions",
            "- keep transactional views visually quieter than discovery views",
            "",
            "## Do Not",
            "",
            "- copy one hero component across all primary pages",
            "- turn every section into cards",
            "- infer a complete visual style from one brand color",
            "- invent visual evidence that has not been researched",
            "- sacrifice accessibility to appear distinctive",
            "",
            "## Pre-code Visual Gate",
            "",
            "Status: `PROVISIONAL_PASS`",
            "",
            "Available:",
            "",
            "- UX / IA artifact",
            "- visual signature",
            "- layout grammar",
            "- hierarchy rules",
            "- color role map",
            "- typography direction",
            "- media direction",
            "- motion rules",
            "- page-role composition matrix",
            "- three representative composition proofs",
            "- mobile transformation notes",
            "- anti-template calibration",
            "",
            "Still blocking FINAL visual lock:",
            "",
            "- verified design-reference benchmark",
            "- confirmed brand assets / exact brand tokens",
            "- representative real product/content media",
            "- final typography choice",
            "",
            "## Contract for Design System",
            "",
            "The future Design Contract may derive tokens and components",
            "from this direction only after unresolved evidence is tracked.",
            "",
            "Design System must preserve page-role composition diversity.",
            "",
            "A component library must not flatten materially different",
            "page roles into one generic template.",
            "",
            "---",
            "",
            "Generated by `ArtDirector -> CreateArtDirection`",
            "",
        ]

        return "\n".join(lines)