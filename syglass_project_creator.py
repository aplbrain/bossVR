import configparser
import os
from PIL import Image
import requests
from tqdm import tqdm
from intern import array
from cloudvolume import CloudVolume
import pandas as pd
import numpy as np
from syglass import pyglass
import os
import time

def get_indices(dim_name, coord_dims, indices, is_cloud=False):
    start, stop = map(int, indices.split(":"))
    if is_cloud:
        dim_size = (coord_dims.get(dim_name))[1]
    else:
        dim_size = coord_dims.get(dim_name)
    
    if stop > dim_size or start >= stop:
        raise ValueError(f"Invalid {dim_name} indices: {start}:{stop}. Must be within range (0:{dim_size}) and start < stop")
    else:
        return start, stop

def create_project(file_location, first_image_img, first_image_seg, project_name):
    # create project in specified path
    proj_file_location = r'{}'.format(file_location)
    project = pyglass.CreateProject(pyglass.path(proj_file_location), project_name)

    # import image data into project    
    # Create DirectoryDescriptor to search folder for TIFFs, find first image of set, and create file list
    dd = pyglass.DirectoryDescription()
    dd.InspectByReferenceFile(first_image_img)

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

    with tqdm(total=100, desc=f"Adding image layer to SyGlass project: ") as pbar:
        while cd.GetPercentage() < 100:
            time.sleep(0.1)
            pbar.update(cd.GetPercentage() - pbar.n)

    # Import segmentation data into project
    if first_image_seg != "":
        # mask data is stored with .syk extension in existing project
        project = pyglass.CreateProject(pyglass.path(proj_file_location), r'{project_name}.syk', True)

        # Import image data into project    
        # Create DirectoryDescriptor to search folder for TIFFs, find first image of set, and create file list
        dd = pyglass.DirectoryDescription()
        dd.InspectByReferenceFile(first_image_seg)
        
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

        with tqdm(total=100, desc=f"Adding mask layer to SyGlass project: ") as pbar:
            while cd.GetPercentage() < 100:
                time.sleep(0.1)
            pbar.update(cd.GetPercentage() - pbar.n)


def save_slices_as_tiff(dataset, path, file_location, z_start, data_type, is_cloud=True):
    if np.iinfo(dataset.dtype).max > np.iinfo(np.uint16).max:
        dataset = dataset.astype(np.uint16)

    first_image_img = ""
    first_image_seg = ""

    if data_type == "segmentation":
        img_file_location = os.path.join(file_location, 'seg')
        os.makedirs(img_file_location, exist_ok=True)
        if is_cloud:
            z_dim = dataset.shape[2]
            for i in tqdm(range(z_dim), desc=f"Saving {data_type} slices (CloudVolume)"):
                slice_image = dataset[:, :, i][:, :, 0]
                img = Image.fromarray(slice_image)
                if (i == 0):
                    first_image_seg = os.path.join(img_file_location, f'{path}_{z_start + 1:03d}.tiff')
                    img.save(first_image_seg)
                else:
                    img.save(os.path.join(img_file_location, f'{path}_{z_start + 1 + i:03d}.tiff'))
        else:
            z_dim = dataset.shape[0]
            for i in tqdm(range(z_dim), desc=f"Saving {data_type} image slices (Intern)"):
                slice_image = dataset[i, :, :]
                img = Image.fromarray(slice_image)
                if (i == 0):
                    first_image_seg = os.path.join(img_file_location, f'{path}_{z_start + 1:03d}.tiff')
                    img.save(first_image_seg)
                else:
                    img.save(os.path.join(img_file_location, f'{path}_{z_start + 1 + i:03d}.tiff'))
        print(f"{z_dim} {data_type} slices have been saved to {img_file_location}")
    
    else:
        img_file_location = os.path.join(file_location, 'img')
        os.makedirs(img_file_location, exist_ok=True)
        if is_cloud:
            z_dim = dataset.shape[2]
            for i in tqdm(range(z_dim), desc=f"Saving image slices (CloudVolume)"):
                slice_image = dataset[:, :, i][:, :, 0]
                img = Image.fromarray(slice_image)
                if (i == 0):
                    first_image_img = os.path.join(img_file_location, f'{path}_{z_start + 1:03d}.tiff')
                    img.save(first_image_img)
                else:
                    img.save(os.path.join(img_file_location, f'{path}_{z_start + 1 + i:03d}.tiff'))
        else:
            z_dim = dataset.shape[0]
            for i in tqdm(range(z_dim), desc=f"Saving image slices (Intern)"):
                slice_image = dataset[i, :, :]
                img = Image.fromarray(slice_image)
                if (i == 0):
                    first_image_img = os.path.join(img_file_location, f'{path}_{z_start + 1:03d}.tiff')
                    img.save(first_image_img)
                else:
                    img.save(os.path.join(img_file_location, f'{path}_{z_start + 1 + i:03d}.tiff'))
        print(f"{z_dim} image slices have been saved to {img_file_location}")

    return first_image_img, first_image_seg


def intern_info(url, resolution, data_type='image'):    
    try:
        # First download base resolution to get all available res and check if input res is available
        bossdb_dataset = array(url)
        avail_res = bossdb_dataset.available_resolutions
        if resolution is not None and resolution not in avail_res:
            raise ValueError(f"Specified resolution {resolution} is not available. Available resolutions are: {avail_res}")

        # Display dimensions for all available resolutions
        res_dims = []
        for res in avail_res:
            arr_res = array(url, resolution=res)
            z_dim, y_dim, x_dim = arr_res.shape
            res_dims.append([res, x_dim, y_dim, z_dim])

        df = pd.DataFrame(res_dims, columns=["Resolution", "X (voxels)", "Y (voxels)", "Z (voxels)"])
        print(df.to_string(index=False))
        # Display dimensions for requested resolution
        req_dims = df[df["Resolution"] == resolution]
        print(f"Requested {data_type} resolution {resolution} has dimensions X: {req_dims['X (voxels)'].values[0]}, Y: {req_dims['Y (voxels)'].values[0]}, Z: {req_dims['Z (voxels)'].values[0]} voxels")

    except requests.exceptions.HTTPError as e:
        print(f"Error: {e.response.json().get('message')}")
        return

def cloud_info(url, resolution, data_type='image'):    
    try:
        # First download base resolution to get all available res and check if input res is available
        vol = CloudVolume(url, fill_missing=True, use_https=True)
        avail_res = list(vol.available_mips)
        if resolution is not None and resolution not in avail_res:
            raise ValueError(f"Specified resolution {resolution} is not available. Available resolutions are: {avail_res}")

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
        req_dims = df[df["Resolution"] == resolution]
        print(f"Requested {data_type} resolution {resolution} has dimensions X: {req_dims['X (voxels)'].values[0]}, Y: {req_dims['Y (voxels)'].values[0]}, Z: {req_dims['Z (voxels)'].values[0]} voxels")

    except requests.exceptions.HTTPError as e:
        print(f"Error: {e.response.json().get('message')}")
        return

def intern_convert(url, path, resolution, x, y, z, output_path, data_type='image'):
    try:
        bossdb_dataset = array(url, resolution=resolution)
        z_dim, y_dim, x_dim = bossdb_dataset.shape
        coord_dims = {'X': x_dim, 'Y': y_dim, 'Z': z_dim}

        if (x is None):
            x_start = 0
            x_stop = x_dim
        else:
            x_start, x_stop = get_indices("X", coord_dims, x)
        
        if (y is None):
            y_start = 0
            y_stop = y_dim
        else:
            y_start, y_stop = get_indices("Y", coord_dims, y)

        if (z is None):
            z_start = 0
            z_stop = z_dim
        else:
            z_start, z_stop = get_indices("Z", coord_dims, z)

        print(f"Downloading {data_type} cutout data over ranges X: {x_start}:{x_stop}, Y: {y_start}:{y_stop}, Z: {z_start}:{z_stop}...")
        cutout = bossdb_dataset[z_start:z_stop, y_start:y_stop, x_start:x_stop]
        print("Download complete.")

        if not os.path.exists(output_path):
            os.makedirs(output_path)
            print(f"Directory {output_path} created.")

        first_image_img, first_image_seg = save_slices_as_tiff(cutout, path, output_path, z_start, data_type, False)
        return first_image_img, first_image_seg

    except requests.exceptions.HTTPError as e:
        print(f"Error: {e.response.json().get('message')}")
    except ValueError as e:
        print(f"Error: {e}")

def cloud_convert(url, path, resolution, x, y, z, output_path, data_type="image"):
    try:
        vol = CloudVolume(url, mip=resolution, fill_missing=True, use_https=True)
        bounds = vol.bounds
        x_bounds = (bounds.minpt[0], bounds.maxpt[0])
        y_bounds = (bounds.minpt[1], bounds.maxpt[1])
        z_bounds = (bounds.minpt[2], bounds.maxpt[2])
        coord_dims = {'X': x_bounds, 'Y': y_bounds, 'Z': z_bounds}

        if (x==''):
            x_start, x_stop = x_bounds
        else:
            x_start, x_stop = get_indices("X", coord_dims, x, is_cloud=True)
        
        if (y==''):
            y_start, y_stop = y_bounds
        else:
            y_start, y_stop = get_indices("Y", coord_dims, y, is_cloud = True)

        if (z==''):
            z_start, z_stop = z_bounds
        else:
            z_start, z_stop = get_indices("Z", coord_dims, z, is_cloud = True)

        print(f"Downloading {data_type} cutout data over ranges X: {x_start}:{x_stop}, Y: {y_start}:{y_stop}, Z: {z_start}:{z_stop}...")
        cutout = vol[x_start:x_stop, y_start:y_stop, z_start:z_stop]
        print("Download complete.")

        if not os.path.exists(output_path):
            os.makedirs(output_path)
            print(f"Directory {output_path} created.")

        first_image_img, first_image_seg = save_slices_as_tiff(cutout, path, output_path, z_start, data_type)
        return first_image_img, first_image_seg

    except requests.exceptions.HTTPError as e:
        print(f"Error: {e.response.json().get('message')}")
    except ValueError as e:
        print(f"Error: {e}")

def parse_url(url):
    parts = url.split("/")
    if len(parts) < 2:
        raise ValueError("Invalid format. Please enter dataset information as Collection/Experiment/Channel or the appropriate CloudVolume Path.")
    
def check_res_cloud(img_uri, img_res, seg_uri, seg_res):
    img_vol = CloudVolume(img_uri, mip=img_res, fill_missing=True, use_https=True)
    seg_vol = CloudVolume(seg_uri, mip=seg_res, fill_missing=True, use_https=True)
    larger = "image"
    if not (img_vol.resolution[0] == seg_vol.resolution[0] and img_vol.resolution[1] == seg_vol.resolution[1] and img_vol.resolution[2] == seg_vol.resolution[2]):
        if img_vol.resolution[0] > seg_vol.resolution[0]:
            larger = "segmentation"
            new_mip = img_vol.resolution[0] / seg_vol.resolution[0]
        else:
            new_mip = seg_vol.resolution[0] / img_vol.resolution[0]
        raise ValueError(f'Image and segmentation data is not at the same resolution. Please downsample {larger} data with resolution mip={int(new_mip - 1)}')

# ineffective to put in use, as voxel_size doesn't update for downsampled dataset with intern
def check_res_intern(img_uri, img_res, seg_uri, seg_res):
    img_dataset = array(img_uri, resolution=img_res)
    seg_dataset = array(seg_uri, resolution=seg_res)

    print(img_dataset.voxel_size)
    print(seg_dataset.voxel_size)

    larger = "image"
    if not (img_dataset.voxel_size[2] == seg_dataset.voxel_size[2] and img_dataset.voxel_size[1] == seg_dataset.voxel_size[1] and img_dataset.voxel_size[0] == seg_dataset.voxel_size[0]):
        if img_dataset.voxel_size[2] > seg_dataset.voxel_size[2]:
            larger = "segmentation"
            new_mip = img_dataset.voxel_size[2] / seg_dataset.voxel_size[2]
        else:
            new_mip = seg_dataset.voxel_size[2] / img_dataset.voxel_size[2]
        raise ValueError(f'Image and segmentation data is not at the same resolution. Please downsample {larger} data with resolution={int(new_mip - 1)}')
    
def main():
    config = configparser.ConfigParser(allow_no_value=True)
    config.read('config.ini')
    mode = config['DEFAULT']['mode']
    
    img_data_uri = config['DEFAULT']['img_uri']
    img_res = int(config['DEFAULT']['img_res'])
    
    seg = config['DEFAULT']['seg']
    seg_data_uri = config['DEFAULT']['seg_uri']
    seg_res = int(config['DEFAULT']['seg_res'])
    
    method = config['DEFAULT']['method']
    x_dimensions = config['DEFAULT'].get('x_dimensions')
    y_dimensions = config['DEFAULT'].get('y_dimensions')
    z_dimensions = config['DEFAULT'].get('z_dimensions')
    output_path = config['DEFAULT']['output_path']

    add_mask = False
    if seg =='True':
        add_mask = True

    try:
        # Handle image
        parse_url(img_data_uri)
        if add_mask:
            parse_url(img_data_uri)

        img_uri = f"bossdb://{img_data_uri}" if method == "intern" else f"s3://bossdb-open-data/{img_data_uri}"
        seg_uri = f"bossdb://{seg_data_uri}" if method == "intern" else f"s3://bossdb-open-data/{seg_data_uri}"

        if mode == "info":
            print("Extracting image dimension information...")
            if method == "intern":
                intern_info(img_uri, img_res)
            else:
                cloud_info(img_uri, img_res)
            
            if (add_mask):
                parse_url(seg_uri)
                print("Extracting segmentation dimension information...")
                if method == "intern":
                    intern_info(seg_uri, seg_res, 'segmentation')
                else:
                    cloud_info(seg_uri, seg_res, 'segmentation')
        else:
            if output_path is None:
                raise ValueError("File path must be specified for images or project command")
            
            if add_mask:
                if method == "cloud":
                    check_res_cloud(img_uri, img_res, seg_uri, seg_res)
                # can check voxel size wth intern, but it does not differ for different resolutions (submitted as issue on Github)
                # else:
                #     check_res_intern(img_uri, img_res, seg_uri, seg_res)

            first_image_img = ""
            first_image_seg = ""
            if method == "intern":
                first_image_img = intern_convert(img_uri, img_data_uri.replace("/", "_"), img_res, x_dimensions, y_dimensions, z_dimensions, output_path)[0]
                if add_mask:
                    first_image_seg = intern_convert(seg_uri, seg_data_uri.replace("/", "_"), seg_res, x_dimensions, y_dimensions, z_dimensions, output_path, "segmentation")[1]
            else:
                first_image_img = cloud_convert(img_uri, img_data_uri.replace("/", "_"), img_res, x_dimensions, y_dimensions, z_dimensions, output_path)[0]
                if add_mask:
                    first_image_seg = cloud_convert(seg_uri, seg_data_uri.replace("/", "_"), seg_res, x_dimensions, y_dimensions, z_dimensions, output_path, "segmentation")[1]
                
            if mode == "project":
                project_name = "project"
                print("Saving SyGlass project...")
                create_project(output_path, first_image_img, first_image_seg, project_name)
                print(f"SyGlass project has been saved to {output_path}\\{project_name}")
    
    except ValueError as e:
        print(f"Error: {str(e)}")

if __name__ == '__main__':
    main()
