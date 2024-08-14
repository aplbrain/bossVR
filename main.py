import configparser
from config.base_config import BaseConfig
from pipeline.pipeline_controller import PipelineController
import ast

if __name__ == '__main__':
    config_file = configparser.ConfigParser(allow_no_value=True)
    config_file.read('config.ini')

    config = BaseConfig(
        x_dimensions=config_file['DEFAULT']['x_dimensions'],
        y_dimensions=config_file['DEFAULT']['y_dimensions'],
        z_dimensions=config_file['DEFAULT']['z_dimensions'],
        output_path=config_file['DEFAULT']['output_path'],
        img_uri=config_file['DEFAULT']['img_uri'], 
        img_res=int(config_file['DEFAULT']['img_res']),
        img_link = f"s3://bossdb-open-data/{config_file['DEFAULT']['img_uri']}",
        seg=config_file['DEFAULT']['seg'],
        seg_uri=config_file['DEFAULT']['seg_uri'], 
        seg_res=int(config_file['DEFAULT']['seg_res']),
        seg_link = f"s3://bossdb-open-data/{config_file['DEFAULT']['seg_uri']}",
        CAVEclient=config_file['DEFAULT']['CAVEclient'],
        mesh_ids=ast.literal_eval(config_file['DEFAULT']['mesh_ids']),
        mesh_uri=config_file['DEFAULT']['mesh_uri'],
        project_name=config_file['DEFAULT']['project_name'],
        syglass_directory=config_file['DEFAULT']['syglass_directory'],
        shader_settings_to_load_path=config_file['DEFAULT']['shader_settings_to_load_path']
    )

    pipeline = PipelineController(config)
    pipeline.run_mesh_download()