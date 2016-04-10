from scipy.constants import k, hbar
import sys
sys.path.append("/Users/benno/Dropbox/Software/python")
import gammaList as gL
import numpy as np

#  P = N \left ( \frac{2}{1 + \exp ( - \Delta E / k_B T)} - 1 \right )

def polarization(nucleus, Temperature, B):
    """This function returns the thermal polarization at a given temperature.
    If nucleus equals "E", then the electron gamma is chosen.
    Arguments:
    - `nucleus`: String describing the nucleus, e.g., "1H", "13C" or "E" for electrons
    - `Temperature`: Temperature in Kelvin
    - `Field`: Magnetic Field in Tesla
    """
    gamma = gL.get(nucleus)
        
    DE = hbar*gamma*B
    polarization = 2/(1 + np.exp(- DE/(k*Temperature))) -1
    return polarization

if __name__ == "__main__":
    print "13C polarization at 3.35 Tesla, 1.5K: ", polarization("13C", 1.5, 3.35)
    print "13C polarization at 9 Tesla, 300K: ", polarization("13C", 300, 9)
    print "Ratio between those: ", polarization("13C", 1, 3)/polarization("13C", 300, 9)
