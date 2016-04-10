import numpy as np

def fwhm(x,y):
    maxVal = np.max(y)
    maxVal50 = 0.5*maxVal
    print "Max: " + str(maxVal)

    biggerCondition = [a > maxVal50 for a in y]

    changePoints = []
    freqPoints = []
    
    for k in range(len(biggerCondition)-1):
        if biggerCondition[k+1] != biggerCondition[k]:
            changePoints.append(k)

    if len(changePoints) > 2:
        print "WARNING: THE FWHM IS LIKELY TO GIVE INCORRECT VALUES"

    #interpolate between points.
    
    for k in changePoints:
        slope = (y[k] - y[k-1])/(x[k] - x[k-1])
        dx = (maxVal50 - y[k-1])/slope
        freq = x[k-1] + dx
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
