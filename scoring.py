import sys
from LDCalc import distanceCalc


def parsePowerFile(powerFile):
    with open(powerFile, "r") as f:
        lines = f.readlines()

    if lines:
        powerline = lines[-2]
        powerdata = powerline.split(",")
        power = float(powerdata[7])
        return power
    return -1

def calc_final_score(groundTruthFile, submissionFile, powerFile):
    if powerFile == None:
        return 0
    ldError = distanceCalc(groundTruthFile, submissionFile)
    ldAccuracy = 1 - ldError
    power = parsePowerFile(powerFile)
    final_score = ldAccuracy / (1 + power)
    return (ldAccuracy, power, final_score)



if __name__ == '__main__':
    watt_hours = parsePowerFile("power_csv.csv")
    print(watt_hours)
    if len(sys.argv) == 3:
        avgDist = distanceCalc(sys.argv[1], sys.argv[2])
        print("%f" %(1 - avgDist))
    else:
        print("Incorrect number of arguments. Found {:d}, expected 3".format(len(sys.argv)))