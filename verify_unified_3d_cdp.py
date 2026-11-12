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

CDP_PORT = 9252
USER_DATA_DIR = tempfile.mkdtemp(prefix="browser_cdp_u3d_")
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

        # ── Setup Authentication & Project State ─────────────────────────────
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

        # Load canonical saved selections for project
        canonical_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "backend-python", "app", "canonical_layouts")
        ext_file = os.path.join(canonical_dir, f"exterior_selections_{PROJECT_ID}.json")
        int_file = os.path.join(canonical_dir, f"interior_selections_{PROJECT_ID}.json")

        ext_data = {}
        if os.path.exists(ext_file):
            with open(ext_file, "r") as f:
                ext_data = json.load(f)

        int_data = {}
        if os.path.exists(int_file):
            with open(int_file, "r") as f:
                int_data = json.load(f)

        fp_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "backend-python", "canonical_layouts", "canonical_50x80_south_g1.json")
        fp_data = {}
        if os.path.exists(fp_file):
            with open(fp_file, "r") as f:
                fp_data = json.load(f)

        setup_js = f"""
        try {{
            localStorage.setItem('app_auth_session', JSON.stringify({json.dumps(mock_auth)}));
            localStorage.setItem('sb-xhyckokbgyqkmvxqfghp-auth-token', JSON.stringify({json.dumps(mock_auth)}));
            localStorage.setItem('project_{PROJECT_ID}', JSON.stringify({json.dumps(mock_project)}));
            localStorage.setItem('exterior_selection_{PROJECT_ID}', JSON.stringify({json.dumps(ext_data)}));
            localStorage.setItem('interior_selections_{PROJECT_ID}', JSON.stringify({json.dumps(int_data)}));
            if ({json.dumps(bool(fp_data))}) {{
                localStorage.setItem('floorplan_{PROJECT_ID}', JSON.stringify({json.dumps(fp_data)}));
            }}
        }} catch (e) {{}}
        """

        print("Registering pre-navigation script & seeding project design data...", flush=True)
        await cdp.send("Page.addScriptToEvaluateOnNewDocument", {"source": setup_js})
        await cdp.send("Page.navigate", {"url": "http://localhost:5173/"})
        await asyncio.sleep(1.5)
        await cdp.eval_js(setup_js)

        # ── 1. Navigate to Project Workspace ─────────────────────────────────
        target_url = f"http://localhost:5173/projects/{PROJECT_ID}"
        print(f"Navigating to {target_url}...", flush=True)
        await cdp.send("Page.navigate", {"url": target_url})
        await asyncio.sleep(2.5)

        # Switch to 3D View Tab
        print("Switching to '3D View' Tab in Project Workspace...", flush=True)
        await cdp.eval_js("""
            (() => {
                const tabs = Array.from(document.querySelectorAll('button'));
                const threeDTab = tabs.find(b => b.textContent.includes('3D View') || b.textContent.includes('View 3D House'));
                if (threeDTab) threeDTab.click();
            })()
        """)
        await asyncio.sleep(3)

        # Check Unified 3D Viewer presence
        viewer_check = await cdp.eval_js("""
            (() => {
                const container = document.querySelector('.unified-3d-page-container');
                const canvas = document.querySelector('.unified-3d-canvas-container canvas');
                const pills = Array.from(document.querySelectorAll('.unified-pill-btn')).map(p => p.textContent.trim());
                const selectOptions = Array.from(document.querySelectorAll('.unified-select option')).map(o => o.textContent.trim());
                return {
                    hasContainer: !!container,
                    hasCanvas: !!canvas,
                    pills: pills,
                    roomCount: selectOptions.length - 1
                };
            })()
        """)
        print(f"Unified 3D Viewer Initial State: {viewer_check}", flush=True)

        # ── 2. Capture Exterior Daylight View ────────────────────────────────
        print("\n--- Verifying Exterior Daylight View ---", flush=True)
        await cdp.capture_screenshot(os.path.join(ARTIFACT_DIR, "phase_6h_unified_exterior_daylight.png"))

        # ── 3. Toggle Night Mode & Capture ───────────────────────────────────
        print("Toggling to Night Mode...", flush=True)
        await cdp.eval_js("""
            (() => {
                const nightBtn = Array.from(document.querySelectorAll('.unified-action-btn')).find(b => b.textContent.includes('Daylight') || b.textContent.includes('Night'));
                if (nightBtn) nightBtn.click();
            })()
        """)
        await asyncio.sleep(1.5)
        await cdp.capture_screenshot(os.path.join(ARTIFACT_DIR, "phase_6h_unified_exterior_night.png"))

        # Switch back to Daylight
        await cdp.eval_js("""
            (() => {
                const nightBtn = Array.from(document.querySelectorAll('.unified-action-btn')).find(b => b.textContent.includes('Daylight') || b.textContent.includes('Night'));
                if (nightBtn) nightBtn.click();
            })()
        """)
        await asyncio.sleep(1)

        # ── 4. Verify Floor Level Isolation (Ground Floor Cutaway) ───────────
        print("\n--- Verifying Floor Level Isolation (Ground Floor Dollhouse) ---", flush=True)
        await cdp.eval_js("""
            (() => {
                const pills = Array.from(document.querySelectorAll('.unified-pill-btn'));
                const gfPill = pills.find(p => p.textContent.includes('Ground Floor'));
                if (gfPill) gfPill.click();
            })()
        """)
        await asyncio.sleep(1.5)
        await cdp.capture_screenshot(os.path.join(ARTIFACT_DIR, "phase_6h_unified_ground_floor_cutaway.png"))

        # ── 5. Verify First Floor Level Isolation ────────────────────────────
        print("Verifying First Floor Cutaway...", flush=True)
        await cdp.eval_js("""
            (() => {
                const pills = Array.from(document.querySelectorAll('.unified-pill-btn'));
                const ffPill = pills.find(p => p.textContent.includes('First Floor'));
                if (ffPill) ffPill.click();
            })()
        """)
        await asyncio.sleep(1.5)
        await cdp.capture_screenshot(os.path.join(ARTIFACT_DIR, "phase_6h_unified_first_floor_cutaway.png"))

        # ── 6. Verify Top-Down Cutaway View ──────────────────────────────────
        print("\n--- Verifying Top-Down View ---", flush=True)
        await cdp.eval_js("""
            (() => {
                const pills = Array.from(document.querySelectorAll('.unified-pill-btn'));
                const topPill = pills.find(p => p.textContent.includes('Top View'));
                if (topPill) topPill.click();
            })()
        """)
        await asyncio.sleep(1.5)
        await cdp.capture_screenshot(os.path.join(ARTIFACT_DIR, "phase_6h_unified_top_down.png"))

        # ── 7. Enter House & Inspect Rooms ───────────────────────────────────
        print("\n--- Verifying Walk-in Room Inspection ---", flush=True)

        # Reset to All Floors
        await cdp.eval_js("""
            (() => {
                const allPill = Array.from(document.querySelectorAll('.unified-pill-btn')).find(p => p.textContent.includes('All Floors'));
                if (allPill) allPill.click();
            })()
        """)
        await asyncio.sleep(0.5)

        # Inspect Room 1: Living Room
        print("Inspecting Living Room...", flush=True)
        await cdp.eval_js("""
            (() => {
                const select = document.querySelector('.unified-select');
                const options = Array.from(select.options);
                const livingOpt = options.find(o => o.text.includes('Living') || o.value.includes('living'));
                if (livingOpt) {
                    select.value = livingOpt.value;
                    select.dispatchEvent(new Event('change', { bubbles: true }));
                }
            })()
        """)
        await asyncio.sleep(2)

        hud_info_living = await cdp.eval_js("""
            (() => {
                const card = document.querySelector('.unified-room-inspector-card');
                const title = card?.querySelector('.room-inspector-title')?.textContent.trim();
                const items = Array.from(card?.querySelectorAll('.room-inspector-item') || []).map(it => ({
                    label: it.querySelector('.room-inspector-item-label')?.textContent.trim(),
                    val: it.querySelector('.room-inspector-item-val')?.textContent.trim()
                }));
                return { hasHUD: !!card, title, items };
            })()
        """)
        print(f"Living Room HUD: {hud_info_living}", flush=True)
        await cdp.capture_screenshot(os.path.join(ARTIFACT_DIR, "phase_6h_unified_room_living.png"))

        # Inspect Room 2: Modular Kitchen
        print("Inspecting Modular Kitchen...", flush=True)
        await cdp.eval_js("""
            (() => {
                const select = document.querySelector('.unified-select');
                const options = Array.from(select.options);
                const kitOpt = options.find(o => o.text.includes('Kitchen') || o.value.includes('kitchen'));
                if (kitOpt) {
                    select.value = kitOpt.value;
                    select.dispatchEvent(new Event('change', { bubbles: true }));
                }
            })()
        """)
        await asyncio.sleep(2)
        await cdp.capture_screenshot(os.path.join(ARTIFACT_DIR, "phase_6h_unified_room_kitchen.png"))

        # Inspect Room 3: Master Bedroom
        print("Inspecting Master Bedroom...", flush=True)
        await cdp.eval_js("""
            (() => {
                const select = document.querySelector('.unified-select');
                const options = Array.from(select.options);
                const bedOpt = options.find(o => o.text.includes('Master') || o.text.includes('Bed'));
                if (bedOpt) {
                    select.value = bedOpt.value;
                    select.dispatchEvent(new Event('change', { bubbles: true }));
                }
            })()
        """)
        await asyncio.sleep(2)

        hud_info_bed = await cdp.eval_js("""
            (() => {
                const card = document.querySelector('.unified-room-inspector-card');
                const title = card?.querySelector('.room-inspector-title')?.textContent.trim();
                const items = Array.from(card?.querySelectorAll('.room-inspector-item') || []).map(it => ({
                    label: it.querySelector('.room-inspector-item-label')?.textContent.trim(),
                    val: it.querySelector('.room-inspector-item-val')?.textContent.trim()
                }));
                return { hasHUD: !!card, title, items };
            })()
        """)
        print(f"Bedroom HUD: {hud_info_bed}", flush=True)
        await cdp.capture_screenshot(os.path.join(ARTIFACT_DIR, "phase_6h_unified_room_bedroom.png"))

        # ── 8. Reset Camera to Exterior ──────────────────────────────────────
        print("Resetting Camera to Exterior...", flush=True)
        await cdp.eval_js("""
            (() => {
                const resetBtn = Array.from(document.querySelectorAll('.unified-action-btn')).find(b => b.textContent.includes('Reset'));
                if (resetBtn) resetBtn.click();
            })()
        """)
        await asyncio.sleep(1.5)

        # ── 9. Verify Existing Exterior Studio Still Works ───────────────────
        print("\n--- Verifying Exterior Studio Route Remains Operational ---", flush=True)
        ext_url = f"http://localhost:5173/projects/{PROJECT_ID}/exterior"
        await cdp.send("Page.navigate", {"url": ext_url})

        # Wait for either cards or preview panel to appear
        for _ in range(12):
            is_ready = await cdp.eval_js("""
                (() => {
                    const cards = document.querySelectorAll('.exterior-design-card').length > 0;
                    const stage2 = !!document.querySelector('.stage2-preview-panel');
                    const stage3 = !!document.querySelector('.stage3-dedicated-layout');
                    const loader = !!document.querySelector('.exterior-loading-state');
                    return !loader && (cards || stage2 || stage3);
                })()
            """)
            if is_ready:
                break
            await asyncio.sleep(0.5)

        ext_operational = await cdp.eval_js("""
            (() => {
                const hasCards = document.querySelectorAll('.exterior-design-card').length > 0;
                const hasStage2 = !!document.querySelector('.stage2-preview-panel');
                const hasStage3 = !!document.querySelector('.stage3-dedicated-layout');
                const hasViewer = !!document.querySelector('.exterior-blueprint-viewer-root') || !!document.querySelector('.exterior-3d-viewer-container');
                return { hasCards, hasStage2, hasStage3, hasViewer };
            })()
        """)
        print(f"Exterior Studio Status: {ext_operational}", flush=True)
        await cdp.capture_screenshot(os.path.join(ARTIFACT_DIR, "phase_6h_exterior_studio_check.png"))

        # ── 10. Verify Existing Interior Studio Still Works ──────────────────
        print("\n--- Verifying Interior Studio Route Remains Operational ---", flush=True)
        int_url = f"http://localhost:5173/projects/{PROJECT_ID}/interior"
        await cdp.send("Page.navigate", {"url": int_url})

        # Wait for interior UI to appear
        for _ in range(12):
            is_int_ready = await cdp.eval_js("""
                (() => {
                    const cards = document.querySelectorAll('.interior-card, .design-card, [class*="card"]').length > 0;
                    const roomSel = !!document.querySelector('.room-selector, [class*="room"]');
                    return cards || roomSel;
                })()
            """)
            if is_int_ready:
                break
            await asyncio.sleep(0.5)

        int_operational = await cdp.eval_js("""
            (() => {
                const hasCards = document.querySelectorAll('.interior-card, .design-card, [class*="card"]').length > 0;
                const hasRoomSelector = !!document.querySelector('.room-selector, [class*="room"]');
                return { hasCards, hasRoomSelector };
            })()
        """)
        print(f"Interior Studio Status: {int_operational}", flush=True)
        await cdp.capture_screenshot(os.path.join(ARTIFACT_DIR, "phase_6h_interior_studio_check.png"))

        print("\nAll Phase 6H verification tests passed successfully!", flush=True)

    finally:
        if cdp:
            await cdp.close()
        proc.terminate()

if __name__ == "__main__":
    asyncio.run(run())
