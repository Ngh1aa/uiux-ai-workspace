# Personalization Patterns Reference

Read this when filling the personalization inventory, writing explanation and control copy, designing cold start or the preference center, or choosing guardrail metrics.

## 1. Classification examples

| Adaptation | Type | Why |
|---|---|---|
| Language chosen in settings | Explicit | User set it |
| Saved search "2-bed under 3 billion VND" | Explicit | User saved it |
| Default currency from locale | Contextual | Derived from request; must be switchable |
| "Recently viewed" row | Implicit (low risk) | Derived from behavior, transparent by nature |
| "Recommended for you" | Implicit | Model inference; needs explanation |
| Ranked search results by predicted interest | Implicit | Changes results materially; disclose and offer non-personalized sort |
| Email content tuned to segment | Implicit | Happens off-site; needs preference center control |

## 2. Remember-by-default decision

Ask three questions for each candidate:
1. Does remembering it save meaningful effort on return? If no, do not store.
2. If someone else saw it on this device, could it embarrass or harm the user? If yes, ask first or keep session-only.
3. Could it reveal or proxy a special category? If yes, exclude unless explicit opt-in and confirmed legal basis.

## 3. Sensitive-inference exclusion list (starter)

Maintain per product; review with the privacy owner.
- Health conditions, medication, pregnancy, mental health, disability.
- Sexual orientation, gender identity.
- Religion or belief, political opinion, union membership.
- Racial or ethnic origin.
- Biometric and genetic data.
- Precise location history, visits to sensitive places (clinics, places of worship, shelters).
- Financial distress signals (debt help pages, payday loans).
- Signals that a user is a minor.
- Bereavement, divorce, job loss.
Also exclude these as targeting inputs in email, push and ads, where exposure risk is higher.

## 4. "Why am I seeing this" copy patterns

Good:
- "Because you saved 3 hiking trails near Da Lat. [Edit saved trails] [See less like this]"
- "Popular with people learning beginner Python on this site. [Not interested]"
- "Shown because you follow Design Systems. [Unfollow]"

Weak:
- "Because of your activity." (no user-visible input, no control)
- "Our AI thinks you'll love this!" (no reason, overclaims)

Rules:
- Reference inputs the user can see and change.
- Every explanation has at least one action next to it.
- If the reason involves partner or off-site data, say so.

## 5. Cold start options

| Option | Use when | Risk |
|---|---|---|
| Editorial picks | Strong content team, brand-sensitive | Staleness; needs review cadence |
| Popular in context (category, locale) | Enough traffic | Popularity loop; add diversity |
| Skippable topic picker | Users have clear interests | Picker ignored if results do not visibly change |
| Recently added | Inventory or news products | Low relevance for niche users |

Never show an empty personalized module. Hide the module or replace it with a contextual default.

## 6. Filter bubble guardrails

- Exploration slots: reserve part of each list for items outside the dominant interest.
- Signal decay: older behavior loses weight over time.
- Source caps: limit repeats from one creator, seller or source.
- Escape hatch: a visible unpersonalized view (Latest, All, Sort by).
- Metrics: diversity of items consumed, share of sessions using the unpersonalized view, "not interested" rate, opt-out rate, complaint rate. Pair with relevance or satisfaction.

## 7. Preference center structure

1. What we remember: list of categories with view, edit and clear per category.
2. Personalization controls: toggles for recommendations, personalized ranking, personalized email, personalized ads, each describing effect when off.
3. Sync scope: device only or account; last synced time.
4. Reset all to defaults, with a confirmation that states what will be cleared and that data use stops.
5. Links to privacy policy and data request routes.

Toggle copy describes effect, not mechanism: "Off: you'll see the same Latest and Popular lists everyone sees."

## 8. Legal checkpoints to raise with the privacy owner (verify current law)

- Lawful basis for each profiling purpose, and whether consent is required in each market.
- Right to object to profiling for direct marketing (GDPR Art. 21) wired to a working control.
- Any solely automated decision with legal or similarly significant effect (GDPR Art. 22): human review route.
- DSA: recommender parameter explanation; non-profiling option if the service is designated very large.
- CCPA and CPRA: "Do Not Sell or Share" for cross-context behavioral advertising, "Limit the Use of My Sensitive Personal Information", opt-out preference signals such as Global Privacy Control, and current automated decision-making rules.

## 9. Worked example (before and after, property listing site)

Before:
- Homepage shows "Recommended homes" ranked by model; no explanation.
- Saved filter "District 7, 2 bed" is stored in browser only and lost on sign-in.
- Results default to "Recommended" every visit, even after user picks "Newest".
- Model uses visits to mortgage hardship articles to push cheaper listings.

After (inventory rows):

| Adaptation | Type (explicit, implicit, contextual) | Input data | Sensitive? Exclusion check | Legal basis or consent | Where stored and sync scope | User control (edit, reset, off) | Explanation copy | Fallback | Guardrail metric |
|---|---|---|---|---|---|---|---|---|---|
| Saved filter | Explicit | User-saved criteria | No | Contract (account feature); confirm with privacy owner | Account, all devices; signed-out filter offered for merge at sign-in | Edit, delete, rename | "Saved to your account" | Default filters by city | Saved-filter reuse rate |
| Sort order | Explicit | Last chosen sort | No | Not personal profiling | Account | Change any time | None needed | Newest | Share overriding default |
| Recommended homes | Implicit | Viewed and saved listings on site | Mortgage hardship pages excluded as financial-distress proxy | Consent where required; verify per market | Account | Not interested, see less, turn off | "Because you saved 2 homes in District 7" | Popular in your city | Diversity, not-interested rate, opt-out rate |

## 10. Testing

- Test with a fresh profile (cold start), a heavy user, a user who opted out, and a shared device.
- Verify that clearing data changes the next result set.
- Verify fallback when the recommendation service times out.
