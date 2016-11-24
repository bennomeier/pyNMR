import numpy as np

def fwhm(x,y, silence = False):
    maxVal = np.max(y)
    maxVal50 = 0.5*maxVal

    if not silence:
        print "Max: " + str(maxVal)

    #this is to detect if there are multiple values
    biggerCondition = [a > maxVal50 for a in y]

    changePoints = []
    freqPoints = []
    
    for k in range(len(biggerCondition)-1):
        if biggerCondition[k+1] != biggerCondition[k]:
            changePoints.append(k)

    if len(changePoints) > 2:
        if not silence:
            print "WARNING: THE FWHM IS LIKELY TO GIVE INCORRECT VALUES"

    #interpolate between points.
    print "ChangePoints: ", changePoints
    
    for k in changePoints:
        # do a polyfit
        # with the points before and after the point where the change occurs.
        
        # note that here we are fitting the frequency as a function of the return loss.
        # then we can use the polynom to compute the frequency at returnloss = threshold.

        yPolyFit = x[k-1:k+2]
        xPolyFit = y[k-1:k+2]

        z = np.polyfit(xPolyFit,yPolyFit,2)
        p = np.poly1d(z)

        print p
        freq = p(maxVal50)
        freqPoints.append(freq)


    if len(freqPoints) == 2:
        value = freqPoints[1] - freqPoints[0]
    else:
        value = None
        print sorted(freqPoints)
    
    return value

def main():
    x = np.linspace(-10,10,100)
    sigma = 2
    y = 3.1*np.exp(-x**2/(2*sigma**2))
    print "OK"
    fwhmVal = fwhm(x,y)
    print "FWHM: " + str(fwhmVal)
    print str(2*np.sqrt(2*np.log(2))*2)

if __name__ == "__main__":
    main()
