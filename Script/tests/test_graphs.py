"""
Comprehensive tests for GraphGenerator module
Tests visualization generation and file output
"""
import pytest
import os
import matplotlib.pyplot as plt
from pathlib import Path

from src.graph_generator import GraphGenerator
from src.error_handler import ErrorHandler


class TestGraphGeneratorInitialization:
    """Test GraphGenerator initialization"""
    
    def test_graph_generator_init(self, timestamp):
        """Test GraphGenerator initialization"""
        graph_gen = GraphGenerator(timestamp)
        
        assert graph_gen.timestamp is not None
        assert graph_gen.output_dir is not None
        assert "graphs" in graph_gen.output_dir
    
    def test_graph_generator_output_dir_creation(self, timestamp, temp_test_dir):
        """Test that output directory is created correctly"""
        # Temporarily change working directory for test
        original_cwd = os.getcwd()
        os.chdir(temp_test_dir)
        
        try:
            graph_gen = GraphGenerator(timestamp)
            # Output directory should be relative to current working directory
            assert graph_gen.output_dir is not None
        finally:
            os.chdir(original_cwd)


class TestGraphGenerationBasics:
    """Test basic graph generation functionality"""
    
    def test_plot_distributions_with_valid_data(self, spark_session, spark_df, timestamp, temp_test_dir):
        """Test distribution plot generation"""
        original_cwd = os.getcwd()
        os.chdir(temp_test_dir)
        
        try:
            os.makedirs(f"output/general/graphs", exist_ok=True)
            
            graph_gen = GraphGenerator(timestamp)
            pandas_df = spark_df.toPandas()
            
            # Generate distribution plots
            graph_gen.plot_distributions(pandas_df)
            
            # Check that file was created
            expected_file = f"output/general/graphs/distributions_{timestamp}.png"
            assert os.path.exists(expected_file), f"Distribution plot not created at {expected_file}"
            
            # Check file size is reasonable
            file_size = os.path.getsize(expected_file)
            assert file_size > 0, "Distribution plot file is empty"
            
        finally:
            plt.close('all')
            os.chdir(original_cwd)
    
    def test_plot_distributions_handles_no_numeric_columns(self, spark_session, string_only_df, timestamp, temp_test_dir):
        """Test distribution plot with no numeric columns"""
        original_cwd = os.getcwd()
        os.chdir(temp_test_dir)
        
        try:
            os.makedirs(f"output/general/graphs", exist_ok=True)
            
            graph_gen = GraphGenerator(timestamp)
            pandas_df = string_only_df.toPandas()
            
            # Should handle gracefully with no numeric columns
            graph_gen.plot_distributions(pandas_df)
            # Should not raise exception
            
        finally:
            plt.close('all')
            os.chdir(original_cwd)
    
    def test_plot_correlations_with_matrix(self, spark_session, numeric_only_df, timestamp, temp_test_dir):
        """Test correlation plot generation"""
        original_cwd = os.getcwd()
        os.chdir(temp_test_dir)
        
        try:
            os.makedirs(f"output/general/graphs", exist_ok=True)
            
            graph_gen = GraphGenerator(timestamp)
            
            # Create correlation data
            correlation_data = {
                'matrix': [[1.0, 0.8], [0.8, 1.0]]
            }
            
            graph_gen.plot_correlations(correlation_data)
            
            # Check that file was created
            expected_file = f"output/general/graphs/correlation_{timestamp}.png"
            assert os.path.exists(expected_file), "Correlation plot not created"
            
            file_size = os.path.getsize(expected_file)
            assert file_size > 0, "Correlation plot file is empty"
            
        finally:
            plt.close('all')
            os.chdir(original_cwd)
    
    def test_plot_correlations_handles_none_input(self, timestamp, temp_test_dir):
        """Test correlation plot with None input"""
        original_cwd = os.getcwd()
        os.chdir(temp_test_dir)
        
        try:
            os.makedirs(f"output/general/graphs", exist_ok=True)
            
            graph_gen = GraphGenerator(timestamp)
            
            # Should handle None gracefully
            graph_gen.plot_correlations(None)
            graph_gen.plot_correlations({})
            # Should not raise exceptions
            
        finally:
            plt.close('all')
            os.chdir(original_cwd)


class TestGraphGenerationIntegration:
    """Integration tests for graph generation"""
    
    def test_generate_all_graphs(self, spark_session, spark_df, timestamp, temp_test_dir):
        """Test generating all graph types at once"""
        original_cwd = os.getcwd()
        os.chdir(temp_test_dir)
        
        try:
            os.makedirs(f"output/general/graphs", exist_ok=True)
            
            graph_gen = GraphGenerator(timestamp)
            
            results = {
                'correlation': {'matrix': [[1.0, 0.5], [0.5, 1.0]]},
                'aggregation': {'data': {'A': 10, 'B': 20}},
                'statistics': {'mean': 15}
            }
            
            # Should generate all graphs without errors
            graph_gen.generate_all_graphs(spark_df, results)
            
        finally:
            plt.close('all')
            os.chdir(original_cwd)
    
    def test_graphs_created_with_correct_names(self, spark_session, numeric_only_df, timestamp, temp_test_dir):
        """Test that generated graphs have correct naming convention"""
        original_cwd = os.getcwd()
        os.chdir(temp_test_dir)
        
        try:
            os.makedirs(f"output/general/graphs", exist_ok=True)
            
            graph_gen = GraphGenerator(timestamp)
            pandas_df = numeric_only_df.toPandas()
            
            graph_gen.plot_distributions(pandas_df)
            
            # All files should contain the timestamp
            graph_files = Path(f"output/general/graphs").glob(f"*{timestamp}*.png")
            graph_files = list(graph_files)
            
            assert len(graph_files) > 0, "No graph files created with timestamp"
            
            for file in graph_files:
                assert timestamp in str(file), "Graph file doesn't contain timestamp"
            
        finally:
            plt.close('all')
            os.chdir(original_cwd)


class TestGraphGeneratorEdgeCases:
    """Test edge cases in graph generation"""
    
    def test_plot_with_single_value_dataframe(self, spark_session, timestamp, temp_test_dir):
        """Test plotting with DataFrame containing single value"""
        original_cwd = os.getcwd()
        os.chdir(temp_test_dir)
        
        try:
            os.makedirs(f"output/general/graphs", exist_ok=True)
            
            # Create DataFrame with single value
            data = [(1, 10.0)]
            df = spark_session.createDataFrame(data, ["id", "value"])
            pandas_df = df.toPandas()
            
            graph_gen = GraphGenerator(timestamp)
            graph_gen.plot_distributions(pandas_df)
            
            # Should handle single value without crashing
            
        finally:
            plt.close('all')
            os.chdir(original_cwd)
    
    def test_plot_with_large_dataframe(self, spark_session, large_spark_df, timestamp, temp_test_dir):
        """Test plotting with larger dataset"""
        original_cwd = os.getcwd()
        os.chdir(temp_test_dir)
        
        try:
            os.makedirs(f"output/general/graphs", exist_ok=True)
            
            graph_gen = GraphGenerator(timestamp)
            # Limit to avoid memory issues
            pandas_df = large_spark_df.limit(5000).toPandas()
            
            graph_gen.plot_distributions(pandas_df)
            
            # Should complete without memory errors
            
        finally:
            plt.close('all')
            os.chdir(original_cwd)


class TestGraphFileOutput:
    """Test graph file output and format"""
    
    def test_graph_files_are_valid_png(self, spark_session, numeric_only_df, timestamp, temp_test_dir):
        """Test that generated PNG files are valid"""
        original_cwd = os.getcwd()
        os.chdir(temp_test_dir)
        
        try:
            os.makedirs(f"output/general/graphs", exist_ok=True)
            
            graph_gen = GraphGenerator(timestamp)
            pandas_df = numeric_only_df.toPandas()
            
            graph_gen.plot_distributions(pandas_df)
            
            # Check PNG signature (PNG files start with specific bytes)
            expected_file = f"output/general/graphs/distributions_{timestamp}.png"
            if os.path.exists(expected_file):
                with open(expected_file, 'rb') as f:
                    header = f.read(8)
                    # PNG signature
                    assert header.startswith(b'\x89PNG'), "Invalid PNG file format"
            
        finally:
            plt.close('all')
            os.chdir(original_cwd)
    
    def test_multiple_graph_generations_dont_overwrite(self, spark_session, numeric_only_df, temp_test_dir):
        """Test that multiple runs don't overwrite each other"""
        original_cwd = os.getcwd()
        os.chdir(temp_test_dir)
        
        try:
            os.makedirs(f"output/general/graphs", exist_ok=True)
            
            timestamp1 = "20250101_120000"
            timestamp2 = "20250101_120001"
            
            graph_gen1 = GraphGenerator(timestamp1)
            graph_gen2 = GraphGenerator(timestamp2)
            
            pandas_df = numeric_only_df.toPandas()
            
            graph_gen1.plot_distributions(pandas_df)
            graph_gen2.plot_distributions(pandas_df)
            
            # Both files should exist
            file1 = f"output/general/graphs/distributions_{timestamp1}.png"
            file2 = f"output/general/graphs/distributions_{timestamp2}.png"
            
            assert os.path.exists(file1), "First graph file not created"
            assert os.path.exists(file2), "Second graph file not created"
            
        finally:
            plt.close('all')
            os.chdir(original_cwd)
from unittest.mock import MagicMock, patch, Mock
from src.graph_generator import GraphGenerator
import pandas as pd
import numpy as np
import os


def test_graph_generator_initialization():
    """Test GraphGenerator initialization"""
    timestamp = "20231201_120000"
    gen = GraphGenerator(timestamp)
    assert gen.timestamp == timestamp
    assert gen.output_dir == "output/general/graphs"


@patch('src.graph_generator.plt')
def test_plot_distributions(mock_plt, tmp_path):
    """Test distribution plot generation"""
    timestamp = "20231201_120000"
    gen = GraphGenerator(timestamp)

    # Create test pandas DataFrame
    test_data = pd.DataFrame({
        'value1': np.random.randn(100),
        'value2': np.random.randn(100),
        'text': ['a'] * 100
    })

    # Mock subplots to return figure and axes
    mock_fig = MagicMock()
    mock_axes = MagicMock()
    mock_plt.subplots.return_value = (mock_fig, mock_axes)

    # Create output directory
    os.makedirs(gen.output_dir, exist_ok=True)

    gen.plot_distributions(test_data)

    # Verify plt methods were called
    mock_plt.subplots.assert_called()
    mock_plt.tight_layout.assert_called()


@patch('src.graph_generator.plt')
@patch('src.graph_generator.sns')
def test_plot_correlations(mock_sns, mock_plt):
    """Test correlation heatmap generation"""
    timestamp = "20231201_120000"
    gen = GraphGenerator(timestamp)

    correlation_data = {
        'matrix': {
            'col1': {'col1': 1.0, 'col2': 0.5},
            'col2': {'col1': 0.5, 'col2': 1.0}
        }
    }

    os.makedirs(gen.output_dir, exist_ok=True)
    gen.plot_correlations(correlation_data)

    # Verify sns.heatmap was called
    mock_sns.heatmap.assert_called_once()
    mock_plt.tight_layout.assert_called()


@patch('src.graph_generator.plt')
def test_plot_correlations_no_data(mock_plt):
    """Test correlation plot with no data"""
    timestamp = "20231201_120000"
    gen = GraphGenerator(timestamp)

    # Should handle gracefully
    gen.plot_correlations(None)
    gen.plot_correlations({})

    # No plots should be generated
    mock_plt.figure.assert_not_called()


@patch('src.graph_generator.plt')
def test_plot_statistical_summary(mock_plt):
    """Test statistical summary plot generation"""
    timestamp = "20231201_120000"
    gen = GraphGenerator(timestamp)

    stats_data = {
        'summary': {
            'summary': ['count', 'mean', 'stddev'],
            'col1': [100, 50.5, 10.2],
            'col2': [100, 25.3, 5.1]
        }
    }

    # Mock subplots to return figure and axes
    mock_fig = MagicMock()
    mock_axes = [MagicMock(), MagicMock()]
    mock_plt.subplots.return_value = (mock_fig, mock_axes)

    os.makedirs(gen.output_dir, exist_ok=True)
    gen.plot_statistical_summary(stats_data)

    mock_plt.subplots.assert_called()
    mock_plt.tight_layout.assert_called()
