from config.base_config import BaseConfig
from syglass import pyglass
import time
from tqdm import tqdm
import glob
import os
import syglass as sy
import numpy as np

class ProjectCreation(BaseConfig):
    def __init__(self, config):
        super().__init__(
            config.x_dimensions, config.y_dimensions, 
            config.z_dimensions, config.output_path, config.img_uri, config.img_res, 
            config.img_link, config.seg_uri, config.seg_res, config.seg_link,
            config.CAVEclient, config.mesh_ids, config.mesh_uri,
            config.project_name, config.syglass_directory, 
            config.shader_settings_to_load_path, config.annotation_csv_file_path, config.trace_file_path
        )

    def create_project_from_first_image(self, first_img_image, proj_file_location):
        # create project in specified path
        project = pyglass.CreateProject(pyglass.path(proj_file_location), self.project_name)

        # import image data into project    
        # Create DirectoryDescriptor to search folder for TIFFs, find first image of set, and create file list
        dd = pyglass.DirectoryDescription()
        dd.InspectByReferenceFile(first_img_image)

        # create a DataProvider to the file list
        dataProvider = pyglass.OpenTIFFs(dd.GetFileList(), False)
        # indicate which channels to include (in this case all channels from the file)
        includedChannels = pyglass.IntList(range(dataProvider.GetChannelsCount()))
        dataProvider.SetIncludedChannels(includedChannels)

        # spawn a ConversionDriver to convert the data
        cd = pyglass.ConversionDriver()
        cd.SetInput(dataProvider)
        cd.SetOutput(project)
        cd.StartAsynchronous()

        with tqdm(total=100, desc=f"Adding image layer to syGlass project: ") as pbar:
            while cd.GetPercentage() < 100:
                time.sleep(0.1)
                pbar.update(cd.GetPercentage() - pbar.n)

    def set_voxel_dimensions(self, proj_file_location):
        proj_file_path = os.path.join(proj_file_location, self.project_name, f'{self.project_name}.syg')
        project = sy.get_project(proj_file_path)

        img_vol = CloudVolume(self.img_uri, mip=self.img_res, fill_missing=True, progress=False, use_https=True)
        img_res = np.array(img_vol.resolution)
        # reverse it to [Z, Y, X] to match syGlass
        img_res = img_res[::-1] 
        
        project.set_voxel_dimensions(img_res, dtype=float)
    
    def create_base_project(self, first_img_image):
        proj_file_location = r'{}'.format(self.output_path)
        self.create_project_from_first_image(first_img_image, proj_file_location)
        self.set_voxel_dimensions(proj_file_location)
        project_file_location = os.path.join(proj_file_location, self.project_name)
        return project_file_location
    
    def add_mask_layer(self, proj_file_location, first_seg_image):
        # Create DirectoryDescriptor to search folder for TIFFs, find first image of set, and create file list
        dd = pyglass.DirectoryDescription()
        project = pyglass.CreateProject(pyglass.path(proj_file_location), f'{self.project_name}.syk', True)
        dd.InspectByReferenceFile(first_seg_image)
        
        # create a DataProvider to the dataProvider the file list
        dataProvider = pyglass.OpenTIFFs(dd.GetFileList(), False)
        # indicate which channels to include; in this case, all channels from the file
        includedChannels = pyglass.IntList(range(dataProvider.GetChannelsCount()))
        dataProvider.SetIncludedChannels(includedChannels)
        
        # spawn a ConversionDriver to convert the data
        cd = pyglass.ConversionDriver(True)
        cd.SetInput(dataProvider)
        cd.SetOutput(project)
        cd.StartAsynchronous()

        with tqdm(total=100, desc=f"Adding mask layer to syGlass project: ") as pbar:
            while cd.GetPercentage() < 100:
                time.sleep(0.1)
            pbar.update(cd.GetPercentage() - pbar.n)

        return proj_file_location
        
    def add_mesh_objs(self, proj_file_location, mesh_file_location):
        print("Adding mesh objects to syGlass project...")
        proj_file_path = os.path.join(proj_file_location, f'{self.project_name}.syg')
        project = sy.get_project(proj_file_path)
        obj_list = os.path.join(mesh_file_location, '*.obj')
        meshes = glob.glob(obj_list)
        project.import_meshes(meshes, "default")
        print("All mesh objects added to syGlass project.")
