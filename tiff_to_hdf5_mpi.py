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
Converts reconstructed tiff image files into its corresponding numpy array.
'''

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import h5py
import numpy as np
from skimage.io import imread
from glob import glob
import os.path
from segmentation_param import *
from mpi4py import MPI
import time
import pdb

__author__ = "Mehdi Tondravi"
__copyright__ = "Copyright (c) 2017, UChicago Argonne, LLC."
__docformat__ = 'restructuredtext en'
__all__ = ['tiff_to_hdf5_files']

def tiff_to_hdf5_files():
    """
    Converts reconstructed tiff image files into a hdf5 file.
    
    Creates a directory to hold the hdf file at the same level as tiff files directory. This directory name
    is the same as tiff directory name plus "_hdf". Creates a hdf5 file with the name made of 
    the concatenation of the first tiff file and the last tiff file. Creates a HDF data set name with the 
    same name as the directory name of the tiff files.
    As an example if the tiff files are located at, "~/projects/eva_block" directory,
    the first tiff name is "data_00860.tiff.tif" and the last tiff file name is "data_01139.tiff.tif" 
    then the HDF file created is:
    ~/projects//eva_block_hdf/data_00860.tiff_data_01139.tiff.hdf5
    and HDF5 data set name is "eva_block".
    Division of work among ranks/processes is based on a tiff file.
    
    Input: Tiff files location is specified in the seg_user_param.py file.
    
    Output: HDF5 files location is specified in the seg_user_param.py file.
    
    """
    
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    size = MPI.COMM_WORLD.Get_size()
    name = MPI.Get_processor_name()
    start_time = int(time.time())
    files = sorted(glob(tiff_files_location + '/*.tif*'))
    parent_dir, tiff_dir = os.path.split(tiff_files_location)
    hdf_dir = parent_dir + '/' + tiff_dir + '_' + 'mpi' + '_hdf'
    
    # if there is no tiff return.
    if not files:
        print("**** Did not find any TIFF file, terminating execution ****")
        return
    
    # Remove all *.hdf5 files from previous runs. Create directory if it does not exist
    if rank == 0:
        print("**** File location is ****", hdf_dir)
        if os.path.exists(hdf_dir):
           hdf5_files =  glob(hdf_dir + '/*.hdf5')
           for file in hdf5_files:
               print("*** Removing file ***", file)
               os.remove(file)
        if not os.path.exists(hdf_dir):
            print("*** Creating directory ***", hdf_dir)
            os.mkdir(hdf_dir)
    comm.Barrier()
    
    # Get the shape and dtype of tiff file - all tiff files have the same shape and type.
    data_shape = imread(files[0], plugin='tifffile').shape
    data_type = imread(files[0], plugin='tifffile').dtype
    
    first_file_name, first_file_ext = os.path.splitext(os.path.basename(files[0]))
    last_file_name, last_file_ext = os.path.splitext(os.path.basename(files[-1]))
    hdf_file_name = hdf_dir + '/'+first_file_name + '_' + last_file_name + '.hdf5'
    file_time = time.time()
    # Need Parallel HDF for faster processing. However the below test lets processing to continue even if
    # Parallel HDF is not available.
    if size == 1:
        hdf_file = h5py.File(hdf_file_name, 'w')
    else:
        hdf_file = h5py.File(hdf_file_name, 'w', driver='mpio', comm=comm)
    data_set_name = tiff_dir
    if rank == 0:
        print("*** Dataset name is %s and file create time is %d***" % (data_set_name, (time.time() - file_time)))
    ds_time = time.time()
    data_set = hdf_file.create_dataset(data_set_name, (len(files), data_shape[0], data_shape[1]), data_type)
    if rank == 0:
        print("dataset creatation time is %d" % (time.time() - ds_time))
    iterations = int(len(files) / size) + (len(files) % size > 0)
    for idx in range(iterations):
        if rank == 0:
            if idx == 0:
                print("***** starting to convert TIFF files ***")
        if (rank + (size * idx)) >= len(files):
            print("\nBREAKING out, my rank is %d, number of files is %d, size is %d and idx is %d" %
                  (rank, len(files), size, idx))
            break
        imread_start = time.time()
        imarray = imread(files[rank + size * idx], plugin='tifffile')
        data_set[(rank + size * idx), :, :] = imarray
        imread_end = time.time()
        if idx % 50 == 0:
            print("IM Read done, rank is %d, idx is %d, time for read is %d sec, number of bytes %d, element size %d, file is %s" % 
                  (rank, idx, (imread_end - imread_start), imarray.nbytes, imarray.itemsize, files[rank + size * idx]))
    
    print("data shape is, rank is", data_set.shape, rank)
    hdf_file.close()
    end_time = int(time.time())
    exec_time = end_time - start_time
    print("Done dividing tiff files, rank is %d, size is %d, name is %s, exec time is %d sec" % (rank, size, name, exec_time))


if __name__ == '__main__':
    tiff_to_hdf5_files()

