import pytest
from unittest.mock import patch
from src.main import ParallelDataAnalysis


def test_main_smoke_run():
    with patch.object(ParallelDataAnalysis, "run_analysis", return_value=True):
        analyzer = ParallelDataAnalysis("TestApp", master="local[*]")
        result = analyzer.run_analysis("dummy.csv", "full")
        assert result is True
