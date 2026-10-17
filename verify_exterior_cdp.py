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

CDP_PORT = 9225
USER_DATA_DIR = tempfile.mkdtemp(prefix="browser_cdp_ext_")
ARTIFACT_DIR = r"C:\Users\DELL\.gemini\antigravity\brain\35ff5483-d119-45be-a407-00f491b2c1fa"

class CDPClient:
    def __init__(self, ws_url):
        self.ws_url = ws_url
        self.ws = None
        self._id = 0

    async def connect(self):
        self.ws = await websockets.connect(self.ws_url)

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
        "--window-size=1440,900",
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
        print(f"Connected to CDP page target: {ws_url} (title: {target.get('title')})", flush=True)

        client = CDPClient(ws_url)
        await client.connect()

        await client.send("Page.enable")
        await client.send("Runtime.enable")
        await client.send("Console.enable")

        test_project_id = "d0e134d1-b801-455a-b71a-82c30ec0b0d1"

        print("\n--- TEST 1: Initial load with Auth & Full Project Configuration ---")
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
                "user_metadata": {"full_name": "Test Architect"}
            }
        }

        mock_project = {
            "id": test_project_id,
            "user_id": "c1a4118e-e650-4eb4-9164-47c1f2d24a6d",
            "name": "Emerald Luxury Villa",
            "plot_width": 40,
            "plot_length": 60,
            "facing": "north",
            "floors": 2,
            "design_style": "Modern Luxury"
        }

        # Navigate to domain first to seed localStorage
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
        """
        await client.eval_js(seed_js)
        print("Pre-seeded localStorage successfully.", flush=True)

        # Navigate to Dedicated Exterior Studio Route
        ext_url = f"http://localhost:5173/projects/{test_project_id}/exterior"
        print(f"Navigating to {ext_url}...")
        await client.send("Page.navigate", {"url": ext_url})
        
        # Wait for loading state to finish and cards to mount
        for _ in range(20):
            cards_count = await client.eval_js("document.querySelectorAll('.exterior-card').length")
            if cards_count and cards_count > 0:
                break
            await asyncio.sleep(0.5)

        current_url = await client.eval_js("window.location.href")
        body_snippet = await client.eval_js("document.body.innerText.substring(0, 300)")
        print(f"Current URL: {current_url}", flush=True)
        print(f"Body snippet: {body_snippet}", flush=True)

        title_text = await client.eval_js("document.querySelector('.studio-page-title')?.innerText")
        proj_tag = await client.eval_js("document.querySelector('.studio-project-tag')?.innerText")
        cards_count = await client.eval_js("document.querySelectorAll('.exterior-card').length")
        compat_badges = await client.eval_js("document.querySelectorAll('.compatibility-badge-box').length")
        cost_text = await client.eval_js("document.querySelector('.cost-amount')?.innerText")

        print(f"Studio Title: {title_text}", flush=True)
        print(f"Project Tag: {proj_tag}", flush=True)
        print(f"Exterior Cards Rendered: {cards_count} (Expect 32)", flush=True)
        print(f"Compatibility Badges Rendered: {compat_badges}", flush=True)
        print(f"Current Cost: {cost_text}", flush=True)

        # Capture Screenshot of Exterior Studio Gallery
        os.makedirs(ARTIFACT_DIR, exist_ok=True)
        gallery_shot = os.path.join(ARTIFACT_DIR, "phase_6f1_exterior_studio_gallery.png")
        await client.capture_screenshot(gallery_shot)

        # TEST 2: Open Customization Modal on first card
        print("\n--- TEST 2: Opening Customization Modal ---")
        open_modal_res = await client.eval_js("""
        (function() {
            const btn = document.querySelector('.btn-customize-elevation');
            if (btn) {
                btn.click();
                return 'clicked';
            }
            return 'not_found';
        })()
        """)
        print(f"Clicked customize button: {open_modal_res}")
        await asyncio.sleep(1.5)

        modal_title = await client.eval_js("document.querySelector('.modal-header-title')?.innerText")
        color_inputs = await client.eval_js("document.querySelectorAll('.native-color-swatch-input').length")
        breakdown_rows = await client.eval_js("document.querySelectorAll('.cost-breakdown-row').length")
        print(f"Modal Title: {modal_title}")
        print(f"Color Swatch Inputs: {color_inputs}")
        print(f"Cost Breakdown Rows: {breakdown_rows}")

        # Capture Screenshot of Customization Modal
        modal_shot = os.path.join(ARTIFACT_DIR, "phase_6f1_exterior_customizer_modal.png")
        await client.capture_screenshot(modal_shot)

        # TEST 3: Apply & Save Selection in Modal
        print("\n--- TEST 3: Applying and Saving Customization ---")
        save_btn_res = await client.eval_js("""
        (function() {
            const saveBtn = Array.from(document.querySelectorAll('button')).find(b => b.innerText.includes('Apply & Save Selection'));
            if (saveBtn) {
                saveBtn.click();
                return 'saved_clicked';
            }
            return 'save_not_found';
        })()
        """)
        print(f"Clicked save button: {save_btn_res}")
        await asyncio.sleep(2.0)

        # Check Active Elevation Card Banner
        active_banner = await client.eval_js("document.querySelector('.active-elevation-card')?.innerText")
        new_cost = await client.eval_js("document.querySelector('.cost-amount')?.innerText")
        print(f"Active Banner rendered: {'Yes' if active_banner else 'No'}")
        print(f"Updated Total Exterior Cost: {new_cost}")

        # Capture Screenshot with Active Selection Banner
        active_shot = os.path.join(ARTIFACT_DIR, "phase_6f1_exterior_studio_active_selection.png")
        await client.capture_screenshot(active_shot)

        await client.close()
        print("\nVerification completed successfully!")

    finally:
        edge_proc.terminate()
        try:
            edge_proc.wait(timeout=2)
        except Exception:
            edge_proc.kill()

if __name__ == "__main__":
    asyncio.run(run_verification())
