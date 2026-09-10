from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from core.verification.post_render_evaluators import (
    PostRenderEvaluatorSuite as BasePostRenderEvaluatorSuite,
)


class PostRenderEvaluatorSuite(BasePostRenderEvaluatorSuite):
    """WCAG-aware and pseudo-localization-aware upgrade of post-render QA.

    Preserves the v1 report filenames/contracts while adding keyboard focus
    semantics, Content-on-Hover-or-Focus checks, and pseudo-localization stress.
    These are automated evidence checks, not a WCAG conformance claim or a full
    localization certification.
    """

    EVALUATOR_VERSION = "1.1.0"
    MAX_KEYBOARD_STEPS = 48
    MAX_DISCLOSURE_TRIGGERS = 10

    DISCLOSURE_TRIGGER_SELECTOR = (
        "a[href],button,summary,[role='button'],[aria-describedby],"
        "[aria-controls],[data-tooltip],[data-popover],[data-hover]"
    )

    _OUTCOME_RANK = {
        "inapplicable": 0,
        "passed": 1,
        "untested": 2,
        "cantTell": 3,
        "failed": 4,
    }

    @classmethod
    def _combine_result_rows(
        cls,
        base: dict[str, Any],
        upgrade: dict[str, Any],
        *,
        label: str,
    ) -> dict[str, Any]:
        base_outcome = str(base.get("outcome", "untested"))
        upgrade_outcome = str(upgrade.get("outcome", "untested"))
        if base_outcome == "inapplicable" and upgrade_outcome != "inapplicable":
            chosen = upgrade_outcome
        elif upgrade_outcome == "inapplicable" and base_outcome != "inapplicable":
            chosen = base_outcome
        else:
            chosen = max(
                (base_outcome, upgrade_outcome),
                key=lambda value: cls._OUTCOME_RANK.get(value, 99),
            )
        applicable_values = [base.get("applicable"), upgrade.get("applicable")]
        applicable = (
            True
            if True in applicable_values
            else (False if applicable_values == [False, False] else None)
        )
        return cls._result(
            chosen,
            applicable=applicable,
            rationale=(
                f"{base.get('rationale', '').strip()} "
                f"{label}: {upgrade.get('rationale', '').strip()}"
            ).strip(),
            test_targets=list(
                dict.fromkeys(
                    [str(value) for value in base.get("test_targets", [])]
                    + [str(value) for value in upgrade.get("test_targets", [])]
                )
            ),
            evidence_files=list(
                dict.fromkeys(
                    [str(value) for value in base.get("evidence_files", [])]
                    + [str(value) for value in upgrade.get("evidence_files", [])]
                )
            ),
        )

    @staticmethod
    def _focus_setup_script() -> str:
        return r"""() => {
          const visible = el => {
            const r = el.getBoundingClientRect();
            const s = getComputedStyle(el);
            return r.width > 0 && r.height > 0 &&
              s.display !== 'none' && s.visibility !== 'hidden' &&
              !el.disabled && el.getAttribute('aria-disabled') !== 'true';
          };
          const nodes = Array.from(document.querySelectorAll(
            "a[href],button,input:not([type='hidden']),select,textarea,summary,[tabindex]:not([tabindex='-1']),[contenteditable='true']"
          )).filter(visible);
          window.__uiuxFocusBaseline = {};
          nodes.forEach((el, index) => {
            const id = `f-${index}`;
            el.setAttribute('data-uiux-focus-id', id);
            const s = getComputedStyle(el);
            window.__uiuxFocusBaseline[id] = {
              color:s.color, backgroundColor:s.backgroundColor,
              borderColor:s.borderColor, borderWidth:s.borderWidth,
              outlineStyle:s.outlineStyle, outlineColor:s.outlineColor,
              outlineWidth:s.outlineWidth, outlineOffset:s.outlineOffset,
              boxShadow:s.boxShadow, textDecoration:s.textDecorationLine
            };
          });
          document.body.setAttribute('tabindex', '-1');
          document.body.focus();
          return {count:nodes.length,ids:nodes.map(el => el.getAttribute('data-uiux-focus-id'))};
        }"""

    @staticmethod
    def _active_focus_info_script() -> str:
        return r"""() => {
          const el = document.activeElement;
          if (!el || !el.getAttribute) return null;
          const id = el.getAttribute('data-uiux-focus-id');
          if (!id) return null;
          const base = (window.__uiuxFocusBaseline || {})[id] || {};
          const s = getComputedStyle(el);
          const r = el.getBoundingClientRect();
          const inViewport = r.bottom > 0 && r.right > 0 && r.top < innerHeight && r.left < innerWidth;
          const points = [
            [r.left + r.width / 2, r.top + r.height / 2],
            [r.left + Math.min(3, r.width / 2), r.top + Math.min(3, r.height / 2)],
            [r.right - Math.min(3, r.width / 2), r.bottom - Math.min(3, r.height / 2)]
          ].filter(([x,y]) => x >= 0 && y >= 0 && x < innerWidth && y < innerHeight);
          const exposed = points.some(([x,y]) => {
            const top = document.elementFromPoint(x,y);
            return !!top && (top === el || el.contains(top) || top.contains(el));
          });
          const styleChanged = [
            'color','backgroundColor','borderColor','borderWidth','outlineStyle',
            'outlineColor','outlineWidth','outlineOffset','boxShadow','textDecorationLine'
          ].some(key => String(base[key] ?? '') !== String(s[key] ?? ''));
          const outlinePx = Number.parseFloat(s.outlineWidth) || 0;
          const visibleOutline = s.outlineStyle !== 'none' && outlinePx > 0;
          const focusVisible = el.matches(':focus-visible');
          const label = (
            el.getAttribute('aria-label') || el.innerText || el.getAttribute('name') ||
            el.getAttribute('href') || el.tagName
          ).trim().slice(0,120);
          return {
            id, label, tag:el.tagName.toLowerCase(), focusVisible,
            indicatorVisible:focusVisible && (visibleOutline || styleChanged),
            inViewport, notObscured:inViewport && exposed,
            outlineStyle:s.outlineStyle, outlineWidth:s.outlineWidth,
            outlineColor:s.outlineColor, boxShadow:s.boxShadow
          };
        }"""

    async def _keyboard_focus_semantics(self, page, route: str) -> dict[str, Any]:
        setup = await page.evaluate(self._focus_setup_script())
        expected_ids = set(str(value) for value in setup.get("ids", []))
        if not expected_ids:
            return {
                "outcome": "inapplicable",
                "applicable": False,
                "rationale": "No visible keyboard-focusable controls were found.",
                "test_targets": [],
                "evidence_files": [],
                "details": [],
                "unreached": [],
            }

        reached: set[str] = set()
        details: list[dict[str, Any]] = []
        failures: list[str] = []
        steps = min(self.MAX_KEYBOARD_STEPS, max(len(expected_ids) + 6, len(expected_ids) * 2))
        for _ in range(steps):
            await page.keyboard.press("Tab")
            info = await page.evaluate(self._active_focus_info_script())
            if not info:
                continue
            identifier = str(info["id"])
            if identifier in reached:
                if reached == expected_ids:
                    break
                continue
            reached.add(identifier)
            details.append(info)
            if not bool(info.get("focusVisible")):
                failures.append(f"{route}:{info.get('label','control')} focus-visible=false")
            elif not bool(info.get("indicatorVisible")):
                failures.append(f"{route}:{info.get('label','control')} no-visible-indicator")
            if not bool(info.get("notObscured")):
                failures.append(f"{route}:{info.get('label','control')} focus-obscured")
            if reached == expected_ids:
                break

        unreached = sorted(expected_ids - reached)
        if failures:
            outcome = "failed"
            rationale = (
                f"Keyboard focus semantics failed on {len(failures)} observations: "
                "focus must be visibly indicated and at least partially unobscured."
            )
        elif unreached:
            outcome = "cantTell"
            rationale = (
                f"{len(reached)} of {len(expected_ids)} focusable controls were reached by "
                f"bounded keyboard traversal; {len(unreached)} remained unresolved."
            )
        else:
            outcome = "passed"
            rationale = (
                f"All {len(reached)} visible focusable controls were keyboard-reached with "
                "a visible focus indicator and remained at least partially unobscured."
            )
        return {
            "outcome": outcome,
            "applicable": True,
            "rationale": rationale,
            "test_targets": failures + [f"{route}:{value}:unreached" for value in unreached],
            "evidence_files": [],
            "details": details,
            "unreached": unreached,
        }

    @staticmethod
    def _visible_snapshot_script() -> str:
        return r"""() => {
          const visible = el => {
            const r=el.getBoundingClientRect(), s=getComputedStyle(el);
            return r.width>1 && r.height>1 && s.display!=='none' &&
              s.visibility!=='hidden' && Number(s.opacity || '1') > 0.01;
          };
          let counter=0;
          const rows={};
          for (const el of document.body.querySelectorAll('*')) {
            if (!el.hasAttribute('data-uiux-node-id')) el.setAttribute('data-uiux-node-id', `n-${counter++}`);
            if (!visible(el)) continue;
            const r=el.getBoundingClientRect();
            const id=el.getAttribute('data-uiux-node-id');
            rows[id]={
              text:(el.innerText||el.getAttribute('aria-label')||'').trim().slice(0,180),
              role:el.getAttribute('role')||'', tag:el.tagName.toLowerCase(),
              x:r.x,y:r.y,width:r.width,height:r.height,position:getComputedStyle(el).position
            };
          }
          return rows;
        }"""

    @staticmethod
    def _disclosure_detail_script(node_id: str, before_ids: list[str]) -> str:
        encoded_id = json.dumps(node_id)
        encoded_before = json.dumps(before_ids)
        return f"""() => {{
          const id={encoded_id};
          const before=new Set({encoded_before});
          const el=document.querySelector(`[data-uiux-node-id="${{id}}"]`);
          if (!el) return null;
          const visible = node => {{
            const r=node.getBoundingClientRect(), s=getComputedStyle(node);
            return r.width>1 && r.height>1 && s.display!=='none' &&
              s.visibility!=='hidden' && Number(s.opacity||'1')>0.01;
          }};
          if (!visible(el)) return null;
          const r=el.getBoundingClientRect();
          let obscures=false;
          for (const otherId of before) {{
            const other=document.querySelector(`[data-uiux-node-id="${{otherId}}"]`);
            if (!other || other===el || other.contains(el) || el.contains(other) || !visible(other)) continue;
            const o=other.getBoundingClientRect();
            const w=Math.max(0,Math.min(r.right,o.right)-Math.max(r.left,o.left));
            const h=Math.max(0,Math.min(r.bottom,o.bottom)-Math.max(r.top,o.top));
            if (w*h > 64) {{ obscures=true; break; }}
          }}
          const close=Array.from(el.querySelectorAll('button,[role="button"]')).some(node => {{
            const label=(node.getAttribute('aria-label')||node.textContent||'').trim().toLowerCase();
            return /close|dismiss|đóng|×|✕|x/.test(label);
          }});
          return {{
            id,text:(el.innerText||'').trim().slice(0,180),role:el.getAttribute('role')||'',
            obscures,explicitClose:close,x:r.x,y:r.y,width:r.width,height:r.height
          }};
        }}"""

    async def _test_disclosures(self, page, route: str, base_url: str) -> dict[str, Any]:
        trigger_count = min(
            await page.locator(self.DISCLOSURE_TRIGGER_SELECTOR).count(),
            self.MAX_DISCLOSURE_TRIGGERS,
        )
        disclosures: list[dict[str, Any]] = []
        failures: list[str] = []
        evidence_files: list[str] = []

        for index in range(trigger_count):
            if index:
                await page.goto(base_url.rstrip("/") + route, wait_until="networkidle", timeout=30000)
            triggers = page.locator(self.DISCLOSURE_TRIGGER_SELECTOR)
            if index >= await triggers.count():
                break
            trigger = triggers.nth(index)
            if not await trigger.is_visible():
                continue
            label = (
                (await trigger.get_attribute("aria-label"))
                or (await trigger.inner_text())
                or (await trigger.get_attribute("href"))
                or f"trigger-{index}"
            ).strip()[:100]
            before = await page.evaluate(self._visible_snapshot_script())
            try:
                await trigger.hover(timeout=1800)
            except Exception:
                continue
            await page.wait_for_timeout(120)
            after = await page.evaluate(self._visible_snapshot_script())
            new_ids = [
                node_id
                for node_id, row in after.items()
                if node_id not in before
                and (str(row.get("text", "")).strip() or str(row.get("role", "")) in {"tooltip", "dialog", "menu", "listbox"})
            ]
            for node_id in new_ids[:4]:
                detail = await page.evaluate(self._disclosure_detail_script(node_id, list(before.keys())))
                if not detail:
                    continue
                await page.wait_for_timeout(350)
                persistent = await page.locator(f'[data-uiux-node-id="{node_id}"]').is_visible()
                hoverable = False
                if persistent:
                    box = await page.locator(f'[data-uiux-node-id="{node_id}"]').bounding_box()
                    if box:
                        await page.mouse.move(box["x"] + box["width"] / 2, box["y"] + box["height"] / 2)
                        await page.wait_for_timeout(120)
                        hoverable = await page.locator(f'[data-uiux-node-id="{node_id}"]').is_visible()
                dismissible = not bool(detail.get("obscures"))
                escape_dismissed = False
                if not dismissible:
                    await page.keyboard.press("Escape")
                    await page.wait_for_timeout(100)
                    escape_dismissed = not await page.locator(f'[data-uiux-node-id="{node_id}"]').is_visible()
                    dismissible = escape_dismissed or bool(detail.get("explicitClose"))
                row = {
                    "route": route,
                    "trigger": label,
                    "content": detail.get("text", ""),
                    "persistent": persistent,
                    "hoverable": hoverable,
                    "dismissible": dismissible,
                    "obscures": bool(detail.get("obscures")),
                    "escape_dismissed": escape_dismissed,
                    "explicit_close": bool(detail.get("explicitClose")),
                }
                disclosures.append(row)
                if not (persistent and hoverable and dismissible):
                    failures.append(
                        f"{route}:{label}:persistent={persistent},hoverable={hoverable},dismissible={dismissible}"
                    )
                    shot = self.evidence_dir / "wcag-interaction" / f"{self._safe_route(route)}-hover-{index}.png"
                    shot.parent.mkdir(parents=True, exist_ok=True)
                    await page.screenshot(path=str(shot), full_page=True)
                    evidence_files.append(str(shot))
                break

        focus_triggers = page.locator("[aria-describedby],[aria-controls],[data-tooltip],[data-popover]")
        for index in range(min(await focus_triggers.count(), self.MAX_DISCLOSURE_TRIGGERS)):
            if index:
                await page.goto(base_url.rstrip("/") + route, wait_until="networkidle", timeout=30000)
                focus_triggers = page.locator("[aria-describedby],[aria-controls],[data-tooltip],[data-popover]")
            trigger = focus_triggers.nth(index)
            if not await trigger.is_visible():
                continue
            label = ((await trigger.get_attribute("aria-label")) or (await trigger.inner_text()) or f"focus-trigger-{index}").strip()[:100]
            before = await page.evaluate(self._visible_snapshot_script())
            try:
                await trigger.focus(timeout=1600)
            except Exception:
                continue
            await page.wait_for_timeout(120)
            after = await page.evaluate(self._visible_snapshot_script())
            new_ids = [
                node_id
                for node_id, row in after.items()
                if node_id not in before
                and (str(row.get("text", "")).strip() or str(row.get("role", "")) in {"tooltip", "dialog", "menu", "listbox"})
            ]
            for node_id in new_ids[:2]:
                detail = await page.evaluate(self._disclosure_detail_script(node_id, list(before.keys())))
                if not detail:
                    continue
                await page.wait_for_timeout(350)
                persistent = await page.locator(f'[data-uiux-node-id="{node_id}"]').is_visible()
                dismissible = not bool(detail.get("obscures"))
                escape_dismissed = False
                if not dismissible:
                    await page.keyboard.press("Escape")
                    await page.wait_for_timeout(100)
                    escape_dismissed = not await page.locator(f'[data-uiux-node-id="{node_id}"]').is_visible()
                    dismissible = escape_dismissed or bool(detail.get("explicitClose"))
                disclosures.append(
                    {
                        "route": route,
                        "trigger": label,
                        "content": detail.get("text", ""),
                        "focus_triggered": True,
                        "persistent": persistent,
                        "dismissible": dismissible,
                        "obscures": bool(detail.get("obscures")),
                        "escape_dismissed": escape_dismissed,
                    }
                )
                if not (persistent and dismissible):
                    failures.append(
                        f"{route}:{label}:focus-disclosure:persistent={persistent},dismissible={dismissible}"
                    )
                break

        if not disclosures:
            return {
                "outcome": "inapplicable",
                "applicable": False,
                "rationale": (
                    "No author-controlled additional content triggered by hover/focus was demonstrated; "
                    "native user-agent title tooltips are excluded."
                ),
                "test_targets": [],
                "evidence_files": evidence_files,
                "details": [],
            }
        if failures:
            return {
                "outcome": "failed",
                "applicable": True,
                "rationale": (
                    f"{len(failures)} hover/focus disclosure checks failed one or more "
                    "dismissible/hoverable/persistent semantics."
                ),
                "test_targets": failures,
                "evidence_files": evidence_files,
                "details": disclosures,
            }
        return {
            "outcome": "passed",
            "applicable": True,
            "rationale": (
                f"All {len(disclosures)} demonstrated author-controlled hover/focus disclosures "
                "satisfied the applicable dismissible/hoverable/persistent checks."
            ),
            "test_targets": [],
            "evidence_files": evidence_files,
            "details": disclosures,
        }

    async def _run_wcag_focus_hover(self, browser, base_url: str) -> dict[str, Any]:
        focus_rows: list[dict[str, Any]] = []
        disclosure_rows: list[dict[str, Any]] = []
        screenshots: list[str] = []
        for route in self.browser.routes:
            context, page = await self._open_local_page(browser, base_url, route, 1440, 1000)
            try:
                focus = await self._keyboard_focus_semantics(page, route)
                focus_rows.append({"route": route, **focus})
                shot = self.evidence_dir / "wcag-interaction" / f"{self._safe_route(route)}-keyboard-focus.png"
                shot.parent.mkdir(parents=True, exist_ok=True)
                await page.screenshot(path=str(shot), full_page=True)
                screenshots.append(str(shot))
                await page.goto(base_url.rstrip("/") + route, wait_until="networkidle", timeout=30000)
                disclosure = await self._test_disclosures(page, route, base_url)
                disclosure_rows.append({"route": route, **disclosure})
            finally:
                await context.close()

        def fold(rows: list[dict[str, Any]], *, empty_rationale: str) -> dict[str, Any]:
            applicable = [row for row in rows if row.get("applicable") is True]
            if not applicable:
                return self._result(
                    "inapplicable",
                    applicable=False,
                    rationale=empty_rationale,
                    evidence_files=screenshots,
                )
            if any(row.get("outcome") == "failed" for row in applicable):
                outcome = "failed"
            elif any(row.get("outcome") == "cantTell" for row in applicable):
                outcome = "cantTell"
            else:
                outcome = "passed"
            return self._result(
                outcome,
                applicable=True,
                rationale=" ".join(str(row.get("rationale", "")) for row in applicable),
                test_targets=[str(value) for row in applicable for value in row.get("test_targets", [])][:30],
                evidence_files=list(
                    dict.fromkeys(
                        screenshots
                        + [str(value) for row in applicable for value in row.get("evidence_files", [])]
                    )
                ),
            )

        return {
            "focus": fold(focus_rows, empty_rationale="No keyboard-focusable controls were found on representative routes."),
            "disclosures": fold(disclosure_rows, empty_rationale="No applicable author-controlled hover/focus disclosure was demonstrated."),
            "focus_routes": focus_rows,
            "disclosure_routes": disclosure_rows,
        }

    async def _run_interaction_state(self, browser, base_url: str) -> Path:
        path = await super()._run_interaction_state(browser, base_url)
        payload = json.loads(path.read_text(encoding="utf-8"))
        wcag = await self._run_wcag_focus_hover(browser, base_url)
        payload["evaluator_version"] = self.EVALUATOR_VERSION
        payload["wcag_focus_hover_semantics"] = {
            "focus_visible_and_not_obscured": wcag["focus_routes"],
            "content_on_hover_or_focus": wcag["disclosure_routes"],
            "standards_notes": [
                "WCAG 2.4.7 Focus Visible is approximated with keyboard traversal and rendered focus-style evidence.",
                "WCAG 2.4.11 Focus Not Obscured (Minimum) is approximated with viewport intersection plus hit-testing.",
                "WCAG 1.4.13 Content on Hover or Focus is tested for demonstrated author-controlled additional content.",
            ],
        }
        payload.setdefault("limitations", []).extend(
            [
                "Automated focus/hover checks are strong rendered evidence but are not a full WCAG conformance audit.",
                "Pure CSS/JS hover disclosures with no detectable visibility delta may remain undetected.",
            ]
        )
        requirements = payload.setdefault("requirements", {})
        for requirement_id in ("INTERACTION-002", "STATE-001"):
            existing = requirements.get(
                requirement_id,
                self._result("untested", applicable=None, rationale="Base interaction-state evidence was unavailable."),
            )
            combined = self._combine_result_rows(existing, wcag["focus"], label="WCAG keyboard focus semantics")
            combined = self._combine_result_rows(combined, wcag["disclosures"], label="WCAG content-on-hover-or-focus semantics")
            requirements[requirement_id] = combined
        path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
        return path

    @staticmethod
    def pseudo_localization_profiles() -> list[dict[str, Any]]:
        return [
            {"id": "expanded-accented-40", "direction": "ltr", "description": "Pseudo-accent text and expand visible strings by about 40%."},
            {"id": "vietnamese-heavy", "direction": "ltr", "description": "Long Vietnamese strings with diacritics, currency and place names."},
            {"id": "accented-density", "direction": "ltr", "description": "High diacritic density without aggressive expansion."},
            {"id": "rtl-bidi", "direction": "rtl", "description": "RTL/BIDI mixed-script text with numbers and punctuation."},
        ]

    @staticmethod
    def _pseudo_mutation_script() -> str:
        return r"""profile => {
          const visible = el => {
            const r=el.getBoundingClientRect(),s=getComputedStyle(el);
            return r.width>0&&r.height>0&&s.display!=='none'&&s.visibility!=='hidden';
          };
          const selector='h1,h2,h3,h4,p,li,button,label,a,span,td,th,summary,option';
          const nodes=Array.from(document.querySelectorAll(selector))
            .filter(el=>visible(el)&&el.children.length===0&&(el.textContent||'').trim().length>=2)
            .slice(0,24);
          const map={a:'á',b:'ƀ',c:'ç',d:'đ',e:'ë',f:'ƒ',g:'ğ',h:'ħ',i:'ï',j:'ĵ',k:'ķ',l:'ľ',m:'ɱ',n:'ñ',o:'ô',p:'þ',q:'ʠ',r:'ř',s:'š',t:'ŧ',u:'ü',v:'ṽ',w:'ŵ',x:'ẋ',y:'ÿ',z:'ž'};
          const accent = value => value.split('').map(ch=>{const low=ch.toLowerCase(),rep=map[low];if(!rep)return ch;return ch===low?rep:rep.toUpperCase();}).join('');
          const expand40 = value => {const target=Math.max(value.length+1,Math.ceil(value.length*1.4));let out=`⟦${accent(value)}⟧`;const pad=' ẋƥåñđ';while(out.length<target)out+=pad;return out.slice(0,target);};
          const vi=[
            'Bộ sưu tập nước hoa thủ công phiên bản giới hạn dành cho những khoảnh khắc đáng nhớ',
            'Nguyễn Thị Minh Anh — khách hàng thân thiết tại Thành phố Hồ Chí Minh',
            'Giao hàng tiêu chuẩn trong vòng ba đến năm ngày làm việc trên toàn quốc',
            '99.999.999.999 ₫ — giá tham khảo đã bao gồm thuế giá trị gia tăng',
            'Khám phá tầng hương hoa tím, gỗ đàn hương và xạ hương mềm mại kéo dài suốt cả ngày'
          ];
          const rtl=[
            'مرحبا بكم في تجربة التسوق — ١٢٣٬٤٥٦ ₫ — منتج جديد',
            'عطر فاخر محدود الإصدار — משלוח מהיר — 2026',
            'اكتشف المجموعة الجديدة עכשיו — السعر 99.999 ₫',
            'حساب المستخدم — כתובת למשלוח — رقم الطلب 12345'
          ];
          nodes.forEach((el,index)=>{
            const original=(el.textContent||'').trim();let value=original;
            if(profile==='expanded-accented-40')value=expand40(original);
            if(profile==='accented-density')value=`⟦${accent(original)}⟧`;
            if(profile==='vietnamese-heavy')value=vi[index%vi.length];
            if(profile==='rtl-bidi')value=rtl[index%rtl.length];
            el.textContent=value;el.setAttribute('data-uiux-stress-target','1');
          });
          if(profile==='rtl-bidi'){document.documentElement.setAttribute('dir','rtl');document.body.setAttribute('dir','rtl');}
          return {count:nodes.length,dir:document.documentElement.getAttribute('dir')||'ltr'};
        }"""

    @staticmethod
    def _stress_metrics_script() -> str:
        return r"""() => {
          const root=document.documentElement,body=document.body;
          const overflowX=Math.max(root.scrollWidth,body.scrollWidth)-root.clientWidth;
          const targets=Array.from(document.querySelectorAll('[data-uiux-stress-target="1"]'));
          const visible=el=>{const r=el.getBoundingClientRect(),s=getComputedStyle(el);return r.width>0&&r.height>0&&s.display!=='none'&&s.visibility!=='hidden';};
          const clipped=[];const offscreen=[];
          targets.filter(visible).forEach((el,index)=>{
            const r=el.getBoundingClientRect(),s=getComputedStyle(el);
            const hiddenX=['hidden','clip'].includes(s.overflowX)||['hidden','clip'].includes(s.overflow);
            const hiddenY=['hidden','clip'].includes(s.overflowY)||['hidden','clip'].includes(s.overflow);
            const clipX=el.scrollWidth>el.clientWidth+2&&hiddenX;
            const clipY=el.scrollHeight>el.clientHeight+2&&hiddenY;
            if(clipX||clipY)clipped.push({index,clipX,clipY,tag:el.tagName.toLowerCase()});
            if(r.right>innerWidth+2||r.left<-2)offscreen.push({index,left:r.left,right:r.right});
          });
          const controls=Array.from(document.querySelectorAll('button,a[href],input:not([type="hidden"]),select,textarea,[role="button"]')).filter(visible);
          const overlaps=[];
          for(let i=0;i<targets.length;i++){
            const a=targets[i];if(!visible(a))continue;const ar=a.getBoundingClientRect();
            for(let j=0;j<controls.length;j++){
              const b=controls[j];if(a===b||a.contains(b)||b.contains(a))continue;const br=b.getBoundingClientRect();
              const w=Math.max(0,Math.min(ar.right,br.right)-Math.max(ar.left,br.left));
              const h=Math.max(0,Math.min(ar.bottom,br.bottom)-Math.max(ar.top,br.top));
              if(w*h>24)overlaps.push({text:(a.textContent||'').trim().slice(0,80),control:(b.getAttribute('aria-label')||b.textContent||b.getAttribute('name')||b.tagName).trim().slice(0,80),area:w*h});
            }
          }
          return {overflowX,clipped,offscreen,overlaps,targetCount:targets.length,dir:document.documentElement.getAttribute('dir')||'ltr'};
        }"""

    async def _run_pseudo_localization_stress(self, browser, base_url: str) -> dict[str, Any]:
        profiles = self.pseudo_localization_profiles()
        viewports = (("mobile", 390, 844), ("tablet", 768, 1024), ("desktop", 1440, 1000))
        cases: list[dict[str, Any]] = []
        failures: list[str] = []
        unresolved: list[str] = []
        screenshots: list[str] = []
        total_targets = 0

        for route in self.browser.routes:
            for viewport_name, width, height in viewports:
                for profile in profiles:
                    context, page = await self._open_local_page(browser, base_url, route, width, height)
                    try:
                        baseline = await page.evaluate("() => Math.max(document.documentElement.scrollWidth,document.body.scrollWidth)-document.documentElement.clientWidth")
                        mutation = await page.evaluate(self._pseudo_mutation_script(), profile["id"])
                        total_targets += int(mutation.get("count", 0))
                        await page.evaluate("() => new Promise(r => requestAnimationFrame(() => requestAnimationFrame(r)))")
                        metrics = await page.evaluate(self._stress_metrics_script())
                        case_id = f"{route}@{viewport_name}:{profile['id']}"
                        failed = (
                            float(metrics.get("overflowX", 0)) > max(2.0, float(baseline) + 2.0)
                            or bool(metrics.get("clipped"))
                            or bool(metrics.get("offscreen"))
                            or bool(metrics.get("overlaps"))
                        )
                        if int(mutation.get("count", 0)) == 0:
                            unresolved.append(case_id)
                        elif failed:
                            failures.append(case_id)
                        shot = self.evidence_dir / "pseudo-localization" / f"{self._safe_route(route)}-{viewport_name}-{profile['id']}.png"
                        shot.parent.mkdir(parents=True, exist_ok=True)
                        await page.screenshot(path=str(shot), full_page=True)
                        screenshots.append(str(shot))
                        cases.append(
                            {
                                "route": route,
                                "viewport": viewport_name,
                                "profile": profile["id"],
                                "targets": int(mutation.get("count", 0)),
                                "baseline_overflow_x": baseline,
                                **metrics,
                                "failed": failed,
                                "screenshot": str(shot),
                            }
                        )
                    except Exception as exc:
                        case_id = f"{route}@{viewport_name}:{profile['id']}"
                        unresolved.append(case_id)
                        cases.append({"route": route, "viewport": viewport_name, "profile": profile["id"], "error": f"{type(exc).__name__}: {exc}", "failed": None})
                    finally:
                        await context.close()

        if total_targets == 0:
            outcome = "inapplicable"; applicable = False
            rationale = "No visible leaf text targets were available for pseudo-localization stress."
        elif failures:
            outcome = "failed"; applicable = True
            rationale = f"Pseudo-localization produced clipping/overflow/offscreen/overlap failures in {len(failures)} route/viewport/profile cases."
        elif unresolved:
            outcome = "cantTell"; applicable = True
            rationale = f"Pseudo-localization completed without demonstrated layout failure, but {len(unresolved)} cases could not be fully exercised."
        else:
            outcome = "passed"; applicable = True
            rationale = f"All {len(cases)} pseudo-localization cases passed across 40% expansion, accented text, Vietnamese-heavy content and RTL/BIDI stress profiles."

        return {
            "result": self._result(outcome, applicable=applicable, rationale=rationale, test_targets=(failures + unresolved)[:40], evidence_files=screenshots),
            "profiles": profiles,
            "cases": cases,
            "failures": failures,
            "unresolved": unresolved,
        }

    async def _run_content_stress(self, browser, base_url: str) -> Path:
        path = await super()._run_content_stress(browser, base_url)
        payload = json.loads(path.read_text(encoding="utf-8"))
        pseudo = await self._run_pseudo_localization_stress(browser, base_url)
        payload["evaluator_version"] = self.EVALUATOR_VERSION
        payload["pseudo_localization"] = {
            "profiles": pseudo["profiles"],
            "cases": pseudo["cases"],
            "method": "Disposable DOM mutation using expansion/accent/Vietnamese/RTL fixtures; generated source files are never modified.",
        }
        payload.setdefault("limitations", []).extend(
            [
                "Passing pseudo-localization stress is not proof that real translations are correct.",
                "RTL/BIDI stress is a rendered layout check, not linguistic review.",
                "Approximate 40% expansion follows common pseudolocalization practice for surfacing truncation risk.",
            ]
        )
        existing = payload.setdefault("requirements", {}).get(
            "RESPONSIVE-004",
            self._result("untested", applicable=None, rationale="Base content-stress evidence was unavailable."),
        )
        payload["requirements"]["RESPONSIVE-004"] = self._combine_result_rows(existing, pseudo["result"], label="Pseudo-localization stress")
        path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
        return path
