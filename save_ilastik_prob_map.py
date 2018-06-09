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
This module saves probability map dataset created by Ilastik in a file.
'''

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import pdb
import numpy as np
import h5py
import os.path
from glob import glob
import time
from segmentation_param import *

__author__ = "Mehdi Tondravi"
__copyright__ = "Copyright (c) 2017, UChicago Argonne, LLC."
__docformat__ = 'restructuredtext en'
__all__ = ['save_ilastik_prob_map']

def save_ilastik_prob_map(prob_maps, orig_idx_data, rightoverlap_data, leftoverlap_data, idx, idx_list):
    """ 
    
    Inputs: 
    prob_maps -  Composite sub-volumes image array
    orig_idx_data - whole volume array indices
    rightoverlap_data - number of overlapped pixels from the right side of the sub-volume.
    leftoverlap_data  - number of overlapped pixels from the left side of the sub-volume.
    idx - file number
    idx_list - list of indices of object classes to save their probability map
    Ouputs:
    a hdf5 file per sub-volume with a dataset for each defined segmented class.
    """
    
    start_time = time.time()
    ilastik_classes = get_ilastik_labels()
    prob_map_file = hdf_subvol_files_location + '/subarr_prob_map_' + str(idx).zfill(5) + '.h5'
    probfile = h5py.File(prob_map_file, 'w')
    # Save sub-volume indices 
    subvol_indx = probfile.create_dataset('orig_indices', (6,), dtype='uint64')
    subvol_indx[...] = orig_idx_data
    # Save sub-volume right and left side overlaps.
    subvol_rightoverlap = probfile.create_dataset('right_overlap', (3,), dtype='uint8')
    subvol_rightoverlap[...] = rightoverlap_data
    subvol_leftoverlap = probfile.create_dataset('left_overlap', (3,), dtype='uint8')
    subvol_leftoverlap[...] = leftoverlap_data
    print("*** Create subvolume probability map for ****", idx_list)
    write_time = time.time()
    for label_idx in idx_list:
        dataset = ilastik_classes[label_idx]
        map_to_save = prob_maps[..., label_idx]
        mapds = probfile.create_dataset(dataset, map_to_save.shape, map_to_save.dtype)
        mapds[...] = map_to_save
    
    print("dataset write time for one dataset is %d Sec" % (time.time() - write_time))
    probfile.close()
    end_time = time.time()
    print("Exec time for create_segmented_subvol is %d Sec" % ((end_time - start_time)))
    return

