#! /usr/bin/env python

"""Wraps :mod:`run_lacosmic` to permutate different input
parameters for a given filter in order to find the best
combination.
    
Author:

    C.M. Gosmeyer, Jan. 2014

Use:

    Create a subdirectory containing a subset (~3) of FLTs for the
    given filter. cd into the subdirectory and then, 
    
    >>> python run_lacosmic_tester.py

Outputs: 

    Subdirectory for each FLT image containing diagonistic PNGs of the 
    original, mask, and clean images.
      
    Browse through these PNGs to find the best combination of params. 
    
Notes:

    For post-flashed images, you may need bump the 'sigclip' up to near
    10.0. Non-post-flashed images are good around 'sigclip' 5.0, 5.5. 
"""

import os
import shutil

from run_lacosmic import *  # Just this once
from set_paths import set_paths
from count_masked_pixels import count_masked_pixels
from lacosmic_tools import get_keyval

#-------------------------------------------------------------------------------# 

def run_lacosmic_tester(sigclip_list, sigfrac_list, objlim_list, niter_list, \
                        count_masked_pixels=False):
    """Tests different parameters of `LACOSMIC`.
    
    Parameters
    ----------
    sigclip_list : list of floats
        Detection limits for cosmic rays.
    sigfrac_list : list of floats
        Detection limits for adjacent pixels.
    objlim_list : list of ints
        Max numbers of objects desired in image.
    niter_list : list of ints
        Numbers of iterations of cosmic ray finder.
    count_masked_pixels : {True, False}
        Default False. Set to True if want to count the
        number of masked pixels per image.
            
    Outputs
    -------
    If count_masked_pixels True:
        ascii file. `<filter>_mask_counts.dat`.
        The number of masked pixels in each mask image.
    """
    
    filenames = create_file_list()
    # Create subdirectories for each filename
    for filename in filenames:
        dir_rootname = filename.split('.fits')[0]
        #os.makedirs(dir_rootname)

    paths = set_paths()
    define_lacosmic(paths['lacos_im'] + 'lacos_im.cl')
    # Run the permutations, creating plots for each
    for filename in filenames:
        for sigclip in sigclip_list:
            for sigfrac in sigfrac_list:
                for objlim in objlim_list:
                    run_lacosmic(filename, \
                                 sigclip, \
                                 sigfrac, \
                                 objlim, \
                                 niter_list[1])
                    create_images_png(file, str(sigclip) + '_' + \
                                            str(sigfrac) + '_' + \
                                 	        str(objlim) + '_' + \
                                 	        str(niter_list[1]) + '.png')

                    if count_masked_pixels:
                        # Rename the .clean and .mask files
                        mask_to_rename = filename.split('.fits')[0]+'.mask.fits'
                        clean_to_rename = filename.split('.fits')[0]+'.clean.fits'
                        os.rename(mask_to_rename, str(sigclip) + '_' + \
                                                  str(sigfrac) + '_' + \
                                 	              str(objlim) + '_' + \
                                 	              str(niter_list[1]) + \
                                 	              '_mask.fits') 
                        os.rename(clean_to_rename, str(sigclip) + '_' + \
                                                   str(sigfrac) + '_' + \
                                 	               str(objlim) + '_' + \
                                 	               str(niter_list[1]) + \
                                 	               '_clean.fits') 
                        
                        newfiles = glob.glob('*mask*')
                        print newfiles
                    elif not count_masked_pixels:
                        # Delete the .clean and .mask files
                        clean_to_delete = glob.glob('*.clean.fits')
                        mask_to_delete = glob.glob('*.mask.fits')
                        os.remove(clean_to_delete[0]) 
                        os.remove(mask_to_delete[0]) 
        # Move all PNGs into subdirectory of the current filename
        png_files = glob.glob('*.png')
        for png_file in png_files:
            shutil.move(png_file, filename.split('.fits')[0])
        
        # Move all .mask and .clean FITS into subdirectory of the current filename    
        if count_masked_pixels:
            mask_files = glob.glob('*mask.fits')
            clean_files = glob.glob('*clean.fits')
            all_files = mask_files + clean_files
            for filename in all_files:
                shutil.move(filename, file.split('.fits')[0])
   
#    if count_masked_pixels:         
#        filtername = get_keyval(filename=filename, keyword='FILTER')
#        count_masked_pixels(filter=filtername)


#-------------------------------------------------------------------------------# 
# The Main.
#-------------------------------------------------------------------------------# 

if __name__=='__main__':
    # Change these how you like.
    sigclip_list = [9.0, 9.5, 10.0]  # Post-flash test values
                  #[5.0, 5.5, 6.0, 6.5]  # Non-post-flash test values
    sigfrac_list = [0.3, 0.4]
    objlim_list = [2,3,4,5]
    niter_list = [4,5]

    tester_run_lacosmic_v2(sigclip_list, sigfrac_list, objlim_list, niter_list, \
                           count_masked_pixels=True)

