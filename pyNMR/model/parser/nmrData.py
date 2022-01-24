""" This file defines the NMR data object. All parsers are children of this object.

This object defines the plus and minus operations

"""
from datetime import datetime


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

        self.timeParsed = datetime.now()

    def reset(self):
        self.allFid = [self.allFid[0]]
        self.allSpectra = []

    def __print__(self):
        print("NMR Data Object, parsed on " + self.timeParsed)


