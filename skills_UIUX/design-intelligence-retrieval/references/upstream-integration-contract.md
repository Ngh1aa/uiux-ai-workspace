# Upstream Design-Intelligence Integration Contract

## Locked upstream

- Repository: `nextlevelbuilder/ui-ux-pro-max-skill`
- Commit: `314307f156aeab0c6b567bbaa1ce4e7aabd5a636`
- Imported: 2026-09-06
- License: MIT; retained at `vendor/ui-ux-pro-max/LICENSE`

## Ownership boundaries

| Layer | Role |
|---|---|
| `vendor/ui-ux-pro-max/skills/` | all seven upstream skill packages, kept verbatim |
| `vendor/ui-ux-pro-max/engine/` | full upstream `src/ui-ux-pro-max`: data, search/reasoning code, templates and tests |
| `design-intelligence-retrieval/` | local adapter, routing, context-budget and synthesis rules |
| `skills_UIUX` core | project truth, evidence, UX/IA, Design Contract, implementation, accessibility, QA and release governance |

## Precedence

`current user request > project truth/source > passed Design Contract/artifacts > routed local skills > retrieved design intelligence > generic model prior`

A vendor result is a candidate recommendation. It never silently becomes project truth.

## Retrieval policy

Use progressive disclosure:
1. determine the real decision and scope;
2. select `--design-system`, one `--domain`, or `--stack`;
3. run a narrow query;
4. retain only decision-relevant results/provenance;
5. retry once if empty/off-topic;
6. synthesize `ADOPT / ADAPT / REJECT`.

Full CSV/JSON catalogs are storage/indexes, not model prompt context.

## Persistence policy

Upstream persistence may generate `design-system/<project>/MASTER.md` and page overrides. These files are subordinate retrieved artifacts in this library. The adopted Design Contract remains canonical.

- Read an existing upstream-generated MASTER/page file before regeneration.
- Never use upstream `--force` without explicit user authorization.
- Do not maintain two conflicting design sources of truth.
- If a persisted vendor suggestion conflicts with a passed Design Contract, log the conflict and keep the higher-priority project artifact until an intentional design migration is approved.

## Provenance policy

When a retrieved recommendation materially changes a Design Contract or implementation decision, record:
- upstream commit;
- query/domain/stack mode;
- candidate/result identity when available;
- upstream status/provenance when relevant;
- adaptation rationale;
- downstream verification method.

Do not promote deprecated/pending records as canonical without explicit review.

## Upgrade policy

Do not float on upstream `main`. To change the vendor commit:
1. inspect upstream diff, license, data/provenance and search behavior;
2. verify all seven skill packages and engine/data coverage;
3. run upstream search smoke plus local vendor/skill/profile/eval validators;
4. record migration/conflicts;
5. update `docs/uiux/Skill-Version-Lock.md` only after review.

No automatic vendor refresh may silently change a project’s locked design decisions.
