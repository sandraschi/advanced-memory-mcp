"""
FastMCP 2.14.1+ Sampling with Tools — Agentic Content Workflows (SEP-1577)

Meta-tools that delegate complex multi-step knowledge-management operations
to the client's LLM via ctx.sample().  The LLM receives real tool functions,
calls them autonomously, and returns a validated structured result.

Pattern:
  - Leaf tool functions: plain Python, type hints + docstrings → FastMCP makes schemas
  - ctx.sample(messages=..., tools=[fn,...], result_type=Model) → LLM orchestrates
  - result.result → validated Pydantic object

Only the meta-tools in this file use ctx.sample().
All other portmanteau_*.py files are leaf tools; they don't call the LLM.
"""

import logging
import os
import time
from collections import deque
from dataclasses import dataclass
from typing import Any

from fastmcp import Context
from pydantic import BaseModel

from advanced_memory.mcp.mcp_instance import mcp
from advanced_memory.mcp.tools.content_manager import (
    build_error_response,
    build_success_response,
)

logger = logging.getLogger(__name__)


# ── Token budget & rate limiter ───────────────────────────────────────────────
# Prevents runaway ctx.sample() loops from burning the user's context window.
# All limits are env-configurable so they can be raised without a code deploy.

_MAX_TOKENS_PER_CALL: int = int(os.environ.get("MEMOPS_MAX_TOKENS", "16000"))
_RATE_LIMIT_CALLS: int = int(os.environ.get("MEMOPS_RATE_LIMIT_CALLS", "3"))
_RATE_LIMIT_WINDOW: int = int(os.environ.get("MEMOPS_RATE_LIMIT_WINDOW", "60"))  # seconds

# Sliding window call log — timestamps of recent sampling invocations
_call_timestamps: deque = deque(maxlen=100)


@dataclass
class BudgetCheck:
    allowed: bool
    reason: str = ""
    tokens_cap: int = _MAX_TOKENS_PER_CALL
    calls_in_window: int = 0
    window_seconds: int = _RATE_LIMIT_WINDOW


def _check_budget(requested_tokens: int) -> BudgetCheck:
    """Enforce token cap and sliding-window rate limit before any ctx.sample() call."""
    now = time.monotonic()
    # Prune old timestamps outside the window
    cutoff = now - _RATE_LIMIT_WINDOW
    while _call_timestamps and _call_timestamps[0] < cutoff:
        _call_timestamps.popleft()

    calls_in_window = len(_call_timestamps)

    if calls_in_window >= _RATE_LIMIT_CALLS:
        return BudgetCheck(
            allowed=False,
            reason=(
                f"Rate limit: {calls_in_window}/{_RATE_LIMIT_CALLS} sampling calls "
                f"in the last {_RATE_LIMIT_WINDOW}s. "
                f"Wait or raise MEMOPS_RATE_LIMIT_CALLS env var."
            ),
            calls_in_window=calls_in_window,
        )

    if requested_tokens > _MAX_TOKENS_PER_CALL:
        return BudgetCheck(
            allowed=False,
            reason=(
                f"Token budget: requested {requested_tokens} > cap {_MAX_TOKENS_PER_CALL}. "
                f"Lower max_tokens or raise MEMOPS_MAX_TOKENS env var."
            ),
            calls_in_window=calls_in_window,
        )

    return BudgetCheck(allowed=True, calls_in_window=calls_in_window)


def _record_call():
    """Record a successful sampling call in the rate limiter window."""
    _call_timestamps.append(time.monotonic())


# ── Structured result types ───────────────────────────────────────────────────


class WorkflowResult(BaseModel):
    """Structured result returned by the sampling LLM for content workflows."""

    summary: str
    steps_taken: list[str]
    findings: list[dict]
    success: bool
    notes: str | None = None


class BatchResult(BaseModel):
    """Structured result returned by the sampling LLM for batch processing."""

    summary: str
    items_processed: int
    results: list[dict]
    success: bool
    errors: list[str] = []


# ── Leaf tool functions (passed as tools to ctx.sample) ──────────────────────
# Plain Python functions.  FastMCP generates schemas from type hints + docstrings.
# These call the real service layer — no mocks.


async def search_knowledge_base(query: str, max_results: int = 10) -> str:
    """
    Search the knowledge base for notes matching the query.
    Returns a markdown-formatted list of matching notes with titles and excerpts.
    Use boolean operators: AND, OR, NOT.  Phrase search: "exact phrase".
    """
    try:
        from advanced_memory.mcp.tools.search import search_notes

        results = await search_notes(query=query, results_per_page=max_results)
        if isinstance(results, str):
            return results
        if hasattr(results, "results") and results.results:
            lines = []
            for r in results.results:
                title = getattr(r, "title", "?")
                permalink = getattr(r, "permalink", "")
                excerpt = getattr(r, "excerpt", "")[:150]
                lines.append(f"- **{title}** ({permalink})\n  {excerpt}")
            return "\n".join(lines) or "(no results)"
        return "(no results)"
    except Exception as e:
        return f"ERROR: {e}"


async def read_knowledge_note(identifier: str) -> str:
    """
    Read the full markdown content of a note by its title or permalink.
    Returns the complete note text including observations and relations.
    """
    try:
        from advanced_memory.mcp.tools.read_note import read_note

        return await read_note(identifier=identifier)
    except Exception as e:
        return f"ERROR: {e}"


async def write_knowledge_note(title: str, content: str, folder: str = "inbox", tags: str = "") -> str:
    """
    Write a new note to the knowledge base.
    title: Note title (becomes the filename).
    content: Markdown content including optional [observation] lines and [[relations]].
    folder: Target folder, e.g. 'inbox', 'research', 'dev/mcp'.
    tags: Comma-separated tag list, e.g. 'python,mcp,fix'.
    Returns confirmation with the created file path.
    """
    try:
        from advanced_memory.mcp.tools.write_note import write_note

        tag_list = [t.strip() for t in tags.split(",") if t.strip()] if tags else []
        return await write_note(title=title, content=content, folder=folder, tags=tag_list)
    except Exception as e:
        return f"ERROR: {e}"


async def get_recent_notes(timeframe: str = "7d", max_results: int = 20) -> str:
    """
    Get recently created or modified notes from the knowledge base.
    timeframe: e.g. '1d', '7d', '30d', 'yesterday', 'last week'.
    Returns a markdown list of recent notes with titles and timestamps.
    """
    try:
        from advanced_memory.mcp.tools.recent_activity import recent_activity

        result = await recent_activity(timeframe=timeframe, page_size=max_results)
        if isinstance(result, dict) and result.get("results"):
            lines = []
            for r in result["results"]:
                title = r.get("title", "?")
                updated = r.get("updated_at", "")
                lines.append(f"- {title} ({updated})")
            return "\n".join(lines) or "(no recent notes)"
        return "(no recent notes)"
    except Exception as e:
        return f"ERROR: {e}"


async def list_knowledge_folder(folder_path: str) -> str:
    """
    List notes and subfolders in a knowledge base folder.
    folder_path: Relative path, e.g. 'dev/mcp', 'research', 'inbox'.
    Returns a directory listing with note titles.
    """
    try:
        from advanced_memory.mcp.tools.list_directory import list_directory

        result = await list_directory(dir_name=folder_path)
        if isinstance(result, str):
            return result
        return str(result)
    except Exception as e:
        return f"ERROR: {e}"


# ── Tool registry ─────────────────────────────────────────────────────────────

_TOOL_GROUPS: dict[str, list] = {
    "search": [search_knowledge_base, get_recent_notes],
    "read": [read_knowledge_note, search_knowledge_base],
    "write": [write_knowledge_note, read_knowledge_note, search_knowledge_base],
    "browse": [list_knowledge_folder, search_knowledge_base, get_recent_notes],
    "full": [
        search_knowledge_base,
        read_knowledge_note,
        write_knowledge_note,
        get_recent_notes,
        list_knowledge_folder,
    ],
}

_DEFAULT_TOOLS = [search_knowledge_base, read_knowledge_note, get_recent_notes]


def _resolve_tools(available_tools: list[str]) -> list:
    """Map tool group names → deduplicated Python callables."""
    seen: set[str] = set()
    resolved = []
    for name in available_tools:
        for fn in _TOOL_GROUPS.get(name, []):
            if fn.__name__ not in seen:
                seen.add(fn.__name__)
                resolved.append(fn)
    return resolved or _DEFAULT_TOOLS


# ── Meta-tools ────────────────────────────────────────────────────────────────


# @mcp.tool
async def agentic_content_workflow(
    workflow_prompt: str,
    available_tools: list[str],
    max_iterations: int = 5,
    max_tokens: int = _MAX_TOKENS_PER_CALL,
    ctx: Context = None,
) -> dict:
    """
    Execute agentic content workflows using FastMCP 2.14.1+ sampling with tools.

    Uses ctx.sample() with tools (SEP-1577) so the client's LLM autonomously
    orchestrates complex knowledge management operations without client round-trips.

    EFFICIENCY GAINS:
    - LLM autonomously decides tool usage and sequencing
    - No client mediation for multi-step knowledge workflows
    - Structured validation and error recovery

    TOKEN BUDGET (configurable via env vars):
    - MEMOPS_MAX_TOKENS: hard cap per call (default 16000)
    - MEMOPS_RATE_LIMIT_CALLS: max calls per window (default 3)
    - MEMOPS_RATE_LIMIT_WINDOW: sliding window in seconds (default 60)

    Args:
        workflow_prompt: Description of the workflow to execute
        available_tools: Tool groups: search, read, write, browse, full
        max_iterations: Maximum LLM-tool loops (default: 5, hint only)
        max_tokens: Token cap for this call (default: MEMOPS_MAX_TOKENS env var)

    Returns:
        Structured response with workflow execution results

    Example:
        result = await agentic_content_workflow(
            workflow_prompt="Find all notes about FastMCP sampling and summarise key points",
            available_tools=["search", "read"],
            max_tokens=8000,
        )
    """
    if not workflow_prompt:
        return build_error_response(
            error="No workflow prompt provided",
            error_code="MISSING_WORKFLOW_PROMPT",
            message="workflow_prompt is required",
            recovery_options=["Provide a clear description of the workflow to execute"],
        )

    if ctx is None:
        return build_error_response(
            error="No MCP context — sampling requires a live client session",
            error_code="NO_CONTEXT",
            message=(
                "Ensure this tool is called from a sampling-capable MCP client "
                "(Antigravity/Gemini ✓, Claude Desktop ✗ yet)"
            ),
            recovery_options=["Use Antigravity or another sampling-capable MCP client"],
        )

    # ── Token budget & rate limit guard ───────────────────────────────────────
    budget = _check_budget(max_tokens)
    if not budget.allowed:
        return build_error_response(
            error=budget.reason,
            error_code="BUDGET_EXCEEDED",
            message="Sampling call blocked by token budget / rate limiter",
            recovery_options=[
                f"Wait {_RATE_LIMIT_WINDOW}s for rate limit window to reset",
                "Raise MEMOPS_MAX_TOKENS or MEMOPS_RATE_LIMIT_CALLS env vars",
                "Reduce max_tokens parameter",
            ],
        )
    # ──────────────────────────────────────────────────────────────────────

    tools = _resolve_tools(available_tools or [])

    system_prompt = (
        "You are a knowledge management agent with access to a personal knowledge base. "
        "Use the provided tools to complete the requested workflow. "
        "Search before reading, read before writing. "
        "Be systematic and concise — report key findings, not raw note dumps."
    )

    logger.info(
        "Starting agentic_content_workflow via ctx.sample()",
        extra={
            "workflow": workflow_prompt[:80],
            "tools": [t.__name__ for t in tools],
            "token_cap": max_tokens,
            "rate_window_calls": budget.calls_in_window,
        },
    )

    try:
        _record_call()
        sampling_result = await ctx.sample(
            messages=workflow_prompt,
            system_prompt=system_prompt,
            tools=tools,
            result_type=WorkflowResult,
            max_tokens=max_tokens,
        )

        wf: WorkflowResult = sampling_result.result

        return build_success_response(
            operation="agentic_content_workflow",
            summary=wf.summary,
            result={
                "workflow_prompt": workflow_prompt,
                "steps_executed": wf.steps_taken,
                "findings": wf.findings,
                "notes": wf.notes,
                "execution_summary": {
                    "tools_available": [t.__name__ for t in tools],
                    "sampling_based": True,
                    "llm_orchestrated": True,
                    "tokens_cap": max_tokens,
                    "rate_calls_in_window": budget.calls_in_window + 1,
                },
            },
            success=wf.success,
        )

    except Exception as e:
        logger.error(f"agentic_content_workflow sampling failed: {e}", exc_info=True)
        return build_error_response(
            error=f"Sampling-based workflow failed: {e}",
            error_code="SAMPLING_ERROR",
            message="ctx.sample() raised an exception",
            recovery_options=[
                "Ensure the MCP client supports sampling (Claude Desktop does)",
                "Try a simpler workflow_prompt",
                "Check advanced-memory-mcp logs for details",
            ],
            diagnostic_info={
                "exception": str(e),
                "tools": [t.__name__ for t in tools],
            },
        )


# @mcp.tool
async def intelligent_batch_processor(
    items: list[dict[str, Any]],
    processing_goal: str,
    available_operations: list[str],
    batch_strategy: str = "parallel",
    max_tokens: int = _MAX_TOKENS_PER_CALL,
    ctx: Context = None,
) -> dict:
    """
    Intelligent batch processing of knowledge base items using FastMCP 2.14.1+ sampling.

    The client's LLM analyses each item, chooses the right knowledge operations,
    and orchestrates processing autonomously.

    TOKEN BUDGET (configurable via env vars):
    - MEMOPS_MAX_TOKENS: hard cap per call (default 16000)
    - MEMOPS_RATE_LIMIT_CALLS: max calls per window (default 3)
    - MEMOPS_RATE_LIMIT_WINDOW: sliding window in seconds (default 60)

    Args:
        items: List of items to process (each should have at least a 'title' or 'id' key)
        processing_goal: What you want to achieve, e.g. "summarise all notes about X"
        available_operations: Tool groups: search, read, write, browse, full
        batch_strategy: "parallel" or "sequential" (hint to the LLM, not enforced)
        max_tokens: Token cap for this call (default: MEMOPS_MAX_TOKENS env var)

    Returns:
        Batch processing results with per-item outcomes
    """
    if not items:
        return build_error_response(
            error="No items to process",
            error_code="EMPTY_ITEMS",
            message="items list cannot be empty",
            recovery_options=["Provide items to process"],
        )

    if not processing_goal:
        return build_error_response(
            error="No processing goal specified",
            error_code="MISSING_GOAL",
            message="processing_goal is required",
            recovery_options=["Specify what you want to achieve"],
        )

    if ctx is None:
        return build_error_response(
            error="No MCP context — sampling requires a live client session",
            error_code="NO_CONTEXT",
            message=(
                "Ensure this tool is called from a sampling-capable MCP client "
                "(Antigravity/Gemini ✓, Claude Desktop ✗ yet)"
            ),
            recovery_options=["Use Antigravity or another sampling-capable MCP client"],
        )

    # ── Token budget & rate limit guard ───────────────────────────────────────
    budget = _check_budget(max_tokens)
    if not budget.allowed:
        return build_error_response(
            error=budget.reason,
            error_code="BUDGET_EXCEEDED",
            message="Sampling call blocked by token budget / rate limiter",
            recovery_options=[
                f"Wait {_RATE_LIMIT_WINDOW}s for rate limit window to reset",
                "Raise MEMOPS_MAX_TOKENS or MEMOPS_RATE_LIMIT_CALLS env vars",
                "Reduce max_tokens parameter",
            ],
        )
    # ─────────────────────────────────────────────────────────────────────────

    tools = _resolve_tools(available_operations or [])

    workflow_prompt = (
        f"Process these {len(items)} items. Goal: {processing_goal}\n"
        f"Strategy: {batch_strategy}\n\n"
        f"Items:\n" + "\n".join(f"- {item}" for item in items[:50])  # safety cap
    )

    system_prompt = (
        f"You are an expert batch processing agent for a knowledge base. "
        f"Strategy: {batch_strategy}. "
        f"Goal: {processing_goal}. "
        f"Analyse each item and apply the most appropriate operations. "
        f"Report results for every item processed."
    )

    logger.info(
        "Starting intelligent_batch_processor via ctx.sample()",
        extra={
            "items": len(items),
            "goal": processing_goal[:60],
            "tools": [t.__name__ for t in tools],
            "token_cap": max_tokens,
            "rate_window_calls": budget.calls_in_window,
        },
    )

    try:
        _record_call()
        sampling_result = await ctx.sample(
            messages=workflow_prompt,
            system_prompt=system_prompt,
            tools=tools,
            result_type=BatchResult,
            max_tokens=max_tokens,
        )

        br: BatchResult = sampling_result.result

        return build_success_response(
            operation="intelligent_batch_processor",
            summary=br.summary,
            result={
                "processing_goal": processing_goal,
                "items_submitted": len(items),
                "items_processed": br.items_processed,
                "strategy_used": batch_strategy,
                "results": br.results,
                "errors": br.errors,
                "execution_summary": {
                    "tools_available": [t.__name__ for t in tools],
                    "sampling_based": True,
                    "llm_orchestrated": True,
                    "tokens_cap": max_tokens,
                    "rate_calls_in_window": budget.calls_in_window + 1,
                },
            },
            success=br.success,
        )

    except Exception as e:
        logger.error(f"intelligent_batch_processor sampling failed: {e}", exc_info=True)
        return build_error_response(
            error=f"Batch processing failed: {e}",
            error_code="BATCH_SAMPLING_ERROR",
            message="ctx.sample() raised an exception",
            recovery_options=[
                "Reduce number of items",
                "Simplify processing_goal",
                "Check advanced-memory-mcp logs for details",
            ],
            diagnostic_info={
                "exception": str(e),
                "item_count": len(items),
                "tools": [t.__name__ for t in tools],
            },
        )


# @mcp.tool
async def sampling_capabilities_status(ctx: Context = None) -> dict:
    """
    Check FastMCP 2.14.1+ sampling with tools capabilities and status.

    Reports SEP-1577 implementation status and confirms whether the current
    client session supports sampling.

    Returns:
        Status of sampling capabilities and feature availability.
    """
    sampling_available = ctx is not None

    capabilities = {
        "fastmcp_sampling_api": "ctx.sample(tools=[fn,...], result_type=Model)",
        "sep_1577_implemented": True,
        "sampling_available_this_session": sampling_available,
        "implementation_pattern": "Direct ctx.sample() — no wrapper classes",
        "available_tool_groups": list(_TOOL_GROUPS.keys()),
        "features": [
            "ctx.sample() with Python function tools",
            "Pydantic result_type with auto-validation and retry",
            "ctx.sample_step() for fine-grained control",
            "AnthropicSamplingHandler / OpenAISamplingHandler as fallback",
        ],
        "what_was_fixed": [
            "Removed broken mcp.ctx access (mcp has no .ctx attribute)",
            "Removed AgenticWorkflow manual loop (replaced by ctx.sample tools=)",
            "Replaced mock lambdas with real service calls",
            "Fixed parameter name: context → ctx so FastMCP injects it",
        ],
    }

    return build_success_response(
        operation="sampling_status",
        summary=(
            "Sampling operational"
            if sampling_available
            else "No active session — sampling unavailable outside live MCP connection"
        ),
        result=capabilities,
    )
