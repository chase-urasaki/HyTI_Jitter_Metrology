import configobj as co
from validate  import Validator
import pprint
from matplotlib import pyplot as plt
import ipdb
import numpy as np

def robust_sigma(in_y, zero=0):
   """
   Calculate a resistant estimate of the dispersion of
   a distribution. For an uncontaminated distribution,
   this is identical to the standard deviation.

   Use the median absolute deviation as the initial
   estimate, then weight points using Tukey Biweight.
   See, for example, Understanding Robust and
   Exploratory Data Analysis, by Hoaglin, Mosteller
   and Tukey, John Wiley and Sons, 1983.

   .. note:: ROBUST_SIGMA routine from IDL ASTROLIB.

   :History:
       * H Freudenreich, STX, 8/90
       * Replace MED call with MEDIAN(/EVEN), W. Landsman, December 2001
       * Converted to Python by P. L. Lim, 11/2009

   Examples
   --------
   >>> result = robust_sigma(in_y, zero=1)

   Parameters
   ----------
   in_y: array_like
       Vector of quantity for which the dispersion is
       to be calculated

   zero: int
       If set, the dispersion is calculated w.r.t. 0.0
       rather than the central value of the vector. If
       Y is a vector of residuals, this should be set.

   Returns
   -------
   out_val: float
       Dispersion value. If failed, returns -1.

   """
   # Flatten array
   y = in_y.reshape(in_y.size, )

   eps = 1.0E-20
   c1 = 0.6745
   c2 = 0.80
   c3 = 6.0
   c4 = 5.0
   c_err = -1.0
   min_points = 3

   if zero:
       y0 = 0.0
   else:
       y0 = np.median(y)

   dy    = y - y0
   del_y = abs( dy )

   # First, the median absolute deviation MAD about the median:

   mad = np.median( del_y ) / c1

   # If the MAD=0, try the MEAN absolute deviation:
   if mad < eps:
       mad = np.mean( del_y ) / c2
   if mad < eps:
       return 0.0

   # Now the biweighted value:
   u  = dy / (c3 * mad)
   uu = u*u
   q  = np.where(uu <= 1.0)
   count = len(q[0])
   if count < min_points:
       #print 'ROBUST_SIGMA: This distribution is TOO WEIRD! Returning', c_err
       return c_err

   numerator = np.sum( (y[q]-y0)**2.0 * (1.0-uu[q])**4.0 )
   n    = y.size
   den1 = np.sum( (1.0-uu[q]) * (1.0-c4*uu[q]) )
   siggma = n * numerator / ( den1 * (den1 - 1.0) )

   if siggma > 0:
       out_val = np.sqrt( siggma )
   else:
       out_val = 0.0

   return out_val


class Plotter:
    def __init__(self):
        self.fig = plt.figure()
        self.ax2 = self.fig.add_subplot(1, 1, 1)

        self.line, = self.ax2.plot([],[], marker='o', color='red', ms=10)
        self.ax2.axvline(0, color="black", alpha = 0.5)
        self.ax2.axhline(0, color="black", alpha = 0.5)
        self.maxval = 0.015
        self.ax2.set_xlim(-self.maxval, self.maxval)
        self.ax2.set_ylim(-self.maxval, self.maxval)
        self.ax2.set_xlabel("Offset [meters]")
        self.ax2.set_ylabel("Offset [meters]")
        self.ax2.set_aspect('equal', adjustable='box')
        self.ax2.set_title("")
        #self.text = self.ax2.text(-0.2*self.maxval,0.8*self.maxval, "")

        self.fig.canvas.draw()   # note that the first draw comes before setting data
        plt.show(block=False)


    def update(self, xval, yval, sumval):
        print(xval, yval, sumval)
        self.line.set_data(xval, yval)
        self.update_text(sumval)
        print, xval, yval,
        # redraw everything
        self.fig.canvas.draw()
        self.fig.canvas.flush_events()
        pass

    def update_text(self, sumval):
        #self.text.remove()
        tx = "Sum: "+"%.4f"%sumval
        if sumval>4.0:
            #self.text = self.ax2.text(-0.2*self.maxval, 0.8*self.maxval, tx, color="Red")
            self.ax2.set_title(tx, color="Red")
        else:
            #self.text = self.ax2.text(-0.2*self.maxval, 0.8*self.maxval, tx, color="Black")
            self.ax2.set_title(tx, color="Black")
        pass

def validate_configfile(ini, spec):
    ''' -----------------------------------------------------------------------
    ----------------------------------------------------------------------- '''
    # Parse config file provided by user
    config = co.ConfigObj( ini, configspec = spec)
    # Instanciate the validator class
    val = Validator()
    # Check if the config file match the requirement of the spec file
    res = config.validate(val, preserve_errors = True)
    # If the config file pass the validor test, return the config file
    if res is True: return config
    # If the config file failed to pass the validator test:
    else:
        # Prepare message for the user
        msg  = "Warning: "
        msg += "the config file does not match spec file requirements."
        # Print warning message for the user
        print(msg)
        # Print name of all problematic items.
        for item in co.flatten_errors(config, res): print(item)
        # Raise a Value Error
        raise ValueError('Configuration file corrupted.')

