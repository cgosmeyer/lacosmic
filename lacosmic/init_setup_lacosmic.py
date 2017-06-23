#! /usr/bin/env python

"""Sets the path to the package containing all the lacosmic scripts.
Places the path into a dictionary in ``set_paths.py`` and reads 
``img_scale.py`` from the internet into a file.

*Run this script before all others!*

This only needs be run once when you first clone the repo. If the 
location of the ``lacosmic`` directory is changed, then run again.

Author:

    C.M. Gosmeyer, Sep. 2015
    
Use:

    Be in the ``lacosmic`` directory.

    >>> python init_setup_lacosmic.py

Outputs:

    'set_paths.py'
    'img_scale.py'
"""


import os
import time
import urllib

if __name__ == '__main__':
    cwd = os.getcwd() + '/'
    print "The 'lacosmic' package is located at"
    print cwd
    print "Writing this path in set_paths.py."

    with open("set_paths.py", "w") as paths_file:
        paths_file.write('"""\n')
        paths_file.write('    Path to `detectors_tools/lacosmic`.\n')
        paths_file.write('    File created by init_setup_lacosmic.py on date\n')
        paths_file.write('    ' + time.strftime("%d/%m/%Y") + '\n')
        paths_file.write('"""\n')
        paths_file.write('\n')
        paths_file.write('def set_paths():\n')
        paths_file.write('    """Sets paths for lacosmic scripts"""\n')
        paths_file.write('    paths = {"lacos_im":"' + cwd + '"}\n')
        paths_file.write('    return paths\n')
    print ""
    

    print "Writing img_scale.py from internet."

    img_scale_url = urllib.urlopen("http://dept.astro.lsa.umich.edu/~msshin/science/code/Python_fits_image/img_scale.py")
    with open("img_scale.py", "w") as img_scale_file:
        img_scale_file.write(img_scale_url.read())


    print ""
    print "Lacosmic setup complete."
    print ""
    print "You should have two new files in 'detector_tools/lacosmic':"
    print "    set_paths.py"
    print "    img_scale.py"