# Prototype Verification & Evidence Contract V1

## Purpose

The Factory's 56-item prototype UI/UX checklist is now treated as a versioned verification registry rather than prose that can be silently interpreted as a pass. Each requirement has an ID, applicability statement, verification mode, evaluator owner, evidence expectation and outcome.

The source checklist remains authoritative for the prototype scope: visual experience and interaction quality for HTML/CSS/JS prototypes, not backend, SEO, legal or production-readiness claims.

## Outcome semantics

The ledger uses five outcomes inspired by W3C ACT Rules Format 1.1:

- `passed`: the applicable test target meets the expectation;
- `failed`: an applicable expectation is not met;
- `inapplicable`: the requirement has no test target in this prototype;
- `cantTell`: evaluation was attempted but available evidence cannot support a conclusion;
- `untested`: no evaluation has been attempted.

Do not collapse `cantTell` or `untested` into pass.

## Traceability and provenance

NASA's Requirements Verification Matrix guidance motivates unique requirement IDs, explicit sources, success criteria and verification methods. Evidence artifacts are SHA-256 hashed and bound to a digest of the generated project. If the project changes, prior evidence belongs to the old digest and must not be treated as proof for the new output.

This follows the same provenance principle described by SLSA: evidence should identify where, when and how an artifact was produced and bind conclusions to the artifact being evaluated.

## Machine status vs final approval

`machine_status` only covers requirements whose evaluator is implemented and marked `machine_required`. It may not be used as a synonym for full checklist completion.

`final_status` is stricter:

- `blocked`: at least one final requirement failed, or a planned evaluator is still unresolved;
- `human_review_required`: all implemented/planned verification is resolved, but human-only requirements remain;
- `approved`: every final-required checklist item is passed or legitimately inapplicable.

The two human-only requirements in V1 are the outsider five-second test and independent human review. AI must never fabricate participant evidence for them.

## V1 automation coverage

V1 intentionally automates only requirements already supported by durable BrowserQA/semantic VisualCritic evidence:

- website/domain type fit;
- anti-generic/AI-template review;
- primary decision-object dominance;
- grid/spacing consistency proxy;
- domain/page-role layout fit;
- domain-relevant media;
- visible distinctiveness;
- representative responsive viewport coverage.

All remaining machine-capable evaluators are declared `planned` and therefore remain `untested`, rather than receiving a false pass.

## Next evaluators

The next implementation layer should add:

1. interaction-state crawler with Playwright traces for hover/focus/pressed/loading/empty/error/success;
2. exact mobile target-size/body-type audit for the prototype-specific 44px/16px expectation;
3. blurred screenshot/squint critic;
4. content stress runner with Vietnamese diacritics and long values;
5. side-by-side production-reference critic;
6. demo-path trace with interaction feedback timing;
7. Workbench human-review record that can resolve manual requirements without letting the model self-certify them.

Playwright trace evidence is preferred for dynamic verification because traces can contain action snapshots, screenshots, DOM snapshots, network logs, metadata and attachments.

## Research sources

- W3C ACT Rules Format 1.1: https://www.w3.org/TR/act-rules-format/
- W3C WCAG-EM 2.0 overview: https://www.w3.org/WAI/test-evaluate/conformance/wcag-em/
- Playwright Trace Viewer: https://playwright.dev/docs/trace-viewer
- SLSA Provenance 1.2: https://slsa.dev/spec/v1.2/provenance
- NASA Requirements Verification Matrix: https://www.nasa.gov/reference/appendix-d-requirements-verification-matrix/
