#!/usr/bin/env python
'''
This module applies: binary_fill_holes(), morphology.label() and remove_small_objects() to the
segmented sub-volumes files. Then combines the sub-volumes datasets into a new volume file.
'''

import os.path
import numpy as np
import h5py
from scipy import ndimage as ndi
from skimage import morphology
from glob import glob
from mpi4py import MPI
import time
from segmentation_param import *
import pdb

# cell segmentation post processing
def cell_seg_post_proc():
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    size = MPI.COMM_WORLD.Get_size()
    name = MPI.Get_processor_name()
    start_time = int(time.time())
    # Get the list of all segmented sub-volume files.
    input_files = sorted(glob(outimage_file_location + '/*subvol*.h5'))
    if not input_files:
        print("*** Did not find any sub-volume segmented file in location %s ***" % outimage_file_location)
        return
    
    # Get the "Cell" label index
    cell_label_defined, cell_label_idx = save_prob_map('CELL')
    if cell_label_defined == False:
        print("Cell class is not labeled in the Ilastik training data file, no processing will take place")
        return
    # Shape/Dimension of the volume image is available in the last sub-volume file.
    volume_ds_shape = np.zeros((3,), dtype='uint64')
    # Last file has the dimensions for the volume.
    f = h5py.File(input_files[-1], 'r')
    volshape = f['orig_indices']
    volume_ds_shape[0] = volshape[1]
    volume_ds_shape[1] = volshape[3]
    volume_ds_shape[2] = volshape[5]
    f.close()
    # Get the list of segmented datasets
    # seg_ds_list = f.keys()
    labeld_obj = get_ilastik_labels()
    ds_name = labeld_obj[cell_label_idx]
    # Create an hdf file to contain the post segmentation cell volume image.
    par, name = os.path.split(post_seg_volume_location)
    seg_volume_file = post_seg_volume_location + '/volume_cell_' + name + '.h5'
    if rank == 0:
        print("Post segmentation directory is %s, number of file is %d and number of python processes is %d" % 
              (post_seg_volume_location, len(input_files), size))
        print("Volume shape is", volume_ds_shape)
    # Create directory for the post segmentation processing if it does not exist.
    if rank == 0:
        if not os.path.exists(post_seg_volume_location):
            os.mkdir(post_seg_volume_location)
            print("File directory for post segmentation did not exist, was created")
    comm.Barrier()
    
    # Need Parallel HDF for faster processing. However the below test lets processing to continue even if
    # Parallel HDF is not available.
    if size == 1:
        vol_img_file = h5py.File(seg_volume_file, 'w')
    else:
        vol_img_file = h5py.File(seg_volume_file, 'w', driver='mpio', comm=comm)
    
    if rank == 0:
        print("Dataset name to apply post processing is %s" % ds_name)
    vol_seg_dataset = vol_img_file.create_dataset(ds_name, volume_ds_shape, dtype='uint32',
                                                  chunks=(1, il_sub_vol_y, il_sub_vol_z))
    iterations = int(len(input_files) / size) + (len(input_files) % size > 0)
    for idx in range(iterations):
        if (rank + (size * idx)) >= len(input_files):
            print("\nBREAKING out, my rank is %d, number of files is %d, size is %d and idx is %d" % 
                  (rank, len(input_files), size, idx))
            break
        print("*** Working on file %s and rank is %d ***" % (input_files[rank + size * idx], rank))
        subvol_file = h5py.File(input_files[rank + size * idx], 'r')
        # Retrieve indices into the whole volume.
        orig_idx_ds = subvol_file['orig_indices']
        orig_idx = orig_idx_ds[...]
        
        # Retrieve overlap size to the right and left side of the sub-volume.
        right_overlapds = subvol_file['right_overlap']
        rightoverlap = right_overlapds[...]
        left_overlapds = subvol_file['left_overlap']
        leftoverlap = left_overlapds[...]
        
        myds = subvol_file[ds_name]
        subvoldata = myds[...]
        x_dim = subvoldata.shape[0]
        y_dim = subvoldata.shape[1]
        z_dim = subvoldata.shape[2]
        subvoldata = subvoldata > 0
        subvoldata = ndi.binary_fill_holes(subvoldata)
        subvoldata = morphology.remove_small_objects(subvoldata, MINSZ_CELL, connectivity=2)
        subvoldata = morphology.label(subvoldata.astype('uint32'))
        
        vol_seg_dataset[orig_idx[0]:orig_idx[1], orig_idx[2]:orig_idx[3], orig_idx[4]:orig_idx[5]] = \
            subvoldata[leftoverlap[0] : x_dim - rightoverlap[0],
                       leftoverlap[1] : y_dim - rightoverlap[1],
                       leftoverlap[2] : z_dim - rightoverlap[2]]
        subvol_file.close()
    vol_img_file.close()
    print("Time to execute cell_seg_post_proc() is %d seconds and rank is %d" % ((time.time() - start_time), rank))

if __name__ == '__main__':
    cell_seg_post_proc()
