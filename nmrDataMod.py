# -*- coding: utf-8 -*-
import numpy as np
import scipy as sp
import matplotlib as mpl
import matplotlib.pyplot as plt

from scipy import fft
from scipy.fftpack import fftshift


import struct
import string
from scipy import io, constants
from xml.dom import minidom
import os 
import os.path

class nmrData(object):
    """
    nmrData objects is used to import and store nmrData from several file formats.

    Usage: 
    > nmrData = nmrData(path, type)      
    
    supported type: 'ntnmr', 'TopSpin', 'spinSight'
    """
    def __init__(self, path, datatype, container=0, sizeTD1=0):
        """ This reads the data """
        #plt.close()
        if datatype == '':
            print "No Datatype - Setting it to ntnmr"
            datatype = "ntnmr"

        self.carrier = 0   
        self.allFid = []
        self.allFid.append([])
        self.sizeTD1 = sizeTD1
        
        print "The datatype is {0}".format(datatype)
          
        if datatype == "Magritek":
            if os.path.isfile(path + "/data.1d"):
                f = open(path + "/data.1d", "rb")
                
                f.seek(12) 
                print "Format: ", struct.unpack('<i', f.read(4))[0]

                #get this information out of the acqu file.
                f.seek(16)
                self.sizeTD2 = struct.unpack('<i', f.read(4))[0]

                print "Size TD2: ", self.sizeTD2
                self.sweepWidthTD2 = 1e6

                f.seek(32)
                dwellTime = 1./self.sweepWidthTD2
                self.fidTime = np.linspace(0, (self.sizeTD2-1)*dwellTime, num = self.sizeTD2)

                #t just contains floats with the time
                t = struct.unpack('<' + 'f'*self.sizeTD2, f.read(4*self.sizeTD2))

                data1 = struct.unpack('<' + 'f'*self.sizeTD2*2, f.read(4*self.sizeTD2*2))
                #data2 = struct.unpack('<' + 'f'*2048, fidFile.read(4*2048))
                #data = struct.unpack('>' + 'l'*(sizeTD2*2*1), fidFile.read(sizeTD2*2*1*4))

                self.frequency = np.linspace(-self.sweepWidthTD2/2,self.sweepWidthTD2/2, 2048)

                realPart = np.array(data1[::2])
                imagPart = np.array(data1[1::2])

                self.allFid[0].append(realPart + 1j*imagPart)

            elif os.path.isfile(path + "/data.2d"):
                f = open(path + "/data.2d", "rb")
                
                f.seek(12) 
                print "Format: ", struct.unpack('<i', f.read(4))[0]

                #get this information out of the acqu file.
                f.seek(16)
                self.sizeTD2 = struct.unpack('<i', f.read(4))[0]
                self.sizeTD1 = struct.unpack('<i', f.read(4))[0]

                print "Size TD2: ", self.sizeTD2
                print "Size TD1: ", self.sizeTD1
                self.sweepWidthTD2 = 1e6

                f.seek(32)
                dwellTime = 1./self.sweepWidthTD2

                self.data1 = struct.unpack('<' + 'f'*(self.sizeTD2*self.sizeTD1*2), f.read(4*self.sizeTD2*self.sizeTD1*2))

                self.realStuff = np.array(self.data1[::2])
                self.imagStuff = np.array(self.data1[1::2])

                self.complexData = self.realStuff + 1j*self.imagStuff

                self.allFid[0] = np.split(self.complexData, [self.sizeTD2*(i+1) for i in range(self.sizeTD1-1)])

                self.fidTime = np.linspace(0, (self.sizeTD2-1)*dwellTime, num = self.sizeTD2)

            else:
                print "No 1D file found."

        if datatype == 'TopSpinOld':
            self.f = open(path, mode='rb')
            self.sizeTD2=1
            self.sizeTD1=(int((os.stat(path)).st_size))/8 
            self.data = struct.unpack('>' + 'i'*(self.sizeTD2*2*self.sizeTD1), self.f.read(self.sizeTD2*2*self.sizeTD1*4))
            for i in range(0,  self.sizeTD1):
                print i
                realPart = self.data[i*self.sizeTD2*2:(i+1)*self.sizeTD2*2:2]
                imagPart = sp.multiply(self.data[i*self.sizeTD2*2+1:(i+1)*self.sizeTD2*2+1:2], 1j)
                self.allFid[0].append(sp.add(realPart, imagPart))

        if datatype == 'TopSpin':
            #The acqus file containts the spectral width SW_h and 2*SizeTD2 as ##$TD
            #The acqu2s file contains TD1 as ##$TD
            directory = os.path.dirname(path)
            acqusFile = open(directory + "/acqus", mode='r')

            #check if acqu2sfile exists, if yes, experiment is 2D!
            if os.path.isfile(directory + "/acqu2s"):
                acqu2sFile = open(directory + "/acqu2s", mode='r')
                acqu2File = open(directory + "/acqu2", mode='r')
                self.is2D = True
            else:
                self.is2D = False
                self.sizeTD1 = 1


            #this could be crafted into a common routine which gives names of parameters
            #parameters and works the same for e.g., spinsight and topspin
            count = 0
            while True:
                #try:
                count += 1
                line = acqusFile.readline().strip()
                if "=" in line:
                    line = line.split("=")
                elif len(line) == 0 or count > 1000:
                    print "Ended reading acqus file at line ", count
                    break
                else:
                    next
                    
                    #print line[0]
                if line[0] == "##$SW_h":
                    #this line might be chopping the last digit off....
                    #self.sweepWidthTD2 = int(float(line[1][:-1]))
                    self.sweepWidthTD2 = int(float(line[1]))
                    print "SweepWidthTD2: ", self.sweepWidthTD2
                elif line[0] == "##$TD":
                    self.sizeTD2 = int(line[1])/2
                    print "sizeTD2: ", self.sizeTD2
                elif line[0] == "##$SFO1":
                    self.carrier = float(line[1])*1e6

                elif len(line) == 0:
                    break

            if self.is2D == True:
                count = 0
                while True:
                    #try:
                    count += 1
                    line = acqu2sFile.readline().strip()
                    if "=" in line:
                        line = line.split("=")
                    elif len(line) == 0 or count > 1000:
                        print "Ended reading acqu2s file at line ", count
                        break
                    else:
                        next
                    
                    #print line[0]
                    if line[0] == "##$TD" and self.sizeTD1 == 0:
                        self.sizeTD1 = int(line[1])
                        print "sizeTD1: ", self.sizeTD1
                    elif len(line) == 0:
                        break
                    
            print "TD2: ", self.sizeTD2
            print "TD1: ", self.sizeTD1
            print "Carrier:", self.carrier

            if self.is2D:
                self.f = open(path + "/ser", mode='rb')
            else:
                self.f = open(path + "fid", mode='rb')
                
            dataString = self.f.read(self.sizeTD2*2*self.sizeTD1*4)
            print "len(dataString): ", len(dataString)
            print "OK?"

            dwellTime = 1./self.sweepWidthTD2
            self.fidTime = np.linspace(0, (self.sizeTD2-1)*dwellTime, num = self.sizeTD2)
            
            self.data = struct.unpack('<' + 'i'*(self.sizeTD2*2*self.sizeTD1), dataString)
            for i in range(0,  self.sizeTD1):
                #print i
                realPart = self.data[i*self.sizeTD2*2:(i+1)*self.sizeTD2*2:2]
                imagPart = sp.multiply(self.data[i*self.sizeTD2*2+1:(i+1)*self.sizeTD2*2+1:2], 1j)
                self.allFid[0].append(sp.add(realPart, imagPart))

                
        if datatype == 'spinsight':
            chStr = "" # first read the channel, if succesful read the carrier frequency.
            carrierStr = "carrier string not assigned"
            self.is2D = False
            dataFile = path + "/data"
            print "dataFile is: ", dataFile
            self.f = open(dataFile, mode='rb')
            self.f.seek(0)

            acqFile = path + "/acq"
            self.fACQ = open(acqFile)
            count = 0
            while True:
                count += 1
                try: 
                    line = self.fACQ.readline().strip().split("=")
                    print line
                    if line[0] == "ch1": 
                        chStr = line[1]
                        carrierStr = "sf" + chStr
                    elif line[0] == carrierStr:
                        self.carrier = float(line[1][:-1])*1e6
                    if line[0] == "dw":
                        print "Hellop: ", line[1]
                        self.sweepWidthTD2 = int(1/float(line[1][:-1]))
                        #print "sweepWidthTD2: ", self.sweepWidthTD2
                    elif line[0] == "array_num_values_pd" or line[0] == "array_num_values_tau" or line[0] == "array_num_values_pw90X" or line[0] == "array_num_values_tau1":
                        self.sizeTD1 = int(line[1])
                        self.is2D = True
                    elif len(line) < 2 and count > 10:
                        break

                except:
                    break

            #check if file named apnd exists
            if self.is2D == True:
                self.sizeTD2 = int((os.stat(dataFile)).st_size)/8/self.sizeTD1
            else: 
                self.sizeTD2 = (int((os.stat(dataFile)).st_size))/8
                print "sizeTD2 is: ", self.sizeTD2
                self.sizeTD1 = 1
                print "sizeTD1 is: ", self.sizeTD1
                                          
            #print "Length 1: ", self.sizeTD1*self.sizeTD2*2
            #print "Length 2: ", len(self.f.read(self.sizeTD1*self.sizeTD2*2*4))
            self.f.seek(0)
            self.data = struct.unpack('>' + 'i'*self.sizeTD1*self.sizeTD2*2, self.f.read(self.sizeTD1*self.sizeTD2*2*4))
            print "Length of data: ", len(self.data)

            for i in range(self.sizeTD1):
                print i
                realPart = np.array(self.data[i*self.sizeTD2:(i+1)*self.sizeTD2])
                imagPart = np.array(self.data[self.sizeTD1*self.sizeTD2+i*self.sizeTD2:self.sizeTD1*self.sizeTD2+(i+1)*self.sizeTD2])
                print "Length realPart: ", len(realPart)
                print "Length imagPart: ", len(imagPart)
                self.allFid[0].append(realPart + 1j*imagPart)

            print "sizeTD1: ", self.sizeTD1
            self.fidTime = np.linspace(0, (self.sizeTD2-1)/float(self.sweepWidthTD2), self.sizeTD2)

		
        if datatype == 'ntnmr':
            """ File information taken from J. van Becks matNMR, thanks! """
            self.f = open(path, mode='rb')
		  
            """ Length """
            self.f.seek(16)
            self.structureSize = struct.unpack('<I', self.f.read(4))[0]

            #SizeTD2
            self.f.seek(20)
            self.sizeTD2 = struct.unpack('<I', self.f.read(4))[0]

            #SizeTD1
            if sizeTD1 > 0:
                self.sizeTD1 = sizeTD1
            else:
                self.f.seek(24)
                self.sizeTD1 = struct.unpack('<I', self.f.read(4))[0]

            #SpectralFrequencyTD2/Anregungsfrequenz
            self.f.seek(104)
            self.spectralFrequencyTD2 = struct.unpack('<d', self.f.read(8))[0]*1e6
            print 'spec TD2 is', self.spectralFrequencyTD2

            #SpectralFrequencyTD1
            self.f.seek(112)
            self.spectralFrequencyTD1 = struct.unpack('<d', self.f.read(8))[0]
            print "TD1 is", self.sizeTD1

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
                imagPart = sp.multiply(self.data[i*self.sizeTD2*2+1:(i+1)*self.sizeTD2*2+1:2], 1j)
                self.allFid[0].append(sp.add(realPart, imagPart))
                print "Data imported, Number of Experiments: ", self.sizeTD1


    def offsetCorrection(self, fromPos, toPos, fraction = 0.75, whichFid = 0):

        self.checkToPos(toPos)
        l = len(self.allFid[fromPos][0])
        startOffset = int(fraction*l)

        print "fid: ", whichFid
        print "startOffset: ", startOffset

        print "len allFid: ", len(self.allFid)
        #        print "len allFid[0]: ", len(self.allFid[
        print "len allFid[0]: ", len(self.allFid[0])
        print "==============================================================="
        print "len allFid[0][" + str(whichFid) + "]: ", len(self.allFid[0][0])

        
        oReal = np.mean(np.real(self.allFid[fromPos][whichFid][startOffset:]))
        stdReal = np.std(np.real(self.allFid[fromPos][whichFid][startOffset:])-oReal)

        print "offsetReal: ", oReal
        print "stdReal: ", stdReal
        
        oImag = np.mean(np.imag(self.allFid[fromPos][whichFid][startOffset:]))
        stdImag = np.std(np.imag(self.allFid[fromPos][whichFid][startOffset:])-oImag)

        print "offsetImag: ", oImag
        print "stdImag: ", stdImag

        
        self.allFid[toPos] = [np.real(fid) - oReal +1j*(np.imag(fid) - oImag) for fid in self.allFid[fromPos]]

                
    def lineBroadening(self, fromPos, toPos, LB):
        self.checkToPos(toPos)
        self.allFid[toPos] = sp.multiply(self.allFid[fromPos][:], sp.exp(-self.fidTime*LB))

    def fourierTransform(self, fromPos, toPos):
        self.checkToPos(toPos)
        self.allFid[toPos] = [fftshift(fft(fid)) for fid in self.allFid[fromPos]]
        self.frequency = np.linspace(-self.sweepWidthTD2/2,self.sweepWidthTD2/2,len(self.allFid[fromPos][0]))

    def phase(self, fromPos, toPos, phase, degree=True):
        self.checkToPos(toPos)

        if degree == True:
            phaseFactor = np.exp(-1j*float(phase)/180.*np.pi)
        else:
            phaseFactor = np.exp(-1j*phase)
        self.allFid[toPos] = [fid*phaseFactor for fid in self.allFid[fromPos]]

    def autoPhase0(self, fromPos, index, start, stop, scale = "Hz"):
        """This function should get fromPos and index pointing to a spectrum. It will return the phase for maximimizing the integral over the real part in the spectral region of interest, in degrees."""
        if scale == "Hz":
            i1 = self.getIndexFromFrequency(start)
            i2 = self.getIndexFromFrequency(stop)
        elif scale=="ppm":
            i1 = self.getIndexFromPPM(start)
            i2 = self.getIndexFromPPM(stop)

        phiTest = np.linspace(0, 359, num = 360)

        integrals = np.zeros(np.size(phiTest))

        for k in range(len(integrals)):
            integrals[k] = np.sum(np.real(self.allFid[fromPos][index][start:stop]*np.exp(-1j*phiTest[k]/180*np.pi)))
        return phiTest[np.argmax(integrals)]

        
        
    def phaseFirstOrder(self, fromPos, toPos, phi1, degree = False, noChangeOnResonance=False, pivot = 0):
        """This should only be applied to Fourier transformed spectral data
        It will lead to a zero phase shift at the upper end of the spectrum and to a 
        phase shift of phi1 at the lower end, linear interpolation inbetween.
        this is the spinsight convention.
        """
        self.checkToPos(toPos)
        phaseValues = np.linspace(0,phi1,num=len(self.frequency))

        if noChangeOnResonance == True:
            pivot = 0
        elif pivot !=0:
            print "Using pivot for first order phase correction"
            index = self.getIndexFromFrequency(pivot)            
            phaseValues = phaseValues - phaseValues[index]
            0
        if degree == True:
            phaseValues = phaseValues*np.pi/180
            
        self.allFid[toPos] =  [spectrum*np.exp(-1j*phaseValues) for spectrum in self.allFid[fromPos]]

        
    def leftShift(self, fromPos, toPos, shiftPoints):
        self.checkToPos(toPos)
        self.allFid[toPos] = [self.allFid[fromPos][k][shiftPoints:] for k in range(len(self.allFid[fromPos]))]
        self.fidTime = self.fidTime[shiftPoints:]
        #self.frequency = np.linspace(-self.sweepWidthTD2/2,self.sweepWidthTD2/2,len(self.fidTime))

    def zeroFilling(self, fromPos, toPos, totalPoints):
        self.checkToPos(toPos)
        z = np.zeros(totalPoints)
        self.allFid[toPos] = [np.concatenate((k, z[:-len(k)])) for k in self.allFid[fromPos]]
            
    def getJoinedPartialSpectra(self, fromPos, startFreq, stopFreq):
        spectra = []
        for index in range(self.sizeTD1):
            spectra.extend(self.getPartialSpectrum(fromPos, index, startFreq, stopFreq))
        return spectra

    def getPartialSpectrum(self, fromPos, index, startFreq, stopFreq):
        i1 = self.getIndexFromFrequency(startFreq)
        i2 = self.getIndexFromFrequency(stopFreq)
        return np.real(self.allFid[fromPos][index][i1:i2])

    def integrateRealPart(self, fromPos, index, start, stop, scale="Hz"):
        """This function integrates the real part between start and stop. standard scale is Hz
        Arguments:
        - `fromPos`:
        - `index`: index of the spectrum
        - `startFreq`: lower limit of integration
        - `stopFreq`: upper limit of integration
        """
        if scale == "Hz":
            i1 = self.getIndexFromFrequency(start)
            i2 = self.getIndexFromFrequency(stop)
        elif scale=="ppm":
            i1 = self.getIndexFromPPM(start)
            i2 = self.getIndexFromPPM(stop)
        #print "i1: ", i1
        #print "i2: ", i2
        #print np.real(self.allFid[fromPos][index][i1:i2])
        return np.sum(np.real(self.allFid[fromPos][index][i1:i2]))

    def integrateAllRealPart(self, fromPos, start, stop, scale="Hz"):
        #return all integrals by calling integrateRealPart sizeTD1 times
        return np.array([self.integrateRealPart(fromPos, k, start, stop, scale = scale)
                         for k in range(self.sizeTD1)])

    
    def getPeak(self, fromPos, index, start, stop, negative = False, scale="Hz"):
        """This function returns peak intensities in a given range; it searches for negative peaks if negative = True"""

        i1, i2 = self.getIndices([start, stop], scale=scale)
        spec = self.allFid[fromPos][index]
        
        if negative == False:
            maxVal = np.max(np.real(spec[i1:i2]))
        elif negative ==  True:
            maxVal = -np.max(-np.real(spec[i1:i2]))

        return maxVal

    def getCenterFrequency(self, fromPos, index, start, stop, scale ="Hz"):
        if scale == "Hz":
            i1 = self.getIndexFromFrequency(start)
            i2 = self.getIndexFromFrequency(stop)
        elif scale=="ppm":
            i1 = self.getIndexFromPPM(start)
            i2 = self.getIndexFromPPM(stop)

        #print "i1: ", i1
        #print "i2: ", i2
   
        freqList = np.linspace(start, stop, num = (i2 - i1))
        #print freqList
        return np.sum(freqList*np.real(self.allFid[fromPos][index][i1:i2]))/self.integrateRealPart(fromPos, index, start, stop, scale = scale)

    
    def getIndexFromFrequency(self, freq):
        return np.argmin(abs(self.frequency - freq))

    def getIndexFromPPM(self, ppm):
        indexCounter = 0
        while True:
            if self.ppmScale[indexCounter] < ppm:
                next
            else:
                break
            indexCounter += 1

        if abs(self.ppmScale[indexCounter -1]-ppm) < abs(self.ppmScale[indexCounter] - ppm):
            retVal = indexCounter - 1
        else:
            retVal = indexCounter
        return retVal

    def getIndices(self, interval, scale="Hz"):
        if scale=="Hz":
            i1 = self.getIndexFromFrequency(interval[0])
            i2 = self.getIndexFromFrequency(interval[1])
        elif scale=="ppm":
            i1 = self.getIndexFromPPM(interval[0])
            i2 = self.getIndexFromPPM(interval[1])
        return i1, i2

            
    def checkToPos(self, toPos):
        if len(self.allFid) <= toPos:
            self.allFid.append([])

    def inverseFourierTransform(self, fromPos, toPos):
          #fid = ifft(ifftshift(spectrum))
          # fid = fid[0:len(fid/2)]
          print "This function has not been checked!"

    def getPPMScale(self, reference=[]):
        """this function constructs a chemical shift axis given a reference of the form
        reference = [offset, shift]

        For example if a signal of known chemical shift 3.14 ppm occurs at -350 Hz, then the 
        axis would be constructed using
        getPPMScale(reference=[-350, 3.14]

        If reference is left empty, the 0 ppm value is assumed to be at the carrier frequency.
        """
        print "self.carrier: ", self.carrier

        
        
        if reference == []:
            self.ppmScale = self.frequency/self.carrier*1e6
        else:
            #calculate the magnitude of the reference frequency:
            freqRef = self.carrier + reference[0]
            # now we know that sigmaRef = (omegaRef - omega0)/omega0 => omega0 = omegaRef/(1 + sigmaREf)
            #in this case freqRef = omega, and omega0 will be the zero ppm frequency
            #hence
            f0 = freqRef/( 1 + reference[1]*1e-6)
            #print "f0 is: ", f0
            self.ppmScale = (self.frequency + self.carrier - f0)/f0*1e6

    def export(self, pos, count, filename, scale="Hz", xlim=[], complexType="r", fmt="%.3f"):
        if scale == "Hz":
            xData = self.frequency
        elif scale == "ppm":
            xData = self.ppmScale
        elif scale == "Time":
            L = len(self.allFid[pos][count])
            xData = np.linspace(0,float(L)/self.sweepWidthTD2,L)

        yDataR = np.real(self.allFid[pos][count])
        yDataI = np.imag(self.allFid[pos][count])
        yDataM = np.abs(self.allFid[pos][count])

        if xlim == []:
            start = 0
            stop = -1
        else:
            if scale == "Hz":
                start = self.getIndexFromFrequency(xlim[0])
                stop = self.getIndexFromFrequency(xlim[1])
            elif scale == "ppm":
                start = self.getIndexFromPPM(xlim[0])
                stop = self.getIndexFromPPM(xlim[1])

 
        if complexType == "r":
            data = zip(xData[start:stop], yDataR[start:stop])

        np.savetxt(filename, data, fmt=fmt, delimiter="\t")
            
          
                  

class container(object):
      def __init__(self):
            self.content = []

      def addContent(self, path, type):
            self.content.append(nmrData(path, type))
            return len(self.content)



      

if __name__ == "__main__":
      print nmrData.__doc__

      nmrData = nmrData(2011051010, 'TopSpin')
