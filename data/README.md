# Image Data and Annotated Volumes #

This repo contains manually annotated volumes of 3D X-ray microtomography data. All of the data volumes and annotations are saved as nrrd or nii files, both of which can be opened in Fiji and converted to a wide range of file formats. You can also open nrrd/nii files in Python with the use of the pynrrd package.

***
If you use any of the datasets contained in this repository, please cite the following paper:

__Dyer, Eva L., et al. "Quantifying mesoscale neuroanatomy using X-ray microtomography." eNeuro, 4(5)ENEURO.0195-17.2017. [[Link to Paper]](http://www.eneuro.org/content/4/5/ENEURO.0195-17.2017)__

***
If you have any questions, please contact Eva Dyer at evadyer{at}gatech{dot}edu.

## Details about image data ##
* The images provided are micro-computed tomography (microCT) data collected from 2-BM at Argonne National Laboratory.
* These samples are taken from roughly a cubic mm volume of mouse somatosensory cortex (S1) that spans multiple cortical layers and a small portion of corpus callosum. 
* The spatial resolution is 0.65 um isotropic (each voxel = 0.65x0.65x0.65 um^3).

## What's available ##
* __Download the full dataset (TIFF stack)__ (2.2 GB) [[Link to Full Dataset]](https://www.dropbox.com/s/1fvjih9mvvfdaq6/proj4_masked_390_2014.zip?dl=0)
![alt text](samples/V1-img.PNG?raw=true "V1")

* __Download annotated subvolumes from four regions in the sample__ (269 MB) [[Link to Annotations]](https://www.dropbox.com/sh/hu9e6hm2hvfna67/AADtG-ICqkEa0962pVSwrXBua?dl=0)
   - V1, V2, V3 are all different (non-overlapping) subvolumes that were selected within an unsectioned cubic mm volume of mouse cortex.
   - V1 is the largest annotated volume (300 x 300 x 100 pixels) and currently the only volume that we have full (dense) reconstructions of cells and vessels.
   - V0 is a smaller cube in the middle of V1 for which we have two annotations from different annotators (A1 and A2) combined to produce a dense segmentation of cells and blood vessels.
   - V2 can be used as a small test set for cell detection algorithms (dense annotation of cell bodies, some sparse annotations of vessels).
   - V3 was the final held out test set that we used to evaluate our cell detection methods (only cell centroids, not full cell bodies).
   - V4 is a subvolume that is located near the bottom of layer 6 and reveals myelinated axons in the corpus callosum traversing the subvolume.
***
