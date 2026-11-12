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

CDP_PORT = 9235
USER_DATA_DIR = tempfile.mkdtemp(prefix="browser_cdp_bar_")
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
            "facing": "south",
            "floors": 2,
            "design_style": "Modern Contemporary"
        }

        setup_js = f"""
        localStorage.setItem('app_auth_session', JSON.stringify({json.dumps(mock_auth)}));
        localStorage.setItem('sb-xhyckokbgyqkmvxqfghp-auth-token', JSON.stringify({json.dumps(mock_auth)}));
        localStorage.setItem('project_{test_project_id}', JSON.stringify({json.dumps(mock_project)}));
        """

        print("Seeding credentials...", flush=True)
        await client.send("Page.navigate", {"url": "http://localhost:5173/"})
        time.sleep(1.5)
        await client.eval_js(setup_js)

        url = f"http://localhost:5173/projects/{test_project_id}/exterior"
        print(f"Navigating to {url}...", flush=True)
        await client.send("Page.navigate", {"url": url})

        for _ in range(15):
            time.sleep(1)
            ready = await client.eval_js("document.readyState === 'complete' && !document.querySelector('.fp-loading-spinner')")
            if ready:
                break
        time.sleep(2)

        # Navigate to Step 2
        print("Navigating to Step 2 (Customize)...", flush=True)
        await client.eval_js("""
            (() => {
                const btn = Array.from(document.querySelectorAll('.stage-step-btn')).find(b => b.innerText.includes('Customize') || b.innerText.includes('2'));
                if (btn) btn.click();
            })()
        """)
        time.sleep(2)

        # Test at standard desktop (1440x960)
        print("\n--- Testing at Desktop 1440x960 ---", flush=True)
        desktop_check = await client.eval_js("""
            (() => {
                const bar = document.querySelector('.viewer-bottom-bar-v3');
                const b1 = document.querySelector('.viewer-bottom-left-badge');
                const b2 = document.querySelector('.viewer-bottom-right-badge');

                if (!bar || !b1 || !b2) return { error: 'Badges not found' };

                const r1 = b1.getBoundingClientRect();
                const r2 = b2.getBoundingClientRect();

                // Exact collision check
                const overlap = !(r1.right <= r2.left || r2.right <= r1.left || r1.bottom <= r2.top || r2.bottom <= r1.top);

                return {
                    hasBar: !!bar,
                    b1: { left: r1.left, right: r1.right, top: r1.top, bottom: r1.bottom, width: r1.width, height: r1.height, text: b1.innerText },
                    b2: { left: r2.left, right: r2.right, top: r2.top, bottom: r2.bottom, width: r2.width, height: r2.height, text: b2.innerText },
                    overlap
                };
            })()
        """)
        print(f"Desktop Result: {json.dumps(desktop_check, indent=2)}", flush=True)
        assert desktop_check.get("overlap") is False, "Badges must not overlap at 1440px!"

        shot_desktop = os.path.join(ARTIFACT_DIR, "phase_6g3_fixed_bottom_bar_desktop.png")
        await client.capture_screenshot(shot_desktop)

        # Test at laptop resolution 1366x768 (where 2-column card is narrower)
        print("\n--- Testing at 1366x768 Laptop Resolution ---", flush=True)
        await client.send("Emulation.setDeviceMetricsOverride", {
            "width": 1366,
            "height": 768,
            "deviceScaleFactor": 1,
            "mobile": False
        })
        time.sleep(1.5)

        laptop_check = await client.eval_js("""
            (() => {
                const b1 = document.querySelector('.viewer-bottom-left-badge');
                const b2 = document.querySelector('.viewer-bottom-right-badge');

                if (!b1 || !b2) return { error: 'Badges not found' };

                const r1 = b1.getBoundingClientRect();
                const r2 = b2.getBoundingClientRect();
                const overlap = !(r1.right <= r2.left || r2.right <= r1.left || r1.bottom <= r2.top || r2.bottom <= r1.top);

                return {
                    b1: { left: r1.left, right: r1.right, top: r1.top, bottom: r1.bottom, width: r1.width, text: b1.innerText },
                    b2: { left: r2.left, right: r2.right, top: r2.top, bottom: r2.bottom, width: r2.width, text: b2.innerText },
                    overlap
                };
            })()
        """)
        print(f"1366px Laptop Result: {json.dumps(laptop_check, indent=2)}", flush=True)
        assert laptop_check.get("overlap") is False, "Badges must not overlap at 1366px!"

        shot_laptop = os.path.join(ARTIFACT_DIR, "phase_6g3_fixed_bottom_bar_laptop.png")
        await client.capture_screenshot(shot_laptop)

        # Test at narrow 1024x768 tablet
        print("\n--- Testing at 1024x768 Tablet Resolution ---", flush=True)
        await client.send("Emulation.setDeviceMetricsOverride", {
            "width": 1024,
            "height": 768,
            "deviceScaleFactor": 1,
            "mobile": False
        })
        time.sleep(1.5)

        tablet_check = await client.eval_js("""
            (() => {
                const b1 = document.querySelector('.viewer-bottom-left-badge');
                const b2 = document.querySelector('.viewer-bottom-right-badge');

                if (!b1 || !b2) return { error: 'Badges not found' };

                const r1 = b1.getBoundingClientRect();
                const r2 = b2.getBoundingClientRect();
                const overlap = !(r1.right <= r2.left || r2.right <= r1.left || r1.bottom <= r2.top || r2.bottom <= r1.top);

                return {
                    b1: { left: r1.left, right: r1.right, top: r1.top, bottom: r1.bottom, width: r1.width, text: b1.innerText },
                    b2: { left: r2.left, right: r2.right, top: r2.top, bottom: r2.bottom, width: r2.width, text: b2.innerText },
                    overlap
                };
            })()
        """)
        print(f"1024px Tablet Result: {json.dumps(tablet_check, indent=2)}", flush=True)
        assert tablet_check.get("overlap") is False, "Badges must not overlap at 1024px!"

        shot_tablet = os.path.join(ARTIFACT_DIR, "phase_6g3_fixed_bottom_bar_tablet.png")
        await client.capture_screenshot(shot_tablet)

        print("\n=== ALL BOTTOM BAR OVERLAP VERIFICATIONS PASSED (overlap: false) ===", flush=True)

    finally:
        await client.close()
        proc.terminate()
        try:
            proc.wait(timeout=3)
        except Exception:
            proc.kill()

if __name__ == "__main__":
    asyncio.run(run())
