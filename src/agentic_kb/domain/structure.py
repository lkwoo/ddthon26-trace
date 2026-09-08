"""Pure structure-tree construction from a list of source files (US-A1.1, US-H1)."""

from __future__ import annotations

from ..domain.models import SourceFile, StructureTree, TreeNode


def build_structure_tree(files: list[SourceFile]) -> StructureTree:
    """Build a deterministic directory/file tree from relative paths."""
    # Nested dict of dirs; files stored under a sentinel key.
    root: dict = {"__dirs__": {}, "__files__": []}

    for f in sorted(files, key=lambda x: x.path):
        parts = f.path.split("/")
        cursor = root
        for part in parts[:-1]:
            cursor = cursor["__dirs__"].setdefault(part, {"__dirs__": {}, "__files__": []})
        cursor["__files__"].append(parts[-1])

    def to_node(name: str, path: str, node: dict) -> TreeNode:
        children: list[TreeNode] = []
        for dname in sorted(node["__dirs__"]):
            child_path = f"{path}/{dname}" if path else dname
            children.append(to_node(dname, child_path, node["__dirs__"][dname]))
        for fname in sorted(node["__files__"]):
            child_path = f"{path}/{fname}" if path else fname
            children.append(TreeNode(path=child_path, kind="file", name=fname))
        return TreeNode(path=path, kind="dir", name=name, children=tuple(children))

    return StructureTree(root=to_node("", "", root))
