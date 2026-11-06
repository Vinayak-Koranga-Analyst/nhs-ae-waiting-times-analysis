"""Build a self-contained interactive dashboard (dashboard/index.html).

Usage:
    python src/build_dashboard.py

Reads the query results in outputs/ (run src/run_queries.py first) and writes a
single HTML file that uses Plotly from a CDN. Open it in any browser.
"""

import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs"
DASH = ROOT / "dashboard"

TEMPLATE = """<!doctype html>
<html lang="en-GB">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>NHS A&amp;E Dashboard</title>
<script src="https://cdn.jsdelivr.net/npm/plotly.js-dist-min@2.35.2/plotly.min.js"></script>
<style>
:root {
  --surface: #fcfcfb; --card: #ffffff; --border: #e4e3df;
  --text: #0b0b0b; --muted: #52514e; --blue: #2a78d6; --orange: #eb6834;
}
* { box-sizing: border-box; }
body { margin: 0; background: var(--surface); color: var(--text);
       font: 15px/1.5 system-ui, -apple-system, "Segoe UI", sans-serif; }
main { max-width: 1100px; margin: 0 auto; padding: 24px 16px 48px; }
h1 { font-size: 1.5rem; margin: 0 0 4px; }
.sub { color: var(--muted); margin: 0 0 20px; }
.tiles { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 12px; margin-bottom: 16px; }
.tile, .card { background: var(--card); border: 1px solid var(--border); border-radius: 10px; padding: 14px 16px; }
.tile .label { color: var(--muted); font-size: .85rem; }
.tile .value { font-size: 1.8rem; font-weight: 600; }
.tile .note { color: var(--muted); font-size: .8rem; }
.grid { display: grid; grid-template-columns: 1fr; gap: 16px; }
@media (min-width: 900px) { .grid.two { grid-template-columns: 1fr 1fr; } }
.card h2 { font-size: 1rem; margin: 0 0 4px; }
.card p { color: var(--muted); font-size: .85rem; margin: 0 0 8px; }
.filters { display: flex; gap: 8px; align-items: center; margin: 24px 0 12px; flex-wrap: wrap; }
select { font: inherit; padding: 6px 10px; border-radius: 8px; border: 1px solid var(--border); background: var(--card); color: var(--text); }
table { width: 100%; border-collapse: collapse; font-size: .85rem; }
th, td { text-align: left; padding: 6px 8px; border-bottom: 1px solid var(--border); }
th { color: var(--muted); font-weight: 600; }
td.num, th.num { text-align: right; font-variant-numeric: tabular-nums; }
.table-wrap { overflow-x: auto; }
footer { color: var(--muted); font-size: .8rem; margin-top: 24px; }
</style>
</head>
<body>
<main>
  <h1>NHS A&amp;E waiting times, England</h1>
  <p class="sub">April 2024 – September 2026 · Source: NHS England, A&amp;E Attendances and Emergency Admissions</p>

  <div class="tiles" id="tiles"></div>

  <div class="grid">
    <div class="card">
      <h2>Share of patients seen within 4 hours</h2>
      <p>Dashed line: 78% interim target for March 2026</p>
      <div id="trend" style="height:340px"></div>
    </div>
  </div>

  <div class="grid two" style="margin-top:16px">
    <div class="card">
      <h2>12-hour trolley waits</h2>
      <p>Patients waiting 12+ hours from decision to admit</p>
      <div id="trolley" style="height:300px"></div>
    </div>
    <div class="card">
      <h2>Regions, latest 12 months</h2>
      <p>4-hour performance, all A&amp;E types (Oct 2025 – Sep 2026). Dashed line: 78% target</p>
      <div id="regions" style="height:300px"></div>
    </div>
  </div>

  <div class="filters">
    <label for="region">Region</label>
    <select id="region"></select>
  </div>

  <div class="grid two">
    <div class="card">
      <h2>Trusts: trolley waits vs 4-hour performance</h2>
      <p>Type 1 departments, Oct 2025 – Sep 2026. Hover for trust name.</p>
      <div id="scatter" style="height:360px"></div>
    </div>
    <div class="card">
      <h2>Lowest Type 1 performance</h2>
      <p>The 12 trusts furthest from the target in the selected region</p>
      <div class="table-wrap"><table id="table"></table></div>
    </div>
  </div>

  <footer>Contains public sector information licensed under the Open Government Licence v3.0.
  Analysis by Vinayak Koranga. Not NHS guidance.</footer>
</main>
<script>
const DATA = __DATA__;
const css = getComputedStyle(document.documentElement);
const C = n => css.getPropertyValue(n).trim();
// Plotly mutates layout objects, so build a fresh base layout for every chart.
const baseLayout = () => ({
  margin: {l: 48, r: 16, t: 8, b: 36}, paper_bgcolor: "rgba(0,0,0,0)", plot_bgcolor: "rgba(0,0,0,0)",
  font: {family: "system-ui, sans-serif", color: C("--muted"), size: 12},
  xaxis: {gridcolor: C("--border"), zeroline: false}, yaxis: {gridcolor: C("--border"), zeroline: false},
  hoverlabel: {bgcolor: "#ffffff", bordercolor: C("--border"), font: {color: C("--text")}},
  legend: {orientation: "h", y: -0.15},
});
const cfg = {displayModeBar: false, responsive: true};
const fmt = n => n.toLocaleString("en-GB");

// Tiles
const t = DATA.trend, last = t[t.length - 1];
const peak = t.reduce((a, b) => b.trolley_waits_12h > a.trolley_waits_12h ? b : a);
const best = t.reduce((a, b) => b.pct_4h_all_types > a.pct_4h_all_types ? b : a);
const tiles = [
  ["Within 4 hours, " + last.label, last.pct_4h_all_types.toFixed(1) + "%", (78 - last.pct_4h_all_types).toFixed(1) + " points below the 78% target"],
  ["Best month", best.pct_4h_all_types.toFixed(1) + "%", best.label + " (target month for 78%)"],
  ["12-hour trolley waits, " + last.label, fmt(last.trolley_waits_12h), "Peak: " + fmt(peak.trolley_waits_12h) + " in " + peak.label],
  ["Trusts at or above 78% (Type 1)", DATA.trusts.filter(d => d.pct_4h_type1 >= 78).length + " of " + DATA.trusts.length, "Latest 12 months"],
];
document.getElementById("tiles").innerHTML = tiles.map(([l, v, n]) =>
  `<div class="tile"><div class="label">${l}</div><div class="value">${v}</div><div class="note">${n}</div></div>`).join("");

// Trend
Plotly.newPlot("trend", [
  {x: t.map(d => d.month), y: t.map(d => d.pct_4h_all_types), name: "All A&E types", mode: "lines+markers",
   line: {color: C("--blue"), width: 2}, marker: {size: 6}, hovertemplate: "%{y:.1f}%<extra>All types</extra>"},
  {x: t.map(d => d.month), y: t.map(d => d.pct_4h_type1), name: "Type 1 (major EDs)", mode: "lines+markers",
   line: {color: C("--orange"), width: 2}, marker: {size: 6}, hovertemplate: "%{y:.1f}%<extra>Type 1</extra>"},
], (b => ({...b, hovermode: "x unified", yaxis: {...b.yaxis, ticksuffix: "%", range: [50, 82]},
   shapes: [{type: "line", xref: "paper", x0: 0, x1: 1, y0: 78, y1: 78, line: {color: C("--muted"), dash: "dash", width: 1}}]}))(baseLayout()), cfg);

// Trolley waits
Plotly.newPlot("trolley", [{x: t.map(d => d.month), y: t.map(d => d.trolley_waits_12h), type: "bar",
  marker: {color: C("--blue")}, hovertemplate: "%{x|%b %Y}: %{y:,}<extra></extra>"}],
  {...baseLayout(), bargap: 0.25}, cfg);

// Regions
const r = [...DATA.regions].sort((a, b) => a.pct_4h_latest - b.pct_4h_latest);
Plotly.newPlot("regions", [{y: r.map(d => d.label), x: r.map(d => d.pct_4h_latest), type: "bar", orientation: "h",
  marker: {color: C("--blue")}, text: r.map(d => d.pct_4h_latest.toFixed(1) + "%"), textposition: "inside", insidetextanchor: "end", textfont: {color: "#ffffff"},
  hovertemplate: "%{y}: %{x:.1f}%<extra></extra>"}],
  (b => ({...b, margin: {...b.margin, l: 150}, xaxis: {...b.xaxis, range: [0, 90], ticksuffix: "%"}, shapes: [{type: "line", yref: "paper", y0: 0, y1: 1, x0: 78, x1: 78, line: {color: C("--muted"), dash: "dash", width: 1}}]}))(baseLayout()), cfg);

// Filtered views
const sel = document.getElementById("region");
const regions = ["All regions", ...[...new Set(DATA.trusts.map(d => d.region))].sort()];
sel.innerHTML = regions.map(v => `<option>${v}</option>`).join("");
function draw() {
  const v = sel.value, rows = DATA.trusts.filter(d => v === "All regions" || d.region === v);
  Plotly.react("scatter", [{x: rows.map(d => d.trolley_12h_per_100_adm), y: rows.map(d => d.pct_4h_type1),
    text: rows.map(d => d.trust), mode: "markers", type: "scatter",
    marker: {color: C("--blue"), size: 9, opacity: .85, line: {color: "#ffffff", width: 1}},
    hovertemplate: "%{text}<br>4-hour: %{y:.1f}%<br>Trolley waits per 100 admissions: %{x:.1f}<extra></extra>"}],
    (b => ({...b, xaxis: {...b.xaxis, title: {text: "12-hour trolley waits per 100 admissions"}},
     yaxis: {...b.yaxis, ticksuffix: "%", title: {text: "Type 1 4-hour performance"}}}))(baseLayout()), cfg);
  const worst = [...rows].sort((a, b) => a.pct_4h_type1 - b.pct_4h_type1).slice(0, 12);
  document.getElementById("table").innerHTML =
    `<tr><th>Trust</th><th class="num">4-hour (Type 1)</th><th class="num">Trolley waits / 100</th></tr>` +
    worst.map(d => `<tr><td>${d.trust}</td><td class="num">${d.pct_4h_type1.toFixed(1)}%</td><td class="num">${d.trolley_12h_per_100_adm.toFixed(1)}</td></tr>`).join("");
}
sel.addEventListener("change", draw);
draw();
</script>
</body>
</html>
"""


def title_case(s: str) -> str:
    small = {"and", "of", "the", "nhs"}
    words = s.lower().split()
    out = [w.upper() if w == "nhs" else (w if w in small and i else w.capitalize()) for i, w in enumerate(words)]
    return " ".join(out).replace("Nhs", "NHS")


def main() -> None:
    trend = pd.read_csv(OUT / "01_national_trend.csv")
    trend["label"] = pd.to_datetime(trend["month"]).dt.strftime("%b %Y")
    regions = pd.read_csv(OUT / "03_region_performance.csv")
    regions["label"] = regions["region"].map(title_case)
    trusts = pd.read_csv(OUT / "04_trust_league_table.csv")
    trusts["trust"] = trusts["trust"].map(title_case)
    trusts["region"] = trusts["region"].map(title_case)

    data = {
        "trend": trend.to_dict("records"),
        "regions": regions.to_dict("records"),
        "trusts": trusts[["trust", "region", "pct_4h_type1", "trolley_12h_per_100_adm"]].to_dict("records"),
    }
    DASH.mkdir(exist_ok=True)
    (DASH / "index.html").write_text(TEMPLATE.replace("__DATA__", json.dumps(data)))
    print(f"Wrote {(DASH / 'index.html').relative_to(ROOT)}")


if __name__ == "__main__":
    main()
