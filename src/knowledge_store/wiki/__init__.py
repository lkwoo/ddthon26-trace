"""U7 — Wiki Export & Web Viewer.

WikiExporter serializes the knowledge store into static JSON/HTML artifacts
(Application Design Q8) that the decoupled static D3 viewer loads via ``file://``.
"""

from knowledge_store.wiki.exporter import WikiExporter

__all__ = ["WikiExporter"]
