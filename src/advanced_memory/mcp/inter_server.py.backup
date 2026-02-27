"""
FastMCP 2.14.3 Sampling with Tools Implementation (SEP-1577)

This module implements SEP-1577: Sampling with tools, enabling agentic workflows
where servers borrow the client's LLM and autonomously control tool execution.

Core Features:
- ctx.sample() with tools parameter for automatic tool orchestration
- ctx.sample_step() for single-step control with inspection
- Structured output via result_type (Pydantic model validation)
- Sampling handlers: AnthropicSamplingHandler, OpenAISamplingHandler

Workflow Pattern:
1. Server calls ctx.sample() with tools and prompt
2. Client's LLM receives prompt + available tools
3. LLM decides which tools to call and with what parameters
4. Server executes tools automatically
5. Results fed back to LLM for next decision
6. Loop continues until LLM produces final answer

Benefits:
- Eliminates client round-trips for complex workflows
- LLM makes autonomous tool orchestration decisions
- Server controls execution flow and logic
- Structured validation of LLM outputs
"""

from collections.abc import Callable
from typing import Any

from pydantic import BaseModel


# Sampling Result Models
class SamplingResult(BaseModel):
    """Structured result from sampling operations."""

    content: str
    tool_calls: list[dict[str, Any]] = []
    finished: bool = True
    metadata: dict[str, Any] = {}


class ToolSpec(BaseModel):
    """Specification for a tool that can be used in sampling."""

    name: str
    description: str
    parameters: dict[str, Any]
    function: Callable


class SamplingConfig(BaseModel):
    """Configuration for sampling operations."""

    max_iterations: int = 10
    temperature: float = 0.7
    tools: list[ToolSpec] = []
    result_type: type[BaseModel] | None = None
    system_prompt: str | None = None


class AgenticWorkflow:
    """
    Agentic workflow manager using FastMCP 2.14.3 sampling with tools.

    Enables servers to orchestrate complex multi-step operations by borrowing
    the client's LLM for decision-making and tool execution control.
    """

    def __init__(self, ctx: Any, config: SamplingConfig):
        """
        Initialize agentic workflow.

        Args:
            ctx: FastMCP Context object with sampling capability
            config: Sampling configuration
        """
        self.ctx = ctx
        self.config = config
        self.execution_history: list[dict[str, Any]] = []
        self.iteration_count = 0

    async def execute_workflow(self, initial_prompt: str) -> SamplingResult:
        """
        Execute a complete agentic workflow using sampling with tools.

        Args:
            initial_prompt: Initial prompt to start the workflow

        Returns:
            Final sampling result after workflow completion
        """
        current_prompt = initial_prompt
        self.iteration_count = 0

        while self.iteration_count < self.config.max_iterations:
            self.iteration_count += 1

            # Single sampling step
            step_result = await self.ctx.sample_step(
                messages=[{"role": "user", "content": current_prompt}],
                tools=self._format_tools_for_sampling(),
                temperature=self.config.temperature,
                system=self.config.system_prompt,
            )

            # Record execution step
            self.execution_history.append(
                {
                    "iteration": self.iteration_count,
                    "prompt": current_prompt,
                    "step_result": step_result.model_dump()
                    if hasattr(step_result, "model_dump")
                    else step_result,
                    "tool_calls": step_result.tool_calls
                    if hasattr(step_result, "tool_calls")
                    else [],
                }
            )

            # Execute tools if any were called
            if step_result.tool_calls:
                tool_results = await self._execute_tool_calls(step_result.tool_calls)

                # Build next prompt with tool results
                current_prompt = self._build_next_prompt(current_prompt, tool_results)

                # Check if workflow should continue
                if self._should_finish_workflow(tool_results):
                    break
            else:
                # No tools called, workflow complete
                break

        # Return final result
        final_content = self._extract_final_content()
        return SamplingResult(
            content=final_content,
            tool_calls=self.execution_history[-1]["tool_calls"] if self.execution_history else [],
            finished=True,
            metadata={
                "iterations": self.iteration_count,
                "execution_history": self.execution_history,
                "total_tools_executed": sum(len(h["tool_calls"]) for h in self.execution_history),
            },
        )

    def _format_tools_for_sampling(self) -> list[dict[str, Any]]:
        """Format tools for sampling API."""
        formatted_tools = []
        for tool in self.config.tools:
            formatted_tools.append(
                {"name": tool.name, "description": tool.description, "parameters": tool.parameters}
            )
        return formatted_tools

    async def _execute_tool_calls(self, tool_calls: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Execute the tools called by the LLM."""
        results = []

        for tool_call in tool_calls:
            try:
                tool_name = tool_call.get("name")
                tool_args = tool_call.get("arguments", {})

                # Find and execute the tool
                tool_spec = next((t for t in self.config.tools if t.name == tool_name), None)
                if tool_spec:
                    result = await tool_spec.function(**tool_args)
                    results.append(
                        {
                            "tool_name": tool_name,
                            "args": tool_args,
                            "result": result,
                            "success": True,
                        }
                    )
                else:
                    results.append(
                        {
                            "tool_name": tool_name,
                            "args": tool_args,
                            "error": f"Tool '{tool_name}' not found",
                            "success": False,
                        }
                    )

            except Exception as e:
                results.append(
                    {
                        "tool_name": tool_call.get("name"),
                        "args": tool_call.get("arguments", {}),
                        "error": str(e),
                        "success": False,
                    }
                )

        return results

    def _build_next_prompt(self, current_prompt: str, tool_results: list[dict[str, Any]]) -> str:
        """Build the next prompt incorporating tool results."""
        result_summary = "\n\nTool execution results:\n"
        for result in tool_results:
            if result["success"]:
                result_summary += f"✅ {result['tool_name']}: {result['result']}\n"
            else:
                result_summary += f"❌ {result['tool_name']}: {result['error']}\n"

        return (
            current_prompt
            + result_summary
            + "\n\nContinue with the next step, or provide final answer if complete."
        )

    def _should_finish_workflow(self, tool_results: list[dict[str, Any]]) -> bool:
        """Determine if the workflow should finish based on tool results."""
        # Simple heuristic: finish if no successful tool executions
        successful_tools = [r for r in tool_results if r["success"]]
        return len(successful_tools) == 0

    def _extract_final_content(self) -> str:
        """Extract the final content from the workflow."""
        if self.execution_history:
            # Use the last step's content as final answer
            last_step = self.execution_history[-1]
            return last_step.get("step_result", {}).get("content", "Workflow completed")
        return "Workflow completed without execution history"


# Convenience functions for common use cases


async def sample_with_tools(
    ctx: Any,
    prompt: str,
    tools: list[ToolSpec],
    max_iterations: int = 5,
    result_type: type[BaseModel] | None = None,
    system_prompt: str | None = None,
) -> SamplingResult:
    """
    Convenience function for sampling with tools using FastMCP 2.14.3.

    Args:
        ctx: FastMCP context with sampling capability
        prompt: Initial prompt for the LLM
        tools: List of tools available for the LLM to use
        max_iterations: Maximum number of LLM-tool loops
        result_type: Optional Pydantic model for structured output validation
        system_prompt: Optional system prompt

    Returns:
        SamplingResult with final content and execution metadata

    Example:
        result = await sample_with_tools(
            ctx,
            "Process these 100 notes and create a summary",
            [prettify_tool, analyze_tool, summarize_tool],
            max_iterations=10
        )
    """
    config = SamplingConfig(
        max_iterations=max_iterations,
        tools=tools,
        result_type=result_type,
        system_prompt=system_prompt,
    )

    workflow = AgenticWorkflow(ctx, config)
    return await workflow.execute_workflow(prompt)


def create_tool_spec(
    name: str, description: str, function: Callable, parameters: dict[str, Any]
) -> ToolSpec:
    """
    Create a tool specification for use in sampling operations.

    Args:
        name: Tool name
        description: Tool description for LLM
        function: Callable to execute
        parameters: JSON schema for tool parameters

    Returns:
        ToolSpec for sampling operations
    """
    return ToolSpec(name=name, description=description, parameters=parameters, function=function)
