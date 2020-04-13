import sys
from LDCalc import distanceCalc


if __name__ == '__main__':
    if len(sys.argv) == 3:
        avgDist = distanceCalc(sys.argv[1], sys.argv[2])
        print("%f" %(1 - avgDist))
    else:
        print("Incorrect number of arguments. Found {:d}, expected 3".format(len(sys.argv)))