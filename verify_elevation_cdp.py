import asyncio
import json
import os
import subprocess
import tempfile
import time
import urllib.request
import websockets
import sys

sys.stdout.reconfigure(encoding='utf-8')

BROWSER_EXE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
if not os.path.exists(BROWSER_EXE):
    BROWSER_EXE = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

CDP_PORT = 9248
USER_DATA_DIR = tempfile.mkdtemp(prefix="browser_cdp_elev_")
ARTIFACT_DIR = r"C:\Users\DELL\.gemini\antigravity\brain\35ff5483-d119-45be-a407-00f491b2c1fa"
PROJECT_ID = "d0e134d1-b801-455a-b71a-82c30ec0b0d1"

class CDPClient:
    def __init__(self, ws_url):
        self.ws_url = ws_url
        self.ws = None
        self._id = 0

    async def connect(self):
        self.ws = await websockets.connect(self.ws_url, max_size=50_000_000)

    async def send(self, method, params=None):
        self._id += 1
        msg = {"id": self._id, "method": method, "params": params or {}}
        await self.ws.send(json.dumps(msg))
        while True:
            resp = json.loads(await self.ws.recv())
            if resp.get("id") == self._id:
                return resp.get("result", {})

    async def eval_js(self, expression):
        res = await self.send("Runtime.evaluate", {
            "expression": expression,
            "returnByValue": True,
            "awaitPromise": True
        })
        return res.get("result", {}).get("value")

    async def set_viewport(self, width, height):
        await self.send("Emulation.setDeviceMetricsOverride", {
            "width": width,
            "height": height,
            "deviceScaleFactor": 1,
            "mobile": False
        })
        await self.send("Emulation.setVisibleSize", {"width": width, "height": height})

    async def capture_screenshot(self, filepath):
        res = await self.send("Page.captureScreenshot", {"format": "png"})
        import base64
        data = base64.b64decode(res.get("data", ""))
        with open(filepath, "wb") as f:
            f.write(data)
        print(f"  [SAVED] {os.path.basename(filepath)} ({len(data)} bytes)", flush=True)

    async def close(self):
        if self.ws:
            await self.ws.close()

async def run():
    print(f"Launching browser on port {CDP_PORT}...", flush=True)
    proc = subprocess.Popen([
        BROWSER_EXE,
        "--headless=new",
        f"--remote-debugging-port={CDP_PORT}",
        f"--user-data-dir={USER_DATA_DIR}",
        "--disable-extensions",
        "--disable-default-apps",
        "--disable-gpu",
        "--no-first-run",
        "--no-default-browser-check"
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    cdp = None
    try:
        await asyncio.sleep(2)
        resp = urllib.request.urlopen(f"http://127.0.0.1:{CDP_PORT}/json").read()
        tabs = json.loads(resp)
        page_tab = next(t for t in tabs if t.get("type") == "page")
        ws_url = page_tab["webSocketDebuggerUrl"]

        cdp = CDPClient(ws_url)
        await cdp.connect()
        await cdp.send("Page.enable")
        await cdp.send("Runtime.enable")
        await cdp.set_viewport(1920, 1080)

        # ── Setup Authentication & Mock Project ──────────────────────────────
        import base64
        jwt_header = base64.urlsafe_b64encode(json.dumps({"alg":"HS256","typ":"JWT"}).encode()).decode().rstrip("=")
        jwt_payload = base64.urlsafe_b64encode(json.dumps({
            "sub": "c1a4118e-e650-4eb4-9164-47c1f2d24a6d",
            "aud": "authenticated",
            "role": "authenticated",
            "email": "user@example.com",
            "exp": int(time.time()) + 86400 * 365
        }).encode()).decode().rstrip("=")
        jwt_sig = base64.urlsafe_b64encode(b"mock_sig_12345").decode().rstrip("=")
        mock_jwt = f"{jwt_header}.{jwt_payload}.{jwt_sig}"

        mock_auth = {
            "access_token": mock_jwt,
            "token_type": "bearer",
            "expires_in": 3600 * 24 * 365,
            "expires_at": int(time.time()) + 86400 * 365,
            "refresh_token": "mock-refresh-token",
            "user": {
                "id": "c1a4118e-e650-4eb4-9164-47c1f2d24a6d",
                "aud": "authenticated",
                "role": "authenticated",
                "email": "user@example.com",
                "created_at": "2026-01-01T00:00:00.000Z",
                "app_metadata": {"provider": "email"},
                "user_metadata": {"full_name": "Lead Architect"}
            }
        }

        mock_project = {
            "id": PROJECT_ID,
            "user_id": "c1a4118e-e650-4eb4-9164-47c1f2d24a6d",
            "name": "The Glass & Terracotta Villa",
            "plot_width": 30,
            "plot_length": 50,
            "facing": "South",
            "floors": 2,
            "design_style": "Modern Contemporary",
            "budget": 4500000
        }

        setup_js = f"""
        localStorage.setItem('app_auth_session', JSON.stringify({json.dumps(mock_auth)}));
        localStorage.setItem('sb-xhyckokbgyqkmvxqfghp-auth-token', JSON.stringify({json.dumps(mock_auth)}));
        localStorage.setItem('project_{PROJECT_ID}', JSON.stringify({json.dumps(mock_project)}));
        """

        print("Navigating to home to seed auth credentials...", flush=True)
        await cdp.send("Page.navigate", {"url": "http://localhost:5173/"})
        await asyncio.sleep(1.5)
        await cdp.eval_js(setup_js)

        target_url = f"http://localhost:5173/projects/{PROJECT_ID}/exterior"
        print(f"Navigating to {target_url}...", flush=True)
        await cdp.send("Page.navigate", {"url": target_url})

        # Wait for exterior page to load
        for _ in range(12):
            await asyncio.sleep(1)
            loaded = await cdp.eval_js("""
                (() => {
                    const hasCards = document.querySelectorAll('.exterior-design-card').length > 0;
                    const hasStage2 = !!document.querySelector('.stage2-preview-panel');
                    const hasStage3 = !!document.querySelector('.stage3-dedicated-layout');
                    return hasCards || hasStage2 || hasStage3;
                })()
            """)
            if loaded:
                print("Exterior Studio page loaded successfully!", flush=True)
                break

        # Check current stage
        state = await cdp.eval_js("""
            (() => {
                const stepItems = Array.from(document.querySelectorAll('.wizard-step-item'));
                const activeStep = stepItems.findIndex(el => el.classList.contains('active')) + 1;
                const hasGallery = !!document.querySelector('.exterior-gallery-grid');
                const hasStage2 = !!document.querySelector('.stage2-preview-panel');
                const hasStage3 = !!document.querySelector('.stage3-dedicated-layout');
                const designCards = document.querySelectorAll('.exterior-design-card').length;
                return { activeStep, hasGallery, hasStage2, hasStage3, designCards };
            })()
        """)
        print(f"Current State: {state}", flush=True)

        # If on Stage 1, select a design and proceed to Stage 2
        if state.get("hasGallery") and not state.get("hasStage2"):
            print("Selecting design in Stage 1 and advancing to Stage 2...", flush=True)
            await cdp.eval_js("""
                (() => {
                    const cards = document.querySelectorAll('.exterior-design-card');
                    if (cards.length > 0) {
                        cards[0].click();
                    }
                })()
            """)
            await asyncio.sleep(1.5)

            # Click proceed button inside modal if open, or proceed button
            await cdp.eval_js("""
                (() => {
                    const btns = Array.from(document.querySelectorAll('button'));
                    const modalProceed = btns.find(b => 
                        b.textContent.includes('Proceed to Step 2') ||
                        b.textContent.includes('Customize Colors') ||
                        b.textContent.includes('Proceed with Selected')
                    );
                    if (modalProceed) modalProceed.click();
                })()
            """)
            await asyncio.sleep(2)

        # ── 2. Stage 2: Verify Visualization Switcher Workspace ──────────────
        print("\n--- Verifying Stage 2 Visualization Switcher Workspace ---", flush=True)
        s2_tabs = await cdp.eval_js("""
            (() => {
                const tabs = Array.from(document.querySelectorAll('.stage2-preview-panel .exterior-view-tab-btn'));
                return tabs.map(t => ({ text: t.textContent.trim(), active: t.classList.contains('is-active') }));
            })()
        """)
        print(f"Stage 2 Tabs: {s2_tabs}", flush=True)

        # Switch to 2D Architectural Elevation Tab
        print("Switching to 'Personalized 2D Architectural Elevation'...", flush=True)
        await cdp.eval_js("""
            (() => {
                const tabs = Array.from(document.querySelectorAll('.stage2-preview-panel .exterior-view-tab-btn'));
                const elevTab = tabs.find(t => t.textContent.includes('Elevation'));
                if (elevTab) elevTab.click();
            })()
        """)
        await asyncio.sleep(1.5)

        # Check elevation viewer elements
        elev_details = await cdp.eval_js("""
            (() => {
                const viewer = document.querySelector('.exterior-blueprint-viewer-root');
                const svg = document.querySelector('.elevation-svg-stage svg');
                const pills = Array.from(document.querySelectorAll('.elevation-pill-btn')).map(p => p.textContent.trim());
                const zoomTag = document.querySelector('.elevation-zoom-tag')?.textContent.trim();
                const titleBlock = svg ? svg.querySelector('text')?.textContent : null;
                const exportBtns = Array.from(document.querySelectorAll('.elevation-action-btn')).map(b => b.textContent.trim());
                return {
                    hasViewer: !!viewer,
                    hasSvg: !!svg,
                    viewBox: svg?.getAttribute('viewBox'),
                    pills: pills,
                    zoomTag: zoomTag,
                    exportBtns: exportBtns
                };
            })()
        """)
        print(f"Elevation Viewer in Stage 2: {elev_details}", flush=True)

        # Test Angle Switcher (3/4 Left, 3/4 Right, Front)
        print("Testing View Angle Pills...", flush=True)
        await cdp.eval_js("""
            (() => {
                const pills = Array.from(document.querySelectorAll('.elevation-pill-btn'));
                const leftPill = pills.find(p => p.textContent.includes('3/4 Left'));
                if (leftPill) leftPill.click();
            })()
        """)
        await asyncio.sleep(1)

        # Test Style Toggle (Color Elevation)
        print("Testing Style Toggle (Color Elevation)...", flush=True)
        await cdp.eval_js("""
            (() => {
                const pills = Array.from(document.querySelectorAll('.elevation-pill-btn'));
                const colorPill = pills.find(p => p.textContent.includes('Color Elevation'));
                if (colorPill) colorPill.click();
            })()
        """)
        await asyncio.sleep(1)

        # Test Zoom In and Reset
        print("Testing Zoom Controls...", flush=True)
        await cdp.eval_js("""
            (() => {
                const toolBtns = Array.from(document.querySelectorAll('.elevation-tool-btn'));
                if (toolBtns.length >= 2) {
                    toolBtns[0].click(); // Zoom Out
                    toolBtns[1].click(); // Zoom In
                    toolBtns[1].click(); // Zoom In
                }
            })()
        """)
        await asyncio.sleep(0.5)

        # Change a color swatch in Stage 2 to verify live elevation color update
        print("Selecting new primary wall color in customizer...", flush=True)
        await cdp.eval_js("""
            (() => {
                const rows = Array.from(document.querySelectorAll('.stage2-table-row'));
                if (rows.length > 0) rows[0].click();
                const swatches = Array.from(document.querySelectorAll('.palette-color-btn, .swatch-btn, .color-swatch-item'));
                if (swatches.length > 4) swatches[4].click();
            })()
        """)
        await asyncio.sleep(1)

        # Capture Stage 2 Elevation Mode Screenshot
        await cdp.capture_screenshot(os.path.join(ARTIFACT_DIR, "phase_6g5_stage2_elevation_mode.png"))

        # Switch to 3D House Preview in Stage 2
        print("Switching back to 'Personalized 3D Preview' in Stage 2...", flush=True)
        await cdp.eval_js("""
            (() => {
                const tabs = Array.from(document.querySelectorAll('.stage2-preview-panel .exterior-view-tab-btn'));
                const p3d = tabs.find(t => t.textContent.includes('3D Preview'));
                if (p3d) p3d.click();
            })()
        """)
        await asyncio.sleep(1.5)
        await cdp.capture_screenshot(os.path.join(ARTIFACT_DIR, "phase_6g5_stage2_3d_mode.png"))

        # Switch to Architectural Reference Image in Stage 2
        print("Switching to 'Architectural Reference Image' in Stage 2...", flush=True)
        await cdp.eval_js("""
            (() => {
                const tabs = Array.from(document.querySelectorAll('.stage2-preview-panel .exterior-view-tab-btn'));
                const refTab = tabs.find(t => t.textContent.includes('Reference'));
                if (refTab) refTab.click();
            })()
        """)
        await asyncio.sleep(1)
        await cdp.capture_screenshot(os.path.join(ARTIFACT_DIR, "phase_6g5_stage2_reference_mode.png"))

        # ── 3. Stage 3: Advance to Plan & 3D Review ──────────────────────────
        print("\n--- Advancing to Stage 3: Plan & 3D Review ---", flush=True)
        await cdp.eval_js("""
            (() => {
                const btns = Array.from(document.querySelectorAll('button'));
                const continueBtn = btns.find(b => b.textContent.includes('Continue to Plan & 3D Review'));
                if (continueBtn) continueBtn.click();
            })()
        """)
        await asyncio.sleep(2)

        s3_tabs = await cdp.eval_js("""
            (() => {
                const tabs = Array.from(document.querySelectorAll('.stage3-dedicated-layout .exterior-view-tab-btn'));
                return tabs.map(t => ({ text: t.textContent.trim(), active: t.classList.contains('is-active') }));
            })()
        """)
        print(f"Stage 3 Tabs: {s3_tabs}", flush=True)

        # Tab 1: 2D Architectural Elevation Blueprint Mode
        print("Checking Stage 3 Elevation View...", flush=True)
        await cdp.eval_js("""
            (() => {
                const tabs = Array.from(document.querySelectorAll('.stage3-dedicated-layout .exterior-view-tab-btn'));
                const elevTab = tabs.find(t => t.textContent.includes('Elevation'));
                if (elevTab) elevTab.click();
                const blueprintBtn = Array.from(document.querySelectorAll('.elevation-pill-btn')).find(p => p.textContent.includes('Blueprint'));
                if (blueprintBtn) blueprintBtn.click();
            })()
        """)
        await asyncio.sleep(1.5)
        await cdp.capture_screenshot(os.path.join(ARTIFACT_DIR, "phase_6g5_stage3_elevation_blueprint.png"))

        # Switch to Rendered Color Elevation in Stage 3
        print("Switching to Color Elevation in Stage 3...", flush=True)
        await cdp.eval_js("""
            (() => {
                const colorBtn = Array.from(document.querySelectorAll('.elevation-pill-btn')).find(p => p.textContent.includes('Color Elevation'));
                if (colorBtn) colorBtn.click();
            })()
        """)
        await asyncio.sleep(1.5)
        await cdp.capture_screenshot(os.path.join(ARTIFACT_DIR, "phase_6g5_stage3_elevation_rendered.png"))

        # Tab 4: Split Comparison View
        print("Switching to Split Comparison View...", flush=True)
        await cdp.eval_js("""
            (() => {
                const tabs = Array.from(document.querySelectorAll('.stage3-dedicated-layout .exterior-view-tab-btn'));
                const splitTab = tabs.find(t => t.textContent.includes('Split Comparison'));
                if (splitTab) splitTab.click();
            })()
        """)
        await asyncio.sleep(1.5)
        await cdp.capture_screenshot(os.path.join(ARTIFACT_DIR, "phase_6g5_stage3_split_view.png"))

        # Test expanding Interior Floor Plan & CAD Layout
        print("Expanding Interior Floor Plan & CAD Layout...", flush=True)
        await cdp.eval_js("""
            (() => {
                const btns = Array.from(document.querySelectorAll('button'));
                const fpBtn = btns.find(b => b.textContent.includes('View Interior Floor Plan'));
                if (fpBtn) fpBtn.click();
            })()
        """)
        await asyncio.sleep(2)
        await cdp.capture_screenshot(os.path.join(ARTIFACT_DIR, "phase_6g5_stage3_interior_floorplan.png"))

        # ── 4. Stage 4: Save & Apply Exterior Design ─────────────────────────
        print("\n--- Advancing to Stage 4: Save & Apply ---", flush=True)
        await cdp.eval_js("""
            (() => {
                const btns = Array.from(document.querySelectorAll('button'));
                const saveBtn = btns.find(b => b.textContent.includes('Save & Apply Exterior'));
                if (saveBtn) saveBtn.click();
            })()
        """)
        await asyncio.sleep(2)

        s4_info = await cdp.eval_js("""
            (() => {
                const card = document.querySelector('.stage4-summary-card');
                const title = card?.querySelector('h3')?.textContent.trim();
                const colorCount = card?.querySelectorAll('.summary-color-item')?.length || 0;
                return { hasCard: !!card, title, colorCount };
            })()
        """)
        print(f"Stage 4 Summary: {s4_info}", flush=True)
        await cdp.capture_screenshot(os.path.join(ARTIFACT_DIR, "phase_6g5_stage4_saved_exterior.png"))

        # Click "Save & Apply to Project"
        print("Clicking 'Save & Apply to Project'...", flush=True)
        await cdp.eval_js("""
            (() => {
                const btns = Array.from(document.querySelectorAll('button'));
                const applyBtn = btns.find(b => b.textContent.includes('Save & Apply to Project'));
                if (applyBtn) applyBtn.click();
            })()
        """)
        await asyncio.sleep(3)

        # ── 5. Project Overview Verification across Viewports ────────────────
        print("\n--- Navigating to Project Overview ---", flush=True)
        overview_url = f"http://localhost:5173/projects/{PROJECT_ID}"
        await cdp.send("Page.navigate", {"url": overview_url})
        await asyncio.sleep(3)

        # Check Exterior module status
        ext_module_status = await cdp.eval_js("""
            (() => {
                const cards = Array.from(document.querySelectorAll('.module-card, [class*="module"]'));
                const extCard = cards.find(c => c.textContent.includes('Exterior'));
                return {
                    text: extCard ? extCard.textContent.trim().replace(/\\s+/g, ' ') : "Not found"
                };
            })()
        """)
        print(f"Project Overview Exterior Status: {ext_module_status}", flush=True)

        # Capture Overview at 1920x1080
        await cdp.set_viewport(1920, 1080)
        await asyncio.sleep(0.5)
        await cdp.capture_screenshot(os.path.join(ARTIFACT_DIR, "phase_6g5_overview_1920.png"))

        # Capture Overview at 1600x900
        await cdp.set_viewport(1600, 900)
        await asyncio.sleep(0.5)
        await cdp.capture_screenshot(os.path.join(ARTIFACT_DIR, "phase_6g5_overview_1600.png"))

        # Capture Overview at 1366x768
        await cdp.set_viewport(1366, 768)
        await asyncio.sleep(0.5)
        await cdp.capture_screenshot(os.path.join(ARTIFACT_DIR, "phase_6g5_overview_1366.png"))

        print("\nAll Phase 6G.5 verification steps completed successfully!", flush=True)

    finally:
        if cdp:
            await cdp.close()
        proc.terminate()

if __name__ == "__main__":
    asyncio.run(run())
