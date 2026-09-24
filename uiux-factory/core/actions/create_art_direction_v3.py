from __future__ import annotations

from core.actions.create_art_direction_v2 import CreateArtDirectionV2


class CreateArtDirectionV3(CreateArtDirectionV2):
    """Direction-aware art direction with explicit V1 acceptance contracts."""

    name: str = "CreateArtDirectionV3"

    @staticmethod
    def style_profile(goal: str, domain: str) -> tuple[list[str], str]:
        text = goal.casefold()
        if domain == "ecommerce" and any(term in text for term in ("perfume", "fragrance", "nước hoa")):
            return ["Sensory", "Editorial", "Refined"], "A fragrance-led experience should read immediately as sensory, image-conscious and premium without collapsing into generic luxury card patterns."
        if domain == "ecommerce" and any(term in text for term in ("fashion", "clothing", "apparel", "quần áo")):
            return ["Editorial", "Expressive", "Tactile"], "A fashion-led storefront should make product imagery, styling and browse confidence immediately legible before generic commerce chrome."
        if domain == "ecommerce" and any(term in text for term in ("electronics", "device", "laptop", "phone")):
            return ["Precise", "Technical", "Confident"], "An electronics storefront should make products, specifications and comparison confidence immediately legible."
        if domain == "ecommerce":
            return ["Product-led", "Clear", "Distinctive"], "A commerce experience should make the product decision and next shopping action obvious before decorative UI."
        if domain == "education":
            return ["Trustworthy", "Clear", "Welcoming"], "An education experience should immediately communicate institutional trust, relevant learning paths and a clear admissions or enquiry direction."
        if domain == "agency":
            return ["Distinctive", "Evidence-led", "Confident"], "An agency experience should immediately communicate a point of view, credible work evidence and a clear path to evaluate fit."
        if domain == "corporate":
            return ["Credible", "Structured", "Clear"], "A corporate experience should immediately clarify what the organization does, why it is credible and what the visitor should do next."
        return ["Purposeful", "Distinctive", "Coherent"], "The opening view should make the site's purpose, primary evidence and next action understandable without relying on a generic template shell."

    async def run(self, instruction: str) -> str:
        goal, _research, ux_ia = self.parse_input(instruction)
        domain = self.detect_domain(goal, ux_ia)
        base = await super().run(instruction)
        words, impression = self.style_profile(goal, domain)

        block = "\n".join([
            "## First Impression",
            "",
            impression,
            "",
            "## Style Adjectives",
            "",
            *[f"- {word}" for word in words],
        ])
        if "## First Impression" not in base and "## Style Adjectives" not in base:
            base = self.insert_before(base, "## Visual Signature", block)
        return base
