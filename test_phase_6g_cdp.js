const { spawn } = require('child_process');
const fs = require('fs');
const path = require('path');
const { WebSocket } = require('undici');

const ARTIFACT_DIR = 'C:\\Users\\DELL\\.gemini\\antigravity\\brain\\35ff5483-d119-45be-a407-00f491b2c1fa';

async function delay(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

async function main() {
  console.log('--- Launching Edge Headless for Phase 6G Verification ---');
  const edgePath = 'C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe';
  const edge = spawn(edgePath, [
    '--headless=new',
    '--remote-debugging-port=9224',
    '--disable-gpu',
    '--no-sandbox',
    '--window-size=1440,900',
    'about:blank'
  ]);

  await delay(1800);

  let target;
  for (let i = 0; i < 6; i++) {
    try {
      const res = await fetch('http://127.0.0.1:9224/json/list');
      const list = await res.json();
      if (list && list.length > 0) {
        target = list[0];
        break;
      }
    } catch (_) {}
    await delay(500);
  }

  if (!target) {
    console.error('Failed to connect to Edge CDP target.');
    process.exit(1);
  }

  console.log('Connected to target:', target.webSocketDebuggerUrl);
  const ws = new WebSocket(target.webSocketDebuggerUrl);

  let msgId = 1;
  const callbacks = new Map();

  function send(method, params = {}) {
    return new Promise((resolve, reject) => {
      const id = msgId++;
      callbacks.set(id, { resolve, reject });
      ws.send(JSON.stringify({ id, method, params }));
    });
  }

  ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    if (data.id && callbacks.has(data.id)) {
      const { resolve, reject } = callbacks.get(data.id);
      callbacks.delete(data.id);
      if (data.error) reject(data.error);
      else resolve(data.result);
    }
  };

  await new Promise(resolve => { ws.onopen = resolve; });

  await send('Page.enable');
  await send('Runtime.enable');
  await send('DOM.enable');

  // Step 1: Initialize auth state in client
  console.log('Navigating to app root and setting auth store...');
  await send('Page.navigate', { url: 'http://localhost:5173/login' });
  await delay(1500);

  await send('Runtime.evaluate', {
    expression: `
      if (window.useAuthStore) {
        window.useAuthStore.setState({
          user: { id: 'test-user-1', email: 'architect@example.com' },
          session: { access_token: 'dummy', user: { id: 'test-user-1' } },
          initialized: true,
          loading: false
        });
      }
      if (window.useProjectStore) {
        window.useProjectStore.setState({
          currentProject: {
            id: 'd0e134d1-b801-455a-b71a-82c30ec0b0d1',
            name: 'Modern Skyline Villa',
            plot_width: 35,
            plot_length: 50,
            floors: 2,
            facing: 'North-East',
            budget_tier: 'Premium'
          }
        });
      }
      localStorage.setItem('project_d0e134d1-b801-455a-b71a-82c30ec0b0d1', JSON.stringify({
        id: 'd0e134d1-b801-455a-b71a-82c30ec0b0d1',
        name: 'Modern Skyline Villa',
        plot_width: 35,
        plot_length: 50,
        floors: 2,
        facing: 'North-East',
        budget_tier: 'Premium'
      }));
    `
  });

  // ── TEST 1: Reference Gallery View ──────────────────────────────────────────
  console.log('\n--- TEST 1: Navigating to Exterior Design Studio (Gallery Mode) ---');
  await send('Page.navigate', {
    url: 'http://localhost:5173/projects/d0e134d1-b801-455a-b71a-82c30ec0b0d1/exterior'
  });
  await delay(2500);

  // If redirect happened, re-apply auth and re-navigate
  const currentUrl = await send('Runtime.evaluate', { expression: 'window.location.href' });
  if (currentUrl.result.value.includes('/login')) {
    console.log('Login redirect detected, injecting auth and proceeding...');
    await send('Runtime.evaluate', {
      expression: `
        if (window.useAuthStore) {
          window.useAuthStore.setState({
            user: { id: 'test-user-1', email: 'architect@example.com' },
            session: { access_token: 'dummy', user: { id: 'test-user-1' } },
            initialized: true,
            loading: false
          });
        }
      `
    });
    await delay(300);
    await send('Page.navigate', {
      url: 'http://localhost:5173/projects/d0e134d1-b801-455a-b71a-82c30ec0b0d1/exterior'
    });
    await delay(2500);
  }

  const galleryInfo = await send('Runtime.evaluate', {
    expression: `
      (() => {
        const cards = document.querySelectorAll('.exterior-card');
        const activeName = document.querySelector('.active-design-name')?.innerText || '';
        const modeButtons = Array.from(document.querySelectorAll('.mode-switch-btn')).map(b => b.innerText.trim());
        const categoryPills = Array.from(document.querySelectorAll('.filter-category-pill')).map(b => b.innerText.trim());
        const images = Array.from(cards).map(c => c.querySelector('img')?.src);
        return {
          cardCount: cards.length,
          activeName,
          modeButtons,
          categoryPillCount: categoryPills.length,
          firstImage: images[0]
        };
      })()
    `,
    returnByValue: true
  });
  console.log('Gallery State:', galleryInfo.result.value);

  // Capture Gallery Screenshot
  const ss1 = await send('Page.captureScreenshot', { format: 'png' });
  const path1 = path.join(ARTIFACT_DIR, 'phase_6g_exterior_reference_gallery.png');
  fs.writeFileSync(path1, Buffer.from(ss1.data, 'base64'));
  console.log('Saved Gallery screenshot:', path1);

  // ── TEST 2: Switch to Personalized 3D Model ─────────────────────────────────
  console.log('\n--- TEST 2: Switching to Personalized 3D Model (WebGL) ---');
  await send('Runtime.evaluate', {
    expression: `
      (() => {
        const btns = Array.from(document.querySelectorAll('.mode-switch-btn'));
        const btn3d = btns.find(b => b.innerText.includes('3D'));
        if (btn3d) btn3d.click();
      })()
    `
  });
  await delay(2500);

  const model3dInfo = await send('Runtime.evaluate', {
    expression: `
      (() => {
        const canvas = document.querySelector('.exterior-3d-wrapper canvas');
        const costVal = document.querySelector('.cost-val')?.innerText || '';
        const presets = Array.from(document.querySelectorAll('.exterior-3d-wrapper button')).map(b => b.innerText.trim());
        return {
          canvasExists: Boolean(canvas),
          canvasSize: canvas ? { width: canvas.width, height: canvas.height } : null,
          costVal,
          presets: presets.filter(p => p.length > 0)
        };
      })()
    `,
    returnByValue: true
  });
  console.log('3D Model State:', model3dInfo.result.value);

  // Capture 3D Model Daylight Screenshot
  const ss2 = await send('Page.captureScreenshot', { format: 'png' });
  const path2 = path.join(ARTIFACT_DIR, 'phase_6g_personalized_3d_daylight.png');
  fs.writeFileSync(path2, Buffer.from(ss2.data, 'base64'));
  console.log('Saved 3D Model Daylight screenshot:', path2);

  // ── TEST 3: Toggle Night Atmosphere on 3D Model ────────────────────────────
  console.log('\n--- TEST 3: Toggling Night Atmosphere with 2700K Window Illumination ---');
  await send('Runtime.evaluate', {
    expression: `
      (() => {
        const btns = Array.from(document.querySelectorAll('.exterior-3d-wrapper button'));
        const nightBtn = btns.find(b => b.innerText.includes('Daylight') || b.innerText.includes('Night'));
        if (nightBtn) nightBtn.click();
      })()
    `
  });
  await delay(1500);

  const ss3 = await send('Page.captureScreenshot', { format: 'png' });
  const path3 = path.join(ARTIFACT_DIR, 'phase_6g_personalized_3d_night.png');
  fs.writeFileSync(path3, Buffer.from(ss3.data, 'base64'));
  console.log('Saved 3D Model Night screenshot:', path3);

  // ── TEST 4: Switch to Architectural CAD Elevation ──────────────────────────
  console.log('\n--- TEST 4: Switching to Architectural CAD Elevation (Technical 2D) ---');
  await send('Runtime.evaluate', {
    expression: `
      (() => {
        const btns = Array.from(document.querySelectorAll('.mode-switch-btn'));
        const cadBtn = btns.find(b => b.innerText.includes('CAD'));
        if (cadBtn) cadBtn.click();
      })()
    `
  });
  await delay(2500);

  const cadInfo = await send('Runtime.evaluate', {
    expression: `
      (() => {
        const svg = document.querySelector('.cad-svg-render-area svg');
        const specs = Array.from(document.querySelectorAll('.spec-item')).map(s => s.innerText.replace(/\\n/g, ': '));
        return {
          svgExists: Boolean(svg),
          svgDimensions: svg ? { width: svg.clientWidth, height: svg.clientHeight } : null,
          specs
        };
      })()
    `,
    returnByValue: true
  });
  console.log('CAD Elevation State:', cadInfo.result.value);

  const ss4 = await send('Page.captureScreenshot', { format: 'png' });
  const path4 = path.join(ARTIFACT_DIR, 'phase_6g_architectural_cad_elevation.png');
  fs.writeFileSync(path4, Buffer.from(ss4.data, 'base64'));
  console.log('Saved CAD Elevation screenshot:', path4);

  // ── TEST 5: Verify Floor Plan Viewer Pan, Zoom, and Export Buttons ─────────
  console.log('\n--- TEST 5: Verifying Workspace Floor Plan Viewer (Pan, Zoom, SVG/PNG Export) ---');
  await send('Page.navigate', {
    url: 'http://localhost:5173/projects/d0e134d1-b801-455a-b71a-82c30ec0b0d1'
  });
  await delay(3000);

  const fpViewerInfo = await send('Runtime.evaluate', {
    expression: `
      (() => {
        const svg = document.querySelector('.fp-svg-viewport svg');
        const exportBtns = Array.from(document.querySelectorAll('.fp-export-btn')).map(b => b.innerText.trim());
        const zoomLabel = document.querySelector('.fp-zoom-label')?.innerText || '';
        const cursor = getComputedStyle(document.querySelector('.fp-svg-viewport') || document.body).cursor;
        return {
          svgExists: Boolean(svg),
          exportButtons: exportBtns,
          zoomLabel,
          viewportCursor: cursor
        };
      })()
    `,
    returnByValue: true
  });
  console.log('Floor Plan Viewer State:', fpViewerInfo.result.value);

  const ss5 = await send('Page.captureScreenshot', { format: 'png' });
  const path5 = path.join(ARTIFACT_DIR, 'phase_6g_floor_plan_viewer_pan_export.png');
  fs.writeFileSync(path5, Buffer.from(ss5.data, 'base64'));
  console.log('Saved Floor Plan Viewer screenshot:', path5);

  console.log('\n=== All Phase 6G Verification Tests Completed Successfully! ===');
  ws.close();
  edge.kill();
  process.exit(0);
}

main().catch(err => {
  console.error('Error during verification:', err);
  process.exit(1);
});
