"""Content AI enrichment services — summarize, enhance, generate.

Extracted verbatim from content_manager.py (lines 2104-2408) during
Phase 1 of the 2.0 migration (ARCHITECTURE_2_0.md). Pure move, no
behavior changes. Legacy names: _summarize_operation,
_enhance_operation, _generate_operation. The only adaptation:
_generate_operation called _write_operation, which now lives in
services.content.crud as write_note (same signature and semantics).
"""

from loguru import logger

from advanced_memory.mcp.tools.utils import (
    build_error_response,
    build_success_response,
)
from advanced_memory.services.content.crud import write_note
from advanced_memory.utils import parse_tags

TagType = list[str] | str | None


async def summarize_note(active_project, identifier: str) -> dict:
    """Summarize a note using LLM."""
    try:
        # Read the note first
        from advanced_memory.mcp.tools.read_note import read_note

        note_content = await (read_note.fn if hasattr(read_note, "fn") else read_note)(
            identifier=identifier, project=active_project.name
        )

        if not note_content or note_content.startswith("# Error"):
            return f"# Error\n\nCould not read note: {identifier}\n\n{note_content}"

        # Use LLM to summarize
        from advanced_memory.services.llm_client import get_llm_client

        llm = get_llm_client()

        system_prompt = """You are a summarization assistant. Create a concise, informative summary of the note content.

The summary should:
1. Capture the main points and key information
2. Be clear and well-structured
3. Preserve important details and context
4. Use markdown formatting for readability

Return the summary as plain text (not JSON)."""

        # Use string concatenation to avoid f-string parsing of JSON curly braces in content
        note_preview = note_content[:4000]
        prompt = f"Summarize this note:\n\n{note_preview}"

        summary = await llm.generate(prompt, system_prompt, max_tokens=1000, temperature=0.3)

        return f"""# Note Summary

**Note:** {identifier}

---

## Summary

{summary}

---

**Original note length:** {len(note_content)} characters
**Summary length:** {len(summary)} characters
"""

    except Exception as e:
        logger.error(f"Summarization error: {e}", exc_info=True)
        return build_error_response(
            error="LLM service unavailable",
            error_code="LLM_UNAVAILABLE",
            message="Could not generate note summary",
            recovery_options=[
                "Configure an LLM provider using adn_llm('select_model', provider='ollama', model='llama3')",
                "Check LLM service is running (ollama serve, LMStudio, etc.)",
                "Try again if it's a temporary service issue",
            ],
            diagnostic_info={"error_details": str(e), "operation": "summarize"},
            urgency="medium",
        )


async def enhance_note(
    active_project,
    identifier: str,
    enhancement_instruction: str | None,
    update_content: bool = True,
    update_style: bool = True,
    add_bibliography: bool = False,
    add_examples: bool = False,
    add_context: bool = False,
    expand_sections: bool = False,
    update_stale_tech: bool = False,
) -> str:
    """Enhance a note using LLM. Supports batch-upgrading weak-LLM notes with SOTA LLM."""
    try:
        # Read the note first
        from advanced_memory.mcp.tools.read_note import read_note

        note_content = await (read_note.fn if hasattr(read_note, "fn") else read_note)(
            identifier=identifier, project=active_project.name
        )

        if not note_content or note_content.startswith("# Error"):
            return build_error_response(
                error="Could not read note",
                error_code="NOTE_NOT_FOUND",
                message=f"Failed to read note '{identifier}' before enhancement",
                recovery_options=[
                    "Verify identifier with adn_content('read', identifier='...')",
                    "Use full permalink if note is in a folder",
                ],
                diagnostic_info={"identifier": identifier},
                urgency="medium",
            )

        # Use LLM to enhance
        from advanced_memory.services.llm_client import get_llm_client

        llm = get_llm_client()

        from datetime import datetime

        instruction = enhancement_instruction or ""
        enhancement_tasks = []
        if update_content:
            enhancement_tasks.append(
                "Fix typos, spelling, and factual errors (e.g. Paris is capital of France not Spain)"
            )
            enhancement_tasks.append(
                "Update biographical info if relevant: if the note mentions a person who died after "
                "the note was written, add their death date and any notable later-life events"
            )
        if update_style:
            enhancement_tasks.append("Improve structure, clarity, readability, and organization")
        if add_examples:
            enhancement_tasks.append("Add concrete examples, illustrations, or case studies where relevant")
        if add_context:
            enhancement_tasks.append("Add background, definitions, and explain why the topic matters")
        if expand_sections:
            enhancement_tasks.append(
                "Expand bullet points and skeletal sections into full paragraphs; turn outlines into complete notes"
            )
        if update_stale_tech:
            enhancement_tasks.append(
                "Stale tech/version check: if the note references specific software versions (e.g. FastMCP 2.10, "
                "Python 3.11) that you know are outdated, update version references and add a brief migration note "
                "for breaking changes. If uncertain, add a prominent callout: 'Note: verify against current docs.' "
                "Prefer flagging uncertainty over guessing version numbers."
            )
        if add_bibliography:
            enhancement_tasks.append("Add a References/Bibliography section with relevant sources if applicable")
        if not enhancement_tasks:
            enhancement_tasks.append("Improve the note while preserving all original content and meaning")
        if instruction:
            enhancement_tasks.append(f"Additional instruction: {instruction}")

        today = datetime.now().strftime("%Y-%m-%d")
        system_prompt = f"""You are a content enhancement assistant. Today's date: {today}. Enhance notes by:
{chr(10).join(f"{i + 1}. {t}" for i, t in enumerate(enhancement_tasks))}

Always preserve the original meaning and key information. For biographical updates, use current knowledge (today is {today}) to add death dates or life events that occurred after the note was written. Return the enhanced note body in markdown format (no frontmatter)."""

        # Use string concatenation to avoid f-string parsing of JSON curly braces in content
        note_preview = note_content[:4000]
        custom_instruction = f"\n\nCustom instruction: {instruction}" if instruction else ""
        prompt = f"Enhance this note:\n\n{note_preview}{custom_instruction}\n\nReturn the complete enhanced note body (markdown, no YAML frontmatter)."

        enhanced_content = await llm.generate(prompt, system_prompt, max_tokens=4000, temperature=0.5)

        # Strip frontmatter from LLM response if present (we preserve existing frontmatter)
        from advanced_memory.file_utils import has_frontmatter, remove_frontmatter

        if has_frontmatter(enhanced_content):
            try:
                enhanced_content = remove_frontmatter(enhanced_content)
            except Exception:
                pass  # Use as-is if parse fails

        # Update the note with enhanced content (replace_body preserves frontmatter)
        from advanced_memory.mcp.tools.edit_note import edit_note

        edit_result = await (edit_note.fn if hasattr(edit_note, "fn") else edit_note)(
            identifier=identifier,
            operation="replace_body",
            content=enhanced_content,
            project=active_project.name,
        )

        # edit_note returns error string on failure (does not raise)
        if isinstance(edit_result, str) and (
            edit_result.startswith("# Edit Failed") or edit_result.startswith("# Error")
        ):
            return build_error_response(
                error="Could not persist enhanced content",
                error_code="EDIT_FAILED",
                message=f"LLM generated enhanced content ({len(enhanced_content)} chars) but edit_note failed to write it",
                recovery_options=[
                    "Check the note exists with adn_content('read', identifier='...')",
                    "Use full permalink (e.g. content/strawberry-facts-test)",
                    "Restart MCP server to ensure replace_body fix is loaded",
                ],
                diagnostic_info={
                    "identifier": identifier,
                    "edit_error": edit_result[:500],
                },
                urgency="medium",
            )

        return build_success_response(
            operation="enhance",
            summary=f"Note '{identifier}' enhanced and updated ({len(note_content)} -> {len(enhanced_content)} chars)",
            content=f"""# Note Enhanced

**Note:** {identifier}

The note has been enhanced and updated with improved structure, clarity, and readability.

**Original length:** {len(note_content)} characters
**Enhanced length:** {len(enhanced_content)} characters
""",
            identifier=identifier,
            original_length=len(note_content),
            enhanced_length=len(enhanced_content),
        )

    except Exception as e:
        logger.error(f"Enhancement error: {e}", exc_info=True)
        return build_error_response(
            error="LLM service unavailable",
            error_code="LLM_UNAVAILABLE",
            message="Could not enhance note content",
            recovery_options=[
                "Configure an LLM provider using adn_llm('select_model', provider='ollama', model='llama3')",
                "Check LLM service is running (ollama serve, LMStudio, etc.)",
                "Try again if it's a temporary service issue",
            ],
            diagnostic_info={"error_details": str(e), "operation": "enhance"},
            urgency="medium",
        )


async def generate_note(active_project, topic: str, folder: str | None, tags: TagType, entity_type: str) -> str:
    """Generate new note content using LLM."""
    try:
        from advanced_memory.services.llm_client import get_llm_client

        llm = get_llm_client()

        system_prompt = """You are a content generation assistant for a knowledge management system.

Generate comprehensive, well-structured note content on the given topic. The content should:
1. Be informative and accurate
2. Use proper markdown formatting
3. Include clear headings and structure
4. Be suitable for a knowledge base (Zettelkasten-style)
5. Include relevant details and examples

Return the complete note content in markdown format."""

        prompt = f"""Generate a comprehensive note on: {topic}

Create a well-structured markdown note with:
- Clear title/heading
- Introduction
- Main content sections
- Examples if applicable
- Key takeaways

Make it informative and useful for a knowledge base."""

        generated_content = await llm.generate(prompt, system_prompt, max_tokens=3000, temperature=0.7)

        # Extract title from first line
        first_line = generated_content.split("\n")[0].lstrip("#").strip()
        title = first_line if first_line else topic.title()

        # Use default folder if not provided
        target_folder = folder or "inbox"

        # Parse tags
        tag_list = parse_tags(tags) if tags else []

        # Create the note
        return await write_note(
            active_project,
            title,
            generated_content,
            target_folder,
            tag_list,
            entity_type,
        )

    except Exception as e:
        logger.error(f"Content generation error: {e}", exc_info=True)
        return build_error_response(
            error="LLM service unavailable",
            error_code="LLM_UNAVAILABLE",
            message="Could not generate note content",
            recovery_options=[
                "Configure an LLM provider using adn_llm('select_model', provider='ollama', model='llama3')",
                "Check LLM service is running (ollama serve, LMStudio, etc.)",
                "Try again if it's a temporary service issue",
            ],
            diagnostic_info={"error_details": str(e), "operation": "generate"},
            urgency="medium",
        )
