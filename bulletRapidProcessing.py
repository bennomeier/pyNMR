from __future__ import division
import numpy as np
import matplotlib.pyplot as plt
import os
import nmrDataMod as ndm



class Experiment(ndm.nmrData):
    """Extension/wrapper to nmrData class that does basic processing on init
    and has several methods specific to the bullet DNP experiments. """

    def __init__(self, path, folder, expno, lb = 0, phaseCorrIndex = -1,
    bcOrder = 1, interface = "ipynb"):
        """ Loads the specified NMR experiment.
        Does basic NMR processing. PhaseCorrIndex - index of FID
        which will be used for autophase. bcOrder - order of polynomial
        to be used for baseline correction. Intensities are corrected for
        to numuber of scans and receiver gain. """


        # get path to data to load them using the parent __init__
        self.path = path
        self.fullPath = path + folder + "/" + str(expno) + "/"
        self.folder = folder
        self.expno = expno
        self.interface = interface
        self.scaling = None

        # basic processing parameters:
        leftShift = 70
        self.lb = lb

        # load the data and do basic processing:
        super(Experiment, self).__init__(self.fullPath, "TopSpin",
        process = True, ls = leftShift, lb = self.lb,
        phase = 45, debug = False)

        # find correct phase and apply phase correction
        phase = self.autoPhase0(3, phaseCorrIndex, -60000, 60000)
        self.phase(3,3,phase)

        # baseline correction
        baselineCorr = [[-400e3,-60e3], [60e3, 400e3]]
        self.bcOrder = bcOrder
        self.baselineCorrection(3, 4, baselineCorr,
        order = self.bcOrder)

        # correct intensity to number of scans and receiver gain
        self.normalizeIntensity(4,5)


    def spectrum(self, indexList = [-1], center = 0, width = 60000.0,
    returnData = False, showFigure = True, saveFigure = False):
        """Shows selected spectra (indexList, the default corresponds
        to the last spectrum only. Center and width specify the frequency interval
        in which the spectra are plotted.)"""

        pos = -1
        xmin = center - width/2
        xmax = center + width/2

        result = [self.frequency]
        for index in indexList:
            result.append(self.allFid[pos][index])
            # plt.plot(self.frequency, self.allFid[pos][index], label = str(index))
        result = np.array(result)

        if showFigure:
            if self.interface == 'ipynb':
                for i in range(result.shape[0] - 1):
                    plt.plot(result[0], result[i+1], label = str(indexList[i]))
                plt.xlim(xmin, xmax)
                plt.legend()
                plt.grid()
                plt.xlabel("Frequency offset (Hz)")
                plt.ylabel("Intensity (arb. u.)")
                plt.title("Spectrum: " + self.folder+"/" + str(self.expno))
                plt.show()
                if saveFigure:
                    name = "spect_" + self.folder + "_" +str(self.expno) +".pdf"
                    plt.savefig(name)

        if returnData:
            return result

    def nutation(self, center = 0, width = 60000, returnData = False,
    showFigure = True, saveFigure = False):
        """Shows nutation curve. Specta are integrated in specified interval
        (center and width in Hz)"""

        # get pulse durations
        path = self.fullPath + "vplist"
        if os.path.isfile(path):
            # dirty workaround to parse the file - np does not understand the 'u'
            self.vpList = np.loadtxt(path, delimiter = 'u', usecols = [0])

        integrals = []
        for index in range(len(self.allFid[-1])):
            start = center -width/2
            stop = center + width/2
            integral = self.integrateRealPart(-1, index, start, stop )
            integrals.append(integral)
        self.integrals = np.array(integrals)

        # this helps to process incomplete experiment
        result = [self.vpList[:len(self.integrals)], self.integrals]
        result = np.array(result)

        if showFigure:
            if self.interface == 'ipynb':
                plt.plot(result[0], result[1], "--o")
                plt.grid()
                plt.xlabel("Pulse Duration (us)")
                plt.ylabel("Intensity")
                plt.title("Nutation:" + self.folder+"/" + str(self.expno))
                if saveFigure:
                    name = "nut_" + self.folder + "_" +str(self.expno) +".pdf"
                    plt.savefig(name)
                plt.show()


        if returnData:
            return result

    def getScaling(self, intensityThermal, pulseThermal = 10, pulseBuildup = 1,
    temperature = 4.23, larmorFreq = 71.76, factor = 1, returnData = False):
        """This generates a dict with intensity and corresponding polarization.
        Useful to translate intensities in DNP buildups to nuclear polarization
        levels.
        Input is thermal intensity at given temperature, pulse used to observe it,
        pulse that was used for observation in DNP buildup, Larmor Frequency of
        the observed nucleus and a factor corresponding to different sensitivities
        of the rf at buildup and DNP temperatures (if the rf is 2x more sensitive
        at the DNP temperature than at thermal temperature then factor = 2).
        You can override this by manually writing the self.scaling dict.
        """

        h = 4.136e-15 #eV s
        k = 8.617e-5 # eV/K

        #calculate thermal polarization
        polarization = np.tanh(h*larmorFreq*1e6/(2*k*temperature))
        intensity = intensityThermal/np.sin(pulseThermal/180*np.pi)*np.sin(pulseBuildup/180*np.pi)*factor

        self.scaling = {"intensity":intensity, "polarization":polarization}
        if returnData:
            return self.scaling


    def buildup(self, center = 0, width = 60000, returnData = False,
                delay = 1, getPolarization = False, saveFigure = False,
                showFigure = True):

        self.delay = delay

        # generate time axis
        n = len(self.allFid[-1])
        self.time = np.linspace(delay,(n)*delay, n)

        # get the integrals
        integrals = []
        start = center -width/2
        stop = center + width/2
        for index in range(len(self.allFid[-1])):
            integral = self.integrateRealPart(-1, index, start, stop )
            integrals.append(integral)
        self.integrals = np.array(integrals)

        # calculate polarization
        if getPolarization:
            if self.scaling:
                self.factor = self.scaling["polarization"]/self.scaling["intensity"]
                self.integrals = self.integrals*self.factor
            else:
                print("No scaling found, you need to run getScaling first!")

        self.result = np.array([self.time, self.integrals])

        if showFigure:
            if self.interface == "ipynb":
                plt.plot(self.result[0], self.result[1], "--o")
                plt.grid()
                plt.xlabel("Time (s)")
                if getPolarization:
                    plt.ylabel("Polarization (absolute)")
                else:
                    plt.ylabel("Integral Intensity")
                plt.title("Buildup: " + self.folder+"/" + str(self.expno))
                if saveFigure:
                    name = "build_" + self.folder + "_" +str(self.expno) +".pdf"
                    plt.savefig(name)
                plt.show()

        if returnData:
            return self.result
