# Anthropic Skills Integration

The Factory pins the official `anthropics/skills` repository as a Git submodule so bundled scripts, examples, references and binary resources remain available exactly as upstream shipped them.

## Initialize

After cloning this repository:

```bash
git submodule update --init --recursive
```

Verify the required resources:

```bash
cd uiux-factory
python scripts/verify_anthropic_skills.py
```

## Pinned revision

- Upstream: `https://github.com/anthropics/skills`
- Revision: `41bbe19d1a1a7eaab5e7bb9050a417e5c6cffc8f`
- Local path: `skills_UIUX/upstream/anthropic-skills`

Do not edit upstream files in-place. Make Factory-specific routing or adapters outside the submodule, then update the pinned revision deliberately when upstream changes are reviewed.

## Runtime routing

### frontend-design

Used in:

- Art Direction
- Visual Composition
- Frontend Implementation
- Visual QA
- Root-cause Repair

Its role is aesthetic discipline: ground choices in subject matter, resist templated defaults, critique generic visual grammar before code, and challenge AI-slop/card-soup from rendered evidence.

### webapp-testing

Used in:

- Browser QA
- Visual QA

BrowserQA remains the Factory's canonical execution engine, while the upstream skill supplies reconnaissance-first testing discipline and bundled Playwright/server helpers.

### web-artifacts-builder

Used only for `interactive-prototype` implementation when the brief implies complex state/workflow features such as authentication, dashboards, forms or search. It is not a universal frontend stack and must not force Tailwind/shadcn visual grammar onto unrelated sites.

### skill-creator

Meta-system only. It is intentionally discoverable but not injected into ordinary website stages. Use it when creating or improving `skills_UIUX`: run with-skill versus baseline evaluations, qualitative review and quantitative benchmarks before changing trigger descriptions or skill behavior.

## VisualCritic v3

VisualCritic v3 separates two evidence classes:

1. Browser/runtime evidence: overflow, links, page errors, responsive smoke and screenshot existence.
2. Semantic visual evidence: actual screenshot interpretation against website type, vertical, page role, decision-object dominance, media relevance, hierarchy, distinctiveness and generic-AI tells.

The second class uses the existing bounded free-provider configuration through a multimodal adapter. Screenshot bytes are resized and encoded in memory only; image payloads are not stored in provider history.

By default, proxy-only visual metrics are **not sufficient for PASS**. If no configured free-tier model accepts screenshot input, VisualCritic returns `blocked` rather than claiming it inspected aesthetics.

An owner can explicitly accept weaker proxy-only behavior with:

```text
UIUX_ALLOW_PROXY_VISUAL_PASS=1
```

That escape hatch should not be used for final visual acceptance when domain/page-role quality matters.

## Free multimodal provider configuration

VisualCritic uses the same local `.env.local` policy as `FreeProvider`:

- `UIUX_FREE_TIER_CONFIRMED=1`
- `UIUX_CLOUD_PROVIDERS=...`
- matching provider API key(s)
- matching `UIUX_<PROVIDER>_MODEL`
- optional `UIUX_PROVIDER_VISUAL_QA=<provider>`

The configured model itself must support image input. A text-only model is skipped/rejected and cannot establish semantic visual PASS.

## Anti-generic hard gate

Semantic review may block PASS when rendered evidence shows, for example:

- materially different page roles collapsing into one repeated composition;
- interchangeable rounded-card/SaaS grammar unrelated to the domain;
- weak or visually secondary primary decision objects;
- generic or irrelevant media;
- visible domain identity that could be relabelled for another industry without meaningful redesign.

For luxury fragrance, the critic is specifically instructed not to accept clean generic SaaS/card layouts merely because spacing and typography are technically competent. Repair should return to the owning art-direction/composition decision instead of stacking another cosmetic CSS override.
