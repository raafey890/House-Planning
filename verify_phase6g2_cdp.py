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

CDP_PORT = 9229
USER_DATA_DIR = tempfile.mkdtemp(prefix="browser_cdp_p6g2_")
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
        await asyncio.sleep(2)
        await client.eval_js(setup_js)

        test_url = f"http://localhost:5173/projects/{test_project_id}/exterior"
        print(f"Navigating to {test_url}...", flush=True)
        await client.send("Page.navigate", {"url": test_url})

        # Wait for page load
        await asyncio.sleep(4)

        title = await client.eval_js("document.title")
        print(f"Page title: {title}", flush=True)

        # -------------------------------------------------------------
        # STEP 1: Verify Gallery & Step 1 Selection Confirmation Modal
        # -------------------------------------------------------------
        print("\n--- STEP 1: Verifying Design Selection & Confirmation Modal ---", flush=True)
        card_count = 0
        for _ in range(15):
            card_count = await client.eval_js("document.querySelectorAll('.exterior-card, .exterior-design-card').length") or 0
            if card_count >= 32:
                break
            time.sleep(1)
        print(f"Found {card_count} exterior design cards in catalog gallery.", flush=True)
        assert card_count >= 32, f"Expected at least 32 cards, found {card_count}"

        # Click the first design card to select it and trigger the Step 1 confirmation modal
        click_res = await client.eval_js("""
            (() => {
                const card = document.querySelector('.exterior-card, .exterior-design-card');
                if (!card) return 'No card found';
                card.click();
                return 'Clicked card';
            })()
        """)
        print(f"Card click result: {click_res}", flush=True)
        time.sleep(1)

        # Verify Step 1 modal is visible
        modal_visible = await client.eval_js("""
            (() => {
                const modal = document.querySelector('.step1-selection-modal');
                if (!modal) return { visible: false };
                const title = modal.querySelector('h2')?.innerText;
                const badges = Array.from(modal.querySelectorAll('.config-badge')).map(b => b.innerText);
                const steps = Array.from(modal.querySelectorAll('.wizard-step')).map(s => s.innerText.trim());
                const btns = Array.from(modal.querySelectorAll('button')).map(b => b.innerText.trim());
                return {
                    visible: true,
                    title,
                    badges,
                    steps,
                    btns
                };
            })()
        """)
        print(f"Step 1 Selection Modal Info: {json.dumps(modal_visible, indent=2)}", flush=True)
        assert modal_visible["visible"], "Step 1 selection modal must be visible after card click"
        assert len(modal_visible["badges"]) >= 3, "Expected project configuration badges"

        # Capture Screenshot of Step 1 Selection Modal
        step1_ss_path = os.path.join(ARTIFACT_DIR, "phase_6g2_step1_selection_modal.png")
        await client.capture_screenshot(step1_ss_path)

        # Test "Back to Gallery" button functionality
        back_click = await client.eval_js("""
            (() => {
                const backBtn = Array.from(document.querySelectorAll('.step1-selection-modal button'))
                    .find(b => b.innerText.includes('Back to Gallery'));
                if (!backBtn) return false;
                backBtn.click();
                return true;
            })()
        """)
        print(f"Clicked 'Back to Gallery': {back_click}", flush=True)
        time.sleep(0.5)

        modal_dismissed = await client.eval_js("document.querySelector('.step1-selection-modal') === null")
        print(f"Modal dismissed after 'Back to Gallery': {modal_dismissed}", flush=True)
        assert modal_dismissed, "Modal should close on 'Back to Gallery'"

        # Click card again and click "Continue to Customize"
        await client.eval_js("document.querySelector('.exterior-card, .exterior-design-card').click();")
        time.sleep(0.5)

        cont_click = await client.eval_js("""
            (() => {
                const contBtn = Array.from(document.querySelectorAll('.step1-selection-modal button'))
                    .find(b => b.innerText.includes('Continue to Customize'));
                if (!contBtn) return false;
                contBtn.click();
                return true;
            })()
        """)
        print(f"Clicked 'Continue to Customize': {cont_click}", flush=True)
        time.sleep(1)

        # -------------------------------------------------------------
        # STEP 2: Verify Two-Column Desktop Customization Experience
        # -------------------------------------------------------------
        print("\n--- STEP 2: Verifying Two-Column Customizer & Interactive Tools ---", flush=True)
        step2_info = await client.eval_js("""
            (() => {
                const layout = document.querySelector('.stage2-two-column-layout');
                const leftPanel = document.querySelector('.stage2-left-panel');
                const rightPanel = document.querySelector('.stage2-right-panel');
                const summaryTable = document.querySelector('.stage2-summary-table');
                const summaryRows = document.querySelectorAll('.stage2-summary-table .stage2-table-row').length;
                const toolbarBtns = Array.from(document.querySelectorAll('.stage2-actions-toolbar button')).map(b => b.innerText.trim());
                const componentPills = document.querySelectorAll('.component-pill').length;
                const searchInput = document.querySelector('input.color-search-input');
                const familyChips = document.querySelectorAll('.family-chip-btn').length;
                const swatches = document.querySelectorAll('.palette-swatch-card').length;
                const presets = document.querySelectorAll('.preset-card').length;
                const finishes = document.querySelectorAll('.sidebar-select option').length;
                return {
                    hasLayout: !!layout,
                    hasLeftPanel: !!leftPanel,
                    hasRightPanel: !!rightPanel,
                    hasSummaryTable: !!summaryTable,
                    summaryRows,
                    toolbarBtns,
                    componentPills,
                    hasSearchInput: !!searchInput,
                    familyChips,
                    swatches,
                    presets,
                    finishes
                };
            })()
        """)
        print(f"Step 2 Customizer Verification: {json.dumps(step2_info, indent=2)}", flush=True)
        assert step2_info["hasLayout"], "Desktop two-column layout must be rendered"
        assert step2_info["summaryRows"] == 12, f"Expected 12 component summary rows, got {step2_info['summaryRows']}"
        assert step2_info["componentPills"] == 12, f"Expected 12 component pills, got {step2_info['componentPills']}"
        assert step2_info["hasSearchInput"], "Color search input must be present"
        assert step2_info["familyChips"] >= 10, "Expected at least 10 color family chips"
        assert step2_info["presets"] == 9, f"Expected 9 curated presets, got {step2_info['presets']}"
        assert step2_info["finishes"] >= 8, f"Expected at least 8 material finish options, got {step2_info['finishes']}"

        # Test Search Palette
        search_test = await client.eval_js("""
            (() => {
                const input = document.querySelector('input.color-search-input');
                if (!input) return { ok: false };
                const setter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
                setter.call(input, "Terracotta");
                input.dispatchEvent(new Event('input', { bubbles: true }));
                const visibleSwatches = document.querySelectorAll('.palette-swatch-card').length;
                return { ok: true, visibleSwatches };
            })()
        """)
        print(f"Search for 'Terracotta' returned {search_test.get('visibleSwatches')} swatches", flush=True)
        assert search_test["visibleSwatches"] >= 1 and search_test["visibleSwatches"] < 68, "Should filter swatches when searching"

        # Clear search
        await client.eval_js("""
            (() => {
                const input = document.querySelector('input.color-search-input');
                if (!input) return;
                const setter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
                setter.call(input, "");
                input.dispatchEvent(new Event('input', { bubbles: true }));
            })()
        """)
        time.sleep(0.5)

        # Test Custom HEX Validation Error Display
        hex_val_test = await client.eval_js("""
            (() => {
                const input = document.querySelector('.hex-field');
                if (!input) return { found: false };
                const setter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
                setter.call(input, "XYZ123");
                input.dispatchEvent(new Event('input', { bubbles: true }));
                const errorMsg = document.querySelector('.hex-validation-message')?.innerText;
                return { found: true, errorMsg };
            })()
        """)
        print(f"Custom HEX validation test: {hex_val_test}", flush=True)
        assert hex_val_test.get("errorMsg") and "valid 3 or 6 digit HEX" in hex_val_test["errorMsg"], \
            "Expected helpful validation error message for invalid HEX code"

        # Test Apply to All Exterior Walls
        apply_walls_test = await client.eval_js("""
            (() => {
                const btn = Array.from(document.querySelectorAll('button')).find(b => b.innerText.includes('Apply to All Exterior Walls'));
                if (!btn) return { found: false };
                btn.click();
                return { found: true };
            })()
        """)
        print(f"Apply to All Exterior Walls clicked: {apply_walls_test}", flush=True)
        time.sleep(0.5)

        # Test Undo Last Change
        undo_test = await client.eval_js("""
            (() => {
                const undoBtn = Array.from(document.querySelectorAll('.stage2-actions-toolbar button')).find(b => b.innerText.includes('Undo'));
                if (!undoBtn) return { found: false };
                const disabledBefore = undoBtn.disabled;
                undoBtn.click();
                return { found: true, wasDisabled: disabledBefore };
            })()
        """)
        print(f"Undo action test: {undo_test}", flush=True)

        # Capture Screenshot of Step 2 Two-Column Customizer
        step2_ss_path = os.path.join(ARTIFACT_DIR, "phase_6g2_step2_two_column_customizer.png")
        await client.capture_screenshot(step2_ss_path)

        # Navigate to Step 3
        nav_step3 = await client.eval_js("""
            (() => {
                const btn = Array.from(document.querySelectorAll('button')).find(b => b.innerText.includes('Continue to 3D Preview'));
                if (!btn) return false;
                btn.click();
                return true;
            })()
        """)
        print(f"Navigating to Step 3 (3D Preview): {nav_step3}", flush=True)
        time.sleep(2)

        # -------------------------------------------------------------
        # STEP 3: Verify 3D Preview & Plan Comparison
        # -------------------------------------------------------------
        print("\n--- STEP 3: Verifying 3D House Preview & Architectural Plan Comparison ---", flush=True)
        step3_info = await client.eval_js("""
            (() => {
                const layout = document.querySelector('.stage3-dedicated-layout');
                const comparisonRow = document.querySelector('.stage3-comparison-row');
                const refCard = document.querySelector('.stage3-ref-side-card');
                const viewerCard = document.querySelector('.stage3-viewer-side-card');
                const canvas = document.querySelector('.exterior-3d-wrapper canvas');
                const resetCamBtn = document.querySelector('button[title*="Reset Camera"]');
                const dayNightToggle = Array.from(document.querySelectorAll('.exterior-3d-wrapper button')).find(b => b.innerText.includes('Night') || b.innerText.includes('Day'));
                const turntableBtn = document.querySelector('button[title*="Auto-rotate"]');
                const planCard = document.querySelector('.stage3-plan-summary-card');
                const guaranteeAlert = Array.from(document.querySelectorAll('.rule-guarantee-note')).find(el => el.innerText.includes('Plan Protection Guarantee'));
                const blueprintBtn = Array.from(document.querySelectorAll('.stage3-plan-summary-card button')).find(b => b.innerText.includes('Blueprint'));
                return {
                    hasLayout: !!layout,
                    hasComparisonRow: !!comparisonRow,
                    hasRefCard: !!refCard,
                    hasViewerCard: !!viewerCard,
                    hasCanvas: !!canvas,
                    hasResetCamBtn: !!resetCamBtn,
                    hasDayNightToggle: !!dayNightToggle,
                    hasTurntableBtn: !!turntableBtn,
                    hasPlanCard: !!planCard,
                    hasGuaranteeAlert: !!guaranteeAlert,
                    hasBlueprintBtn: !!blueprintBtn,
                    guaranteeText: guaranteeAlert?.innerText
                };
            })()
        """)
        print(f"Step 3 Verification: {json.dumps(step3_info, indent=2)}", flush=True)
        assert step3_info["hasLayout"], "Step 3 dedicated layout must be present"
        assert step3_info["hasRefCard"], "Selected Exterior Reference card must be present"
        assert step3_info["hasViewerCard"], "Personalized 3D House Preview card must be present"
        assert step3_info["hasCanvas"], "Three.js WebGL canvas must be rendered"
        assert step3_info["hasResetCamBtn"], "Dedicated Reset Camera button must be present"
        assert step3_info["hasGuaranteeAlert"], "Strict Floor Plan Preservation notice must be present"

        # Test Blueprint toggle
        blueprint_toggle = await client.eval_js("""
            (() => {
                const btn = Array.from(document.querySelectorAll('.stage3-plan-summary-card button')).find(b => b.innerText.includes('Blueprint'));
                if (!btn) return false;
                btn.click();
                return true;
            })()
        """)
        print(f"CAD Blueprint expanded: {blueprint_toggle}", flush=True)
        time.sleep(1)

        # Capture Screenshot of Step 3 3D Comparison Preview
        step3_ss_path = os.path.join(ARTIFACT_DIR, "phase_6g2_step3_3d_comparison_preview.png")
        await client.capture_screenshot(step3_ss_path)

        # Navigate to Step 4
        nav_step4 = await client.eval_js("""
            (() => {
                const btn = Array.from(document.querySelectorAll('button')).find(b => b.innerText.includes('Save & Apply Exterior'));
                if (!btn) return false;
                btn.click();
                return true;
            })()
        """)
        print(f"Navigating to Step 4 (Save & Apply): {nav_step4}", flush=True)
        time.sleep(1.5)

        # -------------------------------------------------------------
        # STEP 4: Verify Save & Apply Review, Baseline Protection & Toast
        # -------------------------------------------------------------
        print("\n--- STEP 4: Verifying Summary Review, Civil Baseline Protection & Save ---", flush=True)
        step4_info = await client.eval_js("""
            (() => {
                const summaryCard = document.querySelector('.stage4-summary-card');
                const baselineNote = document.querySelector('.cost-note');
                const saveBtn = Array.from(document.querySelectorAll('button')).find(b => b.innerText.includes('Save & Apply to Project'));
                const costNumber = document.querySelector('.cost-val')?.innerText;
                return {
                    hasSummaryCard: !!summaryCard,
                    hasBaselineNote: !!baselineNote,
                    baselineText: baselineNote?.innerText,
                    hasSaveBtn: !!saveBtn,
                    costNumber
                };
            })()
        """)
        print(f"Step 4 Review Info: {json.dumps(step4_info, indent=2)}", flush=True)
        assert step4_info["hasSummaryCard"], "Summary review card must be present"
        assert step4_info["hasBaselineNote"], "Civil baseline protection note must be present"
        assert "Baseline RCC structural framing" in step4_info["baselineText"] or "Civil Baseline Protection" in step4_info["baselineText"], \
            "Must explicitly protect civil baseline costs"

        # Capture Screenshot of Step 4 Save & Apply Review
        step4_ss_path = os.path.join(ARTIFACT_DIR, "phase_6g2_step4_save_and_apply.png")
        await client.capture_screenshot(step4_ss_path)

        # Execute Save
        save_exec = await client.eval_js("""
            (() => {
                const saveBtn = Array.from(document.querySelectorAll('button')).find(b => b.innerText.includes('Save & Apply to Project'));
                if (!saveBtn) return { found: false };
                saveBtn.click();
                return { found: true };
            })()
        """)
        print(f"Save button clicked: {save_exec}", flush=True)

        # Check for success toast
        toast_info = None
        for _ in range(10):
            time.sleep(0.2)
            toast_info = await client.eval_js("""
                (() => {
                    const headerRight = document.querySelector('.studio-header-right');
                    return {
                        visible: !!headerRight && headerRight.innerText.includes('Saved to Project'),
                        text: headerRight?.innerText
                    };
                })()
            """)
            if toast_info and toast_info.get("visible"):
                break

        print(f"Toast notification result: {toast_info}", flush=True)
        assert toast_info and toast_info["visible"] and "Saved to Project" in toast_info["text"], \
            "Expected 'Saved to Project' success toast notification"

        # Verify navigation to /projects/:id
        time.sleep(2.0)
        curr_url = await client.eval_js("window.location.pathname")
        print(f"Post-save current path: {curr_url}", flush=True)
        assert curr_url == f"/projects/{test_project_id}", f"Expected redirect to /projects/{test_project_id}, got {curr_url}"

        print("\n=== ALL PHASE 6G.2 VERIFICATION CHECKS PASSED SUCCESSFULLY! ===", flush=True)

    finally:
        await client.close()
        edge_proc.kill()

if __name__ == "__main__":
    asyncio.run(run_verification())
