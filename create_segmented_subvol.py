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
This module segments an image into as many as types defined in the trained data.
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
__all__ = ['segment_pixels']

def create_segmented_subvol(subvol_im, pixel_masks, filename, orig_idx_data, rightoverlap_data, leftoverlap_data, seg_output):
    """ 
    Separates pixels in an input sub-volume image array and creates an hdf5 for each input array.
    Pixel mask for each class defined in the trained data is an input to this script.
    This script creates segmented image for each sub-volume by element by element multiplication 
    of the mask and the corresponding composite sub-volume image. Segmented pixels for each class of 
    the sub-volume is written into a separated dataset of the segmented output hdf5 file/sub-volume.
    
    Inputs: 
    subvol_im -  Composite sub-volumes image array
    pixel_mask - sub-volume mask array
    filename - output file name
    orig_idx_data - whole volume array indices
    rightoverlap_data - number of overlapped pixels from the right side of the sub-volume.
    leftoverlap_data  - number of overlapped pixels from the left side of the sub-volume.
    seg_output - whether or not to save segmented output as binary or pixel intensity.
    
    Ouputs:
    a hdf5 file per sub-volume with a dataset for each defined segmented class.
    """
    
    start_time = time.time()
    ilastik_classes = get_ilastik_labels()
    print("Ilastik classes are ", ilastik_classes)
    im_out_filename = outimage_file_location + '/subvol_' + filename + '.h5'
    seg_im_file = h5py.File(im_out_filename, 'w')
    # Save sub-volume indices 
    subvol_indx = seg_im_file.create_dataset('orig_indices', (6,), dtype='uint64')
    subvol_indx[...] = orig_idx_data
    # Save sub-volume right and left side overlaps.
    subvol_rightoverlap = seg_im_file.create_dataset('right_overlap', (3,), dtype='uint8')
    subvol_rightoverlap[...] = rightoverlap_data
    subvol_leftoverlap = seg_im_file.create_dataset('left_overlap', (3,), dtype='uint8')
    subvol_leftoverlap[...] = leftoverlap_data
    
    for label in range(len(ilastik_classes)):
        seg_im_ds = seg_im_file.create_dataset(ilastik_classes[label], subvol_im.shape, subvol_im.dtype)
        multiply_time = time.time()
        if seg_output == True:
            seg_im_ds[...] = pixel_masks[..., label]
        else:
            seg_im_ds[...] = subvol_im * pixel_masks[..., label]
        print("Multiply time for one dataset is %d Sec" % (time.time() - multiply_time))
        
    seg_im_file.close()
    end_time = time.time()
    print("Exec time for create_segmented_subvol is %d Sec" % ((end_time - start_time)))
    return
