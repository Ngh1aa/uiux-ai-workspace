from __future__ import annotations

from core.actions.create_ux_ia import CreateUXIA


class CreateUXIAV1(CreateUXIA):
    """Keep the safe baseline while making V1 UX assumptions explicit.

    These values are deliberately labeled *inferred from the brief*. They are
    design assumptions, not claims of user-research validation, and can be
    replaced by provider/user evidence later in the same canonical artifact.

    V1 also adds a mid-level product-design reasoning layer. The layer does not
    manufacture research or impact. It makes hypotheses, trade-offs, success
    signals, validation needs and case-study evidence explicit so later stages
    can challenge them instead of treating polished UI as proof.
    """

    name: str = "CreateUXIAV1"

    @staticmethod
    def assumption_profile(goal: str, domain: str) -> dict[str, str]:
        text = goal.casefold()
        if domain == "ecommerce":
            if any(term in text for term in ("perfume", "fragrance", "nước hoa")):
                return {
                    "audience": "People discovering, comparing, sampling or purchasing fragrance online",
                    "task": "Discover a relevant fragrance, understand its scent/fit, and progress confidently toward purchase",
                    "conversion": "Product evaluation → cart / sample decision → checkout",
                }
            return {
                "audience": "People browsing, comparing and purchasing the products described by the commerce brief",
                "task": "Find a relevant product, evaluate it, and complete the intended purchase path",
                "conversion": "Product evaluation → cart → checkout",
            }
        if domain == "education":
            return {
                "audience": "Prospective learners and the people helping them evaluate programs or admissions",
                "task": "Find the right program or admissions information and understand the next step",
                "conversion": "Program evaluation → admissions/enquiry next step",
            }
        if domain == "agency":
            return {
                "audience": "Prospective clients evaluating capability, fit, proof and a path to contact",
                "task": "Understand the offer, inspect proof, and reach an appropriate enquiry action",
                "conversion": "Service/proof evaluation → qualified enquiry",
            }
        if domain == "corporate":
            return {
                "audience": "Visitors evaluating the organization, its offering, credibility and contact paths",
                "task": "Understand the organization and reach the most relevant next action",
                "conversion": "Offering/evidence evaluation → contact or primary business action",
            }
        return {
            "audience": "Visitors whose primary need is implied by the website brief and page roles",
            "task": "Understand the primary offering and complete the clearest high-value next action",
            "conversion": "Primary offering/evidence → high-value next action",
        }

    @staticmethod
    def maturity_layer(profile: dict[str, str]) -> str:
        """Return a truth-preserving UX/product reasoning contract.

        This deliberately defines what must be reasoned about and validated,
        without pretending those activities have already happened.
        """
        return "\n".join(
            [
                "## UX Reasoning Frame",
                "",
                f"- **Target user hypothesis:** {profile['audience']} *(INFERRED from brief until verified)*",
                f"- **Top-task hypothesis:** {profile['task']} *(INFERRED from brief until verified)*",
                f"- **Primary behavior / conversion hypothesis:** {profile['conversion']} *(INFERRED from brief)*",
                "- **User problem:** describe the observable friction or unmet need; do not substitute a requested feature for the problem.",
                "- **Owner / business objective:** state the value the organization needs from the same journey.",
                "- **Constraints:** record content, technical, operational, legal, accessibility, device and delivery constraints that can change the solution.",
                "- **Evidence that would change the design:** list the unknowns whose answers could invalidate the current direction.",
                "",
                "### Decision rule",
                "",
                "Every material UX decision must be explainable as:",
                "",
                "`evidence or explicit hypothesis → user/business tension → options/trade-off → decision → expected behavior → validation signal`",
                "",
                "A visual preference alone is not a sufficient rationale for a product decision.",
                "",
                "## Product Thinking Ledger",
                "",
                "For each critical journey or feature, capture:",
                "",
                "| Field | Required content | Truth rule |",
                "|---|---|---|",
                "| User value | What becomes easier, clearer, safer or more useful | May be hypothesis before validation |",
                "| Owner value | Conversion, qualified enquiry, retention, comprehension, support reduction or other relevant objective | Do not invent business impact |",
                "| Evidence | Research, analytics, brief, production behavior or inspected competitor/reference evidence | Label VERIFIED / INFERRED / ASSUMED / UNKNOWN |",
                "| Options considered | At least one credible alternative for high-impact decisions | Do not create fake explorations after the fact |",
                "| Trade-off | What the chosen direction improves and what it gives up | Required for consequential decisions |",
                "| Technical reality | Component, content, data, performance and implementation constraints | Confirm with code/dev evidence when available |",
                "| Success signal | Observable task or metric that would indicate improvement | A target is not a measured result |",
                "| Risk | What could fail for users or the business | Must map to validation where material |",
                "",
                "## Validation Contract",
                "",
                "Validation is required to reduce uncertainty; polished UI is not validation.",
                "",
                "Before implementation or portfolio claims, define:",
                "",
                "1. **Hypothesis** — what behavior or comprehension is expected and why.",
                "2. **Method** — usability test, task-based prototype test, heuristic/accessibility review, analytics review, A/B test, stakeholder/dev review, or another fit-for-risk method.",
                "3. **Participants / evidence source** — who or what can legitimately answer the question.",
                "4. **Critical tasks** — realistic tasks stated without coaching the expected UI path.",
                "5. **Success criteria** — completion, error/recovery, comprehension, confidence, time-on-task, conversion or another relevant signal.",
                "6. **Findings** — OBSERVED / MEASURED only when evidence exists; otherwise keep as PLANNED / UNKNOWN.",
                "7. **Iteration** — show what changed because of evidence, including rejected findings when justified.",
                "",
                "### Validation integrity",
                "",
                "- Never fabricate interviews, participant counts, quotes, A/B results, analytics or uplift.",
                "- If no participant research exists, say so and use `PLANNED VALIDATION`, `HEURISTIC REVIEW`, or another truthful label.",
                "- A small qualitative usability round can be useful for finding interaction problems, but participant count must reflect the real study rather than a portfolio convention.",
                "- Automated accessibility/browser checks are implementation evidence, not proof that the product is usable for every user.",
                "",
                "## Accessibility & State Reasoning",
                "",
                "Critical flows must account for:",
                "",
                "- keyboard and visible focus behavior",
                "- accessible names, labels and error association",
                "- contrast and non-color status cues",
                "- target sizing and touch behavior",
                "- loading, empty, error, success, disabled, selected/saved and recovery states where relevant",
                "- responsive priority rather than desktop shrinkage",
                "- reduced-motion behavior when motion is non-essential",
                "",
                "Treat WCAG conformance as a claim requiring the corresponding checks/evidence.",
                "",
                "## Case Study Capture Contract",
                "",
                "Capture evidence while the project is being designed so the portfolio does not reconstruct a fictional process later.",
                "",
                "Each case study should be able to answer, in recruiter-scan order:",
                "",
                "1. **Context / challenge** — what real decision or friction existed?",
                "2. **Role & scope** — what did the designer actually own?",
                "3. **Constraints** — what made the problem non-trivial?",
                "4. **Evidence & unknowns** — what was known, inferred and still unverified?",
                "5. **Reasoning** — which options/trade-offs led to the chosen direction?",
                "6. **System / implementation** — how did the decision become reusable responsive behavior?",
                "7. **Validation** — what was tested or inspected, and what changed because of it?",
                "8. **Outcome** — what can be truthfully claimed from available evidence?",
                "9. **Boundary** — what cannot be claimed?",
                "10. **Reflection / next test** — what would be learned or improved next?",
                "",
                "A case-study screen should exist because it supports a problem, decision, evidence point or outcome — not only because it looks impressive.",
                "",
                "## Mid-level UX Gate",
                "",
                "A project may progress with hypotheses, but the artifact must not hide missing evidence.",
                "",
                "Minimum to progress from UX/IA:",
                "",
                "- user problem and owner objective are both stated",
                "- critical journey and page roles are explicit",
                "- material assumptions are labeled",
                "- at least one success signal exists for the critical journey",
                "- high-risk decisions have a validation method",
                "- accessibility/state risks are identified",
                "- portfolio capture preserves reasoning and evidence boundaries",
                "",
            ]
        )

    async def run(self, instruction: str) -> str:
        goal, _research = self.parse_input(instruction)
        domain = self.detect_domain(goal)
        profile = self.assumption_profile(goal, domain)
        base = await super().run(instruction)
        base = base.replace(
            "- Primary audience: `UNKNOWN`",
            f"- Primary audience: {profile['audience']} *(inferred from brief; validate if a narrower segment matters)*",
        )
        base = base.replace(
            "- Highest-value user task: `UNKNOWN`",
            f"- Highest-value user task: {profile['task']} *(inferred from brief)*",
        )
        base = base.replace(
            "- Primary conversion: inferred only from project goal",
            f"- Primary conversion: {profile['conversion']} *(inferred from brief)*",
        )

        maturity = self.maturity_layer(profile)
        marker = "## Contract for Art Direction"
        if marker in base:
            base = base.replace(marker, f"{maturity}\n{marker}", 1)

        base = base.replace(
            "- evidence status\n\nArt Direction receives:",
            "- evidence status\n\nArt Direction also receives the product-thinking ledger, validation contract and case-study capture requirements above.\n\nArt Direction receives:",
            1,
        )
        return base
