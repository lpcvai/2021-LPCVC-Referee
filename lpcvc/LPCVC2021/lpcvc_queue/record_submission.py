import os
import time

import requests

from lpcvc.LPCVC2021 import DataSet, Compare

SITE = os.getenv('LPCVC_SITE', os.path.expanduser('~/sites/lpcv.ai'))
SITE_URL = os.getenv('LPCVC_SITE_URL', 'https://lpcv.ai')
TEST_DATA_DIR = os.getenv('LPCVC_TEST_DATA_DIR', "test_data")

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
    print(TEST_DATA_DIR + "/correct/{}.csv")
    return Compare(correct, submitted, 10).score


def append_video_score(video, score_cvs):
    file_location = SITE + "/results/power.csv"
    energy, duration, error = parse_power_file(file_location)
    score = 0
    if error == '':
        score = get_video_score(video)
    energy -= duration * MIN_POWER
    final_score = score / energy if energy > 0 else 0
    score_cvs.writerow([video, round(score, 2), energy, duration, round(final_score, 5)])


def report_score(submission):
    """
    Tell the server to store the average result into the database
    """
    print("INFO: " + submission + " has been scored!\n\n\n\n==================\n")
    time.sleep(0.2)
    if SITE_URL:
        requests.get(SITE_URL + "/organizers/video20/grade/%s" % (submission,), verify=False)
