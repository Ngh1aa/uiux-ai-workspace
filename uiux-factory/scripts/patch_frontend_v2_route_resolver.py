from pathlib import Path

path = Path("core/actions/generate_frontend_project_v2.py")

text = path.read_text(encoding="utf-8")

old = '''    @staticmethod
    def find_page(
        composition: VisualComposition,
        path: str,
    ) -> PageSpec:
        for page in composition.pages:
            if page.path == path:
                return page

        raise RuntimeError(
            f"Visual Composition missing required route: {path}"
        )
'''

new = '''    @staticmethod
    def find_page(
        composition: VisualComposition,
        path: str,
    ) -> PageSpec:
        def normalize(value: str) -> str:
            if not value:
                return "/"

            normalized = "/" + value.strip("/")

            if normalized == "/":
                return "/"

            return normalized.lower()

        requested = normalize(path)

        # 1. Exact normalized route match.
        for page in composition.pages:
            if normalize(page.path) == requested:
                return page

        # 2. Dynamic/nested route match.
        # Example: requested /category can resolve /category/[slug].
        prefix = requested.rstrip("/") + "/"

        for page in composition.pages:
            candidate = normalize(page.path)

            if candidate.startswith(prefix):
                return page

        # 3. Semantic fallback using page role / composition family.
        aliases = {
            "/category": (
                "category",
                "catalog",
                "catalogue",
                "collection",
                "browse",
                "listing",
                "shop",
                "products",
            ),
            "/search": (
                "search",
                "find",
                "query",
                "results",
            ),
            "/cart": (
                "cart",
                "basket",
                "bag",
            ),
            "/checkout": (
                "checkout",
                "payment",
                "order",
                "purchase",
            ),
        }

        keywords = aliases.get(
            requested,
            (),
        )

        for page in composition.pages:
            haystack = " ".join(
                [
                    page.path,
                    page.page_role,
                    page.composition_family,
                ]
            ).lower()

            if any(
                keyword in haystack
                for keyword in keywords
            ):
                return page

        available = [
            {
                "path": page.path,
                "page_role": page.page_role,
                "composition_family": page.composition_family,
            }
            for page in composition.pages
        ]

        raise RuntimeError(
            "Visual Composition missing a route compatible with "
            f"{path}. Available pages: "
            f"{available}"
        )
'''

if old not in text:
    raise RuntimeError(
        "Could not find the old find_page method. "
        "The file may already be patched or differ from the expected V2."
    )

text = text.replace(old, new, 1)

path.write_text(text, encoding="utf-8")

print("FrontendEngineerV2 route resolver patched.")
