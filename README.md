# BossVR
https://github.com/user-attachments/assets/359d64c9-5494-4d80-8e8d-05bc388210b9

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

Alternatively, set up a new environment with the `bossVR.yaml` file:

```sh
conda env create -f bossVR.yaml
```

This tool supports both `intern` and `CloudVolume` for accessing BossDB data. Follow the installation instructions for [intern](https://github.com/jhuapl-boss/intern) and [CloudVolume](https://github.com/seung-lab/cloud-volume?tab=readme-ov-file) for detailed guidance.

## Available Functions

### Config Module
- **BaseConfig**: Handles the configuration settings for the tool, including dataset dimensions, paths, and project details.

### Pipeline Module

- **ExtractInfo**: Retrieves detailed information about datasets from BossDB.
  - `cloud_info(data_type='image')`: Retrieves and displays the available resolutions and dimensions for image or segmentation data.

- **ImageDownload**: Downloads images from BossDB and saves them in TIFF format.
  - `cloud_convert(data_type='image')`: Downloads cutout data from BossDB and saves it as TIFF files. Can operate on both image and segmentation stacks.
  - The dimensions for image download are specified in the configuration file, but are automatically calculated for the segmentation (ex. if both are not in the same resolution). 
 
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

**common_functions**: Provides utility functions for image processing, file handling, and other tasks.

- `save_slices_as_tiff(dataset, path, file_location, offset, data_type='')`: 
  Saves image slices from a 3D dataset as TIFF files. The function supports both block-based and standard image stacks and handles image rotation and flipping to transform image orientation consistent with how images are loaded in syGlass

- `get_pair_indices(index, dim, vol, indices)`: 
  Parses and validates index ranges for a given dimension of a 3D volume, ensuring the range is within the volume bounds.

- `get_indices(vol, x_indices, y_indices, z_indices)`: 
  Retrieves and validates the start and stop indices for the X, Y, and Z dimensions of a 3D volume.

- `parse_url(url)`: 
  Parses a URL to ensure it contains the correct format for accessing a dataset from BossDB with CloudVolume.

- `check_res_cloud(img_uri, img_res, seg_uri, seg_res)`: 
  Checks if the resolution of image and segmentation data match. If they don't, it raises a warning and suggests downsampling the larger dataset.

- `transform_annotation_points(vertex, img_resolution, x, y, z)`: 
  Transforms annotation points from the syGlass real-world coordinate system to the dataset coordinate system of voxels.

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
- **run_mesh_download**: Downloads and transforms meshes, co-registered to the image and segmentation stacks
- **create_project_only_img**: Creates a project with just the images.
- **create_project_img_mesh**: Creates a project with images and meshes.
- **create_project_img_seg_mesh**: Creates a project with images, segmentation masks, and meshes.
- **export_shader_settings**: Exports shader settings as a JSON.
- **apply_view_shader_settings**: Opens project in specified shader settings.
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

**Notes/Future Improvements**: 
1. The project creation steps may raise errors if syGlass believes a project is still open, or for other  reasons. In such cases, download the images, segmentations, meshes as individual steps, and manually upload to syGlass, specifying the voxel resolution.
2. The project creation tools with pyGlass require a Windows operating system.
3. When importing and exporting annotations, the project cannot be actively open in syGlass simultaneously.
4. To use `apply_view_shader_settings()`, the project must already be in the syGlass project directory. The function only renders the project in the specified shader settings, but does not automatically save the project with them. To save the settings to the project, this must be done in syGlass.
