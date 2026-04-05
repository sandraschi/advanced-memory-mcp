"""Google Gemini import service for Advanced Memory."""

import logging
from datetime import datetime
from typing import Any

from advanced_memory.importers.base import Importer
from advanced_memory.importers.utils import clean_filename, format_timestamp
from advanced_memory.markdown.schemas import EntityFrontmatter, EntityMarkdown
from advanced_memory.schemas.importer import ChatImportResult

logger = logging.getLogger(__name__)


class GeminiImporter(Importer):
    """Service for importing Google Gemini conversations."""

    async def import_data(
        self, source_data: Any, destination_folder: str, **kwargs: Any
    ) -> ChatImportResult:
        """Import conversations from Gemini JSON export.

        Args:
            source_data: Gemini conversations JSON data (array or object with conversations array).
            destination_folder: Destination folder within the project.
            **kwargs: Additional keyword arguments.

        Returns:
            ChatImportResult containing statistics and status of the import.
        """
        try:
            # Ensure the destination folder exists
            self.ensure_folder_exists(destination_folder)

            # Handle different JSON structures
            conversations = self._extract_conversations(source_data)

            # Process each conversation
            messages_imported = 0
            chats_imported = 0

            for chat in conversations:
                # Convert to entity
                entity = self._format_chat_content(destination_folder, chat)

                # Write file
                file_path = self.base_path / f"{entity.frontmatter.metadata['permalink']}.md"
                await self.write_entity(entity, file_path)

                # Count messages
                msg_count = self._count_messages(chat)
                chats_imported += 1
                messages_imported += msg_count

            return ChatImportResult(
                import_count={"conversations": chats_imported, "messages": messages_imported},
                success=True,
                conversations=chats_imported,
                messages=messages_imported,
            )

        except Exception as e:  # pragma: no cover
            logger.exception("Failed to import Gemini conversations")
            return self.handle_error("Failed to import Gemini conversations", e)  # pyright: ignore [reportReturnType]

    def _extract_conversations(self, source_data: Any) -> list[dict[str, Any]]:
        """Extract conversations array from various JSON structures.

        Args:
            source_data: JSON data (could be array, object with 'conversations', etc.).

        Returns:
            List of conversation objects.
        """
        # If it's already a list, return it
        if isinstance(source_data, list):
            return source_data

        # If it's an object, try common keys
        if isinstance(source_data, dict):
            # Try common keys for conversation arrays
            for key in ["conversations", "chats", "data", "items"]:
                if key in source_data and isinstance(source_data[key], list):
                    return source_data[key]

            # If single conversation object, wrap in list
            if "title" in source_data or "name" in source_data or "messages" in source_data:
                return [source_data]

        # Fallback: empty list
        return []

    def _count_messages(self, conversation: dict[str, Any]) -> int:
        """Count messages in a conversation.

        Args:
            conversation: Conversation data.

        Returns:
            Number of messages.
        """
        # Try different message array keys
        for key in ["messages", "chat_messages", "items", "parts"]:
            if key in conversation and isinstance(conversation[key], list):
                return len(conversation[key])

        return 0

    def _format_chat_content(
        self, folder: str, conversation: dict[str, Any]
    ) -> EntityMarkdown:  # pragma: no cover
        """Convert chat conversation to Advanced Memory entity.

        Args:
            folder: Destination folder name.
            conversation: Gemini conversation data.

        Returns:
            EntityMarkdown instance representing the conversation.
        """
        # Extract title/name
        title = (
            conversation.get("title")
            or conversation.get("name")
            or conversation.get("id")
            or "Untitled Conversation"
        )

        # Extract timestamps
        created_at = self._extract_timestamp(conversation, "created_at", "created", "create_time")
        modified_at = (
            self._extract_timestamp(conversation, "updated_at", "updated", "update_time")
            or created_at
        )

        # Generate permalink
        date_prefix = (
            datetime.fromtimestamp(created_at).strftime("%Y%m%d")
            if created_at
            else datetime.now().strftime("%Y%m%d")
        )
        clean_title = clean_filename(title)

        # Format content
        content = self._format_chat_markdown(
            title=title,
            conversation=conversation,
            created_at=created_at,
            modified_at=modified_at,
        )

        # Create entity
        entity = EntityMarkdown(
            frontmatter=EntityFrontmatter(
                metadata={
                    "type": "conversation",
                    "title": title,
                    "created": format_timestamp(created_at)
                    if created_at
                    else format_timestamp(datetime.now().timestamp()),
                    "modified": format_timestamp(modified_at)
                    if modified_at
                    else format_timestamp(datetime.now().timestamp()),
                    "permalink": f"{folder}/{date_prefix}-{clean_title}",
                }
            ),
            content=content,
        )

        return entity

    def _extract_timestamp(self, data: dict[str, Any], *keys: str) -> float | None:
        """Extract timestamp from conversation data using multiple possible keys.

        Args:
            data: Conversation data.
            *keys: Possible keys to check.

        Returns:
            Unix timestamp or None.
        """
        for key in keys:
            if key in data:
                value = data[key]
                if isinstance(value, int | float):
                    return float(value)
                if isinstance(value, str):
                    try:
                        # Try ISO format
                        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
                        return dt.timestamp()
                    except ValueError:
                        try:
                            # Try unix timestamp as string
                            return float(value)
                        except ValueError:
                            pass
        return None

    def _format_chat_markdown(
        self,
        title: str,
        conversation: dict[str, Any],
        created_at: float | None,
        modified_at: float | None,
    ) -> str:  # pragma: no cover
        """Format chat as clean markdown.

        Args:
            title: Chat title.
            conversation: Conversation data.
            created_at: Creation timestamp.
            modified_at: Modification timestamp.

        Returns:
            Formatted markdown content.
        """
        # Start with title
        lines = [f"# {title}\n"]

        # Extract messages from various possible structures
        messages = self._extract_messages(conversation)

        # Format each message
        for msg in messages:
            # Get author/role
            author = self._get_message_author(msg)
            ts = (
                format_timestamp(msg.get("timestamp") or msg.get("created_at") or created_at)
                if msg.get("timestamp") or msg.get("created_at") or created_at
                else ""
            )

            # Add message header
            if ts:
                lines.append(f"### {author} ({ts})")
            else:
                lines.append(f"### {author}")

            # Add message content
            content = self._get_message_content(msg)
            if content:
                lines.append(content)

            # Add spacing
            lines.append("")

        return "\n".join(lines)

    def _extract_messages(self, conversation: dict[str, Any]) -> list[dict[str, Any]]:
        """Extract messages array from conversation.

        Args:
            conversation: Conversation data.

        Returns:
            List of message objects.
        """
        # Try different keys for messages array
        for key in ["messages", "chat_messages", "items", "parts", "history"]:
            if key in conversation and isinstance(conversation[key], list):
                return conversation[key]

        # If no messages array, return empty
        return []

    def _get_message_author(self, message: dict[str, Any]) -> str:
        """Extract author/role from message.

        Args:
            message: Message data.

        Returns:
            Author name (User, Gemini, Model, etc.).
        """
        # Try different role/author keys
        role = (
            message.get("role")
            or message.get("author")
            or message.get("sender")
            or message.get("type")
            or "Unknown"
        )

        # Normalize role names
        role_lower = str(role).lower()
        if role_lower in ["user", "human"]:
            return "User"
        elif role_lower in ["model", "assistant", "gemini", "ai", "bot"]:
            return "Gemini"
        else:
            return str(role).title()

    def _get_message_content(self, message: dict[str, Any]) -> str:
        """Extract clean message content.

        Args:
            message: Message data.

        Returns:
            Cleaned message content.
        """
        # Try different content keys
        content = (
            message.get("content")
            or message.get("text")
            or message.get("message")
            or message.get("parts")
            or ""
        )

        # Handle different content types
        if isinstance(content, str):
            return content
        elif isinstance(content, list):
            # Join list of strings or extract text from parts
            parts = []
            for part in content:
                if isinstance(part, str):
                    parts.append(part)
                elif isinstance(part, dict):
                    # Try to extract text from part object
                    text = part.get("text") or part.get("content") or part.get("message") or ""
                    if text:
                        parts.append(str(text))
            return "\n".join(parts)
        elif isinstance(content, dict):
            # Try to extract text from content object
            return content.get("text") or content.get("content") or str(content)

        return str(content) if content else ""

    def handle_error(self, message: str, error: Exception | None = None) -> ChatImportResult:
        """Handle errors during import.

        Args:
            message: Error message.
            error: Optional exception that caused the error.

        Returns:
            ChatImportResult with error information.
        """
        error_msg = f"{message}: {error}" if error else message
        logger.error(error_msg)
        return ChatImportResult(
            import_count={"conversations": 0, "messages": 0},
            success=False,
            error_message=error_msg,
            conversations=0,
            messages=0,
        )
