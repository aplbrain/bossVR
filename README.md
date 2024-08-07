# BossDB Image Conversion Script

This script allows you to interact with datasets from [BossDB](https://bossdb.org/projects) with `intern` and `CloudVolume`. You can retrieve information about the dataset or download images in TIFF format with command-line interface. 

## Requirements

All the required packages can be installed using the `requirements.txt` file:

```sh
pip install -r requirements.txt
```

Or with conda, you can setup a new environment with the `cloud_intern.yaml` file:

```sh
conda env create -f cloud_intern.yaml
```

This code supports usage of both `intern` and  `CloudVolume` for reading of BossDB data and access to more detailed dataset info. Follow [intern installation instructions](https://github.com/jhuapl-boss/intern)) and [CloudVolume installation instructions](https://github.com/seung-lab/cloud-volume?tab=readme-ov-file)) for more information.

## Usage

The script can operate in two modes: `info`, to provide information about the dataset, or `download`, to download the images based on the provided parameters. Additionally, it can operate with either `intern` or `CloudVolume`

### Command-Line Arguments
- `mode`: Mode of script (`info` or `download`). Positional argument. Required.
- `-u`, `--url`: BossDB or CloudVolume path. Required.
- `-m`, `--method`: Method of implementation (`intern` or `cloud`). Optional. By default, `cloud` is used.
- `-r`, `--resolution`: Desired resolution level. Optional. By default, resolution=0.
- `-x`, `--x_dimensions`: Range for X dimension in the format `x_start:x_stop`. Optional. By default, the entire range is extracted.
- `-y`, `--y_dimensions`: Range for Y dimension in the format `y_start:y_stop`. Optional. By default, the entire range is extracted.
- `-z`, `--z_dimensions`: Range for Z dimension in the format `z_start:z_stop`. Optional. By default, the entire range is extracted.
- `-o`, `--output_path`: Directory where the TIFF files should be saved. Optional. By default, images will be saved in the default directory .
### Examples

#### 1. Retrieve Information About the Dataset

In `info` mode, the script will output the X, Y, and Z dimensions of the dataset at each available resolution level, in voxels, without downloading images.

With Intern:

```sh
python bossdb_to_tiff_converter.py info -m intern -u myCollection/myExperiment/myChannel
```

With CloudVolume

```sh
python bossdb_to_tiff_converter.py info -u myBossDB/s3/url
```

#### 2. Download Images with Intern

In download mode, by default, images will download in the default directory. 

To download images using `intern`, default mode:

```sh
python bossdb_to_tiff_converter.py download -m intern -u myCollection/myExperiment/myChannel
```

To download images using `intern`, specifying output directory:

```sh
python bossdb_to_tiff_converter.py download -m intern -u myCollection/myExperiment/myChannel -o /path/to/save/images
```

#### 3. Download Images with CloudVolume

To download images using `CloudVolume`, default mode:

```sh
python bossdb_to_tiff_converter.py download -u myBossDB/s3/url
```

To download images using `CloudVolume`, specifying output directory:

```sh
python bossdb_to_tiff_converter.py download -u myBossDB/s3/url -o /path/to/save/images
```

### Detailed Examples with Dimension, Resolution, and Output Specifications

#### Intern Examples

In `info` mode with `intern`, resolution can be specified:

```sh
python bossdb_to_tiff_converter.py info -intern -u myCollection/myExperiment/myChannel -r 2
```

In `download` mode with `intern`, resolution, dimension ranges to download over, and output file path can be specified:

```sh
python bossdb_to_tiff_converter.py download -intern -u myBossDB/s3/url -r 2 -x 0:1000 -y 0:1000 -z 0:100 -o /path/to/save/images
```

#### CloudVolume Examples

In `info` mode with `cloud`, resolution can be specified:

```sh
python bossdb_to_tiff_converter.py info -u myBossDB/s3/url -r 2
```

In `download` mode with `cloud`, resolution, dimension ranges to download over, and output file path can be specified:

```sh
python bossdb_to_tiff_converter.py download -u myBossDB/s3/url -r 2 -x 0:1000 -y 0:1000 -z 0:100 -o /path/to/save/images
```

## Script Details

### Functions

- `get_indices(dim_name, coord_dims, indices, is_cloud=False)`: Validates and returns the start and stop indices for the specified dimension.
- `save_slices_as_tiff(dataset, url, file_location, z_start, is_cloud=False)`: Saves the image slices as TIFF files.
- `intern_info(url, resolution)`: Retrieves and prints information about the dataset in `intern` mode.
- `cloud_info(url, resolution)`: Retrieves and prints information about the dataset in `cloud` mode.
- `intern_convert(url, path, resolution, x, y, z, output_path)`: Downloads and saves image slices from BossDB.
- `cloud_convert(url, path, resolution, x, y, z, output_path)`: Downloads and saves image slices from CloudVolume.
- `parse_url(url)`: Parses and validates the URL format.

### Main Function

The `main` function uses `argparse` to parse command-line arguments and calls the appropriate functions based on the mode (`intern` or `cloud`) and the provided parameters.

### Running the Script

To run the script, refer to the command-line examples provided above, specifying the appropriate arguments for your use case.

### Running Tests

To run tests using `pytest`, navigate to the main directory and use the following command:

```sh
pytest
```

This will discover and run all the tests in the `tests` directory.
