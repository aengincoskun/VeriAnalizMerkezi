#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""EmlakTrend Aşama 2 — Fırsat Haritası patch script"""

fpath = '/Users/aenginc/Downloads/claude/VeriAnalizMerkezi/emlaktrend.html'
bkpath = fpath + '.bak'
import shutil, os
if os.path.exists(bkpath):
    shutil.copy(bkpath, fpath)
    print('Restored from backup')

with open(fpath, 'r', encoding='utf-8') as f:
    html = f.read()

print(f'Read OK, length={len(html)}')

# ═══════════════════════════════════════════════
# 1. CSS — </style> öncesine ekle
# ═══════════════════════════════════════════════
CSS_ADD = """
    /* ══ CONTENT TABS ══ */
    .ctab-bar{display:none;gap:2px;background:var(--bg4);border-radius:8px;padding:3px;width:fit-content}
    .ctab{padding:5px 15px;font-size:13px;font-weight:600;background:none;border:none;border-radius:6px;color:var(--t2);cursor:pointer;transition:all .15s;white-space:nowrap}
    .ctab.on{background:var(--bg2);color:var(--t1);box-shadow:0 1px 3px rgba(0,0,0,.35)}
    .ctab:hover:not(.on){color:var(--t1)}
    /* ══ FIRSAT PANEL ══ */
    #firsatPanel{display:none;flex-direction:column;gap:14px;width:100%}
    .fo-cards{display:grid;grid-template-columns:repeat(3,1fr);gap:12px}
    .fo-card{background:var(--bg2);border:1px solid var(--border);border-radius:10px;padding:14px 16px;transition:border-color .2s}
    .fo-card:hover{border-color:var(--accent)}
    .fo-card-icon{font-size:22px;margin-bottom:8px}
    .fo-card-lbl{font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:.08em;color:var(--t3);margin-bottom:4px}
    .fo-card-val{font-size:16px;font-weight:800;color:var(--t1)}
    .fo-card-sub{font-size:11px;color:var(--t2);margin-top:3px}
    .opp-table{width:100%;border-collapse:collapse;font-size:13px}
    .opp-table th{font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:.06em;color:var(--t3);padding:8px 10px;text-align:left;border-bottom:1px solid var(--border);white-space:nowrap}
    .opp-table td{padding:9px 10px;border-bottom:1px solid rgba(48,54,61,.5);vertical-align:middle}
    .opp-table tbody tr{cursor:pointer;transition:background .15s}
    .opp-table tbody tr:hover{background:var(--bg4)}
    .opp-table tbody tr.best-row{background:rgba(63,185,80,.05)}
    .opp-score{display:inline-flex;align-items:center;justify-content:center;width:28px;height:28px;border-radius:6px;font-size:12px;font-weight:800}
    .score-high{background:rgba(63,185,80,.2);color:var(--green)}
    .score-mid{background:rgba(227,179,65,.2);color:var(--yellow)}
    .score-low{background:rgba(248,81,73,.2);color:var(--red)}
    .best-badge{display:inline-block;font-size:9px;font-weight:700;padding:2px 6px;border-radius:4px;background:rgba(63,185,80,.2);color:var(--green);margin-left:5px;vertical-align:middle}
    .trans-dots{display:flex;gap:2px}
    .tdot{width:8px;height:8px;border-radius:50%}
    .tdot.on{background:var(--accent)}.tdot.off{background:var(--border)}
    .scatter-wrap{position:relative;height:360px}
    @media(max-width:900px){.fo-cards{grid-template-columns:1fr 1fr}}
    @media(max-width:600px){.fo-cards{grid-template-columns:1fr}}
"""
assert '  </style>' in html, "CSS marker not found"
html = html.replace('  </style>', CSS_ADD + '  </style>', 1)
print('✓ CSS added')

# ═══════════════════════════════════════════════
# 2. CTAB BAR HTML — main içinde, analyzPanel öncesine
# ═══════════════════════════════════════════════
CTAB_HTML = """  <!-- CONTENT TABS -->
  <div class="ctab-bar" id="ctabBar">
    <button class="ctab on" id="ctFiyat" onclick="switchContentTab('fiyat')">📊 Fiyat Analizi</button>
    <button class="ctab" id="ctFirsat" onclick="switchContentTab('firsat')">🗺️ Fırsat Haritası</button>
  </div>

  """
MARKER2 = '  <!-- \u2500\u2500 ANALİZ PANELİ \u2500\u2500 -->'  # exact unicode from file
assert MARKER2 in html, f"HTML marker 2 not found"
html = html.replace(MARKER2, CTAB_HTML + MARKER2, 1)
print('✓ ctab-bar HTML added')

# ═══════════════════════════════════════════════
# 3. FIRSAT PANEL HTML — radarPanel'den sonra
# ═══════════════════════════════════════════════
FIRSAT_HTML = """
  <!-- ── FIRSAT HARİTASI PANELİ ── -->
  <div id="firsatPanel">

    <!-- Özet Kartlar -->
    <div class="fo-cards" id="foCards"></div>

    <!-- İlçe Karşılaştırma Tablosu -->
    <div class="cbox">
      <div style="font-size:13px;font-weight:700;margin-bottom:12px;display:flex;align-items:center;gap:8px">
        🗺️ İlçe Karşılaştırma Tablosu
        <span style="font-size:11px;color:var(--t3);font-weight:400" id="foTableCity">—</span>
      </div>
      <div style="overflow-x:auto">
        <table class="opp-table">
          <thead>
            <tr>
              <th>İlçe</th>
              <th>Güncel m² Fiyatı</th>
              <th>1Y Değişim %</th>
              <th>3Y Değişim %</th>
              <th>Kira Getirisi %</th>
              <th>Ulaşım</th>
              <th>Dönüşüm</th>
              <th>Fırsat Skoru</th>
            </tr>
          </thead>
          <tbody id="oppTableBody"></tbody>
        </table>
      </div>
    </div>

    <!-- Scatter Plot -->
    <div class="cbox">
      <div style="font-size:13px;font-weight:700;margin-bottom:4px">📈 Fiyat vs. Büyüme Dağılımı</div>
      <div style="font-size:11px;color:var(--t2);margin-bottom:14px">
        X: Güncel m² fiyatı &nbsp;—&nbsp; Y: 1 yıllık değişim % &nbsp;·&nbsp; Sol Üst = En İyi Fırsat
      </div>
      <div class="scatter-wrap"><canvas id="scatterChart"></canvas></div>
    </div>

    <div class="fnote">⚠️ Fırsat Haritası verileri simüle edilmiştir. Yatırım kararı için profesyonel danışmanlık alınız.</div>

  </div><!-- /firsatPanel -->
"""
MARKER3 = '  </div><!-- /radarPanel -->'
assert MARKER3 in html, "radarPanel end marker not found"
html = html.replace(MARKER3, MARKER3 + FIRSAT_HTML, 1)
print('✓ firsatPanel HTML added')

# ═══════════════════════════════════════════════
# 4. switchView — güncelle
# ═══════════════════════════════════════════════
OLD_SW = "function switchView(v){\n  document.getElementById('ntAnaliz').classList.toggle('on', v==='analiz');\n  document.getElementById('ntRadar').classList.toggle('on',  v==='radar');\n  document.getElementById('analyzPanel').style.display = v==='analiz' ? 'flex' : 'none';\n  document.getElementById('radarPanel').style.display  = v==='radar'  ? 'flex' : 'none';\n  if(v==='radar') renderRadar();\n}"
NEW_SW = """function switchView(v){
  document.getElementById('ntAnaliz').classList.toggle('on', v==='analiz');
  document.getElementById('ntRadar').classList.toggle('on',  v==='radar');
  const isAnaliz = v === 'analiz';
  document.getElementById('ctabBar').style.display = isAnaliz ? 'flex' : 'none';
  if(isAnaliz){
    if(currentContentTab === 'firsat'){
      document.getElementById('analyzPanel').style.display = 'none';
      document.getElementById('firsatPanel').style.display = 'flex';
      renderFirsatPanel();
    } else {
      document.getElementById('analyzPanel').style.display = 'flex';
      document.getElementById('firsatPanel').style.display = 'none';
    }
  } else {
    document.getElementById('analyzPanel').style.display = 'none';
    document.getElementById('firsatPanel').style.display = 'none';
  }
  document.getElementById('radarPanel').style.display = v==='radar' ? 'flex' : 'none';
  if(v==='radar') renderRadar();
}"""
assert OLD_SW in html, "switchView original not found"
html = html.replace(OLD_SW, NEW_SW, 1)
print('✓ switchView updated')

# ═══════════════════════════════════════════════
# 5. Init — ctabBar'ı başlangıçta göster
# ═══════════════════════════════════════════════
OLD_INIT = "S.district='atasehir';\n  renderAlerts();\n  renderChart();\n});"
NEW_INIT = "S.district='atasehir';\n  document.getElementById('ctabBar').style.display='flex';\n  renderAlerts();\n  renderChart();\n});"
assert OLD_INIT in html, "init marker not found"
html = html.replace(OLD_INIT, NEW_INIT, 1)
print('✓ Init ctabBar visibility set')

# ═══════════════════════════════════════════════
# 6. JS FONKSİYONLARI — </script> öncesine ekle
# ═══════════════════════════════════════════════
JS_ADD = r"""
// ════════════════════════════════════════════════
// FIRSAT HARİTASI — FONKSİYONLAR
// ════════════════════════════════════════════════
const TRANSPORT_SCORE = {
  istanbul:{atasehir:5,kadikoy:5,besiktas:5,sisli:5,uskudar:5,maltepe:4,pendik:4,umraniye:4,kartal:4,bagcilar:4,esenyurt:3,beylikduzu:3,bahcelievler:4,sariyer:3,zeytinburnu:5},
  ankara:{cankaya:5,kecioren:4,mamak:3,etimesgut:4,yenimahalle:4,sincan:4,altindag:3,pursaklar:2,golbasi:3},
  izmir:{konak:5,karsiyaka:4,bornova:4,buca:3,bayrakli:5,cigli:3,gaziemir:4,balcova:3,narlidere:3},
  bursa:{nilufer:4,osmangazi:4,yildirim:3,gorukle:3,mudanya:2},
  antalya:{muratpasa:4,kepez:3,konyaalti:3,dosemealti:2,alanya:2,manavgat:2}
};

const DONUSUM_LABEL = {
  istanbul:{atasehir:'Aktif',kadikoy:'Kismi',besiktas:'Secili',sisli:'Devam',uskudar:'Kismi',maltepe:'Orta',pendik:'Aktif',umraniye:'Yogun',kartal:'Aktif',bagcilar:'Yogun',esenyurt:'Buyume',beylikduzu:'Az',bahcelievler:'Orta',sariyer:'Sinirli',zeytinburnu:'Aktif'},
  ankara:{cankaya:'Kismi',kecioren:'TOKI',mamak:'Aktif',etimesgut:'Buyume',yenimahalle:'Orta',sincan:'Yeni',altindag:'Kismi',pursaklar:'Az',golbasi:'Sinirli'},
  izmir:{konak:'Sinirli',karsiyaka:'Kismi',bornova:'Tekno',buca:'TOKI',bayrakli:'Merkez',cigli:'OSB',gaziemir:'STB',balcova:'Termal',narlidere:'Marina'},
  bursa:{nilufer:'Az',osmangazi:'Orta',yildirim:'Aktif',gorukle:'Buyume',mudanya:'Sahil'},
  antalya:{muratpasa:'Sahil',kepez:'TOKI',konyaalti:'Turizm',dosemealti:'Villa',alanya:'Buyume',manavgat:'Turizm'}
};

let scatterChartInst = null;
let currentContentTab = 'fiyat';

function switchContentTab(tab){
  currentContentTab = tab;
  const ap = document.getElementById('analyzPanel');
  const fp = document.getElementById('firsatPanel');
  const ctF = document.getElementById('ctFiyat');
  const ctO = document.getElementById('ctFirsat');
  if(tab === 'fiyat'){
    ap.style.display = 'flex'; fp.style.display = 'none';
    ctF.classList.add('on'); ctO.classList.remove('on');
  } else {
    ap.style.display = 'none'; fp.style.display = 'flex';
    ctF.classList.remove('on'); ctO.classList.add('on');
    renderFirsatPanel();
  }
}

function calcDistrictData(city, room){
  const results = [];
  Object.entries(CITIES[city].districts).forEach(([dKey, dVal]) => {
    const raw = generateRaw(city, dKey, room);
    const last = raw[62], pt1Y = raw[50], pt3Y = raw[26];
    const m2 = last.m2;
    const chg1Y = (last.m2 - pt1Y.m2) / pt1Y.m2 * 100;
    const chg3Y = (last.m2 - pt3Y.m2) / pt3Y.m2 * 100;
    const tScore = (TRANSPORT_SCORE[city] || {})[dKey] || 3;
    const base = KIRA_GETIRI_BASE[room] || 4.2;
    const carp = ((KIRA_BOLGE_CARP[city] || {})[dKey]) || 1.0;
    const rentYield = base * carp;
    const donusum = (DONUSUM_LABEL[city] || {})[dKey] || 'Orta';
    results.push({ key: dKey, name: dVal.n, m2, chg1Y, chg3Y, rentYield, tScore, donusum });
  });
  const prices = results.map(r => r.m2);
  const growths = results.map(r => r.chg1Y);
  const minP = Math.min(...prices), maxP = Math.max(...prices);
  const minG = Math.min(...growths), maxG = Math.max(...growths);
  results.forEach(r => {
    const normP = maxP > minP ? (r.m2 - minP) / (maxP - minP) : 0.5;
    const normG = maxG > minG ? (r.chg1Y - minG) / (maxG - minG) : 0.5;
    r.oppScore = Math.round(((1 - normP) * 0.4 + normG * 0.35 + (r.tScore / 5) * 0.25) * 100) / 10;
  });
  results.sort((a, b) => b.oppScore - a.oppScore);
  return results;
}

function renderFirsatPanel(){
  const city = S.city, room = S.room;
  const data = calcDistrictData(city, room);
  document.getElementById('foTableCity').textContent = CITIES[city].name + ' \u00b7 ' + room;

  const best = data[0];
  const cheapest = [...data].sort((a,b) => a.m2 - b.m2)[0];
  const fastest = [...data].sort((a,b) => b.chg1Y - a.chg1Y)[0];
  document.getElementById('foCards').innerHTML = `
    <div class="fo-card">
      <div class="fo-card-icon">\u{1F3C6}</div>
      <div class="fo-card-lbl">En Y\u00fcksek F\u0131rsat Potansiyeli</div>
      <div class="fo-card-val">${best.name}</div>
      <div class="fo-card-sub">F\u0131rsat Skoru: <strong style="color:var(--green)">${best.oppScore}/10</strong></div>
    </div>
    <div class="fo-card">
      <div class="fo-card-icon">\u{1F4C9}</div>
      <div class="fo-card-lbl">En Uygun Fiyatl\u0131 \u0130l\u00e7e</div>
      <div class="fo-card-val">${cheapest.name}</div>
      <div class="fo-card-sub">\u20ba${cheapest.m2.toLocaleString('tr-TR')}/m\u00b2</div>
    </div>
    <div class="fo-card">
      <div class="fo-card-icon">\u{1F680}</div>
      <div class="fo-card-lbl">En H\u0131zl\u0131 Y\u00fckselen</div>
      <div class="fo-card-val">${fastest.name}</div>
      <div class="fo-card-sub">1Y: <strong style="color:var(--green)">+${fastest.chg1Y.toFixed(1)}%</strong></div>
    </div>`;

  const scCls = s => s >= 7 ? 'score-high' : s >= 4 ? 'score-mid' : 'score-low';
  const dots = s => {
    let d = '';
    for(let i = 1; i <= 5; i++) d += `<div class="tdot ${i <= s ? 'on' : 'off'}"></div>`;
    return `<div class="trans-dots">${d}</div>`;
  };
  const chgF = v => {
    const c = v >= 0 ? 'var(--green)' : 'var(--red)';
    return `<span style="color:${c};font-weight:700">${v >= 0 ? '+' : ''}${v.toFixed(1)}%</span>`;
  };
  document.getElementById('oppTableBody').innerHTML = data.map((r, i) => `
    <tr onclick="selectDistrictFromFirsat('${r.key}')" ${i === 0 ? 'class="best-row"' : ''}>
      <td><strong>${r.name}</strong>${i === 0 ? '<span class="best-badge">\u{1F947} En \u0130yi F\u0131rsat</span>' : ''}</td>
      <td>\u20ba${r.m2.toLocaleString('tr-TR')}</td>
      <td>${chgF(r.chg1Y)}</td>
      <td>${chgF(r.chg3Y)}</td>
      <td style="color:var(--purple);font-weight:700">%${r.rentYield.toFixed(1)}</td>
      <td>${dots(r.tScore)}</td>
      <td style="font-size:11px;color:var(--t2)">${r.donusum}</td>
      <td><span class="opp-score ${scCls(r.oppScore)}">${r.oppScore}</span></td>
    </tr>`).join('');

  renderScatterChart(data);
}

function renderScatterChart(data){
  if(scatterChartInst){ scatterChartInst.destroy(); scatterChartInst = null; }
  const prices = data.map(r => r.m2), growths = data.map(r => r.chg1Y);
  const midP = (Math.min(...prices) + Math.max(...prices)) / 2;
  const midG = (Math.min(...growths) + Math.max(...growths)) / 2;
  const mkCol = r => {
    if(r.m2 <= midP && r.chg1Y >= midG) return '#3fb950';
    if(r.m2 > midP  && r.chg1Y >= midG) return '#388bfd';
    if(r.m2 <= midP && r.chg1Y < midG)  return '#e3b341';
    return '#f85149';
  };
  const pts = data.map(r => ({ x: r.m2, y: parseFloat(r.chg1Y.toFixed(2)), label: r.name, col: mkCol(r) }));
  const ctx = document.getElementById('scatterChart').getContext('2d');
  scatterChartInst = new Chart(ctx, {
    type: 'scatter',
    data: { datasets: [{
      data: pts.map(p => ({ x: p.x, y: p.y })),
      backgroundColor: pts.map(p => p.col + 'bb'),
      borderColor: pts.map(p => p.col),
      pointRadius: 9, pointHoverRadius: 12, borderWidth: 2
    }]},
    options: {
      responsive: true, maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        tooltip: {
          callbacks: {
            label: ctx2 => {
              const p = pts[ctx2.dataIndex];
              return `${p.label}  |  \u20ba${p.x.toLocaleString('tr-TR')}/m\u00b2  |  1Y: ${p.y >= 0 ? '+' : ''}${p.y.toFixed(1)}%`;
            }
          },
          backgroundColor: '#1c2128', borderColor: '#30363d', borderWidth: 1,
          titleColor: '#e6edf3', bodyColor: '#8b949e', padding: 10
        }
      },
      scales: {
        x: {
          grid: { color: 'rgba(48,54,61,.6)' },
          ticks: { color: '#6e7681', callback: v => '\u20ba' + Number(v).toLocaleString('tr-TR') },
          title: { display: true, text: 'G\u00fcncel m\u00b2 Fiyat\u0131 (\u20ba)', color: '#6e7681', font: { size: 11 } }
        },
        y: {
          grid: { color: 'rgba(48,54,61,.6)' },
          ticks: { color: '#6e7681', callback: v => v + '%' },
          title: { display: true, text: '1 Y\u0131ll\u0131k De\u011fi\u015fim %', color: '#6e7681', font: { size: 11 } }
        }
      }
    },
    plugins: [{
      id: 'quadrant',
      afterDraw(chart){
        const { ctx: c, chartArea: { left, right, top, bottom } } = chart;
        const sx = chart.scales.x, sy = chart.scales.y;
        const qx = sx.getPixelForValue(midP), qy = sy.getPixelForValue(midG);
        c.save();
        c.strokeStyle = 'rgba(48,54,61,.9)'; c.lineWidth = 1; c.setLineDash([4, 4]);
        c.beginPath(); c.moveTo(qx, top); c.lineTo(qx, bottom); c.stroke();
        c.beginPath(); c.moveTo(left, qy); c.lineTo(right, qy); c.stroke();
        c.setLineDash([]);
        [
          { x: left + 7,  y: top + 15,   t: '\u2705 Ucuz + Y\u00fckselen',  col: '#3fb950' },
          { x: qx + 7,   y: top + 15,   t: '\u{1F4C8} Pahal\u0131 + Y\u00fckselen', col: '#388bfd' },
          { x: left + 7,  y: bottom - 7, t: '\u26a0\ufe0f Ucuz + D\u00fc\u015fen',   col: '#e3b341' },
          { x: qx + 7,   y: bottom - 7, t: '\u274c Pahal\u0131 + D\u00fc\u015fen',  col: '#f85149' }
        ].forEach(l => {
          c.fillStyle = l.col; c.font = 'bold 10px system-ui'; c.fillText(l.t, l.x, l.y);
        });
        c.fillStyle = '#8b949e'; c.font = '10px system-ui';
        pts.forEach(p => {
          const px = sx.getPixelForValue(p.x), py = sy.getPixelForValue(p.y);
          c.fillText(p.label, px + 9, py - 5);
        });
        c.restore();
      }
    }]
  });
}

function selectDistrictFromFirsat(distKey){
  document.getElementById('districtSelect').value = distKey;
  S.district = distKey;
  switchContentTab('fiyat');
  scheduleUpdate();
}

"""
MARKER6 = '\n</script>\n</body>'
assert MARKER6 in html, "script end marker not found"
html = html.replace(MARKER6, JS_ADD + MARKER6, 1)
print('✓ JS functions added')

# ═══════════════════════════════════════════════
# KAYDET
# ═══════════════════════════════════════════════
with open(fpath, 'w', encoding='utf-8') as f:
    f.write(html)
print(f'✓ Saved! New length={len(html)}')
