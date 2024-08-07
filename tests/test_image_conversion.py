import pytest
import os
from .. import bossdb_to_tiff_converter

# Constants for testing
URL = "wildenberg2023/mouse_v1_l4_p105/em"
RESOLUTION = 0
X_DIMENSIONS = "0:100"
Y_DIMENSIONS = "0:100"
Z_DIMENSIONS = "0:100"
FILE_PATH = "./test_output"

# Test index exception handling
def test_get_indices_invalid_range():
    coord_dims = {'X': 10, 'Y': 10, 'Z': 10}
    with pytest.raises(ValueError):
        bossdb_to_tiff_converter.get_indices('X', coord_dims, '5:15')
    with pytest.raises(ValueError):
        bossdb_to_tiff_converter.get_indices('Y', coord_dims, '10:5')

# Test intern_convert
def test_intern_convert(tmpdir):
    #mock_array.return_value = intern_dataset_mock
    file_path = str(tmpdir.mkdir("test_output"))
    bossdb_to_tiff_converter.intern_convert(f"bossdb://{URL}", URL.replace("/", "_"), RESOLUTION, X_DIMENSIONS, Y_DIMENSIONS, Z_DIMENSIONS, file_path)
    assert len(os.listdir(file_path)) == 100

# Test cloud_convert
def test_cloud_convert(tmpdir):
    file_path = str(tmpdir.mkdir("test_output"))
    bossdb_to_tiff_converter.cloud_convert(f"s3://bossdb-open-data/{URL}", URL.replace("/", "_"), RESOLUTION, X_DIMENSIONS, Y_DIMENSIONS, Z_DIMENSIONS, file_path)
    assert len(os.listdir(file_path)) == 100
