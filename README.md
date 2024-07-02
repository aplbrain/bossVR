# BossDB Image Conversion Script

This script allows you to interact with datasets from BossDB and CloudVolume. You can retrieve information about the dataset or download images in TIFF format. The script supports two modes: `intern` and `cloud`, and provides a command-line interface using `argparse`.

## Requirements

All the required packages can be installed using the `requirements.txt` file:

```sh
pip install -r requirements.txt
```

This code supports usage of both `intern` and  `CloudVolume` for reading of BossDB data and access to more detailed dataset info. Follow [intern installation instructions](https://github.com/jhuapl-boss/intern)) and [CloudVolume installation instructions](https://github.com/seung-lab/cloud-volume?tab=readme-ov-file)) for more information.

## Usage

The script can operate in two modes: `intern` for BossDB and `cloud` for CloudVolume. Additionally, it can either provide information about the dataset or also download the images based on the provided parameters.

### Command-Line Arguments

- `-m`, `--mode`: Mode of implementation (`intern` or `cloud`). Required.
- `-u`, `--url`: BossDB or CloudVolume path. Required.
- `-r`, `--resolution`: Desired resolution level. Default is 0.
- `-x`, `--x_dimensions`: Range for X dimension in the format `x_start:x_stop`. Optional. By default, the entire range is extracted.
- `-y`, `--y_dimensions`: Range for Y dimension in the format `y_start:y_stop`. Optional. By default, the entire range is extracted.
- `-z`, `--z_dimensions`: Range for Z dimension in the format `z_start:z_stop`. Optional. By default, the entire range is extracted.
- `-f`, `--file_path`: Directory where the TIFF files should be saved. If not provided, the script will only output information about the dataset.

### Examples

#### 1. Retrieve Information About the Dataset

To get information about the dataset without downloading images:

With Intern:

```sh
python bossdb_to_tiff_converter.py -m intern -u myCollection/myExperiment/myChannel
```

With CloudVolume:

```sh
python bossdb_to_tiff_converter.py -m cloud -u myBossDB/url
```

#### 2. Download Images from BossDB

To download images using `intern`, default mode:

```sh
python bossdb_to_tiff_converter.py -m intern -u myCollection/myExperiment/myChannel -f /path/to/save/images
```

#### 3. Download Images from CloudVolume

To download images using `CloudVolume`, default mode:

```sh
python bossdb_to_tiff_converter.py -m cloud -u myBossDB/url -f /path/to/save/images
```

### Detailed Examples with Dimension and Resolution Specifications

#### Intern Example

```sh
python bossdb_to_tiff_converter.py -m intern -u myCollection/myExperiment/myChannel -r 2 -x 0:1000 -y 0:1000 -z 0:100 -f /path/to/save/images
```

#### CloudVolume Example

```sh
python bossdb_to_tiff_converter.py -m cloud -u myBossDB/url -r 2 -x 0:1000 -y 0:1000 -z 0:1000 -f /path/to/save/images
```

## Script Details

### Functions

- `get_indices(dim_name, coord_dims, indices, is_cloud=False)`: Validates and returns the start and stop indices for the specified dimension.
- `save_slices_as_tiff(dataset, url, file_location, z_start, is_cloud=False)`: Saves the image slices as TIFF files.
- `intern_info(url, file_path)`: Retrieves and prints information about the dataset in `intern` mode.
- `cloud_info(url, resolution, file_path)`: Retrieves and prints information about the dataset in `cloud` mode.
- `intern_convert(url, resolution, x, y, z, file_path)`: Downloads and saves image slices from BossDB.
- `cloud_convert(url, resolution, x, y, z, file_path)`: Downloads and saves image slices from CloudVolume.
- `parse_url(url)`: Parses and validates the URL format.

### Main Function

The `main` function uses `argparse` to parse command-line arguments and calls the appropriate functions based on the mode (`intern` or `cloud`) and the provided parameters.

### Running the Script

To run the script, use the command-line examples provided above, specifying the appropriate arguments for your use case.

### Running Tests

To run tests using `pytest`, navigate to the main directory and use the following command:

```sh
pytest
```

This will discover and run all the tests in the `tests` directory.
