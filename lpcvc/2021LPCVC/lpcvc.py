import os
from pathlib import Path
import psutil
import requests
import signal
from subprocess import Popen
import sys
import time

TEST_SUB_SCRIPT = ''
PI_USER = ''
PI_TEST_DIR = ''
SUBMISSION_DIR = ''
PI_FIREWALL_SCRIPT = ''
SHELL = ''
ENV_DIR = ''
SHELL_EXT = ''
TEST_DATA_DIR = ''
METER_USER = ''
METER_CMD = ''
METER_CSV = ''
SITE = ''
TEST_VIDEOS = ''
REFRESH_RATE = 60
SITE_URL = ''


def is_process_running(process_name):
    """
    Check if there is any running process that contains the given name processName.
    https://thispointer.com/python-check-if-a-process-is-running-by-name-and-find-its-process-id-pid/
    Iterate over the all the running process
    """
    count = 0
    for proc in psutil.process_iter():
        try:
            # Check if process name contains the given name string.
            if process_name in [arg.rsplit('/')[-1] for arg in proc.cmdline()]:
                count += 1
                if count == 2:
                    return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return False


def setup_submission(submission):
    """
    Load the submission onto the Pi and install the requirements
    """
    # clear files in ~/Documents/run_sub
    # print('\u001b[1m\u001b[4mCopying submission to Pi\u001b[0m')
    if Popen(['ssh', PI_USER, 'rm -rf ' + PI_TEST_DIR + '/*']).wait() != 0:
        print("ERROR: Raspberry Pi mysteriously disconnected or incorrectly set up")
        exit(1)

    # send user submission from ~/sites/lpcv.ai/submissions/ to r_pi
    os.system("scp " + SUBMISSION_DIR + "/" + submission + " " + PI_USER + ":" + PI_TEST_DIR + "/solution.pyz")
    # print('\u001b[1m\u001b[4mExtracting submission on Pi\u001b[0m')
    if Popen(['ssh', PI_USER, 'unzip', PI_TEST_DIR + '/solution.pyz', '-d', PI_TEST_DIR + '/solution']).wait() != 0:
        print("ERROR: Cannot unzip the solution")
        return False

    # pip install requirements
    # print('\u001b[1m\u001b[4mPIP installing requirements\u001b[0m')
    os.system('ssh ' + PI_USER + ' -tt "sudo ' + PI_FIREWALL_SCRIPT + ' allow"')
    if Popen(['ssh', PI_USER, SHELL, '-c', '"cd ' + os.path.join(PI_TEST_DIR,
                                                                 'solution') + ' && . ' + ENV_DIR + '/bin/activate' + SHELL_EXT + ' && pip3 install -r requirements.txt"']).wait() != 0:
        print("ERROR: Cannot install the requirements")
        return False
    os.system('ssh ' + PI_USER + ' -tt "sudo ' + PI_FIREWALL_SCRIPT + ' block"')

    return True


def run_on_video(video):
    # copy test video and question to r_pi
    # print('\u001b[1m\u001b[4mCopying test footage and questions to Pi\u001b[0m')
    # os.system("scp -r test_data/%s/pi " + PI_USER + ":" + PI_TEST_DIR + "/test_data" % (video,))

    # step 2: start meter.py on laptop, download pi_metrics.csv through http
    # account for pcms crashing
    # print('\u001b[1m\u001b[4mRunning submission\u001b[0m')
    with open(os.path.join(TEST_DATA_DIR, video, "testlen.txt"), 'r') as testlen:
        timeout = int(testlen.readline())

    os.system('ssh ' + PI_USER + ' "rm -f ' + PI_TEST_DIR + '/answers.txt"')
    if Popen(['stdbuf', '-o0', '-e0', "ssh", METER_USER,
              METER_CMD.format_map({'timeout': timeout, 'video': video})]).wait() != 0:
        print("FATAL: Cannot start power meter", file=sys.stderr)
        exit(1)
    else:
        os.system("scp -T " + METER_USER + ":" + METER_CSV + " " + os.path.join(SITE, "results/power.csv"))
        # step 4: copy answer_txt from pi
        # name of output file? Currently any .txt file
        # print('\u001b[1m\u001b[4mScoring answers\u001b[0m')
        os.system("scp -T " + PI_USER + ":" + PI_TEST_DIR + "/answers.txt " + SITE + "/results")


def test_submission(submission, videos):
    data = {}
    if setup_submission(submission):
        for video in videos:
            run_on_video(video)
            with open(os.path.join(SITE, "results/power.csv"), "r") as powerfile:
                power, time, error = powerfile.readlines()[1].split(',')
                runtime = float(time)
                error = error.strip()
            data[video] = [error, runtime]
    return data


class GracefulKiller:
    # https://stackoverflow.com/a/31464349
    kill_now = False
    shutdown_withhold = False

    def __init__(self):
        signal.signal(signal.SIGINT, self.exit_gracefully)
        signal.signal(signal.SIGTERM, self.exit_gracefully)

    def exit_gracefully(self, signum, frame):
        self.kill_now = True
        if not self.shutdown_withhold:
            exit()


def start_queue(queue_path):
    """
    User submissions are queued then move to '~/sites/lpcv.ai/submissions/' one at a time
    """
    try:
        os.mkdir(queue_path)
    except FileExistsError:
        pass

    # Create a signal handler to finish as soon as possible
    killer: GracefulKiller = GracefulKiller()
    while True:
        if killer.kill_now:
            exit()
        killer.shutdown_withhold = True

        queue = sorted(map(str, Path(queue_path).iterdir()), key=os.path.getctime, reverse=True)  # build queue
        while queue:
            submission = queue.pop()
            sub_file = str(submission).split('/')[-1]
            if killer.kill_now:
                exit()

        killer.shutdown_withhold = False
        time.sleep(REFRESH_RATE)


def report_score(submission):
    """
    Tell the server to store the average result into the database
    """
    print("INFO: " + submission + " has been scored!\n\n\n\n==================\n")
    time.sleep(0.2)
    if SITE_URL:
        requests.get(SITE_URL + "/organizers/video20/grade/%s" % (submission,), verify=False)


def test_and_grade(submission, videos):
    data = {}
    if setup_submission(submission):
        for video in videos:
            pass
    return data


def setup_pi():
    os.system('ssh ' + PI_USER + ' "mkdir ' + os.path.dirname(ENV_DIR) + '; mkdir ' + PI_TEST_DIR + '"')
    os.system('ssh ' + PI_USER + ' "python3.8 -m venv --system-site-packages --prompt LPCVC-UAV ' + ENV_DIR + '"')
    os.system('scp ./test_sub ' + PI_USER + ':' + TEST_SUB_SCRIPT)
    os.system('scp ./piFirewall.sh ' + PI_USER + ':' + PI_FIREWALL_SCRIPT)
    os.system('ssh ' + PI_USER + ' "chmod +x ' + TEST_SUB_SCRIPT + '"')
    os.system('ssh ' + PI_USER + ' "chmod +x ' + PI_FIREWALL_SCRIPT + '"')
