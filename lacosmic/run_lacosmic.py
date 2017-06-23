#! /usr/bin/env python

"""Performs ``IRAF`` task ``LACosmic`` on FLTs in current working
directory to mask cosmic rays.

Can be run on either Hubble WFC3/UVIS full-chip or subarray images.

This is best run after :mod:`run_lacosmic_tester`, which should
help you find the most ideal parameters for the given filter.


Author:

    C.M. Gosmeyer, Jan. 2014

Use:

   For this script to run properly, be sure you first ran
   :mod:`init_setup_lacosmic.py` from the directory containing this
   script. Note that this only needs be done once, unless you move
   the location of the directory.

   All other times, just cd into directory containing FLTs. Then

    >>> python run_lacosmic.py

Outputs:

    LACosmic cleaned images, ``flt_cleans/*.clean.fits``

    LACosmic mask images, ``flt_cleans/*.clean.fits``

    Diagnostic PNGs of the original, mask, and clean images,
    ``png_masks_cleans/*.png``

Notes:

    See the `README.md` for full documentation of the entire package.

    Some quick comments:

    * Add ``LACosmic`` parameters to :func:`lacosmic_param_dictionary`
      for each filter as needed. Find these parameters using
      :mod:`run_lacosmic_tester`.
    * Look through all the diagnostic plots. If you see that LACosmic
      "blew up" (masked light from the source) on an image, take its
      clean FLT from its directory and store it in a ``flags`` directory.
    * For post-flashed images, you may need bump the 'sigclip' up to near
      10.0. Non-post-flashed images are good around 'sigclip' 5.0, 5.5.

"""

import glob
import numpy as np
import os
import pylab
import shutil
import sys

from astropy.io import fits
from pyraf import iraf

import img_scale
from set_paths import set_paths
from lacosmic.lacosmic_tools import get_keyval
from lacosmic.lacosmic_tools import move_files

#-------------------------------------------------------------------------------#

def create_images_png(filename, outfilename='Default'):
    """Creates the original, clean, and mask images in single a PNG.
    Useful for checking how well LACosmic worked.

    You may want to adjust the size of the "cut" images so to
    capture your source star.

    Parameters:
        filename : string
            Name of the original FITS image, including the path.
        outfilename : string, optional
            Name of the outfile PNG.

    Returns:
        nothing

    Outputs:
        PNG file. ``<file rootname>.png`` by default.
        Shows both full frame images and "cut" images of the source.
    """
    pylab.ioff()
    # create page for plots
    page_width = 21.59/2
    page_height = 27.94/2
    fig = pylab.figure(figsize=(page_width, page_height))

    file_clean = (filename.split('.fits')[0]+'.clean.fits')
    file_mask = (filename.split('.fits')[0]+'.mask.fits')

    scmax = 7000 # scale_max for raw and clean
    scmin = 3 # scale_min for raw and clean

    # Plot the original image
    pylab.subplot(3,2,1, aspect='equal') # 311
    image_orig = fits.open(filename)
    image_orig_ext = image_orig[1].data
    image_orig_scaled = img_scale.log(image_orig_ext, \
                                      scale_min=scmin, \
                                      scale_max=scmax)
    plt_orig = pylab.imshow(image_orig_scaled, aspect='equal')
    pylab.title('Original (SCI)')

    # Plot cut of original image
    pylab.subplot(3,2,2, aspect='equal')
    image_orig_cut = img_scale.log(image_orig_ext[175:275,175:275], \
                                   scale_min=scmin, \
                                   scale_max=scmax)
    plt_orig_cut = pylab.imshow(image_orig_cut, aspect='equal')
    pylab.title('Original (SCI)')
    image_orig.close()


    # Plot the mask image
    pylab.subplot(3,2,3) #312
    image_mask = fits.open(file_mask)
    image_mask_ext = image_mask[0].data
    plt_orig = pylab.imshow(image_mask_ext, aspect='equal', vmin=-2, vmax=1) #-2, -5
    pylab.title('Mask')

    # Plot cut of the mask image
    pylab.subplot(3,2,4)
    plt_mask_cut = pylab.imshow(image_mask_ext[175:275,175:275], \
                                aspect='equal', vmin=-2, vmax=1)
    pylab.title('Mask')
    image_mask.close()


    # Plot the LACosmic-cleaned image
    pylab.subplot(3,2,5) #313
    image_clean = fits.open(file_clean)
    image_clean_ext = image_clean[0].data
    image_clean_scaled = img_scale.log(image_clean_ext, \
                                       scale_min=scmin, \
                                       scale_max=scmax)
    plt_clean = pylab.imshow(image_clean_scaled, aspect='equal')
    pylab.title('Clean')

    #Plot cut of the LACosmic-cleaned image
    pylab.subplot(3,2,6)
    image_clean_cut = img_scale.log(image_clean_ext[175:275,175:275], \
                                    scale_min=scmin, scale_max=scmax)
    plt_clean_cut = pylab.imshow(image_clean_cut, aspect='equal')
    pylab.title('Clean')
    image_clean.close()

    if outfilename == 'Default':
        pylab.savefig(filename.split('.fits')[0] + '.png')
    else:
        pylab.savefig(outfilename)
    pylab.close()
    pylab.ion()


#-------------------------------------------------------------------------------#

def define_lacosmic(path_to_lacos_im=''):
    """Moves to ``STSDAS`` package and defines ``LACOS_IM`` as an
    ``iraf`` task.

    Parameters
    -----------
    path_to_lacos_im : string
        Your path to ``lacos_im.cl``.
        If left blank, assume Current Working Directory.
        #By default, reads from lacos_setup

    Notes
    -----
    The IRAF way is
        
        task lacos_im = /path/lacos_im.cl
    """
    iraf.stsdas()
    iraf.task(lacos_im = path_to_lacos_im+'lacos_im.cl')


#-------------------------------------------------------------------------------#

def lacosmic_param_dictionary():
    """Holds the best LACosmic parameters for each filter, primarily
    for white dwarf standard GRW+70. Also works well on other white
    dwarfs and red star P330E.
    If running over a field of stars instead of a single standard, will
    likely need increase 'objlim' param.
    Add filters as needed!

    These are determined using :mod:`run_lacosmic_tester`.

    Parameters:
        nothing

    Returns:
        param_dict : dictionary
            Parameters to be used in LACosmic.
            {'Filter':[sigclip, sigfrac, objlim, niter, sigclip_pf]}

    Outputs:
        nothing
    """
    param_dict = {'F200LP':[5.5, 0.05, 7, 5, 9.5],
                  'F218W':[5.5, 0.3, 2, 5, 9.5],
                  'F225W':[5.0, 0.25, 2, 5, 9.5],
                  'F275W':[5.5, 0.3, 2, 4, 9.5],
                  'F280N':[5.0, 0.3, 2, 5, 9.5],
                  'F300X':[5.0, 0.3, 2, 5, 9.5],
                  'F336W':[6.5, 0.3, 5, 5, 9.5],
                  'F365N':[4.5, 0.3, 2, 5, 9.5],
                  'F390M':[5.0, 0.3, 2, 5, 9.5],
                  'F390W':[5.5, 0.25, 2, 5, 9.5],
                  'F395N':[4.5, 0.3, 5, 5, 9.5],
                  'F410M':[5.0, 0.3, 2, 5, 9.5],
                  'F438W':[5.0, 0.3, 2, 5, 9.5],
                  'F343N':[5.0, 0.3, 2, 5, 9.5],
                  'F373N':[5.0, 0.3, 2, 4, 9.5],
                  'F467M':[5.0, 0.3, 2, 5, 9.5],
                  'F469N':[4.5, 0.3, 5, 5, 9.5],
                  'F475W':[5.0, 0.3, 2, 5, 9.5],
                  'F502N':[5.0, 0.3, 2, 5, 9.5],
                  'F547M':[6.5, 0.3, 2, 5, 9.5],
                  'F555W':[4.5, 0.3, 5, 5, 9.5],
                  'F606W':[5.0, 0.3, 2, 5, 9.5],
                  'F631N':[4.5, 0.3, 5, 5, 9.5],
                  'F645N':[4.5, 0.3, 5, 5, 9.5],
                  'F656N':[4.5, 0.3, 5, 5, 9.5],
                  'F657N':[4.5, 0.3, 5, 5, 9.5],
                  'F658N':[4.5, 0.3, 5, 5, 9.5],
                  'F665N':[4.5, 0.3, 5, 5, 9.5],
                  'F673N':[4.5, 0.3, 5, 5, 9.5],
                  'F680N':[4.5, 0.3, 5, 5, 9.5],
                  'F689M':[8.5, 0.3, 5, 5, 9.5],
                  'F763M':[5.0, 0.3, 5, 5, 9.5],
                  'F775W':[5.5, 0.3, 5, 5, 9.5],
                  'F814W':[5.5, 0.3, 5, 5, 9.5],
                  'F845M':[5.0, 0.3, 5, 5, 9.5],
                  'F850LP':[7.5, 0.3, 2, 5, 9.5]}

    return param_dict


#-------------------------------------------------------------------------------#

def sort_files(origin='', dest='', keep_masks = True, \
               temp_folder=False):
    """Moves clean and mask FITS images and their PNGs into their own
    subdirectories, `flt_cleans`., `flt_masks`, and `png_masks_cleans`.

    Parameters
    ----------
    origin : string
        Path to where the mask and clean FLTs and the PNGs are located.
        If left blank, assume Current Working Directory.
    dest : string
        Path where you want the directories to go. (Usually will want
        origin and dest to match). If left blank, assume
        Current Working Directory.
    keep_masks : {True, False}
        True by default. If False, delete all the mask files.
    temp_folder : {True, False}
        False by default. Switch on if want the clean files placed
        in `flt_cleans/temp_lacos/`.

    """
    if temp_folder:
        temp_folder_name = '/temp_lacos'

    else:
        temp_folder_name = ''

    # Sort CLEAN.FITS files.
    move_files(origin + '*clean.fits', dest + 'flt_cleans' + temp_folder_name)

    # Sort PNG files.
    move_files(origin + '*png', dest + 'png_masks_cleans')

    # Sort MASK.FITS files.
    if keep_masks:
        move_files(origin + '*mask.fits', dest + 'flt_masks')

    elif not keep_masks:
        for mask in glob.glob(origin + '*mask.fits'):
            os.remove(mask)


#-------------------------------------------------------------------------------#

def run_lacosmic(filename, sigclip, sigfrac, objlim, niter, sigclip_pf):
    """Runs ``IRAF/LACosmic`` over an FLT file.

    Parameters:
        filename : string
            Name of the FITS file, including the path.
        sigclip : float
            Detection limit for cosmic rays.
        sigfrac : float
            Detection limit for adjacent pixels.
        objlim : int
            Max number of objects desired in image.
        niter : int
            Number of iterations of cosmic ray finder.
        sigclip_pf : float
            Detection limit for cosmic rays in Post-Flashed images.
            Set to 0.0 if no Post-Flashed data.

    Returns:
        nothing

    Outputs:
        ``IRAF/LACosmic`` cleaned FITS file,
        ``<file rootname>.clean.fits``.
    """
    filename = str(filename)
    sigclip = float(sigclip)
    sigfrac = float(sigfrac)
    objlim = int(objlim)
    niter = int(niter)
    sigclip_pf = float(sigclip_pf)

    # Read the header for whether the image is post-flashed.
    fits_file = fits.open(filename)
    flshcorr = fits_file[0].header['FLSHCORR']
    fits_file.close()

    if sigclip_pf == 0.0 or flshcorr == 'OMIT':
        sigclip = sigclip
        print 'FLSHCORR set to OMIT.'
    elif flshcorr == 'COMPLETE':
        sigclip = sigclip_pf
        print 'FLSHCORR set to COMPLETE.'
    iraf.lacos_im(filename+'[1]', \
                  filename.split('.fits')[0]+'.clean.fits', \
                  filename.split('.fits')[0]+'.mask.fits', \
                  gain=1.5, \
                  readn=3.0, \
                  sigclip=sigclip, \
                  sigfrac=sigfrac, \
                  objlim=objlim, \
                  niter=niter)


#-------------------------------------------------------------------------------#
# Main controller.
#-------------------------------------------------------------------------------#

def run_lacosmic_main(origin='', dest='', path_to_lacos_im='', \
                      temp_folder=False, create_png=True):
    """Main to run lacosmic suite.

    Parameters
    ----------
    origin : string
        Path to where FLTs are located.
        If left blank, assume Current Working Directory.
    dest : string
        Path where you want the output directories to go. (Usually
        will want origin and dest to match). If left blank,
        assume Current Working Directory.
    path_to_lacos_im : string
        Your path to ``lacos_im.cl``.
        If left blank, assume Current Working Directory.
    temp_folder : {True, False}
        False by default. Switch on if want the clean files placed
        in `flt_cleans/lacos_temp/`.
    create_png : {True, False}
        True by default. Switch off if do not want a diagnostic PNG.

    Outputs
    -------
    ``IRAF/LACosmic`` cleaned FITS files,
    ``<file rootname>.clean.fits``.
    `IRAF/LACosmic`` mask FITS files,
    ``<file rootname>.mask.fits``.
    PNG files, ``<file rootname>.png``.
    """
    param_dict = lacosmic_param_dictionary()
    fits_list = glob.glob(origin + '*fl*.fits')
    filt = get_keyval(filename=fits_list[0], keyword='filter')
    print "PATH TO LACOS_IM:", path_to_lacos_im
    define_lacosmic(path_to_lacos_im)

    # Run LACOSMIC.
    for fits in fits_list:
        if filt not in param_dict.keys():
            print "Filter not in Param Dictionary. Using default values."
            if 'N' in filt:
                sigclip = 4.5
                objlim = 5
            else:
                sigclip = 5.0
                objlim = 2
            sigfrac = 0.3
            niter = 3
            sigclip_pf = 9.5

        else:
            sigclip = param_dict[filt][0]
            sigfrac = param_dict[filt][1]
            objlim = param_dict[filt][2]
            niter = param_dict[filt][3]
            sigclip_pf = param_dict[filt][4]

        run_lacosmic(fits, sigclip, sigfrac, objlim, niter, sigclip_pf)
        if create_png:
            create_images_png(fits)

    # Finally organize output files.
    sort_files(origin=origin, dest=dest, keep_masks=True, \
               temp_folder=temp_folder)

#-------------------------------------------------------------------------------# 

if __name__ == '__main__':
    paths = set_paths()

    run_lacosmic_main(origin='', \
                      dest='', \
                      path_to_lacos_im=paths['lacos_im']+'/', \
                      temp_folder=False)

    print "Finished at last."
