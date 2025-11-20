import pytest
from unittest.mock import MagicMock
from src.graph_generator import GraphGenerator


def test_generate_basic_plot(tmp_path):
    df = MagicMock()
    df.toPandas.return_value = MagicMock()

    gen = GraphGenerator()
    output_path = tmp_path / "plot.png"

    gen.generate_distribution_plot(df, str(output_path))
    assert output_path.exists()
