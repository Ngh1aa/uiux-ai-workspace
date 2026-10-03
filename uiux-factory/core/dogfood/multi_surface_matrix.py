from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ExpectedSegment:
    phase: str
    intent: str
    scope: tuple[str, ...]
    surface: str
    flow_id: str
    active_stage: str


@dataclass(frozen=True)
class MultiSurfaceCase:
    case_id: str
    family: str
    goal: str
    expected_mode: str
    expected_segments: tuple[ExpectedSegment, ...] = ()
    preserve_contains: tuple[str, ...] = ()
    forbidden_contains: tuple[str, ...] = ()

    def validate(self) -> None:
        if not self.case_id.strip() or not self.family.strip() or not self.goal.strip():
            raise ValueError("P1.4 case id, family and goal are required")
        if self.expected_mode not in {"single", "sequence"}:
            raise ValueError(f"{self.case_id}: invalid expected mode {self.expected_mode}")
        if self.expected_mode == "sequence" and len(self.expected_segments) < 2:
            raise ValueError(f"{self.case_id}: sequence cases require at least two segments")
        if self.expected_mode == "single" and self.expected_segments:
            raise ValueError(f"{self.case_id}: single controls must not declare segment expectations")


def seg(phase: str, intent: str, scope: tuple[str, ...], surface: str, flow_id: str, active_stage: str) -> ExpectedSegment:
    return ExpectedSegment(phase, intent, scope, surface, flow_id, active_stage)


CASES: tuple[MultiSurfaceCase, ...] = (
    MultiSurfaceCase(
        case_id="lifecycle-page-comma",
        family="lifecycle-chain",
        goal="Audit the landing page, redesign checkout, implement it, and QA it.",
        expected_mode="sequence",
        expected_segments=(
            seg("audit", "improve", ("landing-page",), "PAGE", "page-ui-work", "research"),
            seg("design", "redesign", ("checkout",), "PAGE", "page-ui-work", "design"),
            seg("implementation", "redesign", ("checkout",), "PAGE", "page-ui-work", "implementation"),
            seg("qa", "redesign", ("checkout",), "PAGE", "page-ui-work", "qa"),
        ),
    ),
    MultiSurfaceCase(
        case_id="lifecycle-focused",
        family="lifecycle-chain",
        goal="Review the hero, fix hero spacing, implement it, verify it.",
        expected_mode="sequence",
        expected_segments=(
            seg("audit", "improve", ("hero",), "FOCUSED", "existing-ui-improvement", "research"),
            seg("design", "fix", ("hero",), "FOCUSED", "existing-ui-improvement", "implementation"),
            seg("implementation", "fix", ("hero",), "FOCUSED", "existing-ui-improvement", "implementation"),
            seg("qa", "fix", ("hero",), "FOCUSED", "existing-ui-improvement", "qa"),
        ),
    ),
    MultiSurfaceCase(
        case_id="lifecycle-whole-product-arrow",
        family="lifecycle-chain",
        goal="Audit first → redesign the whole product → implement it → QA it.",
        expected_mode="sequence",
        expected_segments=(
            seg("audit", "redesign", (), "PRODUCT", "professional-website-redesign", "research"),
            seg("design", "redesign", (), "PRODUCT", "professional-website-redesign", "design"),
            seg("implementation", "redesign", (), "PRODUCT", "professional-website-redesign", "implementation"),
            seg("qa", "redesign", (), "PRODUCT", "professional-website-redesign", "qa"),
        ),
    ),
    MultiSurfaceCase(
        case_id="lifecycle-whole-site",
        family="lifecycle-chain",
        goal="Audit the whole website; redesign the whole website; implement it; visual QA it.",
        expected_mode="sequence",
        expected_segments=(
            seg("audit", "redesign", (), "REDESIGN", "professional-website-redesign", "research"),
            seg("design", "redesign", (), "REDESIGN", "professional-website-redesign", "design"),
            seg("implementation", "redesign", (), "REDESIGN", "professional-website-redesign", "implementation"),
            seg("qa", "redesign", (), "REDESIGN", "professional-website-redesign", "qa"),
        ),
    ),
    MultiSurfaceCase(
        case_id="mixed-focused-page-preserve",
        family="mixed-surface",
        goal="Fix hero typography and redesign checkout. Keep animation unchanged.",
        expected_mode="sequence",
        expected_segments=(
            seg("design", "fix", ("hero", "typography"), "FOCUSED", "existing-ui-improvement", "implementation"),
            seg("design", "redesign", ("checkout",), "PAGE", "page-ui-work", "design"),
        ),
        preserve_contains=("animation",),
    ),
    MultiSurfaceCase(
        case_id="mixed-page-focused-order",
        family="mixed-surface",
        goal="Redesign checkout and fix hero typography, preserve animation unchanged.",
        expected_mode="sequence",
        expected_segments=(
            seg("design", "redesign", ("checkout",), "PAGE", "page-ui-work", "design"),
            seg("design", "fix", ("hero", "typography"), "FOCUSED", "existing-ui-improvement", "implementation"),
        ),
        preserve_contains=("animation",),
    ),
    MultiSurfaceCase(
        case_id="mixed-micro-page",
        family="mixed-surface",
        goal="Fix the CTA button and redesign checkout.",
        expected_mode="sequence",
        expected_segments=(
            seg("design", "fix", ("button",), "MICRO", "micro-ui-change", "implementation"),
            seg("design", "redesign", ("checkout",), "PAGE", "page-ui-work", "design"),
        ),
    ),
    MultiSurfaceCase(
        case_id="mixed-focused-page-lifecycle",
        family="mixed-surface",
        goal="Improve mobile navigation, redesign homepage, implement it, QA it.",
        expected_mode="sequence",
        expected_segments=(
            seg("design", "improve", ("mobile-nav", "navigation"), "FOCUSED", "existing-ui-improvement", "implementation"),
            seg("design", "redesign", ("homepage",), "PAGE", "page-ui-work", "design"),
            seg("implementation", "redesign", ("homepage",), "PAGE", "page-ui-work", "implementation"),
            seg("qa", "redesign", ("homepage",), "PAGE", "page-ui-work", "qa"),
        ),
    ),
    MultiSurfaceCase(
        case_id="two-focused-owners",
        family="mixed-surface",
        goal="Fix the hero and fix mobile navigation.",
        expected_mode="sequence",
        expected_segments=(
            seg("design", "fix", ("hero",), "FOCUSED", "existing-ui-improvement", "implementation"),
            seg("design", "fix", ("mobile-nav", "navigation"), "FOCUSED", "existing-ui-improvement", "implementation"),
        ),
    ),
    MultiSurfaceCase(
        case_id="constraints-global-inheritance",
        family="constraints",
        goal="Fix the hero and redesign checkout; keep animation unchanged; do not change navigation.",
        expected_mode="sequence",
        expected_segments=(
            seg("design", "fix", ("hero",), "FOCUSED", "existing-ui-improvement", "implementation"),
            seg("design", "redesign", ("checkout",), "PAGE", "page-ui-work", "design"),
        ),
        preserve_contains=("animation",),
        forbidden_contains=("navigation",),
    ),
    MultiSurfaceCase(
        case_id="audit-qa-no-design",
        family="lifecycle-chain",
        goal="Audit checkout, then QA checkout.",
        expected_mode="sequence",
        expected_segments=(
            seg("audit", "improve", ("checkout",), "PAGE", "page-ui-work", "research"),
            seg("qa", "improve", ("checkout",), "PAGE", "page-ui-work", "qa"),
        ),
    ),
    MultiSurfaceCase(
        case_id="implement-qa-no-design",
        family="lifecycle-chain",
        goal="Implement checkout, then QA checkout.",
        expected_mode="sequence",
        expected_segments=(
            seg("implementation", "build", ("checkout",), "PAGE", "page-ui-work", "implementation"),
            seg("qa", "improve", ("checkout",), "PAGE", "page-ui-work", "qa"),
        ),
    ),
    MultiSurfaceCase(
        case_id="vi-lifecycle",
        family="localization",
        goal="Rà soát hero → cải thiện hero → triển khai → kiểm thử.",
        expected_mode="sequence",
        expected_segments=(
            seg("audit", "improve", ("hero",), "FOCUSED", "existing-ui-improvement", "research"),
            seg("design", "improve", ("hero",), "FOCUSED", "existing-ui-improvement", "implementation"),
            seg("implementation", "improve", ("hero",), "FOCUSED", "existing-ui-improvement", "implementation"),
            seg("qa", "improve", ("hero",), "FOCUSED", "existing-ui-improvement", "qa"),
        ),
    ),
    MultiSurfaceCase(
        case_id="vi-mixed-surface",
        family="localization",
        goal="Sửa hero và thiết kế lại checkout, giữ nguyên animation.",
        expected_mode="sequence",
        expected_segments=(
            seg("design", "redesign", ("hero",), "FOCUSED", "existing-ui-improvement", "implementation"),
            seg("design", "redesign", ("checkout",), "PAGE", "page-ui-work", "design"),
        ),
        preserve_contains=("animation",),
    ),
    MultiSurfaceCase(
        case_id="single-redesign-checkout",
        family="single-control",
        goal="Redesign checkout and keep animation unchanged.",
        expected_mode="single",
        preserve_contains=("animation",),
    ),
    MultiSurfaceCase(
        case_id="single-fix-hero",
        family="single-control",
        goal="Fix the existing hero spacing only.",
        expected_mode="single",
    ),
    MultiSurfaceCase(
        case_id="single-whole-product",
        family="single-control",
        goal="Redesign the whole product while preserving the current design system.",
        expected_mode="single",
        preserve_contains=("current design system",),
    ),
)


def validate_matrix() -> None:
    ids: set[str] = set()
    for case in CASES:
        case.validate()
        if case.case_id in ids:
            raise ValueError(f"duplicate P1.4 case id: {case.case_id}")
        ids.add(case.case_id)
