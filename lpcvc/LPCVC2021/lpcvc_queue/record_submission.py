import os
import time
import csv
from datetime import datetime

from lpcvc.LPCVC2021 import DataSet, Compare

SITE = os.getenv('LPCVC_SITE', os.path.expanduser('~/sites/lpcv.ai'))
SITE_URL = os.getenv('LPCVC_SITE_URL', 'https://lpcv.ai')
TEST_DATA_DIR = os.getenv('LPCVC_TEST_DATA_DIR', "test_data")
SUBMISSION_DIR = os.getenv('LPCVC_SUBMISSION_DIR', os.path.expanduser('~/referee/winner_selection'))

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


def get_video_score(video):
    base_name = os.path.splitext(video)[0]
    submitted = DataSet(file_name=SITE + "/results/{}_out.csv".format(base_name))
    correct = DataSet(file_name=TEST_DATA_DIR + "/correct/{}.csv".format(base_name))
    return Compare(correct, submitted, 10).score


def append_video_score(video, score_cvs):
    file_location = SITE + "/results/power.csv"
    energy, duration, error = parse_power_file(file_location)
    score = 0
    if error == '':
        score = get_video_score(video)
    energy -= duration * MIN_POWER
    final_score = score / energy if energy > 0 else 0
    score_cvs.writerow([video, round(score, 2), energy, "None", duration, round(final_score, 5)])


def report_score(submission):
    """
    Tell the server to store the average result into the database
    """
    print("INFO: " + submission + " has been scored!\n\n\n\n==================\n")
    time.sleep(0.2)
    write_avg_score(submission)
    # if SITE_URL:
    #     requests.get(SITE_URL + "/organizers/video20/grade/%s" % (submission,), verify=False)


def write_avg_score(submissionName):
    with open(f"{SUBMISSION_DIR}/{submissionName}.csv") as csvFile:
        csvData = csv.reader(csvFile)
        next(csvData)
        cnt = 0
        avg_accuracy = 0
        avg_energy = 0
        avg_perfomance_score = 0
        for video_name,accuracy,energy,error_status,run_time,perfomance_score in csvData:
            avg_accuracy += float(accuracy)
            avg_energy += float(energy)
            avg_perfomance_score += float(perfomance_score)
            cnt += 1
        avg_accuracy /= cnt
        avg_energy /= cnt
        avg_perfomance_score /= cnt
    print(submissionName)
    with open(f"{SUBMISSION_DIR}/scores.csv", 'a') as score_table:
        # print('{},{},{},{},{}'.format(datetime.now(), submissionName, avg_accuracy, avg_energy, avg_perfomance_score))
        # grading_time,submission_name,avg_accuracy,avg_energy,avg_score
        # score_table.write('\n{},{},{},{},{}'.format(datetime.now(), submissionName, avg_accuracy, avg_energy, avg_perfomance_score))
        score_table_fp = csv.writer(score_table)
        score_table_fp.writerow([datetime.now(), submissionName, avg_accuracy, avg_energy, avg_perfomance_score])


    