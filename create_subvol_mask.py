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
Assigns each pixel to the class with the highest probability determine by Ilastik classifier.
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
__all__ = ['classify_subvolumes']

def create_subvol_mask(prob_maps):
    """ 
    Assigns each pixels to the class with the highest probability value determined by Ilastik classifier.
    
    Ilastik returns probability map in the "prob_maps" dataset with the dimensions of x,y,z 
    (pixel location) by N probability values and N is the number of classes (labels) defined in the Ilastik 
    trained data file. This script for each pixel location sets the highest probability value to one and sets
    the remaining probability values (N-1 valuve) to zeroes. 
    
    Input: Ilastik sub-volumes pixel classified probability map array.
    
    Output: array 
    """
    
    output_array = np.zeros(prob_maps.shape, dtype='uint8')
    print("prob_maps data shape is", prob_maps.shape)
    print_cycle = 500
    start_loop_time = time.time()
    for row in range(output_array.shape[0]):
        for colmn in range(output_array.shape[1]):
            outdata = np.zeros((output_array.shape[2], output_array.shape[3]), 'uint8')
            if row == 0:
                if colmn == 0:
                    print("outdata shape is", outdata.shape)
            outdata[np.arange(len(outdata)), np.argmax(prob_maps[row, colmn, :, :], axis=-1)] = 1
            if np.count_nonzero(outdata) != output_array.shape[2]:
                print("Something is very wrong - check row %d and colmn %d" % (row, colmn))
            output_array[row, colmn, :, :] = outdata.copy()
        if row != 0 and row % print_cycle == 0:
            print("time to classify %d rows is %d Sec" % (print_cycle, (time.time() - start_loop_time)))
            start_loop_time = time.time()
    print("prob map output array shape is", output_array.shape)
    return output_array

