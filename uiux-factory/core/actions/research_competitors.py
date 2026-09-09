from __future__ import annotations

from datetime import datetime

from metagpt.actions import Action

from core.orchestration.intelligent_flow import GoalInterpreter
from core.orchestration.reference_intelligence import ReferenceIntelligencePlanner
from core.research.domain_intelligence import DomainInterpreter
from core.research.live_web_research import LiveWebResearch, ResearchCandidate
from core.skills.loader import SkillLoader


class ResearchCompetitors(Action):
    name: str = "ResearchCompetitors"
    desc: str = (
        "Run domain-aware UI/UX benchmark research from skills_UIUX, "
        "using live web search when configured and truthful curated fallback otherwise."
    )

    @staticmethod
    def _candidate_table(candidates: list[ResearchCandidate]) -> str:
        if not candidates:
            return (
                "| Reference | Family | Query | Evidence |\n"
                "|---|---|---|---|\n"
                "| None | — | — | Live discovery unavailable |"
            )

        rows = [
            "| Reference | Family | Query | Evidence |",
            "|---|---|---|---|",
        ]
        for candidate in candidates:
            description = candidate.description.replace("|", "/").replace("\n", " ")
            query = candidate.query.replace("|", "/")
            rows.append(
                f"| [{candidate.title}]({candidate.url}) | "
                f"{candidate.query_family} | {query} | "
                f"{description[:220] or 'Search result verified by provider'} |"
            )
        return "\n".join(rows)

    @staticmethod
    def _fallback_table(selected) -> str:
        rows = [
            "| Reference | Role | Why it is here | Evidence status |",
            "|---|---|---|---|",
        ]
        for reference in selected:
            rows.append(
                f"| [{reference.label}]({reference.url}) | {reference.role} | "
                f"{reference.rationale} | Curated production fallback; "
                "must be inspected before a material design decision |"
            )
        return "\n".join(rows)

    async def run(self, instruction: str) -> str:
        loader = SkillLoader()
        stats = loader.stats()
        selected_skills = loader.select(limit=8)

        goal_profile = GoalInterpreter().interpret(instruction)
        domain_profile = DomainInterpreter().interpret(
            instruction,
            goal_profile.website_type,
        )

        skills_markdown = (
            "\n".join(
                f"- `{skill.relative_path}` (score: {skill.score})"
                for skill in selected_skills
            )
            if selected_skills
            else "- No matching skill found."
        )

        researcher = LiveWebResearch()
        query_families = researcher.build_query_families(
            website_type=domain_profile.website_type,
            vertical=domain_profile.vertical,
        )
        candidates = researcher.discover(query_families, max_candidates=20)
        finalists = researcher.shortlist(candidates, limit=6)

        fallback_plan = ReferenceIntelligencePlanner().plan(
            goal=instruction,
            user_urls=[],
            auto_enabled=True,
            target_reference_count=4,
        )

        if candidates:
            execution_mode = "live-web-search"
            evidence_status = (
                "PASS_FOR_SYNTHESIS"
                if len(candidates) >= 10 and len(finalists) >= 3
                else "PARTIAL"
            )
            evidence_note = (
                "Live search discovery ran through the configured web-search provider. "
                "Search snippets are discovery evidence, not proof of complete page UX. "
                "Material finalists still require actual page/state inspection or rendered capture."
            )
            candidate_section = self._candidate_table(candidates)
            finalist_section = self._candidate_table(finalists)
        else:
            execution_mode = "curated-fallback"
            evidence_status = "PENDING_LIVE_RESEARCH"
            evidence_note = (
                "BRAVE_SEARCH_API_KEY is not configured or live discovery returned no usable results. "
                "The fallback is explicit and must not be described as live competitor research."
            )
            candidate_section = self._fallback_table(fallback_plan.selected)
            finalist_section = candidate_section

        query_markdown = "\n".join(
            f"### {family}\n"
            + "\n".join(f"- `{query}`" for query in queries)
            for family, queries in query_families.items()
        )

        created_at = datetime.now().isoformat(timespec="seconds")

        return f"""# UI/UX Research Benchmark

## Project interpretation

- Goal: {instruction}
- Website archetype: `{domain_profile.website_type}`
- Vertical/sub-industry: `{domain_profile.vertical}`
- Mode: `{goal_profile.mode}`
- Features: {", ".join(goal_profile.features) if goal_profile.features else "none detected"}
- Created: `{created_at}`

## Execution

- Mode: `{execution_mode}`
- External discovery candidates: `{len(candidates)}`
- Shortlisted finalists: `{len(finalists) if finalists else len(fallback_plan.selected)}`
- skills_UIUX: `{stats["skills_root"]}`
- Skills discovered: `{stats["skill_count"]}`

## Selected skills

{skills_markdown}

## Search strategy

The benchmark follows three independent query families so one generic homepage pattern
cannot become the answer for every page role.

{query_markdown}

## Candidate pool

{candidate_section}

## Shortlist

{finalist_section}

## Page-role research requirements

For every materially different representative page, record:

| Page role | User question/task | Reference page/state | Principle extracted | What not to copy | Project adaptation |
|---|---|---|---|---|---|
| Home/orientation | What is this and why should I care? | REQUIRED | REQUIRED | REQUIRED | REQUIRED |
| Primary browse/task page | How do I find/narrow the right option? | REQUIRED | REQUIRED | REQUIRED | REQUIRED |
| Detail/decision page | Is this specific option right for me? | REQUIRED | REQUIRED | REQUIRED | REQUIRED |
| Conversion/commitment | What happens if I continue? Can I trust it? | REQUIRED | REQUIRED | REQUIRED | REQUIRED |

Domain playbooks may replace these generic roles with more specific ones
(e.g. PLP/PDP/checkout, admissions/programme, rooms/booking, article/topic).

## Domain design intelligence handoff

Before Art Direction, synthesize evidence into:

- primary user decision model;
- domain-native decision objects;
- content priority by page role;
- layout/composition principles by page role;
- media/imagery requirements;
- trust and conversion requirements;
- mobile transformation;
- interaction/state requirements;
- rejected generic/template patterns;
- implementation constraints and unknowns.

Do **not** turn search-result snippets into visual claims. Do **not** copy a reference surface.
The handoff must state what was actually inspected versus what remains an assumption.

## Prototype experience overlay

When mode is `visual-prototype` or `interactive-prototype`, explicitly define:

- intended 3-second impression;
- 3 style adjectives;
- one demo path;
- one hero/signature moment;
- anti-generic/anti-AI-look constraints;
- interaction states used in the demo;
- squint-test and 5-second-test questions for final critique.

## Evidence Gate

Status: `{evidence_status}`

{evidence_note}

Research is not complete merely because URLs were found. For a substantial redesign,
the target is 10–20 discovery candidates, 3–6 finalists with clear jobs, and actual
page/state inspection for every material decision.

---
Generated by ResearchAgent.
"""
