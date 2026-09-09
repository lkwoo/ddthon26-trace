/* Knowledge Store — static D3 viewer.
 * Loads pre-generated export files (structure.json, relationships.json,
 * wiki.json) via fetch and renders three linked views. No build step.
 *
 * The Wiki view behaves like a real web wiki: a table-of-contents landing
 * page plus per-page navigation. The Structure Tree and Dependency Graph are
 * interactive — clicking a node opens its wiki page (or shows related info).
 */
"use strict";

const state = {
  structure: null,
  relationships: null,
  wiki: null,
  pages: new Map(),   // path -> { path, kind, tags, version, sections: [] }
  pageList: [],       // pages sorted by path
};

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

/* ================================================================== *
 *  Wiki — pages, table of contents, navigation                        *
 * ================================================================== */

/* Group latest chunks into "pages" keyed by source path. Each page holds its
 * sections (chunks) ordered by ordinal, so a file/document reads top-to-bottom
 * like a real wiki article. */
function buildPages(wiki) {
  const pages = new Map();
  const entries = (wiki && wiki.entries) || [];
  entries.forEach((e) => {
    let page = pages.get(e.source_path);
    if (!page) {
      page = { path: e.source_path, kind: e.kind, tags: new Set(),
               version: e.latest_version, sections: [] };
      pages.set(e.source_path, page);
    }
    (e.tags || []).forEach((t) => page.tags.add(t));
    page.version = Math.max(page.version, e.latest_version || 0);
    page.sections.push(e);
  });
  pages.forEach((p) => {
    p.sections.sort((a, b) => (a.ordinal || 0) - (b.ordinal || 0));
    p.tags = [...p.tags];
  });
  state.pages = pages;
  state.pageList = [...pages.values()].sort((a, b) => a.path.localeCompare(b.path));
}

function pageTitle(path) {
  const parts = String(path).split("/");
  return parts[parts.length - 1] || path;
}

function pageGroup(path) {
  const parts = String(path).split("/");
  return parts.length > 1 ? parts[0] : "(root)";
}

/* Bucket pages by their top-level directory for a tidy, folder-like TOC. */
function groupedPages(list) {
  const groups = new Map();
  list.forEach((p) => {
    const g = pageGroup(p.path);
    if (!groups.has(g)) groups.set(g, []);
    groups.get(g).push(p);
  });
  return [...groups.entries()].sort((a, b) => a[0].localeCompare(b[0]));
}

/* Pages structurally connected to `path` (via the code graph edges), so the
 * reader can hop between related articles like wiki cross-links. */
function relatedPages(path) {
  const struct = state.structure;
  if (!struct) return [];
  const localIds = new Set(struct.nodes.filter((n) => n.path === path).map((n) => n.id));
  if (!localIds.size) return [];
  const byId = new Map(struct.nodes.map((n) => [n.id, n]));
  const related = new Set();
  struct.edges.forEach((e) => {
    let other = null;
    if (localIds.has(e.src) && !localIds.has(e.dst)) other = byId.get(e.dst);
    else if (localIds.has(e.dst) && !localIds.has(e.src)) other = byId.get(e.src);
    if (other && other.path && other.path !== path && state.pages.has(other.path)) {
      related.add(other.path);
    }
  });
  return [...related].sort();
}

function currentFilter() {
  const el = document.getElementById("wiki-search");
  return (el && el.value || "").toLowerCase();
}

/* Sidebar table of contents. */
function renderWikiNav(filter) {
  const host = document.getElementById("wiki-nav");
  host.innerHTML = "";
  const q = (filter || "").toLowerCase();
  const list = state.pageList.filter((p) =>
    !q || p.path.toLowerCase().includes(q));

  const home = document.createElement("a");
  home.className = "wiki-nav-home";
  home.href = "#";
  home.textContent = "⌂ Contents";
  home.addEventListener("click", (ev) => { ev.preventDefault(); goHome(); });
  host.appendChild(home);

  if (!state.pageList.length) {
    host.appendChild(el("div", "notice-sm", "No wiki content yet."));
    return;
  }
  if (!list.length) {
    host.appendChild(el("div", "notice-sm", "No pages match your search."));
    return;
  }

  groupedPages(list).forEach(([group, pages]) => {
    const details = document.createElement("details");
    details.open = true;
    const summary = document.createElement("summary");
    summary.textContent = `${group} (${pages.length})`;
    details.appendChild(summary);
    pages.forEach((p) => {
      const a = document.createElement("a");
      a.className = "wiki-nav-item";
      a.dataset.path = p.path;
      a.href = pageHash(p.path);
      a.textContent = pageTitle(p.path);
      a.title = p.path;
      a.addEventListener("click", (ev) => { ev.preventDefault(); openWikiPage(p.path); });
      details.appendChild(a);
    });
    host.appendChild(details);
  });
  highlightActiveNav();
}

function highlightActiveNav(path) {
  document.querySelectorAll(".wiki-nav-item").forEach((a) =>
    a.classList.toggle("active", a.dataset.path === path));
}

/* Landing page: the full table of contents. */
function renderWikiHome() {
  const host = document.getElementById("wiki-content");
  host.innerHTML = "";
  highlightActiveNav(null);
  location.hash = "";

  if (!state.pageList.length) {
    host.innerHTML = notice("No wiki content yet. Ingest documents to populate the wiki.");
    return;
  }
  const header = document.createElement("div");
  header.className = "wiki-home-head";
  header.innerHTML =
    `<h2>Table of Contents</h2>` +
    `<p class="muted">${state.pageList.length} pages · ` +
    `${(state.wiki.entries || []).length} sections. Click a page to read it, ` +
    `or explore the Structure Tree / Dependency Graph and click a node to jump here.</p>`;
  host.appendChild(header);

  groupedPages(state.pageList).forEach(([group, pages]) => {
    const sec = document.createElement("section");
    sec.className = "toc-group";
    sec.appendChild(el("h3", "toc-group-title", `${group}`));
    const ul = document.createElement("ul");
    ul.className = "toc-list";
    pages.forEach((p) => {
      const li = document.createElement("li");
      const a = document.createElement("a");
      a.href = pageHash(p.path);
      a.textContent = pageTitle(p.path);
      a.addEventListener("click", (ev) => { ev.preventDefault(); openWikiPage(p.path); });
      li.appendChild(a);
      const meta = el("span", "toc-meta",
        ` · ${p.sections.length} section${p.sections.length === 1 ? "" : "s"} · ${p.kind}`);
      li.appendChild(meta);
      ul.appendChild(li);
    });
    sec.appendChild(ul);
    host.appendChild(sec);
  });
}

/* A single wiki article. */
function openWikiPage(path) {
  const page = state.pages.get(path);
  const host = document.getElementById("wiki-content");
  host.innerHTML = "";
  if (!page) { renderWikiHome(); return; }

  location.hash = pageHash(path);
  highlightActiveNav(path);
  host.scrollTop = 0;

  const crumb = document.createElement("div");
  crumb.className = "breadcrumb";
  const back = document.createElement("a");
  back.href = "#";
  back.textContent = "⌂ Contents";
  back.addEventListener("click", (ev) => { ev.preventDefault(); goHome(); });
  crumb.appendChild(back);
  crumb.appendChild(el("span", "crumb-sep", " / "));
  crumb.appendChild(el("span", "crumb-current", pageGroup(path)));
  host.appendChild(crumb);

  const head = document.createElement("div");
  head.className = "page-head";
  head.innerHTML =
    `<h2>${escapeHtml(pageTitle(path))}</h2>` +
    `<div class="meta">${escapeHtml(path)} · ${escapeHtml(page.kind)}` +
    `<span class="badge">v${page.version}</span>` +
    page.tags.map((t) => `<span class="badge">#${escapeHtml(t)}</span>`).join("") +
    `</div>`;
  host.appendChild(head);

  page.sections.forEach((s, i) => {
    const div = document.createElement("div");
    div.className = "wiki-section";
    div.id = `sec-${s.id}`;
    div.innerHTML =
      (page.sections.length > 1
        ? `<div class="section-label">Section ${i + 1}${s.kind ? " · " + escapeHtml(s.kind) : ""}</div>`
        : "") +
      (s.summary ? `<div class="summary">${escapeHtml(s.summary)}</div>` : "") +
      `<pre>${escapeHtml(s.text)}</pre>`;
    host.appendChild(div);
  });

  const related = relatedPages(path);
  if (related.length) {
    const rel = document.createElement("div");
    rel.className = "related-box";
    rel.appendChild(el("h3", "related-title", "Related pages"));
    const wrap = document.createElement("div");
    wrap.className = "related-chips";
    related.forEach((rp) => {
      const a = document.createElement("a");
      a.className = "chip";
      a.href = pageHash(rp);
      a.textContent = pageTitle(rp);
      a.title = rp;
      a.addEventListener("click", (ev) => { ev.preventDefault(); openWikiPage(rp); });
      wrap.appendChild(a);
    });
    rel.appendChild(wrap);
    host.appendChild(rel);
  }
}

function pageHash(path) { return "#page=" + encodeURIComponent(path); }

function goHome() { renderWikiHome(); }

/* Deep-link routing so tree/graph clicks (and the back/forward buttons) work. */
function routeFromHash() {
  const m = /^#page=(.+)$/.exec(location.hash);
  if (m) openWikiPage(decodeURIComponent(m[1]));
  else renderWikiHome();
}

/* Called from tree/graph node clicks. Navigate to the node's wiki page if one
 * exists; otherwise surface related info in-place. */
function navigateToNode(node, infoHostId, x, y) {
  if (node && node.path && state.pages.has(node.path)) {
    switchView("wiki");
    openWikiPage(node.path);
    return;
  }
  showNodeInfo(node, infoHostId, x, y);
}

function showNodeInfo(node, infoHostId, x, y) {
  const box = document.getElementById(infoHostId);
  if (!box) return;
  const hasPage = node && node.path && state.pages.has(node.path);
  const neighbors = nodeNeighbors(node && node.id);
  box.innerHTML =
    `<button class="info-close" title="Close">×</button>` +
    `<div class="info-name">${escapeHtml(node.name || "(unnamed)")}</div>` +
    `<div class="info-kind">${escapeHtml(node.kind || "node")}` +
    (node.path ? ` · ${escapeHtml(node.path)}` : "") + `</div>` +
    (hasPage ? `<button class="info-open">Open wiki page</button>` : "") +
    (neighbors.length
      ? `<div class="info-rel-title">Connected (${neighbors.length})</div>` +
        `<div class="info-chips">` +
        neighbors.map((n) =>
          `<span class="chip small" data-path="${escapeHtml(n.path || "")}" ` +
          `title="${escapeHtml(n.kind + (n.path ? " · " + n.path : ""))}">` +
          `${escapeHtml(n.name)}</span>`).join("") +
        `</div>`
      : `<div class="info-rel-title muted">No linked nodes.</div>`);
  box.hidden = false;

  box.querySelector(".info-close").addEventListener("click", () => { box.hidden = true; });
  const openBtn = box.querySelector(".info-open");
  if (openBtn) openBtn.addEventListener("click", () => {
    switchView("wiki"); openWikiPage(node.path); box.hidden = true;
  });
  box.querySelectorAll(".info-chips .chip").forEach((c) => {
    const p = c.dataset.path;
    if (p && state.pages.has(p)) {
      c.classList.add("linkable");
      c.addEventListener("click", () => {
        switchView("wiki"); openWikiPage(p); box.hidden = true;
      });
    }
  });
}

function nodeNeighbors(id) {
  const struct = state.structure;
  if (!struct || id == null) return [];
  const byId = new Map(struct.nodes.map((n) => [n.id, n]));
  const seen = new Set();
  const out = [];
  struct.edges.forEach((e) => {
    let other = null;
    if (e.src === id) other = byId.get(e.dst);
    else if (e.dst === id) other = byId.get(e.src);
    if (other && !seen.has(other.id)) { seen.add(other.id); out.push(other); }
  });
  return out;
}

/* ================================================================== *
 *  Structure tree (collapsible)                                       *
 * ================================================================== */
function buildHierarchy(structure) {
  const root = { name: "project", children: [] };
  if (!structure) return root;
  const files = structure.nodes.filter((n) => n.kind === "file");
  const byFile = {};
  files.forEach((f) => {
    byFile[f.id] = { id: f.id, name: f.name, kind: "file", path: f.path, children: [] };
    root.children.push(byFile[f.id]);
  });
  structure.edges
    .filter((e) => e.type === "contain")
    .forEach((e) => {
      const parent = byFile[e.src];
      const child = structure.nodes.find((n) => n.id === e.dst);
      if (parent && child)
        parent.children.push({ id: child.id, name: child.name, kind: child.kind, path: child.path });
    });
  return root;
}

function renderTree() {
  const host = document.getElementById("tree");
  host.innerHTML = "";
  const info = document.getElementById("tree-info");
  if (info) info.hidden = true;
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
    .attr("class", (d) => "node" + (d.data.path && state.pages.has(d.data.path) ? " has-page" : ""))
    .attr("transform", (d) => `translate(${d.y},${d.x})`);
  node.filter((d) => d.depth > 0)
    .style("cursor", "pointer")
    .on("click", (event, d) => {
      event.stopPropagation();
      navigateToNode(d.data, "tree-info", event.offsetX, event.offsetY);
    });
  node.append("circle").attr("r", 4);
  node.append("title").text((d) => d.data.path
    ? `${d.data.kind}: ${d.data.name}\n${d.data.path}` : d.data.name);
  node.append("text").attr("dy", "0.31em").attr("x", (d) => d.children ? -8 : 8)
    .attr("text-anchor", (d) => d.children ? "end" : "start")
    .text((d) => d.data.name);
}

/* ================================================================== *
 *  Dependency graph (force-directed)                                  *
 * ================================================================== */
function renderGraph() {
  const host = document.getElementById("graph");
  host.innerHTML = "";
  const info = document.getElementById("graph-info");
  if (info) info.hidden = true;
  if (typeof d3 === "undefined") { host.innerHTML = notice("D3 unavailable (offline)."); return; }
  const struct = state.structure;
  if (!struct || !struct.nodes.length) {
    host.innerHTML = notice("No graph data. Ingest code to populate the dependency graph.");
    return;
  }
  const width = host.clientWidth || 800, height = host.clientHeight || 600;
  const nodes = struct.nodes.map((n) => ({ id: n.id, name: n.name, kind: n.kind, path: n.path }));
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
    .attr("class", (d) => "gnode" + (d.path && state.pages.has(d.path) ? " has-page" : ""))
    .attr("r", 6)
    .attr("fill", (d) => color[d.kind] || "#8a94a6")
    .call(drag(sim));
  node.append("title").text((d) => `${d.kind}: ${d.name}` + (d.path ? `\n${d.path}` : ""));

  // Click a node → highlight its neighbourhood and show related info (with a
  // shortcut to its wiki page when one exists).
  node.on("click", (event, d) => {
    event.stopPropagation();
    const nb = new Set([d.id]);
    links.forEach((l) => {
      const s = l.source.id ?? l.source, t = l.target.id ?? l.target;
      if (s === d.id) nb.add(t);
      if (t === d.id) nb.add(s);
    });
    node.classed("dim", (o) => !nb.has(o.id)).classed("selected", (o) => o.id === d.id);
    link.classed("dim", (l) => {
      const s = l.source.id ?? l.source, t = l.target.id ?? l.target;
      return !(s === d.id || t === d.id);
    });
    showNodeInfo(d, "graph-info", event.offsetX, event.offsetY);
  });
  svg.on("click", () => {
    node.classed("dim", false).classed("selected", false);
    link.classed("dim", false);
    const box = document.getElementById("graph-info");
    if (box) box.hidden = true;
  });

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

/* ---- helpers ---- */
function el(tag, cls, text) {
  const n = document.createElement(tag);
  if (cls) n.className = cls;
  if (text != null) n.textContent = text;
  return n;
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
  buildPages(state.wiki);
  document.querySelectorAll(".tab").forEach((t) =>
    t.addEventListener("click", () => switchView(t.dataset.view)));
  document.getElementById("wiki-search").addEventListener("input", () => renderWikiNav(currentFilter()));
  window.addEventListener("hashchange", () => {
    if (document.getElementById("view-wiki").classList.contains("active")) routeFromHash();
  });
  const nEntries = (state.wiki && state.wiki.entries || []).length;
  const nNodes = (state.structure && state.structure.nodes || []).length;
  setStatus(`${state.pageList.length} pages · ${nNodes} graph nodes · ${nEntries} wiki entries`);
  renderWikiNav("");
  routeFromHash();
}

document.addEventListener("DOMContentLoaded", init);
