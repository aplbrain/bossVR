import os
import pytest
import numpy as np
from unittest import mock
from PIL import Image
from image_conversion_script import get_indices, get_file_location, save_slices_as_tiff

# Mock dataset for testing
@pytest.fixture
def mock_dataset():
    return np.random.randint(0, 255, (100, 1000, 1000), dtype=np.uint8)

def test_get_indices():
    coord_dims = {'X': 1000, 'Y': 1000, 'Z': 100}

    with mock.patch('builtins.input', side_effect=['10:20']):
        start, stop = get_indices("X", coord_dims)
        assert start == 10
        assert stop == 20

    with mock.patch('builtins.input', side_effect=['-1:10', '10:110', '20:10', '10:20']):
        start, stop = get_indices("X", coord_dims)
        assert start == 10
        assert stop == 20

def test_get_file_location(tmp_path):
    dir_path = str(tmp_path / "test_dir")

    with mock.patch('builtins.input', side_effect=[dir_path]):
        file_location = get_file_location()
        assert os.path.isdir(file_location)
        assert file_location == dir_path

def test_save_slices_as_tiff(mock_dataset, tmp_path):
    file_location = str(tmp_path)
    collection = "test_collection"
    experiment = "test_experiment"
    channel = "test_channel"
    z_start = 0

    save_slices_as_tiff(mock_dataset, file_location, z_start, collection, experiment, channel)

    saved_files = os.listdir(file_location)
    assert len(saved_files) == mock_dataset.shape[0]
    for i, file in enumerate(saved_files):
        assert file == f'{collection.lower()}_{experiment.lower()}_{channel.lower()}_{z_start + 1 + i:03d}.tiff'
        img = Image.open(os.path.join(file_location, file))
        assert np.array(img).shape == (1000, 1000)

@pytest.mark.parametrize("collection,experiment,channel", [
    ("kasthuri", "ac4", "em"),
    ("wildenberg2023", "mouse_v1_l23_p105", "em"),
    ("microns", "basil", "em")
])

def test_main_function(collection, experiment, channel):
    with mock.patch('builtins.input', side_effect=[
        collection, experiment, channel, '0', '10:20', '10:20', '0:10', './test_dir'
    ]), mock.patch('image_conversion_script.array', return_value=np.random.randint(0, 255, (100, 1000, 1000), dtype=np.uint8)), mock.patch('os.makedirs', return_value=None), mock.patch('image_conversion_script.save_slices_as_tiff', return_value=None):
        from image_conversion_script import main
        main()
