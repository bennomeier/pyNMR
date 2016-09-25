from pylab import *

def loessInternal( x, h, xp, yp ):
    w = exp( -0.5*( ((x-xp)/(2*h))**2 )/sqrt(2*pi*h**2) )
    b = sum(w*xp)*sum(w*yp) - sum(w)*sum(w*xp*yp)

    b /= sum(w*xp)**2 - sum(w)*sum(w*xp**2)
    a = ( sum(w*yp) - b*sum(w*xp) )/sum(w)

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
    
