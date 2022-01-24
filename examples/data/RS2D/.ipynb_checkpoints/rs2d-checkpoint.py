# this is just exploring the files

pathSerie = "./19/Serie.xml"
pathHeader = "./19/header.xml"

from bs4 import BeautifulSoup

with open(pathHeader) as fp:
    soup = BeautifulSoup(fp, 'lxml')

# the file size is 478272 for 12 fids, which gives 39856 bytes per fid.
# each fid has 4982 points, so this gives 8 bytes per point.
