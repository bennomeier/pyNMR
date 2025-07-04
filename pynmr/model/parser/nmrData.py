""" This file defines the NMR data object. All parsers are children of this object.

This object defines the plus and minus operations

"""
from datetime import datetime
import numpy as np


class nmrData(object):
    def __init__(self, debug=False):
        self.datatype = ""
        self.carrier = 0

        self.allFid = []
        self.allFid.append([])

        self.allSpectra = []
        # self.allSpectra.append([])

        self.fidTimeForLB = []
        self.sizeTD1 = 0
        self.title = ""
        self.parDictionary = {}
        self.debug = debug
        self.frequency1 = []
        self.is2D = False
        self.path = ""

        self.timeParsed = datetime.now()

    def reset(self):
        self.allFid = [self.allFid[0]]
        self.allSpectra = []

    def __print__(self):
        print("NMR Data Object, parsed on " + self.timeParsed)

    def saveAscii(self):
        print("Trying to save processed data...")
        x = self.ppmScale
        y = np.real(self.allSpectra[-1][-1])

        fname = self.path + "pynmrExport.txt"
        np.savetxt(fname, (x, y), fmt="%.5e")

    def RSPEC(self, pos, id):
        # short hand function to get the real part of the spectrum
        return np.real(self.allSpectra[pos][id])
    
    def ISPEC(self, pos, id):
        # short hand function to get the real part of the spectrum
        return np.imag(self.allSpectra[pos][id])

    def RFID(self, pos, id):
        # short hand function to get the real part of the FID
        return np.real(self.allFid[pos][id])
    
    def IFID(self, pos, id):
        # short hand function to get the real part of the FID
        return np.imag(self.allFid[pos][id])

