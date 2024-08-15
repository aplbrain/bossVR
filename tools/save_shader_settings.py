from config.base_config import BaseConfig
import subprocess
import os

# Functionality for exporting, importing shader settings, and opening a syglass project

class ShaderSettings(BaseConfig):
    def __init__(self, config):
        super().__init__(
            config.x_dimensions, config.y_dimensions, 
            config.z_dimensions, config.output_path, config.img_uri, config.img_res, 
            config.img_link, config.seg, config.seg_uri, config.seg_res, config.seg_link,
            config.CAVEclient, config.mesh_ids, config.mesh_uri,
            config.project_name, config.syglass_directory, config.shader_settings_to_load_path
        )

    def export_shader_settings(self):
        # open the project, then export as JSON -> do error handling for if the project doesn't exist
        command = "syGlassCLI"
        # Assuming self.output_path is an absolute path
        shader_settings_path = os.path.join(self.output_path, "shader_settings")
        os.makedirs(shader_settings_path, exist_ok=True)
        # Construct absolute path for the JSON file
        proj_shader_settings_path = os.path.abspath(os.path.join(shader_settings_path, f'{self.project_name}_shader_settings.json'))
        export_shader_args = [
            "-l", self.project_name,  # open syGlass project
            "-e", proj_shader_settings_path  # export shader settings
        ]
        os.chdir(self.syglass_directory)  # Change directory if needed
        open_export_result = subprocess.run([command] + export_shader_args, capture_output=True, text=True)
        print(open_export_result.stdout)
    
    def apply_view_shader_settings(self):
        # open the project, then imoprt a JSON -> do error handling for if the project doesn't exist
        command = "syGlassCLI"

        apply_shader_args = [
            "-l", self.project_name,  # open syGlass project
            "-i", self.shader_settings_to_load_path  # export shader settings
        ]
        os.chdir(self.syglass_directory)  # Change directory if needed
        apply_settings_result = subprocess.run([command] + apply_shader_args, capture_output=True, text=True)
        print(apply_settings_result.stdout)
    
    def open_project(self):
        command = "syGlassCLI"
        open_proj_args = [
            "-l", self.project_name,  # open syGlass project
        ]
        os.chdir(self.syglass_directory)  # Change directory if needed
        open_proj_result = subprocess.run([command] + open_proj_args, capture_output=True, text=True)
        print(open_proj_result.stdout)