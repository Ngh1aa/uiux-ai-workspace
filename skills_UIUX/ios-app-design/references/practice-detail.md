# Thực hành chuyên sâu

Chỉ mở khi cần chi tiết trong mục dưới đây; WORKFLOWS.md vẫn là nguồn định tuyến duy nhất.

# iOS App Design

## Decisions
Read target brand, components, deployment target and current Apple HIG before choosing a pattern. Record whether a control is system-provided or custom and why. Keep app content distinct from system/navigation chrome; avoid replacing working native controls with decorative imitations.

- Separate top-level destinations, pushed details, sheets and destructive confirmations. Specify interactive dismissal, cancellation and draft preservation.
- Account for safe areas, keyboard and system overlays. Primary actions remain reachable with large text and short available height.
- Use semantic text styles and color roles; test Dynamic Type, dark appearance, contrast and Reduce Motion. A system font is not a license to redistribute font files.
- Apple recommends 44×44 **points** for hit targets; visible glyph size and hit area are distinct. CSS px and Android dp are separate units.
- Design VoiceOver names, roles, values, reading order, grouped content and change announcements. Screenshot inspection cannot validate VoiceOver behavior.
- Request permissions in context; specify denied/revoked states and useful fallback paths.

## Spec sheet
Concrete metrics — Dynamic Type ramp, bar heights, safe areas, sheet detents, control sizes, haptics,
Liquid Glass layering and gestures — are in the [iOS spec sheet](../references/ios-spec-sheet.md).
Cross-platform patterns are in the [mobile patterns playbook](../../mobile-app-design/references/mobile-patterns-playbook.md).

## Version and asset boundaries
Select APIs/design resources for the declared OS range; keep availability and fallback notes in handoff. Review current materials such as Liquid Glass only when appropriate to scope, brand and SDK. Do not promise identical appearance across OS versions.

Apple UI kits are link-only sources in the registry. Use them under their own terms; do not vendor or repackage Apple templates, fonts or extracted symbols for Android. Native system symbol usage and redistributed image assets have different rights.

## Output
Produce iOS-specific navigation, component behavior, semantic text/color mapping, accessibility annotations and an OS/test matrix. Use [Apple entries in the shared registry](../../mobile-app-design/data/sources.json); record each adopted decision and its verification path.
