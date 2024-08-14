from cloudvolume import CloudVolume
import os
from PIL import Image
import numpy as np
from tqdm import tqdm

def save_slices_as_tiff(dataset, path, file_location, offset, data_type=""):
    if np.iinfo(dataset.dtype).max > np.iinfo(np.uint16).max:
        dataset = dataset.astype(np.uint16)
    
    first_image = ""
    
    img_file_location = os.path.join(file_location, data_type, dataset) if data_type=="block" else os.path.join(file_location, data_type)
    
    os.makedirs(img_file_location, exist_ok=True)
    z_dim = dataset.shape[0] if data_type=='block'else dataset.shape[2]
    z_start = offset
   
    for i in tqdm(range(z_dim), desc=f"Saving {data_type} slices"):
        slice_image = dataset[i, :, :, 0] if data_type=='block'else dataset[:, :, i][:, :, 0]
        img = Image.fromarray(slice_image)

        # Rotate and flip the image
        rotate_img = img.transpose(Image.ROTATE_270)
        img = rotate_img.transpose(Image.FLIP_LEFT_RIGHT)

        if i == 0:
            first_image = os.path.join(img_file_location, f'{path}_{z_start + 1:03d}.tiff')
            img.save(first_image)
        else:
            img.save(os.path.join(img_file_location, f'{path}_{z_start + 1 + i:03d}.tiff'))

    print(f"{z_dim} {data_type} slices have been saved to {img_file_location}")
    return first_image

def get_pair_indices(index, dim, vol, indices):
    bounds = vol.bounds.minpt[index], vol.bounds.maxpt[index]
    start, stop = map(int, indices.split(":"))

    if indices=='':
        start, stop = bounds

    size = bounds[1] - bounds[0]

    if stop > size or start >= stop:
        raise ValueError(f"Invalid {dim} indices: {start}:{stop}. Must be within range ({bounds[0]}:{bounds[1]}) and start < stop")
    else:
        return start, stop
    
def get_indices(vol, x_indices, y_indices, z_indices):
    x_start, x_stop = get_pair_indices(0, "X", vol, x_indices)
    y_start, y_stop = get_pair_indices(1, "Y", vol, y_indices)
    z_start, z_stop = get_pair_indices(2, "Z", vol, z_indices)
    return x_start, x_stop, y_start, y_stop, z_start, z_stop

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
        raise ValueError(f'WARNING: Image and segmentation data is not at the same resolution. Please downsample {larger} data with resolution mip={int(new_mip - 1)}')

def flip_images_in_directory(img_stack_dir):
    # Iterate over all files in the input directory
    for filename in os.listdir(img_stack_dir):
        if filename.endswith('.tiff') or filename.endswith('.tif'):
            # Construct full file path
            file_path = os.path.join(img_stack_dir, filename)
            # Open an image file
            with Image.open(file_path) as img:
                # Rotate 90 degrees
                rotate_img = img.transpose(Image.ROTATE_270)
                # Flip the image on the Y axis
                flipped_img = rotate_img.transpose(Image.FLIP_LEFT_RIGHT)
                # Save the transformed image to the same directory; replace image
                temp_path = os.path.join(img_stack_dir, "temp_" + filename)
                flipped_img.save(temp_path)
                # Rename the temporary file to the original file name
                os.replace(temp_path, file_path)

def transform_annotation_points(vertex, img_resolution, x, y, z):
    transformed_vertex = [vertex[0] + x * img_resolution[0], vertex[1] + y * img_resolution[1], vertex[2] + z * img_resolution[2]]
    return transformed_vertex