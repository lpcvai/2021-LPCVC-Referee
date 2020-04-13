import sys
from LDCalc import distanceCalc

MAX_POWER = 6.28232727

def parsePowerFile(powerFile):
    with open(powerFile, "r") as f:
        lines = f.readlines()

    if lines:
        powerline = lines[-2]
        powerdata = powerline.split(",")
        power = float(powerdata[7])
        return power
    return -1

def calc_final_score(groundTruthFile, submissionFile, powerFile, videoLength):
    if powerFile == None:
        return 0
    videoLengthHours = videoLength / 360.0
    ldError = distanceCalc(groundTruthFile, submissionFile)
    ldAccuracy = 1 - ldError
    power = parsePowerFile(powerFile)
    final_score_a = ldAccuracy * (1 - (power / (3 * MAX_POWER * videoLengthHours)))
    final_score_b = ldAccuracy / (1 + power)
    return (ldAccuracy, power, final_score_a, final_score_b)



# if __name__ == '__main__':
#     watt_hours = parsePowerFile("power_csv.csv")
#     print(watt_hours)
#     if len(sys.argv) == 3:
#         avgDist = distanceCalc(sys.argv[1], sys.argv[2])
#         print("%f" %(1 - avgDist))
#     else:
#         print("Incorrect number of arguments. Found {:d}, expected 3".format(len(sys.argv)))