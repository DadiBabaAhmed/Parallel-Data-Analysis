import pytest
from unittest.mock import MagicMock
from src.data_loader import DataLoader


def test_loader_initialization():
    spark = MagicMock()
    loader = DataLoader(spark, error_handler=None)
    assert loader.spark == spark


def test_load_csv_file(monkeypatch):
    spark = MagicMock()
    loader = DataLoader(spark, error_handler=None)

    fake_df = MagicMock()
    spark.read.csv.return_value = fake_df

    df = loader.load_data("test.csv")
    spark.read.csv.assert_called_once()
    assert df == fake_df
