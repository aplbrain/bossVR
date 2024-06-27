import numpy as np
from intern import array
import matplotlib.pyplot as plt
import os
import sys
from PIL import Image
from tqdm import tqdm

def get_indices(dim_name, coord_dims):
    while True:
        format_error = True 
        dim_size = coord_dims.get(dim_name)
        try:
            indices = input(f"Please enter the {dim_name} indices in the range to download over, in the format start:stop ")
            start, stop = map(int, indices.split(":"))
            format_error = False  # Set format_error to False if the conversion is successful
            
            if start < 0 or stop < 0 or stop > dim_size or start >= stop:
                raise ValueError(f"Invalid {dim_name} indices: {start}:{stop}. Must be within range (0:{dim_size}) and start < stop")

            return start, stop
            
        except ValueError as e:
            if format_error:
                print("Error: invalid literal for int() with base 10. Must be in the format start:stop")
            else:
                print(f"Error: {e}.")

def get_file_location():
    while True:
        file_location = input("Please enter the directory where the images should be saved: ")
        if not os.path.exists(file_location):
            try:
                os.makedirs(file_location)
                print(f"Directory {file_location} created.")
                break
            except OSError as e:
                print(f"Error creating directory: {e}")
        elif os.path.isdir(file_location):
            break
        else:
            print(f"{file_location} is not a valid directory. Please try again.")
    return file_location

def save_slices_as_tiff(dataset, file_location, z_start, collection, experiment, channel):
    z_dim = dataset.shape[0]
    start = z_start
    for i in range(z_dim):
        start += 1
        slice_image = dataset[i, :, :]
        img = Image.fromarray(slice_image)
        img.save(os.path.join(file_location, f'{collection.lower()}_{experiment.lower()}_{channel.lower()}_{z_start + i:03d}.tiff'))
    print(str(z_dim) + " images have been saved to the specified directory.")

def main():
    # Ask user for collection, experiment, channel name
    collection = input("Please enter the collection name: ")
    experiment = input("Please enter the experiment name: ")
    channel = input("Please enter the channel name: ")

    # Get BossDB URL
    url = "bossdb://" + collection + "/" + experiment + "/" + channel
    print("BossDB URL: " + url)

    # Ask user for desired resolution
    while True:
        try:
            res = int(input("Please enter the desired resolution level: "))
            break  # Exit the loop if conversion is successful
        except ValueError:
            print("Invalid input. Please enter an integer value.")

    #  Convert to full dataset with specified resolution   
    bossdb_dataset = array(url, resolution=res)

    # Extract dimensions
    z_dim, y_dim, x_dim = bossdb_dataset.shape
    coord_dims = {'X': x_dim, 'Y': y_dim, 'Z': z_dim}
    print(f"This dataset is {x_dim} voxels in the X dimension, {y_dim} voxels in the Y dimension, and {z_dim} voxels in the Z dimension.")

    # Get user input for each dimension
    x_start, x_stop = get_indices("X", coord_dims)
    y_start, y_stop = get_indices("Y", coord_dims)
    z_start, z_stop = get_indices("Z", coord_dims)

    print(f"Selected ranges - X: {x_start}:{x_stop}, Y: {y_start}:{y_stop}, Z: {z_start}:{z_stop}")

    # View the data
    cutout = bossdb_dataset[z_start:z_stop, y_start:y_stop, x_start:x_stop]

    # Convert to TIFF and save in specified directory
    file_location = get_file_location()
    save_slices_as_tiff(cutout, file_location, z_start, collection, experiment, channel)

if __name__ == '__main__':
    main()