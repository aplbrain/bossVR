import configparser
from config.base_config import BaseConfig
from tools.bossvr_controller import BossVRController
import ast
import argparse

def main(args):
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
        seg_uri=config_file['DEFAULT']['seg_uri'], 
        seg_res=int(config_file['DEFAULT']['seg_res']),
        seg_link = f"s3://bossdb-open-data/{config_file['DEFAULT']['seg_uri']}",
        CAVEclient=config_file['DEFAULT']['CAVEclient'],
        mesh_ids=ast.literal_eval(config_file['DEFAULT']['mesh_ids']),
        mesh_uri=config_file['DEFAULT']['mesh_uri'],
        project_name=config_file['DEFAULT']['project_name'],
        syglass_directory=config_file['DEFAULT']['syglass_directory'],
        shader_settings_to_load_path=config_file['DEFAULT']['shader_settings_to_load_path'],
        annotation_csv_file_path = config_file['DEFAULT']['annotation_csv_file_path'],
        trace_file_path = config_file['DEFAULT']['trace_file_path']
    )

    controller = BossVRController(config)

    if args.command == "extract_img_info":
        controller.extract_img_info()
    elif args.command == "extract_seg_info":
        controller.extract_seg_info()
    elif args.command == "download_img":
        controller.download_img()
    elif args.command == "download_seg":
        controller.download_seg()
    elif args.command == "run_mesh_download":
        controller.run_mesh_download()
    elif args.command == "create_project_only_img":
        controller.create_project_only_img()
    elif args.command == "create_project_img_seg":
        controller.create_project_img_seg()
    elif args.command == "create_project_img_mesh":
        controller.create_project_img_mesh()
    elif args.command == "create_project_img_seg_mesh":
        controller.create_project_img_seg_mesh()
    elif args.command == "export_shader_settings":
        controller.export_shader_settings()
    elif args.command == "apply_view_shader_settings":
        controller.apply_view_shader_settings()
    elif args.command == "open_project":
        controller.open_project()
    elif args.command == "export_tracking_points":
        controller.export_tracking_points()
    elif args.command == "import_tracking_points":
        controller.import_tracking_points()
    elif args.command == "get_all_volumetric_blocks":
        controller.get_all_volumetric_blocks()
    elif args.command == "get_volumetric_block_around_point":
        controller.get_volumetric_block_around_point(args.block_num)
    elif args.command == "export_tracings":
        controller.export_tracings()
    elif args.command == "import_tracings":
        controller.import_tracings()
    elif args.command == "export_roi":
        controller.export_roi(args.roi_index)
    elif args.command == "import_roi":
        controller.import_roi(args.roi_index, args.roi_mask)
    else:
        print(f"Command {args.command} not recognized.")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Run BossVR operations from the command line.")
    parser.add_argument('command', type=str, help="Command to run, corresponding to a method in BossVRController.")
    parser.add_argument('--block_num', type=int, help="Block number for get_volumetric_block_around_point.", required=False)
    parser.add_argument('--roi_index', type=int, help="ROI index for export/import ROI.", required=False)
    parser.add_argument('--roi_mask', type=str, help="ROI mask for import_roi.", required=False)
    args = parser.parse_args()
    main(args)