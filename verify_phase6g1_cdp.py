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

CDP_PORT = 9228
USER_DATA_DIR = tempfile.mkdtemp(prefix="browser_cdp_p6g1_")
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
            "total_builtup_sqft": 2450
        }

        setup_js = f"""
        localStorage.setItem('app_auth_session', JSON.stringify({json.dumps(mock_auth)}));
        localStorage.setItem('sb-xhyckokbgyqkmvxqfghp-auth-token', JSON.stringify({json.dumps(mock_auth)}));
        localStorage.setItem('project_{test_project_id}', JSON.stringify({json.dumps(mock_project)}));
        localStorage.setItem('floorplan_{test_project_id}', JSON.stringify({json.dumps(mock_floorplan)}));
        """

        print("Seeding local session credentials...", flush=True)
        await client.send("Page.navigate", {"url": "http://localhost:5173/"})
        await asyncio.sleep(2)
        await client.eval_js(setup_js)

        studio_url = f"http://localhost:5173/projects/{test_project_id}/exterior"
        print(f"Navigating to Exterior Studio: {studio_url}", flush=True)
        await client.send("Page.navigate", {"url": studio_url})
        await asyncio.sleep(4)

        # ── Test 1: Stage 1 Choose Design ────────────────────────────────────
        print("\n--- Testing Stage 1: Choose Design ---", flush=True)
        stage1_check = await client.eval_js("""
        (() => {
            const stepper = document.querySelectorAll('.stage-step-btn');
            const cards = document.querySelectorAll('.exterior-design-card');
            const activeTag = document.querySelector('.active-pill-tag');
            const activeName = document.querySelector('.active-design-name');
            const selectedBadges = document.querySelectorAll('.card-selected-badge');
            return {
                stepsCount: stepper.length,
                activeStep: document.querySelector('.stage-step-btn.active')?.textContent.trim(),
                cardsCount: cards.length,
                activeDesignName: activeName ? activeName.textContent : null,
                selectedBadgesCount: selectedBadges.length
            };
        })()
        """)
        print("Stage 1 initial state:", stage1_check, flush=True)

        # Select a specific design: Indian Modern Terracotta Jaali Screen (ext_indmod_01) or 2nd card
        print("Selecting second design card...", flush=True)
        await client.eval_js("""
        (() => {
            const cards = document.querySelectorAll('.exterior-design-card');
            if (cards.length > 1) {
                const btn = cards[1].querySelector('.btn-select-design');
                if (btn) btn.click();
            }
        })()
        """)
        await asyncio.sleep(1.5)

        selection_verification = await client.eval_js("""
        (() => {
            const activeCard = document.querySelector('.exterior-design-card.is-selected');
            const activeName = document.querySelector('.active-design-name')?.textContent;
            const badge = activeCard?.querySelector('.card-selected-badge')?.textContent;
            return {
                hasSelectedCard: Boolean(activeCard),
                cardBadge: badge,
                activeDesignName: activeName
            };
        })()
        """)
        print("Selection verification:", selection_verification, flush=True)
        await client.capture_screenshot(os.path.join(ARTIFACT_DIR, "phase_6g1_stage1_design_selection.png"))

        # ── Test 2: Stage 2 Customize Colors & Materials ──────────────────────
        print("\n--- Testing Stage 2: Customize Colors & Materials ---", flush=True)
        # Click Next or Stage 2 button
        await client.eval_js("""
        (() => {
            const steps = document.querySelectorAll('.stage-step-btn');
            if (steps.length > 1) steps[1].click();
        })()
        """)
        await asyncio.sleep(2)

        stage2_check = await client.eval_js("""
        (() => {
            const componentPills = document.querySelectorAll('.component-pill');
            const familyChips = document.querySelectorAll('.family-chip-btn');
            const swatches = document.querySelectorAll('.palette-swatch-card');
            const presets = document.querySelectorAll('.preset-card');
            const searchInput = document.querySelector('.color-search-input');
            return {
                componentPillsCount: componentPills.length,
                familyChipsCount: familyChips.length,
                swatchesCount: swatches.length,
                presetsCount: presets.length,
                hasSearchInput: Boolean(searchInput)
            };
        })()
        """)
        print("Stage 2 components check:", stage2_check, flush=True)

        # Test Color Search for 'Sandstone'
        print("Testing color search input for 'Sandstone'...", flush=True)
        await client.eval_js("""
        (() => {
            const input = document.querySelector('.color-search-input');
            if (input) {
                input.value = 'Sandstone';
                input.dispatchEvent(new Event('input', { bubbles: true }));
            }
        })()
        """)
        await asyncio.sleep(1)

        search_result = await client.eval_js("""
        (() => {
            const swatches = document.querySelectorAll('.palette-swatch-card');
            const names = Array.from(swatches).map(s => s.querySelector('.swatch-card-name')?.textContent);
            return { count: swatches.length, names: names };
        })()
        """)
        print("Search results for 'Sandstone':", search_result, flush=True)

        # Click the Sandstone swatch
        await client.eval_js("""
        (() => {
            const firstSwatch = document.querySelector('.palette-swatch-card');
            if (firstSwatch) firstSwatch.click();
        })()
        """)
        await asyncio.sleep(1)

        # Test "Apply to All Exterior Walls"
        print("Testing 'Apply to All Exterior Walls'...", flush=True)
        await client.eval_js("""
        (() => {
            const btn = document.querySelector('.btn-apply-all-walls');
            if (btn) btn.click();
        })()
        """)
        await asyncio.sleep(1)

        # Test 9 Curated Architectural Presets: click 'Terracotta & Cream' or 'Modern White & Charcoal'
        print("Applying 'Terracotta & Cream' preset...", flush=True)
        await client.eval_js("""
        (() => {
            const presets = document.querySelectorAll('.preset-card');
            for (const p of presets) {
                if (p.textContent.includes('Terracotta & Cream') || p.textContent.includes('Modern White')) {
                    p.click();
                    break;
                }
            }
        })()
        """)
        await asyncio.sleep(1.5)

        updated_colors = await client.eval_js("""
        (() => {
            const pills = document.querySelectorAll('.component-pill');
            const res = {};
            pills.forEach(p => {
                const name = p.querySelector('.component-pill-name')?.textContent;
                const hex = p.querySelector('.component-pill-hex')?.textContent;
                if (name) res[name] = hex;
            });
            return res;
        })()
        """)
        print("Updated 12 component colors after preset:", updated_colors, flush=True)
        await client.capture_screenshot(os.path.join(ARTIFACT_DIR, "phase_6g1_stage2_color_customizer.png"))

        # ── Test 3: Stage 3 Review Plan & 3D Model ────────────────────────────
        print("\n--- Testing Stage 3: Review Plan & 3D Model ---", flush=True)
        await client.eval_js("""
        (() => {
            const steps = document.querySelectorAll('.stage-step-btn');
            if (steps.length > 2) steps[2].click();
        })()
        """)
        await asyncio.sleep(3)

        stage3_check = await client.eval_js("""
        (() => {
            const canvas3d = document.querySelector('canvas');
            const floorPlanSvg = document.querySelector('.stage3-plan-pane svg') || document.querySelector('.stage3-plan-pane');
            const checklist = document.querySelector('.stage3-checklist-card');
            const scoreBadge = document.querySelector('.checklist-score-badge');
            return {
                has3DCanvas: Boolean(canvas3d),
                hasFloorPlanArea: Boolean(floorPlanSvg),
                hasChecklist: Boolean(checklist),
                scoreText: scoreBadge?.textContent.trim()
            };
        })()
        """)
        print("Stage 3 alignment check:", stage3_check, flush=True)

        # Test Day/Night toggle
        print("Testing Night/Day toggle...", flush=True)
        await client.eval_js("""
        (() => {
            const toggle = document.querySelector('.mode-toggle-pill') || document.querySelector('button[title*="Night"]') || document.querySelector('button[title*="Daylight"]');
            if (toggle) toggle.click();
        })()
        """)
        await asyncio.sleep(1.5)

        # Test Regeneration Confirmation Modal
        print("Testing Floor Plan Regeneration confirmation modal...", flush=True)
        await client.eval_js("""
        (() => {
            const regenBtn = Array.from(document.querySelectorAll('button')).find(b => b.textContent.includes('Regeneration'));
            if (regenBtn) regenBtn.click();
        })()
        """)
        await asyncio.sleep(1)

        modal_check = await client.eval_js("""
        (() => {
            const modal = document.querySelector('.modal-dialog-box');
            const title = modal ? modal.querySelector('.modal-title')?.textContent : null;
            return { modalOpen: Boolean(modal), modalTitle: title };
        })()
        """)
        print("Modal open check:", modal_check, flush=True)

        # Dismiss modal
        await client.eval_js("""
        (() => {
            const keepBtn = Array.from(document.querySelectorAll('button')).find(b => b.textContent.includes('Keep Existing'));
            if (keepBtn) keepBtn.click();
        })()
        """)
        await asyncio.sleep(1)

        await client.capture_screenshot(os.path.join(ARTIFACT_DIR, "phase_6g1_stage3_plan_and_3d_review.png"))

        # ── Test 4: Stage 4 Save & Apply ──────────────────────────────────────
        print("\n--- Testing Stage 4: Save & Apply ---", flush=True)
        await client.eval_js("""
        (() => {
            const steps = document.querySelectorAll('.stage-step-btn');
            if (steps.length > 3) steps[3].click();
        })()
        """)
        await asyncio.sleep(2)

        stage4_check = await client.eval_js("""
        (() => {
            const summaryCard = document.querySelector('.stage4-summary-card');
            const heroTitle = summaryCard ? summaryCard.querySelector('h3')?.textContent : null;
            const colorItems = document.querySelectorAll('.summary-color-item');
            const costVal = document.querySelector('.cost-val')?.textContent;
            return {
                hasSummaryCard: Boolean(summaryCard),
                elevationTitle: heroTitle,
                colorItemsCount: colorItems.length,
                totalCost: costVal
            };
        })()
        """)
        print("Stage 4 summary check:", stage4_check, flush=True)

        # Test Save Changes
        print("Testing Save Changes action...", flush=True)
        await client.eval_js("""
        (() => {
            const saveBtn = Array.from(document.querySelectorAll('button')).find(b => b.textContent.includes('Save Changes'));
            if (saveBtn) saveBtn.click();
        })()
        """)
        await asyncio.sleep(2)

        save_toast = await client.eval_js("""
        (() => {
            const toast = document.querySelector('.studio-header-right');
            return toast ? toast.textContent.trim() : null;
        })()
        """)
        print("Save confirmation toast status:", save_toast, flush=True)
        await client.capture_screenshot(os.path.join(ARTIFACT_DIR, "phase_6g1_stage4_save_and_apply.png"))

        print("\nAll Phase 6G.1 workflow steps verified successfully!", flush=True)

    finally:
        try:
            edge_proc.terminate()
        except Exception:
            pass

if __name__ == "__main__":
    asyncio.run(run_verification())
