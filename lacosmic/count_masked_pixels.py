#! /usr/bin/env python

"""Counts the masked pixels in `*flt.mask.fits`, which is output from
    `LACOSMIC`.

Author:

    C.M. Gosmeyer, Aug. 2014
    
Use:

    >>> python count_masked_pixels.py
    
Outputs: 

    ascii file. `<filter>_mask_counts.dat`.
    The number of masked pixels in each mask image.
    
Notes:

    Original git history in 'detectors/wfc3_contam/count_masked_pixels.py'.
    
Updates:

    Perhaps include this in the LACOSMIC suite, to be included with 
    the other outputs.   
"""

import glob
import pylab
from astropy.io import fits, ascii

from set_paths import set_paths


#-------------------------------------------------------------------------------#

def count_masked_pixels(orig='', dest='', filt=''):
    """Counts the number of masked pixels (=1) in `*flt.mask.fits` 
    files.
    
    Parameters
    ----------
    orig : string
        Path to mask files.
    dest : string
        Path to where you want output file.
    filt : string
        Name of the filter.
    
    Outputs
    -------
    ascii file. `<filter>_mask_counts.dat`.
    The number of masked pixels in each mask image.
    """
    print orig
    mask_list = glob.glob(os.path.join(orig, '*mask.fits'))
    print mask_list
    
    mask_counts_list = []
    date_list = []
    
    # Count masked pixels in each mask image.
    for mask in mask_list:
        hdulist = fits.open(mask)
        header0 = hdulist[0].header
        data0 = hdulist[0].data
        
        date = header0['EXPSTART']
        
        mask_pixel_count = 0
        for row in data0:
            for pixel in row:
                if pixel == 1:
                    mask_pixel_count += 1
        
        hdulist.close()
        mask_counts_list.append(mask_pixel_count)
        date_list.append(date)
        print mask, mask_pixel_count, date
        
    # Write masked pixel counts to file.
    tt = {'#Filename':mask_list, 'Mask_Counts[pixels]':mask_counts_list, 'Date':date_list}
    
    ascii.write(tt, dest + filt + '_mask_counts.dat', \
                names=['#Filename', 'Mask_Counts[pixels]', 'Date'])

    # Plot the pixel counts vs time.
    pylab.ioff()
    fig=pylab.figure(figsize=(13.5,9.5))    

    pylab.scatter(date_list, mask_counts_list)
    pylab.xlabel('MJD', fontsize=14, weight='bold')
    pylab.ylabel('Number Masked Pixels', fontsize=14, weight='bold')
    pylab.annotate('Post-Flashing Begun',[0.65,0.9],xycoords='axes fraction',fontname='monospace',\
                   size='large',color='r')
    pylab.annotate(filt,[0.03,0.9],xycoords='axes fraction',fontname='monospace',size='large',weight='bold')
    pylab.axvline(56232, color='r', ls='--', linewidth=2)
    pylab.savefig(dest + filt + '_mask_counts.png')
    pylab.close()
    pylab.ion()
 
 
#-------------------------------------------------------------------------------#
 
def parse_args():
    """Parses command line arguments.
        
    Returns
    -------
    args : object
        Containing the image and destination arguments.
            
    """

    orig_help = 'Path to filter dirs containing *mask.fits files.'
    dest_help = 'Destination path for out plots.'
    filt_help = 'Name of filter dir to run over. By default runs over all in Origin.'
        
    parser = argparse.ArgumentParser()
    parser.add_argument('--orig', dest='orig',
                        action='store', type=str, required=True,
                        help=orig_help, default='')
        
    parser.add_argument('--dest', dest='dest',
                        action='store', type=str, required=True,
                        help=dest_help, default='')
                        
    parser.add_argument('--filt', dest='filt',
                        action='store', type=str, required=False,
                        help=filt_help)
    args = parser.parse_args()
     
        
    return args
 
#-------------------------------------------------------------------------------#    
# The main.
#-------------------------------------------------------------------------------#

def main_count_masked_pixels():
    """
    """
    
    args = parse_args()
    
    orig = args.orig
    dest = args.dest
    #filt = args.filt
    
    if filt == None:
        filters = glob.glob(orig + '/F*')
    else:
        filters = list(filt)
        
    for filt in filters:    
        count_masked_pixels(orig, dest, filt)
        
if __name__ == '__main__':

    main_count_masked_pixels()