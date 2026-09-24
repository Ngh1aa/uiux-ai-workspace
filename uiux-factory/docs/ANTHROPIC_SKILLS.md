# Anthropic Skills Integration

The Factory pins the official `anthropics/skills` repository as a Git submodule so bundled scripts, examples, references and binary resources remain available exactly as upstream shipped them.

## Initialize

After cloning this repository:

```bash
git submodule update --init --recursive
```

Verify the pinned revision and required runtime/meta-tool resources:

```bash
cd uiux-factory
python scripts/verify_anthropic_skills.py
```

## Pinned revision

- Upstream: `https://github.com/anthropics/skills`
- Revision: `41bbe19d1a1a7eaab5e7bb9050a417e5c6cffc8f`
- Local path: `skills_UIUX/upstream/anthropic-skills`

Do not edit upstream files in-place. Make Factory-specific routing or adapters outside the submodule, then update the pinned revision deliberately when upstream changes are reviewed. CI checks both the submodule revision and the required scripts/assets, including the binary shadcn component bundle used by `web-artifacts-builder`.

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

The complete upstream skill folder remains available through the pinned submodule, including agents, references, eval viewer, benchmark/report scripts, packaging/validation utilities and assets. The Factory verifier checks the resources required for this integration rather than copying or modifying them.

## VisualCritic v4

VisualCritic separates three evidence classes:

1. Browser/runtime evidence: overflow, links, page errors, responsive smoke and screenshot existence.
2. Semantic visual evidence: actual screenshot interpretation against website type, vertical, page role, decision-object dominance, media relevance, hierarchy, distinctiveness and generic-AI tells.
3. Evidence integrity: every representative screenshot route must be reviewed exactly once and every scored route must cite concrete visible evidence.

The semantic class uses the existing bounded free-provider configuration through a multimodal adapter. Screenshot bytes are resized and encoded in memory only; image payloads are not stored in provider history.

By default, proxy-only visual metrics are **not sufficient for PASS**. If no configured free-tier model accepts screenshot input, VisualCritic returns `blocked` rather than claiming it inspected aesthetics.

An owner can explicitly accept weaker proxy-only behavior with:

```text
UIUX_ALLOW_PROXY_VISUAL_PASS=1
```

That escape hatch should not be used for final visual acceptance when domain/page-role quality matters.

### Domain visual acceptance profiles

`core/domain_visual_profiles.py` resolves a rubric from `website_type + vertical`. The profile is a task-specific acceptance policy, not a layout template. It changes the importance and thresholds of media relevance, decision-object dominance, page-role fit, distinctiveness and generic-AI detection according to the type of site.

Examples:

- luxury fragrance ecommerce: fragrance/product/media identity, sensory discovery, strong PLP/PDP distinction and strict card-soup rejection;
- electronics ecommerce: comparison/specification evidence may legitimately be denser and media is not the only decision signal;
- hospitality/hotel: credible property/room/destination imagery carries a higher media requirement;
- news: editorial priority and headline hierarchy matter more than promotional card uniformity;
- government: task clarity and service completion outrank visual novelty or image density;
- portfolio: work evidence and distinctiveness are deliberately held to a higher visual bar.

The semantic model receives this profile with the screenshots. The returned scores are then checked again by deterministic policy code, so a model cannot bypass a strict vertical rule merely by forgetting to set `blocking_generic=true`.

### Complete screenshot coverage gate

A semantic review cannot PASS when it:

- omits a supplied representative route;
- invents an unsupplied route;
- duplicates route reviews;
- returns route scores without concrete visible screenshot evidence.

The VisualCritic result exposes explicit gates for semantic route coverage, grounded evidence and domain-policy application. Aggregate score is capped below PASS when evidence coverage is incomplete.

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

For luxury fragrance, the critic is specifically instructed and deterministically policy-checked not to accept clean generic SaaS/card layouts merely because spacing and typography are technically competent. Repair should return to the owning art-direction/composition decision instead of stacking another cosmetic CSS override.
