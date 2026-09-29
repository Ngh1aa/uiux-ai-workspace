# A37 — Real-project external-agent E2E dogfood

A37 validates the A33/A35/A36 infrastructure as one connected pipeline against a pinned real project: `Ngh1aa/cennext-b2b-prototype@273403accf8979608fbb16dbe2741cedb0430fb6`.

## Why CENNEXT

CENNEXT is a static B2B/enterprise project, intentionally different from Nova. It already contains a component-state handoff page, so Factory can verify real target markup without adding synthetic application behavior.

The target currently exposes Default, Disabled, Error, Success, Saved/Selected and other interaction specimens. It does **not** expose an asynchronous Loading specimen. A37 therefore does not fabricate one merely to satisfy a canonical five-state list.

## Pipeline

The workflow `.github/workflows/a37-external-agent-e2e-dogfood.yml` performs:

1. exact-SHA checkout of Factory and CENNEXT;
2. GitHub-native external-agent task packet compilation;
3. existing A14 real-project source audit at the same target SHA;
4. browser evidence on the real `component-states.html` route;
5. semantic State Coverage across desktop/tablet/mobile using the Factory-owned dogfood adapter contract;
6. automatic rendered matrix generation;
7. A35 Deployment Truth evaluation;
8. A36 release evidence registry generation with artifact hashes and cross-gate claim state;
9. assertions that the final registry preserves truth boundaries.

## Deployment boundary intentionally tested

A37 does not have trusted provider/API metadata proving which source SHA is currently served by a production provider. Therefore the expected deployment classification is `READY_BUT_NOT_DEPLOYED`, not `DEPLOYED_VERIFIED`.

This is a feature of the dogfood, not a missing assertion: the purpose is to prove that a green local/browser/state pipeline cannot silently manufacture deployment proof. A real `DEPLOYED_VERIFIED` claim still requires provider-reported deployment SHA + ready status + production route 2xx through A35.

## Completion criteria

A37 passes only when:

- target checkout SHA exactly matches the pinned source;
- external-agent packet truthfully reports `invokes_llm_provider=false`;
- real-project source audit passes;
- browser evidence route is healthy;
- semantic State Coverage passes at all declared viewports and matrix is generated;
- deployment truth remains the expected bounded unresolved classification without provider SHA;
- release evidence registry hashes the produced artifacts;
- state coverage is `VERIFIED`, deployment truth stays `UNKNOWN`, and overall release readiness stays `UNKNOWN` instead of being fabricated.
