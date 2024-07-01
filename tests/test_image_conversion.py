import pytest
import os
import numpy as np
from unittest.mock import patch, MagicMock
from .. import bossdb_to_tiff_converter

# Constants for testing
URL = "wildenberg2023/mouse_v1_l4_p105/em"
RESOLUTION = 0
X_DIMENSIONS = "0:100"
Y_DIMENSIONS = "0:100"
Z_DIMENSIONS = "0:100"
FILE_PATH = "./test_output"

# Fixtures
@pytest.fixture
def intern_dataset_mock():
    data = np.random.randint(0, 255, (100, 100, 100), dtype=np.uint8)
    mock_dataset = MagicMock()
    mock_dataset.shape = data.shape
    mock_dataset.__getitem__.side_effect = lambda key: data[key]
    return mock_dataset

@pytest.fixture
def cloud_dataset_mock():
    data = np.random.randint(0, 255, (100, 100, 100, 1), dtype=np.uint8)
    mock_dataset = MagicMock()
    mock_dataset.shape = data.shape
    mock_dataset.__getitem__.side_effect = lambda key: data[key]
    mock_dataset.bounds.minpt = [0, 0, 0]
    mock_dataset.bounds.maxpt = [100, 100, 100]
    mock_dataset.available_mips = [RESOLUTION]
    return mock_dataset

# Test exception handling
def test_get_indices_invalid_range():
    coord_dims = {'X': 10, 'Y': 10, 'Z': 10}
    with pytest.raises(ValueError):
        bossdb_to_tiff_converter.get_indices('X', coord_dims, '5:15')
    with pytest.raises(ValueError):
        bossdb_to_tiff_converter.get_indices('Y', coord_dims, '10:5')

# Test intern_convert
@patch('bossdb_image_conversion.bossdb_to_tiff_converter.array')
def test_intern_convert(mock_array, intern_dataset_mock, tmpdir):
    mock_array.return_value = intern_dataset_mock
    file_path = str(tmpdir.mkdir("test_output"))
    bossdb_to_tiff_converter.intern_convert(f"bossdb://{URL}", URL.replace("/", "_"), RESOLUTION, X_DIMENSIONS, Y_DIMENSIONS, Z_DIMENSIONS, file_path)
    assert len(os.listdir(file_path)) == 100

# Test cloud_convert
@patch('bossdb_image_conversion.bossdb_to_tiff_converter.CloudVolume')
def test_cloud_convert(mock_cloudvolume, cloud_dataset_mock, tmpdir):
    mock_cloudvolume.return_value = cloud_dataset_mock
    file_path = str(tmpdir.mkdir("test_output"))
    bossdb_to_tiff_converter.cloud_convert(f"s3://bossdb-open-data/{URL}", URL.replace("/", "_"), RESOLUTION, X_DIMENSIONS, Y_DIMENSIONS, Z_DIMENSIONS, file_path)
    assert len(os.listdir(file_path)) == 100
