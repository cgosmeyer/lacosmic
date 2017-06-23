LACosmic Wrapper
================

Author: C. Gosmeyer, 2015

Last Updated: 29 Sep. 2015


About
-----

The script `run_lacosmic.py` wraps the IRAF task `LACosmic`, written by Pieter G. van Dokkum (http://www.astro.yale.edu/dokkum/lacosmic/). The wrapper is tweaked specifically for Hubble WFC3/UVIS FITS-format images of single white dwarf stars. If you use it for other targets/instruments, expect some experimentation!

It generates cosmic-ray cleaned FITS (`*clean.fits`) and the cosmic-ray mask FITS 
(`*mask.fits`), and a diagnostic PNG file that displays on a single page 
the original image, the mask, and the cosmic-ray cleaned image.  
It presently assumes the source is at the center (usually true in my white dwarf 
data) so it also displays ‘zoomed-in’ panels of the image center.  Using this PNG you can quickly diagnose whether `LACosmic` did a good job masking the cosmic-rays or did poorly enough that you need adjust parameters and run the script again.

There is, in fact, a Python version, which is faster than IRAF (yes, crazy, I know!).  
But unfortunately it is not smart about how it handles the headers of 
multi-extension FITS. Besides that caveat, the output images of both versions 
look the same in all my tests.  On a distant future day I may fix the Python 
version and incorporate it into the wrapper.

Also included in this package are a script that iterates through different
permutations of parameters so that you can with relative ease find the best
for your WFC3/UVIS data. This script is named `run_lacosmic_tester.py`.

See the doc strings for further information on inputs and outputs for
`run_lacosmic.py` and `run_lacosmic_tester.py`.


Install ‘lacosmic’ Package
---------------------------------

1. git clone the ‘lacosmic’ package to desired location

2. To install the package, type

    > make setup

3. Finally add the PYTHONPATH to your .cshrc file with something like

    # Python paths
    setenv PYTHONPATH ${PYTHONPATH}:/your/path/to/lacosmic/

If the installation went smoothly, you should have the following in
the `lacosmic` directory: 
   `__init__.py`
   `count_masked_pixels.py`
   `init_setup_lacosmic.py`
   `lacos_im.cl`
   `lacosmic_tools.py`
   `run_lacosmic.py`
   `run_lacosmic_tester.py`
   `examples/`


Setup ‘lacosmic’ Sub-Package
----------------------------

Actually, as long as you ran the makefile, you don’t need do anything to setup 
the ‘lacosmic’ sub-package. The ‘make setup’ command runs `init_setup_lacosmic.py`, 
which does the following:

1. Creates ‘set_paths.py’, which just contains a dictionary of the absolute
   path to the directory where you put `lacosmic`. 

2. Creates ‘img_scale.py’, which is written from a script available on the
   internet. I did not write it so I did not include it in the `lacosmic`
   package.

You may, after an initial run, need adjust for your different filters the 
    ``LACosmic`` parameters in the `run_lacosmic.py` function 
    `lacosmic_param_dictionary`. You can find these parameters by your own 
    trial and error or by using an already-built tester, `run_lacosmic_tester.py`.


Run
---

Installation and setup should ideally need be done only once. Now you
are free to run the LACosmic wrapper on a whim. Hooray!

1. To run the bare `run_lacosmic.py`, cd into the directory containing the
   FLTs you want cosmic ray cleaned.  If your PYTHONPATH is correct, then
   you need just do

   > python run_lacosmic.py

2. Wait. For a WFC3/UVIS subarray, it takes 30-40 seconds each. You might speed it 
   up by decreasing the ‘niter’ param. (By default it is set to the highest, 5). 

3. An error-free run should have created the following directories:

   flt_cleans/
   flt_masks/
   png_masks_cleans/   

   Containing, respectively, for each of your original FLTs,

   <rootname>.clean.fits
   <rootname>.mask.fits
   <rootname>.png

   The .clean.fits file is the cleaned FLT with which you want to do your 
   analyses.


4. But first look through all the diagnostic plots in ‘png_masks_cleans’. 
   If you see that LACosmic "blew up" (overflags and masks pixels) on an 
   image, move its clean, mask, and diagnostic plot to a ‘flags’ 
   directory. Then adjust parameters and re-run. You can compare your new
   runs with the old you stored in ‘flags’.

   See the plots in `examples` for good and bad runs. All images of the 
   (post-flashed!) white dwarf GRW+70 in the WFC3/UVIS filter F218W. 

‘good.png’ — Close to what you want to see. Only cosmic rays masked. ‘sigclip’ 
    appropriately high to account for post-flash.
‘center_overflagged.png’ — The star’s center is masked. Try increasing ‘sigclip’
     and ‘objlim’.
‘sigclip_too_low.png’ — Background flagged everywhere! Try increasing ‘sigclip’
     to about 9.5.

   Sometimes LACosmic blows up for no reason, no matter how you adjust the 
   parameters. If you are doing a big batch that spans multiple visits, expect 
   about 5% of your images to do this.  But if more than ~5% are getting over-
   flagged in the PSF or the background, you’ll probably need to toss out this 
   run and start again with adjusted parameters. See Tips Section below.

Tips
—---

LACosmic’s four parameters are
    sigclip : Detection limit for cosmic rays.
    sigfrac : Detection limit for adjacent pixels.
    objlim : Max number of objects desired in image.      
    niter : Number of iterations of cosmic ray finder. 

In general, for the standard white dwarf GRW+70, I use
    sigclip = 5.5 (9.5 if post-flashed)
    sigfrac = .3 (I rarely vary this)
    objlim = 2 or 5 
    niter = 5  (Also rarely vary)

Narrow band filters generally work better with ‘sigclip’ about 4.5.
Long pass filters generally work better with ’sigclip’ > 5.5.

 
If you notice LACosmic is over-flagging pixels

1. Check whether your images are post-flashed. 
   For post-flashed images, you may need bump the 'sigclip' up to near
   10.0. Non-post-flashed images are good around 'sigclip' 5.0, 5.5. 

2. Increase ‘sigclip’ even if not post-flashed.

3. Increase ‘objlim’. 


If you notice it is not flagging /enough/ pixels

1. Decrease ‘objlim’.

2. Decrease ‘sigclip’.

You’ll find that you’re more often over-flagging than under-flagging.

