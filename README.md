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

To run the script, modify the parameters in the configuration file in the same directory as the script, config.ini

- `img_uri`:  CloudVolume image data URI. Required.
- `img_res`: Desired resolution for image data. By default, img_res=0  
- `seg_uri`:  CloudVolume segmentation data URI.
- `seg_res`: Desired resolution for segmentation data. By default, seg_res=0
- `x_dimensions`: Range for X dimension in the format `x_start:x_stop`. If not provided, the entire range is extracted.
- `y_dimensions`: Range for X dimension in the format `x_start:x_stop`. If not provided, the entire range is extracted.
- `z_dimensions`: Range for X dimension in the format `x_start:x_stop`. If not provided, the entire range is extracted.
- `output_path`: Directory where the images, segmentations, meshes, and syGlass project should be saved. If not provided, images will be saved in the default directory
- `CAVEclient`: Name of the CAVEclient bucket to pull meshes from. Optional.
- `mesh_ids`: List of mesh IDs to be downloaded and transformed. Required for downloading meshes. Otherwise optional. 
- `mesh_uri`: CloudVolume URI to pull meshes from. If both  `mesh_uri` and `CAVEclient` are provided, script by default will use `CAVEclient`.
- `project_name`: Desired name of project. Required. 
- `syglass_directory`: File path to syGlass installation. Folder containing built-in syGlassCLI.exe. Required for importing and exporting of shader settings. Otherwise optional. 
- `shader_settings_to_load_path`: File path to JSON file of shader settings to load in created project. 

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

### Available Functions

### Config Module
- **BaseConfig**: Handles the configuration settings for the tool, including dataset dimensions, paths, and project details.

### Pipeline Module

- **ExtractInfo**: Retrieves detailed information about datasets from BossDB.
  - `cloud_info(data_type='image')`: Retrieves and displays the available resolutions and dimensions for image or segmentation data.

- **ImageDownload**: Downloads images from BossDB and saves them in TIFF format.
  - `cloud_convert(data_type='image')`: Downloads cutout data from BossDB and saves it as TIFF files. Can operate on both image and segmentation stacks. 
 
- **Annotations**: Manage annotations including extraction, importing, volumetric block operations, and ROI handling.
  - `extract_tracking_points()`: Extracts tracking points from a syGlass project as a 'CAVE annotation table'-like DataFrame. 
  - `import_tracking_points(df)`: Imports tracking points from a 'CAVE annotation table'-like DataFrame into a syGlass project.
  - `get_all_volumetric_blocks()`: Retrieves all volumetric blocks around tracking points. Returns a list of syGlass `blocks`. 
  - `get_volumetric_block_around_point(block_num)`: Retrieves a specific volumetric block centered around a particular tracking point, and converts it into a TIFF stack. `block_num` denotes the index of the block, as numbered in the counting point annotation table.
  - `export_tracings()`: Exports tracings to SWC files in the directory. 
  - `import_tracings(trace_file_path)`: Imports tracings from SWC files.
  - `export_roi(roi_index)`: Exports ROI data as TIFF. Indexed by ROI index. 
  - `import_roi(roi_index, roi_mask)`: Imports ROI data as a mask numpy array. 

- **MeshDownload**: Downloads and transforms meshes from BossDB.
  - `download_meshes_cave(mesh_file_location)`: Downloads meshes using the CAVEclient.
  - `download_meshes_cv(mesh_file_location)`: Downloads meshes using CloudVolume.
  - `transform_meshes(mesh_file_location)`: Transforms mesh coordinates based on the dataset's resolution and dimensions, to co-register with the image stacks in the syGlass project.
  - `run_mesh_download()`: Executes the mesh download and transformation process.

- **ProjectCreation**: Handles the creation and modification of syGlass projects.
  - `create_base_project(first_img_image)`: Creates a new syGlass project with the downloaded image stack.
  - `add_mask_layer(proj_file_location, first_seg_image)`: Adds a mask layer to the existing syGlass project.
  - `add_mesh_objs(proj_file_location, mesh_file_location)`: Adds mesh objects to the existing syGlass project.

- **ShaderSettings**: Manages shader settings for syGlass projects.
  - `export_shader_settings()`: Exports shader settings from a syGlass project as a JSON file. Saves the file in ./output_file_path/shader_settings/project_name_shader_settings.json
  - `apply_view_shader_settings()`: Opens the syGlass project with the specific shader settings JSON specified in config.ini
  - `open_project()`: Opens a syGlass project.

### Util Module
- **common_functions**: Provides utility functions for image processing, file handling, and other tasks.

## Example Workflow and Usage

The `main.py` script is the entry point for running the tool. It reads the configured project parameters from `config.ini` and uses it to execute various tasks via the `PipelineController` class.

```sh
python main.py
```

1. **Extract Dataset Information**:
   Retrieve information such as the dimensions of the dataset at each resolution level.
   - Use `PipelineController.extract_img_info()` to retrieve image dataset information.
   - Use `PipelineController.extract_seg_info()` to retrieve segmentation dataset information.

3. **Download Images and Meshes**:
   - Use `PipelineController.download_img()` to download images as a TIFF stack.
   - Use `PipelineController.download_seg()` to download segmentation images as a TIFF stack.
   - Use `PipelineController.run_mesh_download()` to download and transform meshes to the specified image stack.

4. **Create syGlass Project**:
   - Use `PipelineController.create_project_only_img()` to create a project with just the images.
   - Use `PipelineController.create_project_img_mesh()` to create a project with the images and meshes.
   - Use `PipelineController.create_project_img_seg_mesh()` to create a project with images, segmentation masks, and meshes.

5. **Manage Annotations**:
   - Use `PipelineController.export_tracking_points()` to export annotation points as a dataframe. 
   - Use `PipelineController.import_tracking_points(df)` to import annotation points from a dataframe.
   - Use `PipelineController.get_all_volumetric_blocks()` to export list of volumetric blocks from counting points in project.
   - Use `PipelineController.get_volumetric_block_around_point(block_num)` to export TIFF image stack around a particular counting point.
   - Use `PipelineController.export_tracings()` to export tracings from syGlass project as .SWC files.
   - Use `PipelineController.import_tracings(trace_file_path)` to import .SWC file tracings from specified directory into syGlass project.
   - Use `PipelineController.export_roi(roi_index)` to a particular ROI as TIFF.
   - Use `PipelineController.import_roi(roi_index, roi_mask)` to create an ROI from a mask numpy array.
  
**NOTE**: When importing and exporting annotations, the project cannot be actively open in syGlass stimultaneously. 

6. **Manage Shader Settings**:
   - Use `PipelineController.export_shader_settings()` to export shader settings.
   - Use `PipelineController.apply_view_shader_settings()` to apply shader settings.
  
**NOTE**: To use apply_view_shader_settings(), the project must already be in the syGlass project directory. The function only renders the project in the specified shader settings, but does not automatically save the project with them. To save the settings to the project, this must be done in syGlass. 
  
