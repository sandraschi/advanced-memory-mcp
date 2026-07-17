"""Utility functions for making HTTP requests in Advanced Memory MCP tools.

These functions provide a consistent interface for making HTTP requests
to the Advanced Memory API, with improved error handling and logging.
"""

import typing

from httpx import URL, AsyncClient, HTTPStatusError, Response
from httpx._client import USE_CLIENT_DEFAULT, UseClientDefault
from httpx._types import (
    AuthTypes,
    CookieTypes,
    HeaderTypes,
    QueryParamTypes,
    RequestContent,
    RequestData,
    RequestExtensions,
    RequestFiles,
    TimeoutTypes,
)
from loguru import logger
from mcp.server.fastmcp.exceptions import ToolError


def get_error_message(status_code: int, url: URL | str, method: str, msg: str | None = None) -> str:
    """Get a friendly error message based on the HTTP status code.

    Args:
        status_code: The HTTP status code
        url: The URL that was requested
        method: The HTTP method used

    Returns:
        A user-friendly error message
    """
    # Extract path from URL for cleaner error messages
    if isinstance(url, str):
        path = url.split("/")[-1]
    else:
        path = str(url).split("/")[-1] if url else "resource"

    # Client errors (400-499)
    if status_code == 400:
        return f"Invalid request: The request to '{path}' was malformed or invalid"
    elif status_code == 401:  # pragma: no cover
        return f"Authentication required: You need to authenticate to access '{path}'"
    elif status_code == 403:  # pragma: no cover
        return f"Access denied: You don't have permission to access '{path}'"
    elif status_code == 404:
        return f"Resource not found: '{path}' doesn't exist or has been moved"
    elif status_code == 409:  # pragma: no cover
        return f"Conflict: The request for '{path}' conflicts with the current state"
    elif status_code == 429:  # pragma: no cover
        return "Too many requests: Please slow down and try again later"
    elif 400 <= status_code < 500:  # pragma: no cover
        return f"Client error ({status_code}): The request for '{path}' could not be completed"

    # Server errors (500-599)
    elif status_code == 500:
        return f"Internal server error: Something went wrong processing '{path}'"
    elif status_code == 503:  # pragma: no cover
        return f"Service unavailable: The server is currently unable to handle requests for '{path}'"
    elif 500 <= status_code < 600:  # pragma: no cover
        return f"Server error ({status_code}): The server encountered an error handling '{path}'"

    # Fallback for any other status code
    else:  # pragma: no cover
        return f"HTTP error {status_code}: {method} request to '{path}' failed"


async def call_get(
    client: AsyncClient,
    url: URL | str,
    *,
    params: QueryParamTypes | None = None,
    headers: HeaderTypes | None = None,
    cookies: CookieTypes | None = None,
    auth: AuthTypes | UseClientDefault | None = USE_CLIENT_DEFAULT,
    follow_redirects: bool | UseClientDefault = USE_CLIENT_DEFAULT,
    timeout: TimeoutTypes | UseClientDefault = USE_CLIENT_DEFAULT,
    extensions: RequestExtensions | None = None,
) -> Response:
    """Make a GET request and handle errors appropriately.

    Args:
        client: The HTTPX AsyncClient to use
        url: The URL to request
        params: Query parameters
        headers: HTTP headers
        cookies: HTTP cookies
        auth: Authentication
        follow_redirects: Whether to follow redirects
        timeout: Request timeout
        extensions: HTTPX extensions

    Returns:
        The HTTP response

    Raises:
        ToolError: If the request fails with an appropriate error message
    """
    logger.debug(f"Calling GET '{url}' params: '{params}'")
    error_message = None
    try:
        response = await client.get(
            url,
            params=params,
            headers=headers,
            cookies=cookies,
            auth=auth,
            follow_redirects=follow_redirects,
            timeout=timeout,
            extensions=extensions,
        )

        if response.is_success:
            return response

        # Handle different status codes differently
        status_code = response.status_code
        # get the message if available
        response_data = response.json()
        if isinstance(response_data, dict) and "detail" in response_data:
            error_message = response_data["detail"]
        else:
            error_message = get_error_message(status_code, url, "GET")

        # Log at appropriate level based on status code
        if 400 <= status_code < 500:
            # Client errors: log as info except for 429 (Too Many Requests)
            if status_code == 429:  # pragma: no cover
                logger.warning(f"Rate limit exceeded: GET {url}: {error_message}")
            else:
                logger.info(f"Client error: GET {url}: {error_message}")
        else:  # pragma: no cover
            # Server errors: log as error
            logger.error(f"Server error: GET {url}: {error_message}")

        # Raise a tool error with the friendly message
        response.raise_for_status()  # Will always raise since we're in the error case
        return response  # This line will never execute, but it satisfies the type checker  # pragma: no cover

    except HTTPStatusError as e:
        raise ToolError(error_message) from e


async def call_put(
    client: AsyncClient,
    url: URL | str,
    *,
    content: RequestContent | None = None,
    data: RequestData | None = None,
    files: RequestFiles | None = None,
    json: typing.Any | None = None,
    params: QueryParamTypes | None = None,
    headers: HeaderTypes | None = None,
    cookies: CookieTypes | None = None,
    auth: AuthTypes | UseClientDefault = USE_CLIENT_DEFAULT,
    follow_redirects: bool | UseClientDefault = True,
    timeout: TimeoutTypes | UseClientDefault = USE_CLIENT_DEFAULT,
    extensions: RequestExtensions | None = None,
) -> Response:
    """Make a PUT request and handle errors appropriately.

    Args:
        client: The HTTPX AsyncClient to use
        url: The URL to request
        content: Request content
        data: Form data
        files: Files to upload
        json: JSON data
        params: Query parameters
        headers: HTTP headers
        cookies: HTTP cookies
        auth: Authentication
        follow_redirects: Whether to follow redirects
        timeout: Request timeout
        extensions: HTTPX extensions

    Returns:
        The HTTP response

    Raises:
        ToolError: If the request fails with an appropriate error message
    """
    logger.debug(f"Calling PUT '{url}'")
    error_message = None

    try:
        response = await client.put(
            url,
            content=content,
            data=data,
            files=files,
            json=json,
            params=params,
            headers=headers,
            cookies=cookies,
            auth=auth,
            follow_redirects=follow_redirects,
            timeout=timeout,
            extensions=extensions,
        )

        if response.is_success:
            return response

        # Handle different status codes differently
        status_code = response.status_code

        # get the message if available
        response_data = response.json()
        if isinstance(response_data, dict) and "detail" in response_data:
            error_message = response_data["detail"]  # pragma: no cover
        else:
            error_message = get_error_message(status_code, url, "PUT")

        # Log at appropriate level based on status code
        if 400 <= status_code < 500:
            # Client errors: log as info except for 429 (Too Many Requests)
            if status_code == 429:  # pragma: no cover
                logger.warning(f"Rate limit exceeded: PUT {url}: {error_message}")
            else:
                logger.info(f"Client error: PUT {url}: {error_message}")
        else:  # pragma: no cover
            # Server errors: log as error
            logger.error(f"Server error: PUT {url}: {error_message}")

        # Raise a tool error with the friendly message
        response.raise_for_status()  # Will always raise since we're in the error case
        return response  # This line will never execute, but it satisfies the type checker  # pragma: no cover

    except HTTPStatusError as e:
        raise ToolError(error_message) from e


async def call_patch(
    client: AsyncClient,
    url: URL | str,
    *,
    content: RequestContent | None = None,
    data: RequestData | None = None,
    files: RequestFiles | None = None,
    json: typing.Any | None = None,
    params: QueryParamTypes | None = None,
    headers: HeaderTypes | None = None,
    cookies: CookieTypes | None = None,
    auth: AuthTypes | UseClientDefault = USE_CLIENT_DEFAULT,
    follow_redirects: bool | UseClientDefault = USE_CLIENT_DEFAULT,
    timeout: TimeoutTypes | UseClientDefault = USE_CLIENT_DEFAULT,
    extensions: RequestExtensions | None = None,
) -> Response:
    """Make a PATCH request and handle errors appropriately.

    Args:
        client: The HTTPX AsyncClient to use
        url: The URL to request
        content: Request content
        data: Form data
        files: Files to upload
        json: JSON data
        params: Query parameters
        headers: HTTP headers
        cookies: HTTP cookies
        auth: Authentication
        follow_redirects: Whether to follow redirects
        timeout: Request timeout
        extensions: HTTPX extensions

    Returns:
        The HTTP response

    Raises:
        ToolError: If the request fails with an appropriate error message
    """
    logger.debug(f"Calling PATCH '{url}'")
    try:
        response = await client.patch(
            url,
            content=content,
            data=data,
            files=files,
            json=json,
            params=params,
            headers=headers,
            cookies=cookies,
            auth=auth,
            follow_redirects=follow_redirects,
            timeout=timeout,
            extensions=extensions,
        )

        if response.is_success:
            return response

        # Handle different status codes differently
        status_code = response.status_code

        # Try to extract specific error message from response body
        try:
            response_data = response.json()
            if isinstance(response_data, dict) and "detail" in response_data:
                error_message = response_data["detail"]
            else:
                error_message = get_error_message(status_code, url, "PATCH")  # pragma: no cover
        except Exception:  # pragma: no cover
            error_message = get_error_message(status_code, url, "PATCH")  # pragma: no cover

        # Log at appropriate level based on status code
        if 400 <= status_code < 500:
            # Client errors: log as info except for 429 (Too Many Requests)
            if status_code == 429:  # pragma: no cover
                logger.warning(f"Rate limit exceeded: PATCH {url}: {error_message}")
            else:
                logger.info(f"Client error: PATCH {url}: {error_message}")
        else:  # pragma: no cover
            # Server errors: log as error
            logger.error(f"Server error: PATCH {url}: {error_message}")  # pragma: no cover

        # Raise a tool error with the friendly message
        response.raise_for_status()  # Will always raise since we're in the error case
        return response  # This line will never execute, but it satisfies the type checker  # pragma: no cover

    except HTTPStatusError as e:
        status_code = e.response.status_code

        # Try to extract specific error message from response body
        try:
            response_data = e.response.json()
            if isinstance(response_data, dict) and "detail" in response_data:
                error_message = response_data["detail"]
            else:
                error_message = get_error_message(status_code, url, "PATCH")  # pragma: no cover
        except Exception:  # pragma: no cover
            error_message = get_error_message(status_code, url, "PATCH")  # pragma: no cover

        raise ToolError(error_message) from e


async def call_post(
    client: AsyncClient,
    url: URL | str,
    *,
    content: RequestContent | None = None,
    data: RequestData | None = None,
    files: RequestFiles | None = None,
    json: typing.Any | None = None,
    params: QueryParamTypes | None = None,
    headers: HeaderTypes | None = None,
    cookies: CookieTypes | None = None,
    auth: AuthTypes | UseClientDefault = USE_CLIENT_DEFAULT,
    follow_redirects: bool | UseClientDefault = USE_CLIENT_DEFAULT,
    timeout: TimeoutTypes | UseClientDefault = USE_CLIENT_DEFAULT,
    extensions: RequestExtensions | None = None,
) -> Response:
    """Make a POST request and handle errors appropriately.

    Args:
        client: The HTTPX AsyncClient to use
        url: The URL to request
        content: Request content
        data: Form data
        files: Files to upload
        json: JSON data
        params: Query parameters
        headers: HTTP headers
        cookies: HTTP cookies
        auth: Authentication
        follow_redirects: Whether to follow redirects
        timeout: Request timeout
        extensions: HTTPX extensions

    Returns:
        The HTTP response

    Raises:
        ToolError: If the request fails with an appropriate error message
    """
    logger.debug(f"Calling POST '{url}'")
    error_message = None
    try:
        follow_redirects_value = True if isinstance(follow_redirects, UseClientDefault) else follow_redirects
        response = await client.post(
            url=url,
            content=content,
            data=data,
            files=files,
            json=json,
            params=params,
            headers=headers,
            cookies=cookies,
            auth=auth,
            follow_redirects=follow_redirects_value,
            timeout=timeout,
            extensions=extensions,
        )
        content_type = response.headers.get("content-type", "")
        response_payload: typing.Any
        if content_type and "application/json" in content_type.lower():
            try:
                response_payload = response.json()
            except ValueError:
                response_payload = None
        else:
            response_payload = response.text or None

        if response_payload is not None:
            logger.debug(f"POST {url} response body: {response_payload}")

        if response.is_success:
            return response

        # Handle different status codes differently
        status_code = response.status_code
        # get the message if available
        response_data = response_payload if isinstance(response_payload, dict) else None
        if response_data and "detail" in response_data:
            error_message = response_data["detail"]
        else:
            error_message = get_error_message(status_code, url, "POST")
            if isinstance(response_payload, str) and response_payload.strip():
                error_message = f"{error_message}. Response: {response_payload.strip()}"

        # Log at appropriate level based on status code
        if 400 <= status_code < 500:
            # Client errors: log as info except for 429 (Too Many Requests)
            if status_code == 429:  # pragma: no cover
                logger.warning(f"Rate limit exceeded: POST {url}: {error_message}")
            else:  # pragma: no cover
                logger.info(f"Client error: POST {url}: {error_message}")
        else:
            # Server errors: log as error
            logger.error(f"Server error: POST {url}: {error_message}")

        # Raise a tool error with the friendly message
        response.raise_for_status()  # Will always raise since we're in the error case
        return response  # This line will never execute, but it satisfies the type checker  # pragma: no cover

    except HTTPStatusError as e:
        status_code = e.response.status_code
        if not error_message:
            try:
                response_data = e.response.json()
                if isinstance(response_data, dict) and "detail" in response_data:
                    error_message = response_data["detail"]
                else:
                    error_message = get_error_message(status_code, url, "POST")
            except Exception:
                error_message = get_error_message(status_code, url, "POST")
        raise ToolError(error_message) from e


async def call_delete(
    client: AsyncClient,
    url: URL | str,
    *,
    params: QueryParamTypes | None = None,
    headers: HeaderTypes | None = None,
    cookies: CookieTypes | None = None,
    auth: AuthTypes | UseClientDefault = USE_CLIENT_DEFAULT,
    follow_redirects: bool | UseClientDefault = USE_CLIENT_DEFAULT,
    timeout: TimeoutTypes | UseClientDefault = USE_CLIENT_DEFAULT,
    extensions: RequestExtensions | None = None,
) -> Response:
    """Make a DELETE request and handle errors appropriately.

    Args:
        client: The HTTPX AsyncClient to use
        url: The URL to request
        params: Query parameters
        headers: HTTP headers
        cookies: HTTP cookies
        auth: Authentication
        follow_redirects: Whether to follow redirects
        timeout: Request timeout
        extensions: HTTPX extensions

    Returns:
        The HTTP response

    Raises:
        ToolError: If the request fails with an appropriate error message
    """
    logger.debug(f"Calling DELETE '{url}'")
    error_message = None
    try:
        response = await client.delete(
            url=url,
            params=params,
            headers=headers,
            cookies=cookies,
            auth=auth,
            follow_redirects=follow_redirects,
            timeout=timeout,
            extensions=extensions,
        )

        if response.is_success:
            return response

        # Handle different status codes differently
        status_code = response.status_code
        # get the message if available
        response_data = response.json()
        if isinstance(response_data, dict) and "detail" in response_data:
            error_message = response_data["detail"]  # pragma: no cover
        else:
            error_message = get_error_message(status_code, url, "DELETE")

        # Log at appropriate level based on status code
        if 400 <= status_code < 500:
            # Client errors: log as info except for 429 (Too Many Requests)
            if status_code == 429:  # pragma: no cover
                logger.warning(f"Rate limit exceeded: DELETE {url}: {error_message}")
            else:
                logger.info(f"Client error: DELETE {url}: {error_message}")
        else:  # pragma: no cover
            # Server errors: log as error
            logger.error(f"Server error: DELETE {url}: {error_message}")

        # Raise a tool error with the friendly message
        response.raise_for_status()  # Will always raise since we're in the error case
        return response  # This line will never execute, but it satisfies the type checker  # pragma: no cover

    except HTTPStatusError as e:
        raise ToolError(error_message) from e


def check_migration_status() -> str | None:
    """Check if sync/migration is in progress and return status message if so.

    Returns:
        Status message if sync is in progress, None if system is ready
    """
    try:
        from advanced_memory.services.sync_status_service import sync_status_tracker

        if not sync_status_tracker.is_ready:
            return sync_status_tracker.get_summary()
        return None
    except Exception:
        # If there's any error checking sync status, assume ready
        return None


async def wait_for_migration_or_return_status(timeout: float = 5.0, project_name: str | None = None) -> str | None:
    """Wait briefly for sync/migration to complete, or return status message.

    Args:
        timeout: Maximum time to wait for sync completion
        project_name: Optional project name to check specific project status.
                     If provided, only checks that project's readiness.
                     If None, uses global status check (legacy behavior).

    Returns:
        Status message if sync is still in progress, None if ready
    """
    try:
        import asyncio

        from advanced_memory.services.sync_status_service import sync_status_tracker

        # Check if we should use project-specific or global status
        def is_ready() -> bool:
            if project_name:
                return sync_status_tracker.is_project_ready(project_name)
            return sync_status_tracker.is_ready

        if is_ready():
            return None

        # Wait briefly for sync to complete
        loop = asyncio.get_running_loop()
        start_time = loop.time()
        while (loop.time() - start_time) < timeout:
            if is_ready():
                return None
            # Configurable polling interval
            import os

            poll_interval = float(os.getenv("SYNC_POLL_INTERVAL", "0.1"))
            await asyncio.sleep(poll_interval)

        # Still not ready after timeout
        if project_name:
            # For project-specific checks, get project status details
            project_status = sync_status_tracker.get_project_status(project_name)
            if project_status and project_status.status.value == "failed":
                error_msg = project_status.error or "Unknown sync error"
                return f"[ERROR] Sync failed for project '{project_name}': {error_msg}"
            elif project_status:
                return f"[STATUS] Project '{project_name}' is still syncing: {project_status.message}"
            else:
                return f"[WARNING] Project '{project_name}' status unknown"
        else:
            # Fall back to global summary for legacy calls
            return sync_status_tracker.get_summary()
    except Exception:  # pragma: no cover
        # If there's any error, assume ready
        return None


def sanitize_unicode_content(content: str) -> str:
    """
    Sanitize Unicode characters that cause JSON parsing issues in Claude Desktop.
    """
    replacements = {
        "[UNICODE]": "[OK]",
        "[UNICODE][UNICODE]": "[WARNING]",
        "[TARGET]": "[TARGET]",
        "[FIX]": "[FIX]",
        "[FAST]": "[FAST]",
        "[LAUNCH]": "[LAUNCH]",
        "[SUCCESS]": "[SUCCESS]",
        "[FOLDER]": "[FOLDER]",
        "[NOTE]": "[NOTE]",
        "[LIST]": "[LIST]",
        "[UNICODE]YZ[UNICODE]": "[TARGET]",
        '[UNICODE]Y"[UNICODE]': "[FIX]",
        '[UNICODE]Y"<': "[INFO]",
        "[UNICODE]Ys?": "[STATUS]",
        '[UNICODE]Y"^': "[METRIC]",
        "s[UNICODE]": "[NEXT]",
        "o.": "[OK]",
        "?": "[CHECK]",
    }
    sanitized = content
    for unicode_char, ascii_replacement in replacements.items():
        sanitized = sanitized.replace(unicode_char, ascii_replacement)
    try:
        sanitized.encode("utf-8").decode("utf-8")
    except UnicodeError:
        sanitized = "".join(char if ord(char) < 128 or char.isspace() else "?" for char in sanitized)
    return sanitized


# FastMCP 2.14.3 Conversational Response Builders
def build_success_response(operation: str, summary: str, **kwargs) -> dict:
    """Build conversational success response for MCP clients."""
    return {
        "success": True,
        "message": f"Perfect! {summary}",
        "operation": operation,
        "technical_summary": summary,  # Keep technical details for programmatic use
        **kwargs,
    }


def build_error_response(error: str, error_code: str | None = None, message: str | None = None, **kwargs) -> dict:
    """Build conversational error response with friendly guidance for MCP clients.

    Tolerant signature (2026-07-17): many call sites pass only (code, detail).
    In that case detail lands in error_code and is promoted to message, so a
    failing error path never raises TypeError and masks the real exception
    (which is exactly what happened in make_skill_advanced pre-fix).
    """
    if message is None:
        message = error_code or error
    if error_code is None:
        error_code = "ERROR"
    # Add conversational prefix based on error type
    conversational_message = _make_conversational_error(error, message)

    response = {
        "success": False,
        "error": error,
        "message": message,
        "conversational_summary": conversational_message,
        "technical_details": error,  # Keep technical error for debugging
        "error_code": error_code,
        **kwargs,
    }
    if "recovery_options" not in response:
        response["recovery_options"] = ["Check the documentation for valid parameters", "Verify the input format"]
    return response


def _make_conversational_error(error: str, message: str) -> str:
    """Convert technical errors into friendly, conversational messages."""
    error_lower = error.lower()
    message_lower = message.lower()

    # Connection/authentication issues
    if any(word in error_lower for word in ["connection", "connect", "network", "timeout"]):
        return "Oops, I couldn't connect to the service right now. Please check your internet connection and try again. If the problem persists, the service might be temporarily unavailable."
    elif "unauthorized" in error_lower or "auth" in error_lower:
        return "Looks like we need to get you authenticated first. Please make sure you're logged in and have the right permissions."
    elif "permission" in error_lower or "access" in error_lower:
        return "Sorry, you don't have permission to do that right now. Please check with your administrator or try a different operation."

    # Data/project issues
    elif "project" in error_lower and "not found" in message_lower:
        return "I couldn't find that project. Make sure the project name is spelled correctly and exists. You can list available projects with the project management tools."
    elif "note" in error_lower and "not found" in message_lower:
        return "That note doesn't seem to exist. Try searching for it with different keywords, or check if you have the right project selected."

    # Input validation issues
    elif "required" in error_lower or "missing" in error_lower:
        return "I need a bit more information to help you. Could you please provide the missing details? I'll guide you through what I need."
    elif "invalid" in error_lower or "format" in error_lower:
        return "That format doesn't look quite right. Let me help you get it formatted correctly. Check the examples in my documentation."

    # Search/query issues
    elif "search" in error_lower or "query" in error_lower:
        return "I couldn't find anything matching that search. Try using different keywords or being more specific. I can help you refine your search terms."
    elif "empty" in error_lower or "no results" in message_lower:
        return "No results found for that query. Try broadening your search or using different keywords. I'm here to help you find what you need."

    # File/system issues
    elif "file" in error_lower or "path" in error_lower:
        return "There seems to be an issue with that file or path. Make sure the file exists and you have permission to access it."
    elif "write" in error_lower or "save" in error_lower:
        return "I couldn't save that right now. Please check your permissions and available disk space, then try again."

    # General fallback: surface the actual error, no vague wrapper
    else:
        return f"{message}. Check recovery_options for next steps."
