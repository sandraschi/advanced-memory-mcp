"""Import router for Advanced Memory API."""

import json
import logging
from pathlib import Path
from typing import Any, TypeVar

from fastapi import APIRouter, Form, HTTPException, UploadFile, status
from pydantic import BaseModel

from advanced_memory.deps import (
    ChatGPTImporterDep,
    ClaudeConversationsImporterDep,
    ClaudeProjectsImporterDep,
    InboxProcessorDep,
    MemoryJsonImporterDep,
)
from advanced_memory.importers import Importer
from advanced_memory.schemas.importer import (
    ChatImportResult,
    EntityImportResult,
    ImportResult,
    ProjectImportResult,
)

logger = logging.getLogger(__name__)
T = TypeVar("T", bound=ImportResult)


class BatchImportRequest(BaseModel):
    files: list[str]
    destination_folder: str
    project: str | None = None


router = APIRouter(prefix="/import", tags=["import"])


@router.post("/batch")
async def import_batch(
    request: BatchImportRequest,
    inbox_processor: InboxProcessorDep,
) -> list[dict[str, Any]]:
    """
    Import multiple files in batch using InboxProcessor.
    """
    results = []
    for file_path_str in request.files:
        file_path = Path(file_path_str)
        try:
            result = await inbox_processor.process_file(file_path)
            results.append(
                {
                    "file": file_path_str,
                    "success": result.get("status") == "success",
                    "message": result.get("message", "Processed"),
                    "details": result,
                }
            )
        except Exception as e:
            logger.error(f"Failed to process {file_path_str}: {e}")
            results.append({"file": file_path_str, "success": False, "message": str(e)})
    return results


@router.post("/chatgpt", response_model=ChatImportResult)
async def import_chatgpt(
    importer: ChatGPTImporterDep,
    file: UploadFile,
    folder: str = Form("conversations"),
) -> ChatImportResult:
    """Import conversations from ChatGPT JSON export."""
    return await import_file(importer, file, folder)


@router.post("/claude/conversations", response_model=ChatImportResult)
async def import_claude_conversations(
    importer: ClaudeConversationsImporterDep,
    file: UploadFile,
    folder: str = Form("conversations"),
) -> ChatImportResult:
    """Import conversations from Claude conversations.json export."""
    return await import_file(importer, file, folder)


@router.post("/claude/projects", response_model=ProjectImportResult)
async def import_claude_projects(
    importer: ClaudeProjectsImporterDep,
    file: UploadFile,
    folder: str = Form("projects"),
) -> ProjectImportResult:
    """Import projects from Claude projects.json export."""
    return await import_file(importer, file, folder)


@router.post("/memory-json", response_model=EntityImportResult)
async def import_memory_json(
    importer: MemoryJsonImporterDep,
    file: UploadFile,
    folder: str = Form("conversations"),
) -> EntityImportResult:
    """Import entities and relations from a memory.json file."""
    try:
        file_data = []
        file_bytes = await file.read()
        file_str = file_bytes.decode("utf-8")
        for line in file_str.splitlines():
            json_data = json.loads(line)
            file_data.append(json_data)

        result = await importer.import_data(file_data, folder)
        if not result.success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result.error_message or "Import failed",
            )
    except Exception as e:
        logger.exception("Import failed")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Import failed: {e!s}",
        ) from e
    return result


async def import_file(importer: Importer, file: UploadFile, destination_folder: str) -> T:
    try:
        json_data = json.load(file.file)
        result = await importer.import_data(json_data, destination_folder)
        if not result.success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result.error_message or "Import failed",
            )

        return result

    except Exception as e:
        logger.exception("Import failed")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Import failed: {e!s}",
        ) from e
