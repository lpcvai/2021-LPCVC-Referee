import sys
from LDCalc import distanceCalc

MAX_POWER = 6.28232727

def parsePowerFile(powerFile):
    """Returns Accumulated Energy from csv file"""
    with open(powerFile, "r") as f:
        lines = f.readlines()

    if lines:
        powerline = lines[-2]
        powerdata = powerline.split(",")
        energy = float(powerdata[7])
        return energy
    return -1

def calc_final_score(groundTruthFile, submissionFile, powerFile):
    """Returns a tuple containing accuracy, energy, and the final score

    Final Score = Levenshtein Word Score / Accumulated Energy
    """
    if powerFile == None:
        return 0
    ldError = distanceCalc(groundTruthFile, submissionFile)
    ldAccuracy = 1 - ldError
    energy = parsePowerFile(powerFile)
    # Final score is calculated. If energy has a bad value the final score is 0
    final_score = ldAccuracy / (energy) if energy != -1 else 0
    return (ldAccuracy, energy, round(final_score,5))



if __name__ == '__main__':
    if len(sys.argv) == 4:
        final_tuple = calc_final_score(sys.argv[1], sys.argv[2], sys.argv[3])
        print(final_tuple)
        exit()
    print("Incorrect number of arguments. Found {:d}, expected 5".format(len(sys.argv)))
    print("Usage: python3 scoring.py [ground truth file] [submission file] [power csv file]]")
