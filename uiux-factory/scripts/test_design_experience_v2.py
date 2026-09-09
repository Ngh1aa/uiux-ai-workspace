from core.actions.create_art_direction_v2 import (
    CreateArtDirectionV2,
)
from core.actions.create_visual_composition_v2 import (
    CreateVisualCompositionV2,
)


def assert_equal(
    actual,
    expected,
    label: str,
) -> None:
    if actual != expected:
        raise AssertionError(
            f"{label}: expected {expected!r}, got {actual!r}"
        )


def main() -> None:
    goal = """
Thiết kế website ecommerce màu tím.

## SELECTED DESIGN DIRECTION
Name: Editorial Commerce
Intent: Product discovery should feel editorial.
Composition: Oversized type + asymmetric product staging.
Typography: Expressive display + restrained product UI.
Media: Product objects lead the page.
Avoid: Card soup and generic SaaS gradients.
Signature: Editorial product theatre with purple wayfinding.

## MANUAL REFERENCES
1. https://example.com/reference
""".strip()

    direction = (
        CreateArtDirectionV2
        .extract_direction(
            goal
        )
    )

    assert_equal(
        direction["name"],
        "Editorial Commerce",
        "direction name",
    )

    assert_equal(
        direction["signature"],
        "Editorial product theatre with purple wayfinding.",
        "direction signature",
    )

    urls = (
        CreateArtDirectionV2
        .reference_urls(
            goal,
            "Reference URL: https://stripe.com/",
        )
    )

    if (
        "https://example.com/reference"
        not in urls
    ):
        raise AssertionError(
            "manual reference URL was not detected"
        )

    if "https://stripe.com/" not in urls:
        raise AssertionError(
            "research reference URL was not detected"
        )

    assert_equal(
        CreateVisualCompositionV2
        .direction_profile(
            goal
        ),
        "editorial",
        "direction profile",
    )

    ecommerce_home = (
        CreateVisualCompositionV2
        .sections_for(
            "ecommerce",
            "/",
            "Home",
            "editorial",
        )
    )

    if len(ecommerce_home) < 4:
        raise AssertionError(
            "ecommerce home needs multiple composition chapters"
        )

    if (
        "editorial"
        not in ecommerce_home[1]
        .composition
    ):
        raise AssertionError(
            "selected editorial profile did not affect hero composition"
        )

    corporate_home = (
        CreateVisualCompositionV2
        .sections_for(
            "corporate",
            "/",
            "Home",
            "precision",
        )
    )

    if any(
        section.type
        == "featured-products"
        for section in corporate_home
    ):
        raise AssertionError(
            "corporate composition must not inherit ecommerce merchandising"
        )

    education_home = (
        CreateVisualCompositionV2
        .sections_for(
            "education",
            "/",
            "Home",
            "human",
        )
    )

    if not any(
        section.type
        == "program-pathways"
        for section in education_home
    ):
        raise AssertionError(
            "education home is missing program pathways"
        )

    agency_home = (
        CreateVisualCompositionV2
        .sections_for(
            "agency",
            "/",
            "Home",
            "editorial",
        )
    )

    if not any(
        section.type
        == "selected-work"
        for section in agency_home
    ):
        raise AssertionError(
            "agency home is missing work-first composition"
        )

    print(
        "PASS: Design Experience V2 direction parsing and "
        "domain-aware composition checks succeeded."
    )


if __name__ == "__main__":
    main()
