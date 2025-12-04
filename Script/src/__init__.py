"""
src package for Parallel-Data-Analysis.

Use relative imports so `python -m src.main` works when `src` is
imported as a package inside the container. Absolute imports (e.g.
`from data_loader import DataLoader`) failed because the package
parent directory may not be on sys.path in all execution contexts.
"""

from .data_loader import DataLoader
from .data_analyzer import DataAnalyzer
from .graph_generator import GraphGenerator
from .performance_monitor import PerformanceMonitor
from .error_handler import ErrorHandler

__all__ = [
    "DataLoader",
    "DataAnalyzer",
    "GraphGenerator",
    "PerformanceMonitor",
    "ErrorHandler",
]
