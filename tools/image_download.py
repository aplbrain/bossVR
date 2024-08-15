from config.base_config import BaseConfig
from utils.common_functions import get_indices
from utils.common_functions import check_res_cloud
import os
from PIL import Image
import requests
from tqdm import tqdm
from cloudvolume import CloudVolume
import numpy as np
from utils.common_functions import save_slices_as_tiff

class ImageDownload(BaseConfig):
    def __init__(self, config):
        super().__init__(
            config.x_dimensions, config.y_dimensions, 
            config.z_dimensions, config.output_path, config.img_uri, config.img_res, 
            config.img_link, config.seg, config.seg_uri, config.seg_res, config.seg_link,
            config.CAVEclient, config.mesh_ids, config.mesh_uri,
            config.project_name, config.syglass_directory, config.shader_settings_to_load_path
        )

    def cloud_convert(self, data_type='image'):
        try:
            uri = self.img_uri
            spec_res = self.img_res

            if (data_type=='segmentation'):
                check_res_cloud(self.img_link, self.img_res, self.seg_link, self.seg_res)
                uri = self.seg_uri
                spec_res = self.seg_res

            vol = CloudVolume(f"s3://bossdb-open-data/{uri}", mip=spec_res, fill_missing=True, use_https=True)

            x_start, x_stop, y_start, y_stop, z_start, z_stop = get_indices(vol, self.x_dimensions, self.y_dimensions, self.z_dimensions)

            print(f"Downloading {data_type} cutout data over ranges X: {x_start}:{x_stop}, Y: {y_start}:{y_stop}, Z: {z_start}:{z_stop}...")
            cutout = vol[x_start:x_stop, y_start:y_stop, z_start:z_stop]
            print("Download complete.")

            if not os.path.exists(self.output_path):
                os.makedirs(self.output_path)
                print(f"Directory {self.output_path} created.")

            first_image = save_slices_as_tiff(cutout, uri.replace("/", "_"), self.output_path, z_start, data_type)
            return first_image

        except requests.exceptions.HTTPError as e:
            print(f"Error: {e.response.json().get('message')}")
        except ValueError as e:
            print(f"Error: {e}")