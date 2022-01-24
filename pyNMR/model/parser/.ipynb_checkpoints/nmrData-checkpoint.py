""" This file defines the NMR data object. All parsers are children of this object.

This object defines the plus and minus operations

"""
from datetime import datetime


class nmrData(object):
    def __init__(self, debug = False):
        self.datatype = ""
        self.carrier = 0

        self.allFid = []
        self.allFid.append([])

        self.allSpectra = []
        #self.allSpectra.append([])

        self.sizeTD1 = 0
        self.title = ""
        self.parDictionary = {}
        self.debug = debug
        self.is2D = False

        self.timeParsed = datetime.now()

    def __print__(self):
        print("NMR Data Object, parsed on " + self.timeParsed)

        
