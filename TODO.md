##TODO list

Incomplete and not in order of improtance, but we have to stat somewhere:

 - [ ] comment the code a bit more

 - [ ] docstrings - more of them, longer, more informative

 - [ ] examples - create a folder with example ipython notebooks

 - [ ] tests - write some unit tests so we can confirm that the sofrware works as expected 

 - [ ] background - write a method to create a background spectrum that can then be subtracted from the exeperimental one (e.g. in integration)

 - [ ] endians - add optional argument for __init__ that lets user specify endian. Perhaps write a dedicated import function that is called from the __init__

 - [ ] copy - create a method that will return another instance ot the whole nmrData object 

 - [ ] automatic first order phase correction 

 - [ ] load carrier frequency automatically for all experiment types 
(now this does not work at least for 2D TopSpin) 

 - [x] getPPMScale shold have an option to use absolute frequency (instead of 
offset from the current carrier), this can be done via an optional argument:
getPPMScale(self, reference=[], scale = 'offset') 

 - [ ] check getPPMScale

 - [ ] ISSUE: fromPos/toPos - turn them into optional arguments (with: default being fromPos = len(self.allFid) - 1, toPos = len(self.allFid) ). Breaks backward compatibility ( = BBC).

 - [ ] ISSUE: stop storing all the history explicitly in the allFId, instead store only the latest FID and only the latest spectrum (with their time/frequency scales) and keep a log of all the processing commands. BBC

 - [ ] ISSUE: separate FIDs from spectra. Currently everything is stored in allFID, time and frequency axes are stored separately and there is only one version of each. It would be better to reserve the allFid for time domain data only (and store the all the time axes as well). The spectra could be stored in something like allSpectra and again the frequency axes should be stored as well (e.g. imagine you want to compare spectra with and without zero filling).  BBC 


