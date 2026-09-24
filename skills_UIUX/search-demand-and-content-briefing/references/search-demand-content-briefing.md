# Search Demand & Content Briefing — Pinned Synthesis

Source reviewed: `mblode/agent-skills@0a639b1ef3b75aa6cc945e778fb1486def1d41bf` → `seo-program` (MIT).

This reference adapts the upstream distinction between demand research and technical SEO implementation. Vendor-specific statistics in upstream material are not copied as durable facts; current claims must be reverified when used.

## Evidence protocol

For every numeric demand/performance claim, keep:

`metric → exact source/tool/property → market/scope → match/definition → date/window → value/NO_DATA → limitation`

Examples:
- Keyword volume without market/window/match context is incomplete.
- Search Console query data must name the correct property and time window.
- A third-party connector is not assumed equivalent to first-party data until reconciled when material.

When a tool returns no result, use `NO_DATA`, not a guessed zero and not a remembered industry average.

## Question map

Translate a topic into user questions across the decision journey:

| Intent | Example shape |
|---|---|
| Understand | What is X? When is it useful? |
| Compare | X vs Y? What are the alternatives? |
| Choose | Which option fits my situation? |
| Do | How do I accomplish the task? |
| Trust | What does it cost? What are the limits/risks/proof? |
| Specific | How does this product/service handle my exact case? |

Questions should sound like something a person would ask. Avoid manufacturing unnatural long-tail phrases only to include keywords.

## Content-brief contract

A useful brief is a **decision artifact**, not a full article draft. Include:

- why this page deserves to exist;
- audience, entry intent and decision job;
- primary topic/query with evidence;
- secondary question cluster;
- content/proof that must be present;
- page/section priorities rather than exhaustive prose;
- internal-link relationships;
- CTA/next step;
- technical SEO requirements to hand off;
- evidence table.

Do not include invented quotes, stats or product behavior. Do not bury the designer/writer under a rigid outline when the evidence does not justify it.

## Existing-page monitoring

When reviewing changes, keep comparisons like-for-like and investigate before attributing cause. Typical reconciliation dimensions:

- property/domain and page set;
- query set/brand vs non-brand;
- date range/seasonality;
- device/country;
- indexing/canonical/redirect changes;
- content/template changes;
- result-page changes;
- analytics/reporting definition differences.

Search performance evidence can trigger a design/content hypothesis, but it does not by itself prove the page design is the cause.

## UI/UX handoff

Search intelligence can influence:
- sitemap/page-family priority;
- page role and entry context;
- first-screen questions;
- comparison/proof sections;
- internal linking and next destinations;
- content hierarchy.

It should not override brand, product truth, user research or accessibility constraints merely because a keyword has volume.
