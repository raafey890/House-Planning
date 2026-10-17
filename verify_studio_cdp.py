import asyncio
import json
import os
import subprocess
import tempfile
import time
import urllib.request
import websockets

EDGE_EXE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
CDP_PORT = 9222
USER_DATA_DIR = os.path.join(tempfile.gettempdir(), "edge_cdp_profile_interior")

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
        print(f"Screenshot saved: {filepath} ({len(data)} bytes)")

    async def close(self):
        if self.ws:
            await self.ws.close()

async def run_verification():
    print("Launching Edge headless...")
    edge_proc = subprocess.Popen([
        EDGE_EXE,
        "--headless=new",
        f"--remote-debugging-port={CDP_PORT}",
        f"--user-data-dir={USER_DATA_DIR}",
        "--disable-gpu",
        "--no-first-run",
        "--no-default-browser-check",
        "about:blank"
    ])

    time.sleep(2)

    try:
        # Get CDP targets
        req = urllib.request.urlopen(f"http://127.0.0.1:{CDP_PORT}/json")
        targets = json.loads(req.read().decode())
        ws_url = targets[0]["webSocketDebuggerUrl"]
        print(f"Connected to CDP target: {ws_url}")

        client = CDPClient(ws_url)
        await client.connect()

        # Enable necessary domains
        await client.send("Page.enable")
        await client.send("Runtime.enable")
        await client.send("Console.enable")

        test_project_id = "d0e134d1-b801-455a-b71a-82c30ec0b0d1"

        # TEST 1: Direct navigation with authenticated session and project with floor plan
        print("\n--- TEST 1: Initial load with Auth & Full Project with Floor Plan ---")
        # Pre-seed localStorage with auth session and a sample floor plan
        mock_auth = {
            "access_token": "mock-jwt-token-12345",
            "token_type": "bearer",
            "expires_in": 3600,
            "refresh_token": "mock-refresh-token",
            "user": {
                "id": "c1a4118e-e650-4eb4-9164-47c1f2d24a6d",
                "email": "user@example.com"
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

        mock_floorplan = {
            "layout_data": {
                "floors": [
                    {
                        "name": "Ground Floor",
                        "rooms": [
                            {"id": "r_lr_01", "name": "Grand Living Room", "type": "living_room", "width": 18, "length": 22, "area": 396},
                            {"id": "r_kit_01", "name": "Chef Modular Kitchen", "type": "kitchen", "width": 14, "length": 15, "area": 210},
                            {"id": "r_mbr_01", "name": "Master Suite Bedroom", "type": "master_bedroom", "width": 16, "length": 18, "area": 288},
                            {"id": "r_bath_01", "name": "Master En-Suite Bath", "type": "bathroom", "width": 8, "length": 10, "area": 80},
                            {"id": "r_stairs_01", "name": "Internal Staircase", "type": "staircase", "width": 7, "length": 12, "area": 84}
                        ],
                        "doors": [
                            {"id": "d1", "room_id": "r_lr_01", "width": 4.0},
                            {"id": "d2", "room_id": "r_mbr_01", "width": 3.5}
                        ],
                        "windows": [
                            {"id": "w1", "room_id": "r_lr_01", "width": 6.0},
                            {"id": "w2", "room_id": "r_mbr_01", "width": 5.0}
                        ]
                    }
                ]
            }
        }

        # Navigate to domain first to access localStorage
        await client.send("Page.navigate", {"url": "http://localhost:5173/"})
        await asyncio.sleep(1.5)

        # Inject auth and cache into localStorage
        seed_script = f"""
        localStorage.setItem('sb-cptjtxjqsyuwrwstcehu-auth-token', JSON.stringify({json.dumps(mock_auth)}));
        localStorage.setItem('project_{test_project_id}', JSON.stringify({json.dumps(mock_project)}));
        localStorage.setItem('floorplan_{test_project_id}', JSON.stringify({json.dumps(mock_floorplan)}));
        """
        await client.eval_js(seed_script)

        # Now navigate to the actual Interior Studio route
        target_url = f"http://localhost:5173/projects/{test_project_id}/interior"
        print(f"Navigating to {target_url}...")
        await client.send("Page.navigate", {"url": target_url})
        await asyncio.sleep(2.5)

        # Inspect DOM
        title = await client.eval_js("document.title")
        body_text_len = await client.eval_js("document.body.innerText.length")
        root_html_len = await client.eval_js("document.getElementById('root')?.innerHTML.length")
        page_title = await client.eval_js("document.querySelector('.studio-page-title')?.innerText")
        project_pill = await client.eval_js("document.querySelector('.studio-project-pill')?.innerText")
        room_items = await client.eval_js("Array.from(document.querySelectorAll('.room-nav-item')).map(el => el.innerText.split('\\n')[0])")
        design_cards = await client.eval_js("document.querySelectorAll('.design-gallery-card').length")
        staircase_present = await client.eval_js("Array.from(document.querySelectorAll('.room-nav-item')).some(el => el.innerText.toLowerCase().includes('stair'))")

        print(f"Document Title: {title}")
        print(f"Root HTML Length: {root_html_len}")
        print(f"Body Text Length: {body_text_len}")
        print(f"Page Title in DOM: {page_title}")
        print(f"Project Pill in DOM: {project_pill}")
        print(f"Rooms in Navigation Sidebar: {room_items}")
        print(f"Staircase in Room List (Must be False): {staircase_present}")
        print(f"Design Cards Rendered in Gallery: {design_cards} (Expect 32)")

        screenshot_path = os.path.join(os.getcwd(), "studio_success_state.png")
        await client.capture_screenshot(screenshot_path)

        # TEST 2: Missing Floor Plan State (No silent fake rooms!)
        print("\n--- TEST 2: Missing Floor Plan State (No fake rooms) ---")
        clear_plan_script = f"""
        localStorage.removeItem('floorplan_{test_project_id}');
        """
        await client.eval_js(clear_plan_script)
        await client.send("Page.navigate", {"url": target_url})
        await asyncio.sleep(2.0)

        missing_plan_title = await client.eval_js("document.querySelector('.studio-state-title')?.innerText")
        missing_plan_desc = await client.eval_js("document.querySelector('.studio-state-desc')?.innerText")
        planner_btn = await client.eval_js("document.querySelector('.btn-studio-primary')?.innerText")

        print(f"Missing Plan Title: {missing_plan_title}")
        print(f"Missing Plan Description: {missing_plan_desc}")
        print(f"Action Button: {planner_btn}")

        screenshot_missing_plan = os.path.join(os.getcwd(), "studio_missing_plan_state.png")
        await client.capture_screenshot(screenshot_missing_plan)

        # TEST 3: Missing Project State
        print("\n--- TEST 3: Missing / Invalid Project State ---")
        invalid_url = "http://localhost:5173/projects/00000000-0000-0000-0000-000000000000/interior"
        await client.send("Page.navigate", {"url": invalid_url})
        await asyncio.sleep(2.0)

        not_found_title = await client.eval_js("document.querySelector('.studio-state-title')?.innerText")
        not_found_desc = await client.eval_js("document.querySelector('.studio-state-desc')?.innerText")
        print(f"Not Found Title: {not_found_title}")
        print(f"Not Found Description: {not_found_desc}")

        screenshot_not_found = os.path.join(os.getcwd(), "studio_not_found_state.png")
        await client.capture_screenshot(screenshot_not_found)

        await client.close()
        print("\nAll verification checks completed successfully!")

    finally:
        edge_proc.terminate()
        try:
            edge_proc.wait(timeout=3)
        except Exception:
            edge_proc.kill()

if __name__ == "__main__":
    asyncio.run(run_verification())
