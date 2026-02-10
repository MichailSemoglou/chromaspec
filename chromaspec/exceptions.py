"""
Custom exception classes for ChromaSpec.

This module defines a hierarchy of exceptions for better error handling
and user-friendly error messages.
"""


class ChromaSpecError(Exception):
    """Base exception for all ChromaSpec errors."""

    pass


class FileProcessingError(ChromaSpecError):
    """Raised when file processing fails."""

    pass


class FileNotFoundError(ChromaSpecError):
    """Raised when an input file is not found."""

    pass


class UnsupportedFormatError(ChromaSpecError):
    """Raised when an unsupported file format is encountered."""

    pass


class ValidationError(ChromaSpecError):
    """Raised when input validation fails."""

    pass


class ImageProcessingError(ChromaSpecError):
    """Raised when image processing fails."""

    pass


class PDFGenerationError(ChromaSpecError):
    """Raised when PDF generation fails."""

    pass


class ConfigurationError(ChromaSpecError):
    """Raised when configuration is invalid."""

    pass
