#! /usr/bin/env python3

import argparse
import configparser
import csv
import os
from pathlib import Path
import psutil
import requests
from scoring import calc_final_score
import signal
from subprocess import Popen
import sys
import time

# Get Environment Variables from .env
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

my_env = os.environ.copy()
parser = configparser.ConfigParser({k: v.replace('$', '$$') for k, v in os.environ.items()},
                                   interpolation=configparser.ExtendedInterpolation())
settingsFile = os.path.join(PROJECT_ROOT, ".env")
if os.path.isfile(settingsFile):
    with open(settingsFile) as stream:
        parser.read_file(['[DEFAULT]\n', *stream])
        for k, v in parser["DEFAULT"].items():
            my_env.setdefault(k.upper(), v)

SITE = my_env.get('LPCVC_SITE', os.path.expanduser('~/sites/lpcv.ai'))
SITE_URL = my_env.get('LPCVC_SITE_URL', 'https://lpcv.ai')
PI_USER = my_env.get('LPCVC_PI_USER', 'xiaohu@referee.local')
METER_USER = my_env.get('LPCVC_METER_USER', 'user@meter.local')
SHELL = my_env.get('LPCVC_SHELL', 'bash')
if SHELL == 'bash':
    SHELL_EXT = ''
else:
    SHELL_EXT = '.' + SHELL

ENV_DIR = my_env.get('LPCVC_ENV_DIR', '~/facebook-sol/mysol')
PI_TEST_DIR = my_env.get('LPCVC_PI_TEST_DIR', '~/contestant-sol/')
TEST_SUB_SCRIPT = my_env.get('LPCVC_TEST_SUB_SCRIPT', '~/test_sub')
PI_FIREWALL_SCRIPT = my_env.get('LPCVC_PI_FIREWALL_SCRIPT', '~/piFirewall.sh')
SUBMISSION_DIR = my_env.get('LPCVC_SUBMISSION_DIR', SITE + '/submissions/2020CVPR/20lpcvc_video')
TEST_DATA_DIR = my_env.get('LPCVC_TEST_DATA_DIR', "test_data")

METER_CMD = my_env.get('LPCVC_METER_CMD',
                       'C:\\lpcvc\\python\\python.exe -u C:\\lpcvc\\WT310\\Debug\\wt310_client.py --pmtimeout {timeout:d} --pminf USB "C:\\Program Files\\OpenSSH\\ssh" -tt ' + PI_USER + ' "cd ' + PI_TEST_DIR + ' && . ' + ENV_DIR + '/bin/activate' + SHELL_EXT + ' && ' + TEST_SUB_SCRIPT + ' {video}"')
METER_CSV = my_env.get('LPCVC_METER_CSV', 'C:\\lpcvc\\WT310\\Debug\\monitor.csv').replace('\\', '\\\\')
REFRESH_RATE = int(my_env.get('LPCVC_REFRESH_RATE', '10'))

TEST_VIDEOS = my_env.get('LPCVC_TEST_VIDEOS',
                         'test01_FlexBase_edited3min test02_Flex3rd_part1 test02_Flex3rd_part2 test03_clip2 test04_FlexBase02_part1').split()


def check_if_process_running(process_name):
    '''
    Check if there is any running process that contains the given name processName.
    '''
    # https://thispointer.com/python-check-if-a-process-is-running-by-name-and-find-its-process-id-pid/
    # Iterate over the all the running process
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


def get_version(file):
    """
    Detect the version of Python used for a submission.
    """
    with open(file, 'rb') as pyz:
        if pyz.read(2) == b'#!':
            version = pyz.readline().rsplit(b'python', 2)[1].strip()
            if version in (b'3.8',):
                return version.decode()
        return '3.8'


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
    shutdown_withold = False

    def __init__(self):
        signal.signal(signal.SIGINT, self.exit_gracefully)
        signal.signal(signal.SIGTERM, self.exit_gracefully)

    def exit_gracefully(self, signum, frame):
        self.kill_now = True
        if not self.shutdown_withold:
            exit()


def start_queue(queue_path):
    """
    User submissions are queued then move to '~/sites/lpcv.ai/submissions/' one at a time
    """
    try:
        os.mkdir(queue_path)
    except FileExistsError:
        pass
    videos = TEST_VIDEOS

    # Create a signal handler to finish as soon as possible
    killer = GracefulKiller()
    while True:
        if killer.kill_now:
            exit()
        killer.shutdown_withold = True

        queue = sorted(map(str, Path(queue_path).iterdir()), key=os.path.getctime, reverse=True)  # build queue
        while queue:
            submission = queue.pop()
            subfile = str(submission).split('/')[-1]
            # print('\u001b[1m\u001b[4mRunning submission ' + subfile + '\u001b[0m')
            with open(submission, 'w') as scoreCSVFile:
                scoreCSV = csv.writer(scoreCSVFile)
                scoreCSV.writerow(["video_name", "accuracy", "energy", "error_status", "run_time", "perfomance_score"])
                if setup_submission(subfile):
                    for video in videos:
                        run_on_video(video)
                        crunchScore(video, subfile, scoreCSV)
                else:
                    for video in videos:
                        scoreCSV.writerow([video, 0, 0, 'CTE', 0, 0])
            os.rename(submission, SUBMISSION_DIR + "/" + subfile + ".csv")
            reportScore(subfile)
            if killer.kill_now:
                exit()

        killer.shutdown_withold = False
        time.sleep(REFRESH_RATE)


def crunchScore(video, submission, scoreCSV):
    """
    Process power.csv and dist.txt to get (video_name, accuracy, energy, error, time, score)
    """
    ldAccuracy, energy, timeDurr, error, final_score_a = calc_final_score(
        os.path.join(TEST_DATA_DIR, video, "realA.txt"), SITE + "/results/answers.txt", SITE + "/results/power.csv")
    scoreCSV.writerow([video, ldAccuracy, energy, error, timeDurr, final_score_a])


def reportScore(submission):
    """
    Tell the server to store the average result into the database
    """
    print("INFO: " + submission + " has been scored!\n\n\n\n==================\n")
    time.sleep(0.2)
    if SITE_URL:
        requests.get(SITE_URL + "/organizers/video20/grade/%s" % (submission,), verify=False)


def testAndGrade(submission, videos):
    data = {}
    if setup_submission(submission):
        for video in videos:
            run_on_video(video)
            ldAccuracy, power, error, run_time, final_score_a = calc_final_score(
                os.path.join(TEST_DATA_DIR, video, "realA.txt"), SITE + "/results/answers.txt",
                SITE + "/results/power.csv")
            data[video] = [ldAccuracy, power, error, run_time, final_score_a]
    return data


def setupPi():
    os.system('ssh ' + PI_USER + ' "mkdir ' + os.path.dirname(ENV_DIR) + '; mkdir ' + PI_TEST_DIR + '"')
    os.system('ssh ' + PI_USER + ' "python3.8 -m venv --system-site-packages --prompt LPCVC-UAV ' + ENV_DIR + '"')
    os.system('scp ./test_sub ' + PI_USER + ':' + TEST_SUB_SCRIPT)
    os.system('scp ./piFirewall.sh ' + PI_USER + ':' + PI_FIREWALL_SCRIPT)
    os.system('ssh ' + PI_USER + ' "chmod +x ' + TEST_SUB_SCRIPT + '"')
    os.system('ssh ' + PI_USER + ' "chmod +x ' + PI_FIREWALL_SCRIPT + '"')


def main():
    import argparse
    from ld_calc import distance_calculator

    queuePath = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'queue')

    parser = argparse.ArgumentParser(description='LPCVC UAV Track Submission Queue and Grader',
                                     epilog="The suggested way to start the queue is by using the /etc/init.d script. "
                                            "Please use that instead to start and stop the queue in production. This "
                                            "script is primarily used as a library for that script and for testing.")
    subs = parser.add_subparsers()

    tG_parser = subs.add_parser('', help='default option for compatibility; test and grade a single submission')
    tG_parser.set_defaults(func=testAndGrade, submission='test.pyz', videos=TEST_VIDEOS)
    tG_parser.add_argument('submission', help="file name of the submission", nargs='?')
    tG_parser.add_argument('videos', help="name of the video to test on", nargs='*')

    r_parser = subs.add_parser('r', help='start the queue')
    r_parser.set_defaults(func=start_queue, queuePath=queuePath, sleepTime=120)

    r_parser.add_argument('queuePath', help="directory on the system to store the queue", nargs='?')
    r_parser.add_argument('sleepTime', help="amount of time to sleep in between rounds of tests", nargs='?', type=float)

    t_parser = subs.add_parser('t', help='test a single submission')
    t_parser.set_defaults(func=test_submission, submission='test.pyz', videos=TEST_VIDEOS)
    t_parser.add_argument('submission', help="file name of the submission", nargs='?')
    t_parser.add_argument('videos', help="name of the video to test on", nargs='*')

    g_parser = subs.add_parser('g', help='grade an answers.txt file')
    g_parser.set_defaults(func=distance_calculator, aTxtName=SITE + "/results/answers.csv")
    g_parser.add_argument('realATxtName', help="path of the real answers.txt file")
    g_parser.add_argument('aTxtName', help="path of the submitted answers.txt file", nargs='?')

    G_parser = subs.add_parser('G', help='grade using all files')
    G_parser.set_defaults(func=calc_final_score, submissionFile=SITE + "/results/answers.txt",
                          powerFile=SITE + "/results/power.csv")
    G_parser.add_argument('groundTruthFile', help="path of the real answers.txt file")
    G_parser.add_argument('submissionFile', help="path of the submitted answers.txt file", nargs='?')
    G_parser.add_argument('powerFile', help="path of the power.csv file", nargs='?')
    args = parser.parse_args()

    if not hasattr(args, 'func'):
        # parser.print_help()
        # exit()
        args.func = testAndGrade
        args.submission = 'test.pyz'
        args.videos = TEST_VIDEOS

    if args.func in (start_queue, test_submission) and check_if_process_running(sys.argv[0].split('/')[-1]):
        print("A queue process is already running. Please wait for it to finish.")
        exit(1)

    func = args.func
    del args.func
    output = func(**vars(args))
    if output is not None:
        print("Operation returned " + str(output))


if __name__ == "__main__":
    main()
