#Workflow for segmentation of Terabyte sized 3D Datasets


## Workflow Description
--------------------
3D imaging of brain at single-neuron resolution generates Terabyte sized datasets. In follow-on analysis, it is essential to go beyond a 3D density image to segment out features of interest (such as blood vessels, cells, and axons in the example of brains).

Scripts in this folder contains a parallel processing workflow for segmenting large/Terabyte sized datasets based on Ilastik Pixel Classification Workflow.

## Workflow Architecture
---------------------
**This workflow consists of the following processing steps:**

**\1. Creating Sub-Volumes for Automated Segmentation**

The input to this workflow is TIFF file stack in grayscale. The first step is to create an HDF5 file with a dataset configured to correspond the entire 3D volume. The 3D volume/dataset then is divided into several overlapping subarrays to be pixel classified by the next step. Each subarray is saved into an HDF5 file. 
This step should be run on a set of networked servers to speed up the processing.

**\2. Automated Segmentation with Parallelized Ilastik**

In this step, Ilastik pixel classification process is run on each subarray. Input to each Ilastik classifier process is the trained data file and a subarray/sub-volume file from previous step. Ilastik classifier creates K probability maps and K is the number of annotated voxel classes/types in the trained data file. Then each pixel in the probability map is assigned to the class with the highest probability value. Output from this step is an HDF5 file with K subarray/sub-volume datasets for each input subarray file.
This step should be run on a set of networked servers to speed up the processing.

**\3. Merging of overlapping sub-volumes**

In this step, the K subarrays in sub-volume files are combined to create K arrays for the volume. 
This step should be run on a set of networked servers to speed up the processing.


## Step 1. Configuring python environments to run this workflow
----------------------------------------------------

To read and write into a common HDF5 file need hdf5 package compiled in “parallel” mode. Ilastik is not built with this option and will be too much effort to build it for parallel HDF5. So, should create the following two python environments and take advantage of the pre-built required Ilastik packages.

**\1. Python Environment for making and combining sub-volumes**

This environment should be used when creating sub-volumes for segmentation, and when combining segmented sub-volumes into a whole volume file. Python modules installed into this environment in addition to parallel HDF5 should include h5py, skimage, mpi4py, glob, multiprocessing and psutil.

**\2. Python Environment for Automated Segmentation with Ilastik**

This environment is needed to segment the sub-volume files. Below is a suggestion on how to make this environment assuming the new python environment name is "lastik-devel" :

conda create -n ilastik-devel -c ilastik ilastik-everything-no-solvers

conda install -n ilastik-devel  -c conda-forge ipython

conda install -n ilastik-devel -c conda-forge  mpi4py

source activate ilastik-devel


## Running the Pipeline

# Edit file “seg_user_param.py” to specify the sub-volume dimensions (Z, Y & X pixels), the input TIFF stack directory and the Ilastik trained file location.

# Activate python environment

*\1. source activate Ilastik-devel*

# Convert TIFF stack into a 3D volume array - **must use one python processe.**

*\2. mpirun –np 1 python tiff_to_hdf5_mpi.py*

# Create sub-volume files - **must use one python processe.**

*\3. mpirun –np 1 python make_subvolume_mpi.py*

# Segment sub-volume files created in previous step assuming 12 python processes on 12 servers.

*\4. mpirun -f $HOSTLIST –np 12 python segment_subvols_pixels.py*

# combine sub-volumes into volume - **must use one python processe.**

*\5. mpirun –np 4 python combine_segmented_subvols.py*

# xbrain-bigdata
python code for running xbrain on large datasets
