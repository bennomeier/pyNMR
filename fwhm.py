"""# -*- coding: utf-8 -*- 
This module provides
- fwhm()
functionality to get the full width at half maximum.

- main()
A test of fwhm() using a Gaussian.
"""


import numpy as np

def fwhm(x,y):
    """Calulate the FWHM for a set of x and y values.

    The FWHM is returned in the same units as those of x."""
    
    maxVal = np.max(y)
    maxVal50 = 0.5*maxVal

    #this is to detect if there are multiple values
    biggerCondition = [a > maxVal50 for a in y]

    changePoints = []
    xPoints = []
    
    for k in range(len(biggerCondition)-1):
        if biggerCondition[k+1] != biggerCondition[k]:
            changePoints.append(k)

    assert len(changePoints) == 2, "More than two crossings of the threshold found."
            
    for k in changePoints:
        # do a polyfit
        # with the points before and after the point where the change occurs.
        
        # note that here we are fitting the x values as a function of the y values.
        # then we can use the polynom to compute the value of x at the threshold, i.e. at maxVal50.

        yPolyFit = x[k-1:k+2]
        xPolyFit = y[k-1:k+2]

        z = np.polyfit(xPolyFit,yPolyFit,2)
        p = np.poly1d(z)

        xThis = p(maxVal50)
        xPoints.append(xThis)


    if len(xPoints) == 2:
        linewidth = xPoints[1] - xPoints[0]
    else:
        linewidth = None
        print(sorted(xPoints))
    
    return linewidth

def main():
    """Use a Gaussian to test the fwhm() routine"""
    
    print("TEST\n============================")
    x = np.linspace(-10,10,100)
    sigma = 2
    y = 3.1*np.exp(-x**2/(2*sigma**2))
    fwhmVal = fwhm(x,y)

    print("The following two values should match closely.")
    print("Computed value: " + str(fwhmVal))
    print("Analytical result for the Gaussian: " + str(2*np.sqrt(2*np.log(2))*2))

if __name__ == "__main__":
    main()
