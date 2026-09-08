"""Built-in CSS for the web viewer (no external CDN/fonts — local, offline)."""

CSS = """\
* { box-sizing: border-box; }
body { font-family: system-ui, sans-serif; margin: 0; color: #222; }
nav { background: #24292f; padding: .6rem 1rem; }
nav a { color: #fff; text-decoration: none; margin-right: .5rem; }
main { padding: 1rem 1.5rem; max-width: 1000px; }
footer { padding: .8rem 1.5rem; color: #666; font-size: .85rem; border-top: 1px solid #eee; }
h1 { font-size: 1.4rem; }
details { margin-left: 1rem; }
summary { cursor: pointer; font-weight: 600; }
ul { list-style: none; padding-left: 1rem; }
li.file a { color: #36c; text-decoration: none; }
pre { background: #f6f8fa; padding: .6rem; overflow-x: auto; border-radius: 6px; }
code { font-family: ui-monospace, monospace; background: #f0f0f0; padding: 0 .2rem; }
pre code { background: none; padding: 0; }
.banner { background: #fff8e1; border: 1px solid #f0d060; padding: .6rem; border-radius: 6px; margin: .6rem 0; }
.badge { display: inline-block; font-size: .75rem; padding: .1rem .5rem; border-radius: 10px; margin-bottom: .4rem; }
.badge.engine { background: #e6f0ff; color: #1a4; }
.badge.note { background: #f0e6ff; color: #63c; }
section { border-top: 1px solid #eee; padding-top: .6rem; margin-top: .6rem; }
.note .meta { color: #888; font-size: .8rem; }
.kind { color: #888; font-size: .8rem; }
.empty { color: #888; }
svg.graph text { font-size: .8rem; fill: #333; }
"""
