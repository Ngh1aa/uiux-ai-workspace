# Thực hành chuyên sâu

Chỉ mở khi cần chi tiết trong mục dưới đây; WORKFLOWS.md vẫn là nguồn định tuyến duy nhất.

# Trust, Credibility & Transparency

## Goal and scope

Give users enough verifiable evidence, at the moment they decide, to judge whether an organization is real, competent and honest. Trust is not a visual style; it is the ratio of checkable proof to unsupported claims, placed where doubt actually arises.

**When not to use**

- Persuasive argument, objection handling and CTA strategy for a landing page: use `conversion-and-content`.
- Manipulative patterns (fake urgency, hidden costs, confirmshaming): use `ethical-ux-and-deceptive-patterns`.
- Data handling, consent mechanics and security signals: use `security-and-privacy`.
- Tracing research claims to sources inside the design team: use `evidence-provenance-and-research-ops`.
- Ongoing content ownership, review cycles and expiry in the CMS: use `content-governance-and-cms`.

**Prerequisites**

- List of the decisions users make on the site (enquire, apply, donate, book a viewing, buy).
- Inventory of what the organization can actually prove: registrations, accreditations, named people, case studies with permission, policies, audited figures.
- Owner who can confirm dates, permissions and relationships behind each piece of evidence.

## Decisions

**Claim inventory first.** List every trust-critical claim (e.g. "accredited", "500 clients", "award-winning", "safe", "100% placement"). For each, record evidence, source, date and who can verify. A claim with no evidence is rewritten, qualified or removed. Superlatives ("leading", "best") need a named, dated, third-party basis or they go.

**Stanford Web Credibility guidelines as the audit frame (Fogg).** Check that the site makes it easy to verify accuracy, shows a real organization behind it, highlights real expertise, shows honest and trustworthy people, makes contact easy, looks professional for its purpose, is easy to use, is updated, uses restraint with promotional content, and avoids errors. Treat these as a checklist of evidence types, not a styling brief.

**Proximity of evidence to decision.** Put proof within the same view as the claim or the commitment it supports: fees and refund terms beside the apply button, accreditation body and number beside "accredited", safety certificate beside the booking step. An "About" page full of proof does not help a user hesitating on a pricing page. Rule: if a user must navigate away to verify a claim made at a decision point, move or link the evidence inline.

**Verifiability ladder.** Prefer, in order: independently checkable (registry number with link to the issuing body's lookup, named reviewer on a third-party platform), attributable (named person, role, date, consented photo), organization-asserted with specifics (dated figure with method), vague assertion. Design for the highest rung you can honestly reach.

**Testimonials and endorsements.** Follow FTC Endorsement Guides principles for US audiences (and equivalent consumer-protection rules elsewhere; verify current guidance and jurisdiction):
- Testimonials reflect real, honest experience of real customers; no composites presented as one person.
- Disclose material connections (paid, gifted, employee, affiliate, family) clearly and near the endorsement.
- If results shown are not typical, do not imply they are; show what typical users can expect or avoid outcome claims.
- Do not selectively suppress negative reviews while presenting the remainder as representative.
- Fake or AI-generated reviews and testimonials attributed to non-existent people are prohibited; recent FTC rules address this directly, verify current rule text.

**Logos and relationships.** Show a client, partner or accreditor logo only with a documented relationship and permission. Label the relationship ("client since 2022", "member of", "featured in"); "as seen in" for a single passing mention misleads. Remove logos when the relationship ends.

**Recency stamps.** Every fact that can go stale (prices, fees, staff, statistics, policies, availability, rankings) shows a "last reviewed" or "as of" date and has an owner. If content cannot be dated, do not present it as current. Stale-but-useful content is labelled archival.

**Representative content.** Stock or staged imagery, illustrative floor plans and sample data are labelled as such when users could mistake them for the real thing (real estate, education campuses, team pages).

**Identity and contact.** Legal entity name, registered address or registration number where relevant, and at least one human contact route with an expected response time, reachable within one step from any page (typically footer and contact page).

## Workflow

1. List trust-critical claims and user decisions; pair each claim with the decision it influences.
2. Map evidence: people, clients, projects, certifications, policies, dates, contacts and third-party proof. Record source, date, permission, owner.
3. Place evidence near the decision it supports; link checkable proof to the issuing source.
4. Use authentic imagery and data where available; label representative content.
5. Expose ownership, contact routes and content recency with dates and owners.
6. Remove or soften unsupported superlatives; disclose material connections on endorsements.
7. Re-audit after launch on a review cadence tied to the most volatile fact type.

**Anti-patterns**

- Logo walls of companies whose one employee once attended a webinar.
- Testimonials with first name, initial and stock headshot, no date, no way to tell if real.
- "Trusted by 10,000+ customers" unchanged for years, no method, no date.
- Accreditation badge image with no issuer name, number or verification link.
- Team page with departed staff, or stock models presented as staff.
- Fees and cancellation terms only in a PDF linked from the footer, away from the checkout.
- Star rating aggregated from an undisclosed, curated subset of reviews.
- "Award-winning" with no award named.
- Influencer or affiliate content with disclosure hidden behind "more" or at the end.

**Resources**

- Need the claim-evidence matrix template, placement patterns by site type, disclosure wording or a worked example? Read [evidence architecture reference](../references/evidence-architecture.md).
- Before release, run [trust gate](../checklists/trust-gate.md).

**Output**

1. Claim-evidence matrix:

| Claim (exact wording) | Page and decision point | Evidence | Verifiability rung | Source and date | Permission or disclosure | Owner | Review cadence | Action (keep, qualify, link, remove) |
|---|---|---|---|---|---|---|---|---|

2. Placement plan: for each decision point, the evidence shown inline and the link to deeper proof.
3. Identity and contact spec: entity, registration, contact routes, response time, location in layout.
4. Recency plan: which content types carry dates, who reviews, how often.

## Quality gate

- PASS only if every major claim has evidence or qualified wording (major claims have evidence or qualified wording).
- PASS only if identity and contact information is reachable within one step from any page (identity and contact information is easy to find).
- PASS only if every volatile fact shows a review date and owner; FAIL if stale or unknown content is presented as current fact.
- FAIL if any logo or testimonial implies a relationship without documented support and permission (logos and testimonials do not imply relationships without support).
- PASS only if every endorsement with a material connection discloses it clearly and next to the endorsement.
- PASS only if evidence for a claim made at a decision point is visible or linked inline at that point.
- PASS only if representative imagery or data that could be mistaken for real is labelled.

**Baseline and sources**

- B. J. Fogg and Stanford Persuasive Technology Lab, Stanford Web Credibility Guidelines and Prominence-Interpretation theory.
- US FTC, Guides Concerning the Use of Endorsements and Testimonials in Advertising (16 CFR Part 255) and the FTC rule on consumer reviews and testimonials. Verify current text and jurisdiction; this is design guidance, not legal advice.
- NN/g research on trustworthiness and credibility signals.
- EU and UK consumer-protection rules on reviews apply to their markets; verify current guidance.
