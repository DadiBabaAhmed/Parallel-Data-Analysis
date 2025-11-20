import pytest
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

    os.makedirs(gen.output_dir, exist_ok=True)
    gen.plot_statistical_summary(stats_data)

    mock_plt.subplots.assert_called()
    mock_plt.tight_layout.assert_called()
