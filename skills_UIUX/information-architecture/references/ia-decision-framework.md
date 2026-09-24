# IA Decision Framework

Use this reference when the information space is large, ambiguous, multilingual, multi-audience or being migrated from a legacy site.

## 1. IA is broader than navigation

IA models:
- content/function inventory;
- taxonomy and category relationships;
- labels and vocabulary;
- hierarchy and polyhierarchy;
- page roles;
- navigation/search/findability paths;
- metadata and URL relationships.

Navigation is the UI mechanism that exposes part of that structure.

## 2. Breadth vs depth

Do not optimize for an arbitrary number of clicks.

Prefer shallower structures when:
- categories are distinct and recognizable;
- high-frequency destinations can be exposed clearly;
- menu scanning remains manageable.

Allow deeper structures when:
- intermediate context helps users understand choices;
- the information domain has natural levels;
- flattening creates overlapping or overwhelming categories.

For deep structures add orientation and shortcuts: breadcrumbs, local navigation, search, contextual links and high-value shortcuts.

## 3. Label quality / information scent

A strong label lets users predict the destination before clicking.

Evaluate each label for:
- specificity;
- familiarity to the intended audience;
- distinction from sibling labels;
- consistency with destination heading/content;
- language/localization clarity;
- avoidance of internal jargon.

Weak examples: `More`, `Discover`, `Explore`, `Solutions` without context.

## 4. Taxonomy

For each taxonomy dimension decide whether it is:
- hierarchical — parent/child categories;
- faceted — independent attributes used for filtering;
- sequential — time/process/order;
- audience-based — only if users genuinely identify by audience;
- task/topic-based — common for public-facing sites.

Avoid duplicating the same concept under slightly different labels without a defined synonym/alias strategy.

## 5. Polyhierarchy and cross-listing

Cross-list an item when multiple category paths are legitimate user mental models. Do not duplicate the underlying content unnecessarily; expose multiple routes to the same canonical destination.

Useful for ambiguous content such as:
- technology solution relevant to multiple industries;
- school information relevant to both program and age group;
- corporate resource relevant to investor and company-information journeys.

## 6. Page-role model

### Orientation page
Explains what the site/service covers and routes major intents.

### Hub/category page
Surfaces a coherent set of child topics and helps comparison.

### Transition/routing page
Exists mainly to help choose a branch. It must add decision value; avoid empty gateway pages.

### Destination/detail page
Answers a specific information need.

### Task/transaction page
Supports completion of an action/process.

### Search/results page
Supports retrieval across taxonomy boundaries and recovery when users do not know where content lives.

### Recovery/support page
Helps recover from errors, missing content, permissions or uncertainty.

## 7. Navigation layers

- Global: stable major sections.
- Local: siblings/children within a section.
- Contextual: next/related items relevant to current content.
- Utility: account, language, search, cart, contact, etc.
- Breadcrumb: hierarchy/orientation support when structure is deep enough to benefit.
- Footer: reference/secondary destinations, not a dumping ground for unresolved IA.

## 8. Search vs navigation

Do not assume search replaces navigation. Users vary between browsing, known-item seeking and exploratory behavior. Search becomes more important as vocabulary/content volume grows, while navigation remains important for orientation and discovery.

## 9. Validation methods

### Card sorting
Use to understand grouping and labeling expectations. Results inform hypotheses; they do not automatically become the sitemap.

### Tree testing
Use to test whether users can find target destinations in the proposed hierarchy without visual design cues.

### Moderated usability testing
Use for end-to-end navigation, interpretation, recovery and cross-channel behavior.

### Search logs
Use to discover user vocabulary, missing synonyms, failed queries and content gaps.

### Analytics
Use cautiously to identify routing friction, not to infer motivation without supporting evidence.

## 10. Redesign migration

Before changing IA:
- crawl/list current URLs;
- identify traffic/backlinks/conversion value;
- classify keep/merge/retire;
- map old → new;
- define redirect/canonical strategy;
- preserve content ownership and metadata where needed;
- verify internal links after migration.

## Research baseline

This framework aligns with current guidance including:
- Nielsen Norman Group — Information Architecture study guide, IA vs navigation, information scent, flat vs deep hierarchies, tree testing;
- GOV.UK / Home Office user-centred design guidance — clear, consistent navigation and logical content/service structure;
- W3C/WAI principles — semantic structure and navigation that support orientation and accessibility.
