from __future__ import annotations

import os
import re
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path


UPSTREAM_RELATIVE_ROOT = Path("skills_UIUX/upstream/motion-primitives-website")
UPSTREAM_COMPONENT_ROOT = Path("src/components")
SUPPORTED_SUFFIXES = {".tsx", ".ts"}


@dataclass(frozen=True)
class MotionPrimitiveCandidate:
    path: str
    category: str
    dependencies: tuple[str, ...]
    score: float
    reasons: tuple[str, ...]

    def to_dict(self) -> dict[str, object]:
        return {
            "path": self.path,
            "category": self.category,
            "dependencies": list(self.dependencies),
            "score": self.score,
            "reasons": list(self.reasons),
        }


class MotionPrimitiveCatalog:
    """Search the pinned Motion Primitives corpus without treating it as project truth.

    The adapter intentionally returns source references, not copied code. Selection and
    implementation still belong to the Design Contract + target project stack.
    """

    _ALIASES: dict[str, tuple[str, ...]] = {
        "hero": ("hero", "spotlight", "background", "reveal", "gradient", "aurora"),
        "scroll": ("scroll", "parallax", "sticky", "reveal", "marquee", "progress"),
        "image": ("image", "media", "gallery", "carousel", "reveal", "mask"),
        "editorial": ("image", "text", "reveal", "scroll", "mask", "cursor"),
        "luxury": ("image", "reveal", "cursor", "parallax", "text", "gallery"),
        "automotive": ("scroll", "reveal", "3d", "tilt", "parallax", "spotlight"),
        "mobility": ("progress", "path", "scroll", "map", "route", "transition"),
        "enterprise": ("button", "card", "navigation", "tooltip", "dialog", "transition"),
        "fintech": ("card", "number", "progress", "transition", "tooltip", "button"),
        "education": ("progress", "step", "text", "feedback", "reveal", "navigation"),
        "ai": ("chat", "text", "typing", "loader", "progress", "reveal"),
        "3d": ("3d", "three", "tilt", "spline", "webgl"),
        "glass": ("glass", "blur", "dock", "navigation"),
        "text": ("text", "type", "typing", "scramble", "word", "letter"),
    }

    _CATEGORY_HINTS: dict[str, tuple[str, ...]] = {
        "backgrounds": ("background", "hero", "gradient", "aurora", "mesh", "spotlight"),
        "buttons": ("button", "cta", "press", "hover", "magnetic"),
        "cards": ("card", "tilt", "spotlight", "hover", "stack"),
        "chat": ("chat", "message", "typing", "assistant", "ai"),
        "effects": ("effect", "shader", "noise", "cursor", "distortion", "glow"),
        "interactive": ("interactive", "drag", "cursor", "magnetic", "hover"),
        "layout": ("layout", "grid", "bento", "section", "hero"),
        "navigation": ("navigation", "nav", "dock", "menu", "tabs"),
        "scroll": ("scroll", "parallax", "sticky", "reveal", "marquee"),
    }

    def __init__(self, upstream_root: Path | None = None) -> None:
        if upstream_root is None:
            env_root = os.environ.get("UIUX_MOTION_PRIMITIVES_ROOT")
            if env_root:
                upstream_root = Path(env_root)
            else:
                workspace_root = Path(__file__).resolve().parents[3]
                upstream_root = workspace_root / UPSTREAM_RELATIVE_ROOT
        self.upstream_root = Path(upstream_root).resolve()
        self.component_root = self.upstream_root / UPSTREAM_COMPONENT_ROOT

    @property
    def available(self) -> bool:
        return self.component_root.is_dir()

    def require_available(self) -> None:
        if not self.available:
            raise FileNotFoundError(
                f"Motion Primitives submodule missing at {self.upstream_root}. "
                "Run: git submodule update --init --recursive"
            )

    @staticmethod
    def _tokens(value: str) -> tuple[str, ...]:
        return tuple(dict.fromkeys(re.findall(r"[a-z0-9]+", value.lower())))

    @classmethod
    def _expanded_terms(cls, query: str) -> set[str]:
        terms = set(cls._tokens(query))
        expanded = set(terms)
        for term in tuple(terms):
            expanded.update(cls._ALIASES.get(term, ()))
        return expanded

    @staticmethod
    def _dependencies(source: str) -> tuple[str, ...]:
        checks = (
            ("framer-motion", ("framer-motion",)),
            ("motion", ('from "motion/', "from 'motion/")),
            ("gsap", ("gsap", "ScrollTrigger")),
            ("three", ("three", "@react-three/fiber", "@react-three/drei")),
            ("spline", ("@splinetool", "Spline")),
            ("lenis", ("lenis", "@studio-freight/lenis")),
        )
        found: list[str] = []
        lowered = source.lower()
        for name, needles in checks:
            if any(needle.lower() in lowered for needle in needles):
                found.append(name)
        return tuple(found)

    @lru_cache(maxsize=1)
    def _source_files(self) -> tuple[Path, ...]:
        self.require_available()
        files = [
            path
            for path in self.component_root.rglob("*")
            if path.is_file()
            and path.suffix in SUPPORTED_SUFFIXES
            and path.name not in {"index.ts", "index.tsx"}
            and "docs" not in path.relative_to(self.component_root).parts
        ]
        return tuple(sorted(files))

    def discover(self) -> tuple[str, ...]:
        """Return stable upstream-relative component source paths."""
        return tuple(path.relative_to(self.upstream_root).as_posix() for path in self._source_files())

    def search(
        self,
        query: str,
        *,
        limit: int = 5,
        categories: tuple[str, ...] | None = None,
    ) -> list[MotionPrimitiveCandidate]:
        """Rank likely component references for one focused motion intent.

        This is lexical retrieval by design: it is deterministic, dependency-free and easy
        to audit. Callers still need to inspect shortlisted source before adopting anything.
        """
        if not query.strip():
            raise ValueError("query must not be empty")
        if limit < 1:
            raise ValueError("limit must be >= 1")

        wanted_categories = {item.lower() for item in categories or ()}
        terms = self._expanded_terms(query)
        candidates: list[MotionPrimitiveCandidate] = []

        for path in self._source_files():
            relative = path.relative_to(self.upstream_root)
            parts = relative.parts
            try:
                component_index = parts.index("components")
                category = parts[component_index + 1] if component_index + 1 < len(parts) - 1 else "core"
            except ValueError:
                category = "core"
            if wanted_categories and category.lower() not in wanted_categories:
                continue

            source = path.read_text(encoding="utf-8", errors="ignore")
            path_text = " ".join(self._tokens(relative.as_posix().replace("-", " ")))
            source_head = source[:5000].lower()
            filename_tokens = set(self._tokens(path.stem.replace("-", " ")))
            path_tokens = set(self._tokens(path_text))

            score = 0.0
            reasons: list[str] = []
            direct_filename = sorted(terms.intersection(filename_tokens))
            direct_path = sorted(terms.intersection(path_tokens))
            if direct_filename:
                score += 5.0 * len(direct_filename)
                reasons.append("filename:" + ",".join(direct_filename[:4]))
            if direct_path:
                score += 2.0 * len(direct_path)
                reasons.append("path:" + ",".join(direct_path[:4]))

            category_terms = set(self._CATEGORY_HINTS.get(category, ()))
            category_match = sorted(terms.intersection(category_terms))
            if category_match:
                score += 2.5 + 0.5 * len(category_match)
                reasons.append("category:" + category)

            source_hits = [term for term in terms if len(term) >= 4 and term in source_head]
            if source_hits:
                score += min(4.0, 0.6 * len(source_hits))
                reasons.append("source:" + ",".join(sorted(source_hits)[:4]))

            deps = self._dependencies(source)
            if "three" in terms and "three" in deps:
                score += 3.0
                reasons.append("dependency:three")
            if "spline" in terms and "spline" in deps:
                score += 3.0
                reasons.append("dependency:spline")
            if "gsap" in terms and "gsap" in deps:
                score += 2.0
                reasons.append("dependency:gsap")

            if score <= 0:
                continue

            candidates.append(
                MotionPrimitiveCandidate(
                    path=relative.as_posix(),
                    category=category,
                    dependencies=deps,
                    score=round(score, 2),
                    reasons=tuple(reasons),
                )
            )

        candidates.sort(key=lambda item: (-item.score, item.path))
        return candidates[:limit]
