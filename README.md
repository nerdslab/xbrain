# xbrain-bigdata
This repository contains methods for _segmenting large 3D brain image volumes_. You can find further details about how we apply the methods in this repo to segment mm-scale brain volumes in the following paper:

__Dyer, Eva L., et al. "Quantifying mesoscale neuroanatomy using X-ray microtomography." eNeuro, [eneuro.org/content/4/5/ENEURO.0195-17.2017](http://www.eneuro.org/content/4/5/ENEURO.0195-17.2017) (2017).__

If you use any of the code or datasets in this repo, please cite this paper. 
Please direct any questions to Eva Dyer at evadyer{at}gatech{dot}edu.

----------------------------------------------------

## Workflow Architecture

- **Creating Sub-Volumes for Automated Segmentation**
The input to this workflow is a stack of grayscale TIFFs. The first step is to create an HDF5 file with a dataset configured to correspond the entire 3D volume. The 3D volume/dataset then is divided into several overlapping subarrays to be pixel classified by the next step. Each subarray is saved into an HDF5 file. 

- **Automated Segmentation with Parallelized Ilastik**
In this step, Ilastik pixel classification process is run on each subarray. Input to each Ilastik classifier process is the trained data file and a subarray/sub-volume file from previous step. Ilastik classifier creates K probability maps and K is the number of annotated voxel classes/types in the trained data file. Then each pixel in the probability map is assigned to the class with the highest probability value. Output from this step is an HDF5 file with K subarray/sub-volume datasets for each input subarray file. This step should be run on a set of networked servers to speed up the processing.

- **Merging of overlapping sub-volumes**
In this step, the K subarrays in sub-volume files are combined to create K arrays for the volume. 

----------------------------------------------------
## How to Run the Pipeline to Segment a Large Dataset

### Step 0. Train a pixel classifier in Ilastik
Before running the pipeline, you must first train a Pixel Classifier in Ilastik ([ilastik.org](http://www.ilastik.org)) to find the objects that you are interested in segmenting. Please check out their [tutorial](http://ilastik.org/documentation/pixelclassification/pixelclassification) on how to train a classifier with ilastik. Once you are done training the classifier, make note of the path to your .ilp file, you will need it later.


### Step 1. Configuring python environments to run this workflow
To create sub-volumes for segmentation, run ilastik, and combine segmented sub-volumes into a whole volume file you will need to create the following conda environment (example below will create an environment called "ilastik-devel"). Python modules installed into this environment include h5py, skimage, mpi4py, glob, multiprocessing and psutil.

```
conda create -n ilastik-devel -c ilastik ilastik-everything-no-solvers

conda install -n ilastik-devel  -c conda-forge ipython

conda install -n ilastik-devel -c conda-forge  mpi4py

source activate ilastik-devel
```

Note: If you have problems running the pipeline using this environment, you can also try to add a different build of mpi4py. Try to use this build instead >> conda install -n ilastik-devel -c intel  mpi4py

### Step 2. Running the pipeline

(1) *Edit the file “seg_user_param.py” to specify the input parameters*

The user should specify the following info:
- The sub-volume dimensions: il_sub_vol_x (number of slices), il_sub_vol_y (columns) and il_sub_vol_z (rows)
- tiff_files_location - the full path to the directory containing TIFF image files
- classifier - the full path to the directory containing the Ilastik trained data file
- Number of threads to be used by an Ilastik classifier python process
- Percentage of available memory in a server to be used by an Ilastik classifier python process
- save_cell_prob_map - 'yes' if you want to save cell probability map, 'no' otherwise
- save_vessel_prob_map - 'yes' if you want to save vessel probability map, 'no' otherwise
- binary_output - 'yes' if you want to save a binary segmented output, 'no' otherwise

(2) *Activate Python environment*
```
source activate ilastik-devel
```

(3) *Segment data*
```
python tiff_to_hdf5_mpi.py
python make_subvolume_mpi.py
python segment_subvols_pixels.py
python combine_segmented_subvols.py
```

----------------------------------------------------

### Contributors:
- Mehdi Tondravi, Advanced Photon Source, Argonne National Laboratory
- Eva Dyer, Georgia Institute of Technology ([Lab Website](http://dyerlab.gatech.edu))

