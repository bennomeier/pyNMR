import glob
import sys
import os

#directory = input("Enter Directory: ")
#print("Directory: ", directory)



folder = "/home/benno/Dropbox/RESEARCH/bullet/experiments/H2O17atC60/20170510/H2OC60ODCB20170408/"
#folder = askdirectory()

subdirectories = [x[0] for x in os.walk(folder)]

experiments = set()

for i in subdirectories:
    # now add these to a set.
    experiments.add(i.split(folder)[1].split("/")[0])

for i in experiments:
    try:
        pathToTitle = folder +  i + '/pdata/1/title'
        titleFile = open(pathToTitle, mode='r')
        #self.files.append(titleFile)
        title = list(titleFile)
        titleF = [line.strip() for line in title]
        print("\n\n {} \n========================".format(i))
        for i in title:
            print(i.rstrip())
    except:
        print("Some Error")
        print("No title file.")

