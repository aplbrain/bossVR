# syGlass Project Creation for BossDB Datasets

This script allows you to create syGlass projects for datasets from [BossDB](https://bossdb.org/projects) with `intern` and `CloudVolume`. You can retrieve information about the dataset, download image and segmentation data in TIFF format, and create syGlass projects with image and mask layers. 

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

The script can operate in three modes: `info`, to provide information about the dataset, `image`, to only download the images as TIFFs based on the provided parameters, and `info` to download the images as TIFFs and create the corresponding syGlass project. Additionally, it can operate with either `intern` or `CloudVolume`

### Configuration File Arguments

To run the script, modify the parameters in the configuration file in the same directory as the script, config.ini

- `mode`: Mode of script (`info`, `download`, `project`).
- `img_uri`: BossDB or CloudVolume image data URI.
- `img_res`: Desired resolution for image data. By default, img_res=0  
- `seg`: Indicates whether the user wants to download segmentation data and add a mask layer to the project. By default, it is true.
- `seg_uri`: BossDB or CloudVolume segmentation data URI.
- `seg_res`: Desired resolution for segmentation data. By default, seg_res=0
- `method`: Method of image downloading (`intern` or `cloud`). By default, method=cloud
- `x_dimensions`: Range for X dimension in the format `x_start:x_stop`. If not provided, the entire range is extracted.
- `y_dimensions`: Range for X dimension in the format `x_start:x_stop`. If not provided, the entire range is extracted.
- `z_dimensions`: Range for X dimension in the format `x_start:x_stop`. If not provided, the entire range is extracted.
- `output_path`: Directory where the syGlass project and TIFF files should be saved. If not provided, images will be saved in the default directory .
