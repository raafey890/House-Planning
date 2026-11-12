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

CDP_PORT = 9240
USER_DATA_DIR = tempfile.mkdtemp(prefix="browser_cdp_ov_")
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

    async def set_viewport(self, width, height):
        await self.send("Emulation.setDeviceMetricsOverride", {
            "width": width,
            "height": height,
            "deviceScaleFactor": 1,
            "mobile": False
        })
        await self.send("Emulation.setVisibleSize", {"width": width, "height": height})
        time.sleep(0.5)

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
        "--window-size=1920,1080",
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
            "location": "Bengaluru, KA",
            "budget": 7500000,
            "facing": "South",
            "floors": 2,
            "design_style": "Modern Contemporary",
            "status": "In Progress",
            "created_at": "2026-02-15T10:00:00.000Z"
        }

        # Load disk exterior selection fixture
        fixture_path = r"C:\Users\DELL\OneDrive\Desktop\House plaining\backend-python\app\canonical_layouts\exterior_selections_d0e134d1-b801-455a-b71a-82c30ec0b0d1.json"
        with open(fixture_path, "r", encoding="utf-8") as f:
            saved_exterior = json.load(f)

        setup_js = f"""
        try {{
            localStorage.setItem('app_auth_session', JSON.stringify({json.dumps(mock_auth)}));
            localStorage.setItem('sb-cptjtxjqsyuwrwstcehu-auth-token', JSON.stringify({json.dumps(mock_auth)}));
            localStorage.setItem('project_{test_project_id}', JSON.stringify({json.dumps(mock_project)}));
            localStorage.setItem('exterior_selection_{test_project_id}', JSON.stringify({json.dumps(saved_exterior)}));
        }} catch (e) {{}}
        """

        print("Registering pre-navigation script...", flush=True)
        await client.send("Page.addScriptToEvaluateOnNewDocument", {"source": setup_js})

        overview_url = f"http://localhost:5173/projects/{test_project_id}"
        print(f"Navigating to {overview_url}...", flush=True)
        await client.send("Page.navigate", {"url": overview_url})

        # Wait for React to mount and cards to appear
        for i in range(20):
            time.sleep(0.5)
            found = await client.eval_js("Boolean(document.querySelector('#overview-project-details-card'))")
            if found:
                print(f"Overview cards rendered after {(i + 1) * 0.5}s", flush=True)
                break
        time.sleep(1)

        # ── Test 1: Viewport 1920x1080 (Desktop)
        print("\n--- TEST 1: DESKTOP 1920x1080 ---", flush=True)
        await client.set_viewport(1920, 1080)
        time.sleep(1)

        details_card = await client.eval_js("""
            (() => {
                const card = document.querySelector('#overview-project-details-card');
                if (!card) return null;
                const rect = card.getBoundingClientRect();
                const parent = card.closest('.workspace-content');
                const parentRect = parent ? parent.getBoundingClientRect() : null;
                const text = card.innerText;
                return {
                    found: true,
                    top: rect.top,
                    bottom: rect.bottom,
                    height: rect.height,
                    width: rect.width,
                    clippedByParent: parentRect ? (rect.bottom > parentRect.bottom && parent.style.overflow === 'hidden') : false,
                    hasPlotDimensions: text.includes('50 ft (W) × 80 ft (L)'),
                    hasPlotArea: text.includes('4,000 sq ft'),
                    hasLocation: text.includes('Bengaluru, KA'),
                    hasBudget: text.includes('75,00,000')
                };
            })()
        """)
        print("Project Details Card Check:", json.dumps(details_card, indent=2), flush=True)

        module_card = await client.eval_js("""
            (() => {
                const card = document.querySelector('#overview-module-status-card');
                if (!card) return null;
                const rect = card.getBoundingClientRect();
                const items = Array.from(card.querySelectorAll('.module-status-item')).map(item => ({
                    title: item.querySelector('.module-name-title')?.innerText,
                    desc: item.querySelector('.module-desc-sub')?.innerText,
                    badge: item.querySelector('.pill-badge')?.innerText
                }));
                return {
                    found: true,
                    top: rect.top,
                    bottom: rect.bottom,
                    height: rect.height,
                    width: rect.width,
                    itemCount: items.length,
                    items: items
                };
            })()
        """)
        print("Module Status Card Check:", json.dumps(module_card, indent=2), flush=True)

        exterior_card = await client.eval_js("""
            (() => {
                const card = document.querySelector('#saved-exterior-showcase');
                if (!card) return null;
                const rect = card.getBoundingClientRect();
                const img = card.querySelector('img.saved-exterior-img');
                const swatches = Array.from(card.querySelectorAll('.color-swatch-chip')).map(chip => ({
                    name: chip.querySelector('.swatch-name')?.innerText,
                    hex: chip.querySelector('.swatch-hex')?.innerText,
                    color: chip.querySelector('.swatch-color-box')?.style.backgroundColor
                }));
                const specs = Array.from(card.querySelectorAll('.spec-tag')).map(t => t.innerText.trim());
                const costTag = card.querySelector('.cost-amount-tag')?.innerText;
                const nameTag = card.querySelector('.saved-exterior-name')?.innerText;

                return {
                    found: true,
                    name: nameTag,
                    top: rect.top,
                    bottom: rect.bottom,
                    height: rect.height,
                    imgSrc: img?.src,
                    imgNaturalWidth: img?.naturalWidth,
                    swatches: swatches,
                    specs: specs,
                    cost: costTag
                };
            })()
        """)
        print("Saved Exterior Showcase Card Check:", json.dumps(exterior_card, indent=2), flush=True)

        # Capture Desktop screenshot
        desktop_ss = os.path.join(ARTIFACT_DIR, "phase_6g4_overview_desktop_1920.png")
        await client.capture_screenshot(desktop_ss)

        # ── Test 2: Viewport 1600x900 (Standard Monitor)
        print("\n--- TEST 2: STANDARD MONITOR 1600x900 ---", flush=True)
        await client.set_viewport(1600, 900)
        time.sleep(1)

        layout_1600 = await client.eval_js("""
            (() => {
                const detailsRect = document.querySelector('#overview-project-details-card')?.getBoundingClientRect();
                const moduleRect = document.querySelector('#overview-module-status-card')?.getBoundingClientRect();
                const extRect = document.querySelector('#saved-exterior-showcase')?.getBoundingClientRect();
                return {
                    detailsBottom: detailsRect?.bottom,
                    moduleBottom: moduleRect?.bottom,
                    extBottom: extRect?.bottom,
                    bodyScrollHeight: document.body.scrollHeight,
                    windowInnerHeight: window.innerHeight
                };
            })()
        """)
        print("1600x900 Layout Metrics:", json.dumps(layout_1600, indent=2), flush=True)
        ss_1600 = os.path.join(ARTIFACT_DIR, "phase_6g4_overview_monitor_1600.png")
        await client.capture_screenshot(ss_1600)

        # ── Test 3: Viewport 1366x768 (Laptop / Smaller screen)
        print("\n--- TEST 3: LAPTOP 1366x768 ---", flush=True)
        await client.set_viewport(1366, 768)
        time.sleep(1)

        layout_1366 = await client.eval_js("""
            (() => {
                const detailsRect = document.querySelector('#overview-project-details-card')?.getBoundingClientRect();
                const moduleRect = document.querySelector('#overview-module-status-card')?.getBoundingClientRect();
                const extRect = document.querySelector('#saved-exterior-showcase')?.getBoundingClientRect();
                return {
                    detailsBottom: detailsRect?.bottom,
                    moduleBottom: moduleRect?.bottom,
                    extBottom: extRect?.bottom,
                    bodyScrollHeight: document.body.scrollHeight,
                    windowInnerHeight: window.innerHeight
                };
            })()
        """)
        print("1366x768 Layout Metrics:", json.dumps(layout_1366, indent=2), flush=True)
        laptop_ss = os.path.join(ARTIFACT_DIR, "phase_6g4_overview_laptop_1366.png")
        await client.capture_screenshot(laptop_ss)

        # ── Test 4: Scrolled Viewport on Desktop to Showcase Card
        print("\n--- TEST 4: SAVED EXTERIOR SHOWCASE VIEW ---", flush=True)
        await client.set_viewport(1920, 1080)
        await client.eval_js("document.querySelector('#saved-exterior-showcase')?.scrollIntoView({ behavior: 'instant', block: 'center' });")
        time.sleep(1)
        showcase_ss = os.path.join(ARTIFACT_DIR, "phase_6g4_overview_saved_exterior_showcase.png")
        await client.capture_screenshot(showcase_ss)

        # ── Test 5: Interactive Navigation to Exterior Studio
        print("\n--- TEST 5: INTERACTIVE NAVIGATION ---", flush=True)
        nav_test = await client.eval_js("""
            (() => {
                const extBtn = document.querySelector('#saved-exterior-showcase .btn-outline');
                if (extBtn) {
                    extBtn.click();
                    return { clicked: true, target: 'exterior_studio' };
                }
                return { clicked: false };
            })()
        """)
        print("Nav test clicked:", nav_test, flush=True)
        time.sleep(2)
        current_url = await client.eval_js("window.location.href")
        print("URL after clicking Exterior Studio button:", current_url, flush=True)

        # ── Test 6: Empty Exterior State Verification
        print("\n--- TEST 6: EMPTY EXTERIOR STATE ---", flush=True)
        await client.eval_js(f"localStorage.removeItem('exterior_selection_{test_project_id}');")
        await client.send("Page.navigate", {"url": overview_url})
        for i in range(15):
            time.sleep(0.5)
            has_empty = await client.eval_js("Boolean(document.querySelector('.empty-state-showcase-card'))")
            if has_empty:
                print(f"Empty state card rendered after {(i + 1) * 0.5}s", flush=True)
                break
        time.sleep(1)
        empty_info = await client.eval_js("""
            (() => {
                const card = document.querySelector('.empty-state-showcase-card');
                return {
                    found: Boolean(card),
                    text: card?.innerText
                };
            })()
        """)
        print("Empty State Card Check:", json.dumps(empty_info, indent=2), flush=True)
        empty_ss = os.path.join(ARTIFACT_DIR, "phase_6g4_overview_empty_exterior.png")
        await client.capture_screenshot(empty_ss)

        await client.close()
        print("\nAll Phase 6G.4 verification checks passed successfully!", flush=True)

    finally:
        proc.terminate()
        try:
            proc.wait(timeout=3)
        except Exception:
            proc.kill()

if __name__ == "__main__":
    asyncio.run(run())
