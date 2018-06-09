#!/bin/bash
echo "**** Executing segmentation script ****"
sleep 1

if cp  $1 ./seg_user_param.py; then
    echo "copying options file succeeded"
else
    exit 1
fi

echo "**** Executing tiff_to_hdf5_mpi() Script ****"
if python tiff_to_hdf5_mpi.py; then
    echo "**** Done Executing tiff_to_hdf5_mpi() Script ***"
else
    exit 1
fi
sleep 1

echo "**** Executing make_subvolume_mpi() ****"
if python make_subvolume_mpi.py; then
    echo "**** Done Executing make_subvolume_mpi() ****"
else
    exit 1
fi
sleep 1

echo "**** Executing segment_subvols_pixels() ****"
if python segment_subvols_pixels.py; then
    echo "**** Done Executing segment_subvols_pixels() ****"
else
    exit 1
fi
sleep 1

echo "**** Executing combine_segmented_subvols() ****"
if python combine_segmented_subvols.py; then
    echo "**** Done Executing combine_segmented_subvols() ****"
else
    exit 1
fi
sleep 1

cell_map=$(python cell_map_option.py)
if [ "$cell_map" == "yes" ]; then
    echo "**** Executing combine_subvols_prob_map() ****" 
    if python combine_subvols_prob_map.py; then
	echo "**** Done Executing combine_subvols_prob_map() ****"
    else
	exit 1
    fi
fi
sleep 1
echo "**** All Done ****"
