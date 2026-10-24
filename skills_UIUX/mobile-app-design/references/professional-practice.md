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

## Giao việc thiết kế app
Khi nhờ Claude thiết kế app, nêu rõ ba điều: nền tảng (iOS, Android hay cả hai), đầu ra (chỉ thiết kế và handoff, hay prototype chạy trên trình duyệt) và app mới hay app đang có. Claude dùng flow `mobile-app-design` cho thiết kế, `mobile-app-audit` khi chỉ soát. Thiếu thông tin nền tảng thì ghi là chưa biết, không tự đoán.

Một trang web responsive vẫn đi theo flow web. Việc vừa web vừa app thì tách thành hai phần, bằng chứng của nền tảng này không thay cho nền tảng kia.

## Interactive browser demo for clients

Use flow `mobile-web-preview` when the output is a coded mobile prototype opened by link. The [browser preview skill](../../mobile-web-preview/SKILL.md) owns renderer/state reuse, phone/desktop presentation, static-host export, browser QA and client handoff. Native output remains a separate unsupported implementation request.

Publishing the prototype to a public link is a separate step; check the live URL in a real browser before sending it to a client.
