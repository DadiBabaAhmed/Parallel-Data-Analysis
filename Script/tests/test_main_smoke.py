import pytest
from unittest.mock import patch, MagicMock
from src.main import ParallelDataAnalysis


@patch('src.main.SparkSession')
@patch('src.main.ErrorHandler')
@patch('src.main.PerformanceMonitor')
@patch('src.main.GraphGenerator')
def test_main_initialization(mock_graph, mock_perf, mock_error, mock_spark):
    """Test ParallelDataAnalysis initialization"""
    mock_spark.builder.appName.return_value.master.return_value.config.return_value.config.return_value.config.return_value.config.return_value.config.return_value.getOrCreate.return_value = MagicMock()

    analyzer = ParallelDataAnalysis("TestApp", master="local[*]")

    assert analyzer.app_name == "TestApp"
    assert analyzer.master == "local[*]"
    assert analyzer.timestamp is not None


@patch('src.main.SparkSession')
@patch('src.main.ErrorHandler')
@patch('src.main.PerformanceMonitor')
@patch('src.main.GraphGenerator')
@patch('src.main.DataLoader')
@patch('src.main.DataAnalyzer')
def test_main_run_analysis(mock_analyzer, mock_loader, mock_graph, mock_perf, mock_error, mock_spark):
    """Test run_analysis method"""
    # Setup mocks
    mock_spark_session = MagicMock()
    mock_spark.builder.appName.return_value.master.return_value.config.return_value.config.return_value.config.return_value.config.return_value.config.return_value.getOrCreate.return_value = mock_spark_session

    # Mock dataframe
    mock_df = MagicMock()
    mock_df.count.return_value = 100
    mock_df.limit.return_value.toPandas.return_value.to_csv = MagicMock()

    mock_loader_instance = MagicMock()
    mock_loader_instance.load_data.return_value = mock_df
    mock_loader.return_value = mock_loader_instance

    mock_analyzer_instance = MagicMock()
    mock_analyzer_instance.statistical_analysis.return_value = {'summary': {}}
    mock_analyzer_instance.aggregate_data.return_value = {'data': {}}
    mock_analyzer_instance.correlation_analysis.return_value = {'matrix': {}}
    mock_analyzer.return_value = mock_analyzer_instance

    mock_graph_instance = MagicMock()
    mock_graph.return_value = mock_graph_instance

    mock_perf_instance = MagicMock()
    mock_perf.return_value = mock_perf_instance

    mock_error_instance = MagicMock()
    mock_error.return_value = mock_error_instance

    analyzer = ParallelDataAnalysis("TestApp", master="local[*]")
    analyzer.run_analysis("dummy.csv", "statistical")

    # Verify that load_data was called
    mock_loader_instance.load_data.assert_called_once_with("dummy.csv")
    mock_analyzer_instance.statistical_analysis.assert_called_once()


@patch('src.main.SparkSession')
@patch('src.main.ErrorHandler')
@patch('src.main.PerformanceMonitor')
@patch('src.main.GraphGenerator')
def test_create_output_dirs(mock_graph, mock_perf, mock_error, mock_spark):
    """Test output directory creation"""
    mock_spark.builder.appName.return_value.master.return_value.config.return_value.config.return_value.config.return_value.config.return_value.config.return_value.getOrCreate.return_value = MagicMock()

    analyzer = ParallelDataAnalysis("TestApp", master="local[*]")

    # Directories should be created during initialization
    import os
    assert os.path.exists("output/general")
    assert os.path.exists("output/general/graphs")
