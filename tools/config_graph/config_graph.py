#!/usr/bin/env python3
"""
Baseline Tools Dependency & Attribute Graph Generator

Two views:
  1. Inclusion Chain — select a flow, see its A→B→C include tree (auto-fit)
  2. Tool Overlap   — pesg_fe.baseline_tools grouped into clusters by unique
                       attribute similarity (common base removed). Click a
                       cluster to see what's shared and each tool's config.

Uses plotly (embedded JS, no CDN) + networkx for clustering/layout.

Prerequisites:  cth_psetup_fe  (for Cheetah reader)
Third-party:    import UsrIntel.R1  (provides plotly, networkx)

Usage:
    python3 config_graph.py --baseline-dir <path> [--output graph.html]
"""

import UsrIntel.R1

import argparse
import json
import math
import os
import re
import sys
from abc import ABC, abstractmethod
from collections import Counter
from itertools import combinations

import networkx as nx
from networkx.algorithms.community import greedy_modularity_communities
import plotly
import plotly.graph_objects as go


# ---------------------------------------------------------------------------
# Config data
# ---------------------------------------------------------------------------

class ConfigData:
    __slots__ = ("name", "path", "toolversions", "envs", "params",
                 "licenses", "includes", "raw_includes")

    def __init__(self, name: str, path: str = ""):
        self.name = name
        self.path = path
        self.toolversions: dict[str, str] = {}
        self.envs: dict[str, str] = {}
        self.params: dict[str, str] = {}
        self.licenses: list[dict] = []
        self.includes: list[str] = []
        self.raw_includes: list[str] = []

    def to_dict(self):
        return {
            "name": self.name,
            "toolversions": self.toolversions,
            "envs": self.envs,
            "params": self.params,
            "licenses": self.licenses,
            "includes": self.includes,
        }

    def attr_set(self) -> set[str]:
        s = set()
        for k, v in self.envs.items():
            s.add(f"env:{k}={v}")
        for k, v in self.toolversions.items():
            s.add(f"tv:{k}={v}")
        for lic in self.licenses:
            feat = lic.get("Feature", lic.get("feature",
                   lic.get("Name", "?")))
            s.add(f"lic:{feat}")
        return s


# ---------------------------------------------------------------------------
# Config readers
# ---------------------------------------------------------------------------

class BaseConfigReader(ABC):
    @abstractmethod
    def read_tool(self, tool_dir: str) -> ConfigData: ...
    @abstractmethod
    def reader_name(self) -> str: ...


def _parse_raw_includes(path: str) -> list[str]:
    includes = []
    in_sec = False
    try:
        with open(path) as fh:
            for line in fh:
                s = line.strip()
                if s.lower() == "[includes]":
                    in_sec = True
                    continue
                if in_sec:
                    if s.startswith("[") or not s:
                        in_sec = False
                        continue
                    if not s.startswith("#"):
                        includes.append(s)
    except OSError:
        pass
    return includes


def _resolve_include_label(inc: str, tool_dir: str) -> str:
    base = os.path.dirname(tool_dir)
    resolved = os.path.normpath(os.path.join(base, inc))
    if "/pesg_fe.baseline_tools/" in resolved:
        m = re.search(r"/pesg_fe\.baseline_tools/([^/]+)", resolved)
        if m:
            return f"pesg_fe:{m.group(1)}"
    bn = os.path.basename(resolved)
    if bn.endswith(".cth"):
        return bn.replace(".cth", "")
    return os.path.basename(os.path.dirname(resolved))


class CheetahConfigReader(BaseConfigReader):
    def __init__(self):
        from CTH.Config import Config
        self._Config = Config

    def reader_name(self) -> str:
        return "Cheetah-RTL"

    def read_tool(self, tool_dir: str) -> ConfigData:
        cth = os.path.join(tool_dir, "tool.cth")
        data = ConfigData(os.path.basename(tool_dir), tool_dir)
        data.raw_includes = _parse_raw_includes(cth)
        for inc in data.raw_includes:
            data.includes.append(_resolve_include_label(inc, tool_dir))
        try:
            cfg = self._Config()
            cfg.setFile(cth)
            r = cfg.get(resolve=0) or {}
        except Exception:
            r = {}
        if isinstance(r, dict):
            data.toolversions = r.get("toolversion", {})
            data.envs = r.get("envs", {})
            data.params = r.get("params", {})
            lic = r.get("license", [])
            data.licenses = [lic] if isinstance(lic, dict) else (
                lic if isinstance(lic, list) else [])
        return data


class ACEConfigReader(BaseConfigReader):
    def reader_name(self) -> str:
        return "ACE"
    def read_tool(self, tool_dir: str) -> ConfigData:
        raise NotImplementedError("ACE reader not yet implemented.")


# ---------------------------------------------------------------------------
# Discovery
# ---------------------------------------------------------------------------

EXCLUDE = {"iflow", "iflow-mako", "iflow_mako", "ifeed",
           "pesg_fe.baseline_tools", "flow_cfg", "python", "proj_config"}


def discover_flows(baseline: str) -> list[str]:
    return [os.path.join(baseline, e)
            for e in sorted(os.listdir(baseline))
            if e not in EXCLUDE
            and os.path.isdir(os.path.join(baseline, e))
            and os.path.isfile(os.path.join(baseline, e, "tool.cth"))]


def discover_pesg_tools(baseline: str) -> list[str]:
    pesg = os.path.join(baseline, "pesg_fe.baseline_tools")
    if not os.path.isdir(pesg):
        return []
    return [os.path.join(pesg, e)
            for e in sorted(os.listdir(pesg))
            if os.path.isdir(os.path.join(pesg, e))
            and os.path.isfile(os.path.join(pesg, e, "tool.cth"))]


# ---------------------------------------------------------------------------
# Clustering: unique-overlap communities
# ---------------------------------------------------------------------------

def compute_common_base(tool_configs, pct=0.40):
    """Attributes present in >= pct of all tools → common base to subtract."""
    counts = Counter()
    for cd in tool_configs.values():
        for a in cd.attr_set():
            counts[a] += 1
    thresh = int(len(tool_configs) * pct)
    return {a for a, c in counts.items() if c >= thresh}


def cluster_tools(tool_configs, common_base, sim_threshold=0.20):
    """Build unique-overlap graph and detect communities."""
    G = nx.Graph()
    for a, b in combinations(tool_configs.keys(), 2):
        sa = tool_configs[a].attr_set() - common_base
        sb = tool_configs[b].attr_set() - common_base
        exact = sa & sb
        if not exact:
            continue
        union = sa | sb
        ratio = len(exact) / len(union)
        if ratio >= sim_threshold:
            G.add_edge(a, b, weight=ratio, exact=len(exact))

    if G.number_of_edges() == 0:
        return [], list(tool_configs.keys())

    communities = list(greedy_modularity_communities(G, weight="weight"))
    communities.sort(key=lambda c: -len(c))

    in_graph = set(G.nodes())
    singletons = [n for n in sorted(tool_configs) if n not in in_graph]

    clusters = []
    for comm in communities:
        members = sorted(comm)
        shared = tool_configs[members[0]].attr_set() - common_base
        for m in members[1:]:
            shared &= tool_configs[m].attr_set() - common_base
        clusters.append({
            "members": members,
            "shared_unique": sorted(shared),
            "size": len(members),
        })

    return clusters, singletons


# ---------------------------------------------------------------------------
# Build all data
# ---------------------------------------------------------------------------

def build_all(reader, baseline):
    flow_configs = {}
    for td in discover_flows(baseline):
        try:
            cd = reader.read_tool(td)
            flow_configs[cd.name] = cd
        except Exception as e:
            print(f"  WARN flow: {td}: {e}", file=sys.stderr)

    tool_configs = {}
    for td in discover_pesg_tools(baseline):
        try:
            cd = reader.read_tool(td)
            tool_configs[cd.name] = cd
        except Exception as e:
            print(f"  WARN tool: {td}: {e}", file=sys.stderr)

    common_base = compute_common_base(tool_configs)
    clusters, singletons = cluster_tools(tool_configs, common_base)

    return flow_configs, tool_configs, clusters, singletons, common_base


# ---------------------------------------------------------------------------
# Plotly: Overlap cluster view
# ---------------------------------------------------------------------------

CLUSTER_COLORS = [
    "#4A90D9", "#E67E22", "#2ECC71", "#E74C3C", "#9B59B6",
    "#1ABC9C", "#F39C12", "#3498DB", "#E91E63", "#00BCD4",
    "#8BC34A", "#FF5722", "#607D8B", "#795548", "#CDDC39",
]


def build_cluster_fig(clusters, singletons, tool_configs, common_base):
    traces = []
    annotations = []
    shapes = []

    n_clusters = len(clusters)
    n_cols = max(1, math.ceil(math.sqrt(n_clusters + 1)))
    spacing = 5.0

    for ci, cl in enumerate(clusters):
        members = cl["members"]
        cx = (ci % n_cols) * spacing
        cy = -(ci // n_cols) * spacing

        n_mem = len(members)
        radius = max(0.8, 0.4 * math.sqrt(n_mem))

        # draw enclosing circle
        shapes.append(dict(
            type="circle",
            x0=cx - radius - 0.4, y0=cy - radius - 0.4,
            x1=cx + radius + 0.4, y1=cy + radius + 0.4,
            line=dict(color=CLUSTER_COLORS[ci % len(CLUSTER_COLORS)],
                      width=2, dash="dot"),
            fillcolor="rgba(255,255,255,0.03)",
        ))

        # cluster label
        annotations.append(dict(
            x=cx, y=cy + radius + 0.6, text=f"<b>Cluster {ci+1}</b>",
            showarrow=False,
            font=dict(size=11, color=CLUSTER_COLORS[ci % len(CLUSTER_COLORS)]),
        ))

        # position members in a small circle within the cluster
        mx, my, mtxt, mhover = [], [], [], []
        for mi, name in enumerate(members):
            angle = 2 * math.pi * mi / max(n_mem, 1)
            r = radius * 0.7 if n_mem > 1 else 0
            px = cx + r * math.cos(angle)
            py = cy + r * math.sin(angle)
            mx.append(px)
            my.append(py)
            mtxt.append(name)

            cd = tool_configs.get(name)
            unique = cd.attr_set() - common_base if cd else set()
            mhover.append(
                f"<b>{name}</b><br>"
                f"Unique attrs: {len(unique)}<br>"
                f"Envs: {len(cd.envs) if cd else 0}<br>"
                f"Versions: {len(cd.toolversions) if cd else 0}<br>"
                f"Licenses: {len(cd.licenses) if cd else 0}"
            )

        color = CLUSTER_COLORS[ci % len(CLUSTER_COLORS)]
        traces.append(go.Scatter(
            x=mx, y=my, mode="markers+text",
            marker=dict(size=20, color=color, symbol="square",
                        line=dict(width=2, color="#16213e")),
            text=mtxt, textposition="bottom center",
            textfont=dict(size=10, color="#e0e0e0", family="monospace"),
            hovertext=mhover, hoverinfo="text",
            showlegend=False,
            customdata=[f"cluster:{ci}" for _ in members],
        ))

    # Singletons: arrange in a grid below the clusters
    if singletons:
        cluster_rows = max(1, math.ceil(n_clusters / n_cols))
        base_y = -(cluster_rows) * spacing - 1.5

        annotations.append(dict(
            x=0, y=base_y + 1.0,
            text="<b>No unique overlap (singletons)</b>",
            showarrow=False,
            font=dict(size=11, color="#94a3b8"),
            xanchor="left",
        ))

        s_cols = max(1, math.ceil(math.sqrt(len(singletons))))
        sx, sy, stxt, shover = [], [], [], []
        for si, name in enumerate(singletons):
            px = (si % s_cols) * 2.0
            py = base_y - (si // s_cols) * 1.5
            sx.append(px)
            sy.append(py)
            stxt.append(name)
            cd = tool_configs.get(name)
            shover.append(
                f"<b>{name}</b><br>"
                f"(singleton — only common-base attrs)<br>"
                f"Envs: {len(cd.envs) if cd else 0}<br>"
                f"Licenses: {len(cd.licenses) if cd else 0}"
            )

        traces.append(go.Scatter(
            x=sx, y=sy, mode="markers+text",
            marker=dict(size=14, color="#555", symbol="square",
                        line=dict(width=1, color="#333")),
            text=stxt, textposition="bottom center",
            textfont=dict(size=9, color="#777", family="monospace"),
            hovertext=shover, hoverinfo="text",
            showlegend=False,
            customdata=["singleton" for _ in singletons],
        ))

    fig = go.Figure(data=traces)
    fig.update_layout(
        title=dict(
            text="Tool Clusters (unique overlap after removing common base)",
            font=dict(color="#e0e0e0", size=14)),
        plot_bgcolor="#1a1a2e", paper_bgcolor="#1a1a2e",
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False,
                   scaleanchor="y", scaleratio=1),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        hovermode="closest",
        margin=dict(l=20, r=20, t=60, b=20),
        shapes=shapes,
        annotations=annotations,
    )
    return fig


# ---------------------------------------------------------------------------
# HTML generator
# ---------------------------------------------------------------------------

def generate_html(flow_configs, tool_configs, clusters, singletons,
                  common_base, reader_name, output):
    # Inclusion chain data
    chain_data = {}
    for name, cd in flow_configs.items():
        nodes = [{"id": name, "label": name, "type": "flow"}]
        edges = []
        for inc in cd.includes:
            nodes.append({"id": inc, "label": inc, "type": "shared"})
            edges.append({"from": name, "to": inc})
        chain_data[name] = {"nodes": nodes, "edges": edges}

    # Cluster figure
    ovl_fig = build_cluster_fig(clusters, singletons, tool_configs, common_base)
    ovl_json = plotly.io.to_json(ovl_fig)

    # Extract plotly.js
    full_dummy = plotly.io.to_html(
        go.Figure(), full_html=False, include_plotlyjs=True)
    scripts = re.findall(r'<script[^>]*>.*?</script>', full_dummy, re.DOTALL)
    plotly_js = "\n".join(scripts[:2])

    # JSON data for JS
    chain_json = json.dumps(chain_data)
    flow_detail = json.dumps({n: cd.to_dict() for n, cd in flow_configs.items()})
    tool_detail = json.dumps({n: cd.to_dict() for n, cd in tool_configs.items()})
    flow_names = json.dumps(sorted(flow_configs.keys()))
    cluster_json = json.dumps(clusters)
    common_base_json = json.dumps(sorted(common_base))

    html = f"""\
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Baseline Tools Graph — {reader_name}</title>
{plotly_js}
<style>
* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{ font-family:'Segoe UI',system-ui,sans-serif; background:#1a1a2e; color:#e0e0e0; }}
#toolbar {{
  display:flex; align-items:center; gap:12px; padding:10px 20px;
  background:#16213e; border-bottom:1px solid #0f3460; flex-wrap:wrap;
}}
#toolbar h1 {{ font-size:16px; font-weight:600; }}
.stats {{ font-size:12px; color:#94a3b8; }}
.btn {{
  padding:6px 16px; font-size:13px; background:#0f3460; color:#e0e0e0;
  border:1px solid #1a5276; border-radius:4px; cursor:pointer;
}}
.btn:hover {{ background:#1a5276; }}
.btn.active {{ background:#1565C0; border-color:#1976D2; }}
select {{
  padding:5px 10px; font-size:12px; background:#0f3460; color:#e0e0e0;
  border:1px solid #1a5276; border-radius:4px; max-width:200px;
}}
.tab {{ display:none; width:100%; height:calc(100vh - 50px); }}
.tab.active {{ display:block; }}

#panel {{
  position:fixed; right:0; top:50px; width:400px; height:calc(100vh - 50px);
  background:#16213e; border-left:1px solid #0f3460; overflow-y:auto;
  display:none; z-index:100; font-size:12px; padding:0;
}}
#panel .hdr {{
  padding:12px 16px; background:#0f3460; position:sticky; top:0; z-index:1;
  display:flex; justify-content:space-between; align-items:center;
}}
#panel .hdr h3 {{ color:#FFD54F; font-size:14px; }}
#panel .close {{ cursor:pointer; color:#94a3b8; font-size:18px; }}
#panel .body {{ padding:12px 16px; }}
.sec {{ margin:8px 0; }}
.sec summary {{ color:#4A90D9; font-weight:600; cursor:pointer; }}
.sec summary:hover {{ text-decoration:underline; }}
.kv {{ color:#b0bec5; word-break:break-all; padding:1px 0; }}
.kv b {{ color:#e0e0e0; }}
.cluster-shared {{ background:#1a2744; border-radius:6px; padding:10px; margin:8px 0; }}
.cluster-shared h4 {{ color:#2ECC71; margin-bottom:6px; }}
.tool-block {{ border-top:1px solid #0f3460; padding-top:8px; margin-top:10px; }}
.tool-block h4 {{ color:#4A90D9; margin-bottom:4px; }}
</style>
</head>
<body>
<div id="toolbar">
  <h1>Baseline Tools</h1>
  <span class="stats">{reader_name} &bull; {len(tool_configs)} tools &bull; {len(clusters)} clusters &bull; {len(singletons)} singletons</span>
  <button class="btn active" id="btn-inc">Inclusion Chains</button>
  <button class="btn" id="btn-ovl">Tool Clusters</button>
  <span id="inc-controls">
    <label style="font-size:12px;color:#94a3b8">Flow:</label>
    <select id="flow-select"></select>
  </span>
</div>

<div id="tab-inc" class="tab active">
  <div id="inc-graph" style="width:100%;height:100%"></div>
</div>
<div id="tab-ovl" class="tab">
  <div id="plot-ovl" style="width:100%;height:100%"></div>
</div>

<div id="panel">
  <div class="hdr">
    <h3 id="panel-title"></h3>
    <span class="close" id="panel-close">&times;</span>
  </div>
  <div class="body" id="panel-body"></div>
</div>

<script>
var flowNames = {flow_names};
var chains = {chain_json};
var flowData = {flow_detail};
var toolData = {tool_detail};
var figOvl = {ovl_json};
var clusterInfo = {cluster_json};
var commonBase = {common_base_json};
var ovlRendered = false;

// ---- Flow selector ----
var sel = document.getElementById('flow-select');
flowNames.forEach(function(f) {{
  var o = document.createElement('option');
  o.value = f; o.textContent = f;
  sel.appendChild(o);
}});

// ---- Inclusion chain (single flow, auto-fit) ----
function renderChain(flowName) {{
  var c = chains[flowName];
  if (!c) return;

  var levels = {{}};
  var queue = [flowName];
  levels[flowName] = 0;
  var childMap = {{}};
  c.nodes.forEach(function(n) {{ childMap[n.id] = []; }});
  c.edges.forEach(function(e) {{
    if (childMap[e.from]) childMap[e.from].push(e.to);
  }});

  while (queue.length) {{
    var cur = queue.shift();
    (childMap[cur] || []).forEach(function(ch) {{
      if (levels[ch] === undefined) {{
        levels[ch] = levels[cur] + 1;
        queue.push(ch);
      }}
    }});
  }}

  var byLevel = {{}};
  Object.keys(levels).forEach(function(id) {{
    var lv = levels[id];
    if (!byLevel[lv]) byLevel[lv] = [];
    byLevel[lv].push(id);
  }});

  var xs = {{}}, ys = {{}};
  Object.keys(byLevel).forEach(function(lv) {{
    var arr = byLevel[lv];
    arr.forEach(function(id, i) {{
      xs[id] = (i - (arr.length-1)/2) * 2;
      ys[id] = -parseInt(lv) * 2;
    }});
  }});

  var eTraces = [];
  c.edges.forEach(function(e) {{
    if (xs[e.from] === undefined || xs[e.to] === undefined) return;
    eTraces.push({{
      x: [xs[e.from], xs[e.to], null],
      y: [ys[e.from], ys[e.to], null],
      mode: 'lines', line: {{width: 2.5, color: '#607D8B'}},
      hoverinfo: 'none', showlegend: false, type: 'scatter',
    }});
  }});

  var nx_ = [], ny = [], txt = [], hover = [], colors = [], syms = [], sz = [];
  c.nodes.forEach(function(n) {{
    if (xs[n.id] === undefined) return;
    nx_.push(xs[n.id]); ny.push(ys[n.id]);
    txt.push(n.label);
    colors.push(n.type === 'flow' ? '#4A90D9' : '#FF8A65');
    syms.push(n.type === 'flow' ? 'square' : 'diamond');
    sz.push(28);
    hover.push('<b>' + n.label + '</b>');
  }});

  var nodeTrace = {{
    x: nx_, y: ny, mode: 'markers+text',
    marker: {{size: sz, color: colors, symbol: syms, line: {{width: 2, color: '#16213e'}}}},
    text: txt, textposition: 'top center',
    textfont: {{size: 13, color: '#e0e0e0', family: 'monospace'}},
    hovertext: hover, hoverinfo: 'text', showlegend: false, type: 'scatter',
  }};

  Plotly.newPlot('inc-graph', eTraces.concat([nodeTrace]), {{
    title: {{text: flowName + ' — Inclusion Chain', font: {{color: '#e0e0e0', size: 16}}}},
    plot_bgcolor: '#1a1a2e', paper_bgcolor: '#1a1a2e',
    xaxis: {{showgrid: false, zeroline: false, showticklabels: false,
             scaleanchor: 'y', scaleratio: 1}},
    yaxis: {{showgrid: false, zeroline: false, showticklabels: false}},
    hovermode: 'closest',
    margin: {{l: 40, r: 40, t: 60, b: 40}},
  }}, {{responsive: true}}).then(function() {{
    document.getElementById('inc-graph').on('plotly_click', function(data) {{
      if (data.points && data.points.length) {{
        var nm = data.points[0].text;
        if (flowData[nm]) showToolPanel(nm, flowData);
        else if (toolData[nm]) showToolPanel(nm, toolData);
      }}
    }});
  }});
}}

// ---- Panel: single tool detail ----
function showToolPanel(name, src) {{
  var cd = src[name];
  if (!cd) return;
  document.getElementById('panel-title').textContent = name;
  document.getElementById('panel-body').innerHTML = buildToolHtml(cd);
  document.getElementById('panel').style.display = 'block';
}}

function buildToolHtml(cd) {{
  var h = '';
  function sec(title, items) {{
    if (!items || !items.length) return '';
    return '<details class="sec"><summary>' + title + ' (' + items.length + ')</summary>'
      + items.map(function(x){{ return '<div class="kv">' + x + '</div>'; }}).join('')
      + '</details>';
  }}
  if (cd.includes && cd.includes.length)
    h += sec('Includes', cd.includes.map(function(x){{ return '→ ' + x; }}));
  h += sec('Licenses', (cd.licenses||[]).map(function(l){{
    return '<b>' + (l.Feature||l.feature||l.Name||'?') + '</b>';
  }}));
  var envItems = Object.keys(cd.envs||{{}}).sort().map(function(k){{
    var v = cd.envs[k]||''; if(v.length>55) v=v.substring(0,55)+'…';
    return '<b>'+k+'</b> = '+v;
  }});
  h += sec('Environment Variables', envItems);
  h += sec('Tool Versions', Object.keys(cd.toolversions||{{}}).sort().map(function(k){{
    return '<b>'+k+'</b> = '+(cd.toolversions[k]||'');
  }}));
  h += sec('Params', Object.keys(cd.params||{{}}).sort().map(function(k){{
    var v = cd.params[k]||''; if(v.length>55) v=v.substring(0,55)+'…';
    return '<b>'+k+'</b> = '+v;
  }}));
  return h;
}}

// ---- Panel: cluster detail ----
function showClusterPanel(ci) {{
  var cl = clusterInfo[ci];
  if (!cl) return;
  document.getElementById('panel-title').textContent =
    'Cluster ' + (ci+1) + ' (' + cl.members.length + ' tools)';

  var h = '<div class="cluster-shared">';
  h += '<h4>Shared Unique Attributes (' + cl.shared_unique.length + ')</h4>';
  cl.shared_unique.forEach(function(a) {{
    h += '<div class="kv">' + a + '</div>';
  }});
  h += '</div>';

  cl.members.forEach(function(name) {{
    var cd = toolData[name];
    if (!cd) return;
    h += '<div class="tool-block"><h4>' + name + '</h4>';
    h += buildToolHtml(cd);
    h += '</div>';
  }});

  document.getElementById('panel-body').innerHTML = h;
  document.getElementById('panel').style.display = 'block';
}}

// ---- Overlap view ----
function renderOverlap() {{
  if (ovlRendered) {{
    Plotly.Plots.resize('plot-ovl');
    return;
  }}
  Plotly.newPlot('plot-ovl', figOvl.data, figOvl.layout,
                 {{responsive: true}}).then(function() {{
    ovlRendered = true;
    document.getElementById('plot-ovl').on('plotly_click', function(data) {{
      if (data.points && data.points.length) {{
        var pt = data.points[0];
        var cd = pt.customdata;
        if (cd && cd.startsWith('cluster:')) {{
          showClusterPanel(parseInt(cd.split(':')[1]));
        }} else {{
          var nm = pt.text;
          if (toolData[nm]) showToolPanel(nm, toolData);
        }}
      }}
    }});
  }});
}}

// ---- Tab switching ----
function showTab(id) {{
  document.querySelectorAll('.tab').forEach(function(t){{ t.classList.remove('active'); }});
  document.querySelectorAll('#toolbar .btn').forEach(function(b){{ b.classList.remove('active'); }});
  document.getElementById('tab-' + id).classList.add('active');
  document.getElementById('btn-' + id).classList.add('active');
  document.getElementById('inc-controls').style.display = id === 'inc' ? '' : 'none';
  if (id === 'ovl') renderOverlap();
}}

document.getElementById('btn-inc').addEventListener('click', function(){{ showTab('inc'); }});
document.getElementById('btn-ovl').addEventListener('click', function(){{ showTab('ovl'); }});
document.getElementById('panel-close').addEventListener('click', function(){{
  document.getElementById('panel').style.display = 'none';
}});
document.getElementById('flow-select').addEventListener('change', function(){{
  renderChain(this.value);
}});

if (flowNames.length) renderChain(flowNames[0]);
</script>
</body>
</html>
"""
    with open(output, "w") as fh:
        fh.write(html)
    return output


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--baseline-dir", required=True)
    p.add_argument("--output", default="baseline_graph.html")
    p.add_argument("--reader", default="cheetah", choices=["cheetah", "ace"])
    args = p.parse_args()

    baseline = os.path.abspath(args.baseline_dir)
    readers = {"cheetah": CheetahConfigReader, "ace": ACEConfigReader}
    reader = readers[args.reader]()
    print(f"Reader : {reader.reader_name()}")
    print(f"Scanning: {baseline}")

    flow_configs, tool_configs, clusters, singletons, common_base = \
        build_all(reader, baseline)

    out = generate_html(flow_configs, tool_configs, clusters, singletons,
                        common_base, reader.reader_name(), args.output)
    print(f"Wrote  : {out}")
    print(f"  Flows: {len(flow_configs)}, Tools: {len(tool_configs)}")
    print(f"  Clusters: {len(clusters)}, Singletons: {len(singletons)}")
    print(f"  Common base: {len(common_base)} attrs removed")
    for i, cl in enumerate(clusters):
        print(f"    Cluster {i+1}: {cl['members']} ({len(cl['shared_unique'])} shared)")


if __name__ == "__main__":
    main()
