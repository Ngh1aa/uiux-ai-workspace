---
name: information-architecture
description: |
  Design and review website information architecture: content/function inventory, taxonomy, labeling,
  hierarchy, page roles, navigation systems, findability, URL/migration structure and validation.
  Use before navigation/UI implementation, during redesigns, or when users struggle to find content.
---

# Information Architecture — V3

## Purpose

Information architecture (IA) defines **what information/functionality exists, how it is organized, how it is named, and how pieces relate**. Navigation is one interface expression of IA; it is not the whole IA.

Core objective:

`user/task evidence → content + functionality → taxonomy/labels → hierarchy → navigation/findability → validation`

## Evidence hierarchy

Prefer, in order:
1. current user instruction;
2. project `.uiux-profile.json` and source-of-truth docs;
3. observed research, analytics, search logs, support data;
4. domain playbooks and known content constraints;
5. generic IA patterns.

Do not present assumptions as research findings.

## Prerequisites

Usually pair with:
- `product-discovery` for goals, audience and scope;
- `ux-research-and-journey` for tasks and journeys;
- `website-audit-and-redesign` when restructuring an existing site;
- `card-sorting-and-tree-testing` when findability risk is material;
- `site-search-and-findability` for large/search-heavy systems.

## Required workflow

### 1. Inventory content and functionality

Create a page/content/function inventory before drawing a sitemap.

Minimum fields:

| Item | Type | User need/task | Business need | Source | Current URL | Status | Owner |
|---|---|---|---|---|---|---|---|

Include content, tools, forms, search, filters, directories, account areas, downloads, legal/support content and important system states.

For redesigns classify each existing item:

`keep | improve | merge | split | move | retire | redirect`

### 2. Define audiences, top tasks and entry contexts

For each important audience, identify:
- top tasks;
- likely entry pages (homepage, search engine, campaign, deep link, shared link);
- information needed before the next decision;
- conversion/task completion destination;
- likely recovery routes when lost.

Do not assume every journey starts at the homepage.

### 3. Build taxonomy and labeling system

Group by user mental model and task intent, not internal org chart.

For every category/label record:

| Label | Meaning | Includes | Excludes | Audience/task | Evidence/confidence |
|---|---|---|---|---|---|

Rules:
- prefer specific, familiar, descriptive labels with strong information scent;
- avoid vague labels such as `More`, `Explore`, `Solutions` when the destination is unclear;
- avoid format-first top-level categories (`Videos`, `PDFs`) unless format is itself the user goal;
- define synonyms/aliases for search and cross-linking where terminology varies;
- use polyhierarchy/cross-listing when one item legitimately belongs in multiple user mental models.

### 4. Design hierarchy by breadth/depth tradeoff

There is **no universal 3-click rule** and no fixed maximum depth.

Choose breadth/depth using:
- number and distinctness of categories;
- label clarity;
- user familiarity;
- content volume;
- task frequency/importance;
- device constraints;
- availability of search/shortcuts/contextual navigation.

Prefer fewer unnecessary intermediate layers, but do not flatten so aggressively that menus become ambiguous or overwhelming.

Document the hierarchy as a sitemap/tree with page IDs and page roles.

### 5. Assign page roles

Each important page must have a clear IA role, for example:
- **Home / orientation** — explain scope and route major intents;
- **Hub / category** — expose subtopics and comparison paths;
- **Transition / routing** — help users choose the correct next branch;
- **Destination / detail** — answer the need and support an action;
- **Task / transaction** — complete a process;
- **Search/results** — recover and find across categories;
- **Support/error** — recover from failure or uncertainty.

Avoid pages that exist only because the old sitemap had them.

### 6. Define navigation systems

Design multiple complementary navigation mechanisms as needed:
- global/primary;
- local/section;
- contextual/related links;
- utility (language, account, search, cart, etc.);
- breadcrumbs/orientation for deeper structures;
- footer/reference navigation;
- search and filters for large information spaces.

Do **not** use `7±2` or any fixed item count as a rule for primary navigation. Menu size depends on information scent, grouping, hierarchy and scanning cost.

Navigation labels must match destination expectations and remain consistent across desktop/mobile unless there is a deliberate reason.

### 7. Define URL and migration model

URLs should be stable, descriptive and maintainable, but IA does not require URLs to mechanically mirror every hierarchy level.

For redesign/migration create:

| Old URL | New URL | Action | Redirect | Canonical | Reason |
|---|---|---|---|---|---|

Protect high-value existing URLs, inbound links and indexed content. Coordinate with `seo-strategy` before changing live routes.

### 8. Design findability and recovery

For priority content ensure at least one strong route, and for high-value content often multiple routes:
- navigation;
- contextual link;
- search;
- related content;
- direct entry/search engine;
- task-specific shortcut.

Evaluate information scent at each decision point: **Can the user predict what is behind this label/link?**

### 9. Validate when risk justifies it

Use evidence rather than preference wars.

Possible methods:
- card sorting for grouping/label hypotheses;
- tree testing for hierarchy/findability;
- moderated usability testing for end-to-end behavior;
- search/query logs for vocabulary gaps;
- analytics for dead ends, pogo behavior and high-exit routing pages;
- support/sales questions for missing concepts.

A card sort is input to IA, not the final sitemap.

## Required output

Prefer `docs/information-architecture.md` containing:
1. scope and evidence/assumptions;
2. content/function inventory summary;
3. audiences + top tasks;
4. taxonomy and labeling decisions;
5. sitemap/hierarchy;
6. page roles/template families;
7. navigation model;
8. findability/cross-linking model;
9. URL/migration map when applicable;
10. validation plan/results;
11. unresolved risks and decisions.

Generate `sitemap.xml` only when implementation/SEO scope actually requires it; an XML sitemap is not a substitute for IA documentation.

## Quality gate

Before calling IA complete, verify:
- priority user tasks map to reachable destinations;
- category boundaries and labels are understandable;
- hierarchy breadth/depth has a rationale, not arbitrary click limits;
- global/local/contextual/utility navigation responsibilities are clear;
- deep or complex structures provide orientation/recovery;
- high-value content is not reachable through a single fragile path only;
- redesign migrations preserve/redirect important legacy routes;
- IA assumptions are labeled and high-risk assumptions have a validation plan;
- mobile and accessibility implications are considered;
- sitemap, navigation and page-role model agree with one another.

## Anti-patterns

- Organizing primarily by internal departments when users think by task/topic.
- Treating sitemap = IA.
- Treating navigation = IA.
- Enforcing a false `3-click rule`.
- Enforcing `7±2` navigation items from Miller's Law.
- Adding umbrella categories with weak information scent only to reduce menu count.
- Creating deep chains of transition pages with little new information.
- Hiding important content behind vague labels like `More` or `Learn more`.
- Using format (`Videos`, `Resources`) as top-level IA when users seek topics/tasks.
- Rebuilding URLs without migration/redirect planning.
- Copying competitor sitemap without validating project users and content.

## Progressive resources

- [IA decision framework](references/ia-decision-framework.md)
- [IA quality gate](checklists/ia-quality-gate.md)

## Completion rule

Do not claim an IA is "validated" unless actual validation evidence exists. If no user evidence exists, report confidence and assumptions explicitly.
