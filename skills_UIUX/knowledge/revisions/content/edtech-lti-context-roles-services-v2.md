# EdTech integrations: LTI 1.3 service truth, concrete states and recovery boundaries

Source basis: 1EdTech Learning Tools Interoperability (LTI), with LTI 1.3 identified by 1EdTech as the current version and LTI Advantage built on LTI 1.3.

## Reusable reference

LTI defines an interoperability boundary between a learning platform such as an LMS and an external learning tool. Keep the two systems distinct:

```text
learning platform / LMS ↔ LTI boundary ↔ external learning tool
```

A successful launch proves only that a launch path completed. It does not prove that roster access, grade exchange or content selection are configured. Project truth must establish which roles, services and data exchanges exist.

## LTI Advantage service concepts

- **Assignment and Grade Services (AGS):** gradebook-related exchange such as line-item/grade operations associated with a resource link.
- **Names and Role Provisioning Services (NRPS):** user and role data for an organizational context such as a course.
- **Deep Linking:** selection of tool-provided content for insertion into the learning environment.

These service concepts help name product states and ownership boundaries, but do not prescribe page layout, institutional role taxonomy, permission policy or recovery UI.

## Concrete product-state boundaries

Use only states that the project's configured integration can actually distinguish. A useful minimum model is:

### Launch

```text
ready_to_launch
launching
launched
launch_unavailable
launch_failed
```

- `launched` must be backed by a successful platform→tool launch result.
- `launch_unavailable` should mean the required integration/configuration is not available for the current context; it must not imply the user caused the problem.
- `launch_failed` should not silently become `launched` because a generic page or fallback view rendered.

Recovery guidance should route users toward the product's configured support/admin path when the failure is configuration-owned. Retry should only be offered when the product can safely repeat the launch attempt.

### NRPS / roster-context access

```text
roster_available
roster_unavailable
roster_permission_or_role_limited
roster_error
```

Do not display a populated-roster affordance merely because the product uses LTI 1.3. `roster_available` requires project truth that NRPS is configured and the current context/role can use it.

When unavailable or limited, preserve the distinction between:

```text
service not configured
service configured but current role/context cannot use it
service request failed or returned no usable result
```

Recovery copy should state what the product actually knows and direct the user to the configured support/admin path when configuration or role assignment must change.

### Deep Linking / content selection

```text
content_selection_available
content_selection_unavailable
content_selection_cancelled
content_selection_failed
content_selected
```

A tool launch is not proof that Deep Linking is available. `content_selected` should mean the platform received a usable selection result for the project flow. Cancellation should remain distinct from failure.

If content selection is not configured, do not present a dead selection control. If selection fails, preserve the user's surrounding LMS context and offer retry only when the integration supports a repeatable selection attempt.

### AGS / grade exchange

```text
grade_exchange_available
grade_exchange_unavailable
grade_send_pending
grade_send_succeeded
grade_send_failed
```

Do not turn a local grade value into `grade_send_succeeded` without a project-backed result from the grade-exchange path. A successful tool launch or completed learner activity does not prove grade return succeeded.

For pending/failed exchange, preserve the distinction between the learner/activity result and the external grade-exchange status. Recovery should avoid telling users to repeat learning work when the problem is an integration/configuration failure. Retry/resubmit controls should appear only when the product's implementation supports them safely.

## Source-of-truth matrix

For each enabled LTI capability, product design should record:

```text
visible state
→ authoritative system / observation
→ configured service required
→ role/context constraint
→ unavailable/error meaning
→ safe recovery path
```

Examples:

```text
roster_available
→ platform/tool integration result
→ NRPS
→ configured role/context
→ not inferred from launch success
→ configured admin/support path if unavailable

content_selected
→ Deep Linking return/result
→ Deep Linking
→ configured authoring role/context
→ cancellation ≠ failure
→ preserve LMS context; retry only when supported

grade_send_succeeded
→ grade-exchange result
→ AGS
→ configured assignment/grade context
→ local grade ≠ remote exchange success
→ retry/resubmit only when implementation supports it
```

## Recovery principles specific to this reference

- Name the integration-owned failure instead of blaming the user.
- Preserve the user's LMS/course context when an external-tool capability fails.
- Separate `not configured`, `not permitted for this role/context`, `temporarily failed`, and `unknown` when the implementation can distinguish them.
- Prefer an explicit unknown/unconfirmed state to implying that a service succeeded.
- Never infer NRPS, AGS or Deep Linking support from LTI 1.3 membership alone.

## Scope boundary

This record is domain/reference context only. It does not define generic empty/error/retry patterns, education-site IA, admissions journeys, authentication engineering, privacy policy or institution-specific support workflows. Routed UX skills still own general state design and recovery methodology; project requirements and implementation evidence own the actual controls, copy and retry behavior.

## Why this belongs in Knowledge OS

The revision keeps the reusable LTI facts—platform/tool ownership, launch context/roles, and AGS/NRPS/Deep Linking semantics—but makes them more decision-useful by showing which concrete product states must remain separate and what evidence/recovery boundary each state requires. It still does not turn the standard into a UI recipe.
