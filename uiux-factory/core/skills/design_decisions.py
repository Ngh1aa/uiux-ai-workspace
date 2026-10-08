"""Validate design decision integrity, not taste. No model or browser self-grading."""
from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
import struct
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, ValidationError, model_validator
from core.runtime.flow_os.safe_read import SafeReader


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", allow_inf_nan=False)


class Source(StrictModel):
    kind: Literal["user", "rule", "reference", "hypothesis"]
    ref: str = Field(min_length=1, max_length=2000)


class Decision(StrictModel):
    axis: str = Field(min_length=1, max_length=80)
    source: Source
    value: str = Field(min_length=1, max_length=3000)
    rejected_alternative: str = Field(min_length=1, max_length=2000)


class TypeValue(StrictModel):
    size_px: float = Field(gt=0, le=300)
    line_height: float = Field(gt=0, le=3)
    weight: int = Field(ge=100, le=900)


class TypeRoles(StrictModel):
    title: TypeValue
    section: TypeValue
    body: TypeValue
    ui: TypeValue
    meta: TypeValue


class Layout(StrictModel):
    max_width_px: float | None = Field(default=None, gt=0, le=20000)
    columns: int = Field(ge=1, le=24)
    column_gap_px: float = Field(ge=0, le=1000)
    reading_width_ch: float = Field(gt=0, le=200)
    density: Literal['productive', 'mixed', 'expressive']


class Spacing(StrictModel):
    gutter_px: float = Field(ge=0, le=1000)
    section_gap_px: float = Field(ge=0, le=1000)
    group_gap_px: float = Field(ge=0, le=1000)
    component_padding_px: float = Field(ge=0, le=1000)


class Region(StrictModel):
    role: str = Field(min_length=1, max_length=120)
    layout: str = Field(min_length=1, max_length=120)
    contains: list[str] = Field(min_length=1, max_length=20)


class Structure(StrictModel):
    regions: list[Region] = Field(min_length=1, max_length=20)
    relationships: list[tuple[str, str, str]] = Field(min_length=1, max_length=30)
    mobile_layout: str = Field(min_length=1, max_length=300)
    mobile_grouping: list[list[str]] = Field(min_length=1, max_length=20)

    def fingerprint(self) -> str:
        # Ignore section order, labels/alternative ids and prose. Moving unchanged
        # blocks cannot manufacture a second internal composition.
        shape = {
            "regions": sorted((region.role.lower().strip(), region.layout.lower().strip(), tuple(region.contains)) for region in self.regions),
            "relationships": sorted(self.relationships),
            "mobile_layout": self.mobile_layout.lower().strip(),
            "mobile_grouping": sorted(tuple(group) for group in self.mobile_grouping),
        }
        return sha256(json.dumps(shape, sort_keys=True).encode()).hexdigest()


class Composition(StrictModel):
    id: str = Field(min_length=1, max_length=80)
    anchor: str = Field(min_length=1, max_length=300)
    structure: Structure
    proof: str = Field(min_length=1, max_length=5000)
    tradeoff: str = Field(min_length=1, max_length=3000)
    direction: Direction | None = None


class DirectionTypography(StrictModel):
    family: str = Field(min_length=1, max_length=200, description='Display/title family; body reading family remains a separate project decision')
    title: TypeValue
    body: TypeValue
    title_tracking_em: float = Field(ge=-0.15, le=0.3)
    reading_width_ch: float = Field(gt=0, le=120)


class DirectionDensity(StrictModel):
    mode: Literal['productive', 'mixed', 'expressive']
    section_gap_px: float = Field(ge=0, le=1000)
    group_gap_px: float = Field(ge=0, le=1000)
    object_padding_px: float = Field(ge=0, le=1000)


class DirectionObject(StrictModel):
    kind: str = Field(min_length=1, max_length=120)
    information_task: str = Field(min_length=1, max_length=1000)
    anatomy: list[str] = Field(min_length=2, max_length=20)
    reality: Literal['verified', 'illustrative', 'synthetic', 'unknown']


class Direction(StrictModel):
    desktop_typography: DirectionTypography
    mobile_typography: DirectionTypography
    desktop_density: DirectionDensity
    mobile_density: DirectionDensity
    visual_object: DirectionObject


class AxisConstraint(StrictModel):
    axis: Literal['typography', 'density', 'visual_object']
    source: Source
    reason: str = Field(min_length=1, max_length=1000)

    @model_validator(mode='after')
    def user_only(self):
        if self.source.kind != 'user':
            raise ValueError('a fixed direction axis requires an explicit user constraint')
        return self


class ReferenceTransfer(StrictModel):
    reference_id: str = Field(min_length=1, max_length=200)
    source: Source
    action: Literal['ADOPT', 'ADAPT', 'REJECT']
    property: str = Field(min_length=1, max_length=2000)
    reason: str = Field(min_length=1, max_length=2000)
    boundary: str = Field(min_length=1, max_length=2000)


class ComparisonQuestion(StrictModel):
    id: str = Field(min_length=1, max_length=80)
    dimension: Literal['comprehension', 'distinctiveness']
    prompt: str = Field(min_length=1, max_length=1000)
    criteria: list[str] = Field(min_length=1, max_length=8)


class ComparisonProtocol(StrictModel):
    buyer_task: str = Field(min_length=1, max_length=1000)
    held_constant: dict[str, str]
    questions: list[ComparisonQuestion] = Field(min_length=2, max_length=10)

    @model_validator(mode='after')
    def controlled(self):
        required = {'audience', 'content', 'claims', 'cta', 'state', 'assets', 'viewports'}
        if set(self.held_constant) != required or any(not value.strip() for value in self.held_constant.values()):
            raise ValueError('comparison must hold audience/content/claims/cta/state/assets/viewports constant')
        ids = [item.id for item in self.questions]
        if len(ids) != len(set(ids)):
            raise ValueError('comparison question ids must be unique')
        if {item.dimension for item in self.questions} != {'comprehension', 'distinctiveness'}:
            raise ValueError('comparison needs comprehension and distinctiveness questions')
        return self


class ComparisonRecord(StrictModel):
    plan: str = Field(min_length=1, max_length=1000)
    observations: str = Field(min_length=1, max_length=1000)


# Resolve the forward type once all direction models exist.
Composition.model_rebuild()


def direction_differences(first: Direction, second: Direction) -> set[str]:
    """Material, declared differences. Captures/reviewer still own pixel truth."""
    axes = set()
    for viewport in ('desktop', 'mobile'):
        a, b = getattr(first, viewport + '_typography'), getattr(second, viewport + '_typography')
        if (a.family.casefold().strip() != b.family.casefold().strip()
                or abs(a.title.size_px - b.title.size_px) >= max(6, min(a.title.size_px, b.title.size_px) * .15)
                or abs(a.title.weight - b.title.weight) >= 200
                or abs(a.title.line_height - b.title.line_height) >= .15
                or abs(a.reading_width_ch - b.reading_width_ch) >= 10):
            axes.add('typography')
        a, b = getattr(first, viewport + '_density'), getattr(second, viewport + '_density')
        differences = sum(abs(getattr(a, key) - getattr(b, key)) >= max(minimum, min(getattr(a, key), getattr(b, key)) * .2)
                          for key, minimum in [('section_gap_px', 8), ('group_gap_px', 4), ('object_padding_px', 4)])
        if differences >= 2:
            axes.add('density')
    # Renaming a kind or writing different rationale cannot prove object diversity.
    a = tuple(item.casefold().strip() for item in first.visual_object.anatomy)
    b = tuple(item.casefold().strip() for item in second.visual_object.anatomy)
    if sorted(a) != sorted(b):
        axes.add('visual_object')
    return axes


class PageDecision(StrictModel):
    route: str = Field(min_length=1, max_length=1000)
    page_role: str = Field(min_length=1, max_length=120)
    user_question: str = Field(min_length=1, max_length=1000)
    cta: str = Field(min_length=1, max_length=300)
    decisions: list[Decision] = Field(min_length=1, max_length=30)
    desktop_type: TypeRoles
    mobile_type: TypeRoles
    desktop_layout: Layout
    mobile_layout: Layout
    desktop_spacing: Spacing
    mobile_spacing: Spacing
    compositions: list[Composition] = Field(min_length=1, max_length=5)
    selected_composition: str
    comparison_required: bool = True
    inherited_from: str | None = None
    composition_constraint: Source | None = None
    axis_constraints: list[AxisConstraint] = Field(default_factory=list, max_length=3)
    reference_transfers: list[ReferenceTransfer] = Field(default_factory=list, max_length=12)
    comparison_protocol: ComparisonProtocol | None = None
    comparison_record: ComparisonRecord | None = None

    @model_validator(mode="after")
    def check_choices(self):
        axes = {decision.axis for decision in self.decisions}
        missing = {"layout", "font", "typography", "spacing", "media", "voice"} - axes
        if missing:
            raise ValueError("missing material decision traces: " + ", ".join(sorted(missing)))
        ids = [composition.id for composition in self.compositions]
        if len(ids) != len(set(ids)) or self.selected_composition not in ids:
            raise ValueError("composition ids must be unique and selected_composition must exist")
        if self.composition_constraint is not None:
            if self.composition_constraint.kind != "user":
                raise ValueError("only an explicit user constraint may preserve a fixed composition")
        elif self.comparison_required and len({composition.structure.fingerprint() for composition in self.compositions}) < 2:
            raise ValueError("alternatives need distinct internal topology; renamed, skinned or reordered unchanged blocks do not count")
        elif not self.comparison_required and not self.inherited_from:
            raise ValueError("a rollout page must name its representative decision owner in inherited_from")
        return self


class Capture(StrictModel):
    route: str
    composition_id: str
    file: str
    sha256: str = Field(pattern=r"^[a-f0-9]{64}$")
    width: int = Field(ge=1, le=20000)
    viewport_height: int = Field(ge=1, le=20000)
    inspected: Literal[True]
    review_source: Literal["agent-heuristic", "human"]
    critique: dict[str, str]


class DesignDecisions(StrictModel):
    schema_version: Literal["1.0", "2.0"]
    pages: list[PageDecision] = Field(min_length=1, max_length=30)
    captures: list[Capture] = Field(default_factory=list, max_length=200)

    @model_validator(mode="after")
    def unique_routes(self):
        routes = [page.route for page in self.pages]
        if len(routes) != len(set(routes)):
            raise ValueError("page routes must be unique")
        owners = {page.route for page in self.pages if page.comparison_required or page.composition_constraint is not None}
        if not owners:
            raise ValueError("at least one representative comparison or explicit user constraint is required")
        for page in self.pages:
            if not page.comparison_required and page.composition_constraint is None and page.inherited_from not in owners:
                raise ValueError("inherited_from must reference a representative route in this contract")
            if self.schema_version == '2.0':
                if not page.reference_transfers:
                    raise ValueError('v2 pages need a reasoned reference transfer or explicit rejection of a researched reference')
                if any(item.direction is None for item in page.compositions):
                    raise ValueError('v2 compositions need desktop/mobile typography, density and visual object values')
                chosen = next(item.direction for item in page.compositions if item.id == page.selected_composition)
                for viewport in ('desktop', 'mobile'):
                    type_values = getattr(page, viewport + '_type')
                    actual_type = getattr(chosen, viewport + '_typography')
                    spacing_values = getattr(page, viewport + '_spacing')
                    actual_density = getattr(chosen, viewport + '_density')
                    layout_values = getattr(page, viewport + '_layout')
                    if type_values.title != actual_type.title or type_values.body != actual_type.body:
                        raise ValueError('selected direction typography must agree with page numeric values')
                    if (spacing_values.section_gap_px != actual_density.section_gap_px or spacing_values.group_gap_px != actual_density.group_gap_px
                            or spacing_values.component_padding_px != actual_density.object_padding_px or layout_values.density != actual_density.mode
                            or layout_values.reading_width_ch != actual_type.reading_width_ch):
                        raise ValueError('selected direction density/measure must agree with page numeric values')
                if page.comparison_required and page.composition_constraint is None:
                    if page.comparison_protocol is None:
                        raise ValueError('v2 representative pages need a controlled comparison protocol')
                    locked = [item.axis for item in page.axis_constraints]
                    if len(locked) != len(set(locked)):
                        raise ValueError('direction axis constraints must be unique')
                    for axis in locked:
                        keys = ('visual_object',) if axis == 'visual_object' else ('desktop_' + axis, 'mobile_' + axis)
                        values = {json.dumps({key: getattr(item.direction, key).model_dump() for key in keys}, sort_keys=True) for item in page.compositions}
                        if len(values) != 1:
                            raise ValueError('fixed direction axes must be identical across candidates')
                    required = {'typography', 'density', 'visual_object'} - set(locked)
                    if not any(required <= direction_differences(a.direction, b.direction)
                               for index, a in enumerate(page.compositions) for b in page.compositions[index + 1:]):
                        raise ValueError('representative alternatives must materially vary every free typography/density/visual_object axis in one pair')
        return self


def check_design_decisions(payload: dict, *, phase: str = "design", project_root: Path | None = None) -> dict:
    if phase not in {"design", "rendered"}:
        raise ValueError("phase must be design or rendered")
    errors = []
    comparison_reviews = []
    try:
        contract = DesignDecisions.model_validate(payload)
    except ValidationError as error:
        errors = [f"{'.'.join(map(str, item['loc']))}: {item['msg']}" for item in error.errors()]
        contract = None
    if contract is not None and phase == "rendered":
        root = Path(project_root).resolve() if project_root is not None else None
        pages = {page.route: page for page in contract.pages}
        verified = []
        for capture in contract.captures:
            page = pages.get(capture.route)
            if page is None or capture.composition_id not in {composition.id for composition in page.compositions}:
                errors.append(f"capture references unknown route/composition: {capture.route}/{capture.composition_id}")
                continue
            if any(not capture.critique.get(key, '').strip() for key in ("hierarchy", "typography", "spacing", "media", "distinctiveness")):
                errors.append("capture needs concrete critique for hierarchy/type/spacing/media/distinctiveness")
                continue
            try:
                raw_path = Path(capture.file)
                if root is None or raw_path.is_absolute():
                    raise ValueError("capture must be project-relative with an explicit root")
                path = (root / raw_path).resolve()
                path.relative_to(root)
                if path.stat().st_size > 30_000_000:
                    raise ValueError("capture exceeds 30 MB")
                raw = path.read_bytes()
                if sha256(raw).hexdigest() != capture.sha256:
                    raise ValueError("capture digest mismatch")
                if raw[:8] != b'\x89PNG\r\n\x1a\n' or raw[12:16] != b'IHDR' or len(raw) < 33:
                    raise ValueError("capture must be a PNG with dimensions")
                width, height = struct.unpack('>II', raw[16:24])
                if width != capture.width or height < capture.viewport_height:
                    raise ValueError("capture dimensions disagree with viewport")
                verified.append(capture)
            except (OSError, ValueError, struct.error) as error:
                errors.append(f"capture {capture.file}: {error}")
        for page in contract.pages:
            compositions = page.compositions if page.comparison_required else [item for item in page.compositions if item.id == page.selected_composition]
            for composition in compositions:
                captures = [item for item in verified if item.route == page.route and item.composition_id == composition.id]
                if not any(item.width <= 480 for item in captures) or not any(item.width >= 1024 for item in captures):
                    errors.append(f"missing inspected desktop/mobile comparison for {page.route}/{composition.id}")
            widths = {capture.width for capture in verified if capture.route == page.route}
            for width in widths:
                same_viewport = [capture for capture in verified if capture.route == page.route and capture.width == width]
                if len({capture.composition_id for capture in same_viewport}) > len({capture.sha256 for capture in same_viewport}):
                    errors.append(f"identical screenshots cannot establish alternative render evidence at {page.route}/{width}")
        if contract.schema_version == '2.0' and not errors:
            # Local import avoids a model/checker dependency cycle. Capture integrity
            # above is already verified; the comparison reader cannot bypass that gate.
            from core.skills.design_comparison import evaluate_comparison, read_comparison_json
            for page in contract.pages:
                if not page.comparison_required or page.composition_constraint is not None:
                    continue
                if page.comparison_record is None or root is None:
                    errors.append(f'{page.route}: rendered v2 needs comparison_record paths and an explicit root')
                    continue
                try:
                    result = evaluate_comparison(payload, read_comparison_json(root, page.comparison_record.plan),
                                                 read_comparison_json(root, page.comparison_record.observations), root,
                                                 _capture_integrity_verified=True)
                    if result['returncode'] or result['status'] == 'PLANNED_VALIDATION':
                        errors.append(f"{page.route}: comparison must have actual recorded review, not only a plan: {result.get('errors', [])}")
                    elif read_comparison_json(root, page.comparison_record.plan)['route'] != page.route:
                        errors.append(f'{page.route}: comparison plan belongs to another route')
                    comparison_reviews.append({'route': page.route, 'status': result['status'], 'human_review_count': result.get('human_review_count', 0)})
                except (ValueError, OSError) as error:
                    errors.append(f'{page.route}: invalid comparison record: {error}')
    return {
        "status": "FAIL" if errors else "PASS",
        "returncode": 1 if errors else 0,
        "phase": phase,
        "contract_version": contract.schema_version if contract else None,
        "errors": errors,
        "page_count": len(contract.pages) if contract else 0,
        "verification": "DECISION_INTEGRITY_ONLY",
        "aesthetic_quality": "UNKNOWN",
        "human_preference": "UNKNOWN",
        "comparison_reviews": comparison_reviews,
        "direction_comparison": 'LEGACY_LAYOUT_ONLY' if contract and contract.schema_version == '1.0' else 'MULTI_AXIS_DECLARED' if contract else 'UNKNOWN',
    }


def check_design_file(project_root: Path, relative_path: str, phase: str = "design") -> dict:
    root = Path(project_root).resolve()
    loaded = SafeReader(root).read_text(relative_path)
    if len(loaded.content) > 512_000:
        raise ValueError("design decision contract exceeds 512000 chars")
    result = check_design_decisions(json.loads(loaded.content), phase=phase, project_root=root)
    result["contract_sha256"] = sha256(loaded.content.encode('utf-8')).hexdigest()
    result["path"] = relative_path
    return result
