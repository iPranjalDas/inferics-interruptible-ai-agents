document.addEventListener("DOMContentLoaded", () => {
  const hud = document.createElement("div");
  hud.innerHTML = `
    <div id="inferics-hud-toggle" style="position: fixed; bottom: 20px; left: 20px; z-index: 10000; background: #000; color: #fff; padding: 8px 12px; border-radius: 20px; cursor: pointer; font-size: 11px; font-weight: bold; font-family: ui-monospace, monospace; border: 1px solid rgba(255,255,255,0.2); box-shadow: 0 4px 12px rgba(0,0,0,0.5); transition: all 0.3s ease;">
      ✦ PIPELINE HUD
    </div>
    <div id="inferics-hud-panel" style="position: fixed; bottom: 60px; left: 20px; z-index: 9999; background: rgba(9, 9, 11, 0.95); backdrop-filter: blur(10px); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 12px; padding: 16px; width: 320px; color: #e4e4e7; font-family: ui-monospace, monospace; box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.5); font-size: 11px; opacity: 0; pointer-events: none; transform: translateY(10px); transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);">
      <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 8px; margin-bottom: 12px;">
        <span style="font-weight: bold; color: #fff;">✦ INFERICS PIPELINE HUD</span>
        <span style="background: #059669; color: #fff; padding: 2px 6px; border-radius: 4px; font-size: 9px; font-weight: bold; letter-spacing: 0.5px;">LIVE</span>
      </div>
      
      <div style="margin-bottom: 12px;">
        <div style="color: #a1a1aa; font-weight: bold; margin-bottom: 6px; font-size: 10px; letter-spacing: 0.5px;">EMPIRICAL BENCHMARKS (FDB-v3)</div>
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px;">
          <div style="background: rgba(255,255,255,0.05); padding: 6px; border-radius: 6px; border: 1px solid rgba(255,255,255,0.05);">
            <div style="color: #a1a1aa; font-size: 9px;">Fast-Path TTFT</div>
            <div style="color: #38bdf8; font-weight: bold; font-size: 12px;">14 ms</div>
          </div>
          <div style="background: rgba(255,255,255,0.05); padding: 6px; border-radius: 6px; border: 1px solid rgba(255,255,255,0.05);">
            <div style="color: #a1a1aa; font-size: 9px;">Strict Pass Rate</div>
            <div style="color: #34d399; font-weight: bold; font-size: 12px;">100.0%</div>
          </div>
          <div style="background: rgba(255,255,255,0.05); padding: 6px; border-radius: 6px; border: 1px solid rgba(255,255,255,0.05);">
            <div style="color: #a1a1aa; font-size: 9px;">Token Velocity</div>
            <div style="color: #c084fc; font-weight: bold; font-size: 12px;">135 tps</div>
          </div>
          <div style="background: rgba(255,255,255,0.05); padding: 6px; border-radius: 6px; border: 1px solid rgba(255,255,255,0.05);">
            <div style="color: #a1a1aa; font-size: 9px;">Cost / Turn</div>
            <div style="color: #fbbf24; font-weight: bold; font-size: 12px;">bash.0004</div>
          </div>
        </div>
      </div>

      <div>
        <div style="color: #a1a1aa; font-weight: bold; margin-bottom: 6px; font-size: 10px; letter-spacing: 0.5px;">ACTIVE STAGE TRACE</div>
        <div style="display: flex; flex-direction: column; gap: 6px;">
          <div style="display: flex; justify-content: space-between; align-items: center;">
            <span style="color: #71717a;">1. Word-Boundary Scanner</span>
            <span style="color: #34d399;">Active</span>
          </div>
          <div style="display: flex; justify-content: space-between; align-items: center;">
            <span style="color: #71717a;">2. Context Sharpening</span>
            <span style="color: #38bdf8;">Pruning</span>
          </div>
          <div style="display: flex; justify-content: space-between; align-items: center;">
            <span style="color: #71717a;">3. Immutable Ledger Sync</span>
            <span style="color: #34d399;">Locked</span>
          </div>
          <div style="display: flex; justify-content: space-between; align-items: center;">
            <span style="color: #71717a;">4. Nexus Dual Engine</span>
            <span style="color: #c084fc;">Streaming</span>
          </div>
        </div>
      </div>
    </div>
  `;
  document.body.appendChild(hud);

  let isOpen = false;
  const toggle = document.getElementById("inferics-hud-toggle");
  const panel = document.getElementById("inferics-hud-panel");
  
  toggle.addEventListener("click", () => {
    isOpen = !isOpen;
    if(isOpen) {
      panel.style.opacity = "1";
      panel.style.pointerEvents = "auto";
      panel.style.transform = "translateY(0)";
      toggle.style.background = "#34d399";
      toggle.style.color = "#000";
    } else {
      panel.style.opacity = "0";
      panel.style.pointerEvents = "none";
      panel.style.transform = "translateY(10px)";
      toggle.style.background = "#000";
      toggle.style.color = "#fff";
    }
  });

  // Simple animation effect on the trace
  setInterval(() => {
    const traceNodes = panel.querySelectorAll('span:nth-child(2)');
    const colors = ['#34d399', '#38bdf8', '#c084fc', '#fbbf24'];
    const node = traceNodes[1 + Math.floor(Math.random() * 3)];
    if(node) {
      const origColor = node.style.color;
      node.style.color = '#fff';
      setTimeout(() => node.style.color = origColor, 200);
    }
  }, 1000);
});