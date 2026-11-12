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

CDP_PORT = 9238
USER_DATA_DIR = tempfile.mkdtemp(prefix="browser_cdp_bp_")
ARTIFACT_DIR = r"C:\Users\DELL\.gemini\antigravity\brain\35ff5483-d119-45be-a407-00f491b2c1fa"

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
        val = res.get("result", {}).get("value")
        return val

    async def capture_screenshot(self, filepath):
        res = await self.send("Page.captureScreenshot", {"format": "png"})
        import base64
        data = base64.b64decode(res.get("data", ""))
        with open(filepath, "wb") as f:
            f.write(data)
        print(f"Screenshot saved: {os.path.basename(filepath)} ({len(data)} bytes)", flush=True)

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
        "--no-default-browser-check",
        "--window-size=1440,960",
        "about:blank"
    ])

    targets = None
    for attempt in range(12):
        time.sleep(1)
        try:
            req = urllib.request.urlopen(f"http://127.0.0.1:{CDP_PORT}/json", timeout=2)
            targets = json.loads(req.read().decode())
            if targets and len(targets) > 0:
                print(f"Connected to CDP endpoint after {attempt + 1}s", flush=True)
                break
        except Exception:
            pass

    try:
        pages = [t for t in targets if t.get("type") == "page"]
        target = pages[0] if pages else targets[0]
        ws_url = target["webSocketDebuggerUrl"]

        client = CDPClient(ws_url)
        await client.connect()

        await client.send("Page.enable")
        await client.send("DOM.enable")
        await client.send("Runtime.enable")

        test_project_id = "d0e134d1-b801-455a-b71a-82c30ec0b0d1"

        import base64
        jwt_header = base64.urlsafe_b64encode(json.dumps({"alg":"HS256","typ":"JWT"}).encode()).decode().rstrip("=")
        jwt_payload = base64.urlsafe_b64encode(json.dumps({
            "sub": "c1a4118e-e650-4eb4-9164-47c1f2d24a6d",
            "aud": "authenticated",
            "role": "authenticated",
            "email": "user@example.com",
            "exp": int(time.time()) + 86400 * 365
        }).encode()).decode().rstrip("=")
        jwt_sig = base64.urlsafe_b64encode(b"mock_signature_bytes_1234567890").decode().rstrip("=")
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
            "id": test_project_id,
            "user_id": "c1a4118e-e650-4eb4-9164-47c1f2d24a6d",
            "name": "The Glass & Terracotta Villa",
            "plot_width": 50,
            "plot_length": 80,
            "facing": "South",
            "floors": 2,
            "design_style": "Modern Contemporary"
        }

        # Clear floorplan cache intentionally to test the empty-state recovery!
        setup_js = f"""
        localStorage.setItem('app_auth_session', JSON.stringify({json.dumps(mock_auth)}));
        localStorage.setItem('sb-xhyckokbgyqkmvxqfghp-auth-token', JSON.stringify({json.dumps(mock_auth)}));
        localStorage.setItem('project_{test_project_id}', JSON.stringify({json.dumps(mock_project)}));
        localStorage.removeItem('floorplan_{test_project_id}');
        """

        print("Seeding credentials (with clean floorplan cache to test recovery)...", flush=True)
        await client.send("Page.navigate", {"url": "http://localhost:5173/"})
        time.sleep(1.5)
        await client.eval_js(setup_js)

        url = f"http://localhost:5173/projects/{test_project_id}/exterior"
        print(f"Navigating to {url}...", flush=True)
        await client.send("Page.navigate", {"url": url})

        for _ in range(15):
            time.sleep(1)
            ready = await client.eval_js("document.readyState === 'complete'")
            if ready:
                break
        time.sleep(2)

        # Select exterior design
        print("Selecting exterior design...", flush=True)
        await client.eval_js("""
            (() => {
                const card = document.querySelector('.ext-design-card');
                if (card) card.click();
            })()
        """)
        time.sleep(1)

        # Advance to stage 2 via modal or directly
        print("Advancing to Step 2...", flush=True)
        await client.eval_js("""
            (() => {
                const modalBtn = document.querySelector('.step1-modal-footer .btn-primary');
                if (modalBtn) {
                    modalBtn.click();
                } else {
                    const step2Btn = document.querySelectorAll('.stage-step-btn')[1];
                    if (step2Btn) step2Btn.click();
                }
            })()
        """)
        time.sleep(1.5)

        # Advance to stage 3 (Plan & 3D Review)
        print("Advancing to Step 3 (Plan & 3D Review)...", flush=True)
        await client.eval_js("""
            (() => {
                const step3Btn = document.querySelectorAll('.stage-step-btn')[2];
                if (step3Btn) {
                    step3Btn.click();
                } else {
                    const contBtn = Array.from(document.querySelectorAll('button')).find(b => b.innerText.includes('Continue to Plan'));
                    if (contBtn) contBtn.click();
                }
            })()
        """)
        time.sleep(2)

        stage_info = await client.eval_js("""
            (() => {
                const activeBtn = document.querySelector('.stage-step-btn.active');
                return {
                    activeStepText: activeBtn ? activeBtn.innerText : 'none',
                    hasStage3Layout: !!document.querySelector('.stage3-dedicated-layout'),
                    allButtons: Array.from(document.querySelectorAll('button')).map(b => b.innerText.trim()).filter(Boolean)
                };
            })()
        """)
        print(f"Current stage diagnostics: {json.dumps(stage_info, indent=2)}", flush=True)

        # Click "View Floor Plan & CAD Blueprint"
        print("Clicking 'View Floor Plan & CAD Blueprint'...", flush=True)
        click_res = await client.eval_js("""
            (() => {
                const btn = Array.from(document.querySelectorAll('button')).find(b => b.innerText.includes('View Floor Plan & CAD Blueprint'));
                if (btn) {
                    btn.click();
                    return { clicked: true, text: btn.innerText };
                }
                return { clicked: false };
            })()
        """)
        print(f"Blueprint toggle click: {json.dumps(click_res)}", flush=True)
        time.sleep(2)

        # Inspect Blueprint Viewer DOM state
        print("Inspecting Blueprint DOM state...", flush=True)
        bp_check = await client.eval_js("""
            (() => {
                const emptyState = document.querySelector('.fp-empty-state');
                const viewerContainer = document.querySelector('.fp-viewer-container');
                const svg = document.querySelector('.fp-svg-viewport svg');
                const toolbar = document.querySelector('.fp-toolbar');
                const floorTabs = Array.from(document.querySelectorAll('.fp-floor-tab')).map(t => t.innerText.trim());
                const infoBadges = Array.from(document.querySelectorAll('.fp-info-badge')).map(b => b.innerText.trim());
                const rectCount = svg ? svg.querySelectorAll('rect').length : 0;
                const textCount = svg ? svg.querySelectorAll('text').length : 0;
                const lineCount = svg ? svg.querySelectorAll('line').length : 0;

                return {
                    hasEmptyState: !!emptyState,
                    hasViewerContainer: !!viewerContainer,
                    hasSvg: !!svg,
                    hasToolbar: !!toolbar,
                    floorTabs,
                    infoBadges,
                    svgStats: {
                        rects: rectCount,
                        texts: textCount,
                        lines: lineCount
                    }
                };
            })()
        """)

        print(f"Blueprint Check Result:\n{json.dumps(bp_check, indent=2)}", flush=True)

        # Assertions
        assert bp_check["hasEmptyState"] is False, "CRITICAL: Empty state placeholder ('READY TO GENERATE') must NOT appear!"
        assert bp_check["hasViewerContainer"] is True, "CRITICAL: FloorPlanViewer container must be mounted!"
        assert bp_check["hasSvg"] is True, "CRITICAL: SVG Blueprint must be rendered!"
        assert bp_check["svgStats"]["rects"] > 10, f"Expected >10 SVG rects (rooms/fixtures), found {bp_check['svgStats']['rects']}"
        assert bp_check["svgStats"]["texts"] > 5, f"Expected >5 SVG room labels/dimensions, found {bp_check['svgStats']['texts']}"
        
        tab_names_lower = [t.lower() for t in bp_check["floorTabs"]]
        assert any("ground" in t for t in tab_names_lower), f"Ground Floor tab must be present in {bp_check['floorTabs']}"
        assert any("first" in t for t in tab_names_lower), f"First Floor tab must be present in {bp_check['floorTabs']}"

        print("Ground Floor Blueprint successfully validated!", flush=True)
        await client.eval_js("document.querySelector('.stage3-blueprint-container')?.scrollIntoView({ behavior: 'instant', block: 'center' });")
        time.sleep(1)
        shot_ground = os.path.join(ARTIFACT_DIR, "phase_6g3_step3_blueprint_ground.png")
        await client.capture_screenshot(shot_ground)

        # Switch to First Floor tab
        print("\nSwitching to First Floor...", flush=True)
        await client.eval_js("""
            (() => {
                const btn = Array.from(document.querySelectorAll('.fp-floor-tab')).find(t => t.innerText.toLowerCase().includes('first'));
                if (btn) btn.click();
            })()
        """)
        time.sleep(1)
        await client.eval_js("document.querySelector('.stage3-blueprint-container')?.scrollIntoView({ behavior: 'instant', block: 'center' });")
        shot_first = os.path.join(ARTIFACT_DIR, "phase_6g3_step3_blueprint_first_floor.png")
        await client.capture_screenshot(shot_first)

        # Switch to Side-by-Side Blueprint
        print("\nSwitching to Side-by-Side Blueprint...", flush=True)
        await client.eval_js("""
            (() => {
                const btn = Array.from(document.querySelectorAll('.fp-floor-tab')).find(t => t.innerText.toLowerCase().includes('side-by-side'));
                if (btn) btn.click();
            })()
        """)
        time.sleep(1)
        await client.eval_js("document.querySelector('.stage3-blueprint-container')?.scrollIntoView({ behavior: 'instant', block: 'center' });")
        shot_both = os.path.join(ARTIFACT_DIR, "phase_6g3_step3_blueprint_side_by_side.png")
        await client.capture_screenshot(shot_both)

        # Switch to Site Plan
        print("\nSwitching to Site Plan...", flush=True)
        await client.eval_js("""
            (() => {
                const btn = Array.from(document.querySelectorAll('.fp-floor-tab')).find(t => t.innerText.toLowerCase().includes('site'));
                if (btn) btn.click();
            })()
        """)
        time.sleep(1)
        await client.eval_js("document.querySelector('.stage3-blueprint-container')?.scrollIntoView({ behavior: 'instant', block: 'center' });")
        shot_site = os.path.join(ARTIFACT_DIR, "phase_6g3_step3_blueprint_site_plan.png")
        await client.capture_screenshot(shot_site)

        print("\nALL BLUEPRINT CAD INTEGRATION TESTS PASSED WITH 100% SUCCESS!", flush=True)
        await client.close()

    finally:
        proc.terminate()
        try:
            proc.wait(timeout=3)
        except Exception:
            proc.kill()

if __name__ == "__main__":
    asyncio.run(run())
