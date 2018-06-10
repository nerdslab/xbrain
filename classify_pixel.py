#!/usr/bin/env python
# -*- coding: utf-8 -*-

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
Interface module to Ilastik pixel classifier to create probability maps for a given dataset and training data.
'''

from __future__ import (absolute_import, division, print_function, unicode_literals)
import numpy as np
import six
import pdb
from collections import OrderedDict
import vigra
import os
import ilastik_main
from ilastik.applets.dataSelection import DatasetInfo
from ilastik.workflows.pixelClassification import PixelClassificationWorkflow

def classify_pixel(input_data, classifier, threads, ram):

    """
    Interface function to Ilastik object classifier functions.  
    
    Runs a pre-trained ilastik classifier on a volume of data
    Adapted from Stuart Berg's example here:
    https://github.com/ilastik/ilastik/blob/master/examples/example_python_client.py

    Arguments:
        input_data: data to be classified - 3D numpy array
        classifier: ilastik trained/classified file
        threads: number of thread to use for classifying input data
        ram: RAM to use in MB

    Returns:
        pixel_out: The probability maps for the classified pixels
    """
    
    # Before we start ilastik, prepare these environment variable settings.
    os.environ["LAZYFLOW_THREADS"] = str(threads)
    os.environ["LAZYFLOW_TOTAL_RAM_MB"] = str(ram)

    # Set the command-line arguments directly into argparse.Namespace object
    # Provide your project file, and don't forget to specify headless.
    args = ilastik_main.parser.parse_args([])
    args.headless = True
    args.project = classifier

    # Instantiate the 'shell', (an instance of ilastik.shell.HeadlessShell)
    # This also loads the project file into shell.projectManager
    shell = ilastik_main.main(args)
    assert isinstance(shell.workflow, PixelClassificationWorkflow)

    # Obtain the training operator
    opPixelClassification = shell.workflow.pcApplet.topLevelOperator

    # Sanity checks
    assert len(opPixelClassification.InputImages) > 0
    assert opPixelClassification.Classifier.ready()

    # In this example, we're using 3D data (extra dimension for channel).
    # Tagging the data ensures that ilastik interprets the axes correctly.
    input_data = vigra.taggedView(input_data, 'zyx')

    # In case you're curious about which label class is which,
    # let's read the label names from the project file.
    label_names = opPixelClassification.LabelNames.value
    label_colors = opPixelClassification.LabelColors.value
    probability_colors = opPixelClassification.PmapColors.value
    
    print("label_names, label_colors, probability_colors", label_names, label_colors, probability_colors)
    
    # Construct an OrderedDict of role-names -> DatasetInfos
    # (See PixelClassificationWorkflow.ROLE_NAMES)
    role_data_dict = OrderedDict([("Raw Data",
                                   [DatasetInfo(preloaded_array=input_data)])])
    
    # Run the export via the BatchProcessingApplet
    # Note: If you don't provide export_to_array, then the results will
    #       be exported to disk according to project's DataExport settings.
    #       In that case, run_export() returns None.
    
    predictions = shell.workflow.batchProcessingApplet.\
        run_export(role_data_dict, export_to_array=True)
    print("predictions.dtype, predictions.shape", predictions[0].dtype, predictions[0].shape)
    
    print("DONE.")
    
    return predictions[0]
