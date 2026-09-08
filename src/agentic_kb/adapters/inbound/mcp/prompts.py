"""PromptsProvider — static prompt templates (US-A5).

Pure text composition. No LLM/external calls (BR-M2/M12). ``onboarding`` gives a
new agent a fast path to project context; ``task`` focuses guidance on a named
task kind.
"""

from __future__ import annotations

PROMPT_NAMES = ("onboarding", "task")

_ONBOARDING = """\
You are working with an Agentic Knowledge Base for this project.
To understand the project quickly, use these MCP resources and tools in order:

1. Read resource `agentic-kb://structure` for the directory/module tree.
2. Read resource `agentic-kb://relationships` for module dependency/call edges.
3. Use the `query` tool (keyword or graph mode) to locate task-relevant symbols.
4. Read `agentic-kb://summary/{target}` for a specific file/module summary
   (engine structural summary + agent-authored deep notes, engine-first).
5. Use the `snippet` tool with a token budget to pull only the code you need.

Prefer these structured resources over reading whole files. When you produce a
deeper natural-language summary, persist it with the `update_note` tool.
"""

_TASK = """\
Task: {task_kind}

Approach using the knowledge base:
1. `query` for symbols/files relevant to "{task_kind}".
2. Inspect their `agentic-kb://summary/{{target}}` resources for context.
3. Pull focused code with the `snippet` tool (respect your token budget).
4. Follow module relationships via `agentic-kb://relationships/{{target}}`.
5. Record any durable findings with `update_note` so future sessions reuse them.
"""


class PromptNotFound(LookupError):
    """Raised when an unknown prompt name is requested."""


class PromptsProvider:
    def list_prompts(self) -> list[str]:
        return list(PROMPT_NAMES)

    def render(self, name: str, args: dict | None = None) -> str:
        args = args or {}
        if name == "onboarding":
            return _ONBOARDING
        if name == "task":
            task_kind = args.get("task_kind", "general")
            return _TASK.format(task_kind=task_kind)
        raise PromptNotFound(name)
