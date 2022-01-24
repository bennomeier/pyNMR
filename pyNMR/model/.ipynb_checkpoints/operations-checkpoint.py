import numpy as np
import scipy as sp

from scipy import fft
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
        nmrData.fidTime = nmrData.fidTime[self.shiftPoints:]

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
        length = len(nmrData.allFid[-1][0])
        nmrData.allFid.append(
            sp.multiply(nmrData.allFid[-1][:],
                        sp.exp(-nmrData.fidTime[:length]*self.lineBroadening*np.pi)))

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

        
