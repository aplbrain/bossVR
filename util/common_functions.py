from cloudvolume import CloudVolume
import os
from PIL import Image

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