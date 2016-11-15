import numpy as np
from scipy.constants import mu_0

import sys
import gammaList as gL

gamma = gL.get("1H")

Q = 500
P = 100
r = 2.5e-3
h = 3e-2

V = pi*r**2*h

omega = 2*pi*500e6


#An estimate of the B1 strength. See Slichter's book (Chapter 2) for a derivation.
#B1 = sqrt(mu_0*Q*P/(2*omega*V))
#print "B1 in Hz is: ", gamma*B1/(2*pi)
#print "in seconds this is: ", 2*pi/(gamma*B1)


def getB1Strength(nuc, Q, P, f = 0, B = 0, r = 0, h = 0, V = 0):
    """Calculate B1 Strength and duration of pi/2 pulse.

    - nuc: string specifying the nucleus, e.g., "1H"
    - Q: quality factor 
    - P: power (Watt)
    - f: Larmor Frequency (Hz)
    - B: Magnetic Field (Tesla), only required if f = 0
    - r: radius
    - h: height
    - V: Volume

    If radius is > 0, radius and height are used to calculate the coil volume.

    If radius == 0, the optional argument V is used for the coil volume."""

    gamma = gL.get(nuc)
    
    if r > 0:
        assert h > 0, "non-positive height specified."

        V = np.pi*r**2*h
    else:
        assert V > 0, "neither positive height or radius specified."
        

    if f > 0:
        omega = 2*np.pi*f
    else:
        assert B > 0, "neither positive frequency nor field specified."
        omega = gamma*B

    B1 = np.sqrt(mu_0*Q*P/(2*omega*V))

    print "B1: {:.3f} mT".format(B1*1e3)
    print "B1: {:.3f} kHz".format(gamma*B1 /( 2*pi) / 1000)
    print "pi/2 is: {:.3f} us".format(pi/(2*gamma*B1)*1e6)


def getB1FromPiHalf(tauPiHalf):
    """Calculate B1 from piHalf pulse.

    - tauPiHalf: piHalf pulse in us"""

    print "B1 is: {:.3f} kHz: ".format(1./(4.*tauPiHalf*1e-6) / 1e3)

    

def getPiHalfFromB1(B1):
    """Calculate piHalf pulse duration.

    - B1: B1 in kHz."""

    tauPiHalf = 1 /(4.*B1*1000)
    print "pi/2 is: {:.3f} us".format(tauPiHalf*1e6)
