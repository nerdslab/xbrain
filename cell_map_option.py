#!/usr/bin/env python 

from seg_user_param import save_cell_prob_map
from seg_user_param import save_vessel_prob_map

def cell_map_option():
    if save_cell_prob_map.upper() == 'YES':
        print("yes")
    elif save_vessel_prob_map.upper() == 'YES':
        print("yes")
    else:
        print("no")
    return

if __name__ == '__main__':
    cell_map_option()



