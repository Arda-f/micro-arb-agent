from __future__ import annotations


def render_dashboard() -> str:
    return """
<!doctype html>
<html lang="tr">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>Mikro-Arbitraj Ajanı</title>
    <style>
      @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=DM+Serif+Display&display=swap');
      :root {
        --bg: #0c0f14;
        --bg-soft: #141824;
        --accent: #f4d06f;
        --accent-2: #94f0ff;
        --ink: #f7f7f2;
        --muted: #9aa4b2;
        --danger: #ff8c8c;
      }
      * { box-sizing: border-box; }
      body {
        margin: 0;
        font-family: "Space Grotesk", system-ui, sans-serif;
        background: radial-gradient(circle at 10% 20%, #1a2240 0%, #0c0f14 55%);
        color: var(--ink);
      }
      .shell {
        min-height: 100vh;
        display: grid;
        grid-template-columns: minmax(260px, 1fr) 2.2fr;
        gap: 24px;
        padding: 32px;
      }
      .panel {
        background: var(--bg-soft);
        border: 1px solid rgba(244, 208, 111, 0.15);
        border-radius: 18px;
        padding: 22px;
        box-shadow: 0 30px 80px rgba(0,0,0,0.35);
      }
      .title {
        font-family: "DM Serif Display", serif;
        font-size: clamp(28px, 3vw, 40px);
        letter-spacing: 0.5px;
        margin: 0 0 12px;
      }
      .subtitle {
        color: var(--muted);
        margin: 0 0 18px;
      }
      .grid {
        display: grid;
        gap: 16px;
      }
      .stat {
        background: rgba(255,255,255,0.02);
        border: 1px solid rgba(148,240,255,0.12);
        border-radius: 16px;
        padding: 16px;
      }
      .stat h4 {
        margin: 0 0 8px;
        font-size: 12px;
        letter-spacing: 1.2px;
        text-transform: uppercase;
        color: var(--muted);
      }
      .stat strong {
        font-size: 24px;
        color: var(--accent-2);
      }
      .cta {
        display: flex;
        gap: 12px;
        margin-top: 18px;
      }
      button {
        background: var(--accent);
        color: #1a1a1a;
        border: none;
        border-radius: 999px;
        padding: 10px 18px;
        font-weight: 600;
        cursor: pointer;
        transition: transform 160ms ease, box-shadow 160ms ease;
      }
      button:hover { transform: translateY(-1px); box-shadow: 0 10px 30px rgba(244,208,111,0.2); }
      button.secondary {
        background: transparent;
        color: var(--ink);
        border: 1px solid rgba(244, 208, 111, 0.35);
      }
      table {
        width: 100%;
        border-collapse: collapse;
        font-size: 14px;
      }
      th, td {
        text-align: left;
        padding: 12px 8px;
        border-bottom: 1px solid rgba(255,255,255,0.07);
      }
      th {
        color: var(--muted);
        font-weight: 500;
      }
      .profit {
        color: var(--accent);
        font-weight: 600;
      }
      .log {
        font-size: 12px;
        color: var(--muted);
        line-height: 1.5;
      }
      .status {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        font-size: 13px;
        color: var(--muted);
      }
      .pulse {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: var(--accent-2);
        box-shadow: 0 0 12px rgba(148,240,255,0.6);
      }
      @media (max-width: 980px) {
        .shell {
          grid-template-columns: 1fr;
        }
      }
    </style>
  </head>
  <body>
    <div class="shell">
      <section class="panel">
        <h1 class="title">Mikro‑Arbitraj Ajanı</h1>
        <p class="subtitle">5 markette düşük riskli dijital varlıkları tarar, fırsatları sıralar.</p>
        <div class="grid">
          <div class="stat">
            <h4>Tarama Durumu</h4>
            <div class="status"><span class="pulse" id="pulse"></span><span id="statusText">-</span></div>
          </div>
          <div class="stat">
            <h4>Son Tarama</h4>
            <strong id="lastScan">-</strong>
          </div>
          <div class="stat">
            <h4>Aktif Fırsat</h4>
            <strong id="oppCount">-</strong>
          </div>
        </div>
        <div class="cta">
          <button onclick="toggleBot(true)">Başlat</button>
          <button class="secondary" onclick="toggleBot(false)">Durdur</button>
        </div>
        <div class="stat" style="margin-top:18px;">
          <h4>İşlem Günlüğü</h4>
          <div id="logs" class="log"></div>
        </div>
      </section>
      <section class="panel">
        <h2 class="title" style="font-size: clamp(22px, 2.6vw, 32px);">Fırsat Akışı</h2>
        <table>
          <thead>
            <tr>
              <th>Varlık</th>
              <th>Alış</th>
              <th>Satış</th>
              <th>Kâr (ETH)</th>
              <th>Zaman</th>
            </tr>
          </thead>
          <tbody id="opps"></tbody>
        </table>
      </section>
    </div>
    <script>
      async function toggleBot(value) {
        await fetch('/api/toggle', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ running: value })
        });
        await refresh();
      }

      function formatOpp(opp) {
        return `
          <tr>
            <td>${opp.product_name}</td>
            <td>${opp.buy_market} · ${opp.buy_price.toFixed(4)} ETH</td>
            <td>${opp.sell_market} · ${opp.sell_price.toFixed(4)} ETH</td>
            <td class="profit">${opp.expected_profit.toFixed(4)} ETH</td>
            <td>${opp.timestamp}</td>
          </tr>
        `;
      }

      async function refresh() {
        const res = await fetch('/api/status');
        const data = await res.json();
        document.getElementById('statusText').textContent = data.running ? 'Çalışıyor' : 'Durdu';
        document.getElementById('pulse').style.opacity = data.running ? '1' : '0.25';
        document.getElementById('lastScan').textContent = data.last_scan || '-';
        document.getElementById('oppCount').textContent = data.opportunities.length;
        document.getElementById('opps').innerHTML = data.opportunities.map(formatOpp).join('');
        document.getElementById('logs').innerHTML = data.logs
          .map(item => `${item.timestamp} · ${item.level} · ${item.message}`)
          .slice(0, 8)
          .join('<br/>');
      }

      refresh();
      setInterval(refresh, 2000);
    </script>
  </body>
</html>
"""
