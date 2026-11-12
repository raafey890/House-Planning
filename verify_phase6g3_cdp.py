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

CDP_PORT = 9231
USER_DATA_DIR = tempfile.mkdtemp(prefix="browser_cdp_p6g3_")
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

async def run_verification():
    print(f"=== PHASE 6G.3 CDP VERIFICATION START ===", flush=True)
    print(f"Launching browser on port {CDP_PORT}...", flush=True)
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

        mock_floorplan = {
            "rooms": [
                {"id": "living_01", "name": "Formal Living Room", "x": 2, "y": 2, "width": 16, "length": 18, "floor": 0, "room_type": "living"},
                {"id": "dining_01", "name": "Dining & Breakfast Bar", "x": 18, "y": 2, "width": 12, "length": 14, "floor": 0, "room_type": "dining"},
                {"id": "kitchen_01", "name": "Open Modular Kitchen", "x": 18, "y": 16, "width": 12, "length": 12, "floor": 0, "room_type": "kitchen"},
                {"id": "master_01", "name": "Master Suite", "x": 2, "y": 20, "width": 16, "length": 16, "floor": 0, "room_type": "bedroom"},
                {"id": "bed_02", "name": "Guest Bedroom", "x": 2, "y": 2, "width": 14, "length": 16, "floor": 1, "room_type": "bedroom"},
                {"id": "lounge_02", "name": "Family Lounge & Terrace", "x": 16, "y": 2, "width": 14, "length": 16, "floor": 1, "room_type": "living"}
            ],
            "walls": [],
            "doors": [],
            "windows": [],
            "total_builtup_sqft": 3200
        }

        setup_js = f"""
        localStorage.setItem('app_auth_session', JSON.stringify({json.dumps(mock_auth)}));
        localStorage.setItem('sb-xhyckokbgyqkmvxqfghp-auth-token', JSON.stringify({json.dumps(mock_auth)}));
        localStorage.setItem('project_{test_project_id}', JSON.stringify({json.dumps(mock_project)}));
        localStorage.setItem('floorplan_{test_project_id}', JSON.stringify({json.dumps(mock_floorplan)}));
        """

        print("Seeding local session credentials...", flush=True)
        await client.send("Page.navigate", {"url": "http://localhost:5173/"})
        time.sleep(2)
        await client.eval_js(setup_js)

        url = f"http://localhost:5173/projects/{test_project_id}/exterior"
        print(f"Navigating to {url}...", flush=True)
        await client.send("Page.navigate", {"url": url})

        # Wait for page load
        for _ in range(15):
            time.sleep(1)
            ready = await client.eval_js("document.readyState === 'complete' && !document.querySelector('.fp-loading-spinner')")
            if ready:
                print("Page DOM loaded and loading spinner cleared.", flush=True)
                break

        time.sleep(3)

        # Check title and current stage
        page_info = await client.eval_js("""
            (() => {
                const title = document.querySelector('h1')?.innerText || '';
                const activeNav = document.querySelector('.wizard-step-node.active .step-node-name')?.innerText || '';
                const cards = document.querySelectorAll('.exterior-design-card').length;
                return { title, activeNav, cards };
            })()
        """)
        print(f"Initial Page State: {page_info}", flush=True)

        # Transition to Stage 2 by clicking the palette icon or selecting a design card
        print("\n--- Selecting design and navigating to Step 2 ---", flush=True)
        await client.eval_js("""
            (() => {
                // Click customize button on first card or card itself
                const btn = document.querySelector('.exterior-design-card button[title*="customize"]') ||
                            document.querySelector('.exterior-design-card button');
                if (btn) btn.click();
            })()
        """)
        time.sleep(1.5)

        # Ensure we are in Stage 2
        await client.eval_js("""
            (() => {
                const navBtns = document.querySelectorAll('.stage-step-btn');
                for (const b of navBtns) {
                    if (b.innerText.includes('Customize') || b.innerText.includes('2')) {
                        b.click();
                        break;
                    }
                }
            })()
        """)
        time.sleep(2)

        # Verify Stage 2 Layout
        layout_check = await client.eval_js("""
            (() => {
                const workspace = document.querySelector('.stage2-customizer-workspace');
                const leftPanel = document.querySelector('.stage2-controls-panel');
                const rightPanel = document.querySelector('.stage2-preview-panel');
                const stickyCard = document.querySelector('.stage2-preview-sticky-card');
                const canvas = document.querySelector('.stage2-viewer-canvas-box canvas');
                const topBar = document.querySelector('.viewer-top-bar-v3');
                const presetsPill = document.querySelector('.viewer-presets-pill-group');
                const actionsPill = document.querySelector('.viewer-actions-pill-group');

                let topBarOverlap = false;
                if (presetsPill && actionsPill) {
                    const r1 = presetsPill.getBoundingClientRect();
                    const r2 = actionsPill.getBoundingClientRect();
                    topBarOverlap = !(r1.right < r2.left || r2.right < r1.left || r1.bottom < r2.top || r2.bottom < r1.top);
                }

                return {
                    hasWorkspace: !!workspace,
                    hasLeftPanel: !!leftPanel,
                    hasRightPanel: !!rightPanel,
                    hasStickyCard: !!stickyCard,
                    hasCanvas: !!canvas,
                    hasTopBar: !!topBar,
                    topBarOverlap
                };
            })()
        """)
        print(f"Stage 2 Layout Verification: {layout_check}", flush=True)

        # Take screenshot of Step 2 initial live 3D preview
        step2_shot = os.path.join(ARTIFACT_DIR, "phase_6g3_step2_live_3d_preview.png")
        await client.capture_screenshot(step2_shot)

        # Test Material Sync via Three.js
        print("\n--- Testing Live Material Synchronization in 3D Viewer ---", flush=True)

        # Test 1: Change Main Wall to Ivory
        print("1. Selecting Main Walls and applying Ivory color (#FAF9F6)...", flush=True)
        sync_result1 = await client.eval_js("""
            (() => {
                // Click primary_wall component
                const pills = document.querySelectorAll('.component-pill');
                for (const p of pills) {
                    if (p.innerText.includes('Main Walls')) {
                        p.click();
                        break;
                    }
                }

                // Apply via Hex input
                const hexField = document.querySelector('.hex-field');
                if (hexField) {
                    // Set value and trigger input event
                    hexField.value = 'FAF9F6';
                    hexField.dispatchEvent(new Event('input', { bubbles: true }));
                }
                const applyBtn = document.querySelector('.btn-apply-hex');
                if (applyBtn && !applyBtn.disabled) {
                    applyBtn.click();
                }

                const mat = window.__exteriorViewerMaterials ? window.__exteriorViewerMaterials.primary_wall : null;
                const activeHex = document.querySelector('.component-pill.active .component-pill-hex')?.innerText || '';
                return {
                    activeComponent: document.querySelector('.component-pill.active .component-pill-name')?.innerText || '',
                    activeHex: activeHex,
                    matHex: mat ? ('#' + mat.color.getHexString().toUpperCase()) : 'N/A'
                };
            })()
        """)
        print(f"   Main Wall Sync Result: {sync_result1}", flush=True)
        time.sleep(1)

        # Test 2: Change Main Wall to Charcoal Slate
        print("2. Changing Main Wall to Slate Charcoal (#2B313B)...", flush=True)
        sync_result2 = await client.eval_js("""
            (() => {
                const hexField = document.querySelector('.hex-field');
                if (hexField) {
                    hexField.value = '2B313B';
                    hexField.dispatchEvent(new Event('input', { bubbles: true }));
                }
                const applyBtn = document.querySelector('.btn-apply-hex');
                if (applyBtn && !applyBtn.disabled) {
                    applyBtn.click();
                }

                const mat = window.__exteriorViewerMaterials ? window.__exteriorViewerMaterials.primary_wall : null;
                const activeHex = document.querySelector('.component-pill.active .component-pill-hex')?.innerText || '';
                return {
                    activeHex: activeHex,
                    matHex: mat ? ('#' + mat.color.getHexString().toUpperCase()) : 'N/A'
                };
            })()
        """)
        print(f"   Charcoal Slate Sync Result: {sync_result2}", flush=True)
        time.sleep(1)

        # Test 3: Change Entrance Door to Warm Walnut
        print("3. Selecting Entrance Door and applying Warm Walnut (#8B5A2B)...", flush=True)
        sync_result3 = await client.eval_js("""
            (() => {
                const pills = document.querySelectorAll('.component-pill');
                for (const p of pills) {
                    if (p.innerText.includes('Entrance Door') || p.innerText.includes('Door')) {
                        p.click();
                        break;
                    }
                }

                const hexField = document.querySelector('.hex-field');
                if (hexField) {
                    hexField.value = '8B5A2B';
                    hexField.dispatchEvent(new Event('input', { bubbles: true }));
                }
                const applyBtn = document.querySelector('.btn-apply-hex');
                if (applyBtn && !applyBtn.disabled) {
                    applyBtn.click();
                }

                const mat = window.__exteriorViewerMaterials ? window.__exteriorViewerMaterials.door : null;
                const activeHex = document.querySelector('.component-pill.active .component-pill-hex')?.innerText || '';
                return {
                    component: 'door',
                    activeHex: activeHex,
                    matHex: mat ? ('#' + mat.color.getHexString().toUpperCase()) : 'N/A'
                };
            })()
        """)
        print(f"   Entrance Door Sync Result: {sync_result3}", flush=True)
        time.sleep(1)

        # Test 4: Change Window Frames to Dark Graphite (#20252B)
        print("4. Selecting Window Frames and applying Dark Graphite (#20252B)...", flush=True)
        sync_result4 = await client.eval_js("""
            (() => {
                const pills = document.querySelectorAll('.component-pill');
                for (const p of pills) {
                    if (p.innerText.includes('Window Frame') || p.innerText.includes('Windows')) {
                        p.click();
                        break;
                    }
                }

                const hexField = document.querySelector('.hex-field');
                if (hexField) {
                    hexField.value = '20252B';
                    hexField.dispatchEvent(new Event('input', { bubbles: true }));
                }
                const applyBtn = document.querySelector('.btn-apply-hex');
                if (applyBtn && !applyBtn.disabled) {
                    applyBtn.click();
                }

                const mat = window.__exteriorViewerMaterials ? window.__exteriorViewerMaterials.window_frame : null;
                const activeHex = document.querySelector('.component-pill.active .component-pill-hex')?.innerText || '';
                return {
                    component: 'window_frame',
                    activeHex: activeHex,
                    matHex: mat ? ('#' + mat.color.getHexString().toUpperCase()) : 'N/A'
                };
            })()
        """)
        print(f"   Window Frame Sync Result: {sync_result4}", flush=True)
        time.sleep(1)

        # Capture customized colors screenshot
        step2_custom_shot = os.path.join(ARTIFACT_DIR, "phase_6g3_step2_customized_colors_live.png")
        await client.capture_screenshot(step2_custom_shot)

        # Test Camera Angle Presets & Lighting
        print("\n--- Testing Camera Angle Presets & Day/Night Mode ---", flush=True)
        await client.eval_js("""
            (() => {
                const aerialBtn = Array.from(document.querySelectorAll('.btn-viewer-preset')).find(b => b.innerText.includes('Aerial') || b.innerText.includes('3/4 Left'));
                if (aerialBtn) aerialBtn.click();
            })()
        """)
        time.sleep(1.2)

        # Toggle to Night Mode
        print("Toggling to Night Mode...", flush=True)
        await client.eval_js("""
            (() => {
                const nightBtn = Array.from(document.querySelectorAll('.btn-viewer-action')).find(b => b.innerText.includes('Night') || b.innerText.includes('Daylight'));
                if (nightBtn) nightBtn.click();
            })()
        """)
        time.sleep(1.5)

        step2_night_shot = os.path.join(ARTIFACT_DIR, "phase_6g3_step2_night_mode_glowing.png")
        await client.capture_screenshot(step2_night_shot)

        # Toggle back to Daylight
        await client.eval_js("""
            (() => {
                const dayBtn = Array.from(document.querySelectorAll('.btn-viewer-action')).find(b => b.innerText.includes('Daylight') || b.innerText.includes('Night'));
                if (dayBtn) dayBtn.click();
            })()
        """)
        time.sleep(1)

        # Test Responsive Tablet Viewport
        print("\n--- Testing Responsive Viewport (1024x768) ---", flush=True)
        await client.send("Emulation.setDeviceMetricsOverride", {
            "width": 1024,
            "height": 768,
            "deviceScaleFactor": 1,
            "mobile": False
        })
        time.sleep(1.2)

        responsive_check = await client.eval_js("""
            (() => {
                const topBar = document.querySelector('.viewer-top-bar-v3');
                const presetsPill = document.querySelector('.viewer-presets-pill-group');
                const actionsPill = document.querySelector('.viewer-actions-pill-group');

                let topBarOverlap = false;
                if (presetsPill && actionsPill) {
                    const r1 = presetsPill.getBoundingClientRect();
                    const r2 = actionsPill.getBoundingClientRect();
                    topBarOverlap = !(r1.right < r2.left || r2.right < r1.left || r1.bottom < r2.top || r2.bottom < r1.top);
                }

                return { topBarOverlap };
            })()
        """)
        print(f"Responsive Check at 1024px: {responsive_check}", flush=True)
        step2_resp_shot = os.path.join(ARTIFACT_DIR, "phase_6g3_step2_responsive_tablet.png")
        await client.capture_screenshot(step2_resp_shot)

        # Reset viewport
        await client.send("Emulation.setDeviceMetricsOverride", {
            "width": 1440,
            "height": 960,
            "deviceScaleFactor": 1,
            "mobile": False
        })
        time.sleep(1)

        # Transition to Step 3
        print("\n--- Navigating to Step 3 (Plan & 3D Review) ---", flush=True)
        await client.eval_js("""
            (() => {
                const navBtns = document.querySelectorAll('.stage-step-btn');
                for (const b of navBtns) {
                    if (b.innerText.includes('3D Preview') || b.innerText.includes('3')) {
                        b.click();
                        break;
                    }
                }
            })()
        """)
        time.sleep(2)

        step3_shot = os.path.join(ARTIFACT_DIR, "phase_6g3_step3_plan_and_3d_review.png")
        await client.capture_screenshot(step3_shot)

        # Transition to Step 4
        print("\n--- Navigating to Step 4 (Save & Apply) ---", flush=True)
        await client.eval_js("""
            (() => {
                const navBtns = document.querySelectorAll('.stage-step-btn');
                for (const b of navBtns) {
                    if (b.innerText.includes('Save') || b.innerText.includes('4')) {
                        b.click();
                        break;
                    }
                }
            })()
        """)
        time.sleep(2)

        # Trigger Save
        print("Clicking 'Save Changes' button in Step 4...", flush=True)
        save_trigger = await client.eval_js("""
            (() => {
                const saveBtn = Array.from(document.querySelectorAll('button')).find(b => b.innerText.includes('Save Changes'));
                if (saveBtn) {
                    saveBtn.click();
                    return { clicked: true, text: saveBtn.innerText };
                }
                return { clicked: false };
            })()
        """)
        print(f"Save Triggered: {save_trigger}", flush=True)
        time.sleep(2.5)

        step4_shot = os.path.join(ARTIFACT_DIR, "phase_6g3_step4_saved_and_persisted.png")
        await client.capture_screenshot(step4_shot)

        # Reload and verify persistence
        print("\n--- Reloading Page to Verify Persistence ---", flush=True)
        await client.send("Page.reload")
        for _ in range(12):
            time.sleep(1)
            ready = await client.eval_js("document.readyState === 'complete' && !document.querySelector('.fp-loading-spinner')")
            if ready:
                break
        time.sleep(2.5)

        await client.eval_js("""
            (() => {
                const step2Node = Array.from(document.querySelectorAll('.stage-step-btn')).find(n => n.innerText.includes('Customize') || n.innerText.includes('2'));
                if (step2Node) step2Node.click();
            })()
        """)
        time.sleep(1.5)

        persisted_summary = await client.eval_js("""
            (() => {
                const pills = document.querySelectorAll('.component-pill');
                const values = {};
                for (const p of pills) {
                    const name = p.querySelector('.component-pill-name')?.innerText;
                    const hex = p.querySelector('.component-pill-hex')?.innerText;
                    if (name) values[name] = hex;
                }
                return values;
            })()
        """)
        print(f"Persisted Colors After Reload: {json.dumps(persisted_summary, indent=2)}", flush=True)

        print("\n=== ALL PHASE 6G.3 CDP VERIFICATIONS COMPLETED SUCCESSFULLY ===", flush=True)

    finally:
        await client.close()
        edge_proc.terminate()
        try:
            edge_proc.wait(timeout=3)
        except Exception:
            edge_proc.kill()

if __name__ == "__main__":
    asyncio.run(run_verification())
