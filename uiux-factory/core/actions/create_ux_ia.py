from datetime import datetime

from metagpt.actions import Action

from core.skills.loader import SkillLoader


class CreateUXIA(Action):
    name: str = "CreateUXIA"

    desc: str = (
        "Transform research into a provisional UX strategy "
        "and information architecture."
    )

    @staticmethod
    def parse_input(instruction: str) -> tuple[str, str]:
        goal = instruction.strip()
        research = ""

        if "## GOAL" in instruction:
            content = instruction.split("## GOAL", 1)[1]

            if "## RESEARCH" in content:
                goal, research = content.split(
                    "## RESEARCH",
                    1,
                )
            else:
                goal = content

        return goal.strip(), research.strip()

    @staticmethod
    def detect_domain(goal: str) -> str:
        text = goal.lower()

        ecommerce_terms = (
            "ecommerce",
            "e-commerce",
            "thương mại điện tử",
            "shop",
            "shopping",
            "bán hàng",
        )

        education_terms = (
            "education",
            "school",
            "trường học",
            "giáo dục",
        )

        agency_terms = (
            "agency",
            "digital agency",
            "marketing agency",
        )

        corporate_terms = (
            "corporate",
            "company",
            "doanh nghiệp",
        )

        if any(term in text for term in ecommerce_terms):
            return "ecommerce"

        if any(term in text for term in education_terms):
            return "education"

        if any(term in text for term in agency_terms):
            return "agency"

        if any(term in text for term in corporate_terms):
            return "corporate"

        return "generic-website"

    @staticmethod
    def get_pages(domain: str) -> list[tuple[str, str]]:
        if domain == "ecommerce":
            return [
                ("Home", "Discovery, campaign entry and orientation."),
                ("Category / Collection", "Browse and refine product groups."),
                ("Search", "Find products from explicit intent."),
                ("Product Detail", "Evaluate a product before purchase."),
                ("Cart", "Review selected products."),
                ("Checkout", "Complete the transaction."),
                ("Account", "Orders, profile and preferences."),
                ("Support", "Delivery, returns and customer help."),
            ]

        if domain == "agency":
            return [
                ("Home", "Position the agency and direct intent."),
                ("Services", "Explain service categories."),
                ("Service Detail", "Explain value, process and CTA."),
                ("Case Studies", "Provide proof and outcomes."),
                ("About", "Build credibility."),
                ("Insights", "Demonstrate expertise."),
                ("Contact", "Capture qualified enquiries."),
            ]

        if domain == "education":
            return [
                ("Home", "Orient students and families."),
                ("About", "Institution and credibility."),
                ("Programs", "Learning pathways and curriculum."),
                ("Admissions", "Application journey."),
                ("Student Life", "Campus and student experience."),
                ("News / Events", "Current activity."),
                ("Contact", "Enquiry and campus visit."),
            ]

        return [
            ("Home", "Primary orientation."),
            ("About", "Context and credibility."),
            ("Products / Services", "Core offering."),
            ("Evidence", "Proof and outcomes."),
            ("Resources", "Supporting content."),
            ("Contact", "Primary conversion."),
        ]

    async def run(self, instruction: str) -> str:
        goal, research = self.parse_input(instruction)
        domain = self.detect_domain(goal)

        loader = SkillLoader()
        stats = loader.stats()

        skills = loader.select(
            keywords=(
                "information architecture",
                "journey",
                "top tasks",
                "navigation",
                "findability",
                "taxonomy",
                "card sorting",
                "user flow",
                "ux research",
            ),
            limit=8,
        )

        if skills:
            skills_markdown = "\n".join(
                f"- `{skill.relative_path}` (score: {skill.score})"
                for skill in skills
            )
        else:
            skills_markdown = "- No matching UX/IA skill found."

        pages = self.get_pages(domain)

        pages_markdown = "\n".join(
            f"- **{name}** — {description}"
            for name, description in pages
        )

        sitemap = "\n".join(
            f'    HOME --> P{index}["{name}"]'
            for index, (name, _) in enumerate(
                pages[1:],
                start=1,
            )
        )

        created_at = datetime.now().isoformat(
            timespec="seconds"
        )

        research_status = (
            "received"
            if research
            else "missing"
        )

        lines = [
            "# UX Strategy & Information Architecture",
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
            f"- Research input: `{research_status}`",
            f'- skills_UIUX root: `{stats["skills_root"]}`',
            f'- Skills discovered: `{stats["skill_count"]}`',
            "",
            "## Relevant skills",
            "",
            skills_markdown,
            "",
            "## Evidence Status",
            "",
            "`PROVISIONAL`",
            "",
            "The current research stage does not contain verified external evidence.",
            "",
            "Therefore this UX/IA output is a working hypothesis, not validated user research.",
            "",
            "## UX Principles",
            "",
            "1. Prioritize user intent over internal organization.",
            "2. Keep navigation shallow and understandable.",
            "3. Give every important page a clear role.",
            "4. Maintain strong information scent.",
            "5. Keep primary conversion paths visible.",
            "6. Separate discovery, evaluation and transaction tasks.",
            "7. Design mobile information priority explicitly.",
            "8. Preserve UNKNOWN values instead of inventing evidence.",
            "",
            "## Audience & Top Tasks",
            "",
            "- Primary audience: `UNKNOWN`",
            "- Secondary audience: `UNKNOWN`",
            "- Highest-value user task: `UNKNOWN`",
            "- Device priority: `UNKNOWN`",
            "- Search importance: `NEEDS_VALIDATION`",
            "- Primary conversion: inferred only from project goal",
            "",
            "## Provisional Page Roles",
            "",
            pages_markdown,
            "",
            "## Provisional Sitemap",
            "",
            "```mermaid",
            "graph TD",
            '    HOME["Home"]',
            sitemap,
            "```",
            "",
            "## Navigation Strategy",
            "",
            "Primary navigation should:",
            "",
            "- use recognizable labels",
            "- avoid internal department terminology",
            "- avoid duplicate destinations",
            "- avoid ambiguous marketing wording",
            "- keep high-value tasks easy to reach",
            "",
            "Secondary navigation should only be introduced when it materially improves orientation or discovery.",
            "",
            "## Critical Journey",
            "",
            "```text",
            "Entry",
            "  ↓",
            "Orient",
            "  ↓",
            "Discover",
            "  ↓",
            "Evaluate",
            "  ↓",
            "Act / Convert",
            "  ↓",
            "Confirmation / Recovery",
            "```",
            "",
            "## Ecommerce Journey",
            "",
            "```text",
            "Entry",
            "  ↓",
            "Browse / Search",
            "  ↓",
            "Category",
            "  ↓",
            "Product Detail",
            "  ↓",
            "Cart",
            "  ↓",
            "Checkout",
            "  ↓",
            "Confirmation",
            "```",
            "",
            "## Page Hierarchy Contract",
            "",
            "Every important page should eventually define:",
            "",
            "1. page purpose",
            "2. audience intent",
            "3. primary action",
            "4. supporting information",
            "5. evidence / reassurance",
            "6. secondary routes",
            "7. next-step path",
            "",
            "## Responsive Strategy",
            "",
            "Mobile priority:",
            "",
            "1. orientation",
            "2. key content",
            "3. primary action",
            "4. navigation",
            "5. supporting information",
            "",
            "Desktop may expose more discovery and comparison without changing the underlying IA.",
            "",
            "## UX / IA Gate",
            "",
            "Status: `PASS_WITH_ASSUMPTIONS`",
            "",
            "Currently satisfied:",
            "",
            "- research artifact received",
            "- uncertainty is explicitly tracked",
            "- provisional sitemap exists",
            "- page roles exist",
            "- journey model exists",
            "- assumptions are not presented as research evidence",
            "",
            "Still required later:",
            "",
            "- verified audience",
            "- validated top tasks",
            "- real competitor evidence",
            "- analytics where available",
            "- usability validation",
            "",
            "## Contract for Art Direction",
            "",
            "Art Direction receives:",
            "",
            "- project goal",
            "- detected domain",
            "- UX principles",
            "- provisional sitemap",
            "- page roles",
            "- journey model",
            "- evidence status",
            "",
            "Art Direction must not silently change core IA.",
            "",
            "Major structural changes should return to UX/IA.",
            "",
            "---",
            "",
            "Generated by `UXStrategist -> CreateUXIA`",
            "",
        ]

        return "\n".join(lines)