"""
src package for Parallel-Data-Analysis.

This file makes the src directory a proper Python package so that
relative imports (e.g., from .data_loader import DataLoader) work and
modules can be imported as `src.<module>` from tests and other code.
"""
from data_loader import DataLoader
from data_analyzer import DataAnalyzer
from graph_generator import GraphGenerator
from performance_monitor import PerformanceMonitor
from error_handler import ErrorHandler

__all__ = [
    "DataLoader",
    "DataAnalyzer",
    "GraphGenerator",
    "PerformanceMonitor",
    "ErrorHandler",
]
