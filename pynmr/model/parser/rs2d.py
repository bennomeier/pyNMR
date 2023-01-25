from pynmr.model.parser.nmrData import nmrData
import numpy as np
import scipy as sp
import os
import struct

from bs4 import BeautifulSoup

class RS2D(nmrData):
    def __init__(self, path, endianess=">", debug=False, maxLoad=0):
        """This class only takes the following arguments:

        - path: path to an NMR experiment

        All other arguments are optional Keyword Arguments:
        - endianess = ">"
        - debug = False: set to True to output additional debuging information.
        - maxLoad = 0: set to an integer value to limit loading and processing
to an NMR experiment, an optional argument for endianess"""
        super().__init__(debug = debug)
        
        if self.debug:
            print("hi, this is self.debug for the RS2D datatype")

        #The acqus file containts the spectral width SW_h and 2*SizeTD2 as ##$TD
        #The acqu2s file contains TD1 as ##$TD
        directory = os.path.dirname(path)
        acqusFile = directory + "/header.xml"


        if self.debug:
            print("Importing RS2D data")

        with open(acqusFile) as fp:
            soup = BeautifulSoup(fp, 'lxml-xml')

        allEntries = soup.find_all("entry")

        for e in allEntries:
            keyName = e.key.string
            keyValue = e.value.value.string
            res = e.find_all("value", {"xsi:type": "numberParam"})

            if len(res) > 0:
                r = float(e.value.value.string)
                if r.is_integer():
                    self.parDictionary[e.key.string] = int(r)
                else:
                    self.parDictionary[e.key.string] = r

        self.sizeTD1 = self.parDictionary["ACQUISITION_MATRIX_DIMENSION_2D"]
        self.sizeTD2 = self.parDictionary["ACQUISITION_MATRIX_DIMENSION_1D"]
        self.sweepWidthTD2 = self.parDictionary["SPECTRAL_WIDTH"]

        if self.sizeTD1 > 1:
            self.is2D = True
        else:
            self.is2D = False
        
        if self.debug: print("2D: ", self.is2D)

        if self.debug:
            print("TD2: ", self.sizeTD2)
            print("TD1: ", self.sizeTD1)
            print("Carrier:", self.carrier)

        with open(path + "/data.dat", mode='rb') as f:
            dataString = struct.unpack(">" + "f"*(self.sizeTD2*self.sizeTD1)*2, f.read())

        if self.debug: print("len(dataString) new: ", len(dataString))

        self.data = dataString

        if self.sizeTD2 == 0:
            self.sizeTD2 = int(len(self.data) / self.sizeTD1 / 2)

        self.dwellTime = 1./self.sweepWidthTD2
        self.fidTime = np.linspace(0, (self.sizeTD2-1)*self.dwellTime,
                                   num=self.sizeTD2)

        # here we create one array of complex numbers for each of the FIDs
        # i runs over all fids in a ser file, in case of a fid file i = 0
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
            title = list(titleFile)
            self.title = [line.strip() for line in title]
        except:
            if self.debug:
                print("No title file.")
            else:
                pass

        self.shiftPoints = self.parDictionary["DIGITAL_FILTER_SHIFT"]
        #pointsRemaining = delay - self.shiftPoints

        #self.timeShift = pointsRemaining*self.dwellTime

        #if self.debug:
        #    print("Left Shift by {:d} points.".format(self.shiftPoints))
        #    print("Points Remaining: {:.3f} points.".format(pointsRemaining))
        #    print("Time Shift: {:.3e} s.".format(self.timeShift))
