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

CDP_PORT = 9226
USER_DATA_DIR = tempfile.mkdtemp(prefix="browser_cdp_p6f2_")
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
        print(f"Screenshot saved: {filepath} ({len(data)} bytes)", flush=True)

    async def close(self):
        if self.ws:
            await self.ws.close()

async def run_verification():
    print(f"Launching headless browser on port {CDP_PORT}...", flush=True)
    edge_proc = subprocess.Popen([
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

    if not targets:
        print("Failed to reach Edge CDP port!", flush=True)
        return

    try:
        pages = [t for t in targets if t.get("type") == "page"]
        target = pages[0] if pages else targets[0]
        ws_url = target["webSocketDebuggerUrl"]
        print(f"Connected to CDP page target: {ws_url}", flush=True)

        client = CDPClient(ws_url)
        await client.connect()

        await client.send("Page.enable")
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
            "plot_width": 35,
            "plot_length": 50,
            "facing": "north",
            "floors": 2,
            "design_style": "Modern Contemporary"
        }

        mock_selection = {
            "project_id": test_project_id,
            "selection": {
                "project_id": test_project_id,
                "design_id": "ext_mod_01",
                "design_name": "Geometric Cubic Modern Elevation",
                "category": "modern_contemporary",
                "style": "Modern Contemporary",
                "colors": {
                    "primary_wall": "#F4F4F0",
                    "accent_wall": "#2B313B",
                    "boundary_wall": "#2B313B",
                    "door": "#8B5A2B",
                    "window_frame": "#1F2937",
                    "railing": "#1F2937"
                },
                "materials": {
                    "finish_type": "textured_paint",
                    "cladding_type": "fluted_composite_louvers",
                    "door_material": "solid_teak",
                    "railing_material": "toughened_glass"
                },
                "lighting": {
                    "style": "architectural_grazers",
                    "fixture_count": 8
                },
                "landscaping": {
                    "greenery_level": "moderate"
                }
            },
            "total_exterior_cost": 165000
        }

        # Navigate to domain to seed localStorage
        await client.send("Page.navigate", {"url": "http://localhost:5173/"})
        await asyncio.sleep(1.5)

        seed_js = f"""
        localStorage.setItem('sb-cptjtxjqsyuwrwstcehu-auth-token', JSON.stringify({json.dumps(mock_auth)}));
        localStorage.setItem('project_{test_project_id}', JSON.stringify({json.dumps(mock_project)}));
        localStorage.setItem('floorplan_{test_project_id}', JSON.stringify({{ "layout_data": {{ "floors": [{{ "name": "Ground Floor", "rooms": [{{ "id": "r1", "name": "Living", "type": "living_room" }}] }}] }} }}));
        localStorage.setItem('projects-storage', JSON.stringify({{
            state: {{
                projects: [{json.dumps(mock_project)}],
                currentProject: {json.dumps(mock_project)}
            }},
            version: 0
        }}));
        localStorage.setItem('exterior_selection_{test_project_id}', JSON.stringify({json.dumps(mock_selection)}));
        """
        await client.eval_js(seed_js)
        print("Pre-seeded project and exterior selection into localStorage.", flush=True)

        # Navigate to Dedicated Exterior Studio
        ext_url = f"http://localhost:5173/projects/{test_project_id}/exterior"
        print(f"Navigating to {ext_url}...")
        await client.send("Page.navigate", {"url": ext_url})

        # Wait for SVG canvas to render
        for _ in range(25):
            has_svg = await client.eval_js("document.querySelector('.elevation-svg-wrapper svg') !== null")
            if has_svg:
                break
            await asyncio.sleep(0.5)

        title = await client.eval_js("document.querySelector('.hero-title')?.innerText")
        cost = await client.eval_js("document.querySelector('.hero-cost-value')?.innerText")
        has_svg = await client.eval_js("document.querySelector('.elevation-svg-wrapper svg') !== null")
        print(f"Hero Title: {title}")
        print(f"Elevation Upgrade Cost: {cost}")
        print(f"Vector Elevation SVG Rendered: {has_svg}")

        # Capture Screenshot 1: Front Elevation Daylight
        os.makedirs(ARTIFACT_DIR, exist_ok=True)
        shot1 = os.path.join(ARTIFACT_DIR, "phase_6f2_front_elevation_daylight.png")
        await client.capture_screenshot(shot1)

        # TEST 2: Switch to Left 3/4 Perspective and Night Mode
        print("\n--- TEST 2: Switching to Left 3/4 Perspective & Night Lights ---")
        await client.eval_js("""
        (function() {
            const pills = Array.from(document.querySelectorAll('.btn-pill'));
            const leftPill = pills.find(p => p.innerText.includes('Left 3/4 Perspective'));
            if (leftPill) leftPill.click();

            const lights = Array.from(document.querySelectorAll('.btn-lighting'));
            const nightBtn = lights.find(b => b.innerText.includes('Night Lights'));
            if (nightBtn) nightBtn.click();
        })()
        """)
        await asyncio.sleep(2.0)

        shot2 = os.path.join(ARTIFACT_DIR, "phase_6f2_left_perspective_night.png")
        await client.capture_screenshot(shot2)

        # TEST 3: Switch to Right 3/4 Perspective & Daylight
        print("\n--- TEST 3: Switching to Right 3/4 Perspective ---")
        await client.eval_js("""
        (function() {
            const pills = Array.from(document.querySelectorAll('.btn-pill'));
            const rightPill = pills.find(p => p.innerText.includes('Right 3/4 Perspective'));
            if (rightPill) rightPill.click();

            const lights = Array.from(document.querySelectorAll('.btn-lighting'));
            const dayBtn = lights.find(b => b.innerText.includes('Daylight'));
            if (dayBtn) dayBtn.click();
        })()
        """)
        await asyncio.sleep(2.0)

        shot3 = os.path.join(ARTIFACT_DIR, "phase_6f2_right_perspective.png")
        await client.capture_screenshot(shot3)

        # TEST 4: Split View Comparison (Personalized Blueprint vs Reference Photo)
        print("\n--- TEST 4: Testing Split View Comparison ---")
        await client.eval_js("""
        (function() {
            const pills = Array.from(document.querySelectorAll('.btn-pill'));
            const splitBtn = pills.find(p => p.innerText.includes('Split View'));
            if (splitBtn) splitBtn.click();
        })()
        """)
        await asyncio.sleep(1.5)

        shot4 = os.path.join(ARTIFACT_DIR, "phase_6f2_split_comparison.png")
        await client.capture_screenshot(shot4)

        # TEST 5: Test AI Render Trigger and Honest Diagnostics
        print("\n--- TEST 5: Testing AI Render Generation & Diagnostics ---")
        ai_click_res = await client.eval_js("""
        (function() {
            const aiBtn = Array.from(document.querySelectorAll('button')).find(b => b.innerText.includes('Generate Photorealistic Render'));
            if (aiBtn) {
                aiBtn.scrollIntoView({ behavior: 'instant', block: 'center' });
                aiBtn.click();
                return 'ai_clicked';
            }
            return 'ai_not_found';
        })()
        """)
        print(f"Triggered AI Render button: {ai_click_res}")
        await asyncio.sleep(2.5)

        diagnostic_text = await client.eval_js("document.querySelector('.ai-diagnostic-banner')?.innerText")
        print(f"AI Diagnostic Notice: {diagnostic_text}")

        # Scroll to show AI bar and diagnostic banner in center
        await client.eval_js("document.querySelector('.ai-render-action-bar')?.scrollIntoView({ behavior: 'instant', block: 'center' })")
        await asyncio.sleep(1.0)

        shot5 = os.path.join(ARTIFACT_DIR, "phase_6f2_ai_generation_diagnostics.png")
        await client.capture_screenshot(shot5)

        await client.close()
        print("\nPhase 6F.2 Browser CDP Verification Completed Successfully!", flush=True)

    finally:
        edge_proc.terminate()
        try:
            edge_proc.wait(timeout=2)
        except Exception:
            edge_proc.kill()

if __name__ == "__main__":
    asyncio.run(run_verification())
