import argparse
import os
from PIL import Image
import requests

# Intern imports
from intern import array

# Cloud imports
from cloudvolume import CloudVolume

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

def save_slices_as_tiff(dataset, path, file_location, z_start, is_cloud=False):
    if is_cloud:
        z_dim = dataset.shape[2]
        for i in range(z_dim):
            slice_image = dataset[:, :, i][:, :, 0]
            img = Image.fromarray(slice_image)
            img.save(os.path.join(file_location, f'{path}_{z_start + 1 + i:03d}.tiff'))
    else:
        z_dim = dataset.shape[0]
        for i in range(z_dim):
            slice_image = dataset[i, :, :]
            img = Image.fromarray(slice_image)
            img.save(os.path.join(file_location, f'{path}_{z_start + 1 + i:03d}.tiff'))
    
    print(f"{z_dim} images have been saved to the specified directory.")

def intern_info(url, resolution, file_path):
    try:
        bossdb_dataset = array(url, resolution=resolution)
        z_dim, y_dim, x_dim = bossdb_dataset.shape
        print(f"This dataset is {x_dim} voxels in the X dimension, {y_dim} voxels in the Y dimension, and {z_dim} voxels in the Z dimension in resolution {resolution}")
        if (file_path is None):
            print("Input file path and optionally required resolution and dimensions to download images. ")
    except requests.exceptions.HTTPError as e:
        print(f"Error: {e.response.json().get('message')}")
        return

def cloud_info(url, resolution, file_path):
    vol = CloudVolume(url, mip=resolution, use_https=True)
    avail_res = list(vol.available_mips)
    
    if resolution not in avail_res:
        raise ValueError(f"Specified resolution {resolution} is not available. Available resolutions are: {avail_res}")
    
    bounds = vol.bounds
    x_bounds = (bounds.minpt[0], bounds.maxpt[0])
    y_bounds = (bounds.minpt[1], bounds.maxpt[1])
    z_bounds = (bounds.minpt[2], bounds.maxpt[2])

    try:
        print(f"This dataset has dimensions X: {x_bounds}, Y: {y_bounds}, Z: {z_bounds} at resolution {resolution}")
        print(f"Available mipmap levels: {avail_res}")
        if (file_path is None):
            print("Input file path and optionally required resolution and dimensions to download images. ")
    except requests.exceptions.HTTPError as e:
        print(f"Error: {e.response.json().get('message')}")
        return

def intern_convert(url, path, resolution, x, y, z, file_path):
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

        print(f"Downloading cutout data over ranges X: {x_start}:{x_stop}, Y: {y_start}:{y_stop}, Z: {z_start}:{z_stop}...")
        cutout = bossdb_dataset[z_start:z_stop, y_start:y_stop, x_start:x_stop]
        print("Download complete.")

        if not os.path.exists(file_path):
            os.makedirs(file_path)
            print(f"Directory {file_path} created.")

        save_slices_as_tiff(cutout, path, file_path, z_start)

    except requests.exceptions.HTTPError as e:
        print(f"Error: {e.response.json().get('message')}")
    except ValueError as e:
        print(f"Error: {e}")

def cloud_convert(url, path, resolution, x, y, z, file_path):
    try:
        vol = CloudVolume(url, mip=resolution, use_https=True)
        bounds = vol.bounds
        x_bounds = (bounds.minpt[0], bounds.maxpt[0])
        y_bounds = (bounds.minpt[1], bounds.maxpt[1])
        z_bounds = (bounds.minpt[2], bounds.maxpt[2])
        coord_dims = {'X': x_bounds, 'Y': y_bounds, 'Z': z_bounds}

        if (x is None):
            x_start, x_stop = x_bounds
        else:
            x_start, x_stop = get_indices("X", coord_dims, x, is_cloud=True)
        
        if (y is None):
            y_start, y_stop = y_bounds
        else:
            y_start, y_stop = get_indices("Y", coord_dims, y, is_cloud = True)

        if (z is None):
            z_start, z_stop = z_bounds
        else:
            z_start, z_stop = get_indices("Z", coord_dims, z, is_cloud = True)

        print(f"Downloading over ranges X: {x_start}:{x_stop}, Y: {y_start}:{y_stop}, Z: {z_start}:{z_stop}...")
        cutout = vol[x_start:x_stop, y_start:y_stop, z_start:z_stop]
        print("Download complete.")

        if not os.path.exists(file_path):
            os.makedirs(file_path)
            print(f"Directory {file_path} created.")

        save_slices_as_tiff(cutout, path, file_path, z_start, is_cloud=True)

    except requests.exceptions.HTTPError as e:
        print(f"Error: {e.response.json().get('message')}")
    except ValueError as e:
        print(f"Error: {e}")

def parse_url(url):
    parts = url.split("/")
    if len(parts) < 2:
        raise ValueError("Invalid format. Please enter dataset information as Collection/Experiment/Channel.")

def main():
    parser = argparse.ArgumentParser(description="BossDB Image Conversion Script")
    parser.add_argument("-m", "--mode", required=True, choices=["intern", "cloud"], help="Mode of implementation (intern or cloud)")
    parser.add_argument("-u", "--url", required=True, nargs='+', help="BossDB or CloudVolume path")    
    parser.add_argument("-r", "--resolution", type=int, default=0, help="Desired resolution level")
    parser.add_argument("-x", "--x_dimensions", help="Range for x in the format x_start:x_stop")
    parser.add_argument("-y", "--y_dimensions", help="Range for y in the format y_start:y_stop")
    parser.add_argument("-z", "--z_dimensions", help="Range for z in the format z_start:z_stop")
    parser.add_argument("-f", "--file_path", help="Directory where the TIFF files should be saved")

    args = parser.parse_args()
    args.url = ''.join(args.url)

    try:
        parse_url(args.url)
        url = f"bossdb://{args.url}" if args.mode == "intern" else f"s3://bossdb-open-data/{args.url}"

        if args.mode == "intern":
            intern_info(url, args.resolution, args.file_path)
        else:
            cloud_info(url, args.resolution, args.file_path)

        if args.file_path is not None:
            if args.mode == "intern":
                intern_convert(url, args.url.replace("/", "_"), args.resolution, args.x_dimensions, args.y_dimensions, args.z_dimensions, args.file_path)
            else:
                cloud_convert(url, args.url.replace("/", "_"), args.resolution, args.x_dimensions, args.y_dimensions, args.z_dimensions, args.file_path)
    
    except ValueError as e:
        print(f"Error: {str(e)}")

if __name__ == '__main__':
    main()
