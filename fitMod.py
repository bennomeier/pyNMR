from __future__ import division
from scipy.optimize import curve_fit
import numpy as np
from scipy.stats import t

from scipy.constants import k, epsilon_0
debye = 3.33564e-30
#import numpy as np

def getError(var_matrix, dof):
    a = 1 - 0.05/2
    factorSE = t.isf(a, dof)
    variance = np.diagonal(var_matrix)
    SE = np.sqrt(variance)
    error = np.abs(SE*factorSE)
    return error


class Model(object):
    """This class can represent any model. A Model is given by its parameters, their names and a functional relationship.
    """

    def __init__(self):
        """
        """
        self.params = np.array()
        self.paramNames = []
        self.model = None
        self.p0 = 0
        self.popt = []
        self.pcov = []

    def fitGeneral(self, x, y, p0, silence = False):
        self.popt, self.pcov = curve_fit(self.model, np.array(x), np.array(y), p0 = p0)

        errors = self.getError(self.pcov, len(x) - len(p0))
        if not silence:
            for k in range(len(self.popt)):
                print self.paramNames[k] + ": " + str(self.popt[k])  + "(" + str(errors[k]) + ")"


    def getError(self,var_matrix, dof):
        a = 1 - 0.05/2
        factorSE = t.isf(a, dof)
        variance = np.diagonal(var_matrix)
        SE = np.sqrt(variance)
        error = np.abs(SE*factorSE)
        return error

class t1InversionRecovery(Model):
    """This class represents the T1 Inversion Recovery Model."""

    def __init__(self, include_non_perfect_inversion=False):
        if include_non_perfect_inversion:
            self.paramNames = ["A", "T1", "k"]
            self.model = self.model1
        else:
            self.paramNames = ["A", "T1"]
            self.model = self.model2

    def model1(self, t, A, T1, k):
        """A Model for fitting T1 inversion recovery measurements with imperfect inversion
        This does not look very correct
        """
        return A*(1 - k*np.exp(-t/float(T1)))

    def model2(self, t, A, T1):
        """A Model for fitting T1 inversion recovery"""
        return A*(1 - 2*np.exp(-t/float(T1)))

    def fit(self, x, y, p0 = []):
        if len(p0) == 0:
            if len(self.paramNames) == 2:
                p0 = [np.max(y), np.max(x)/2]
            elif len(self.paramNames) == 3:
                p0 = [np.max(y), np.max(x)/2, 2]
            print "Parameters have been estimated: ", p0
        self.p0 = self.fitGeneral(x,y,p0)




class polarizability(Model):
    """This class represents the classical polarizability model alpha + mu^2 / (3*k*T)
    """

    def __init__(self, unit1="volume", unit2 = "Debye", fixDipole = 0):
        self.unit1 = unit1
        self.unit2 = unit2

        if fixDipole > 0:
            #fix the dipole moment at p0
            self.paramNames = ["alpha"]
            self.fixDipole = fixDipole
            self.model = self.model1
        else:
            self.paramNames = ["p0", "alpha"]
            self.model = self.model2

    def model1(self, t, alpha):
        if self.unit2 == "SI":
            dipole = self.fixDipole
        elif self.unit2 == "Debye":
            dipole = self.fixDipole*debye

        if self.unit1 == "SI":
            conversionFactor = 1
        else:
            conversionFactor = 1/(4*np.pi*epsilon_0)*1e30


        retVal = alpha + dipole**2/(3*k*t)*conversionFactor
        return retVal

    def model2(self, t, p0, alpha):
        if self.unit2 == "SI":
            dipole = p0
        elif self.unit2 == "Debye":
            dipole = p0*debye

        if self.unit1 == "SI":
            conversionFactor = 1
        else:
            conversionFactor = 1/(4*np.pi*epsilon_0)*1e30

        retVal = alpha + dipole**2/(3*k*t)*conversionFactor
        return retVal

    def fit(self, x,y, p0 = []):
        if len(p0) == 0:
            if len(self.paramNames) == 2:
                p0 = [1, np.min(y)]
            elif len(self.paramNames) == 1:
                p0 = [np.min(y)]
            print "Parameters have been estimated: ", p0
        self.fitGeneral(x,y, p0)




class capacitance(Model):
    """This class represents the capacitance Model C = C0 + CH2O*exp(-t/tau)
    """
    def __init__(self):
        self.paramNames = ["C0", "CH2O", "tau"]
        self.model = self.model1

    def model1(self, t, C0, CH2O, tau):
        return C0 + CH2O*np.exp(-t/float(tau))

    def fit(self, x,y, p0 = []):
        self.fitGeneral(x,y, p0)



class nutationCurve(Model):
    """This class represents the T1 Inversion Recovery Model."""
    def __init__(self):
        """This is the init routine
        """
        self.paramNames = ["A", "tau"]
        self.model = self.nutationCurve

    def nutationCurve(self, t, A, tau):
        """A model for fitting a perfect nutation"""
        return A*np.sin(np.pi/(2*tau)*t)

    def fit(self, x, y, p0 = []):
        if len(p0) == 0:
            if len(self.paramNames) == 2:
                A = np.max(y)
                #estimate piHalf pulse duration as time of maximum.
                tau = 10# x(y.index(A))
                p0 = [A, tau]
            elif len(self.paramNames) == 3:#incl. offset
                A = np.max(y)
                tau = 10
                offset = y[-1]
                p0 = [A, tau, offset]
            print "Parameters have been estimated: ", p0
        self.p0 = self.fitGeneral(x,y,p0)
        return self.p0

class exponentialDecay(Model):
    """This class represents a simple exponential decay."""
    def __init__(self, offset=False):
        """This is the init routine
        """

        print "We're going to the zoo."
        self.outputString = ""

        print "Offset value is: ", offset
        if offset == False:
            self.paramNames = ["A", "tau"]
            self.model = self.exponentialDecay
        else:
            self.paramNames = ["A", "tau", "offset"]
            self.model = self.exponentialDecayOffset
        print self.paramNames

    def exponentialDecay(self, t, A, tau):
        """A model for fitting an exponential Decay"""
        return A*np.exp(-t/tau)

    def exponentialDecayOffset(self, t, A, tau, offset):
        """A model for fitting an exponential Decay"""
        return A*np.exp(-t/tau)+offset

    def fit(self, x, y, p0 = []):
        if len(p0) == 0:
            if len(self.paramNames) == 2:
                A = np.max(y)
                #estimate piHalf pulse duration as time of maximum.
                tau = 10# x(y.index(A))
                p0 = [A, tau]
            elif len(self.paramNames) == 3:
                A = np.max(y)
                tau = 30
                offset = y[-1]
                p0 = [A, tau, offset]
            print "Parameters have been estimated: ", p0

        self.p0 = self.fitGeneral(x,y,p0)


class secondOrder2(Model):
    """This class represents second order dynamics, according to eq. 7 in paper on kinetics in H2O@C60
    It implents the solution of the following equation:
    DSolve[y'[x] == - 2 k (y[x] - f0)^2, y[x], x]

    The parameters are A, B, k and the fit equation is B + A/(1 + k*t)
    """
    #self.outputString = Model.outputString

    def __init__(self):
        self.paramNames = ["A", "B","k"]
        self.model = self.model1
        self.outputString = ""

    def model1(self, t, A, B, k):
        val =B + A/(1 + k*t)
        return val

    def fit(self,x,y,p0 = []):
        if len(p0) == 0:
            B = y[-1]
            A = y[0] - B
            k = 0.1
            p0 = [A, B, k]

        print "p0 is: ", p0
        self.fitGeneral(x,y,p0)


class curie(Model):
    """This class represents a simple Curie dependence, A + B/T, T being the temperature."""
    def __init__(self):
        self.paramNames = ["A", "B"]
        self.model = self.curieCurve

    def curieCurve(self, T, A, B):
        return A + B/T


    def fit(self, x, y, p0 = []):
        if len(p0) == 0:
            A = y[-1]
            #print "y: ", y, "Type(y): ", type(y)
            #print "============="
            #print "x: ", x, "Type(x). ", type(x)
            B = (y[0]-y[1])*x[0]*x[1]/(x[1] - x[0])

            p0 = [A, B]
            print "Parameters have been estimated: ", p0

        self.fitGeneral(x,y,p0)


class curieWeiss(Model):
    """This class represents a simple Curie dependence, A + B/T, T being the temperature."""
    def __init__(self):
        self.paramNames = ["A", "C", "T_c"]
        self.model = self.curieWeissCurve

    def curieWeissCurve(self, T, A, C, T_c):
        return C/(T - T_c)+1 + A


    def fit(self, x, y, p0 = []):
        if len(p0) == 0:
            A = y[-1] -1
            C = 1
            T_c = 1
            p0 = [A, C, T_c]
            print "Parameters have been estimated: ", p0

        self.fitGeneral(x,y,p0)

class clausiusMossoti(Model):
    def __init__(self):
        """Coefficients: alpha is the temperature independent part, for C60 the lit value is 85 A^3
       p0 is the dipole moment in Debye"""

        self.paramNames = ["alpha", "p_0","N"]
        self.model = self.clausiusMossoti

    def clausiusMossoti(self, T, alpha, p_0, N):
        #in cgs
        N = N/1e6
        T = T
        alpha = alpha*1e6

        #SI
        #debye = 3.33564e-30
        #gamma = alpha + 1/(3*epsilon_0)*(p_0*debye)/(k*T)*(p_0*debye)

        kCGS = 1.3806e-16
        gamma = alpha + 4*np.pi/3*p_0**2/(kCGS*T)
        chi = gamma*N/(1 - gamma*N/3)#factor three might be different for different structures
        epsilon = chi + 1

        return epsilon

    def fit(self, x, y, p0 = []):
        if len(p0) == 0:
            alpha = 85e-30
            p_0 = 1
            N = 0.15*1.37e27
            p0 = [alpha, p_0, N]
        self.fitGeneral(x,y,p0)



class saturationRecovery(Model):
    """This class represents a simple"""
    def __init__(self, offset = False):
        self.paramNames = ["B", "A", "k"]
        self.offset = offset
        if offset:
            self.paramnames = ["B", "A", "k"]
            self.model = self.saturationRecoveryOffset
        else:
            self.paramNames = ["A", "k"]
            self.model = self.saturationRecovery

    def saturationRecoveryOffset(self, t, A, B, k):
        return B+A*(1-np.exp(-k*t))

    def saturationRecovery(self, t, A, k):
        return A*(1-np.exp(-k*t))

    def fit(self, x, y, p0 = []):
        if len(p0) == 0 and self.offset == True:
            A = y[-1]-y[0]
            B = y[0]
            k = 1
            p0 = [A, B, k]
            print "Parameters have been estimated: ", p0
        elif len(p0) == 0 and self.offset == False:
            A = y[0]-y[-1]
            k = 1
            p0 = [A, k]
            print "Parameters have been estimated: ", p0

        self.fitGeneral(x,y,p0)


class liqXtalHaller(Model):
    """This class represents a simple model for temperature dependence of
    liquid crystal order parameter (Haller equation):
    S(T) = (1-T/Tdag)**exp
    where Tdag = Ttrans + deltaT (deltaT ~ 1-3K)
    The Haller equation is modified here - a scaling factor is added:
    X(T) = scale*(1-T/Tdag)**exp
    So this model can be used to fit variables that should be proportional
    to the liquid crystal order parameter.
    """
    def __init__(self):
        self.paramNames = ["transitionTemperature", "temperatureShift", "exponent", "scale"]
        self.model = self.haller

    def haller(self, temperatures, transitionTemperature, temperatureShift, exponent, scale):
        """Returns Haller estimate of liquid crystal order parameter
        (Haller1975 http://dx.doi.org/10.1016/0079-6786(75)90008-4). Defaults are for MBBA with C60.
        Note: the original expression does not have the scaling factor in it,
        the factor is included in order to fit things that are expected to be
        be proportional to the liquid crystal order parameter."""
        tCross = transitionTemperature + temperatureShift
        results = []
        for t in temperatures:
            if t < transitionTemperature:
                 results.append(scale*(1 - t/tCross)**exponent)
            else:
                 results.append(0)
        return results


    def fit(self, x, y, p0 = []):
        if len(p0) == 0:
            transitionTemperature = 316
            temperatureShift = 1
            exponent = 0.219
            scale = 1
            p0 = [transitionTemperature, temperatureShift, exponent, scale]
            print "Parameters have been estimated: ", p0


        self.fitGeneral(x,y,p0)


class doubleGaussian(Model):
    """This class represents second order dynamics, according to eq. 7 in paper on kinetics in H2O@C60
    It implents the solution of the following equation:
    DSolve[y'[x] == - 2 k (y[x] - f0)^2, y[x], x]

    The parameters are A, B, k and the fit equation is B + A/(1 + k*t)
    """
    #self.outputString = Model.outputString

    def __init__(self, normalizedGaussians = True):
        self.paramNames = ["A1", "x01","sigma1", "A2", "x02", "sigma2"]
        self.model = self.model1
        self.outputString = ""
        self.normalizedGaussians = normalizedGaussians


    def gaussian(self, x, mu, sig):
        if self.normalizedGaussians:
            return 1./(np.sqrt(2.*np.pi)*sig)*np.exp(-np.power((x - mu)/sig, 2.)/2)
        else:
            #print "Gaussian Normalization off"
            return np.exp(-np.power((x - mu)/sig, 2.)/2)


    def model1(self, x, A1, x01, sigma1, A2, x02, sigma2):
        return A1*self.gaussian(x, x01, sigma1) + A2*self.gaussian(x, x02, sigma2)


    def fit(self,x,y,p0 = []):
        assert len(p0) == 6, "Initial parameters required!"

        print "p0 is: ", p0
        self.fitGeneral(x,y,p0)

class doubleGaussianAmplitudesOnly(doubleGaussian):
    def __init__(self, x01, sigma1, x02, sigma2, normalizedGaussians = False):
        self.paramNames = ["A1", "A2"]
        self.normalizedGaussians = normalizedGaussians
        self.outputString = ""
        self.x01 = x01
        self.sigma1 = sigma1
        self.x02 = x02
        self.sigma2 = sigma2
        self.model = self.model2

    def model2(self, x, A1, A2):
        return self.model1(x, A1, self.x01, self.sigma1, A2, self.x02, self.sigma2)

    def fit(self, x, y, p0 = []):
        assert len(p0) == 2, "Initial parameters required."
        self.fitGeneral(x, y, p0, silence = True)
