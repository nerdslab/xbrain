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
Specify segmentation project data in this file.

Must specify the subvolume dimensions, TIFF file location/directory,
full path to Ilastik training data file, number of threads and percentage
of memory  to be used by an Ilastik python process,  whether or not to
save cell probably map for cell object class, whether or not to
save vessel probably map for vessel object class, and whether or not to save
segmented output in binary or pixel intensity.
"""

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

__author__ = "Mehdi Tondravi"
__copyright__ = "Copyright (c) 2017, UChicago Argonne, LLC."
__docformat__ = 'restructuredtext en'

'''
User should specify the following info:

1) The sub-volume dimensions: il_sub_vol_x (number of slices), il_sub_vol_y (columns) and il_sub_vol_z (rows)
2) tiff_files_location - the full path to the directory containing TIFF image files.
3) classifier - the full path to the directory containing the Ilastik trained data file.
4) Number of threads to be used by an Ilastik classifier python process.
5) Precentage of available memory in a server to be used by an Ilastik classifier python process.
6) save_cell_prob_map - save cell probability map? 
7) save_vessel_prob_map - save vessel probability map?
8) binary_output - save segmented output in binary?
'''

# Subvolume dimensions for breaking up the volume image.
# il_sub_vol_x = number of slices
# il_sub_vol_y = number of columns
# il_sub_vol_z = number of rows
il_sub_vol_x = 400
il_sub_vol_y = 400
il_sub_vol_z = 600

# Specify full path to the reconstructed image tiff files directory
# tiff_files_location = '/projects/mousebrain/recon_rot34_crop_cc'

# Specify full path to the Ilastik trained data file.
# classifier = '/projects/classifiers/v1_4xmouse_train_data.ilp'

tiff_files_location = '/Users/mehditondravi/xray_data/neurodata_test_eneura_tiff'
classifier = '/Users/mehditondravi/xray_data/neurodata_test/neurodata_test_train.ilp'

'''
Specify number of threads to be used by Ilastik. For example:
If want four threads to be used then:
no_of_threads_to_use = '4'
If want all threads to be used then leave it blank:
no_of_threads_to_use = ''
'''
no_of_threads_to_use = '4'

'''
Specify prencentage of memory to be used by Ilastik.
If want 25% to be used then:
percent_mem_to_use = '25'
If want all memory to be used then leave it blank:
percent_mem_to_use = ''
'''
percent_mem_to_use = '50'

# whether or not to save Ilastik cell probability map.
save_cell_prob_map = 'yes'

# whether or not to save Ilastik Vessel probability map.
save_vessel_prob_map = 'yes'

# whether to save segmented pixels in binary or pixel intensity.
binary_output = 'no'
