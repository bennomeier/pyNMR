"""This is the abstract model.
There sould be only one instance of the pyNmrDataModel,
and this will contain all data, processors, etc. that are
 visualized by the viewer.

There may however be multiple instances of pyNmrDataSet, each corresponding
to one (possibly multi-dimensional) NMR data set.

The nmrDataModel is passed to the gui for visualization and modification."""


class pyNmrDataModel(object):
    def __init__(self, dataSet=None):
        self.dataSets = []

        if dataSet:
            self.dataSets.append(dataSet)


class pyNmrDataSet(object):
    def __init__(self, data=None, processor=None):
        self.data = data
        self.processorStack = []
        self.regionStack = []

        if processor:
            self.processorStack.append(processor)

            processor.runStack(self.data)

