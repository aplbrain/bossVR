class BaseConfig:
    def __init__(self, x_dimensions, y_dimensions, z_dimensions, output_path, 
                 img_uri, img_res, img_link, seg, seg_uri, seg_res, seg_link, CAVEclient, mesh_ids, mesh_uri, project_name, syglass_directory, shader_settings_to_load_path):
        self.x_dimensions = x_dimensions
        self.y_dimensions = y_dimensions
        self.z_dimensions = z_dimensions
        self.output_path = output_path
        self.img_uri = img_uri
        self.img_res = img_res
        self.img_link = img_link
        self.seg = seg
        self.seg_uri = seg_uri
        self.seg_res = seg_res
        self.seg_link = seg_link
        self.CAVEclient = CAVEclient
        self.mesh_ids = mesh_ids
        self.mesh_uri = mesh_uri
        self.project_name = project_name
        self.syglass_directory = syglass_directory
        self.shader_settings_to_load_path = shader_settings_to_load_path