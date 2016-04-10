from numpy import pi, sqrt
from scipy.constants import mu_0

import sys
sys.path.append("/Users/benno/Dropbox/Software/python/")
import gammaList as gL

gamma = gL.get("1H")

Q = 500
P = 100
r = 2.5e-3
h = 3e-2

V = pi*r**2*h

omega = 2*pi*500e6


#An estimate of the B1 strength. See Slichter's book (Chapter 2) for a derivation.
B1 = sqrt(mu_0*Q*P/(2*omega*V))
print "B1 in Hz is: ", gamma*B1/(2*pi)
print "in seconds this is: ", 2*pi/(gamma*B1)


