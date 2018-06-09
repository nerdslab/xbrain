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

"""
This file has various parameters values needed for segmentation of big data.
"""

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import multiprocessing
from psutil import virtual_memory
from seg_user_param import *

__author__ = "Mehdi Tondravi"
__copyright__ = "Copyright (c) 2017, UChicago Argonne, LLC."
__docformat__ = 'restructuredtext en'

'''
The below parameters should not be changed.
'''

# Number of pixel to use for overlapping in sub-voluming images.
pixeloverlap = 20

# Volume raw input data
hdf_files_location = tiff_files_location + '_mpi_hdf'

# Ilastik sub-volume input/oputput hdf5 files
hdf_subvol_files_location = tiff_files_location + '_ilastik_inout'

# Segmented pixel Sub-volume directory - contains an hdf5 file for each sub-volume.
outimage_file_location = tiff_files_location + '_pixels_maps'

# Segmented pixel volume directory - contains one hdf5 file with a datasets for each segmented class.
volume_map_file_location = tiff_files_location + '_volume_prob_maps'

# Post segmentation image volume files.
post_seg_volume_location = tiff_files_location + '_post_segmentation'

# Dataset name for Ilastik probability map for classified classes.
ilastik_ds_name = 'exported_data'

no_of_threads = multiprocessing.cpu_count()
ram_size = int(virtual_memory().total/(1024**3)) * 1000

ilp_file_name = classifier

# small size objects to be removed from cell segmentation
MINSZ_CELL = 100

import h5py
import pdb

def get_ilastik_labels():
    '''
    This function finds and returns the object class names defined during the 
    Ilastik training session.
    '''
    
    ilpfile = h5py.File(ilp_file_name, 'r')
    label_ds = ilpfile['PixelClassification/LabelNames']
    labels = label_ds[...].tolist()
    
    for idx in range(len(labels)):
        labels[idx] = labels[idx].decode()
    
    print(labels)
    return labels


def save_prob_map(label):
    '''
    This function returns whether to save Ilastik cell probability map to file or not.
    '''
    index = 0
    save_to_file = False
    if label == 'CELL':
        save_class = save_cell_prob_map
    elif label == 'VESSEL':
        save_class = save_vessel_prob_map
    else:
        return (save_to_file, index)
    
    if save_class.upper() == 'YES':
        labels = get_ilastik_labels()
        for item in labels:
            if label in item.upper():
                save_to_file = True
                index = labels.index(item)
                break
            
    return (save_to_file, index)

def seg_pixel_value():
    '''
    Retuns whether to save segmented pixels in binary or pixel intensity.
    '''
    if binary_output.upper() == 'YES':
        save_binary = True
    else:
        save_binary = False
    return save_binary

