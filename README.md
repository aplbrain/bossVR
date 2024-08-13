# BossVR

This script allows you to interact with datasets from [BossDB](https://bossdb.org/projects) and create and modify syGlass projects. You can retrive information about the dataset, download images in TIFF format, download and transform meshes, create syGlass projects with image stacks, mask layers, and meshes, and upload and export annotations/  

## Requirements

All the required packages can be installed using the `requirements.txt` file:

```sh
pip install -r requirements.txt
```

Or with conda, you can setup a new environment with the `cloud_intern.yaml` file:

```sh
conda env create -f cloud_intern.yaml
```

This code supports usage of both `intern` and  `CloudVolume` for reading of BossDB data and access to more detailed dataset info. Follow [intern installation instructions](https://github.com/jhuapl-boss/intern)) and [CloudVolume installation instructions](https://github.com/seung-lab/cloud-volume?tab=readme-ov-file)) for more information.
