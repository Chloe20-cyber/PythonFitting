#!/usr/bin/env python


specIdat = 'Source8.dat'
specIdat = 'HotSpot.dat'

order = 0

#=============================================================================#
import os, sys, shutil
import math as m
import numpy as np
from mpfit import mpfit
import scipy.optimize as op
import pylab as pl
import matplotlib as mpl
from numpy import nanmedian
from numpy import nanmean


#-----------------------------------------------------------------------------#
def main():

    # Read in the spectrum
    specIArr = np.loadtxt(specIdat, dtype="float64", unpack=True)
    specIArr[0] /=1e9
     
    # Fit the spectrum
    retMatrix = fit_spec_poly5(specIArr[0], specIArr[1], specIArr[4], order)
    p = retMatrix[0]
    chiSq = retMatrix[1]
    chiSqRed = chiSq/(len(specIArr[0])-len(p)-1)
    print("CHISQ:", retMatrix[1])
    print("CHISQred:", retMatrix[1]/(len(specIArr[0])-len(p)-1))
    print("P:", retMatrix[1])

    for e in retMatrix:
        print(e)

    # Plot the model spectrum
    plot_spec_poly5(p, specIArr[0], specIArr[1], specIArr[4])


#-----------------------------------------------------------------------------#
def fit_spec_poly5(xData, yData, dyData, order=5):

    xData = np.array(xData, dtype='f8')
    yData = np.array(yData, dtype='f8')
    
    # Estimate starting coefficients
    C1 = nanmean(np.diff(yData)) / nanmedian(np.diff(xData))
    ind = int(np.median(np.where(~np.isnan(yData))))
    C0 = yData[ind] - (C1 * xData[ind])
#   if order<1:
#       order=1
    p0 = [0.0, 0.0, 0.0, 0.0, C1, C0]

    # Set the order
    p0 = p0[(-order-1):]

    def chisq(p, x, y):
        return np.sum( ((poly5(p)(x) - y)/ dyData)**2.0 )

    # Use minimize to perform the fit
    return op.fmin(chisq, p0, args=(xData, yData), full_output=1,
                        disp=False, retall=False)


#-----------------------------------------------------------------------------#
def plot_spec_poly5(p, x, y, dy):

    # Make the model curve
    nSamples = 100
    dXSamp = (np.max(x) - np.min(x)) / nSamples
    iLst = np.arange(nSamples, dtype='float32')
    xSamp = np.min(x) + dXSamp * iLst
    ySamp = poly5(p)(xSamp)

    # Plot the channels and fit
    fig = pl.figure()
    fig.set_size_inches([8,4])
    ax = fig.add_subplot(1,1,1)
    ax.set_xlabel('Frequency (GHz)')
    ax.set_ylabel('Amplitude (Jy)')
    ax.plot(xSamp, ySamp, color='k',marker='None',mfc='w',
            mec='g', ms=10, label='none', lw=1.0)
    ax.errorbar(x=x , y=y, yerr=dy, mfc='none', ms=4, fmt='D', ecolor='grey',
                elinewidth=1.0, capsize=2)
    fig.show()
    input("Press <Return> to finish:")

    
#-----------------------------------------------------------------------------
def poly5(p):
    """
    Function which returns another function to evaluate a polynomial.
    The subfunction can be accessed via 'argument unpacking' like so:
    'y = poly5(p)(*x)', where x is a vector of X values and p is a
    vector of polynomial coefficients.
    """

    # Fill out the vector to length 6
    p = np.append(np.zeros((6-len(p))), p)
    
    def rfunc(x):
        y = p[0]*x**5.0 + p[1]*x**4.0 + p[2]*x**3.0 + p[3]*x**2.0 + p[4]*x +p[5]
        return y
    return rfunc


#-----------------------------------------------------------------------------#
main()
