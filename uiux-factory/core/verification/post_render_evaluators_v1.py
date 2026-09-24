from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from core.actions.run_browser_qa import StaticServer
from core.runtime.free_provider import ProviderError
from core.runtime.free_vision_provider import FreeVisionProvider
from core.verification.evidence_contract import EvidenceContractEvaluator, RequirementRegistry
from core.verification.post_render_evaluators_wcag import (
    PostRenderEvaluatorSuite as WCAGPostRenderEvaluatorSuite,
)


class PostRenderEvaluatorSuite(WCAGPostRenderEvaluatorSuite):
    """Final V1 evidence suite.

    This layer closes the remaining machine-verifiable evaluator families without
    weakening the conservative outcome semantics established by the Evidence
    Contract. A missing contract, unavailable vision provider, or ambiguous user
    journey becomes ``cantTell``/``untested`` rather than an invented PASS.
    """

    EVALUATOR_VERSION = "2.0.0"
    MAX_FONT_FAMILIES = int(os.getenv("UIUX_MAX_FONT_FAMILIES", "3"))
    MOBILE_BODY_MIN_PX = float(os.getenv("UIUX_MOBILE_BODY_MIN_PX", "16"))
    MAX_LONGFORM_CHARS_PER_LINE = float(os.getenv("UIUX_MAX_LONGFORM_CHARS_PER_LINE", "95"))
    CONTROL_MOTION_MAX_MS = float(os.getenv("UIUX_CONTROL_MOTION_MAX_MS", "300"))

    @staticmethod
    def _json_file(path: Path) -> dict[str, Any]:
        try:
            value = json.loads(path.read_text(encoding="utf-8"))
            return value if isinstance(value, dict) else {}
        except (OSError, json.JSONDecodeError):
            return {}

    @staticmethod
    def _text_file(path: Path) -> str:
        try:
            return path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            return ""

    @staticmethod
    def _parse_duration_ms(value: str) -> float:
        values = WCAGPostRenderEvaluatorSuite._parse_ms_list(value)
        return max(values) if values else 0.0

    async def _run_design_system_metrics(self) -> Path:
        report = self._base_report("design-system-metrics")
        path = self.run_dir / "design-system.json"
        payload = self._json_file(path)
        if not payload:
            report["requirements"]["VISUAL-005"] = self._result(
                "cantTell",
                applicable=True,
                rationale="design-system.json is missing or unreadable; font-role restraint cannot be verified.",
            )
            return self._write_report("design-system-metrics.json", report)

        foundations = payload.get("foundations") or {}
        typography = foundations.get("typography") or {}
        semantic_colors = foundations.get("semantic_colors") or {}
        family_rows: list[dict[str, str]] = []
        for name, raw in typography.items() if isinstance(typography, dict) else []:
            if "family" not in str(name).casefold():
                continue
            value = raw.get("value") if isinstance(raw, dict) else raw
            text = str(value or "").strip()
            if not text or text.casefold() in {"unknown", "none", "null"}:
                continue
            primary = text.split(",", 1)[0].strip().strip("'\"").casefold()
            family_rows.append({"token": str(name), "value": text, "primary_family": primary})

        unique_families = sorted({row["primary_family"] for row in family_rows if row["primary_family"]})
        role_tokens = sorted(row["token"] for row in family_rows)
        if not unique_families:
            outcome = "cantTell"
            rationale = "No resolved font-family role tokens were found in the design system."
        elif len(unique_families) > self.MAX_FONT_FAMILIES:
            outcome = "failed"
            rationale = (
                f"Design system resolves {len(unique_families)} primary font families; "
                f"V1 restraint policy allows at most {self.MAX_FONT_FAMILIES} unless a future explicit exception is modeled."
            )
        else:
            outcome = "passed"
            rationale = (
                f"Design system uses {len(unique_families)} resolved primary font family/families across explicit roles: "
                + ", ".join(role_tokens)
                + "."
            )

        report["metrics"] = {
            "font_family_limit": self.MAX_FONT_FAMILIES,
            "font_families": unique_families,
            "font_role_tokens": role_tokens,
            "semantic_color_roles": sorted(str(key) for key in semantic_colors) if isinstance(semantic_colors, dict) else [],
            "component_count": len(payload.get("components") or []),
        }
        report["requirements"]["VISUAL-005"] = self._result(
            outcome,
            applicable=True,
            rationale=rationale,
            test_targets=unique_families if outcome != "passed" else [],
            evidence_files=[str(path)] if path.is_file() else [],
        )
        return self._write_report("design-system-metrics.json", report)

    @staticmethod
    def _typography_measure_script() -> str:
        return r"""() => {
          const visible = el => { const r=el.getBoundingClientRect(),s=getComputedStyle(el); return r.width>1&&r.height>1&&s.display!=='none'&&s.visibility!=='hidden'; };
          const px = value => { const n=parseFloat(value); return Number.isFinite(n)?n:0; };
          const rows=[];
          for(const el of Array.from(document.querySelectorAll('h1,h2,h3,h4,h5,h6,p,li,blockquote,label,button')).filter(visible).slice(0,180)){
            const s=getComputedStyle(el),r=el.getBoundingClientRect(),text=(el.textContent||'').trim().replace(/\s+/g,' ');
            const font=px(s.fontSize), line=px(s.lineHeight);
            rows.push({
              tag:el.tagName.toLowerCase(), text:text.slice(0,220), chars:text.length,
              fontSize:font, lineHeight:line, lineHeightRatio:font?line/font:0,
              width:r.width, approxCharsPerLine:font?r.width/(font*.52):0,
              family:s.fontFamily, weight:s.fontWeight,
              overflowX:el.scrollWidth>el.clientWidth+2, overflowY:el.scrollHeight>el.clientHeight+2 && ['hidden','clip'].includes(s.overflowY)
            });
          }
          return rows;
        }"""

    async def _run_typography_metrics(self, browser, base_url: str) -> Path:
        report = self._base_report("typography-metrics")
        cases: list[dict[str, Any]] = []
        hierarchy_failures: list[str] = []
        longform_failures: list[str] = []
        screenshots: list[str] = []
        total_text = 0
        longform_count = 0

        for route in self.browser.routes:
            for viewport, width, height in (("mobile", 390, 844), ("desktop", 1440, 1000)):
                context, page = await self._open_local_page(browser, base_url, route, width, height)
                try:
                    rows = await page.evaluate(self._typography_measure_script())
                    total_text += len(rows)
                    headings: dict[str, float] = {}
                    for row in rows:
                        tag = str(row.get("tag", ""))
                        if tag in {"h1", "h2", "h3"} and tag not in headings:
                            headings[tag] = float(row.get("fontSize", 0))
                        if tag in {"p", "li", "blockquote"} and int(row.get("chars", 0)) >= 40:
                            if viewport == "mobile" and float(row.get("fontSize", 0)) + .01 < self.MOBILE_BODY_MIN_PX:
                                hierarchy_failures.append(f"{route}@mobile:{tag} {row.get('fontSize')}px")
                            ratio = float(row.get("lineHeightRatio", 0))
                            if ratio and not 1.25 <= ratio <= 2.0:
                                hierarchy_failures.append(f"{route}@{viewport}:{tag} line-height={ratio:.2f}")
                        if tag in {"p", "li", "blockquote"} and int(row.get("chars", 0)) >= 160:
                            longform_count += 1
                            measure = float(row.get("approxCharsPerLine", 0))
                            if measure > self.MAX_LONGFORM_CHARS_PER_LINE or bool(row.get("overflowX")) or bool(row.get("overflowY")):
                                longform_failures.append(f"{route}@{viewport}:{tag} ~{measure:.0f}ch")
                    if headings.get("h1", 0) and headings.get("h2", 0) and headings["h1"] + 1 < headings["h2"]:
                        hierarchy_failures.append(f"{route}@{viewport}: h1<h2")
                    if headings.get("h2", 0) and headings.get("h3", 0) and headings["h2"] + 1 < headings["h3"]:
                        hierarchy_failures.append(f"{route}@{viewport}: h2<h3")
                    shot = self.evidence_dir / "typography" / f"{self._safe_route(route)}-{viewport}.png"
                    shot.parent.mkdir(parents=True, exist_ok=True)
                    await page.screenshot(path=str(shot), full_page=True)
                    screenshots.append(str(shot))
                    cases.append({"route": route, "viewport": viewport, "rows": rows})
                finally:
                    await context.close()

        if total_text == 0:
            type_outcome, type_applicable = "inapplicable", False
            type_rationale = "No visible typographic targets were found."
        elif hierarchy_failures:
            type_outcome, type_applicable = "failed", True
            type_rationale = f"Computed type hierarchy/body readability policy failed on {len(hierarchy_failures)} observations."
        else:
            type_outcome, type_applicable = "passed", True
            type_rationale = "Computed heading order, mobile body size and line-height checks passed on representative routes."

        if longform_count == 0:
            measure_outcome, measure_applicable = "inapplicable", False
            measure_rationale = "No long-form text blocks (>=160 characters) were present on representative routes."
        elif longform_failures:
            measure_outcome, measure_applicable = "failed", True
            measure_rationale = f"Long-form measure/clipping policy failed on {len(longform_failures)} observations."
        else:
            measure_outcome, measure_applicable = "passed", True
            measure_rationale = f"All {longform_count} long-form observations stayed within the configured maximum readable measure without clipping."

        report["policy"] = {
            "mobile_body_min_px": self.MOBILE_BODY_MIN_PX,
            "line_height_ratio": [1.25, 2.0],
            "max_longform_chars_per_line_approx": self.MAX_LONGFORM_CHARS_PER_LINE,
        }
        report["cases"] = cases
        report["requirements"]["VISUAL-006"] = self._result(
            type_outcome,
            applicable=type_applicable,
            rationale=type_rationale,
            test_targets=hierarchy_failures[:30],
            evidence_files=screenshots,
        )
        report["requirements"]["VISUAL-007"] = self._result(
            measure_outcome,
            applicable=measure_applicable,
            rationale=measure_rationale,
            test_targets=longform_failures[:30],
            evidence_files=screenshots,
        )
        return self._write_report("typography-metrics.json", report)

    @staticmethod
    def _motion_inventory_script() -> str:
        return r"""() => {
          const visible=el=>{const r=el.getBoundingClientRect(),s=getComputedStyle(el);return r.width>1&&r.height>1&&s.display!=='none'&&s.visibility!=='hidden'};
          const ms=value=>Math.max(0,...String(value||'').split(',').map(v=>{v=v.trim();return v.endsWith('ms')?parseFloat(v):v.endsWith('s')?parseFloat(v)*1000:0}).filter(Number.isFinite));
          const rows=[];
          for(const el of Array.from(document.querySelectorAll('body *')).filter(visible).slice(0,500)){
            const s=getComputedStyle(el),td=ms(s.transitionDuration),ad=ms(s.animationDuration),name=s.animationName;
            if(td>0||ad>0||(name&&name!=='none')) rows.push({tag:el.tagName.toLowerCase(),className:String(el.className||'').slice(0,120),transitionMs:td,animationMs:ad,animationName:name,timing:s.transitionTimingFunction});
          }
          let reducedRule=false;
          for(const sheet of Array.from(document.styleSheets)){
            try{for(const rule of Array.from(sheet.cssRules||[])){if(String(rule.conditionText||'').includes('prefers-reduced-motion')) reducedRule=true;}}catch(e){}
          }
          return {rows,reducedRule};
        }"""

    def _source_motion_markers(self) -> dict[str, bool]:
        text_parts: list[str] = []
        for pattern in ("*.css", "*.js", "*.jsx", "*.ts", "*.tsx"):
            for path in list(self.project_dir.rglob(pattern))[:120]:
                try:
                    text_parts.append(path.read_text(encoding="utf-8", errors="ignore")[:250_000])
                except OSError:
                    continue
        source = "\n".join(text_parts).casefold()
        return {
            "scroll_trigger": any(token in source for token in ("intersectionobserver", "data-reveal", "scroll-reveal", "scrollreveal", "reveal-on-scroll")),
            "custom_cursor": bool(re.search(r"cursor\s*:\s*none|custom[-_ ]cursor|cursor[-_ ]follower", source)),
            "parallax": "parallax" in source,
        }

    async def _run_motion_metrics(self, browser, base_url: str) -> Path:
        report = self._base_report("motion-accessibility")
        normal_cases: list[dict[str, Any]] = []
        reduced_cases: list[dict[str, Any]] = []
        repeated_failures: list[str] = []
        reduced_failures: list[str] = []
        material_motion = False
        reduced_rule_seen = False
        markers = self._source_motion_markers()

        for route in self.browser.routes:
            context, page = await self._open_local_page(browser, base_url, route, 1440, 1000)
            try:
                normal = await page.evaluate(self._motion_inventory_script())
                normal_cases.append({"route": route, **normal})
                reduced_rule_seen = reduced_rule_seen or bool(normal.get("reducedRule"))
                rows = normal.get("rows") or []
                material_motion = material_motion or bool(rows)
                if markers["scroll_trigger"]:
                    names: dict[str, int] = {}
                    for row in rows:
                        name = str(row.get("animationName", "none"))
                        if name and name != "none":
                            names[name] = names.get(name, 0) + 1
                    if names and max(names.values()) >= 4:
                        repeated_failures.append(f"{route}: repeated animation {max(names, key=names.get)!r} on {max(names.values())} visible elements")
            finally:
                await context.close()

            reduced_context = await browser.new_context(viewport={"width": 1440, "height": 1000}, reduced_motion="reduce", service_workers="block")
            reduced_page = await reduced_context.new_page()
            try:
                await reduced_page.goto(base_url.rstrip("/") + route, wait_until="networkidle", timeout=30000)
                reduced = await reduced_page.evaluate(self._motion_inventory_script())
                reduced_cases.append({"route": route, **reduced})
                normal_rows = (normal_cases[-1].get("rows") or [])
                reduced_rows = reduced.get("rows") or []
                normal_max = max([max(float(r.get("transitionMs", 0)), float(r.get("animationMs", 0))) for r in normal_rows] or [0])
                reduced_max = max([max(float(r.get("transitionMs", 0)), float(r.get("animationMs", 0))) for r in reduced_rows] or [0])
                if normal_max > 100 and not (reduced_max <= 100 or reduced_max <= normal_max * .5):
                    reduced_failures.append(f"{route}: normal={normal_max:.0f}ms reduced={reduced_max:.0f}ms")
            finally:
                await reduced_context.close()

        if not markers["scroll_trigger"]:
            motion4 = self._result("inapplicable", applicable=False, rationale="No broad scroll-trigger marker was detected in generated source.")
        elif repeated_failures:
            motion4 = self._result("failed", applicable=True, rationale="Broad scroll-trigger behavior reuses the same visible animation indiscriminately.", test_targets=repeated_failures[:20])
        else:
            motion4 = self._result("passed", applicable=True, rationale="Scroll-trigger behavior is present, but no repeated visible animation pattern crossed the V1 generic-motion threshold.")

        if not material_motion:
            motion6 = self._result("inapplicable", applicable=False, rationale="No material rendered motion was observed on representative routes.")
        elif reduced_failures:
            motion6 = self._result("failed", applicable=True, rationale="prefers-reduced-motion did not materially reduce observed motion on one or more routes.", test_targets=reduced_failures[:20])
        elif not reduced_rule_seen:
            motion6 = self._result("cantTell", applicable=True, rationale="Material motion exists and no author-declared prefers-reduced-motion media rule was observable; reduced rendering happened to be non-blocking but intent is unverified.")
        else:
            motion6 = self._result("passed", applicable=True, rationale="Material motion is present, an author-controlled prefers-reduced-motion rule exists, and reduced rendering materially suppresses or shortens motion where needed.")

        report["source_markers"] = markers
        report["normal"] = normal_cases
        report["reduced"] = reduced_cases
        report["requirements"]["INTERACTION-004"] = motion4
        report["requirements"]["INTERACTION-006"] = motion6
        return self._write_report("motion-accessibility-report.json", report)

    def _planned_journey(self) -> tuple[list[dict[str, str]], list[str]]:
        payload = self._json_file(self.run_dir / "implementation-plan.json")
        rows = [row for row in (payload.get("routes") or []) if isinstance(row, dict)]
        browser_routes = list(self.browser.routes)
        unresolved: list[str] = []

        def resolve(path: str) -> str | None:
            if path in browser_routes:
                return path
            if "[" in path:
                pattern = "^" + re.sub(r"\\\[[^]]+\\\]", "[^/]+", re.escape(path)) + "$"
                for route in browser_routes:
                    if re.match(pattern, route):
                        return route
            for route in browser_routes:
                if path != "/" and route.startswith(path.rstrip("/") + "/"):
                    return route
            return None

        ordered: list[dict[str, str]] = []
        role_groups = (
            ("home",),
            ("category", "collection", "search", "browse", "listing"),
            ("product", "detail"),
            ("cart",),
            ("checkout",),
        )
        used: set[str] = set()
        for keywords in role_groups:
            match = next((row for row in rows if id(row) not in used and any(key in str(row.get("page_role", "")).casefold() for key in keywords)), None)
            if not match:
                continue
            used.add(id(match))
            raw_path = str(match.get("path", "/"))
            actual = resolve(raw_path)
            if actual:
                ordered.append({"route": actual, "page_role": str(match.get("page_role", "unknown"))})
            else:
                unresolved.append(f"planned route unavailable: {raw_path} ({match.get('page_role','unknown')})")

        if len(ordered) < 2:
            ordered = []
            for row in rows:
                if str(row.get("priority", "P1")) != "P0":
                    continue
                actual = resolve(str(row.get("path", "/")))
                if actual and actual not in {item["route"] for item in ordered}:
                    ordered.append({"route": actual, "page_role": str(row.get("page_role", "unknown"))})
                if len(ordered) >= 3:
                    break
        return ordered, unresolved

    @staticmethod
    def _route_matches(href: str, target: str) -> bool:
        if not href:
            return False
        path = urlparse(href).path or "/"
        return path.rstrip("/") == target.rstrip("/") or (target != "/" and path.startswith(target.rstrip("/") + "/"))

    async def _click_toward(self, page, target: str, role: str) -> tuple[bool, str]:
        anchors = page.locator("a[href]")
        for index in range(min(await anchors.count(), 100)):
            anchor = anchors.nth(index)
            try:
                if not await anchor.is_visible():
                    continue
                href = (await anchor.get_attribute("href")) or ""
                if self._route_matches(href, target):
                    label = ((await anchor.inner_text()) or href).strip()[:100]
                    await anchor.click(timeout=2500)
                    await page.wait_for_load_state("networkidle", timeout=10000)
                    return self._route_matches(page.url, target), f"link:{label}"
            except Exception:
                continue

        role_key = role.casefold()
        patterns: list[str] = []
        if "cart" in role_key:
            patterns = ["add to cart", "thêm vào giỏ", "view cart", "giỏ hàng"]
        elif "checkout" in role_key:
            patterns = ["checkout", "thanh toán", "proceed", "continue to payment"]
        elif "contact" in role_key:
            patterns = ["contact", "liên hệ", "get in touch"]
        controls = page.locator("button,[role='button'],a")
        for phrase in patterns:
            for index in range(min(await controls.count(), 80)):
                control = controls.nth(index)
                try:
                    if not await control.is_visible():
                        continue
                    label = ((await control.inner_text()) or (await control.get_attribute("aria-label")) or "").strip()
                    if phrase not in label.casefold():
                        continue
                    await control.click(timeout=2500)
                    await page.wait_for_timeout(150)
                    if self._route_matches(page.url, target):
                        return True, f"control:{label[:100]}"
                    anchors2 = page.locator("a[href]")
                    for j in range(min(await anchors2.count(), 100)):
                        a = anchors2.nth(j)
                        href = (await a.get_attribute("href")) or ""
                        if await a.is_visible() and self._route_matches(href, target):
                            await a.click(timeout=2500)
                            await page.wait_for_load_state("networkidle", timeout=10000)
                            return self._route_matches(page.url, target), f"control+link:{label[:60]}"
                except Exception:
                    continue
        return False, "no safe UI transition found"

    def _custom_effect_markers(self) -> dict[str, bool]:
        return self._source_motion_markers()

    async def _run_journey(self, browser, base_url: str) -> Path:
        report = self._base_report("demo-path-journey")
        steps, unresolved = self._planned_journey()
        contract_path = self.run_dir / "demo-path-contract.json"
        contract = {"source": "implementation-plan.json", "steps": steps, "unresolved": unresolved}
        contract_path.write_text(json.dumps(contract, indent=2, ensure_ascii=False), encoding="utf-8")
        trace = self.evidence_dir / "journey" / "demo-path-trace.zip"
        trace.parent.mkdir(parents=True, exist_ok=True)
        screenshots: list[str] = []
        transitions: list[dict[str, Any]] = []

        if len(steps) < 2:
            result = self._result("cantTell", applicable=True, rationale="A machine-executable demo path with at least two resolved routes could not be derived from implementation-plan.json.", test_targets=unresolved, evidence_files=[str(contract_path)])
            report["requirements"]["CRITIQUE-006"] = result
            report["requirements"]["INTERACTION-007"] = self._result("inapplicable", applicable=False, rationale="Custom-effect justification is evaluated only when a custom cursor/parallax marker is present.")
            return self._write_report("journey-report.json", report)

        context, page = await self._open_local_page(browser, base_url, steps[0]["route"], 1440, 1000)
        await context.tracing.start(screenshots=True, snapshots=True, sources=False)
        failed: list[str] = []
        try:
            first = self.evidence_dir / "journey" / "step-00.png"
            await page.screenshot(path=str(first), full_page=True)
            screenshots.append(str(first))
            for index, target in enumerate(steps[1:], start=1):
                ok, action = await self._click_toward(page, target["route"], target["page_role"])
                transitions.append({"from": steps[index-1], "to": target, "action": action, "success": ok, "url": page.url})
                shot = self.evidence_dir / "journey" / f"step-{index:02d}.png"
                await page.screenshot(path=str(shot), full_page=True)
                screenshots.append(str(shot))
                if not ok:
                    failed.append(f"{steps[index-1]['route']} -> {target['route']}: {action}")
                    break
        finally:
            await context.tracing.stop(path=str(trace))
            await context.close()

        if failed:
            journey_outcome = "failed"
            journey_rationale = "The documented representative route sequence could not be completed through visible UI controls."
        elif unresolved:
            journey_outcome = "cantTell"
            journey_rationale = "The exercised steps completed, but part of the planned path could not be resolved to a rendered route."
        else:
            journey_outcome = "passed"
            journey_rationale = f"Playwright completed {len(steps)-1} UI-driven transition(s) across the representative demo path without direct navigation between steps."
        journey_result = self._result(
            journey_outcome,
            applicable=True,
            rationale=journey_rationale,
            test_targets=(failed + unresolved)[:20],
            evidence_files=[str(trace), str(contract_path), *screenshots],
        )
        report["contract"] = contract
        report["transitions"] = transitions
        report["requirements"]["CRITIQUE-006"] = journey_result

        markers = self._custom_effect_markers()
        effect_names = [name for name in ("custom_cursor", "parallax") if markers.get(name)]
        if not effect_names:
            effect_result = self._result("inapplicable", applicable=False, rationale="No custom cursor or parallax marker was detected in generated source.")
        else:
            art = self._text_file(self.run_dir / "art-direction.md").casefold()
            rationale_present = all(name.replace("_", " ") in art or name.replace("_", "-") in art for name in effect_names)
            state_payload = self._json_file(self.run_dir / "interaction-state-report.json")
            state_row = (state_payload.get("requirements") or {}).get("INTERACTION-002", {})
            control_ok = state_row.get("outcome") == "passed"
            if rationale_present and control_ok and journey_outcome == "passed":
                effect_result = self._result("passed", applicable=True, rationale="Custom effects are explicitly reflected in art direction and coexist with passing control-state and journey evidence.", evidence_files=[str(trace), str(self.run_dir / "art-direction.md")])
            elif not rationale_present:
                effect_result = self._result("failed", applicable=True, rationale="A custom cursor/parallax effect is present without an explicit art-direction rationale.", test_targets=effect_names, evidence_files=[str(trace)])
            else:
                effect_result = self._result("cantTell", applicable=True, rationale="Custom-effect rationale exists, but complete control/journey evidence is not strong enough to prove the effect preserves user control.", test_targets=effect_names, evidence_files=[str(trace)])
        report["requirements"]["INTERACTION-007"] = effect_result

        interaction_path = self.run_dir / "interaction-state-report.json"
        interaction_payload = self._json_file(interaction_path)
        if interaction_payload:
            interaction_payload.setdefault("requirements", {})["CRITIQUE-006"] = journey_result
            interaction_path.write_text(json.dumps(interaction_payload, indent=2, ensure_ascii=False), encoding="utf-8")
        return self._write_report("journey-report.json", report)

    def _style_adjectives(self) -> list[str]:
        text = self._text_file(self.run_dir / "art-direction.md")
        section = re.search(r"##\s*(?:Style Adjectives|Style Words)\s*\n(.*?)(?=\n##\s|\Z)", text, flags=re.I | re.S)
        values: list[str] = []
        if section:
            for line in section.group(1).splitlines():
                match = re.match(r"\s*(?:[-*]|\d+[.)])\s*(?:\*\*)?([^*\n—:]{2,50})", line)
                if match:
                    values.append(match.group(1).strip().strip("`*_ "))
        if not values:
            line = re.search(r"(?:style adjectives|style words)\s*:\s*([^\n]+)", text, flags=re.I)
            if line:
                values = [item.strip().strip("`*_ ") for item in re.split(r"[,;/]", line.group(1)) if item.strip()]
        return list(dict.fromkeys(value for value in values if value))

    async def _run_style_word_critic(self) -> Path:
        report = self._base_report("style-word-critic")
        adjectives = self._style_adjectives()
        screenshots = self._representative_screenshots()
        if len(adjectives) != 3:
            report["requirements"]["CRITIQUE-004"] = self._result("cantTell", applicable=True, rationale=f"Exactly three explicit style adjectives are required for a blind style-word comparison; found {len(adjectives)}.")
            report["adjectives"] = adjectives
            return self._write_report("style-word-review.json", report)
        if not screenshots:
            report["requirements"]["CRITIQUE-004"] = self._result("untested", applicable=None, rationale="No representative screenshots are available for style-word critique.")
            return self._write_report("style-word-review.json", report)
        images = [(f"route={route}", path) for route, path in list(screenshots.items())[:4]]
        observed: dict[str, Any] = {}
        try:
            provider = FreeVisionProvider.from_env(Path(__file__).resolve().parents[2])
            response = await provider.complete_vision(
                stage="visual_qa_style_words",
                system="Judge only visible evidence in the supplied rendered screenshots. Do not reward a style word because it appears in the prompt.",
                prompt=(
                    "For each of these exactly three intended style adjectives, judge whether typography, colour, media, spacing/composition and motion cues visible in the static evidence support it: "
                    + json.dumps(adjectives, ensure_ascii=False)
                    + ". Return JSON only: {\"adjectives\":[{\"word\":\"...\",\"score\":0,\"evidence\":[\"...\"]}],\"contradictions\":[\"...\"]}. Scores are 0-100."
                ),
                images=images,
            )
            observed = json.loads(self._clean_json(response))
        except (ProviderError, ValueError, json.JSONDecodeError) as exc:
            report["limitations"].append(f"Style-word vision proxy unavailable: {exc}")

        rows = observed.get("adjectives") if isinstance(observed, dict) else None
        valid = isinstance(rows, list) and len(rows) == 3 and all(isinstance(row, dict) and row.get("evidence") for row in rows)
        if not valid:
            result = self._result("cantTell", applicable=True, rationale="Style-word vision review did not return complete evidence for all three adjectives.", evidence_files=[str(path) for _, path in images])
        else:
            low = [str(row.get("word", "")) for row in rows if float(row.get("score", 0)) < 70]
            result = self._result("failed" if low else "passed", applicable=True, rationale=("One or more intended style adjectives lack sufficient visible support." if low else "All three style adjectives received screenshot-grounded evidence at or above the V1 support threshold."), test_targets=low, evidence_files=[str(path) for _, path in images])
        report["adjectives"] = adjectives
        report["observed"] = observed
        report["limitations"].append("This is screenshot-grounded model evidence, not an independent human aesthetic review.")
        report["requirements"]["CRITIQUE-004"] = result
        return self._write_report("style-word-review.json", report)

    def _reference_evidence(self) -> tuple[list[str], list[tuple[str, Path]]]:
        board = self._json_file(self.run_dir / "reference-dna.json")
        principles: list[str] = []
        images: list[tuple[str, Path]] = []
        for reference in (board.get("references") or [])[:6]:
            if not isinstance(reference, dict):
                continue
            url = str(reference.get("url", "reference"))
            principles.extend(str(value) for value in reference.get("patterns", []) if str(value).strip())
            for raw in reference.get("screenshots", [])[:2]:
                candidate = self.run_dir / str(raw)
                if candidate.is_file():
                    images.append((f"reference={url}", candidate))
        return list(dict.fromkeys(principles))[:30], images[:6]

    async def _run_reference_comparison(self) -> Path:
        report = self._base_report("reference-comparison")
        principles, reference_images = self._reference_evidence()
        current = self._representative_screenshots()
        if not principles and not reference_images:
            report["requirements"]["CRITIQUE-005"] = self._result("inapplicable", applicable=False, rationale="No observed production-reference DNA or screenshots are available for a competitive comparison.")
            return self._write_report("reference-comparison-review.json", report)
        if not current:
            report["requirements"]["CRITIQUE-005"] = self._result("untested", applicable=None, rationale="Reference evidence exists but current representative screenshots are unavailable.")
            return self._write_report("reference-comparison-review.json", report)
        current_images = [(f"CURRENT route={route}", path) for route, path in list(current.items())[:4]]
        images = current_images + reference_images
        observed: dict[str, Any] = {}
        try:
            provider = FreeVisionProvider.from_env(Path(__file__).resolve().parents[2])
            response = await provider.complete_vision(
                stage="visual_qa_reference_comparison",
                system="Compare current rendered website evidence against observed production-reference evidence without asking for imitation. Reward domain fit, task clarity, composition quality and project-specific distinctiveness; penalize generic template mimicry.",
                prompt=(
                    "Observed reference principles: " + json.dumps(principles, ensure_ascii=False) +
                    ". Return JSON only: {\"domain_fit\":0,\"task_clarity\":0,\"distinctiveness\":0,\"polish\":0,\"genericity\":0,\"evidence\":[\"...\"],\"reference_influence\":[\"...\"]}. Use only supplied screenshots/principles."
                ),
                images=images,
            )
            observed = json.loads(self._clean_json(response))
        except (ProviderError, ValueError, json.JSONDecodeError) as exc:
            report["limitations"].append(f"Reference-comparison vision proxy unavailable: {exc}")

        evidence = observed.get("evidence") if isinstance(observed, dict) else None
        if not isinstance(evidence, list) or not evidence:
            result = self._result("cantTell", applicable=True, rationale="Reference evidence exists, but comparison did not return screenshot/principle-grounded findings.", evidence_files=[str(path) for _, path in images])
        else:
            scores = [float(observed.get(key, 0)) for key in ("domain_fit", "task_clarity", "distinctiveness", "polish")]
            genericity = float(observed.get("genericity", 100))
            failed = min(scores) < 65 or genericity > 45
            result = self._result("failed" if failed else "passed", applicable=True, rationale=("Competitive comparison found weak domain/task/distinctiveness/polish evidence or excessive genericity." if failed else "Current output meets the V1 principle-grounded competitive distinctiveness threshold without requiring reference imitation."), evidence_files=[str(path) for _, path in images])
        report["reference_principles"] = principles
        report["observed"] = observed
        report["comparison_mode"] = "direct-reference-screenshots" if reference_images else "reference-principles-only"
        report["requirements"]["CRITIQUE-005"] = result
        return self._write_report("reference-comparison-review.json", report)

    async def _run_decoration_review(self) -> Path:
        report = self._base_report("decoration-review")
        screenshots = self._representative_screenshots()
        if not screenshots:
            report["requirements"]["CRITIQUE-003"] = self._result("untested", applicable=None, rationale="No screenshots are available for remove-one-decoration review.")
            return self._write_report("decoration-review.json", report)
        images = [(f"route={route}", path) for route, path in list(screenshots.items())[:4]]
        observed: dict[str, Any] = {}
        try:
            provider = FreeVisionProvider.from_env(Path(__file__).resolve().parents[2])
            response = await provider.complete_vision(
                stage="visual_qa_decoration_review",
                system="Challenge unnecessary visual decoration in rendered web UI. Preserve elements that carry hierarchy, brand meaning, feedback, accessibility or task clarity.",
                prompt="Return JSON only: {\"decision\":\"remove|retain\",\"target\":\"visible element or pattern\",\"rationale\":\"...\",\"evidence\":[\"...\"]}. You must make one concrete remove-or-retain decision, not a generic suggestion.",
                images=images,
            )
            observed = json.loads(self._clean_json(response))
        except (ProviderError, ValueError, json.JSONDecodeError) as exc:
            report["limitations"].append(f"Decoration review unavailable: {exc}")
        valid = str(observed.get("decision", "")) in {"remove", "retain"} and bool(str(observed.get("target", "")).strip()) and bool(str(observed.get("rationale", "")).strip()) and bool(observed.get("evidence"))
        report["decision"] = observed
        report["requirements"]["CRITIQUE-003"] = self._result("passed" if valid else "cantTell", applicable=True, rationale=("A concrete screenshot-grounded remove/retain decision was recorded." if valid else "A concrete screenshot-grounded remove/retain decision could not be established."), evidence_files=[str(path) for _, path in images])
        return self._write_report("decoration-review.json", report)

    def _write_readiness(self, outputs: dict[str, str]) -> Path:
        registry = RequirementRegistry()
        built_in = {"semantic_visual", "browser_target_smoke", "browser_contrast_smoke", "browser_viewports", "reference_plan", "artifact_claim", "human_review"}
        dedicated = set(EvidenceContractEvaluator.DEDICATED_REPORTS)
        requested = sorted({str(rule.evaluator or "") for rule in registry.rules if rule.evaluator})
        missing = sorted(set(requested) - built_in - dedicated)
        payload = {
            "schema_version": 1,
            "registry_version": registry.version,
            "machine_requirement_count": sum(1 for rule in registry.rules if rule.machine_gate),
            "requested_evaluators": requested,
            "built_in_evaluators": sorted(built_in),
            "dedicated_evaluators": sorted(dedicated),
            "missing_evaluator_implementations": missing,
            "outputs": outputs,
            "v1_evaluator_coverage_complete": not missing,
            "note": "Coverage-complete means every registry evaluator has an implementation path. A concrete website may still truthfully fail or return cantTell when evidence is insufficient.",
        }
        return self._write_report("v1-verification-readiness.json", payload)

    async def run(self) -> dict[str, str]:
        outputs = await super().run()
        design_system = await self._run_design_system_metrics()
        outputs["design_system_metrics"] = str(design_system)

        try:
            from playwright.async_api import async_playwright
        except ImportError as exc:
            raise RuntimeError("Final V1 evaluators require Python Playwright.") from exc

        with StaticServer(self.project_dir) as server:
            base_url = f"http://127.0.0.1:{server.port}"
            async with async_playwright() as playwright:
                browser = await playwright.chromium.launch(headless=True)
                try:
                    outputs["typography_metrics"] = str(await self._run_typography_metrics(browser, base_url))
                    outputs["motion_metrics"] = str(await self._run_motion_metrics(browser, base_url))
                    outputs["journey"] = str(await self._run_journey(browser, base_url))
                finally:
                    await browser.close()

        outputs["decoration_review"] = str(await self._run_decoration_review())
        outputs["style_word_review"] = str(await self._run_style_word_critic())
        outputs["reference_comparison"] = str(await self._run_reference_comparison())
        readiness = self._write_readiness(outputs)
        outputs["v1_readiness"] = str(readiness)
        return outputs
