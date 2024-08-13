from config.base_config import BaseConfig
from cloudvolume import CloudVolume
from caveclient import CAVEclient
from util.common_functions import get_indices
import os
import glob
import trimesh

class MeshDownload(BaseConfig):
    def __init__(self, config):
        super().__init__(
            config.x_dimensions, config.y_dimensions, 
            config.z_dimensions, config.output_path, config.img_uri, config.img_res, 
            config.img_link, config.seg, config.seg_uri, config.seg_res, config.seg_link,
            config.CAVEclient, config.mesh_ids, config.mesh_uri,
            config.project_name, config.syglass_directory, config.shader_settings_to_load_path
        )

    def download_meshes_cave(self, mesh_file_location):
        # initialize CAVEclient
        client = CAVEclient(self.CAVEclient)
        vol = CloudVolume(client.info.segmentation_source(), progress=False, use_https=True)

        # specify where to save mesh objs
        os.makedirs(mesh_file_location, exist_ok=True)

        # iterate through mesh_ids and download
        for mesh_id in self.mesh_ids:
            mesh = vol.mesh.get([mesh_id], fuse=False)
            mesh_obj = mesh[mesh_id].to_obj()

            with open(os.path.join(mesh_file_location, f"{mesh_id}.obj"), 'wb') as f:
                f.write(mesh_obj)
            
    def download_meshes_cv(self, mesh_file_location):
        mesh_vol = CloudVolume(f"s3://bossdb-open-data/{self.mesh_uri}", fill_missing=True, use_https=True)

        # specify where to save mesh objs
        os.makedirs(mesh_file_location, exist_ok=True)

        # iterate through mesh_ids and download
        for mesh_id in self.mesh_ids:
            mesh = mesh_vol.mesh.get([mesh_id], fuse=False)
            mesh_obj = mesh[mesh_id].to_obj()

            with open(os.path.join(mesh_file_location, f"{mesh_id}.obj"), 'wb') as f:
                f.write(mesh_obj)
                
    def transform_meshes(self, mesh_file_location):
        obj_list = os.path.join(mesh_file_location, '*.obj')

        # get image resolution to scale meshes appropriately
        img_vol = CloudVolume(f"s3://bossdb-open-data/{self.img_uri}", mip=self.img_res, fill_missing=True, use_https=True)
        x_start, _, y_start, _, z_start, _ = get_indices(img_vol, self.x_dimensions, self.y_dimensions, self.z_dimensions)
        img_resolution = img_vol.resolution

        for path in glob.glob(obj_list):    
            mesh = trimesh.load(path)
            mesh.vertices -= [x_start * img_resolution[0], y_start * img_resolution[1], z_start * img_resolution[2]]
            mesh.export(path)
    
    def run_mesh_download(self):
        mesh_file_location = os.path.join(self.output_path, "meshes")
        if self.CAVEclient == '':
            self.download_meshes_cv(mesh_file_location)
        else:
            self.download_meshes_cave(mesh_file_location)
        self.transform_meshes(mesh_file_location)
        return mesh_file_location