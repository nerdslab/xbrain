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
This module segments an image sub-volume into as many sub-volumes as labeled in training data.
'''

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import os.path
import h5py
import numpy as np
from glob import glob
from mpi4py import MPI
import time
from segmentation_param import *
from classify_pixel import classify_pixel
from create_subvol_mask import create_subvol_mask
from create_segmented_subvol import create_segmented_subvol
from save_ilastik_prob_map import save_ilastik_prob_map
import pdb

__author__ = "Mehdi Tondravi"
__copyright__ = "Copyright (c) 2017, UChicago Argonne, LLC."
__docformat__ = 'restructuredtext en'
__all__ = ['segment_subvols_pixels']

def segment_subvols_pixels():
    """
    Divides many *.hdf5 sub-volume image files among ranks created for classification
    and segmentation. A rank uses Ilastik classifier to create probability maps, and then
    separate the input image into as many as images as are defined labels in the training data.
    
    Inputs: 
    The *.hdf5 sub-volume files location is specified in seg_user_param.py file.
    Ilastik trained data - file location is specified in seg_user_param.py file.
        
    Output: 
    The segmented sub-volumes files in location as specified in seg_user_param.py file.
    Saves cell probability map if the user has requested it by setting "save_cell_prob_map" to "yes".
    
    """
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    size = MPI.COMM_WORLD.Get_size()
    name = MPI.Get_processor_name()
    start_time = int(time.time())
    # Allow Ilatisk to use all available threads of the server/compute node.
    threads = int(no_of_threads/1)
    # Allow Ilastik to use all available memory of the server/compute node.
    ram = int(ram_size)
    
    threads = 12
    #ram = 36
    
    # if not enough memory stop processing. Required memory is subvolume size times 4 bytes times
    # number of labeled classed plus two.
    mem_required = il_sub_vol_x * il_sub_vol_y * il_sub_vol_z * (len(get_ilastik_labels()) + 2) * 4
    if int(mem_required / 1e6) > ram:
        print("AVAILABLE MEMORY IS NOT BIG ENOUGH TO PROCEED. MAKE SUBVOLUME SMALLER AND TRY AGAIN")
        print("Avaiable memory is %d MB and required memory is %d MB" % (ram, int(mem_required/ 1e6)))
        return
    if rank == 0:
        print("*** size is %d, No of thread is %d, ram size is %d" % (size, threads, ram))
    # assumes sub-volume image file extension is .hdf5
    input_files = sorted(glob(hdf_subvol_files_location + '/*.hdf5'))
    if not input_files:
        print("*** Did not find any file ending with .hdf5 extension  ***")
        return
    if rank == 0:
        print("Number of input/HDF5 files is %d, and Number of processes is %d" % ((len(input_files)), size))
    
    if rank == 0:
        print("Sub-Volume file location is %s" % outimage_file_location)
        # Remove sub-volume files from previous run
        '''
        if os.path.exists(outimage_file_location):
            subvolfiles = glob(outimage_file_location + '/subvol*.h5')
            for subfile in subvolfiles:
                print("*** Removing file ***", subfile)
                os.remove(subfile)
        '''
        # Create the directory for segmented sub-volume images if it does not exist. 
        if not os.path.exists(outimage_file_location):
            print("*** Creating directory %s ***" % outimage_file_location)
            os.mkdir(outimage_file_location)
    
    comm.Barrier()
    
    if rank == 0:
        print("Number of input/HDF5 files is %d, and Number of processes is %d" % ((len(input_files)), size))
    
    # Figure out how many sub-volume files each rank should handle.
    iterations = int(len(input_files) / size) + (len(input_files) % size > 0)
    # Divide pixel classification of sub-volume files among processes/ranks. 
    for idx in range(iterations):
        if (rank + (size * idx)) >= len(input_files):
            print("\nBREAKING out, this rank is done with its processing, my rank is %d, number of files is %d, size is %d and idx is %d" %
                  (rank, len(input_files), size, idx))
            break
        start_loop_time = time.time()
        filename = input_files[(rank + size * idx)]
        dsname, ext = os.path.splitext(os.path.basename(filename))
        hdf_filename = h5py.File(filename, 'r')
        subvol_ds = hdf_filename[dsname]
        # Retrieve the indices into whole volume for this sub-volume.
        orig_idx_ds = hdf_filename['orig_indices']
        orig_idx_data = orig_idx_ds[...]
        # Retrive overlap size to the right side of the sub-volume. 
        rightoverlap_ds = hdf_filename['right_overlap']
        rightoverlap_data = rightoverlap_ds[...]
        # Retrive overlap size to the left side of the sub-volume.
        leftoverlap_ds = hdf_filename['left_overlap']
        leftoverlap_data = leftoverlap_ds[...]
        
        start_dstime = time.time()
        subvol_data = subvol_ds[...]
        print("Read time for datasetfrom disk is %d sec and rank is %d" % ((time.time() - start_dstime), rank))
        ilastik_time = time.time()
        probability_maps = classify_pixel(subvol_data, classifier, threads, ram)
        print("probability_map shape and data type are", probability_maps.shape, probability_maps.dtype)
        print("time for ilastik classification is %d sec and rank is %d" % ((time.time() - ilastik_time), rank))
        
        mask_time = time.time()
        subvol_pixel_masks = create_subvol_mask(probability_maps)
        print("time to create pixel masks is %d sec and rank is %d" % ((time.time() - mask_time), rank))
        
        segment_time = time.time()
        create_segmented_subvol(subvol_data, subvol_pixel_masks, dsname, orig_idx_data, rightoverlap_data, leftoverlap_data)
        print("time to time to segement pixels is %d sec and rank is %d" % ((time.time() - mask_time), rank))
        # Save cell probability map in a file if user has asked for it.
        savemap, label_index = save_prob_map()
        if savemap == True:
            # Save probability map
            labeld_obj = get_ilastik_labels()
            print("Saving probability map for object type %s, rank is %d" % (labeld_obj[label_index], rank))
            save_ilastik_prob_map(probability_maps, label_index, dsname, orig_idx_data,
                                  rightoverlap_data, leftoverlap_data)
    
    end_time = int(time.time())
    exec_time = end_time - start_time
    print("*** My Rank is %d, exec time is %d sec - Done with classifying pixels in sub-volume files ***" % (rank, exec_time))

if __name__ == '__main__':
    segment_subvols_pixels()
