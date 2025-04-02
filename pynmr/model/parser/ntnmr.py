from pynmr.model.parser.nmrData import nmrData
import pysftp
import numpy as np
import os
import struct

class NTNMR(nmrData):
    def __init__(self, path, endianess = "<", debug = False, maxLoad = 0, sizeTD1 = 0):
        super().__init__(debug = debug)

        self.sizeTD1 = sizeTD1
        
        """ File information taken from J. van Becks matNMR, thanks! """
        self.f = open(path, mode='rb')

        """ Length """
        self.f.seek(16)
        self.structureSize = struct.unpack('<I', self.f.read(4))[0]

        #SizeTD2
        self.f.seek(20)
        self.sizeTD2 = struct.unpack('<I', self.f.read(4))[0]
        if self.debug: print("The sizeTD2 is: ", self.sizeTD2)

        #SizeTD1
        if sizeTD1 > 0:
            self.sizeTD1 = sizeTD1
        else:
            self.f.seek(24)
            self.sizeTD1 = struct.unpack('<I', self.f.read(4))[0]
            
        #SpectralFrequencyTD2/Anregungsfrequenz
        self.f.seek(104)
        self.carrier = struct.unpack('<d', self.f.read(8))[0]*1e6
        if self.debug: print('The carrier is at {:.3f} MHz'.format(self.carrier / 1e6))

        #SpectralFrequencyTD1
        self.f.seek(112)
        self.spectralFrequencyTD1 = struct.unpack('<d', self.f.read(8))[0]
        if self.debug: print("TD1 is", self.sizeTD1)

        #SweepWidthTD2, SampleRate?
        self.f.seek(260)
        self.sweepWidthTD2 = struct.unpack('<d', self.f.read(8))[0]

        #SweepWidthTD1
        self.f.seek(268)
        self.sweepWidthTD1 = struct.unpack('<d', self.f.read(8))[0]

        
        #a, Daten im Float32, f und 4
        self.f.seek(1056)
        #                self.sizeTD1 = 581
        #print "The length is", len(self.f.read(self.sizeTD2*2*self.sizeTD1*4))
        self.data = struct.unpack('<' + 'f'*(self.sizeTD2*2*self.sizeTD1), self.f.read(self.sizeTD2*2*self.sizeTD1*4))
        self.f.close()

        for i in range(0,  self.sizeTD1):
            #print i
            realPart = self.data[i*self.sizeTD2*2:(i+1)*self.sizeTD2*2:2]
            imagPart = np.multiply(self.data[i*self.sizeTD2*2+1:(i+1)*self.sizeTD2*2+1:2], 1j)
            self.allFid[0].append(np.add(realPart, imagPart))

        self.fidTime = np.arange(self.sizeTD2)*1/self.sweepWidthTD2

        if self.debug: print("Data imported, Number of Experiments: ", self.sizeTD1)
