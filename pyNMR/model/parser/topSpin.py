from pynmr.model.parser.nmrData import nmrData
import pysftp
import numpy as np
import scipy as sp
import os


def TopSpinSSH(self, path, exp, localPath, server, username, password,
               endianess="<", debug=False):
    """This function first copies the data from via ssh,
    and then initialize and returns a TopSpin Object using the local data.

    path: path on the server
    server: server
    username: username
    password: password
    localPath: path to store topSpin data locally
    endianess = "<" : optional Keyword for endianess"""

    with pysftp.Connection(server, username=username, password=password) as sftp:
        with sftp.cd(path):             # temporarily chdir to public
            sftp.get_r(exp, localPath)         # get a remote file
            
    return TopSpin(localPath + exp, endianness=endianess, debug=debug)


class TopSpin(nmrData):
    def __init__(self, path, endianess="<", debug=False, maxLoad=0):
        """This class only takes the following arguments:

        - path: path to an NMR experiment

        All other arguments are optional Keyword Arguments:
        - endianess = "<"
        - debug = False: set to True to output additional debuging information.
        - maxLoad = 0: set to an integer value to limit loading and processing
to an NMR experiment, an optional argument for endianess"""
        super().__init__(debug = debug)

        self.files = []
        
        if self.debug:
            print("hi, this is self.debug for the TopSpin datatype")

        #The acqus file containts the spectral width SW_h and 2*SizeTD2 as ##$TD
        #The acqu2s file contains TD1 as ##$TD
        directory = os.path.dirname(path)
        acqusFile = open(directory + "/acqus", mode='r')
        self.files.append(acqusFile)

        if self.debug:
            print("Importing TopSpin data")

        #check if acqu2sfile exists, if yes, experiment is 2D.
        if os.path.isfile(directory + "/acqu2s"):
            acqu2sFile = open(directory + "/acqu2s", mode='r')
            self.files.append(acqu2sFile)
            acqu2File = open(directory + "/acqu2", mode='r')
            self.files.append(acqu2File)

            self.is2D = True
        else:
            self.is2D = False
            self.sizeTD1 = 1

        if self.debug: print("2D: ", self.is2D)

        #this could be crafted into a common routine which gives names of parameters
        #parameters and works the same for e.g., spinsight and topspin

        if self.debug: print("reading acqus file")
        count = 0

        # read the acqusFile
        while True:
            if self.debug: print("count = ", count)

            count += 1
            line = acqusFile.readline().strip()
            if self.debug: print(line)
            if "=" in line:
                line = line.split("=")
            elif len(line) > 0:
                line = line.split(" ")
            elif len(line) == 0 or count > 1000:
                if self.debug: print("Ended reading acqus file at line ", count)
                break
            else:
                next

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
                elif line[0] == "##$O1":
                    self.parDictionary["O1"] = float(line[1])
		elif line[0] == "##$PLW":
		     powers1 = acqusFile.readline().strip()
		     powers2 = acqusFile.readline().strip()
		     self.parDictionary["powers"] = [float(p) for p in powers1.strip.split(" ")] + [float(p) for p in powers2.strip.split(" ")] 
                else:
                    if self.debug: print("the catch all else")
                    if len(line) > 1:
                        self.parDictionary[line[0][2:].strip()] = line[1].strip()
                    else:
                        if self.debug: print("skipped too short line")


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
                elif line[0] == "##$SW_h":
                    self.sweepWidthTD1 = int(float(line[1]))
                elif len(line) == 0:
                    break

            if os.path.isfile(directory + "/vdlist"):
                if self.debug: print("VD File exists!")
                self.vdList = np.loadtxt(directory + "/vdlist")

        if self.debug:
            print("TD2: ", self.sizeTD2)
            print("TD1: ", self.sizeTD1)
            print("Carrier:", self.carrier)

        if self.is2D:
            self.f = open(path + "/ser", mode='rb')
        else:
            self.f = open(path + "fid", mode='rb')

        self.files.append(self.f)

        dataString = np.frombuffer(self.f.read(), dtype = endianess + "i4")
        if self.debug: print("len(dataString) new: ", len(dataString))

        self.data = dataString

        if self.sizeTD2 == 0:
            self.sizeTD2 = int(len(self.data) / self.sizeTD1 / 2)

        self.dwellTime = 1./self.sweepWidthTD2
        self.fidTime = np.linspace(0, (self.sizeTD2-1)*self.dwellTime,
                                   num=self.sizeTD2)

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
        # close the files we opened:
        for item in self.files:
            item.close()

        # delete all file handles so that nmrdata objects can be pickled.
        self.files = []
        del self.f

        delay = float(self.parDictionary["$GRPDLY"])

        self.shiftPoints = int(np.floor(delay))
        pointsRemaining = delay - self.shiftPoints

        self.timeShift = pointsRemaining*self.dwellTime

        if self.debug:
            print("Left Shift by {:d} points.".format(self.shiftPoints))
            print("Points Remaining: {:.3f} points.".format(pointsRemaining))
            print("Time Shift: {:.3e} s.".format(self.timeShift))
