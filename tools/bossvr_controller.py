# /pipeline/pipeline_controller.py
from tools.extract_info import ExtractInfo
from tools.image_download import ImageDownload
from tools.mesh_download import MeshDownload
from tools.project_creation import ProjectCreation
from tools.save_shader_settings import ShaderSettings
from tools.extract_annotations import Annotations

class BossVRController:
    def __init__(self, config):
        self.config = config
        self.extract_info = ExtractInfo(config)
        self.image_download = ImageDownload(config)
        self.mesh_download = MeshDownload(config)
        self.project_creation = ProjectCreation(config)
        self.save_shader_settings = ShaderSettings(config)
        self.extract_annotations = Annotations(config)

    def extract_img_info(self):
        self.extract_info.cloud_info()

    def extract_seg_info(self):
        self.extract_info.cloud_info('segmentation')

    def download_img(self):
        self.image_download.cloud_convert()

    def download_seg(self):
        self.image_download.cloud_convert('segmentation')

    def run_mesh_download(self):
        self.mesh_download.run_mesh_download()

    def create_project_only_img(self):
        first_img_image = self.image_download.cloud_convert()
        self.project_creation.create_base_project(first_img_image)

    def create_project_img_seg(self):
        first_img_image = self.image_download.cloud_convert()
        base_proj_path = self.project_creation.create_base_project(first_img_image)
        first_seg_image = self.image_download.cloud_convert('segmentation')
        self.project_creation.add_mask_layer(base_proj_path, first_seg_image)
        
    def create_project_img_mesh(self):
        first_img_image = self.image_download.cloud_convert()
        base_proj_path = self.project_creation.create_base_project(first_img_image)
        mesh_file_path = self.mesh_download.run_mesh_download()
        self.project_creation.add_mesh_objs(base_proj_path, mesh_file_path)

    def create_project_img_seg_mesh(self):
        first_img_image = self.image_download.cloud_convert()
        base_proj_path = self.project_creation.create_base_project(first_img_image)
        first_seg_image = self.image_download.cloud_convert('segmentation')
        mask_proj_path = self.project_creation.add_mask_layer(base_proj_path, first_seg_image)
        mesh_file_path = self.mesh_download.run_mesh_download()
        self.project_creation.add_mesh_objs(mask_proj_path, mesh_file_path)

    def export_shader_settings(self):
        self.save_shader_settings.export_shader_settings()
    
    def apply_view_shader_settings(self):
        self.save_shader_settings.apply_view_shader_settings()
    
    def open_project(self):
        self.save_shader_settings.open_project()
    
    def export_tracking_points(self):
        return self.extract_annotations.extract_tracking_points()

    def import_tracking_points(self, df):
        # df is annotation table with points
        return self.extract_annotations.import_tracking_points(df)
    
    def get_all_volumetric_blocks(self):
        return self.extract_annotations.get_all_volumetric_blocks()
    
    def get_volumetric_block_around_point(self, block_num):
        self.extract_annotations.get_volumetric_block_around_point(block_num)
    
    def export_tracings(self):
        self.extract_annotations.export_tracings()
    
    def import_tracings(self, trace_file_path):
        self.extract_annotations.import_tracings(trace_file_path)
    
    def export_roi(self, roi_index):
        self.extract_annotations.export_roi(roi_index)
    
    def import_roi(self, roi_index, roi_mask):
        self.extract_annotations.import_roi(roi_index, roi_mask)