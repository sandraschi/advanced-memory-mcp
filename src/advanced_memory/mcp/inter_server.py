"""
FastMCP 2.14.1+ Sampling Utilities (SEP-1577)

Minimal module kept for backward-compat imports.
The old AgenticWorkflow / sample_with_tools / create_tool_spec approach
is OBSOLETE — replaced by ctx.sample(tools=[fn1, fn2], result_type=Model)
which FastMCP handles natively.

See inter_server_tools.py for the correct pattern.
"""

# Nothing to export.  Any code that imported AgenticWorkflow / sample_with_tools /
# create_tool_spec should be updated to use ctx.sample() directly.
