"""
AIEDL Python implementation.

This package provides tools for parsing, validating, and building AIEDL files.
"""

try:
    from .parser import parse_edl_with_ai
    from .builder import AIEDLBuilder
    from .validator import validate_file, AIEDLValidator, ValidationError
except ImportError:
    # Fallback for direct execution
    from parser import parse_edl_with_ai
    from builder import AIEDLBuilder
    from validator import validate_file, AIEDLValidator, ValidationError

__all__ = [
    'parse_edl_with_ai',
    'AIEDLBuilder',
    'validate_file',
    'AIEDLValidator',
    'ValidationError',
]

__version__ = '1.0.0'

