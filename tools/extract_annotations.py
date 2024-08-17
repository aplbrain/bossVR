from config.base_config import BaseConfig
from cloudvolume import CloudVolume
import pandas as pd
import os
import syglass as sy
from datetime import datetime
import numpy as np
from utils.common_functions import get_indices
from utils.common_functions import transform_annotation_points
from utils.common_functions import save_slices_as_tiff
import glob
import tifffile

class Annotations(BaseConfig):
    def __init__(self, config):
        super().__init__(
            config.x_dimensions, config.y_dimensions, 
            config.z_dimensions, config.output_path, config.img_uri, config.img_res, 
            config.img_link, config.seg_uri, config.seg_res, config.seg_link,
            config.CAVEclient, config.mesh_ids, config.mesh_uri,
            config.project_name, config.syglass_directory, 
            config.shader_settings_to_load_path, config.annotation_csv_file_path, config.trace_file_path
        )
        
    def extract_tracking_points(self):
        project_file_location = os.path.join(self.output_path, self.project_name, f'{self.project_name}.syg')
        project = sy.get_project(project_file_location)
        counts = project.get_counting_points()

        img_vol = CloudVolume(f"s3://bossdb-open-data/{self.img_uri}", mip=self.img_res, fill_missing=True, use_https=True)
        img_resolution = img_vol.resolution
        x, _, y, _, z, _ = get_indices(img_vol, self.x_dimensions, self.y_dimensions, self.z_dimensions)
        
        rows = []
        columns = ['id', 'created', 'superceded_id', 'valid', 'classification_system',
                'cell_type', 'pt_supervoxel_id', 'pt_root_id', 'pt_position', 'og_pt_position']
        unique_id = 1
        for color, vertices in counts.items():
            for vertex in vertices:
                transformed_vertex = transform_annotation_points(vertex, img_resolution, x, y, z)
                new_row = {
                    'id': unique_id,
                    'created': datetime.now().isoformat(),
                    'superceded_id': '',
                    'valid': '',
                    'classification_system': '',
                    'cell_type': color,
                    'pt_supervoxel_id': '',
                    'pt_root_id': '',
                    'pt_position': transformed_vertex,
                    'og_pt_position': vertex
                }
                rows.append(new_row)
                unique_id += 1

        df = pd.DataFrame(rows, columns=columns)    
        return df

    def import_tracking_points(self):
        df_points = pd.read_csv(self.annotation_csv_file_path)
        
        project_file_location = os.path.join(self.output_path, self.project_name, f'{self.project_name}.syg')
        project = sy.get_project(project_file_location)
        counts = project.get_counting_points()

        img_vol = CloudVolume(f"s3://bossdb-open-data/{self.img_uri}", mip=self.img_res, fill_missing=True, use_https=True)
        img_resolution = img_vol.resolution
        x, _, y, _, z, _ = get_indices(img_vol, self.x_dimensions, self.y_dimensions, self.z_dimensions)

        for _, row in df_points.iterrows():
            color = row['cell_type']
            transformed_vertex = row['pt_position']
            original_vertex = [
                transformed_vertex[0] - x * img_resolution[0],
                transformed_vertex[1] - y * img_resolution[1],
                transformed_vertex[2] - z * img_resolution[2]
            ]

            counts[color] = np.append(counts[color], [original_vertex], axis=0)
        
        for color in counts:
            if counts[color].size == 0:
                counts[color] = np.empty((0, 3))
        
        project.set_counting_points(counts)

        return self.extract_tracking_points()


    def get_all_volumetric_blocks(self, side_length=100):
        # side length is in voxels
        # Get counting points for the default experiment
        project_file_location = os.path.join(self.output_path, self.project_name, f'{self.project_name}.syg')
        project = sy.get_project(project_file_location)
        counts = project.get_counting_points()

        # Determine the index of the highest resolution level
        resolution = len(project.get_resolution_map()) - 1

        # Define a side length and dimensions for our cube
        dimensions = np.full(3, side_length)

        # Iterate over each point in each color series for the default experiment
        blocks = []
        for block_num, color in enumerate(counts):
                for point in counts[color]:
                    # Calculate the offset to each cube based on point position
                    offset = np.maximum(point.astype(int) - side_length / 2, np.zeros(3))

                    # Retrieve a full-resolution cube from the volume
                    block = project.get_custom_block(0, resolution, offset, dimensions)

                    blocks.append(block)
                   
        return blocks
    
    def get_volumetric_block_around_point(self, block_num, side_length=100):
        project_file_location = os.path.join(self.output_path, self.project_name, f'{self.project_name}.syg')
        project = sy.get_project(project_file_location)

        # Ensure real_point is a NumPy array
        df_points = self.extract_tracking_points()
        real_point = df_points.loc[df_points['id'] == block_num, 'og_pt_position']

        # Convert real_point and side_length to numpy arrays if they aren't already
        real_point = np.array(real_point)
        side_length = np.array(side_length)

        offset = [np.maximum(0, int(real_point[0][0]) - side_length/2), np.maximum(0, int(real_point[0][1]) - side_length/2), np.maximum(0, int(real_point[0][2]) - side_length/2)]
        
        resolution = len(project.get_resolution_map()) - 1

        dimensions = np.full(3, side_length)
        block = project.get_custom_block(0, resolution, offset, dimensions)

        # Transform the offset
        img_vol = CloudVolume(f"s3://bossdb-open-data/{self.img_uri}", mip=self.img_res, fill_missing=True, use_https=True)
        img_resolution = img_vol.resolution
        x, _, y, _, z, _ = get_indices(img_vol, self.x_dimensions, self.y_dimensions, self.z_dimensions)
        transformed_offset = transform_annotation_points(offset, img_resolution, x, y, z)

        # Convert to tiff stack
        save_slices_as_tiff(block.data, self.img_uri.replace("/", "_"), self.output_path, transformed_offset, "block")

        return block

    def export_tracings(self):
        project_file_location = os.path.join(self.output_path, self.project_name, f'{self.project_name}.syg')
        project = sy.get_project(project_file_location)

        # Save the tracings (will export each disconnected component as a separate SWC file)
        project.save_tracings(directory=os.path.join(self.output_path))
    
    def import_tracings(self):
        project_file_location = os.path.join(self.output_path, self.project_name, f'{self.project_name}.syg')
        project = sy.get_project(project_file_location)

        self.trace_file_path = os.path.join(self.trace_file_path, '*.swc')
        trace_list = glob.glob(self.trace_file_path)
        project.import_swcs(trace_list, "default")

    def export_roi(self, roi_index):
        project_file_location = os.path.join(self.output_path, self.project_name, f'{self.project_name}.syg')
        project = sy.get_project(project_file_location)
    
        # Get the raw ROI data block
        roi_block = project.get_roi_data(roi_index)

        # Save the ROI data as a tiff file
        roi_img_block_file_path = os.path.join(self.output_path, self.project_name, f"{self.project_name}_roi_img_block_tiffs")
        tifffile.imsave(roi_img_block_file_path, roi_block.data)

        # Get the mask block of the ROI
        mask_block = project.get_mask(roi_index)

        # Save the ROI data as a tiff file
        roi_mask_block_file_path = os.path.join(self.output_path, self.project_name, f"{self.project_name}_roi_mask_block_tiffs")
        os.makedirs(roi_mask_block_file_path, exist_ok=True)
        tifffile.imsave(roi_mask_block_file_path, mask_block.data)
    
    def import_roi(self, roi_index, roi_mask):
        project_file_location = os.path.join(self.output_path, self.project_name, f'{self.project_name}.syg')
        project = sy.get_project(project_file_location)

        # Import an ROI mask numpy array (z,y,x,channel count)
        project.import_mask(roi_mask, roi_index)