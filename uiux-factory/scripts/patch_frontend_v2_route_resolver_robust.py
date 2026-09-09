from pathlib import Path
import re


TARGET = Path(
    "core/actions/generate_frontend_project_v2.py"
)

if not TARGET.exists():
    raise FileNotFoundError(
        f"Target file not found: {TARGET.resolve()}"
    )

text = TARGET.read_text(
    encoding="utf-8",
)

replacement = '''    @staticmethod
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

        # 1. Exact normalized route.
        for page in composition.pages:
            if normalize(page.path) == requested:
                return page

        # 2. Nested / dynamic route.
        prefix = requested.rstrip("/") + "/"

        for page in composition.pages:
            candidate = normalize(page.path)

            if candidate.startswith(prefix):
                return page

        # 3. Semantic route/page-role aliases.
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
                "product listing",
            ),
            "/search": (
                "search",
                "find",
                "query",
                "results",
                "search results",
            ),
            "/cart": (
                "cart",
                "basket",
                "bag",
                "shopping cart",
            ),
            "/checkout": (
                "checkout",
                "payment",
                "order",
                "purchase",
                "transaction",
            ),
        }

        keywords = aliases.get(
            requested,
            (),
        )

        for page in composition.pages:
            haystack = " ".join(
                [
                    page.path or "",
                    page.page_role or "",
                    page.composition_family or "",
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
            f"{path}. Available pages: {available}"
        )

'''

pattern = re.compile(
    r'''
    ^\s{4}@staticmethod\s*\n
    \s{4}def\s+find_page\(
    .*?
    (?=
        ^\s{4}@(staticmethod|classmethod)\s*\n
        |
        ^\s{4}async\s+def\s+
        |
        ^\s{4}def\s+
    )
    ''',
    flags=re.MULTILINE | re.DOTALL | re.VERBOSE,
)

match = pattern.search(text)

if not match:
    if (
        "Semantic route/page-role aliases."
        in text
        or "Visual Composition missing a route compatible with"
        in text
    ):
        print(
            "Route resolver is already patched. No changes needed."
        )
        raise SystemExit(0)

    raise RuntimeError(
        "Could not locate find_page() automatically. "
        "Run: Select-String -Path "
        ".\\core\\actions\\generate_frontend_project_v2.py "
        "-Pattern \"def find_page\" -Context 3,80"
    )

patched = (
    text[:match.start()]
    + replacement
    + text[match.end():]
)

TARGET.write_text(
    patched,
    encoding="utf-8",
)

print(
    "FrontendEngineerV2 route resolver patched successfully."
)
