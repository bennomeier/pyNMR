import numpy as np

def loessInternal( x, h, xp, yp , kernel = "Gaussian"):
    if kernel == "Gaussian":
        w = np.exp( - (x-xp)**2/(2*h**2) )/np.sqrt(2*np.pi*h**2)
    elif kernel == "TriCube":
        w =  (1 - np.abs((x - xp) / h)**3)**3

        w = np.asarray(w)
        low_values_flags = np.abs(xp - x) > h  # Where values are low
        w[low_values_flags] = 0  # All low values set to 0
                
    b = np.sum(w*xp)*np.sum(w*yp) - np.sum(w)*np.sum(w*xp*yp)

    b /= np.sum(w*xp)**2 - np.sum(w)*np.sum(w*xp**2)
    a = ( np.sum(w*yp) - b*np.sum(w*xp) )/np.sum(w)

    return a + b*x

def loess(x,y,h, kernel = "Gaussian"):
    """LOESS model free bandwidth reduction.

    See "Data Analysis with Open Source Tools" by P. K. Janert for fdetails.

    Watch out that x and y do not become too small,
    microseconds don't work. h is bandwidth in units of x"""
    out = []
    for k in x:
        out.append( loessInternal(k, h, x, y, kernel = kernel))
    return np.array(out)
    

def splitLoess(x, y, sigma, SPLIT, kernel = "Gaussian"):
    x1 = x[:SPLIT]
    y1 = y[:SPLIT]
    
    x2 = x[SPLIT:]
    y2 = y[SPLIT:]
    
    y1Loess = loess(x1, y1, sigma, kernel = kernel)
    y2Loess = loess(x2, y2, sigma, kernel = kernel)
    
    return np.concatenate([y1Loess, y2Loess], axis = 0)
