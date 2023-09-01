from os import listdir
from os.path import isfile, join

photosPath = "./example-photos"
onlyfiles = [f for f in listdir(photosPath) if isfile(join(photosPath, f))]

print(onlyfiles)
