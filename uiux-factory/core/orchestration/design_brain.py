"""Opt-in cloud generation with bounded repair and the existing real browser QA."""

import json
from hashlib import sha256
from pathlib import Path
from shutil import copy2

from core.actions.generate_ai_frontend import CODER_CONTRACT, DesignBrief, validate_bundle, write_bundle
from core.actions.create_design_system_v3 import safe_token
from core.agents.browser_qa_agent import BrowserQAAgent
from core.contracts.design_context_schema import ReferenceBoard
from core.contracts.design_system_schema import DesignSystemContract, TokenValue
from core.contracts.browser_qa_schema import BrowserQAResult
from core.contracts.frontend_result_schema import FrontendBuildGate, FrontendResult, GeneratedFile
from core.skills.compiler import SkillInstructionCompiler
from core.skills.frontend_design_policy import FRONTEND_DESIGN_POLICY
from core.skills.router import AdaptiveSkillRouter
from core.orchestration.open_design_bridge import export_design_package


def apply_proposed_tokens(system: DesignSystemContract, proposals: dict[str, str]) -> None:
    allowed = {"color.brand.primary": "colors", "font.family.body": "typography", "font.family.display": "typography"}
    for name, value in proposals.items():
        if name not in allowed:
            raise ValueError(f"Unsupported proposed token: {name}")
        tokens = getattr(system.foundations, allowed[name])
        existing = tokens.get(name)
        if existing and existing.status in {"confirmed", "derived"}:
            continue
        tokens[name] = TokenValue(value=safe_token(allowed[name], name, value), status="derived",
                                  source="AI proposal from brief; requires visual and brand review")
    if proposals:
        system.unresolved_items.append("AI-proposed missing brand tokens require review; existing confirmed/derived tokens were preserved.")


class DesignBrain:
    def __init__(self, context, provider, team_runner):
        self.context = context
        self.provider = provider
        self.team = team_runner
        self.compiler = SkillInstructionCompiler(team_runner.skills_root, max_chars_per_skill=3000, max_total_chars=12000)

    def save(self, name: str, filename: str, content: str) -> Path:
        path = self.context.run_dir / filename
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        self.context.add_artifact(name, path)
        return path

    async def ask(self, stage: str, task: str, prompt: str, json_mode: bool = False) -> str:
        self.context.start_stage(stage)
        selection = AdaptiveSkillRouter.route(stage=stage, goal=self.context.goal)
        skills = self.compiler.build(selection=selection, run_dir=self.context.run_dir)
        self.context.add_artifact(f"skill_context_{stage}", Path(skills.evidence_dir) / "skill-context.json")
        self.team.event_bus(self.context).emit("agent.started", stage=stage, agent="DesignBrain", data={"engine": "cloud", "skill_count": len(skills.sources)})
        try:
            result = await self.provider.complete(stage, FRONTEND_DESIGN_POLICY + "\n" + task,
                prompt + "\n\nSelected skill guidance:\n" + skills.compiled_instruction[:12000], json_mode=json_mode)
        finally:
            self.save("provider_usage", "provider-usage.json", json.dumps(self.provider.history, indent=2))
        if stage in {"research", "art_direction"}:
            self.context.complete_stage(stage)
        self.team.event_bus(self.context).emit("agent.completed", stage=stage, agent="DesignBrain")
        return result

    async def run(self):
        document = Path(self.context.artifacts["design_document"]).read_text(encoding="utf-8")
        # Bounded source data; input remains on disk in full with provenance.
        board = json.loads(Path(self.context.artifacts["reference_analysis"]).read_text(encoding="utf-8"))
        references = [{"url": ref["url"], "status": ref["status"], "patterns": ref["patterns"],
                       "observations": ref["observations"][:12]} for ref in board["references"]]
        input_data = {"brief": self.context.goal, "guideline": self.context.design_context.guideline,
                      "design_document": document, "references": references}
        inputs = json.dumps(input_data, ensure_ascii=False)
        research = await self.ask("research", "Analyze only the supplied brief and measured reference data. List facts, inferences, unknowns, audience tasks and UX opportunities. Include modern design inspiration: identify opportunities for micro-animations, glassmorphism, bento grid layouts, mesh gradients, or scroll-triggered effects that match the brand personality. No browsing claims or invented competitors. Keep under 600 words.", inputs)
        self.save("research", "research.md", research)
        inputs += "\nEvidence-based UX notes:\n" + research[:4000]
        task = ('Return only JSON with direction (string), pages (1-6 objects with path, title, purpose, sections array), '
                'unknowns (array), proposed_tokens (object). Propose only missing color.brand.primary (opaque HEX), font.family.body and font.family.display (CSS font families). '
                'Honor brief colors; do not infer official brand colors/fonts from a logo. Paths: index.html and lowercase route/index.html. Include home, no duplicate routes. '
                'Plan UX and visual direction for the actual business. Keep all explicit constraints. '
                'Use factual supplied content; no invented trust claims. Distinguish unknowns.')
        raw = await self.ask("ux_ia", task, inputs, True)
        brief = DesignBrief.model_validate_json(raw)
        self.context.complete_stage("ux_ia")
        self.save("ai_design_brief", "ai-design-brief.json", brief.model_dump_json(indent=2))
        system = DesignSystemContract.model_validate_json(Path(self.context.artifacts["design_system"]).read_text(encoding="utf-8"))
        apply_proposed_tokens(system, brief.proposed_tokens)
        self.save("design_system", "design-system.json", system.model_dump_json(indent=2))
        export_design_package(self.context.run_dir, system, ReferenceBoard.model_validate(board), self.context.goal)
        input_data["design_document"] = Path(self.context.artifacts["design_document"]).read_text(encoding="utf-8")
        inputs = json.dumps(input_data, ensure_ascii=False) + "\nEvidence-based UX notes:\n" + research[:4000]
        art = await self.ask("art_direction", "Write a concise implementable visual direction: hierarchy, type scale (clamp-based fluid), spacing rhythm, composition (consider bento grid, card-based, or magazine layouts), responsive breakpoints, motion (micro-interactions, smooth transitions, scroll-triggered reveals), and premium visual effects (glassmorphism, mesh gradients, luminous accents). Prioritize distinctive, non-generic aesthetics. No invented evidence.",
                             inputs + "\n" + brief.model_dump_json())
        self.save("art_direction", "art-direction.md", art)
        prompt = inputs + "\nPlan:\n" + brief.model_dump_json() + "\nArt direction:\n" + art[:4500]
        raw = await self.ask("implementation", CODER_CONTRACT, prompt, True)
        slug = "ai-" + self.context.run_id.lower()[:40] + "-" + sha256(self.context.run_id.encode()).hexdigest()[:8]
        tokens = Path(self.context.artifacts["design_tokens"]).read_text(encoding="utf-8")
        report = None
        bundle = None
        project = None
        for attempt in range(3):
            issues = []
            try:
                bundle = validate_bundle(raw, brief)
            except ValueError as error:
                issues = [str(error)[:1500]]
            if not issues:
                project = write_bundle(self.context.root, slug, bundle, tokens)
                self.context.complete_stage("implementation")
                if attempt:
                    self.context.complete_stage("repair")
                copy2(self.context.artifacts["design_document"], project / "DESIGN.md")
                self.context.start_stage("browser_qa")
                result = await self.team.run_role(role_class=BrowserQAAgent, stage="browser_qa", context=self.context,
                    instruction=json.dumps({"project_dir": str(project), "project_slug": slug,
                                            "output_dir": str(self.context.run_dir / f"ai-qa-{attempt + 1}")}))
                report = BrowserQAResult.model_validate_json(result.content)
                self.save("browser_qa", "browser-report.json", report.model_dump_json(indent=2))
                self.context.complete_stage("browser_qa")
                issues = [item.model_dump(exclude={"screenshot"}) for item in report.evidence if item.status != "passed"]
                if report.status == "passed":
                    break
            self.save(f"repair_findings_{attempt}", f"repair-findings-{attempt}.json", json.dumps(issues, ensure_ascii=False, indent=2))
            if attempt < 2:
                raw = await self.ask("repair", CODER_CONTRACT + "\nRepair only the supplied validation/browser findings while retaining the brand and page plan.",
                                     "Plan: " + brief.model_dump_json() + "\nCurrent bundle: " + raw + "\nFindings: " + json.dumps(issues)[:5000], True)
        passed = report is not None and report.status == "passed" and not issues
        self.save("quality_loop", "quality-loop.json", json.dumps({"status": "passed" if passed else "failed", "attempts": attempt + 1,
            "browser_checks_passed": passed, "aesthetic_score": None, "human_visual_review_required": True}, indent=2))
        if project and bundle:
            result = FrontendResult(status="generated" if passed else "blocked", project_slug=slug,
                project_dir=str(project), github_pages_entry=str(project / "index.html"), next_app_dir="",
                files=[GeneratedFile(path=name, kind="static") for name in [*bundle.files, "tokens.css", "DESIGN.md"]],
                unresolved_items=brief.unknowns + ["Human visual review and real backend integrations remain required."],
                gates=FrontendBuildGate(workspace_guardrail_passed=True, root_index_created=True,
                    github_pages_static_tree_created=True, semantic_html_passed=passed, responsive_contract_passed=passed,
                    required_skills_loaded=True, build_verified=passed), generated_by="DesignBrain")
            self.save("implementation", "frontend-result.json", result.model_dump_json(indent=2))
        if not passed:
            raise RuntimeError("AI draft chưa qua QA sau tối đa 2 lần sửa. Xem repair-findings và browser-report trong run.")
