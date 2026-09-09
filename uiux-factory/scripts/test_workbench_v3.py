"""Browser integration against running Bolt (5173) and Factory bridge (8788)."""

import asyncio
import json
from pathlib import Path

from playwright.async_api import async_playwright


async def main():
    output = Path(__file__).resolve().parents[1] / "runs" / "v3-workbench-qa"
    output.mkdir(parents=True, exist_ok=True)
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch()
        try:
            page = await browser.new_page(viewport={"width": 1440, "height": 1000})
            errors = []
            page.on("pageerror", lambda error: errors.append(str(error)))
            await page.goto("http://127.0.0.1:5173/uiux", wait_until="domcontentloaded", timeout=120_000)
            await page.get_by_role("heading", name="Bạn mang ý tưởng.", exact=False).wait_for(timeout=120_000)
            assert await page.get_by_role("button", name="Chuẩn bị bản thiết kế", exact=True).is_disabled()
            await page.get_by_role("button", name="Studio sáng tạo", exact=False).click()
            assert "studio kiến trúc" in await page.get_by_label("Bạn muốn tạo website như thế nào?", exact=True).input_value()
            for width, height in [(1440, 1000), (390, 844)]:
                await page.set_viewport_size({"width": width, "height": height})
                await page.screenshot(path=str(output / f"welcome-{width}.png"), full_page=True)
                assert not await page.evaluate("document.documentElement.scrollWidth > innerWidth")
            await page.set_viewport_size({"width": 1440, "height": 1000})
            await page.get_by_label("Bạn muốn tạo website như thế nào?", exact=True).fill("Thiết kế website studio với dịch vụ, dự án và liên hệ")
            await page.get_by_role("button", name="Thương hiệu / hình ảnh", exact=False).click(timeout=120_000)
            await page.get_by_label("Tên thương hiệu", exact=True).fill("Sprint 1 Demo")
            await page.get_by_label("Brand guideline", exact=True).fill("Primary: #006D6A\nBody font: Arial\nHeading font: Georgia\nCard radius: 16px")
            await page.get_by_text("Import design system / CSS hiện có", exact=True).click()
            await page.get_by_label("Design system JSON", exact=True).fill("{")
            await page.get_by_role("button", name="Phân tích Brand DNA & Reference").click()
            await page.get_by_role("alert").wait_for()
            await page.get_by_label("Design system JSON", exact=True).fill('{"colors":{"primary":"#003B71"}}')
            await page.get_by_placeholder("Paste reference URL…").fill("https://example.com")
            await page.get_by_role("button", name="＋ Reference", exact=True).click()
            async with page.expect_response(lambda response: response.url.endswith("/intelligence") and response.request.method == "POST") as response_info:
                await page.get_by_role("button", name="Phân tích Brand DNA & Reference").click()
            response = await response_info.value
            if response.status != 202:
                raise AssertionError(await response.text())
            job = await response.json()
            print(f"Job {job['id']} accepted through Workbench", flush=True)
            for _ in range(120):
                status = await page.request.get(f"http://127.0.0.1:8788/jobs/{job['id']}")
                job = await status.json()
                if job["status"] in {"completed", "failed"}:
                    break
                await asyncio.sleep(2)
            if job["status"] != "completed":
                raise AssertionError(job)
            await page.get_by_role("link", name="Mở design-system.json").wait_for(timeout=15000)
            assert await page.locator(".dx-stagebar .is-done").count() == 2
            system_response = await page.request.get(f"http://127.0.0.1:8788/jobs/{job['id']}/artifacts/design-system.json")
            system = await system_response.json()
            assert system["foundations"]["colors"]["color.brand.primary"]["value"] == "#003B71"
            assert system["brand"]["name"] == "Sprint 1 Demo"
            assert system["brand"]["conflicts"]
            document_response = await page.request.get(f"http://127.0.0.1:8788/jobs/{job['id']}/artifacts/DESIGN.md")
            assert document_response.status == 200
            assert "#003B71" in await document_response.text()
            reference_response = await page.request.get(f"http://127.0.0.1:8788/jobs/{job['id']}/artifacts/reference-dna.json")
            reference = await reference_response.json()
            print("Reference status:", reference["references"][0]["status"], flush=True)
            shots = page.locator(".dx-reference-shots img")
            assert await shots.count() == 2, "Expected desktop and mobile reference screenshots"
            for shot in await shots.all():
                await shot.scroll_into_view_if_needed()
                await shot.evaluate("image => image.decode()")
                assert await shot.evaluate("image => image.naturalWidth > 0"), "Reference image was blocked or unavailable"
            measurements = []
            for width, height in [(1440, 1000), (900, 1000), (390, 844)]:
                await page.set_viewport_size({"width": width, "height": height})
                await page.screenshot(path=str(output / f"workbench-{width}.png"), full_page=True)
                overflow = await page.evaluate("document.documentElement.scrollWidth > innerWidth")
                measurements.append({"width": width, "horizontal_overflow": overflow})
                assert not overflow, f"Horizontal overflow at {width}px"
            await page.get_by_label("Tên thương hiệu", exact=True).fill("Changed context")
            await page.get_by_text("Context đã thay đổi.", exact=False).wait_for()
            await page.wait_for_function("JSON.parse(localStorage.getItem('uiux-factory-design-context-v3'))?.designContext.brand_name === 'Changed context'")
            await page.reload(wait_until="domcontentloaded")
            await page.get_by_label("Tên thương hiệu", exact=True).wait_for()
            assert await page.get_by_label("Tên thương hiệu", exact=True).input_value() == "Changed context"
            await page.get_by_label("Chế độ tạo giao diện", exact=True).select_option("ai")
            await page.wait_for_function("JSON.parse(localStorage.getItem('uiux-factory-design-context-v3'))?.engine === 'ai'")
            await page.reload(wait_until="domcontentloaded")
            assert await page.get_by_label("Chế độ tạo giao diện", exact=True).input_value() == "ai"
            # UI-only configured-provider fixture: verify AI routing and recoverable errors,
            # without sending a model request or claiming live inference.
            ready_page = await browser.new_page(viewport={"width": 1440, "height": 1000})
            ready_page.on("pageerror", lambda error: errors.append(str(error)))
            await ready_page.route("**/health", lambda route: route.fulfill(json={"status":"ok", "ai":{"configured":True,"providers":["groq"]}}, headers={"Access-Control-Allow-Origin":"http://127.0.0.1:5173"}))
            await ready_page.route("**/api/uiux-search?*", lambda route: route.fulfill(json={"results":[]}))
            sent = []
            async def unavailable_provider(route):
                if route.request.method == "OPTIONS":
                    await route.fulfill(status=204, headers={"Access-Control-Allow-Origin":"http://127.0.0.1:5173", "Access-Control-Allow-Headers":"content-type", "Access-Control-Allow-Methods":"POST"})
                    return
                sent.append(route.request.post_data_json)
                await route.fulfill(status=400, json={"error":"Provider fixture unavailable; brief retained"}, headers={"Access-Control-Allow-Origin":"http://127.0.0.1:5173"})
            await ready_page.route("**/run", unavailable_provider)
            await ready_page.goto("http://127.0.0.1:5173/uiux", wait_until="domcontentloaded")
            await ready_page.get_by_role("button", name="Bắt đầu thiết kế", exact=True).wait_for()
            await ready_page.get_by_label("Bạn muốn tạo website như thế nào?", exact=True).fill("Website studio sáng tạo")
            await ready_page.get_by_role("button", name="Bắt đầu thiết kế", exact=True).click()
            await ready_page.get_by_role("alert").wait_for(timeout=60000)
            assert sent and sent[0]["engine"] == "ai"
            assert "## SELECTED DESIGN DIRECTION" not in sent[0]["prompt"]
            assert await ready_page.get_by_label("Bạn muốn tạo website như thế nào?", exact=True).input_value() == "Website studio sáng tạo"
            await ready_page.close()
            assert not errors, errors
            (output / "result.json").write_text(json.dumps({"job": job["id"], "viewports": measurements,
                "reference_status": reference["references"][0]["status"], "reference_images_loaded": 2,
                "page_errors": errors}, indent=2), encoding="utf-8")
            print("PASS: Workbench input, validation, real bridge job, artifacts, stale context and responsive checks", flush=True)
        except Exception:
            await page.screenshot(path=str(output / "failure.png"), full_page=True)
            print("Page errors:", errors, flush=True)
            raise
        finally:
            await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
