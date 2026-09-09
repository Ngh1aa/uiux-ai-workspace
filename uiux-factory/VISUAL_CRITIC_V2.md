# VisualCritic v2 + real-skill guard

This patch addresses the regression loop that stayed at score 87.

Root cause:
- v1 treated high white-pixel ratio as a composition failure everywhere;
- cart/checkout are intentionally light transactional routes;
- six viewport-level duplicates became six identical repair directives;
- v1 had fixed/proxy scores that could keep the loop at the same score.

VisualCritic v2:
- recognizes /cart/ and /checkout/ as transaction routes;
- validates transaction structure from rendered HTML;
- does not flag light transaction surfaces by white ratio alone;
- deduplicates repeated viewport issues by route/category;
- derives typography score from browser evidence instead of a hard-coded 84;
- derives brand proxy from actual CSS brand token use;
- derives generic-AI proxy from actual visual-composition family diversity;
- conditionally loads the REAL ecommerce-website skill when transaction routes exist.

Also included:
scripts/validate_skill_references.py

Run this guard whenever factory code changes. It scans core/**/*.py for
*/SKILL.md references and FAILS if any path does not exist in the local
skills_UIUX clone.
