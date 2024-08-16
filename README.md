# BossVR
![Logo](bossVR.jfif)

**BossVR** is a Python tool that allows you to interact with datasets from [BossDB](https://bossdb.org/projects) and create or modify [syGlass](https://www.syglass.io/) projects. This tool is designed to retrieve information about datasets, download images in TIFF format, download and transform meshes, create syGlass projects with image stacks, mask layers, and meshes, and upload and export annotations.

## Features

- **Dataset Information Retrieval**: Extract detailed information about your datasets from BossDB.
- **Image and Mesh Downloading**: Download images and meshes from BossDB in the desired format and resolution.
- **syGlass Project Creation**: Create syGlass projects with multiple layers, including images, masks, and meshes.
- **Annotation Management**: Export and import annotations and tracings for syGlass projects.
- **Shader Settings Management**: Export and apply shader settings in syGlass projects.

## Requirements

Install the required packages using the `requirements.txt` file:

```sh
pip install -r requirements.txt
```

Alternatively, set up a new environment with the `cloud_intern.yaml` file:

```sh
conda env create -f cloud_intern.yaml
```

This tool supports both `intern` and `CloudVolume` for accessing BossDB data. Follow the installation instructions for [intern](https://github.com/jhuapl-boss/intern) and [CloudVolume](https://github.com/seung-lab/cloud-volume?tab=readme-ov-file) for detailed guidance.

## Configuration

To run the script, modify the parameters in the configuration file named `config.ini`, located in the same directory as the script:

- `img_uri`: CloudVolume image data URI. Required.
- `img_res`: Desired resolution for image data. By default, `img_res=0`.
- `seg_uri`: CloudVolume segmentation data URI.
- `seg_res`: Desired resolution for segmentation data. By default, `seg_res=0`.
- `x_dimensions`: Range for X dimension in the format `x_start:x_stop`. If not provided, the entire range is extracted.
- `y_dimensions`: Range for Y dimension in the format `y_start:y_stop`. If not provided, the entire range is extracted.
- `z_dimensions`: Range for Z dimension in the format `z_start:z_stop`. If not provided, the entire range is extracted.
- `output_path`: Directory where the images, segmentations, meshes, and syGlass project should be saved. If not provided, images will be saved in the default directory.
- `CAVEclient`: Name of the CAVEclient bucket to pull meshes from. Optional.
- `mesh_ids`: List of mesh IDs to be downloaded and transformed. Required for downloading meshes. Otherwise optional.
- `mesh_uri`: CloudVolume URI to pull meshes from. If both `mesh_uri` and `CAVEclient` are provided, the script by default will use `CAVEclient`.
- `project_name`: Desired name of the project. Required.
- `syglass_directory`: File path to the syGlass installation. Folder containing built-in `syGlassCLI.exe`. Required for importing and exporting shader settings. Otherwise optional.
- `shader_settings_to_load_path`: File path to the JSON file of shader settings to load in the created project.

Example `config.ini` file:

```ini
[DEFAULT]
img_uri = yim_choe_bae2023/dauer1_364/em/em
img_res = 0 
seg = True 
seg_uri = yim_choe_bae2023/dauer1_364/seg_oct22
seg_res = 0  
x_dimensions = 600:9300
y_dimensions = 500:9600
z_dimensions = 0:364
output_path = ./yimchoebae
CAVEclient = 
mesh_ids = [1, 100, 101, 99]
mesh_uri = bae2024/dauer1/mito_seg_v4
project_name = yim_choe_bae2023_project
syglass_directory = C:/Program Files/syGlass/bin
shader_settings_to_load_path = ./shader_settings/shaderSettings.json
```

## CLI Usage

The `main.py` script can be executed from the command line to perform the commands below tasks. The dataset and project parameters must be specified in the config.ini file. 

### Available Commands

- **extract_img_info**: Retrieves image dataset information.
- **extract_seg_info**: Retrieves segmentation dataset information.
- **download_img**: Downloads images as a TIFF stack.
- **download_seg**: Downloads segmentation images as a TIFF stack.
- **run_mesh_download**: Downloads and transforms meshes.
- **create_project_only_img**: Creates a project with just the images.
- **create_project_img_mesh**: Creates a project with images and meshes.
- **create_project_img_seg_mesh**: Creates a project with images, segmentation masks, and meshes.
- **export_shader_settings**: Exports shader settings.
- **apply_view_shader_settings**: Applies shader settings.
- **open_project**: Opens a syGlass project.
- **export_tracking_points**: Exports annotation points as a dataframe.
- **import_tracking_points**: Imports annotation points from a dataframe.
- **get_all_volumetric_blocks**: Retrieves all volumetric blocks from counting points in the project.
- **get_volumetric_block_around_point**: Retrieves a specific volumetric block centered around a tracking point. Requires `--block_num`.
- **export_tracings**: Exports tracings as SWC files.
- **import_tracings**: Imports tracings from SWC files.
- **export_roi**: Exports ROI data as TIFF. Requires `--roi_index`.
- **import_roi**: Imports ROI data as a mask numpy array. Requires `--roi_index` and `--roi_mask`.

### Example Usage

1. **Extract Dataset Information**:
   ```sh
   python main.py extract_img_info
   python main.py extract_seg_info
   ```

2. **Download Images and Meshes**:
   ```sh
   python main.py download_img
   python main.py download_seg
   python main.py run_mesh_download
   ```

3. **Create syGlass Project**:
   ```sh
   python main.py create_project_only_img
   python main.py create_project_img_mesh
   python main.py create_project_img_seg_mesh
   ```

4. **Manage Annotations**:
   ```sh
   python main.py export_tracking_points
   python main.py import_tracking_points --data_frame_path path_to_dataframe
   python main.py get_all_volumetric_blocks
   python main.py get_volumetric_block_around_point --block_num 5
   python main.py export_tracings
   python main.py import_tracings --trace_file_path path_to_tracings
   python main.py export_roi --roi_index 1
   python main.py import_roi --roi_index 1 --roi_mask path_to_roi_mask
   ```

5. **Manage Shader Settings**:
   ```sh
   python main.py export_shader_settings
   python main.py apply_view_shader_settings
   python main.py open_project
   ```

**NOTE**: The project creation tools with pyGlass require a Windows operating system

**NOTE**: When importing and exporting annotations, the project cannot be actively open in syGlass simultaneously.

**NOTE**: To use `apply_view_shader_settings()`, the project must already be in the syGlass project directory. The function only renders the project in the specified shader settings, but does not automatically save the project with them. To save the settings to the project, this must be done in syGlass.
