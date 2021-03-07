# install with pip3 install python-Levenshtein
from Levenshtein import distance
from collections import OrderedDict
import itertools
import sys


def reader(file_name):
    """Parse a submission file into a dictionary.

    The dictionary that is generated in this function is analyzed in a separate
    function to determine the Levenshtein Word Score
    """
    with open(file_name) as txt:
        # Retrieve raw data from file
        org_key_and_values = txt.readlines()
    org_key_and_values = [x.lower() for x in org_key_and_values]

    semi_pos = 0
    keys_and_values = org_key_and_values
    i = 0
    while i < len(org_key_and_values[0]):
        # Loop converts one line default answer format to seperate lines
        if org_key_and_values[0][i] == ';':
            semi_pos = i
        elif org_key_and_values[0][i] == ':':
            if semi_pos != 0:
                keys_and_values[0] = org_key_and_values[0][0:semi_pos] + '|' \
                                     + org_key_and_values[0][(semi_pos + 1):]
        i += 1
    keys_and_values = org_key_and_values[0].split("|")

    key = []
    val = []
    i = 0
    while i < len(keys_and_values):
        # This loop separates keys and values into a dictionary containing
        # the submission
        key_value_list = keys_and_values[i].split(":")
        value_list = key_value_list[1].split(";")
        key_value = [key_value_list[0]]
        for value in value_list:
            key_value.append(value)
        key.append(key_value[0].rsplit())
        inner_value_list = []
        j = 0
        for value in key_value:
            if j != 0:
                inner_value_list.append(value.rsplit())
            j += 1
        val.append(inner_value_list)
        i += 1

    response = OrderedDict()
    for keyNow, value in zip(key, val):
        response.update({str(keyNow): value})
    return response


def flatten(data):
    """Returns a flattened dictionary"""
    merged = list(itertools.chain(*data))
    return merged


# Method to calculate the distance between the values between two dictionaries
def distance_calculator(real_text_file, actual_text_file):
    """Returns a final Levenshtein Word Score"""
    real_data = reader(real_text_file)
    actual_data = reader(actual_text_file)
    for key in actual_data.keys():
        if actual_data[key] == [[]]:
            actual_data[key] = [[""]]

    frame_and_combo_list = []
    for key in real_data:
        # This loop creates the combinations of all the different answers
        # for a given question
        all_real_answers = flatten(real_data[key])
        all_answers = flatten(actual_data[key])
        for realAnswer in all_real_answers:
            curr_frame = []
            if not all_answers:
                # Check to account for case in which submission does not
                # generate an answer for a given question
                curr_frame.append([realAnswer, ""])
                frame_and_combo_list.append(curr_frame)
                continue
            for answer in all_answers:
                curr_frame.append([realAnswer, answer])
            frame_and_combo_list.append(curr_frame)

    # Evaluating distance across frame_and_combo_list into frame_and_score_list
    frame_and_score_list = []
    for i in range(len(frame_and_combo_list)):
        # This loop evaluates the distance across the ground truth and the
        # submission. This loop generates a list of lists of the format
        # [["ground_truth", score], .....]
        ground_truth = frame_and_combo_list[i][0][0]
        min_score = float("inf")
        for dataValue in frame_and_combo_list[i]:
            # This loop generates the best Levenshtein distance for a given
            # answer
            lv_dist = distance(ground_truth, dataValue[1])
            if lv_dist < min_score:
                min_score = lv_dist
        frame_and_score_list.append([ground_truth, min_score])

    final_score = final_score_calculator(frame_and_score_list)
    return final_score


def final_score_calculator(score_list):
    """Returns final Levenshtein Word Score

    Iterates through all the scores for the various queries. Final score is
    calculated by averaging the ratio of the score with the word length of
    the ground truth. A given score is capped at 1.
    """
    final_score = 0.0
    for item in score_list:
        word_len = len(item[0])
        curr_score = item[1]
        curr_final = float(curr_score / word_len)
        if curr_final > 1:
            # Cap error score at 1
            curr_final = 1
        final_score += curr_final
    return float(final_score / len(score_list))


def main():
    if len(sys.argv) == 3:
        average_distance = distance_calculator(sys.argv[1], sys.argv[2])
        print("%f" % (1 - average_distance))
    else:
        print("Incorrect number of arguments. Found {:d}, expected 3"
              .format(len(sys.argv)))


if __name__ == '__main__':
    main()
