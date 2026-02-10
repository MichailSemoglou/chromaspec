"""
Security utilities for ChromaSpec.

This module provides security-focused validation and protection functions
to prevent common vulnerabilities like path traversal, XXE attacks, and
resource exhaustion.
"""

import hashlib
import logging
import signal
from contextlib import contextmanager
from pathlib import Path
from typing import Optional

from chromaspec.exceptions import ValidationError

logger = logging.getLogger(__name__)


def validate_safe_path(path: Path, base_dir: Optional[Path] = None) -> bool:
    """
    Validate that a path doesn't escape the base directory (path traversal protection).

    This prevents malicious paths like '../../../etc/passwd' from being processed.
    If no base_dir is provided, simply validates the path doesn't contain dangerous patterns.

    Args:
        path: Path to validate.
        base_dir: Base directory to restrict to. If None, allows any absolute path
                  but checks for dangerous traversal patterns.

    Returns:
        True if path is safe.

    Raises:
        ValidationError: If path attempts directory traversal.

    Example:
        >>> validate_safe_path(Path("output/report.pdf"))  # OK
        True
        >>> validate_safe_path(Path("../../../etc/passwd"))  # Raises ValidationError
        >>> validate_safe_path(Path("/tmp/test.svg"))  # OK when base_dir=None
        True
    """
    # Check for dangerous patterns in the original path string
    path_str = str(path)
    if ".." in path.parts:
        raise ValidationError(
            f"Path '{path}' contains directory traversal pattern '..' "
            f"which may indicate a path traversal attack."
        )

    # If base_dir is specified, ensure path is within it
    if base_dir is not None:
        try:
            # Resolve to absolute paths and check containment
            resolved_path = path.resolve()
            resolved_base = base_dir.resolve()

            # Check if resolved path is within base directory
            resolved_path.relative_to(resolved_base)
            return True

        except ValueError:
            raise ValidationError(
                f"Path '{path}' attempts to escape base directory '{base_dir}'. "
                f"This may be a path traversal attack."
            )

    # When no base_dir, path is considered safe if it doesn't have traversal patterns
    return True


def sanitize_filename(filename: str, max_length: int = 255) -> str:
    """
    Sanitize filename to prevent injection attacks and filesystem issues.

    Removes or replaces potentially dangerous characters while preserving
    readability. Prevents hidden files and limits length.

    Args:
        filename: Original filename.
        max_length: Maximum filename length. Defaults to 255 (common filesystem limit).

    Returns:
        Sanitized filename safe for filesystem operations.

    Example:
        >>> sanitize_filename("../../evil.pdf")
        'evil.pdf'
        >>> sanitize_filename(".hidden_file")
        'hidden_file'
        >>> sanitize_filename("file<>:name.pdf")
        'file___name.pdf'
    """
    import re

    # Remove path separators
    safe_name = filename.replace("/", "_").replace("\\", "_")

    # Remove any character that isn't alphanumeric, dash, underscore, or dot
    safe_name = re.sub(r"[^a-zA-Z0-9_.-]", "_", safe_name)

    # Prevent hidden files (files starting with '.')
    safe_name = safe_name.lstrip(".")

    # Ensure we have something left
    if not safe_name:
        safe_name = "unnamed_file"

    # Limit length (preserve extension if possible)
    if len(safe_name) > max_length:
        name_parts = safe_name.rsplit(".", 1)
        if len(name_parts) == 2:
            name, ext = name_parts
            max_name_length = max_length - len(ext) - 1
            safe_name = f"{name[:max_name_length]}.{ext}"
        else:
            safe_name = safe_name[:max_length]

    return safe_name


def sanitize_pdf_string(text: str) -> str:
    """
    Sanitize strings before including in PDF to prevent PDF injection attacks.

    PDF files use special characters like parentheses and backslashes in their
    syntax. Unsanitized user input could potentially break PDF structure or
    inject malicious content.

    Args:
        text: Input text to be included in PDF.

    Returns:
        Sanitized text safe for PDF inclusion.

    Example:
        >>> sanitize_pdf_string("Hello (World)")
        'Hello \\(World\\)'
    """
    import re

    # Remove control characters except newline and tab
    # These can break PDF structure or cause rendering issues
    sanitized = re.sub(r"[\x00-\x08\x0B-\x0C\x0E-\x1F\x7F]", "", text)

    # Escape special PDF characters
    sanitized = sanitized.replace("\\", "\\\\")  # Backslash must be first
    sanitized = sanitized.replace("(", "\\(")
    sanitized = sanitized.replace(")", "\\)")

    # Limit length to prevent resource exhaustion
    max_length = 10000
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length] + "..."

    return sanitized


def calculate_file_hash(file_path: Path, algorithm: str = "sha256") -> str:
    """
    Calculate cryptographic hash of a file for cache keys or integrity checks.

    Uses streaming to handle large files efficiently without loading entire
    file into memory.

    Args:
        file_path: Path to file to hash.
        algorithm: Hash algorithm to use ('md5', 'sha256', etc.).

    Returns:
        Hexadecimal hash digest.

    Example:
        >>> calculate_file_hash(Path("image.png"))
        'a3f5b1c2d4...'
    """
    hasher = hashlib.new(algorithm)

    with open(file_path, "rb") as f:
        # Read in chunks to handle large files
        for chunk in iter(lambda: f.read(8192), b""):
            hasher.update(chunk)

    return hasher.hexdigest()


@contextmanager
def timeout(seconds: int):
    """
    Context manager to enforce timeout on operations.

    Raises TimeoutError if operation takes longer than specified seconds.
    Useful for preventing resource exhaustion from malicious or malformed inputs.

    Args:
        seconds: Maximum seconds to allow operation.

    Yields:
        None

    Raises:
        TimeoutError: If operation exceeds timeout.

    Example:
        >>> with timeout(5):
        ...     slow_operation()  # Will be interrupted after 5 seconds

    Note:
        Unix/Linux only. On Windows, this is a no-op (doesn't enforce timeout).
    """

    def timeout_handler(signum, frame):
        raise TimeoutError(f"Operation exceeded {seconds} seconds")

    # Only works on Unix-like systems
    if hasattr(signal, "SIGALRM"):
        old_handler = signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(seconds)

        try:
            yield
        finally:
            signal.alarm(0)
            signal.signal(signal.SIGALRM, old_handler)
    else:
        # On Windows, just yield without timeout (could use threading alternative)
        logger.warning("Timeout not supported on this platform")
        yield


def validate_file_size(file_path: Path, max_size_mb: int) -> bool:
    """
    Validate file size to prevent resource exhaustion attacks.

    Args:
        file_path: Path to file to check.
        max_size_mb: Maximum allowed file size in megabytes.

    Returns:
        True if file size is acceptable.

    Raises:
        ValidationError: If file exceeds size limit.
    """
    file_size = file_path.stat().st_size
    max_size_bytes = max_size_mb * 1024 * 1024

    if file_size > max_size_bytes:
        raise ValidationError(
            f"File size {file_size / 1024 / 1024:.2f}MB exceeds "
            f"maximum allowed size of {max_size_mb}MB"
        )

    return True


def rate_limit_check(
    key: str, max_requests: int = 100, window_seconds: int = 60
) -> bool:
    """
    Simple in-memory rate limiting check.

    Note: This is a basic implementation. For production, use Redis or similar.

    Args:
        key: Identifier for rate limit (e.g., IP address, user ID).
        max_requests: Maximum requests allowed in window.
        window_seconds: Time window in seconds.

    Returns:
        True if request is allowed, False if rate limit exceeded.
    """
    from datetime import datetime, timedelta

    # In production, store this in Redis or similar
    # For now, using module-level dict (will reset on process restart)
    if not hasattr(rate_limit_check, "requests"):
        rate_limit_check.requests = {}

    now = datetime.now()
    window = timedelta(seconds=window_seconds)

    # Clean old entries
    if key not in rate_limit_check.requests:
        rate_limit_check.requests[key] = []

    rate_limit_check.requests[key] = [
        timestamp
        for timestamp in rate_limit_check.requests[key]
        if now - timestamp < window
    ]

    # Check limit
    if len(rate_limit_check.requests[key]) >= max_requests:
        logger.warning(f"Rate limit exceeded for key: {key}")
        return False

    # Record request
    rate_limit_check.requests[key].append(now)
    return True
