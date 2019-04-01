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
import fwhm
import types
from scipy import stats
from scipy import optimize
import imp
imp.reload(fwhm)


class nmrData(object):
    """
    nmrData objects is used to import and store nmrData from several file formats.

    Usage:
    > nmrData = nmrData(path, type)

    supported type: 'Magritek', 'ntnmr', 'TopSpin', 'spinSight', 'varian', 'TopSpin4'
    """
    def __init__(self, path, datatype, container=0, sizeTD1=0, process = False,  lb = 0, phase = 0, ls = 0, zf = 0, ft_only = [], debug = False, hiper_skip_footer = 0, hiper_skip_header = 3, endianess = "<", maxLoad = 0):
        """ This reads the data """
        #plt.close()
        if datatype == '':
            print("No Datatype - Setting it to ntnmr")
            datatype = "ntnmr"

        self.carrier = 0
        self.allFid = []
        self.allFid.append([])
        self.sizeTD1 = sizeTD1
        self.title = ['no title']
        self.vdList = []
        self.files = [] #here we store open files so we can close them later

        self.parDictionary = {}

        self.debug = debug

        if self.debug: print("The datatype is {0}".format(datatype))

        if datatype == "Hiper":
            """Hiper EPR Data import for EPR experiments at St Andrews, UK.

            Note you will have to adjust the skip_footer parameter,
            depending on the length of the pulse programme that is appended to the data file."""

            data = np.genfromtxt(path, skip_header = hiper_skip_header, skip_footer = hiper_skip_footer, delimiter = ",")
            self.sizeTD1 = 1

            timeList = data[:, 0]
            iData = data[:, 1]
            qData = data[:, 2]
            self.sizeTD2 = len(qData)
            if self.debug: print("sizeTD2: ", self.sizeTD2)

            dwellTime = (timeList[1] - timeList[0])*1e-9
            self.sweepWidthTD2 = int(1. /dwellTime)
            if self.debug: print("SweepWidthTD2: ", self.sweepWidthTD2)

            self.allFid[0].append(iData + 1j*qData)
            self.fidTime = np.linspace(0, (self.sizeTD2-1)*dwellTime, num = self.sizeTD2)


        if datatype == "Magritek":

            #get sweep WidthTD2 based on dweelTime in acqu.par
            if os.path.isfile(path + "/acqu.par"):

                f_acqu = open(path + "/acqu.par", "r")

                count = 0
                while True:
                    count += 1
                    line = f_acqu.readline().strip()
                    if "=" in line:
                        line = line.split("=")
                    elif len(line) == 0 or count > 1000:
                        if self.debug: print("Ended dreading acqus file at line ", count)
                        break
                    else:
                        next

                    if len(line[0]) > 1:
                        self.parDictionary[line[0].strip()] = line[1].strip()


                self.sweepWidthTD2 = int(1./(float(self.parDictionary["dwellTime"])*1e-6))
                if self.debug: print("SweepWidthTD2: ", self.sweepWidthTD2)


            if os.path.isfile(path + "/data.1d"):
                f = open(path + "/data.1d", "rb")

                f.seek(12)
                print("Format: ", struct.unpack('<i', f.read(4))[0])

                #get this information out of the acqu file.
                f.seek(16)
                self.sizeTD2 = struct.unpack('<i', f.read(4))[0]

                print("Size TD2: ", self.sizeTD2)

                f.seek(32)
                dwellTime = 1./self.sweepWidthTD2
                self.fidTime = np.linspace(0, (self.sizeTD2-1)*dwellTime, num = self.sizeTD2)

                #t just contains floats with the time
                t = struct.unpack('<' + 'f'*self.sizeTD2, f.read(4*self.sizeTD2))

                data1 = struct.unpack('<' + 'f'*self.sizeTD2*2, f.read(4*self.sizeTD2*2))

                realPart = np.array(data1[::2])
                imagPart = np.array(data1[1::2])

                self.allFid[0].append(realPart + 1j*imagPart)

                self.frequency = np.linspace(-self.sweepWidthTD2/2,self.sweepWidthTD2/2, 2048)

            elif os.path.isfile(path + "/data.2d"):
                f = open(path + "/data.2d", "rb")

                f.seek(12)
                print("Format: ", struct.unpack('<i', f.read(4))[0])

                #get this information out of the acqu file.
                f.seek(16)
                self.sizeTD2 = struct.unpack('<i', f.read(4))[0]
                self.sizeTD1 = struct.unpack('<i', f.read(4))[0]

                print("Size TD2: ", self.sizeTD2)
                print("Size TD1: ", self.sizeTD1)

                f.seek(32)
                dwellTime = 1./self.sweepWidthTD2

                self.data1 = struct.unpack('<' + 'f'*(self.sizeTD2*self.sizeTD1*2), f.read(4*self.sizeTD2*self.sizeTD1*2))

                self.realStuff = np.array(self.data1[::2])
                self.imagStuff = np.array(self.data1[1::2])

                self.complexData = self.realStuff + 1j*self.imagStuff

                self.allFid[0] = np.split(self.complexData, [self.sizeTD2*(i+1) for i in range(self.sizeTD1-1)])

                self.fidTime = np.linspace(0, (self.sizeTD2-1)*dwellTime, num = self.sizeTD2)

            else:
                print("No 1D file found.")

        if datatype == "varian":

            # read the header file
            if os.path.isfile(path + "/procpar"):
                parFile = open(path + "/procpar", 'r')
                rows = parFile.readlines()
                lineCounter = 0;
                for line in rows:
                    if line.find("np ") > -1:
                        nextLine = rows[lineCounter+1]
                        params = nextLine.split(" ")
                        totalComplexPoints = int(params[1]) #np =is R+I
                        self.sizeTD2 = totalComplexPoints/2
                    elif line.find("acqcycles") > -1:
                        nextLine = rows[lineCounter+1]
                        params = nextLine.split(" ")
                        self.sizeTD1 = int(params[1])
                        if self.sizeTD1 > 1:
                            self.is2D = True
                        else:
                            self.is2D = False
                    lineCounter = lineCounter+1
            else:
                print("No procpar file found.")

            # read the binary data file
            if os.path.isfile(path + "/fid"):
                specpoints = self.sizeTD2
                headerskip_init = 8
                headerskip = 7
                f = open(path + "/fid", 'rb');
                data_array = np.fromfile(f, '>f', -1)
                if not self.is2D:
                    self.allFid[0] = data_array[(headerskip_init + headerskip)::2] + 1j*data_array[(headerskip_init + headerskip + 1)::2]
                else:
                    Nacq = (len(data_array) - headerskip_init) / (2 * specpoints + headerskip)
                    if Nacq != self.sizeTD1:
                        print("warning: inconsistent sizes")
                    for n in range(0, Nacq):
                        skipn = headerskip_init + (n+1)*headerskip + n*2*specpoints;
                        realPart = data_array[skipn+0:skipn+2*specpoints:2]
                        imagPart = 1j*data_array[skipn+1:skipn+2*specpoints:2]
                        self.allFid[0].append(sp.add(realPart, imagPart))
            else:
                print("No fid file found.")

        if datatype == 'TopSpinOld':
            self.f = open(path, mode='rb')
            self.sizeTD2=1
            self.sizeTD1=(int((os.stat(path)).st_size))/8
            self.data = struct.unpack('>' + 'i'*(self.sizeTD2*2*self.sizeTD1), self.f.read(self.sizeTD2*2*self.sizeTD1*4))
            for i in range(0,  self.sizeTD1):
                #print i
                realPart = self.data[i*self.sizeTD2*2:(i+1)*self.sizeTD2*2:2]
                imagPart = sp.multiply(self.data[i*self.sizeTD2*2+1:(i+1)*self.sizeTD2*2+1:2], 1j)
                self.allFid[0].append(sp.add(realPart, imagPart))

        if datatype == 'TopSpin':
            if self.debug:
                print("hi, this is self.debug for the TopSpin datatype")
            #The acqus file containts the spectral width SW_h and 2*SizeTD2 as ##$TD
            #The acqu2s file contains TD1 as ##$TD
            directory = os.path.dirname(path)
            acqusFile = open(directory + "/acqus", mode='r')
            self.files.append(acqusFile)

            if self.debug:
                print("Importing TopSpin data")

            #check if acqu2sfile exists, if yes, experiment is 2D!
            if os.path.isfile(directory + "/acqu2s"):
                acqu2sFile = open(directory + "/acqu2s", mode='r')
                self.files.append(acqu2sFile)
                acqu2File = open(directory + "/acqu2", mode='r')
                self.files.append(acqu2File)

                self.is2D = True
            else:
                self.is2D = False
                self.sizeTD1 = 1

            if self.debug:
                print("2D: ", self.is2D)

            #this could be crafted into a common routine which gives names of parameters
            #parameters and works the same for e.g., spinsight and topspin
            if self.debug:
                print("reading acqus file")
            count = 0
            while True:
                if self.debug:
                    print("count = ", count)
                #try:
                count += 1
                line = acqusFile.readline().strip()
                if self.debug:
                    print(line)
                if "=" in line:
                    line = line.split("=")
                elif len(line) > 0:
                    line = line.split(" ")
                elif len(line) == 0 or count > 1000:
                    if self.debug: print("Ended reading acqus file at line ", count)
                    break
                else:
                    next

                    #print line[0]
                if line[0] == "##$SW_h":
                    #this line might be chopping the last digit off....
                    #self.sweepWidthTD2 = int(float(line[1][:-1]))
                    self.sweepWidthTD2 = int(float(line[1]))
                    if self.debug: print("SweepWidthTD2: ", self.sweepWidthTD2)
                elif line[0] == "##$TD":
                    self.sizeTD2 = int(int(line[1])/2)
                    if self.debug: print("sizeTD2: ", self.sizeTD2)
                elif line[0] == "##$SFO1":
                    self.carrier = float(line[1])*1e6
                    if self.debug: print("SFO1:", self.carrier)

                elif len(line) == 0:
                    break


                if len(line[0]) > 1:
                    if "@" in line[-1]:
                        #this line contains date, time, some unknown stuff and user, does not work with all bruker files, hence try only"
                        try:
                            self.parDictionary["date"] = line[1].strip()
                            self.parDictionary["time"] = line[2].strip()
                        except:
                            pass
                    elif line[0] == "##$D":
                        delays1 = acqusFile.readline().strip()
                        delays2 = acqusFile.readline().strip()
                        self.parDictionary["d"] = [float(d) for d in delays1.strip().split(" ")] + [float(d) for d in delays2.strip().split(" ")]

                    elif line[0] == "##$L":
                        loopCounters = acqusFile.readline().strip()
                        self.parDictionary["l"] = [float(l) for l in loopCounters.strip().split(" ")]

                    else:
                        if self.debug:
                            print("the catch all else")
                        if len(line) > 1:
                            self.parDictionary[line[0][2:].strip()] = line[1].strip()
                        else:
                            if self.debug:
                                print("skipped too short line")


            if self.is2D == True:
                if self.debug:
                    print("reading acqu2s file")
                count = 0
                while True:
                    if self.debug:
                        print("count = ", count)
                    #try:
                    count += 1
                    line = acqu2sFile.readline().strip()
                    if "=" in line:
                        line = line.split("=")
                    elif len(line) == 0 or count > 1000:
                        if self.debug: print("Ended reading acqu2s file at line ", count)
                        break
                    else:
                        next

                    #print line[0]
                    if line[0] == "##$TD" and self.sizeTD1 == 0:
                        self.sizeTD1 = int(line[1])
                        if self.debug: print("sizeTD1: ", self.sizeTD1)
                    elif len(line) == 0:
                        break

                if os.path.isfile(directory + "/vdlist"):
                    if self.debug: print("VD File exists!")
                    self.vdList = np.loadtxt(directory + "/vdlist")

            if self.debug:
                print("TD2: ", self.sizeTD2)
                print("TD1: ", self.sizeTD1)
                print("Carrier:", self.carrier)

            # if self.is2D:
            #     self.f = open(path + "/ser", mode='rb')
            # else:
            #     self.f = open(path + "fid", mode='rb')#
            #           dataString = self.f.read(self.sizeTD2*2*self.sizeTD1*4)
            #          if self.debug: print "len(dataString): ", len(dataString)
            #         self.f.close()
            #
            #           # here we read the FID data from fid/ser file
            #          # first convert the datasting into a list of numbers:
            # if self.debug: print "Endianess: ", endianess
            #     self.data = struct.unpack(endianess + 'i'*(self.sizeTD2*2*self.sizeTD1), dataString)


            if self.is2D:
                self.f = open(path + "/ser", mode='rb')
            else:
                self.f = open(path + "fid", mode='rb')

            self.files.append(self.f)

            dataString = np.frombuffer(self.f.read(), dtype = endianess + "i4")
            if self.debug: print("len(dataString) new: ", len(dataString))

            self.data = dataString
            #this is not how it should be done.
            if self.sizeTD2 == 0:
                self.sizeTD2 = int(len(self.data) / self.sizeTD1 / 2)

            dwellTime = 1./self.sweepWidthTD2
            self.fidTime = np.linspace(0, (self.sizeTD2-1)*dwellTime, num = self.sizeTD2)

            # here we create one array of complex numbers for each of the FIDs
            # i runs overa all fids in a ser file, in case of a fid file i = 0
            # TD1 is number of FIDs, TD2 is number of datapoints in each FID
            if maxLoad > 0:
               self.sizeTD1 = maxLoad

            for i in range(0,  self.sizeTD1):
                #print "sizeTD2: ", self.sizeTD2
                #print i
                realPart = self.data[i*self.sizeTD2*2:(i+1)*self.sizeTD2*2:2]
                imagPart = sp.multiply(self.data[i*self.sizeTD2*2+1:(i+1)*self.sizeTD2*2+1:2], 1j)
                self.allFid[0].append(sp.add(realPart, imagPart))

            # here we read the experiment title (only the one stored in pdata/1):
            # could be made to read titles from all pdata folders (if needed)
            try:
                pathToTitle = directory + '/pdata/1/title'
                titleFile = open(pathToTitle, mode='r')
                self.files.append(titleFile)
                title = list(titleFile)
                self.title = [line.strip() for line in title]
            except:
                if self.debug:
                    print("No title file.")
                else:
                    pass
            #close the files we opened:
            for item in self.files:
                item.close()

            # delete all file handles so that nmrdata objects can be pickled.
            self.files = []
            del self.f

        if datatype == 'spinsight':
            chStr = "" # first read the channel, if succesful read the carrier frequency.
            carrierStr = "carrier string not assigned"
            self.is2D = False
            dataFile = path + "/data"
            print("dataFile is: ", dataFile)
            self.f = open(dataFile, mode='rb')
            self.f.seek(0)

            acqFile = path + "/acq"
            self.fACQ = open(acqFile)
            count = 0
            while True:
                count += 1
                try:
                    line = self.fACQ.readline().strip().split("=")
                    print(line)
                    if line[0] == "ch1":
                        chStr = line[1]
                        carrierStr = "sf" + chStr
                    elif line[0] == carrierStr:
                        self.carrier = float(line[1][:-1])*1e6
                    if line[0] == "dw":
                        print("Hellop: ", line[1])
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
                print("sizeTD2 is: ", self.sizeTD2)
                self.sizeTD1 = 1
                print("sizeTD1 is: ", self.sizeTD1)

            #print "Length 1: ", self.sizeTD1*self.sizeTD2*2
            #print "Length 2: ", len(self.f.read(self.sizeTD1*self.sizeTD2*2*4))
            self.f.seek(0)
            self.data = struct.unpack('>' + 'i'*self.sizeTD1*self.sizeTD2*2, self.f.read(self.sizeTD1*self.sizeTD2*2*4))
            print("Length of data: ", len(self.data))

            for i in range(self.sizeTD1):
                print(i)
                realPart = np.array(self.data[i*self.sizeTD2:(i+1)*self.sizeTD2])
                imagPart = np.array(self.data[self.sizeTD1*self.sizeTD2+i*self.sizeTD2:self.sizeTD1*self.sizeTD2+(i+1)*self.sizeTD2])
                print("Length realPart: ", len(realPart))
                print("Length imagPart: ", len(imagPart))
                self.allFid[0].append(realPart + 1j*imagPart)

            print("sizeTD1: ", self.sizeTD1)
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
            print('spec TD2 is', self.spectralFrequencyTD2)

            #SpectralFrequencyTD1
            self.f.seek(112)
            self.spectralFrequencyTD1 = struct.unpack('<d', self.f.read(8))[0]
            print("TD1 is", self.sizeTD1)

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
                print("Data imported, Number of Experiments: ", self.sizeTD1)

        if process == True:
            self.process(ls = ls, zf = zf, lb = lb, phase = phase, ft_only = ft_only)

        if datatype == 'TopSpin4':
            if self.debug:
                print("hi, this is self.debug for the TopSpin4 datatype")
            #The acqus file containts the spectral width SW_h and 2*SizeTD2 as ##$TD
            #The acqu2s file contains TD1 as ##$TD
            directory = os.path.dirname(path)
            acqusFile = open(directory + "/acqus", mode='r')
            self.files.append(acqusFile)

            if self.debug:
                print("Importing TopSpin4 data")

            #check if acqu2sfile exists, if yes, experiment is 2D!
            if os.path.isfile(directory + "/acqu2s"):
                acqu2sFile = open(directory + "/acqu2s", mode='r')
                self.files.append(acqu2sFile)
                acqu2File = open(directory + "/acqu2", mode='r')
                self.files.append(acqu2File)

                self.is2D = True
            else:
                self.is2D = False
                self.sizeTD1 = 1

            if self.debug:
                print("2D: ", self.is2D)

            #this could be crafted into a common routine which gives names of parameters
            #parameters and works the same for e.g., spinsight and topspin
            if self.debug:
                print("reading acqus file")
            count = 0
            while True:
                if self.debug:
                    print("count = ", count)
                #try:
                count += 1
                line = acqusFile.readline().strip()
                if self.debug:
                    print(line)
                if "=" in line:
                    line = line.split("=")
                elif len(line) > 0:
                    line = line.split(" ")
                elif len(line) == 0 or count > 1000:
                    if self.debug: print("Ended reading acqus file at line ", count)
                    break
                else:
                    next

                    #print line[0]
                if line[0] == "##$SW_h":
                    #this line might be chopping the last digit off....
                    #self.sweepWidthTD2 = int(float(line[1][:-1]))
                    self.sweepWidthTD2 = int(float(line[1]))
                    if self.debug: print("SweepWidthTD2: ", self.sweepWidthTD2)
                elif line[0] == "##$TD":
                    self.sizeTD2 = int(int(line[1])/2)
                    if self.debug: print("sizeTD2: ", self.sizeTD2)
                elif line[0] == "##$SFO1":
                    self.carrier = float(line[1])*1e6
                    if self.debug: print("SFO1:", self.carrier)

                elif len(line) == 0:
                    break


                if len(line[0]) > 1:
                    if "@" in line[-1]:
                        #this line contains date, time, some unknown stuff and user, does not work with all bruker files, hence try only"
                        try:
                            self.parDictionary["date"] = line[1].strip()
                            self.parDictionary["time"] = line[2].strip()
                        except:
                            pass
                    elif line[0] == "##$D":
                        delays1 = acqusFile.readline().strip()
                        delays2 = acqusFile.readline().strip()
                        self.parDictionary["d"] = [float(d) for d in delays1.strip().split(" ")] + [float(d) for d in delays2.strip().split(" ")]

                    elif line[0] == "##$L":
                        loopCounters = acqusFile.readline().strip()
                        self.parDictionary["l"] = [float(l) for l in loopCounters.strip().split(" ")]

                    else:
                        if self.debug:
                            print("the catch all else")
                        if len(line) > 1:
                            self.parDictionary[line[0][2:].strip()] = line[1].strip()
                        else:
                            if self.debug:
                                print("skipped too short line")


            if self.is2D == True:
                if self.debug:
                    print("reading acqu2s file")
                count = 0
                while True:
                    if self.debug:
                        print("count = ", count)
                    #try:
                    count += 1
                    line = acqu2sFile.readline().strip()
                    if "=" in line:
                        line = line.split("=")
                    elif len(line) == 0 or count > 1000:
                        if self.debug: print("Ended reading acqu2s file at line ", count)
                        break
                    else:
                        next

                    #print line[0]
                    if line[0] == "##$TD" and self.sizeTD1 == 0:
                        self.sizeTD1 = int(line[1])
                        if self.debug: print("sizeTD1: ", self.sizeTD1)
                    elif len(line) == 0:
                        break

                if os.path.isfile(directory + "/vdlist"):
                    if self.debug: print("VD File exists!")
                    self.vdList = np.loadtxt(directory + "/vdlist")

            if self.debug:
                print("TD2: ", self.sizeTD2)
                print("TD1: ", self.sizeTD1)
                print("Carrier:", self.carrier)

            # if self.is2D:
            #     self.f = open(path + "/ser", mode='rb')
            # else:
            #     self.f = open(path + "fid", mode='rb')#
            #           dataString = self.f.read(self.sizeTD2*2*self.sizeTD1*4)
            #          if self.debug: print "len(dataString): ", len(dataString)
            #         self.f.close()
            #
            #           # here we read the FID data from fid/ser file
            #          # first convert the datasting into a list of numbers:
            # if self.debug: print "Endianess: ", endianess
            #     self.data = struct.unpack(endianess + 'i'*(self.sizeTD2*2*self.sizeTD1), dataString)


            if self.is2D:
                self.f = open(path + "/ser", mode='rb')
            else:
                self.f = open(path + "fid", mode='rb')

            self.files.append(self.f)

            dataString = np.frombuffer(self.f.read(), dtype = endianess + "f8")
            if self.debug: print("len(dataString) new: ", len(dataString))

            self.data = dataString
            #this is not how it should be done.
            if self.sizeTD2 == 0:
                self.sizeTD2 = int(len(self.data) / self.sizeTD1 / 2)

            dwellTime = 1./self.sweepWidthTD2
            self.fidTime = np.linspace(0, (self.sizeTD2-1)*dwellTime, num = self.sizeTD2)

            # here we create one array of complex numbers for each of the FIDs
            # i runs overa all fids in a ser file, in case of a fid file i = 0
            # TD1 is number of FIDs, TD2 is number of datapoints in each FID
            if maxLoad > 0:
               self.sizeTD1 = maxLoad

            for i in range(0,  self.sizeTD1):
                #print "sizeTD2: ", self.sizeTD2
                #print i
                realPart = self.data[i*self.sizeTD2*2:(i+1)*self.sizeTD2*2:2]
                imagPart = sp.multiply(self.data[i*self.sizeTD2*2+1:(i+1)*self.sizeTD2*2+1:2], 1j)
                self.allFid[0].append(sp.add(realPart, imagPart))

            # here we read the experiment title (only the one stored in pdata/1):
            # could be made to read titles from all pdata folders (if needed)
            try:
                pathToTitle = directory + '/pdata/1/title'
                titleFile = open(pathToTitle, mode='r')
                self.files.append(titleFile)
                title = list(titleFile)
                self.title = [line.strip() for line in title]
            except:
                if self.debug:
                    print("No title file.")
                else:
                    pass
            #close the files we opened:
            for item in self.files:
                item.close()

            # delete all file handles so that nmrdata objects can be pickled.
            self.files = []
            del self.f



    def offsetCorrection(self, fromPos, toPos, fraction = 0.75, whichFid = 0):

        self.checkToPos(toPos)
        l = len(self.allFid[fromPos][0])
        startOffset = int(fraction*l)

        print("fid: ", whichFid)
        print("startOffset: ", startOffset)

        print("len allFid: ", len(self.allFid))
        #        print "len allFid[0]: ", len(self.allFid[
        print("len allFid[0]: ", len(self.allFid[0]))
        print("===============================================================")
        print("len allFid[0][" + str(whichFid) + "]: ", len(self.allFid[0][0]))


        oReal = np.mean(np.real(self.allFid[fromPos][whichFid][startOffset:]))
        stdReal = np.std(np.real(self.allFid[fromPos][whichFid][startOffset:])-oReal)

        print("offsetReal: ", oReal)
        print("stdReal: ", stdReal)

        oImag = np.mean(np.imag(self.allFid[fromPos][whichFid][startOffset:]))
        stdImag = np.std(np.imag(self.allFid[fromPos][whichFid][startOffset:])-oImag)

        print("offsetImag: ", oImag)
        print("stdImag: ", stdImag)


        self.allFid[toPos] = [np.real(fid) - oReal +1j*(np.imag(fid) - oImag) for fid in self.allFid[fromPos]]


    def lineBroadening(self, fromPos, toPos, LB):
        """Applies line broadening of given widh (in Hz) to the FID. Resulting spectrum
        (after fft is called) will be convolution of the original spectrum (fromPos)
        and Lorentzian with full-width-at-half-maximum equal to LB"""
        self.checkToPos(toPos)
        #print("Len Fid Time: {}".format(len(self.fidTime)))
        #print("Len All Fid 0: {}".format(len(self.allFid[fromPos][0])))
        self.allFid[toPos] = sp.multiply(self.allFid[fromPos][:], sp.exp(-self.fidTime[:len(self.allFid[fromPos][0])]*LB*np.pi))

    def fourierTransform(self, fromPos, toPos, only = []):
        self.checkToPos(toPos)
        if len(only) > 0:
            self.allFid[toPos] = np.array([fftshift(fft(self.allFid[fromPos][fidIndex])) for fidIndex in only])
        else:
            self.allFid[toPos] = np.array([fftshift(fft(fid)) for fid in self.allFid[fromPos]])

        self.frequency = np.linspace(-self.sweepWidthTD2/2,self.sweepWidthTD2/2,len(self.allFid[fromPos][0]))

    def baselineCorrection(self, fromPos, toPos, fitRange, scale = "Hz", order = 1, applyLocally = False):
        """Polynomial base line correction.

        - fromPos: position where current spectra are stored
        - toPos: position where corrected spectra will be stored
        - fitRange: a list of lists, with each list element giving the limits of a baseline section.
        - order: polynomial order of the baseline correction. Use order = 1 for linear baseline correction
        - applyLocally: set to True for an only local baseline correction that extends only over the entire fitRange."""

        #self.checkToPos(toPos)
        #if toPos exists, erase the data therein
        #if len(self.allFid) >toPos:
        #    self.allFid[toPos] = []
        #if toPos does not exist, create it
        #else:
        #    self.allFid.append([])
        #check that now the toPos exists:
        #assert len(self.allFid) > toPos, "toPos too high"
        #print "Hilo!"
        self.checkToPos(toPos)

        fidList = []
        for k in range(len(self.allFid[fromPos])):
            xVals = []
            yVals = []
            indices = []
            thisFid = []

            for pair in fitRange:
                i1,i2 = self.getIndices(pair, scale = scale)

                indices.extend([i1,i2])

                assert i1 != i2, "Empty Frequency Range - Frequency for Baseline Corrrection outside spectral range?"

                xVals.extend(self.frequency[i1:i2])
                yVals.extend(np.real(self.allFid[fromPos][k][i1:i2]))


            z = np.polyfit(xVals, yVals, order)


            p = np.poly1d(z)
            self.p = p

            if applyLocally:
                thisFid = self.allFid[fromPos][k]
                thisFid[min(indices):max(indices)] -= p(self.frequency[min(indices):max(indices)])
            else:
                thisFid = self.allFid[fromPos][k] - p(self.frequency)
            fidList.append(thisFid)

        #print("BaselineCorrection done. Polynomial: " + p.__repr__())
        self.allFid[toPos] = fidList


    def phase(self, fromPos, toPos, phase, degree=True):
        self.checkToPos(toPos)

        if degree == True:
            phaseFactor = np.exp(-1j*float(phase)/180.*np.pi)
        else:
            phaseFactor = np.exp(-1j*phase)
        self.allFid[toPos] = [fid*phaseFactor for fid in self.allFid[fromPos]]

    def autoPhase0(self, fromPos, index, start, stop, scale = "Hz"):
        """This function should get fromPos and index pointing to a spectrum.
        It returns the phase for maximimizing the integral over the real part
        in the spectral region of interest, in degrees."""

        i1, i2 = self.getIndices([start, stop], scale=scale)
        phiTest = np.linspace(0, 359, num = 360)

        integrals = np.zeros(np.size(phiTest))

        for k in range(len(integrals)):
            integrals[k] = np.sum(np.real(self.allFid[fromPos][index][i1:i2]*np.exp(-1j*float(phiTest[k])/180.*np.pi)))

        return phiTest[np.argmax(integrals)]

    def fwhm(self, fromPos, index, start, stop, scale = "Hz"):
        i1, i2 = self.getIndices([start, stop], scale=scale)
        x = self.frequency[i1:i2]
        y = np.real(self.allFid[fromPos][index][i1:i2])

        linewidth = fwhm.fwhm(x, y)

        if self.debug: print(("Linewidth: {} Hz".format(linewidth)))

        return linewidth


    def phaseFirstOrder(self, fromPos, toPos, phi1, degree = True, noChangeOnResonance=False, pivot = 0, scale= "Hz"):
        """This should only be applied to Fourier transformed spectral data
        It will lead to a zero phase shift at the upper end of the spectrum and to a
        phase shift of phi1 at the lower end, linear interpolation inbetween.
        this is the spinsight convention.

        If a pivot is provided the phase will not be changed at the pivot, but the total change accross the entire spectrum will still amount to phi1.
        """
        self.checkToPos(toPos)
        phaseValues = np.linspace(0,phi1,num=len(self.frequency))

        if noChangeOnResonance == True:
            pivot = 0
        elif pivot !=0:
            index = self.getIndex(pivot, scale= scale)
            phaseValues = phaseValues - phaseValues[index]

            if self.debug:
                print("Using pivot for first order phase correction")
                print("Phi1: {}".format(phi1))
                print("Degree: " + str(degree))
                print("Index: {}".format(index))
                print("Frequency at index: {} Hz".format(self.frequency[index]))

        if degree == True:
            phaseValues = phaseValues*np.pi/180

        self.allFid[toPos] =  [spectrum*np.exp(-1j*phaseValues) for spectrum in self.allFid[fromPos]]


    def leftShift(self, fromPos, toPos, shiftPoints):
        self.checkToPos(toPos)
        self.allFid[toPos] = [self.allFid[fromPos][k][shiftPoints:] for k in range(len(self.allFid[fromPos]))]
        self.fidTime = self.fidTime[:len(self.allFid[toPos][0])]
        #self.frequency = np.linspace(-self.sweepWidthTD2/2,self.sweepWidthTD2/2,len(self.fidTime))

    def zeroFilling(self, fromPos, toPos, totalPoints):
        self.checkToPos(toPos)
        z = np.zeros(totalPoints)
        self.allFid[toPos] = [np.concatenate((k, z[:-len(k)])) for k in self.allFid[fromPos]]

    def getJoinedPartialSpectra(self, fromPos, start, stop, scale = "Hz", returnX = False):
        spectra = []
        for index in range(self.sizeTD1):
            spectra.extend(self.getPartialSpectrum(fromPos, index, start, stop, scale = scale))

        if returnX:
            x = np.array(list(range(len(spectra)))) * self.sizeTD1 / float(len(spectra)) + 0.5
            return x, spectra
        else:
            return spectra

    def getPartialSpectrum(self, fromPos, index, start, stop, scale = "Hz"):
        i1, i2 = self.getIndices([start, stop], scale=scale)

        return np.real(self.allFid[fromPos][index][i1:i2])

    def integrateRealPart(self, fromPos, index, start, stop, scale="Hz", part = "real"):
        """This function integrates the real part between start and stop. standard scale is Hz
        Arguments:
        - `fromPos`:
        - `index`: index of the spectrum
        - `startFreq`: lower limit of integration
        - `stopFreq`: upper limit of integration
        - `scale`: Hz or ppm
        - `part`: real or magnitude
        """
        i1, i2 = self.getIndices([start, stop], scale=scale)

        if scale == "Hz":
            step = np.abs(self.frequency[1] - self.frequency[0])
        elif scale == "ppm":
            step = np.abs(self.ppmScale[1] - self.ppmScale[0])
        else:
            step = 1

        if part == "real":
            retVal = np.sum(np.real(self.allFid[fromPos][index][i1:i2]))*step
        elif part == "magnitude":
            retVal = np.sum(np.abs(self.allFid[fromPos][index][i1:i2]))*step

        return retVal

    def integrateAllRealPart(self, fromPos, start, stop, scale="Hz", part = "real"):
        #return all integrals by calling integrateRealPart sizeTD1 times
        return np.array([self.integrateRealPart(fromPos, k, start, stop, scale = scale, part = part)
                         for k in range(len(self.allFid[fromPos]))])


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
        i1, i2 = self.getIndices([start, stop], scale=scale)

        freqList = np.linspace(start, stop, num = (i2 - i1))
        #print freqList
        return np.sum(freqList*np.real(self.allFid[fromPos][index][i1:i2]))/self.integrateRealPart(fromPos, index, start, stop, scale = scale)


    def getIndexFromFrequency(self, freq):
        return np.argmin(abs(self.frequency - freq))

    def getIndexFromPPM(self, ppm):
        return np.argmin(abs(self.ppmScale - ppm))

    def getIndex(self, value, scale="Hz"):
        if scale == "Hz":
            return self.getIndexFromFrequency(value)
        elif scale == "ppm":
            return self.getIndexFromPPM(value)

    def getIndices(self, interval, scale="Hz"):
        i1 = self.getIndex(interval[0], scale = scale)
        i2 = self.getIndex(interval[1], scale = scale)

        if i1 > i2:
            return i2, i1
        else:
            return i1, i2


    def checkToPos(self, toPos):
        if len(self.allFid) <= toPos:
            self.allFid.append([])

    def inverseFourierTransform(self, fromPos, toPos):
          #fid = ifft(ifftshift(spectrum))
          # fid = fid[0:len(fid/2)]
          print("This function has not been checked!")

    def getPPMScale(self, reference=[], scale = 'offset'):
        """
        getPPMScale(self, reference=[], scale = 'offset')
        this function constructs a chemical shift axis given a reference of the form
        reference = [offset, ppm]

        For example if a signal of known chemical shift 3.14 ppm occurs at -350 Hz, then the
        axis would be constructed using
        getPPMScale(reference=[-350, 3.14])

        If reference is left empty, the 0 ppm value is assumed to be at the carrier frequency.

        scale can be 'offset' or 'absolute' - offset is used for signal frequency measured from
        the carrier, absolute is used of absolute signal frequency (in Hz).
        The 'absolute' is useful when creating a ppm scale based on data from
        different experiment with different SFO1
        """

        assert scale == 'offset' or scale == 'absolute', 'unknown scale'

        if reference == []:
            self.ppmScale = self.frequency/self.carrier*1e6
        else:
            #calculate the magnitude of the reference frequency:
            if scale == 'offset':
                freqRef = self.carrier + reference[0]
            elif scale == 'absolute':
                freqRef = reference[0]
            # now we know that sigmaRef = (omegaRef - omega0)/omega0 => omega0 = omegaRef/(1 + sigmaREf)
            #in this case freqRef = omega, and omega0 will be the zero ppm frequency
            #hence
            f0 = freqRef/( 1 + reference[1]*1e-6)
            #print "f0 is: ", f0
            self.ppmScale = (self.frequency + self.carrier - f0)/f0*1e6

    def process(self, lb = 0, zf = 0, phase = 0, ls = 0, ft_only = []):
        """Process routine for NMR data.

        lb: line broadening in Hz
        phase: phase correction in degree
        ls: left shift (number of points)
        """

        self.phase(0,0,phase,degree=True)
        self.leftShift(0, 1, ls)
        self.lineBroadening(1,2,lb)

        if zf > 0:
            self.zeroFilling(2, 2, zf)

        self.fourierTransform(2, 3, only = ft_only)

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
            data = list(zip(xData[start:stop], yDataR[start:stop]))

        np.savetxt(filename, data, fmt=fmt, delimiter="\t")

    def printTitle(self):
        for line in self.title: print(line)



    def autoPhase1(self, fromPos, index, start = -1e6, stop = 1e6, derivative = 1,
                   penalty = 1e3, scale  = 'Hz'):
        """Automatic phase correction (0 + 1 order) based on entropy
        minimization (Chen et al: J. Mag. Res. 158, 164-168 (2002)).
        Minimizes entropy of phased spectrum + a penalty function (which is
        equal to integral of intensity**2 in regions where intensity<0 multiplied
        by the "penalty" parameter given in autoPhase input).
        Returns phase correction coefs in radians in array [ph0, ph1]
        which can be used by method phase01 to apply the phase correction.
        Derivative should be set to 1-4, increasing penalty puts more
        emphasis on non-negative spectrum.
        By default the spectrum in range +/-1MHz around offset is considered,
        the interval can be set using the start and stop which can be
        in either 'Hz' or 'ppm' scale"""

        assert start < stop, "start should be smaller than stop"
        assert penalty > 0, "penalty shoud be possitive"
        assert type(derivative) is int, "derivative should be a (small possitive) integer"
        assert derivative > 0,  "need derivative > 0"

        spectrum = np.array(self.allFid[fromPos][index])

        # normalize the spectrum:
        spectrum = spectrum/np.abs(spectrum).sum()

        # zero everything that is out of start-stop frequency window
        if scale == 'Hz':
            for i in range(len(spectrum)):
                if self.frequency[i] < start:
                    spectrum[i] = 0
                if self.frequency[i] > stop:
                    spectrum[i] = 0
        if scale == 'ppm':
            for i in range(len(spectrum)):
                if self.ppmScale[i] < start:
                    spectrum[i] = 0
                if self.ppmScale[i] > stop:
                    spectrum[i] = 0

        #record initial values of penalty and entropy:
        penalty_start = self.__penalty(spectrum, penalty)
        entropy_start = self.__entropy(spectrum, derivative)

        # find the phase correction that minimizes the objective function
        correction = [0, 0]
        res = sp.optimize.minimize(self.__tryPhase, correction,
                                   args = (spectrum, derivative, penalty,))

        if self.debug:
            spectrum = self.__phase01(spectrum, res.x)
            print('penalty change:', self.__penalty(spectrum, penalty) - penalty_start)
            print('entropy change:', self.__entropy(spectrum, derivative) - entropy_start)

        return res.x

    def phase01(self, fromPos, toPos, correction):
        """apply zero and first order phase correction to spectra at fromPos
        and write the result to toPos. correction angles are in radians and
        are stored in array correction = [ph0, ph1]. first order
        correction leads to no change at first point of spectrum and maximum
        (ph1) change at the last point.
        This function can be used to apply the phase correction returned by
        autoPhase1"""
        self.checkToPos(toPos)
        #here we apply the correction
        self.allFid[toPos] = [ self.__phase01(spectrum, correction) for spectrum in self.allFid[fromPos]]


    def __phase01(self, spectrum, correction):
        """Returns a spectrum (np.array) to which a specified phase correction
        was applied. ph0 and ph1 are in rad"""
        ph0, ph1 = correction[0], correction[1]
        phaseValues = np.linspace(0, ph1, num = len(spectrum)) + ph0
        corrections = np.exp(1j*phaseValues)

        return np.array([spectrum[i]*corrections[i] for i in range(len(spectrum))])

    def __entropy(self, spectrum, m):
        """Calculates get m-th derivative of the real part of spectrum and
        returns entropy of its absolute value. """
        assert type(m) is int, 'm should be a (possitive) integer'
        assert m > 0, 'need m > 0'

        #get the real part of the spectrum
        spect = np.array(spectrum)
        spect = spect.real

        # calculate the m-th derivative of the real part of the spectrum
        spectrumDerivative = spect
        for i in range(m):
            spectrumDerivative = np.gradient(spectrumDerivative)

        # now get the entropy of the abslolute value of the m-th derivative:
        entropy = sp.stats.entropy(np.abs(spectrumDerivative))
        return entropy



    def __penalty(self, spectrum, gamma):
        """return penalty function for the spectrum - sum of squares of
        all negative points in normalized spectrum multiplied by gamma"""


        penalty = 0
        #normalize the real part of the spectrum:
        spect = spectrum.real/np.abs(spectrum.real).sum()
        #calculate the penalty for the normalized real part
        for point in spect:
            if point < 0:
                penalty += point**2
        return penalty*gamma


    def __tryPhase(self, correction, spectrum, m, gamma):
        """Apply the phase correction to the spectrum, evaluate
        entropy and penalty of the resulting spectrum and return
        their sum (aka objective function)"""


        phased = self.__phase01(spectrum, correction)
        objective = self.__entropy(phased, m) + self.__penalty(phased, gamma)
        return objective

    def normalizeIntensity(self, fromPos, toPos, scaling = 1.0):
        """Takes spectrum in fromPos, divides the intensities by number of scans
        and receiver gain and writes the resulting spectrum to toPos. Useful for
        comparing intensities of specta taken with different settings. Optional
        parameter scaling can be used to correct for additional effects (e.g.
        mass). Spectrum will be divided by this factor - higher scaling means
        lower resulting intensity."""
        self.checkToPos(toPos)
        #delete whatever is in toPos:
        self.allFid[toPos] = []
        #scaling factor:
        factor = float(self.parDictionary["$NS"])*float(self.parDictionary["$RG"])*scaling
        for spectrum in self.allFid[fromPos]:
            self.allFid[toPos].append([point/factor for point in spectrum])

    def __getitem__(self, key):
        return [np.real(self.allFid[key][x]) for x in range(len(self.allFid[key]))]

    def __len__(self):
        return len(self.allFid)





class container(object):
      def __init__(self):
            self.content = []

      def addContent(self, path, type):
            self.content.append(nmrData(path, type))
            return len(self.content)





if __name__ == "__main__":
      print(nmrData.__doc__)

      nmrData = nmrData(2011051010, 'TopSpin')
