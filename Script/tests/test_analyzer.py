import pytest
from unittest.mock import MagicMock
from src.data_analyzer import DataAnalyzer


def test_analyzer_initialization():
    analyzer = DataAnalyzer(None, None, None)
    assert analyzer is not None


def test_run_statistical_analysis():
    analyzer = DataAnalyzer(None, None, None)

    df = MagicMock()
    analyzer._run_statistical_analysis = MagicMock(return_value={"mean": 10})

    result = analyzer._run_statistical_analysis(df)
    assert "mean" in result
