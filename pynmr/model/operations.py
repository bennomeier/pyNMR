import numpy as np
import scipy as sp

from scipy.fft import fft
from scipy.fftpack import fftshift



class Operation(object):
    def __init__():
        self.name = "Empty Operation"


class LeftShift(Operation):
    def __init__(self, shiftPoints):
        self.name = "Left Shift"
        self.shiftPoints = shiftPoints

    def run(self, nmrData):
        nmrData.allFid.append([nmrData.allFid[-1][k][self.shiftPoints:] for
                               k in range(len(nmrData.allFid[-1]))])
        nmrData.fidTimeForLB = nmrData.fidTime[self.shiftPoints:]


class ZeroFill(Operation):
    def __init__(self, totalPoints):
        self.name = "Zero Filling"
        self.totalPoints = totalPoints

    def run(self, nmrData):
        z = np.zeros(self.totalPoints)
        nmrData.allFid.append([np.concatenate((k, z[:-len(k)])) for
                               k in nmrData.allFid[-1]])


class LineBroadening(Operation):
    def __init__(self, lineBroadening):
        self.name = "Exponential Linebroadening"
        self.lineBroadening = lineBroadening

    def run(self, nmrData):
        #print("LB: {} Hz".format(self.lineBroadening))
        length = len(nmrData.allFid[-1][0])
        nmrData.allFid.append(
            sp.multiply(nmrData.allFid[-1][:],
                        sp.exp(-nmrData.fidTimeForLB[:length]
                               * self.lineBroadening * np.pi)))


class FourierTransform(Operation):
    def __init__(self):
        self.name = "Fourier Transform"

    def run(self, nmrData):
        spectra = np.array([fftshift(fft(fid)) for fid in nmrData.allFid[-1]])
        nmrData.allSpectra = []
        nmrData.allSpectra.append(spectra)
        nmrData.frequency = np.linspace(-nmrData.sweepWidthTD2/2,
                                        nmrData.sweepWidthTD2/2,
                                        len(nmrData.allFid[-1][0]))


class FourierTransform2D(Operation):
    def __init__(self):
        self.name = "2D Fourier Transform"

    def run(self, nmrData):
        spectra = np.array([fftshift(fft(nmrData.allFid[-1]))])
        nmrData.allSpectra = []
        nmrData.allSpectra.append(spectra)
        nmrData.frequency = np.linspace(-nmrData.sweepWidthTD2/2,
                                        nmrData.sweepWidthTD2/2,
                                        len(nmrData.allFid[-1][0]))
        nmrData.frequency1 = np.linspace(-nmrData.sweepWidthTD1/2,
                                         nmrData.sweepWidthTD1/2,
                                         nmrData.sizeTD1)


class Phase0D(Operation):
    def __init__(self, phase, degree=True, domain="F"):
        """Zero Order Phase Correction

        Arguments are nmrData and phase.

        By defaullt the phase is in degree and the correction is applied in
        the freuency domain."""

        self.name = "Phase Zero Order"
        self.phase = phase
        self.degree = degree
        self.domain = domain

    def run(self, nmrData):
        if self.degree:
            phaseFactor = np.exp(-1j*float(self.phase)/180.*np.pi)
        else:
            phaseFactor = np.exp(-1j*self.phase)

        if self.domain == "F":
            spectra = [spec*phaseFactor for spec in nmrData.allSpectra[-1]]
            nmrData.allSpectra.append(spectra)
        elif self.domain == "T":
            fids = [fid*phaseFactor for fid in nmrData.allFid[-1]]
            nmrData.allFid.append(fids)


class Phase1D(Operation):
    def __init__(self, value, pivot=0, scale="Hz", unit="radian"):
        """Zero Order Phase Correction

        Arguments are nmrData and phase.

        By defaullt the phase is in degree and the correction is applied in
        the freuency domain."""

        self.name = "Phase First Order"
        self.value = value
        self.pivot = pivot
        self.unit = unit
        self.scale = scale

    def run(self, nmrData):
        if self.unit == "radian":
            self.phase = self.value
        elif self.unit == "degree":
            self.phase = self.value*np.pi/180
        elif self.unit == "time":
            self.phase = 2*np.pi*nmrData.frequency[-1]*self.value

        #print("Phase: ", self.phase)

        phaseValues = np.linspace(-self.phase/2, self.phase/2,
                                  num=len(nmrData.frequency))

        if self.pivot != 0:
            o = GetIndex(self.pivot, scale=self.scale)
            i = o.run(nmrData)
            phaseValues = phaseValues - phaseValues[i]

        spectra = [spec*np.exp(-1j*phaseValues)
                   for spec in nmrData.allSpectra[-1]]
        nmrData.allSpectra.append(spectra)


class GetIndex(Operation):
    def __init__(self, value, scale = "Hz"):
        """Get Indices corresponding to the frequency or ppm Value."""
        self.value = value
        self.scale = scale
        self.name = "Get Index"

    def run(self, nmrData):
        if self.scale == "Hz":
            index = np.argmin(abs(nmrData.frequency - self.value))
        elif self.scale == "ppm":
            index = np.argmin(abs(nmrData.ppmScale - self.value))

        return index


class GetIndices(Operation):
    def __init__(self, values, scale="Hz"):
        """Get Indices corresponding to the frequency."""
        self.values = values
        self.scale = scale
        self.name = "Get Indices"

    def run(self, nmrData):
        indexList = []
        for v in self.values:
            o = GetIndex(v, scale=self.scale)
            indexList.append(o.run(nmrData))

        return sorted(indexList)

class GetPartialSpectrum(Operation):
    def __init__(self, index, start, stop, scale="Hz"):
        """
        - `index`: selects fid out of a 2D experiment
        - `start`: start value (frequency or ppm)
        - `stop`: stop value
        - `scale`: "Hz" or "ppm"
        """
        self.index = index
        self.start = start
        self.stop = stop
        self.scale = scale
        self.name = "Get Partial Spectrum"

    def run(self, nmrData):
        o = GetIndices([self.start, self.stop], scale=self.scale)
        values = o.run(nmrData)

        return np.real(nmrData.allSpectra[-1][self.index][values[0]:values[1]])

class GetJoinedPartialSpectra(Operation):
    def __init__(self, start, stop, scale="Hz", returnX=False):
        self.start = start
        self.stop = stop
        self.scale = scale
        self.returnX = returnX
        self.name = "Get Joined Partial Spectra"

    def run(self, nmrData):
        spectra = []
        o = GetPartialSpectrum(0, self.start, self.stop, scale=self.scale)
        for index in range(nmrData.sizeTD1):
            o.index = index
            spectra.extend(o.run(nmrData))

        if self.returnX:
            x = np.array(list(range(len(spectra)))) * nmrData.sizeTD1 / float(len(spectra)) + 0.5
            return x, spectra
        else:
            return spectra


class GetSingleIntegral(Operation):
    def __init__(self, index, start, stop, scale="Hz", part="real"):
        """This function integrates the real part between start and stop. standard scale is Hz
        Arguments:
        - `index`: index of the spectrum
        - `start`: lower limit of integration
        - `stop`: upper limit of integration
        - `scale`: Hz or ppm
        - `part`: real or magnitude
        """
        self.index = index
        self.start = start
        self.stop = stop
        self.scale = scale
        self.part = part
        self.name = "Get Single Integral"

    def run(self, nmrData):
        dx = 0
        if self.scale == "Hz":
            dx = np.abs(nmrData.frequency[1] - nmrData.frequency[0])
        elif self.scale == "ppm":
            dx = np.abs(nmrData.ppmScale[1] - nmrData.ppmScale[0])
        else:
            dx = 1

        o = GetIndices([self.start, self.stop], scale=self.scale)
        indices = o.run(nmrData)
        i1 = indices[0]
        i2 = indices[1]

        if self.part == "real":
            retVal = np.sum(np.real(nmrData.allSpectra[-1][self.index][i1:i2])) * dx
        elif self.part == "magnitude":
            retVal = np.sum(np.abs(nmrData.allSpectra[-1][self.index][i1:i2]))*dx

        return retVal


class GetAllIntegrals(Operation):
    def __init__(self, start, stop, scale="Hz", part="real"):
        """This function integrates the real part between start and stop.
        Default scale is Hz.
        Arguments:
        - `index`: index of the spectrum
        - `start`: lower limit of integration
        - `stop`: upper limit of integration
        - `scale`: Hz or ppm
        - `part`: real or magnitude
        """
        self.start = start
        self.stop = stop
        self.scale = scale
        self.part = part
        self.name = "Get All Integrals"

    def run(self, nmrData):
        returnList = []
        o = GetSingleIntegral(0, self.start, self.stop, scale=self.scale,
                              part=self.part)
        for i in range(nmrData.sizeTD1):
            o.index = i
            returnList.append(o.run(nmrData))

        return returnList


class GetPhase(Operation):
    def __init__(self, index, start, stop, scale="Hz"):
        """This function returns the 0 order phase in degrees
        that maximizes the integral in the specified range."""

        self.index = index
        self.start = start
        self.stop = stop
        self.scale = scale
        self.name = "Get Single Phase"

    def run(self, nmrData):
        o = GetIndices([self.start, self.stop], scale=self.scale)
        indices = o.run(nmrData)
        i1 = indices[0]
        i2 = indices[1]

        phiTest = np.linspace(-180, 179, num=360)

        integrals = np.zeros(np.size(phiTest))

        for k in range(len(integrals)):
            integrals[k] = np.sum(np.real(
                nmrData.allSpectra[-1][self.index][i1:i2]
                * np.exp(-1j*float(phiTest[k])/180.*np.pi)))

        return phiTest[np.argmax(integrals)]


class GetAllPhases(Operation):
    def __init__(self, start, stop, scale="Hz", unwrap="False"):
        self.start = start
        self.stop = stop
        self.scale = scale
        self.unwrap = unwrap

    def run(self, nmrData):
        pList = np.array([])
        o = GetPhase(0, self.start, self.stop, scale=self.scale)
        for i in range(nmrData.sizeTD1):
            o.index = i
            pList = np.append(pList, o.run(nmrData))

        if self.unwrap:
            return np.unwrap(pList/360*2*np.pi)*360/(2*np.pi)
        else:
            return pList


class SetPPMScale(Operation):
    def __init__(self, offset=-1, shift=0, ppmValue=-1, scale="offset", automatic=True):
        """
        SetPPMScale(self, offset, ppmValue, scale = 'offset')
        this function constructs a chemical shift axis

        the function will parse information from the bruker files, unless 
        the option automatic is set to False
        for a given offset and corresponding ppmValue.

        scale can be 'offset' or 'absolute'
        - offset is used for signal frequency measured from the carrier,
        - shift will be applied to shift the ppm scale after its creation
        - absolute is used of absolute signal frequency (in Hz).
        The 'absolute' is useful when creating a ppm scale based on data from
        different experiment with different SFO1

        - if no options are passed, the routine will parse the O1 value from the acqus file,
        the bf1 value, also from the acqus file, and calculate o1p as o1 / bf1.
        Then the chemical shift range is o1/bf1 - sw
        assuming that it corresponds to 0 ppm
        """
        self.offset = offset
        self.ppmValue = ppmValue
        self.scale = scale
        self.shift = shift
        self.automatic = automatic
        self.name = "Set PPM Scale"

    def run(self, nmrData):
        if self.automatic:
            # print("Setting PPM Scale automatically")

            #print("Setting PPM Scale automatically with offset from acqus: ",
            #      nmrData.parDictionary["O1"])

            self.offset = - nmrData.parDictionary["O1"]
            self.bf1 = nmrData.parDictionary["BF1"]
            self.o1p = self.offset / self.bf1
            self.ppmValue = 0
            #print(self.o1p)
            self.sw = nmrData.sweepWidthTD2/(nmrData.carrier/1e6)
            #print(self.sw)

            nmrData.ppmScale = np.arange(-self.o1p - self.sw/2, -self.o1p + self.sw/2,
                                     step = self.sw/len(nmrData.frequency))
        else:
            if self.scale == "offset":
                freqRef = nmrData.carrier + self.offset
            elif self.scale == "absolute":
                freqRef = self.offset

            f0 = freqRef/(1 + self.ppmValue*1e-6)
            nmrData.ppmScale = (nmrData.frequency + nmrData.carrier - f0)/f0*1e6 + self.shift


        
        
class SINO(Operation):
    def __init__(self, peakRange, noiseRange, specSet = -1, specIndex = 0, scale="ppm"):
        """
        determine the signal to noise in bruker style.

        """
        self.peakRange = peakRange
        self.noiseRange = noiseRange
        self.specSet = specSet
        self.specIndex = specIndex
        self.scale = scale

    def run(self, nmrData, talk = False):
        """
        - nmrData: nmrData Object.

        returns a tuple comprising snr, peak, noise,
        where snr = peak / 2*noise
        """
        
        realSpec = np.real(nmrData.allSpectra[self.specSet][self.specIndex])

        oPeak = GetIndices(self.peakRange, scale=self.scale)
        indices = oPeak.run(nmrData)
        
        peak = np.max(realSpec[indices[0]:indices[1]])

        # maybe determin fwhm

        oNoise = GetIndices(self.noiseRange, scale=self.scale)
        noiseIndices = oNoise.run(nmrData)
        #print(noiseIndices)
        
        noiseSimple = np.std(realSpec[noiseIndices[0]:noiseIndices[1]])

        indices = np.arange(noiseIndices[0], noiseIndices[1])
        #print("Indices: ", indices)
        
        # in the bruker program, a linear baseline is fitted to the noise region and subtracted.
        # the base line has the functional dependence a + i*b, where i is the index.
        # we do the same, but for a and b use the formulas as presented in Janert's "Data Analysis with Open Source Tools"
        
        n = len(indices)
        sum_xy = np.sum([i*realSpec[i] for i in indices])
        sum_x = np.sum([i for i in indices])
        sum_y = np.sum([realSpec[i] for i in indices])
        sum_xx = np.sum([realSpec[i]**2 for i in indices])

        b = (n*sum_xy - sum_x*sum_y)/(n*sum_xx - sum_x**2)
        a = 1/n*(sum_y - b*sum_x)

        noise = np.sqrt(np.sum((realSpec[noiseIndices[0]:noiseIndices[1]]-(a + indices*b))**2)/(n-1))
        
        snr = peak/(2*noise)
        
        if talk:
            print("Peak: {:.1f}".format(peak))
            print("Noise: {:.1f}".format(noise))
            print("SINO: {:.1f}".format(snr))

        nmrData.parDictionary["SINO"] = snr

        return snr, peak, noise
        

class BaseLineCorrection(Operation):
    def __init__(self, regionSet, degree, scale="Hz", applyLocally=False):
        """
        Polynomial baseline correction.
        region: list of intervals where the baseline is to be determined
        degree: degree of the polynomial to be used.
        scale: scale as used in the region specification, default is "Hz",
               other option is "ppm"
        applyLocally: if set to true, apply baseline correction only
                      within the outer limits of the region list.
        """

        self.regionSet = regionSet
        self.degree = degree
        self.scale = scale
        self.applyLocally = False
        self.name = "Baseline Correction"

    def run(self, nmrData):
        fidList = []
        for k in range(len(nmrData.allSpectra[-1])):
            xVals = []
            yVals = []
            indices = []
            thisFid = []

            for pair in self.regionSet:

                o = GetIndices(pair, scale=self.scale)
                indices = o.run(nmrData)
                i1 = indices[0]
                i2 = indices[1]

                indices.extend([i1, i2])

                assert i1 != i2, """Empty Frequency Range -
                Frequency for Baseline Corrrection outside spectral range?"""

                xVals.extend(nmrData.frequency[i1:i2])
                yVals.extend(np.real(nmrData.allSpectra[-1][k][i1:i2]))

            z = np.polyfit(xVals, yVals, self.degree)

            p = np.poly1d(z)
            self.p = p

            if self.applyLocally:
                thisFid = nmrData.allSpectra[-1][k]
                thisFid[min(indices):max(indices)] -= (
                    p(nmrData.frequency[min(indices):max(indices)]))
            else:
                thisFid = nmrData.allSpectra[-1][k] - p(nmrData.frequency)

                fidList.append(thisFid)

        print("BaselineCorrection done. Polynomial: " + p.__repr__())
        print("Length of nmrData.allSpectra before: ", len(nmrData.allSpectra))
        nmrData.allSpectra.append(fidList)
        print("Length of nmrData.allSpectra after: ", len(nmrData.allSpectra))
