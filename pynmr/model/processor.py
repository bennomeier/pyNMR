# this file needs more thinking.

# every operation has a name, and a bunch of (named) parameters with associated values
# sometimes a text entry is sensible for the input, sometimes a slider might be preferred.

# It is conceivable to write a class for every operation.
# This might be sensible, because every operation may need a custom widget anyway,
# along with a corresponding class.
import numpy as np

class Processor(object):
    def __init__(self, operationStack):
        """Define a pyNMR Processor. A processor is a list of operations
        that can be applied to NMR data."""

        self.operationStack = operationStack

    def runStack(self, nmrData, endpoint=-1, startpoint=0):
        nmrData.reset()

        if endpoint > 0:
            opList = self.operationStack[:endpoint]
        else:
            opList = self.operationStack

        for op in opList:
            print(op.name)
            op.run(nmrData)
        
    def __getitem__(self, index):
        return self.operationStack[index]
