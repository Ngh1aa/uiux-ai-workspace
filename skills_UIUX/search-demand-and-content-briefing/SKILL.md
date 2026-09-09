---
name: search-demand-and-content-briefing
description: Researches current search demand and Search Console/query evidence, builds natural-language question/intent maps, and creates evidence-backed content briefs for pages. Use before content/IA decisions when search demand materially affects page role, topic priority or content structure; seo-strategy remains the owner for technical/on-page implementation.
---

# Search Demand & Content Briefing

## Boundary

This skill owns **search-demand evidence → intent/question map → content brief → monitoring insight**.

It does NOT own technical SEO implementation, schema/canonical/robots/sitemap work, article writing, or marketing-copy craft. Hand technical requirements to `seo-strategy` and persuasion/value-proposition wording to `conversion-and-content`.

## Source-of-truth rule

Current numbers require a current source. Before naming search volume, clicks, impressions, positions or AI/search visibility, verify the actual connected/browser/research source and record scope/date. If the relevant source cannot be accessed, write `NO_DATA` / `UNKNOWN`; do not estimate from memory.

## Mode A — Topic / page pipeline

### 1. Define decision context

Capture:
- business/page goal;
- target audience/market/language;
- candidate topic/page role;
- desired conversion or next destination;
- existing page/query evidence if any.

### 2. Pull current demand evidence

Use the best available authoritative/industry tool that is actually accessible. Record:

```text
Query/topic | Metric | Value/NO_DATA | Match/definition | Market | Window/date | Source
```

Do not combine numbers from different scopes/match definitions as if they are directly comparable.

Useful evidence can include:
- keyword/query demand;
- Search Console queries/clicks/impressions/position;
- internal site search;
- support/sales/admissions questions;
- current SERP/result composition;
- verified answer-engine/prompt visibility when a real source exists.

### 3. Build an intent/question map

Group natural questions by decision intent rather than stuffing keyword variants:

- understand/define;
- compare/evaluate;
- choose/decide;
- accomplish/how-to;
- trust/proof/limitations;
- product/service-specific questions.

Mark which questions existing pages already answer and where gaps create a justified page/section opportunity.

Search-demand evidence informs IA/content priority; it does not automatically dictate one page per keyword.

### 4. Create a decision-shaped content brief

Recommended fields:

```text
Brief title / page role:
Audience + entry context:
Business/user goal:
Primary search intent:
Primary query/topic + current evidence:
Secondary questions/clusters:
What must be answered early:
Proof/source requirements:
Content/page shape:
Internal-link opportunities:
CTA / next destination:
SEO implementation handoff:
Unknown/no-data fields:
Evidence table:
```

Avoid over-prescribing every paragraph when the writer/designer needs room to solve the page.

### 5. Handoff

- IA/page-role implications → `information-architecture` / Design Contract.
- Page argument/value proposition → `conversion-and-content`.
- Technical metadata/schema/crawl/index → `seo-strategy`.
- Long-form writing → content owner/writer.

## Mode B — Search-performance review

For an existing site, compare state changes using the same property/scope/metric definition. Investigate material changes before assigning a cause.

Useful checks:
- page/query click and impression movement;
- query/page mix shift;
- indexing/crawl or technical changes;
- seasonality/event/campaign context;
- SERP/result-format change;
- content/URL migration;
- measurement/property mismatch.

A traffic drop is a signal, not a proven UX/SEO root cause.

## Hard rules

- Never fabricate search volume or Search Console metrics.
- Do not claim a tool/account/property is connected until verified.
- Stale exports are historical evidence, not today's numbers.
- Search intent > mechanical keyword density.
- Do not turn award/gallery/reference popularity into search-demand evidence.
- Do not claim ranking/AI-visibility improvement before outcome data exists.
- Keep raw vendor-specific claims out of durable guidance unless reverified when used.

## Progressive reference

Read [references/search-demand-content-briefing.md](references/search-demand-content-briefing.md) for deeper evidence/brief patterns synthesized from the pinned mblode SEO Program source recorded in `vendor/cross-functional-intelligence/SOURCE-LOCKS.md`.

## Acceptance criteria

- Every material numeric search claim has source + scope + date/window or is NO_DATA.
- Question map uses human intent, not keyword-stuffed pseudo-questions.
- Brief connects demand to audience/page role/business goal.
- Technical SEO and copywriting ownership are handed to the correct skills.
- Missing access/data remains explicit.
