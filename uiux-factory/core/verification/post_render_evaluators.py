from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Any

from core.actions.run_browser_qa import StaticServer
from core.contracts.browser_qa_schema import BrowserQAResult
from core.runtime.free_provider import ProviderError
from core.runtime.free_vision_provider import FreeVisionProvider
from core.verification.evidence_contract import EvidenceContractEvaluator


class PostRenderEvaluatorSuite:
    """Generate concrete evidence for previously untested prototype requirements.

    The suite is conservative by design: inability to demonstrate a state becomes
    ``cantTell`` rather than an invented PASS. Source files are never modified.
    Browser stress mutations live only inside disposable Playwright contexts.
    """

    SCHEMA_VERSION = 1
    EVALUATOR_VERSION = "1.0.0"
    LAB_FEEDBACK_MS = int(os.getenv("UIUX_LAB_FEEDBACK_MS", "200"))
    TRANSITION_MAX_MS = int(os.getenv("UIUX_TRANSITION_MAX_MS", "300"))
    PREFERRED_TOUCH_PX = int(os.getenv("UIUX_PREFERRED_TOUCH_PX", "44"))

    CONTROL_SELECTOR = (
        "button,[role='button'],input:not([type='hidden']),select,textarea,summary"
    )

    def __init__(
        self,
        *,
        run_dir: Path,
        project_dir: Path,
        browser_report_path: Path,
        evidence_dir: Path,
    ) -> None:
        self.run_dir = Path(run_dir).resolve()
        self.project_dir = Path(project_dir).resolve()
        self.browser_report_path = Path(browser_report_path).resolve()
        self.evidence_dir = Path(evidence_dir).resolve()
        self.evidence_dir.mkdir(parents=True, exist_ok=True)
        self.browser = BrowserQAResult.model_validate_json(
            self.browser_report_path.read_text(encoding="utf-8")
        )
        self.project_digest = EvidenceContractEvaluator.project_digest(self.project_dir)

    @staticmethod
    def _clean_json(text: str) -> str:
        value = text.strip()
        if value.startswith("```"):
            value = re.sub(r"^```(?:json)?\s*", "", value, flags=re.IGNORECASE)
            value = re.sub(r"\s*```$", "", value)
        start = value.find("{")
        end = value.rfind("}")
        return value[start : end + 1] if start >= 0 and end > start else value

    @staticmethod
    def _safe_route(route: str) -> str:
        return "home" if route == "/" else route.strip("/").replace("/", "__")

    def _base_report(self, evaluator: str) -> dict[str, Any]:
        return {
            "schema_version": self.SCHEMA_VERSION,
            "evaluator": evaluator,
            "evaluator_version": self.EVALUATOR_VERSION,
            "project_digest": self.project_digest,
            "requirements": {},
            "limitations": [],
        }

    def _write_report(self, filename: str, payload: dict[str, Any]) -> Path:
        path = self.run_dir / filename
        path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
        return path

    @staticmethod
    def _result(
        outcome: str,
        *,
        applicable: bool | None,
        rationale: str,
        test_targets: list[str] | None = None,
        evidence_files: list[str] | None = None,
    ) -> dict[str, Any]:
        return {
            "outcome": outcome,
            "applicable": applicable,
            "rationale": rationale,
            "test_targets": test_targets or [],
            "evidence_files": evidence_files or [],
        }

    @staticmethod
    def _style_changed(before: dict[str, str], after: dict[str, str]) -> bool:
        keys = (
            "color",
            "backgroundColor",
            "borderColor",
            "outlineStyle",
            "outlineColor",
            "boxShadow",
            "transform",
            "opacity",
        )
        return any(before.get(key) != after.get(key) for key in keys)

    @staticmethod
    def _parse_ms_list(value: str) -> list[float]:
        values: list[float] = []
        for part in str(value or "").split(","):
            item = part.strip().lower()
            try:
                if item.endswith("ms"):
                    values.append(float(item[:-2]))
                elif item.endswith("s"):
                    values.append(float(item[:-1]) * 1000.0)
            except ValueError:
                continue
        return values

    async def _open_local_page(self, browser, base_url: str, route: str, width: int, height: int):
        context = await browser.new_context(
            viewport={"width": width, "height": height},
            reduced_motion="no-preference",
            service_workers="block",
        )
        page = await context.new_page()
        await page.goto(base_url.rstrip("/") + route, wait_until="networkidle", timeout=30000)
        return context, page

    async def _run_interaction_state(self, browser, base_url: str) -> Path:
        report = self._base_report("state-interaction-crawler")
        route_rows: list[dict[str, Any]] = []
        trace_files: list[str] = []
        total_controls = 0
        core_state_failures: list[str] = []
        safely_tested_actions = 0
        feedback_failures: list[str] = []
        feedback_timings: list[float] = []
        transition_durations: list[float] = []
        multi_step_routes = 0
        multi_step_missing_current = 0
        forms_seen = 0
        form_error_demonstrated = 0
        form_success_demonstrated = 0
        search_seen = 0
        empty_demonstrated = 0
        loading_markers = 0
        success_markers = 0
        error_markers = 0

        for route in self.browser.routes:
            context, page = await self._open_local_page(browser, base_url, route, 1440, 1000)
            route_trace = self.evidence_dir / "interaction" / f"{self._safe_route(route)}-trace.zip"
            route_trace.parent.mkdir(parents=True, exist_ok=True)
            await context.tracing.start(screenshots=True, snapshots=True, sources=False)
            controls: list[dict[str, Any]] = []
            try:
                inventory = await page.evaluate(
                    """() => ({
                        forms: document.querySelectorAll('form').length,
                        searches: document.querySelectorAll('input[type="search"],[role="searchbox"]').length,
                        steps: document.querySelectorAll('[aria-current="step"],progress,[data-step],.step,.steps').length,
                        currentSteps: document.querySelectorAll('[aria-current="step"],[data-current-step],.step.active,.step.current').length,
                        loading: document.querySelectorAll('[aria-busy="true"],[data-state="loading"],.loading,.is-loading').length,
                        success: document.querySelectorAll('[role="status"],[data-state="success"],.success,.is-success').length,
                        error: document.querySelectorAll('[role="alert"],[data-state="error"],.error,.is-error').length
                    })"""
                )
                forms_seen += int(inventory.get("forms", 0))
                search_seen += int(inventory.get("searches", 0))
                if int(inventory.get("steps", 0)):
                    multi_step_routes += 1
                    if not int(inventory.get("currentSteps", 0)):
                        multi_step_missing_current += 1
                loading_markers += int(inventory.get("loading", 0))
                success_markers += int(inventory.get("success", 0))
                error_markers += int(inventory.get("error", 0))

                locators = page.locator(self.CONTROL_SELECTOR)
                count = min(await locators.count(), 10)
                for index in range(count):
                    locator = locators.nth(index)
                    if not await locator.is_visible():
                        continue
                    total_controls += 1
                    label = (
                        (await locator.get_attribute("aria-label"))
                        or (await locator.inner_text())
                        or (await locator.get_attribute("name"))
                        or f"control-{index}"
                    ).strip()[:120]
                    tag = await locator.evaluate("el => el.tagName.toLowerCase()")
                    role = (await locator.get_attribute("role")) or ""
                    input_type = (await locator.get_attribute("type")) or ""

                    async def style_signature() -> dict[str, str]:
                        return await locator.evaluate(
                            """el => { const s=getComputedStyle(el); return {
                                color:s.color,backgroundColor:s.backgroundColor,borderColor:s.borderColor,
                                outlineStyle:s.outlineStyle,outlineColor:s.outlineColor,boxShadow:s.boxShadow,
                                transform:s.transform,opacity:s.opacity,transitionDuration:s.transitionDuration,
                                animationDuration:s.animationDuration
                            }}"""
                        )

                    default = await style_signature()
                    hover = default
                    focus = default
                    pressed = default
                    try:
                        await locator.hover(timeout=1500)
                        hover = await style_signature()
                    except Exception:
                        pass
                    try:
                        await locator.focus(timeout=1500)
                        focus = await style_signature()
                    except Exception:
                        pass
                    try:
                        box = await locator.bounding_box()
                        if box:
                            await page.mouse.move(box["x"] + box["width"] / 2, box["y"] + box["height"] / 2)
                            await page.mouse.down()
                            pressed = await style_signature()
                            await page.mouse.up()
                    except Exception:
                        try:
                            await page.mouse.up()
                        except Exception:
                            pass

                    needs_pointer_states = tag in {"button", "summary"} or role == "button" or input_type in {"button", "submit", "reset"}
                    hover_ok = self._style_changed(default, hover) if needs_pointer_states else True
                    press_ok = self._style_changed(default, pressed) if needs_pointer_states else True
                    focus_ok = self._style_changed(default, focus)
                    if not (hover_ok and press_ok and focus_ok):
                        core_state_failures.append(f"{route}:{label}")

                    durations = self._parse_ms_list(default.get("transitionDuration", ""))
                    durations += self._parse_ms_list(default.get("animationDuration", ""))
                    transition_durations.extend(value for value in durations if value > 0)

                    before_state = await locator.evaluate(
                        """el => ({expanded:el.getAttribute('aria-expanded'),pressed:el.getAttribute('aria-pressed'),checked:el.checked ?? null,open:el.open ?? null,value:el.value ?? null})"""
                    )
                    can_toggle = (
                        before_state.get("expanded") is not None
                        or before_state.get("pressed") is not None
                        or input_type in {"checkbox", "radio"}
                        or tag == "summary"
                    )
                    action_changed = None
                    elapsed = None
                    if can_toggle:
                        safely_tested_actions += 1
                        try:
                            started = await page.evaluate("performance.now()")
                            if input_type in {"checkbox", "radio"}:
                                await locator.click(timeout=1500)
                            else:
                                await locator.click(timeout=1500)
                            await page.evaluate("() => new Promise(r => requestAnimationFrame(() => requestAnimationFrame(r)))")
                            ended = await page.evaluate("performance.now()")
                            elapsed = float(ended) - float(started)
                            after_state = await locator.evaluate(
                                """el => ({expanded:el.getAttribute('aria-expanded'),pressed:el.getAttribute('aria-pressed'),checked:el.checked ?? null,open:el.open ?? null,value:el.value ?? null})"""
                            )
                            action_changed = before_state != after_state
                            feedback_timings.append(elapsed)
                            if not action_changed:
                                feedback_failures.append(f"{route}:{label}")
                        except Exception:
                            feedback_failures.append(f"{route}:{label}")

                    controls.append(
                        {
                            "label": label,
                            "tag": tag,
                            "role": role,
                            "type": input_type,
                            "hover_distinct": hover_ok,
                            "press_distinct": press_ok,
                            "focus_distinct": focus_ok,
                            "safe_action_tested": can_toggle,
                            "feedback_changed": action_changed,
                            "feedback_ms": elapsed,
                        }
                    )

                if int(inventory.get("forms", 0)):
                    forms = page.locator("form")
                    for idx in range(min(await forms.count(), 3)):
                        form = forms.nth(idx)
                        invalid = await form.evaluate(
                            """form => { for (const el of form.querySelectorAll('input,textarea,select')) { if (el.required && 'value' in el) el.value=''; } form.reportValidity(); return form.querySelectorAll(':invalid').length; }"""
                        )
                        if int(invalid) > 0:
                            form_error_demonstrated += 1
                        success = await page.locator("[role='status'],[data-state='success'],.success,.is-success").count()
                        if success:
                            form_success_demonstrated += 1

                searches = page.locator("input[type='search'],[role='searchbox']")
                if await searches.count():
                    search = searches.first
                    try:
                        await search.fill("không-có-kết-quả-uiux-987654321")
                        await page.wait_for_timeout(120)
                        empty_count = await page.locator(
                            "[data-state='empty'],.empty,.no-results,:text-matches('no results|không có kết quả|không tìm thấy','i')"
                        ).count()
                        if empty_count:
                            empty_demonstrated += 1
                    except Exception:
                        pass

                route_rows.append({"route": route, "controls": controls, "inventory": inventory})
            finally:
                await context.tracing.stop(path=str(route_trace))
                trace_files.append(str(route_trace))
                await context.close()

        req = report["requirements"]
        req["INTERACTION-002"] = req["STATE-001"] = self._result(
            "inapplicable" if total_controls == 0 else ("passed" if not core_state_failures else "failed"),
            applicable=False if total_controls == 0 else True,
            rationale=(
                "No representative interactive controls were found."
                if total_controls == 0
                else (
                    f"Hover/pressed/focus evidence passed for {total_controls} tested controls."
                    if not core_state_failures
                    else f"Core visual states were not distinct for {len(core_state_failures)} tested controls."
                )
            ),
            test_targets=[str(value) for value in core_state_failures[:12]],
            evidence_files=trace_files,
        )
        req["UX-006"] = self._result(
            "inapplicable" if total_controls == 0 else ("cantTell" if safely_tested_actions == 0 else ("passed" if not feedback_failures else "failed")),
            applicable=False if total_controls == 0 else True,
            rationale=(
                "No interactive controls were present."
                if total_controls == 0
                else (
                    "No control exposed a safely testable local toggle state; broader action feedback remains unknown."
                    if safely_tested_actions == 0
                    else (
                        f"Visible/state feedback changed for all {safely_tested_actions} safely tested actions."
                        if not feedback_failures
                        else f"{len(feedback_failures)} safely tested actions did not expose observable feedback."
                    )
                )
            ),
            test_targets=feedback_failures[:12],
            evidence_files=trace_files,
        )
        req["UX-007"] = self._result(
            "inapplicable" if multi_step_routes == 0 else ("passed" if multi_step_missing_current == 0 else "failed"),
            applicable=False if multi_step_routes == 0 else True,
            rationale=(
                "No multi-step flow marker was detected."
                if multi_step_routes == 0
                else (
                    "Every detected multi-step route exposed a current/progress marker."
                    if multi_step_missing_current == 0
                    else f"{multi_step_missing_current} multi-step routes lacked an observable current-step marker."
                )
            ),
            evidence_files=trace_files,
        )
        req["UX-008"] = self._result(
            "inapplicable" if total_controls == 0 else ("cantTell" if not feedback_timings else ("passed" if max(feedback_timings) <= self.LAB_FEEDBACK_MS else "failed")),
            applicable=False if total_controls == 0 else True,
            rationale=(
                "No interactive controls were present."
                if total_controls == 0
                else (
                    "No safely measurable state-changing interaction was found."
                    if not feedback_timings
                    else f"Maximum measured local interaction-to-observable-state time was {max(feedback_timings):.1f}ms; lab policy is <= {self.LAB_FEEDBACK_MS}ms."
                )
            ),
            evidence_files=trace_files,
        )
        req["INTERACTION-003"] = self._result(
            "inapplicable" if not transition_durations else ("passed" if max(transition_durations) <= self.TRANSITION_MAX_MS else "failed"),
            applicable=False if not transition_durations else True,
            rationale=(
                "No non-zero CSS transition/animation durations were found on tested controls."
                if not transition_durations
                else f"Maximum tested control transition/animation duration was {max(transition_durations):.1f}ms; prototype policy is <= {self.TRANSITION_MAX_MS}ms."
            ),
            evidence_files=trace_files,
        )
        motion_present = bool(transition_durations)
        req["INTERACTION-001"] = self._result(
            "inapplicable" if not motion_present else "cantTell",
            applicable=False if not motion_present else True,
            rationale=(
                "No material control motion was detected."
                if not motion_present
                else "Motion exists, but generic browser state crawling cannot establish whether one signature motion moment received the highest visual polish."
            ),
            evidence_files=trace_files,
        )
        waiting_applicable = loading_markers > 0
        req["STATE-002"] = self._result(
            "inapplicable" if not waiting_applicable else "passed",
            applicable=waiting_applicable,
            rationale=(
                "No loading/waiting marker was observed, so loading-state applicability was not established."
                if not waiting_applicable
                else f"Observed {loading_markers} loading/busy state marker(s)."
            ),
            evidence_files=trace_files,
        )
        req["STATE-003"] = self._result(
            "inapplicable" if search_seen == 0 else ("passed" if empty_demonstrated > 0 else "cantTell"),
            applicable=False if search_seen == 0 else True,
            rationale=(
                "No search control was detected."
                if search_seen == 0
                else (
                    "A no-results/empty state became observable under an impossible-query stress input."
                    if empty_demonstrated > 0
                    else "Search exists, but an empty/no-results state could not be demonstrated generically."
                )
            ),
            evidence_files=trace_files,
        )
        state4_outcome = "inapplicable" if forms_seen == 0 else ("passed" if form_error_demonstrated > 0 and (form_success_demonstrated > 0 or success_markers > 0) else "cantTell")
        req["STATE-004"] = self._result(
            state4_outcome,
            applicable=False if forms_seen == 0 else True,
            rationale=(
                "No forms/fallible actions were detected."
                if forms_seen == 0
                else f"Error demonstrations={form_error_demonstrated}; success markers/demonstrations={max(success_markers, form_success_demonstrated)}. Both are required for PASS."
            ),
            evidence_files=trace_files,
        )
        feedback_applicable = forms_seen > 0 or loading_markers > 0 or success_markers > 0 or error_markers > 0
        feedback_complete = (
            (loading_markers > 0 if loading_markers else True)
            and (form_error_demonstrated > 0 or error_markers > 0 if forms_seen else True)
            and (form_success_demonstrated > 0 or success_markers > 0 if forms_seen else True)
        )
        req["INTERACTION-005"] = self._result(
            "inapplicable" if not feedback_applicable else ("passed" if feedback_complete else "cantTell"),
            applicable=False if not feedback_applicable else True,
            rationale=(
                "No waiting/form/fallible feedback path was detected."
                if not feedback_applicable
                else "Observed feedback-state evidence is complete for the generically testable path." if feedback_complete else "A feedback path appears applicable, but loading/error/success/validation completeness could not all be demonstrated generically."
            ),
            evidence_files=trace_files,
        )
        report["routes"] = route_rows
        report["timing_policy_ms"] = self.LAB_FEEDBACK_MS
        report["transition_policy_ms"] = self.TRANSITION_MAX_MS
        report["limitations"].append(
            "Generic crawler clicks only local toggle-like controls; transactional/destructive actions are not blindly invoked."
        )
        return self._write_report("interaction-state-report.json", report)

    async def _run_touch_targets(self, browser, base_url: str) -> Path:
        report = self._base_report("preferred-touch-targets")
        targets: list[dict[str, Any]] = []
        failures: list[dict[str, Any]] = []
        screenshots: list[str] = []

        for route in self.browser.routes:
            context, page = await self._open_local_page(browser, base_url, route, 390, 844)
            try:
                rows = await page.evaluate(
                    """() => Array.from(document.querySelectorAll("button,[role='button'],input[type='button'],input[type='submit'],input[type='reset'],select,[aria-expanded]"))
                      .filter(el => { const r=el.getBoundingClientRect(), s=getComputedStyle(el); return r.width>0 && r.height>0 && s.display!=='none' && s.visibility!=='hidden'; })
                      .map((el,i) => { const r=el.getBoundingClientRect(); return {
                        index:i, label:(el.getAttribute('aria-label')||el.textContent||el.getAttribute('name')||el.tagName).trim().slice(0,100),
                        width:r.width,height:r.height, exception:(el.getAttribute('data-touch-target-exception')||'').trim()
                      }; })"""
                )
                for row in rows:
                    row["route"] = route
                    targets.append(row)
                    if (
                        (float(row["width"]) < self.PREFERRED_TOUCH_PX or float(row["height"]) < self.PREFERRED_TOUCH_PX)
                        and not row.get("exception")
                    ):
                        failures.append(row)
                shot = self.evidence_dir / "touch-targets" / f"{self._safe_route(route)}-mobile.png"
                shot.parent.mkdir(parents=True, exist_ok=True)
                await page.screenshot(path=str(shot), full_page=True)
                screenshots.append(str(shot))
            finally:
                await context.close()

        report["preferred_target_css_px"] = self.PREFERRED_TOUCH_PX
        report["targets"] = targets
        report["requirements"]["RESPONSIVE-003"] = self._result(
            "inapplicable" if not targets else ("passed" if not failures else "failed"),
            applicable=False if not targets else True,
            rationale=(
                "No important mobile touch controls were found."
                if not targets
                else (
                    f"All {len(targets)} important mobile controls met the preferred {self.PREFERRED_TOUCH_PX}px target or declared an explicit exception."
                    if not failures
                    else f"{len(failures)} of {len(targets)} important mobile controls were below the preferred {self.PREFERRED_TOUCH_PX}px target without an explicit exception."
                )
            ),
            test_targets=[f"{row['route']}:{row['label']} {row['width']:.0f}x{row['height']:.0f}" for row in failures[:20]],
            evidence_files=screenshots,
        )
        report["limitations"].append(
            "This is a prototype quality preference (44 CSS px by default), not a claim that WCAG 2.2 AA requires 44px."
        )
        return self._write_report("touch-target-metrics.json", report)

    async def _run_content_stress(self, browser, base_url: str) -> Path:
        report = self._base_report("content-stress")
        fixtures = [
            "Bộ sưu tập nước hoa thủ công phiên bản giới hạn dành cho những khoảnh khắc đáng nhớ",
            "Nguyễn Thị Minh Anh — khách hàng thân thiết tại Thành phố Hồ Chí Minh",
            "99.999.999.999 ₫",
            "Supercalifragilisticexpialidocious-UIUX-Extremely-Long-Unbroken-Identifier-987654321",
        ]
        failures: list[dict[str, Any]] = []
        tested_targets = 0
        screenshots: list[str] = []

        for route in self.browser.routes:
            for name, width, height in (("mobile", 390, 844), ("tablet", 768, 1024), ("desktop", 1440, 1000)):
                context, page = await self._open_local_page(browser, base_url, route, width, height)
                try:
                    baseline = await page.evaluate("() => Math.max(document.documentElement.scrollWidth, document.body.scrollWidth) - document.documentElement.clientWidth")
                    changed = await page.evaluate(
                        """fixtures => {
                          const visible = el => { const r=el.getBoundingClientRect(),s=getComputedStyle(el); return r.width>0&&r.height>0&&s.display!=='none'&&s.visibility!=='hidden'; };
                          const nodes=Array.from(document.querySelectorAll('h1,h2,h3,p,li,button,label,a,span,td,th')).filter(el=>visible(el)&&(el.textContent||'').trim().length>=2).slice(0,16);
                          nodes.forEach((el,i)=>{ el.textContent=fixtures[i%fixtures.length]; el.setAttribute('data-uiux-stress-target','1'); });
                          return nodes.length;
                        }""",
                        fixtures,
                    )
                    tested_targets += int(changed)
                    await page.evaluate("() => new Promise(r => requestAnimationFrame(() => requestAnimationFrame(r)))")
                    metrics = await page.evaluate(
                        """() => {
                          const root=document.documentElement, body=document.body;
                          const overflow=Math.max(root.scrollWidth,body.scrollWidth)-root.clientWidth;
                          const clipped=Array.from(document.querySelectorAll('[data-uiux-stress-target="1"]')).filter(el=>{
                            const r=el.getBoundingClientRect(),s=getComputedStyle(el);
                            const intrinsic=el.scrollWidth>el.clientWidth+2;
                            const clippedStyle=['hidden','clip'].includes(s.overflowX)||['hidden','clip'].includes(s.overflow);
                            return r.right>innerWidth+2 || (intrinsic&&clippedStyle);
                          }).length;
                          return {overflow,clipped};
                        }"""
                    )
                    if float(metrics["overflow"]) > max(2.0, float(baseline) + 2.0) or int(metrics["clipped"]) > 0:
                        failures.append({"route": route, "viewport": name, "overflow": metrics["overflow"], "clipped": metrics["clipped"]})
                    shot = self.evidence_dir / "content-stress" / f"{self._safe_route(route)}-{name}.png"
                    shot.parent.mkdir(parents=True, exist_ok=True)
                    await page.screenshot(path=str(shot), full_page=True)
                    screenshots.append(str(shot))
                finally:
                    await context.close()

        report["fixtures"] = fixtures
        report["failures"] = failures
        report["requirements"]["RESPONSIVE-004"] = self._result(
            "inapplicable" if tested_targets == 0 else ("passed" if not failures else "failed"),
            applicable=False if tested_targets == 0 else True,
            rationale=(
                "No visible textual targets were available for stress testing."
                if tested_targets == 0
                else (
                    f"Long/Vietnamese/large-value stress content produced no new horizontal overflow or clipping across {len(screenshots)} route/viewport renders."
                    if not failures
                    else f"Content stress caused overflow/clipping in {len(failures)} route/viewport renders."
                )
            ),
            test_targets=[f"{row['route']}@{row['viewport']}" for row in failures[:20]],
            evidence_files=screenshots,
        )
        report["limitations"].append("Stress text is injected only into disposable browser DOM; generated source files remain unchanged.")
        return self._write_report("content-stress-report.json", report)

    def _representative_screenshots(self) -> dict[str, Path]:
        selected: dict[str, tuple[int, Path]] = {}
        for item in self.browser.evidence:
            path = Path(item.screenshot).resolve()
            if not path.is_file():
                continue
            area = int(item.viewport.width) * int(item.viewport.height)
            if item.route not in selected or area > selected[item.route][0]:
                selected[item.route] = (area, path)
        return {route: value[1] for route, value in selected.items()}

    def _composition_orders(self) -> dict[str, list[str]]:
        path = self.run_dir / "visual-composition.json"
        if not path.is_file():
            return {}
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return {}
        orders: dict[str, list[str]] = {}
        rank = {"P0": 0, "P1": 1, "P2": 2}
        for page in payload.get("pages", []):
            route = str(page.get("path", "/"))
            anchors: list[str] = []
            first = str(page.get("first_visual_anchor", "")).strip()
            if first:
                anchors.append(first)
            sections = list(enumerate(page.get("sections", [])))
            sections.sort(key=lambda pair: (rank.get(str(pair[1].get("priority", "P1")), 1), pair[0]))
            for _, section in sections:
                anchor = str(section.get("visual_anchor", "")).strip()
                if anchor and anchor not in anchors:
                    anchors.append(anchor)
            orders[route] = anchors[:3]
        return orders

    async def _run_squint(self) -> Path:
        report = self._base_report("squint-critic")
        screenshots = self._representative_screenshots()
        expected = self._composition_orders()
        blurred: list[tuple[str, Path]] = []
        blurred_files: list[str] = []

        try:
            from PIL import Image, ImageFilter
        except ImportError:
            report["requirements"]["VISUAL-010"] = report["requirements"]["CRITIQUE-001"] = self._result(
                "cantTell", applicable=True, rationale="Pillow is unavailable, so blurred/squint evidence could not be generated."
            )
            return self._write_report("squint-review.json", report)

        for route, source in screenshots.items():
            target = self.evidence_dir / "squint" / f"{self._safe_route(route)}-blurred.png"
            target.parent.mkdir(parents=True, exist_ok=True)
            with Image.open(source).convert("RGB") as image:
                width = max(1, image.width // 4)
                height = max(1, image.height // 4)
                reduced = image.resize((width, height))
                blurred_image = reduced.filter(ImageFilter.GaussianBlur(radius=max(4, min(width, height) / 40)))
                blurred_image.save(target)
            blurred.append((f"route={route}; candidates={json.dumps(sorted(expected.get(route, [])), ensure_ascii=False)}", target))
            blurred_files.append(str(target))

        if not blurred:
            result = self._result("untested", applicable=None, rationale="No representative screenshots were available for squint transformation.")
            report["requirements"]["VISUAL-010"] = report["requirements"]["CRITIQUE-001"] = result
            return self._write_report("squint-review.json", report)

        missing_intent = [route for route in screenshots if len(expected.get(route, [])) < 3]
        try:
            provider = FreeVisionProvider.from_env(Path(__file__).resolve().parents[2])
            prompt = (
                "Inspect only the supplied blurred screenshots. For each route, rank exactly three visible priorities using only the candidate labels supplied in that image label. "
                "Do not use the candidate list order as the answer; it is alphabetized. Return JSON: {\"routes\":[{\"route\":\"/\",\"ranking\":[\"...\",\"...\",\"...\"],\"evidence\":[\"...\"]}]}."
            )
            response = await provider.complete_vision(
                stage="visual_qa_squint",
                system="You are performing a squint/blur hierarchy test. Judge only blurred visual dominance; ignore detailed copy.",
                prompt=prompt,
                images=blurred,
            )
            payload = json.loads(self._clean_json(response))
            observed = {str(row.get("route", "")): [str(v) for v in row.get("ranking", [])[:3]] for row in payload.get("routes", [])}
        except (ProviderError, ValueError, json.JSONDecodeError) as exc:
            report["limitations"].append(f"Vision squint review unavailable: {exc}")
            observed = {}

        mismatches = []
        incomplete = list(missing_intent)
        for route in screenshots:
            if len(expected.get(route, [])) < 3:
                continue
            if len(observed.get(route, [])) < 3:
                incomplete.append(route)
                continue
            exp = [value.casefold().strip() for value in expected[route][:3]]
            got = [value.casefold().strip() for value in observed[route][:3]]
            if got != exp:
                mismatches.append(route)

        outcome = "cantTell" if incomplete else ("failed" if mismatches else "passed")
        rationale = (
            "Squint comparison could not be completed for routes lacking three intended anchors or complete vision output: " + ", ".join(sorted(set(incomplete)))
            if incomplete
            else (
                "Blurred visual priority order matched the intended first/second/third anchors for every representative route."
                if not mismatches
                else "Blurred visual priority order did not match the intended hierarchy on: " + ", ".join(mismatches)
            )
        )
        result = self._result(
            outcome,
            applicable=True,
            rationale=rationale,
            test_targets=mismatches + sorted(set(incomplete)),
            evidence_files=blurred_files,
        )
        report["expected"] = expected
        report["observed"] = observed
        report["requirements"]["VISUAL-010"] = result
        report["requirements"]["CRITIQUE-001"] = self._result(
            "passed" if observed and not incomplete else "cantTell",
            applicable=True,
            rationale=("Every representative route received a blurred hierarchy review." if observed and not incomplete else "Blurred screenshots exist, but complete route-level squint review evidence is missing."),
            evidence_files=blurred_files,
        )
        return self._write_report("squint-review.json", report)

    @staticmethod
    def _extract_intent(run_dir: Path) -> dict[str, str]:
        research = (run_dir / "research.md").read_text(encoding="utf-8", errors="ignore") if (run_dir / "research.md").is_file() else ""
        ux = (run_dir / "ux-ia.md").read_text(encoding="utf-8", errors="ignore") if (run_dir / "ux-ia.md").is_file() else ""
        def grab(text: str, patterns: list[str]) -> str:
            for pattern in patterns:
                match = re.search(pattern, text, flags=re.IGNORECASE)
                if match:
                    value = match.group(1).strip().strip("`* -")
                    if value and value.upper() not in {"UNKNOWN", "NEEDS_VALIDATION"}:
                        return value
            return ""
        website_type = grab(research, [r"Website archetype:\s*`?([^`\n]+)", r"website type:\s*`?([^`\n]+)"])
        vertical = grab(research, [r"Vertical/sub-industry:\s*`?([^`\n]+)", r"vertical:\s*`?([^`\n]+)"])
        audience = grab(ux, [r"Primary audience:\s*`?([^`\n]+)"])
        action = grab(ux, [r"Highest-value user task:\s*`?([^`\n]+)", r"Primary conversion:\s*`?([^`\n]+)"])
        return {
            "site_identity": " ".join(value for value in (vertical, website_type) if value).strip(),
            "audience": audience,
            "primary_action": action,
        }

    @staticmethod
    def _token_overlap(expected: str, observed: str) -> float:
        tokens = lambda value: {token for token in re.findall(r"[\wÀ-ỹ-]+", value.casefold()) if len(token) >= 3}
        left = tokens(expected)
        right = tokens(observed)
        if not left or not right:
            return 0.0
        return len(left & right) / max(1, len(left))

    async def _run_blind_five_second(self) -> Path:
        report = self._base_report("blind-five-second")
        screenshots = self._representative_screenshots()
        source = screenshots.get("/") or (next(iter(screenshots.values())) if screenshots else None)
        intent = self._extract_intent(self.run_dir)
        if source is None:
            report["requirements"]["CRITIQUE-002"] = self._result("untested", applicable=None, rationale="No representative entry screenshot was available.")
            return self._write_report("blind-five-second-review.json", report)

        observed: dict[str, Any] = {}
        try:
            provider = FreeVisionProvider.from_env(Path(__file__).resolve().parents[2])
            response = await provider.complete_vision(
                stage="visual_qa_blind_five_second",
                system=(
                    "You are a blind first-impression evaluator. You receive only a screenshot and no project brief. "
                    "Infer what the site is, who it appears to be for, and the primary next action. Do not invent hidden functionality."
                ),
                prompt=(
                    "Return JSON only: {\"site_identity\":\"...\",\"audience\":\"...\",\"primary_action\":\"...\",\"confidence\":0,\"evidence\":[\"...\"]}. "
                    "Treat this as a screenshot comprehension proxy, not participant usability research."
                ),
                images=[("blind-entry-screenshot", source)],
            )
            observed = json.loads(self._clean_json(response))
        except (ProviderError, ValueError, json.JSONDecodeError) as exc:
            report["limitations"].append(f"Blind vision review unavailable: {exc}")

        missing_expected = [key for key, value in intent.items() if not value]
        if not observed or missing_expected:
            outcome = "cantTell"
            rationale = (
                "Blind screenshot observation or structured intended identity/audience/action is incomplete; cannot truthfully compare first-impression comprehension."
            )
        else:
            scores = {
                key: self._token_overlap(intent[key], str(observed.get(key, "")))
                for key in ("site_identity", "audience", "primary_action")
            }
            outcome = "passed" if all(value >= 0.25 for value in scores.values()) else "failed"
            rationale = (
                "Blind screenshot inference matched the structured intended identity, audience and primary action."
                if outcome == "passed"
                else "Blind screenshot inference did not sufficiently match one or more intended comprehension targets."
            )
            report["comparison_scores"] = scores

        report["intent"] = intent
        report["observed"] = observed
        report["requirements"]["CRITIQUE-002"] = self._result(
            outcome,
            applicable=True,
            rationale=rationale,
            test_targets=missing_expected,
            evidence_files=[str(source)],
        )
        report["limitations"].append(
            "This is an AI blind-screenshot proxy. It must not be reported as a real five-second participant usability test."
        )
        return self._write_report("blind-five-second-review.json", report)

    async def run(self) -> dict[str, str]:
        outputs: dict[str, str] = {}
        try:
            from playwright.async_api import async_playwright
        except ImportError as exc:
            raise RuntimeError("Post-render evidence evaluators require Python Playwright.") from exc

        with StaticServer(self.project_dir) as server:
            base_url = f"http://127.0.0.1:{server.port}"
            async with async_playwright() as playwright:
                browser = await playwright.chromium.launch(headless=True)
                try:
                    outputs["interaction_state"] = str(await self._run_interaction_state(browser, base_url))
                    outputs["touch_targets"] = str(await self._run_touch_targets(browser, base_url))
                    outputs["content_stress"] = str(await self._run_content_stress(browser, base_url))
                finally:
                    await browser.close()

        outputs["squint"] = str(await self._run_squint())
        outputs["blind_five_second"] = str(await self._run_blind_five_second())
        return outputs
