# EdTech integrations: LTI 1.3 context, roles and service boundaries

Source basis: 1EdTech Learning Tools Interoperability (LTI), with LTI 1.3 identified by 1EdTech as the current version and LTI Advantage built on LTI 1.3.

## Reusable reference

LTI defines an interoperability boundary between a learning platform such as an LMS and an external learning tool. It is useful product context because the platform and tool may exchange launch context, user role information and service-level data while remaining separate systems with separate ownership.

For product framing, keep this distinction explicit:

```text
learning platform / LMS ↔ LTI boundary ↔ external learning tool
```

Do not collapse that boundary into a generic “integration connected” state. A launch can carry organizational or course context and roles that affect what the receiving tool may present or do, but project truth still determines which roles, permissions and data are actually configured.

## LTI Advantage service concepts

LTI Advantage adds three core service concepts that are useful when naming product states or integration responsibilities:

- **Assignment and Grade Services (AGS):** supports gradebook-related exchange such as creating a gradebook column and posting grades associated with a resource link.
- **Names and Role Provisioning Services (NRPS):** provides user and role data for an organization context such as a school, platform or course.
- **Deep Linking:** lets a platform user select content from an external tool and receive launchable content back into the learning environment.

These are protocol/service semantics, not UI recipes. Their presence can clarify whether a product surface is showing roster/context data, grade exchange, or content selection, but the interface still needs project-specific states, permissions, consent/privacy decisions and failure handling.

## Product application guidance

When an EdTech product depends on LTI, verify product copy and system-state labels against the actual integration boundary. Useful questions include:

```text
Which side owns the current action: platform or tool?
What context was supplied for this launch?
Which user role is represented in this context?
Which LTI Advantage service, if any, owns the data exchange?
What remains project-specific configuration rather than standard behavior?
```

Do not claim that LTI participation alone proves a specific UX, institution policy, security posture, certification status or data-sharing configuration. LTI 1.3 uses a modern security model, but implementation/security procedure remains outside this record.

## Scope boundary

This record is domain/reference context only. It does not define education-site information architecture, admissions journeys, authentication engineering, privacy policy, generic UX flows or QA methodology. Those remain owned by routed skills, project requirements and implementation evidence.

## Why this belongs in Knowledge OS

The platform/tool distinction, launch context/roles and LTI Advantage service vocabulary are reusable EdTech facts that can improve terminology and ownership reasoning across research, design, implementation and QA without duplicating the procedural education or security skills.
