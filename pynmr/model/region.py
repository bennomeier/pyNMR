#import os
import dill

class RegionStack(object):
    def __init__(self, regionSets = {}):
        self.regionSets = regionSets

    def save(self, pathToRegionStackFile):
        dill.dump(self, file = open(pathToRegionStackFile, "wb"))

    def add(self, name, scale="ppm", regions=[]):
        if name not in self.regionSets.keys():
            self.regionSets[name] = RegionSet(name, scale=scale, regions=regions)
        else:
            raise Exception("Region already in RegionStack")

    def __getitem__(self, key):
        return self.regionSets[key]


def regionStackFromFile(pathToRegionStackFile):
    return dill.load(open(pathToRegionStackFile, "rb"))
    

class RegionSet(object):
    def __init__(self, name, scale="ppm", regions = []):
        self.name = name
        self.scale = scale
        self.regions = regions


    
