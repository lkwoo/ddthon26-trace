/* Knowledge Store — static D3 viewer.
 * Loads pre-generated export files (structure.json, relationships.json,
 * wiki.json) via fetch and renders three decoupled views. No build step.
 */
"use strict";

const state = { structure: null, relationships: null, wiki: null };

async function loadJSON(name) {
  try {
    const res = await fetch(name);
    if (!res.ok) throw new Error(res.status);
    return await res.json();
  } catch (e) {
    return null;
  }
}

function setStatus(msg) {
  document.getElementById("status").textContent = msg;
}

function switchView(view) {
  document.querySelectorAll(".tab").forEach((t) =>
    t.classList.toggle("active", t.dataset.view === view));
  document.querySelectorAll(".view").forEach((v) =>
    v.classList.toggle("active", v.id === `view-${view}`));
  if (view === "tree") renderTree();
  if (view === "graph") renderGraph();
}

/* ---- Structure tree (collapsible, Graphify tree_html style) ---- */
function buildHierarchy(structure) {
  const root = { name: "project", children: [] };
  if (!structure) return root;
  const files = structure.nodes.filter((n) => n.kind === "file");
  const byFile = {};
  files.forEach((f) => {
    byFile[f.id] = { name: f.name, kind: "file", children: [] };
    root.children.push(byFile[f.id]);
  });
  structure.edges
    .filter((e) => e.type === "contain")
    .forEach((e) => {
      const parent = byFile[e.src];
      const child = structure.nodes.find((n) => n.id === e.dst);
      if (parent && child) parent.children.push({ name: child.name, kind: child.kind });
    });
  return root;
}

function renderTree() {
  const host = document.getElementById("tree");
  host.innerHTML = "";
  if (typeof d3 === "undefined") { host.innerHTML = notice("D3 unavailable (offline)."); return; }
  if (!state.structure || !state.structure.nodes.length) {
    host.innerHTML = notice("No structure data. Ingest code to populate the tree.");
    return;
  }
  const data = buildHierarchy(state.structure);
  const width = host.clientWidth || 800;
  const root = d3.hierarchy(data);
  const dx = 20, dy = width / (root.height + 2);
  d3.tree().nodeSize([dx, dy])(root);
  let x0 = Infinity, x1 = -Infinity;
  root.each((d) => { if (d.x > x1) x1 = d.x; if (d.x < x0) x0 = d.x; });
  const height = x1 - x0 + dx * 2;
  const svg = d3.select(host).append("svg")
    .attr("viewBox", [-dy / 2, x0 - dx, width, height]);
  svg.append("g").selectAll("path").data(root.links()).join("path")
    .attr("class", "link")
    .attr("d", d3.linkHorizontal().x((d) => d.y).y((d) => d.x));
  const node = svg.append("g").selectAll("g").data(root.descendants()).join("g")
    .attr("class", "node").attr("transform", (d) => `translate(${d.y},${d.x})`);
  node.append("circle").attr("r", 4);
  node.append("text").attr("dy", "0.31em").attr("x", (d) => d.children ? -8 : 8)
    .attr("text-anchor", (d) => d.children ? "end" : "start")
    .text((d) => d.data.name);
}

/* ---- Dependency graph (force-directed) ---- */
function renderGraph() {
  const host = document.getElementById("graph");
  host.innerHTML = "";
  if (typeof d3 === "undefined") { host.innerHTML = notice("D3 unavailable (offline)."); return; }
  const struct = state.structure;
  if (!struct || !struct.nodes.length) {
    host.innerHTML = notice("No graph data. Ingest code to populate the dependency graph.");
    return;
  }
  const width = host.clientWidth || 800, height = host.clientHeight || 600;
  const nodes = struct.nodes.map((n) => ({ id: n.id, name: n.name, kind: n.kind }));
  const ids = new Set(nodes.map((n) => n.id));
  const links = struct.edges
    .filter((e) => ids.has(e.src) && ids.has(e.dst))
    .map((e) => ({ source: e.src, target: e.dst, type: e.type, resolved: e.resolved }));
  const color = { file: "#4f9cf9", function: "#7bd88f", class: "#f9c74f", module: "#c792ea" };
  const svg = d3.select(host).append("svg").attr("viewBox", [0, 0, width, height]);
  const sim = d3.forceSimulation(nodes)
    .force("link", d3.forceLink(links).id((d) => d.id).distance(60))
    .force("charge", d3.forceManyBody().strength(-140))
    .force("center", d3.forceCenter(width / 2, height / 2));
  const link = svg.append("g").selectAll("line").data(links).join("line")
    .attr("class", (d) => "gedge" + (d.resolved ? "" : " unresolved"));
  const node = svg.append("g").selectAll("circle").data(nodes).join("circle")
    .attr("class", "gnode").attr("r", 6)
    .attr("fill", (d) => color[d.kind] || "#8a94a6")
    .call(drag(sim));
  node.append("title").text((d) => `${d.kind}: ${d.name}`);
  const label = svg.append("g").selectAll("text").data(nodes).join("text")
    .attr("class", "glabel").attr("dx", 8).attr("dy", 3).text((d) => d.name);
  sim.on("tick", () => {
    link.attr("x1", (d) => d.source.x).attr("y1", (d) => d.source.y)
        .attr("x2", (d) => d.target.x).attr("y2", (d) => d.target.y);
    node.attr("cx", (d) => d.x).attr("cy", (d) => d.y);
    label.attr("x", (d) => d.x).attr("y", (d) => d.y);
  });
}

function drag(sim) {
  return d3.drag()
    .on("start", (event, d) => { if (!event.active) sim.alphaTarget(0.3).restart(); d.fx = d.x; d.fy = d.y; })
    .on("drag", (event, d) => { d.fx = event.x; d.fy = event.y; })
    .on("end", (event, d) => { if (!event.active) sim.alphaTarget(0); d.fx = null; d.fy = null; });
}

/* ---- Wiki content viewer ---- */
function renderWiki(filter) {
  const host = document.getElementById("wiki");
  host.innerHTML = "";
  const entries = (state.wiki && state.wiki.entries) || [];
  const q = (filter || "").toLowerCase();
  const shown = entries.filter((e) =>
    !q || e.text.toLowerCase().includes(q) || e.source_path.toLowerCase().includes(q));
  if (!shown.length) {
    host.innerHTML = notice(entries.length ? "No entries match your filter." :
      "No wiki content yet. Ingest documents to populate the wiki.");
    return;
  }
  shown.forEach((e) => {
    const div = document.createElement("div");
    div.className = "wiki-entry";
    div.innerHTML =
      `<div class="meta">${escapeHtml(e.source_path)} · ${escapeHtml(e.kind)}` +
      `<span class="badge">v${e.latest_version}</span>` +
      (e.tags && e.tags.length ? e.tags.map((t) => `<span class="badge">#${escapeHtml(t)}</span>`).join("") : "") +
      `</div>` +
      (e.summary ? `<div class="summary">${escapeHtml(e.summary)}</div>` : "") +
      `<pre>${escapeHtml(e.text)}</pre>`;
    host.appendChild(div);
  });
}

function notice(msg) { return `<div class="notice">${escapeHtml(msg)}</div>`; }
function escapeHtml(s) {
  return String(s).replace(/[&<>"']/g, (c) =>
    ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
}

async function init() {
  [state.structure, state.relationships, state.wiki] = await Promise.all([
    loadJSON("structure.json"), loadJSON("relationships.json"), loadJSON("wiki.json"),
  ]);
  document.querySelectorAll(".tab").forEach((t) =>
    t.addEventListener("click", () => switchView(t.dataset.view)));
  document.getElementById("wiki-search").addEventListener("input", (e) => renderWiki(e.target.value));
  const nEntries = (state.wiki && state.wiki.entries || []).length;
  const nNodes = (state.structure && state.structure.nodes || []).length;
  setStatus(`${nNodes} graph nodes · ${nEntries} wiki entries`);
  renderTree();
  renderWiki("");
}

document.addEventListener("DOMContentLoaded", init);
