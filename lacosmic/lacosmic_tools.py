"""
Module containing general functions for the "lacosmic" wrapper.

Author:

    C.M. Gosmeyer
"""

import glob
import os
import shutil

from astropy.io import fits

#-------------------------------------------------------------------------------# 

def get_keyval(filename='', keyword='', ext=0):
    """

    Parameters
    ----------
    filename : string
        Name of file you want filter name of.
        If '', assumes you want to glob over directory
        in 'origin'. 
    keyword : string
        Header keyword whose key value you want.
    ext : integer
        Extension in which to search for keyword.
            
    Returns
    -------
    keyvalue : string
        The key value of the given header keyword. 

    Notes
    -----
    This assumes all the FITS in the directory are of the same filter.

    """
    if filename != '' or filename[len(filename)-4:] == 'fits':  ## how slice just the last few?
        fits_file = fits.open(filename)
    else:
        print "No filename given!"
        return None
    
    try: 
        keyvalue = fits_file[0].header[keyword]
        fits_file.close()
        return keyvalue
        
    except:
        print "Keyword does not exist in the extension " + str(ext)
        return None 

#-------------------------------------------------------------------------------# 

def move_files(glob_search, destination_dir):
    """Moves files with 'glob_search' commonality to the directory
    'destination_dir'.
	
    Parameters
    ---------
    glob_search : list of strings
        Commonality between files you wish moved, e.g., 'png'.
        Type what you normally would for a glob.glob search.
        Assumes each consecutive item listed is destinated for
        a subdirectory of the previous.
    destination_dir : list of strings
        Destination directory.
        Assumes each consecutive item is a new subdirectory of
        the previous.
    
    Notes
    -----
    The length of both parameters must match! 
    """
    # Make sure inputs are lists before proceding, even if 
    # they are only singletons.
    if type(glob_search) != type([]):
        glob_search = [glob_search]
    if type(destination_dir) != type([]):
        destination_dir = [destination_dir]
	
    for i in range(len(destination_dir)):
        file_list = glob.glob(glob_search[i])  #'*' + glob_search[i])
        print i
        if file_list != []:
            #if more than one desintation_dir listed:
            if len(destination_dir) > 1 and i >= 1:
                appended_destination_dir = destination_dir[i-1] + '/' + \
			        destination_dir[i] #(destination_dir[i]).split('/')[len(destination_dir)-1]
                if not os.path.exists(appended_destination_dir):
                    os.makedirs(appended_destination_dir)
                for file in file_list:
                    shutil.move(str(file), appended_destination_dir)
	                
            # If lists singletons:
            else:
                if not os.path.exists(destination_dir[i]):
                    os.makedirs(destination_dir[i])
                for file in file_list:
                    shutil.move(str(file), destination_dir[i])