from config.base_config import BaseConfig
from cloudvolume import CloudVolume
import pandas as pd
import requests

class ExtractInfo(BaseConfig):
    def __init__(self, config):
        super().__init__(
            config.x_dimensions, config.y_dimensions, 
            config.z_dimensions, config.output_path, config.img_uri, config.img_res, 
            config.img_link, config.seg, config.seg_uri, config.seg_res, config.seg_link,
            config.CAVEclient, config.mesh_ids, config.mesh_uri,
            config.project_name, config.syglass_directory, config.shader_settings_to_load_path
        )

    def cloud_info(self, data_type='image'):
        url = f"s3://bossdb-open-data/{self.img_uri}"
        spec_res = self.img_res

        if data_type=='segmentation':    
            url = f"s3://bossdb-open-data/{self.seg_uri}"
            spec_res = self.seg_res

        try:
            # First download base resolution to get all available res and check if input res is available
            vol = CloudVolume(url, fill_missing=True, use_https=True)
            print(vol.resolution)

            avail_res = list(vol.available_mips)
            if self.img_res is not None and self.img_res not in avail_res:
                raise ValueError(f"Specified resolution {self.img_res} is not available. Available resolutions are: {avail_res}")

            # Display dimensions for all available resolutions
            res_dims = []
            for res in avail_res:
                vol_res = CloudVolume(url, mip=res, fill_missing=True, use_https=True)
                bounds_res = vol_res.bounds
                x_bounds = bounds_res.maxpt[0] - bounds_res.minpt[0]
                y_bounds = bounds_res.maxpt[1] - bounds_res.minpt[1]
                z_bounds = bounds_res.maxpt[2] - bounds_res.minpt[2]
                res_dims.append([res, x_bounds, y_bounds, z_bounds])

            df = pd.DataFrame(res_dims, columns=["Resolution", "X (voxels)", "Y (voxels)", "Z (voxels)"])
            print(df.to_string(index=False))

            # Display dimensions for requested resolution
            req_dims = df[df["Resolution"] == spec_res]
            print(f"Requested {data_type} resolution {spec_res} has dimensions X: {req_dims['X (voxels)'].values[0]}, Y: {req_dims['Y (voxels)'].values[0]}, Z: {req_dims['Z (voxels)'].values[0]} voxels")

        except requests.exceptions.HTTPError as e:
            print(f"Error: {e.response.json().get('message')}")
            return