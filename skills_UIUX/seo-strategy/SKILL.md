---
name: seo-strategy
description: Designs and verifies technical/on-page SEO implementation: crawl/index controls, canonical/hreflang, metadata, structured data, internal linking, URL migration, sitemaps/robots and search-performance technical checks. Use when implementing or auditing SEO in the site; search-demand-and-content-briefing owns live demand research and content briefs.
---

# SEO Strategy

## Boundary

This skill owns **technical/on-page search implementation and verification**.

`search-demand-and-content-briefing` owns current keyword/query demand, question maps and writer/page briefs. `information-architecture` owns canonical navigation/taxonomy/page roles. `web-quality-and-performance` owns measured performance budgets/CWV evidence.

## Workflow

### 1. Detect project reality first

Inspect framework/router/rendering, localization, CMS/data ownership, deployment/domain setup and existing SEO conventions before editing. Reuse framework-native metadata/sitemap/schema mechanisms where appropriate.

### 2. Indexability and URL intent

For every material route/page family determine:

- should it be indexable?
- canonical URL and duplicate/parameter behavior;
- locale/hreflang behavior when multilingual;
- pagination/faceted/search handling when applicable;
- redirect/migration requirement for changed URLs;
- whether content is actually rendered/crawlable in the deployed architecture.

Do not generate `robots.txt`, `noindex`, canonicals or redirects from a generic template without project intent.

### 3. Page metadata

Define unique, useful:
- document title;
- meta description when appropriate;
- canonical;
- robots directive when needed;
- Open Graph/social metadata;
- language/alternate annotations.

Search engines can rewrite titles/descriptions; character counts are display heuristics, not hard guarantees. Optimize for accurate intent and distinctiveness rather than rigid universal lengths.

### 4. Structured data

Add schema only when:
- the page content genuinely supports the entity/type;
- required/recommended properties can be supplied truthfully;
- markup matches visible/current content;
- current official search/schema guidance is checked when eligibility matters.

Do not fabricate ratings, FAQs, organization details, contact points or other properties.

### 5. Internal linking and discovery

Ensure important public pages are reachable through meaningful navigation/contextual links and represented appropriately in sitemap(s). Use descriptive link text where useful; do not impose arbitrary “N links per page” quotas.

Check orphan pages, broken routes, redirect chains and canonical inconsistencies.

### 6. Sitemap / robots

Generate from actual public-route reality where possible. `robots.txt` controls crawling, not guaranteed de-indexing. Do not hide sensitive/private content with robots rules; use proper authentication/access control.

### 7. SEO + UX/content handoff

Search intent should influence page role/content priority without producing keyword-stuffed UI. When demand evidence is needed, route `search-demand-and-content-briefing`. When copy/argument needs persuasion, route `conversion-and-content`.

### 8. Verification

Depending on scope:
- inspect rendered `<head>` / framework metadata output;
- validate canonical/hreflang/robots on representative routes;
- validate structured data with current official tooling/guidance where relevant;
- check sitemap/robots accessibility and coverage;
- crawl/route-check links and redirects;
- verify production status codes and rendered content when release scope permits;
- inspect Search Console/index data only when actual access exists.

Source/build success alone is not search-engine production verification.

## Output

Use/update a project artifact such as `docs/seo-performance-plan.md` with:

```text
Page-family indexability/canonical plan
Metadata ownership/template rules
Structured-data map
Internal-link/discovery plan
Sitemap/robots plan
URL migration/redirect map
Verification matrix
Search-demand handoff / NO_DATA
Known limitations
```

## Hard rules

- No invented search volume/rank/Search Console metrics.
- No universal metadata/CWV/link-count thresholds presented as guaranteed ranking rules.
- No schema for content that is not real and visible where required.
- No `robots.txt` as security/privacy control.
- Preserve proven URLs/content unless migration rationale + redirect plan exists.
- Current search-engine requirements must be reverified when exact eligibility matters.

## External knowledge handoff

Demand research and content briefs may route to `search-demand-and-content-briefing`, informed by the pinned `mblode/agent-skills` source in `vendor/cross-functional-intelligence/SOURCE-LOCKS.md`.

## Acceptance criteria

- Index/canonical intent is explicit for material page families.
- Metadata/schema reflect real page content and framework ownership.
- Important routes are discoverable without arbitrary link quotas.
- URL changes have migration/redirect handling when applicable.
- Verification uses rendered/deployed evidence appropriate to the claim.
