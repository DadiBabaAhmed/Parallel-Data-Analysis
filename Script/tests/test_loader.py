import pytest
from unittest.mock import MagicMock, patch
from src.data_loader import DataLoader


def test_loader_initialization():
    """Test DataLoader initialization"""
    spark = MagicMock()
    error_handler = MagicMock()
    loader = DataLoader(spark, error_handler)
    assert loader.spark == spark
    assert loader.error_handler == error_handler
    assert loader.supported_formats == ['csv', 'json', 'parquet', 'avro']


def test_load_csv_file():
    """Test loading CSV file"""
    spark = MagicMock()
    error_handler = MagicMock()
    loader = DataLoader(spark, error_handler)

    # Mock the DataFrame
    fake_df = MagicMock()
    fake_df.count.return_value = 100
    fake_df.cache.return_value = fake_df

    # Mock the read chain
    spark.read.option.return_value.option.return_value.option.return_value.csv.return_value = fake_df

    df = loader.load_data("test.csv")
    assert df == fake_df
    fake_df.cache.assert_called_once()


def test_load_json_file():
    """Test loading JSON file"""
    spark = MagicMock()
    error_handler = MagicMock()
    loader = DataLoader(spark, error_handler)

    fake_df = MagicMock()
    fake_df.count.return_value = 50
    fake_df.cache.return_value = fake_df

    spark.read.option.return_value.json.return_value = fake_df

    df = loader.load_data("test.json")
    assert df == fake_df


def test_load_unsupported_format():
    """Test loading unsupported file format"""
    spark = MagicMock()
    error_handler = MagicMock()
    loader = DataLoader(spark, error_handler)

    with pytest.raises(ValueError, match="Unsupported format"):
        loader.load_data("test.xyz")


def test_validate_dataframe_empty():
    """Test validation of empty DataFrame"""
    spark = MagicMock()
    error_handler = MagicMock()
    loader = DataLoader(spark, error_handler)

    fake_df = MagicMock()
    fake_df.count.return_value = 0

    with pytest.raises(ValueError, match="DataFrame is empty"):
        loader._validate_dataframe(fake_df)
