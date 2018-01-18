import numpy as np

def loessInternal( x, h, xp, yp ):
    w = np.exp( -0.5*( ((x-xp)/(2*h))**2 )/np.sqrt(2*np.pi*h**2) )
    b = np.sum(w*xp)*np.sum(w*yp) - np.sum(w)*np.sum(w*xp*yp)

    b /= np.sum(w*xp)**2 - np.sum(w)*np.sum(w*xp**2)
    a = ( np.sum(w*yp) - b*np.sum(w*xp) )/np.sum(w)

    return a + b*x

def loess(x,y,h):
    """LOESS model free bandwidth reduction.

    See "Data Analysis with Open Source Tools" by P. K. Janert for fdetails.

    Watch out that x and y do not become too small,
    microseconds don't work. h is bandwidth in units of x"""
    out = []
    for k in x:
        out.append( loessInternal(k, h, x, y))
    return out
    

def splitLoess(x, y, sigma, SPLIT):
    x1 = x[:SPLIT]
    y1 = y[:SPLIT]
    
    x2 = x[SPLIT:]
    y2 = y[SPLIT:]
    
    y1Loess = loess(x1, y1, sigma)
    y2Loess = loess(x2, y2, sigma)
    
    return np.concatenate([y1Loess, y2Loess], axis = 0)
