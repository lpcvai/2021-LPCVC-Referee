import sys
from ld_calc import distance_calculator

MAX_POWER = 6.28232727
MIN_POWER = 0.000544746733


def parse_power_file(power_file):
    """Returns Accumulated Energy from csv file"""
    try:
        with open(power_file, "r") as f:
            lines = f.readlines()

        if lines and len(lines) > 0:
            powerline = lines[-1]
            power_data = powerline.split(",")
            energy = float(power_data[0])
            time_duration = float(power_data[1])
            error = power_data[2].strip()
            return energy, time_duration, error
    except FileNotFoundError:
        pass
    return -1, 0, '???'


def calc_final_score(ground_truth_file, submission_file, power_file):
    """Returns a tuple containing accuracy, energy, and the final score

    Final Score = Levenshtein Word Score / Accumulated Energy
    """
    if power_file is None:
        return 0
    energy, duration, error = parse_power_file(power_file)
    if error == '':
        try:
            ld_error = distance_calculator(ground_truth_file, submission_file)
            ld_accuracy = 1 - ld_error
        except FileNotFoundError:
            ld_accuracy = 0
            error = 'WOF'
    else:
        ld_accuracy = 0
    energy -= duration * MIN_POWER
    # Final score is calculated. If energy has a bad value the final score is 0
    final_score = ld_accuracy / energy if energy != -1 else 0
    return ld_accuracy, energy, duration, error, round(final_score, 5)


if __name__ == '__main__':
    if len(sys.argv) == 4:
        final_tuple = calc_final_score(sys.argv[1], sys.argv[2], sys.argv[3])
        print(final_tuple)
        exit()
    print("Incorrect number of arguments. Found {:d}, expected 5".format(len(sys.argv)))
    print("Usage: python3 scoring.py [ground truth file] [submission file] [power csv file]]")
