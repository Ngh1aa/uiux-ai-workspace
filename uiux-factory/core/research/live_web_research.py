from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Iterable
from urllib.parse import urlencode, urlparse
from urllib.request import Request, urlopen


@dataclass(frozen=True)
class ResearchCandidate:
    title: str
    url: str
    description: str
    query_family: str
    query: str
    provenance: str = "brave-web-search"

    @property
    def domain(self) -> str:
        return urlparse(self.url).netloc.lower().removeprefix("www.")


class LiveWebResearch:
    """Discover current public references without pretending fallback data is live research."""

    SEARCH_ENDPOINT = "https://api.search.brave.com/res/v1/web/search"

    PAGE_ROLES = {
        "ecommerce": ("homepage", "product listing", "product detail", "checkout"),
        "saas": ("homepage", "use case", "pricing", "product proof"),
        "hospitality": ("homepage", "rooms", "experience", "booking"),
        "education": ("homepage", "programmes", "admissions", "campus"),
        "news": ("homepage", "topic listing", "article", "search"),
        "real-estate": ("homepage", "availability", "property detail", "location"),
        "government": ("service landing", "task page", "form", "confirmation"),
        "nonprofit": ("homepage", "impact", "donation", "campaign"),
        "portfolio": ("homepage", "project index", "case study", "contact"),
        "corporate": ("homepage", "capability", "proof", "contact"),
        "landing": ("landing page", "proof", "conversion"),
        "startup": ("homepage", "product", "proof", "conversion"),
        "generic": ("homepage", "detail page", "conversion"),
    }

    @staticmethod
    def _subject(website_type: str, vertical: str) -> str:
        if vertical and vertical != "generic":
            return vertical.replace("-", " ")
        return website_type.replace("-", " ")

    @classmethod
    def build_query_families(
        cls,
        *,
        website_type: str,
        vertical: str,
    ) -> dict[str, list[str]]:
        subject = cls._subject(website_type, vertical)
        roles = cls.PAGE_ROLES.get(website_type, cls.PAGE_ROLES["generic"])
        role_queries = [f"{subject} {role} website UX" for role in roles[:4]]
        return {
            "industry-reality": [
                f"{subject} {website_type} production website",
                f"best {subject} websites customer experience",
            ],
            "page-role-task": role_queries,
            "visual-art-direction": [
                f"{subject} website art direction typography photography",
                f"{subject} digital brand visual system",
            ],
        }

    def __init__(self, api_key: str | None = None, timeout: float = 8.0) -> None:
        self.api_key = api_key or os.getenv("BRAVE_SEARCH_API_KEY", "").strip()
        self.timeout = timeout

    @property
    def enabled(self) -> bool:
        return bool(self.api_key)

    def search(self, query: str, *, count: int = 8) -> list[dict]:
        if not self.enabled:
            return []

        params = urlencode(
            {
                "q": query,
                "count": max(1, min(20, int(count))),
                "search_lang": "en",
            }
        )
        request = Request(
            f"{self.SEARCH_ENDPOINT}?{params}",
            headers={
                "Accept": "application/json",
                "X-Subscription-Token": self.api_key,
                "User-Agent": "uiux-factory-research/1.0",
            },
        )
        with urlopen(request, timeout=self.timeout) as response:
            payload = json.loads(response.read().decode("utf-8"))

        return list(payload.get("web", {}).get("results", []))

    def discover(
        self,
        query_families: dict[str, list[str]],
        *,
        max_candidates: int = 20,
    ) -> list[ResearchCandidate]:
        candidates: list[ResearchCandidate] = []
        seen_urls: set[str] = set()

        for family, queries in query_families.items():
            for query in queries:
                try:
                    results = self.search(query, count=8)
                except Exception:
                    results = []

                for item in results:
                    url = str(item.get("url", "")).strip()
                    title = str(item.get("title", "")).strip()
                    description = str(item.get("description", "")).strip()
                    if not url.startswith(("https://", "http://")):
                        continue
                    normalized = url.split("#", 1)[0].rstrip("/")
                    if normalized in seen_urls:
                        continue
                    seen_urls.add(normalized)
                    candidates.append(
                        ResearchCandidate(
                            title=title or normalized,
                            url=url,
                            description=description,
                            query_family=family,
                            query=query,
                        )
                    )
                    if len(candidates) >= max_candidates:
                        return candidates

        return candidates

    @staticmethod
    def shortlist(
        candidates: Iterable[ResearchCandidate],
        *,
        limit: int = 6,
    ) -> list[ResearchCandidate]:
        family_weight = {
            "page-role-task": 3,
            "industry-reality": 2,
            "visual-art-direction": 1,
        }
        ranked = sorted(
            candidates,
            key=lambda item: (
                -family_weight.get(item.query_family, 0),
                item.domain,
                item.title.lower(),
            ),
        )

        selected: list[ResearchCandidate] = []
        per_domain: dict[str, int] = {}
        for item in ranked:
            domain = item.domain
            if per_domain.get(domain, 0) >= 2:
                continue
            selected.append(item)
            per_domain[domain] = per_domain.get(domain, 0) + 1
            if len(selected) >= limit:
                break
        return selected
