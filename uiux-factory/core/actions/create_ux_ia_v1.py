from __future__ import annotations

from core.actions.create_ux_ia import CreateUXIA


class CreateUXIAV1(CreateUXIA):
    """Keep the safe baseline while making V1 UX assumptions explicit.

    These values are deliberately labeled *inferred from the brief*. They are
    design assumptions, not claims of user-research validation, and can be
    replaced by provider/user evidence later in the same canonical artifact.
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
        return base
