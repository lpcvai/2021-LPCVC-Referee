import sys
from LDCalc import distanceCalc

MAX_POWER = 6.28232727
MIN_POWER = 0.000544746733

def parsePowerFile(powerFile):
    """Returns Accumulated Energy from csv file"""
    try:
        with open(powerFile, "r") as f:
            lines = f.readlines()

        if lines:
            powerline = lines[-1]
            powerdata = powerline.split(",")
            energy = float(powerdata[0])
            timeDurr = float(powerdata[1])
            error = powerdata[2].strip()
            return energy, timeDurr, error
    except Exception:
        pass
    return -1, 0, '???'

def calc_final_score(groundTruthFile, submissionFile, powerFile):
    """Returns a tuple containing accuracy, energy, and the final score

    Final Score = Levenshtein Word Score / Accumulated Energy
    """
    if powerFile == None:
        return 0
    energy, timeDurr, error = parsePowerFile(powerFile)
    if error == '':
        try:
            ldError = distanceCalc(groundTruthFile, submissionFile)
            ldAccuracy = 1 - ldError
        except Exception:
            ldAccuracy = 0
            error = 'WOF'
    else:
        ldAccuracy = 0
    energy -= timeDurr * MIN_POWER
    # Final score is calculated. If energy has a bad value the final score is 0
    final_score = ldAccuracy / (energy) if energy != -1 else 0
    return (ldAccuracy, energy, timeDurr, error, round(final_score,5))



if __name__ == '__main__':
    if len(sys.argv) == 4:
        final_tuple = calc_final_score(sys.argv[1], sys.argv[2], sys.argv[3])
        print(final_tuple)
        exit()
    print("Incorrect number of arguments. Found {:d}, expected 5".format(len(sys.argv)))
    print("Usage: python3 scoring.py [ground truth file] [submission file] [power csv file]]")
