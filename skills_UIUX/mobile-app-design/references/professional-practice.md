# Mobile research → design → prototype → handoff

## Intake and evidence
Record product problem, top task, platform/OS range, stack, current app/source/design system, requested output and authority. Inventory real screens and states before exporting or redesigning. If a baseline is absent, record it rather than inventing an audit. Preserve existing content, brand and uncommitted work.

Research questions should change a design decision: navigation discoverability, task recovery, permission trust, reading/entry context or device constraints. Use real participant methods when access exists; otherwise provide desk evidence and labelled expert scenarios. Never invent users, quotes or impact.

## Reference transfer
Start with platform guidance; supplement with the smallest relevant code/sample/skill source. Use `data/sources.json` through the parent skill; verify the linked version when adopting time-sensitive APIs.

Record `source → observation → interpretation → ADOPT/ADAPT/REJECT → screen/state/component → verification`. A current repo commit or a skill's license does not establish UX effectiveness. UI-kit licenses and code licenses do not automatically cover fonts/images.

## Screen and state design
Create one navigation graph and screen/state inventory. Prototype the primary task, a consequential failure and recovery. Record permissions, auth, offline/sync, background/resume and deep-link paths when relevant. Identify shared business/content state and platform-specific presentation.

Preserve content and task outcomes while comparing unresolved interaction or visual hypotheses. Avoid arbitrary counts of alternatives. Keep iOS and Android navigation, native controls, text scaling, insets and assistive-technology behavior explicit. Reuse existing components; new variants need a concrete role.

## Handoff and verification
Deliver design contract, token/component mapping, annotated task prototype, platform differences, data/API reality, source/asset licenses, native QA plan and known issues. One artifact may satisfy multiple work-card items. The shared `check-delivery.py` checks current file records/hashes only; it does not certify decisions, rendered quality, user preference or stage completion.

This release of the mobile capability is design/prototype planning and review. Native implementation requests fail closed because no native implementation runner is installed. A later implementation task must choose a compatible adapter and produce native evidence. Existing authority/approval controls still apply to writing target files, Figma mutation, paid services and release.

## Using the canonical ingress
For a design package whose local artifacts may be written within the granted scope:

```bash
python -B skills_UIUX/scripts/prepare-external-task.py \
  --repository owner/app --target-root /path/to/app \
  --task "Thiết kế UI UX app mobile iOS Android; chỉ thiết kế và handoff" \
  --platform-family mobile_app --requested-output design \
  --target-platform ios --target-platform android \
  --authority branch_write --output external-task-manifest.json
```

Use `--authority read_only` for research/review of an existing app. The manifest remains `READY_FOR_EXTERNAL_COLLABORATOR`, not a design/native QA pass. Structured `.uiux-profile.json` may identify `platform_family`, `target_platforms` and `implementation_stack`; it cannot choose the user's requested output, grant authority or waive evidence. Unknown stack/OS remain declared gaps.

The shared manager uses the same interpreter, target truth, planner and work cards. It does not need a separate mobile OS/runtime-policy file. A responsive website remains on the existing web flows. For mixed web/app work, route separate existing work segments rather than treating one platform's evidence as proof of the other.

## Interactive browser demo for clients

Use `--platform-family mobile_app --requested-output browser-prototype` when the output is a coded mobile prototype opened by link. The [browser preview skill](../../mobile-web-preview/SKILL.md) owns renderer/state reuse, phone/desktop presentation, static-host export, browser QA and client handoff. Native output remains a separate unsupported implementation request. Target metadata cannot select this output or authorize publication; pass the requested output and current caller grant explicitly.

```bash
python -B skills_UIUX/scripts/prepare-external-task.py \
  --repository owner/app --target-root /path/to/app \
  --task "Thiết kế mobile app iOS Android và tạo prototype chạy trên trình duyệt cho khách bấm thử" \
  --platform-family mobile_app --requested-output browser-prototype \
  --target-platform ios --target-platform android \
  --authority branch_write --output external-task-manifest.json
```

This prepares the routed task packet, not the app itself. Execute its active stages with the authorized collaborator. `branch_write` prepares source/hosting assets; actual publication and a verified client URL require the existing release authorization and deployment-truth checks.
