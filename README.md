# BossVR
![Logo](bossVR.jfif)

**BossVR** is a Python-based tool that allows you to interact with datasets from [BossDB](https://bossdb.org/projects) and create or modify syGlass projects. This tool is designed to handle various tasks, including retrieving information about datasets, downloading images in TIFF format, downloading and transforming meshes, creating syGlass projects with image stacks, mask layers, and meshes, and uploading and exporting annotations.

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

The `config.ini` file is used to configure your project's settings. Here is an example:

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

## Usage

The `main.py` script is the entry point for running the tool. It reads the configuration from `config.ini` and uses it to execute various tasks via the `PipelineController` class.

```sh
python main.py
```

### Available Functions

### Config Module
- **BaseConfig**: Handles the configuration settings for the tool, including dataset dimensions, paths, and project details.

### Pipeline Module
- **Annotations**: Manage annotations including extraction, importing, volumetric block operations, and ROI handling.
  - `extract_tracking_points()`: Extracts tracking points from a syGlass project.
  - `import_tracking_points(df)`: Imports tracking points from a DataFrame into a syGlass project.
  - `get_all_volumetric_blocks()`: Retrieves all volumetric blocks around tracking points.
  - `get_volumetric_block_around_point(block_num)`: Retrieves a specific volumetric block.
  - `export_tracings()`: Exports tracings to files.
  - `import_tracings(trace_file_path)`: Imports tracings from files.
  - `export_roi(roi_index)`: Exports ROI data as TIFF.
  - `import_roi(roi_index, roi_mask)`: Imports ROI data.

- **ExtractInfo**: Retrieves detailed information about datasets from BossDB.
  - `cloud_info(data_type='image')`: Retrieves and displays the available resolutions and dimensions for image or segmentation data.

- **ImageDownload**: Downloads images from BossDB and saves them in TIFF format.
  - `cloud_convert(data_type='image')`: Downloads cutout data from BossDB and saves it as TIFF files.

- **MeshDownload**: Downloads and transforms meshes from BossDB.
  - `download_meshes_cave(mesh_file_location)`: Downloads meshes using the CAVEclient.
  - `download_meshes_cv(mesh_file_location)`: Downloads meshes using CloudVolume.
  - `transform_meshes(mesh_file_location)`: Transforms mesh coordinates based on the dataset's resolution and dimensions.
  - `run_mesh_download()`: Executes the mesh download and transformation process.

- **ProjectCreation**: Handles the creation and modification of syGlass projects.
  - `create_base_project(first_img_image)`: Creates a new syGlass project with the downloaded image stack.
  - `add_mask_layer(proj_file_location, first_seg_image)`: Adds a mask layer to an existing syGlass project.
  - `add_mesh_objs(proj_file_location, mesh_file_location)`: Adds mesh objects to an existing syGlass project.

- **ShaderSettings**: Manages shader settings for syGlass projects.
  - `export_shader_settings()`: Exports shader settings from a syGlass project.
  - `apply_view_shader_settings()`: Applies shader settings to a syGlass project.
  - `open_project()`: Opens a syGlass project.

### Util Module
- **common_functions**: Provides utility functions for image processing, file handling, and other tasks.

## Example Workflow

Note these functions operate with the project specifications as configured in the config.file. It 

1. **Extract Dataset Information**:
   Retrieve information such as the dimensions of the dataset at each resolution level 
   - Use `PipelineController.extract_img_info()` to retrieve image dataset information
   - Use `PipelineController.extract_seg_info()` to retrieve segmentation dataset information

3. **Download Images and Meshes**:
   - Use `PipelineController.download_img()` to download images as a TIFF stack
   - Use `PipelineController.download_seg()` to download segmentation images as a TIFF stack
   - Use `PipelineController.run_mesh_download()` to download and transform meshes to the specified image stack

4. **Create syGlass Project**:
   - Use `PipelineController.create_project_only_img()` to create a project with just the images.
   - Use `PipelineController.create_project_img_mesh()` to create a project with the images and meshes.
   - Use `PipelineController.create_project_img_seg_mesh()` to create a project with images, segmentation masks, and meshes.

5. **Manage Annotations**:
   - Use `PipelineController.export_tracking_points()` to export annotation points.
   - Use `PipelineController.import_tracking_points(df)` to import annotation points.

6. **Manage Shader Settings**:
   - Use `PipelineController.export_shader_settings()` to export shader settings.
   - Use `PipelineController.apply_view_shader_settings()` to apply shader settings.
