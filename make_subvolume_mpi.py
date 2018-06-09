#!/usr/bin/env python 

# #########################################################################
# Copyright (c) 2015, UChicago Argonne, LLC. All rights reserved.         #
#                                                                         #
# Copyright 2015. UChicago Argonne, LLC. This software was produced       #
# under U.S. Government contract DE-AC02-06CH11357 for Argonne National   #
# Laboratory (ANL), which is operated by UChicago Argonne, LLC for the    #
# U.S. Department of Energy. The U.S. Government has rights to use,       #
# reproduce, and distribute this software.  NEITHER THE GOVERNMENT NOR    #
# UChicago Argonne, LLC MAKES ANY WARRANTY, EXPRESS OR IMPLIED, OR        #
# ASSUMES ANY LIABILITY FOR THE USE OF THIS SOFTWARE.  If software is     #
# modified to produce derivative works, such modified software should     #
# be clearly marked, so as not to confuse it with the version available   #
# from ANL.                                                               #
#                                                                         #
# Additionally, redistribution and use in source and binary forms, with   #
# or without modification, are permitted provided that the following      #
# conditions are met:                                                     #
#                                                                         #
#     * Redistributions of source code must retain the above copyright    #
#       notice, this list of conditions and the following disclaimer.     #
#                                                                         #
#     * Redistributions in binary form must reproduce the above copyright #
#       notice, this list of conditions and the following disclaimer in   #
#       the documentation and/or other materials provided with the        #
#       distribution.                                                     #
#                                                                         #
#     * Neither the name of UChicago Argonne, LLC, Argonne National       #
#       Laboratory, ANL, the U.S. Government, nor the names of its        #
#       contributors may be used to endorse or promote products derived   #
#       from this software without specific prior written permission.     #
#                                                                         #
# THIS SOFTWARE IS PROVIDED BY UChicago Argonne, LLC AND CONTRIBUTORS     #
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT       #
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS       #
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL UChicago     #
# Argonne, LLC OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,        #
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,    #
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;        #
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER        #
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT      #
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN       #
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE         #
# POSSIBILITY OF SUCH DAMAGE.                                             #
# #########################################################################

'''
Module for dividing an image volume into sub-volumes.
'''

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import pdb
import numpy as np
import h5py
from mpi4py import MPI
import os.path
from glob import glob
import time
from segmentation_param import *

__author__ = "Mehdi Tondravi"
__copyright__ = "Copyright (c) 2017, UChicago Argonne, LLC."
__docformat__ = 'restructuredtext en'
__all__ = ['compute_sub_volumes',
           'vessel_detect_big_data_mpi']

def compute_sub_volumes(dataset_shape):
    """
    This function divides a given volume image into sub-volumes and returns three lists. Each list has the
    start and end indices for a sub-volume. The sub-volume size is specified in the seg_user_param.py file. 
    
    Parameters
    ----------
    dataset_shape : dataset shape
    
    Returns
    -------
    x,y,z list of indices
    
    """
    x_sub_volumes_idx = []
    y_sub_volumes_idx = []
    z_sub_volumes_idx = []
    # il_sub_vol_x, il_sub_vol_y and il_sub_vol_z are user option and specified in segmentation_param.py file.
    for x_idx in range(int(dataset_shape[0] / il_sub_vol_x) + (dataset_shape[0] % il_sub_vol_x > 0)):
        for y_idx in range(int(dataset_shape[1] / il_sub_vol_y) + (dataset_shape[1] % il_sub_vol_y > 0)):
            for z_idx in range(int(dataset_shape[2] / il_sub_vol_z) + (dataset_shape[2] % il_sub_vol_z > 0)):
                x_next_idx = []
                if (il_sub_vol_x + il_sub_vol_x * x_idx) < dataset_shape[0]:
                    x_next_idx.append(((il_sub_vol_x * x_idx), (il_sub_vol_x + il_sub_vol_x * x_idx)))
                else:
                    x_next_idx.append(((il_sub_vol_x * x_idx), (dataset_shape[0])))
                x_sub_volumes_idx.append(x_next_idx)
                
                y_next_idx = []
                if (il_sub_vol_y + il_sub_vol_y * y_idx) < dataset_shape[1]:
                    y_next_idx.append(((il_sub_vol_y * y_idx), (il_sub_vol_y + il_sub_vol_y * y_idx)))
                else:
                    y_next_idx.append(((il_sub_vol_y * y_idx), (dataset_shape[1])))
                y_sub_volumes_idx.append(y_next_idx)
                
                z_next_idx = []
                if (il_sub_vol_z + il_sub_vol_z * z_idx) < dataset_shape[2]:
                    z_next_idx.append(((il_sub_vol_z * z_idx), (il_sub_vol_z + il_sub_vol_z * z_idx)))
                else:
                    z_next_idx.append(((il_sub_vol_z * z_idx), (dataset_shape[2])))
                z_sub_volumes_idx.append(z_next_idx)
    return x_sub_volumes_idx, y_sub_volumes_idx, z_sub_volumes_idx

def make_subvolume_mpi():
    """ 
    Volume image is divided into several overlapping sub-volumes and each sub-volume image
    is written to a HDF file. 
    
    Input: The volume cell probability map file location is specified in the segmentation_param.py file. 
    
    Output: Vessel maps are written into a new data set created within the input file.                         
    """
    
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    size = MPI.COMM_WORLD.Get_size()
    name = MPI.Get_processor_name()
    start_time = time.time()
    if rank == 0:
        print("*** Time is %d Entered make_subvolume_mpi() and Size is %d****" % (time.time(), size))
    # assumes volume image file extension is .hdf5 
    hdf5_vol_file = sorted(glob(hdf_files_location + '/*.hdf5'))
    if not hdf5_vol_file:
        print("*** Did not find volume file ending with .hdf5 extension  ***")
        return
    # Remove all *.hdf5 sub-volume image files from previous runs. Create containing directory if it does not exist.
    if rank == 0:
        print("*** Ilastik input/output file location is ***", hdf_subvol_files_location)
        if os.path.exists(hdf_subvol_files_location):
            hdf5_subvol_files =  glob(hdf_subvol_files_location + '/*.hdf5')
            for file in hdf5_subvol_files:
                print("*** Removing file ***", file)
                os.remove(file)
        if not os.path.exists(hdf_subvol_files_location):
            print("*** Creating directory ***", hdf_subvol_files_location)
            os.mkdir(hdf_subvol_files_location)
    comm.Barrier()
    
    # Need Parallel HDF for faster processing. However the below test lets processing to continue even if
    # Parallel HDF is not available.
    if size == 1:
        vol_file = h5py.File(hdf5_vol_file[0], 'r')
    else:
        vol_file = h5py.File(hdf5_vol_file[0], 'r', driver='mpio', comm=comm)
    parent_dir, tiff_dir = os.path.split(tiff_files_location)
    vol_dataset = vol_file[tiff_dir]
    vol_shape = vol_dataset.shape
    if rank == 0:
        print("Volume Image Shape and data type is", vol_dataset.shape, vol_dataset.dtype)
    # Compute the sub-volumes indices
    x_sub_volumes_idx, y_sub_volumes_idx, z_sub_volumes_idx = compute_sub_volumes(vol_dataset.shape)
    if rank % 6 == 0:
        print("Done with computing sub-volumes - This is rank %d of %d running on %s" % (rank, size, name))
    
    # Figure out how many sub-volumes should be handled by each rank/process.
    iterations = int(len(x_sub_volumes_idx) / size) + (len(x_sub_volumes_idx) % size > 0)
    partial_iterations = int(len(x_sub_volumes_idx) % size)
    if rank == 0:
        print("Number of Subvolumes is %d, iterations is %d, partial_iterations is %d" % 
              (len(x_sub_volumes_idx), iterations, partial_iterations))
    for idx in range(iterations):
        if rank % 6 == 0:
            print("*** Time is %d, rank is %d ***" % (time.time(), rank))
        if (rank + (size * idx)) >= len(x_sub_volumes_idx):
            print("\nBREAKING out, my rank is %d, number of subvolume is %d, size is %d,  and idx is %d" % 
                  (rank, len(x_sub_volumes_idx), size, idx))
            break
        x_idx = x_sub_volumes_idx[rank + (size * idx)]
        y_idx = y_sub_volumes_idx[rank + (size * idx)]
        z_idx = z_sub_volumes_idx[rank + (size * idx)]
        filenumber = str(rank + size * idx).zfill(5)
        subvol_filename = hdf_subvol_files_location + '/' + tiff_dir + filenumber + '.hdf5'
        print("rank is %d, idx is %d, size is %d, file name is %s" % (rank, idx, size, subvol_filename))
        subvolfile = h5py.File(subvol_filename, 'w')
        
        # Determine pixels overlap to the right side of the sub-volume.
        if (x_idx[0][1] + pixeloverlap) < vol_shape[0]:
            x_rightoverlap = pixeloverlap
        else:
            x_rightoverlap = 0
        
        if (y_idx[0][1] + pixeloverlap) < vol_shape[1]:
            y_rightoverlap = pixeloverlap
        else:
            y_rightoverlap = 0
        
        if (z_idx[0][1] + pixeloverlap) < vol_shape[2]:
            z_rightoverlap = pixeloverlap
        else:
            z_rightoverlap = 0
        
        # Determine pixels overlap to the left side of the sub-volume.
        if (x_idx[0][0] > pixeloverlap):
            x_leftoverlap = pixeloverlap
        else:
            x_leftoverlap = 0
        
        if (y_idx[0][0] > pixeloverlap):
            y_leftoverlap = pixeloverlap
        else:
            y_leftoverlap = 0
        
        if (z_idx[0][0] > pixeloverlap):
            z_leftoverlap = pixeloverlap
        else:
            z_leftoverlap = 0
        
        x_shape = x_idx[0][1] - x_idx[0][0] + x_rightoverlap + x_leftoverlap
        y_shape = y_idx[0][1] - y_idx[0][0] + y_rightoverlap + y_leftoverlap
        z_shape = z_idx[0][1] - z_idx[0][0] + z_rightoverlap + z_leftoverlap

        subvol_dataset = subvolfile.create_dataset((tiff_dir + filenumber), (x_shape, y_shape, z_shape), vol_dataset.dtype)
        
        start_subvol_time = time.time()
        rows_count = (x_idx[0][1]+x_rightoverlap) - (x_idx[0][0]-x_leftoverlap)
        for row in range(rows_count):
            subvol_dataset[row,:,:] = vol_dataset[x_idx[0][0]-x_leftoverlap + row,
                                                  y_idx[0][0]-y_leftoverlap : y_idx[0][1]+y_rightoverlap, 
                                                  z_idx[0][0]-z_leftoverlap : z_idx[0][1]+z_rightoverlap] 
        end_subvol_time = time.time()
        # Save original indices and shape in datasets
        subvol_indx = subvolfile.create_dataset('orig_indices', (6,), dtype='uint64')
        subvol_indx[0] = x_idx[0][0]
        subvol_indx[1] = x_idx[0][1]
        subvol_indx[2] = y_idx[0][0]
        subvol_indx[3] = y_idx[0][1]
        subvol_indx[4] = z_idx[0][0]
        subvol_indx[5] = z_idx[0][1]
        right_overlapds = subvolfile.create_dataset('right_overlap', (3,), dtype='uint8')
        
        # Save overlap value to the right and left
        right_overlapds[0] = x_rightoverlap
        right_overlapds[1] = y_rightoverlap
        right_overlapds[2] = z_rightoverlap
        left_overlapds = subvolfile.create_dataset('left_overlap', (3,), dtype='uint8')
        left_overlapds[0] = x_leftoverlap
        left_overlapds[1] = y_leftoverlap
        left_overlapds[2] = z_leftoverlap
        
        if idx < 100:
            if rank % 1 == 0:
                print("rank is %d and Sub-volume shape is x, y, z  %d:%d, %d:%d, %d:%d" % 
                      (rank, x_idx[0][0], x_idx[0][1], y_idx[0][0], y_idx[0][1], z_idx[0][0], z_idx[0][1]))
                print("Sub-volume file name is %s, dataset name is %s" % (subvol_filename, subvol_dataset.name))
        
        if idx < 100:
            print("Exec time for read from disk is %d Sec and rank is %d" % ((end_subvol_time - start_subvol_time), rank))
        subvolfile.close()
    vol_file.close()
    end_time = time.time()
    if rank % 6 == 0:
        print("Sub-volume Exec time is %d Sec" % (end_time - start_time))

if __name__ == '__main__':
    make_subvolume_mpi()

