#! /usr/bin/env python3

import argparse
import csv
import LDCalc
import os
from pathlib import Path
import psutil
import requests
from scoring import calc_final_score
import signal
import subprocess
import sys
import time

SITE = os.path.expanduser('~/sites/lpcv.ai')


def checkIfProcessRunning(processName):
    '''
    Check if there is any running process that contains the given name processName.
    '''
    #https://thispointer.com/python-check-if-a-process-is-running-by-name-and-find-its-process-id-pid/
    #Iterate over the all the running process
    count = 0
    for proc in psutil.process_iter():
        try:
            # Check if process name contains the given name string.
            if processName in [arg.rsplit('/')[-1] for arg in proc.cmdline()]:
                count += 1
                if count == 2:
                    return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return False


def findScore(name):
    avgDist = LDCalc.distanceCalc("test_data/%s/realA.txt" % (name,), SITE + "/results/answers.txt")

    fpOut = open(SITE + "/results/usr_LDist.txt", 'w')
    fpOut.write("The error of the solution is: %f" %(avgDist))
    fpOut.close()


def getVersion(file):
    """
    Detect the version of Python used for a submission.
    """
    with open(file, 'rb') as pyz:
        if pyz.read(2) == b'#!':
            version = pyz.readline().rsplit(b'python', 2)[1].strip()
            if version in (b'3.7',):
                return version.decode()
        return '3.7'


def testSubmission(submission, video):
    #clear files in ~/Documents/run_sub
    os.system('ssh pi@referee.local "rm -r ~/Documents/run_sub/*"')
    os.system('scp ./test_sub pi@referee.local:~/Documents/run_sub/test_sub')
    os.system('ssh pi@referee.local "chmod +x ~/Documents/run_sub/test_sub"')

    #send user submission from ~/sites/lpcv.ai/submissions/ to r_pi
    os.system("scp " + SITE + "/submissions/2020CVPR/20lpcvc_video/" + submission + " pi@referee.local:~/Documents/run_sub/solution.pyz")
    os.system('ssh pi@referee.local "unzip ~/Documents/run_sub/solution.pyz -d ~/Documents/run_sub/solution"')

    #pip install requirements
    os.system('ssh pi@referee.local "cd ~/Documents/run_sub; . ~/20cvpr/myenv/bin/activate; pip3 install -r solution/requirements.txt"')

    #copy test video and question to r_pi
    os.system("scp -r test_data/%s/pi pi@referee.local:~/Documents/run_sub/test_data" % (video,))

    #step 2: start meter.py on laptop, download pi_metrics.csv through http
    #account for pcms crashing
    with open(SITE + "/results/power.txt", "w") as power:
        s = requests.Session()
        r = s.get("http://meter.local/")
        power.write(r.text)


    #step 4: copy answer_txt from pi
    # name of output file? Currently any .txt file
    os.system("scp pi@referee.local:~/Documents/run_sub/*.txt " + SITE + "/results")

    #step 5: run LDCalc
    #findScore(name) # old. now done in scoring.py


class GracefulKiller:
    #https://stackoverflow.com/a/31464349
    kill_now = False
    shutdown_withold = False
    def __init__(self):
        signal.signal(signal.SIGINT, self.exit_gracefully)
        signal.signal(signal.SIGTERM, self.exit_gracefully)

    def exit_gracefully(self,signum, frame):
        self.kill_now = True
        if not self.shutdown_withold:
            exit()


def startQueue(queuePath, sleepTime):
    """
    User submissions are queued then move to '~/sites/lpcv.ai/submissions/' one at a time
    """
    try:
        os.mkdir(queuePath)
    except FileExistsError:
        pass
    videos = [('flex1', 300)]

    # Create a signal handler to finish as soon as possible
    killer = GracefulKiller()
    while not killer.kill_now:
        killer.shutdown_withold = True

        queue = sorted(Path(queuePath).iterdir(), key=os.path.getctime, reverse=True) #build queue
        while queue:
            submission = queue.pop()
            with open(submission, 'w') as scoreCSVFile:
                scoreCSV = csv.writer(scoreCSVFile)
                scoreCSV.writerow(["video_name", "accuracy", "energy", "perfomance_score"])
                subfile = str(submission).split('/')[-1]
                for video, videoLength in videos:
                    testSubmission(subfile, video)
                    crunchScore(video, subfile, scoreCSV, videoLength)
                    if killer.kill_now:
                        exit()
                reportScore(subfile, scoreCSV)
                os.rename(submission, "/submissions/2020CVPR/20lpcvc_video/" + subfile + ".csv")

        killer.shutdown_withold = False
        time.sleep(120)

    exit()


def crunchScore(video, submission, scoreCSV, videoLength):
    """
    TODO: Process power.csv and dist.txt to get (video_name, accuracy, energy, score)
    """
    ldAccuracy, power, final_score_a, final_score_b = calc_final_score("test_data/%s/realA.txt" % (video,), SITE + "/results/answers.txt", SITE + "/results/power.csv", videoLength)
    scoreCSV.writerow([video, ldAccuracy, power, final_score_a])


def reportScore(submission, scoreCSV):
    """
    TODO: Tell the server to store the average result into the database
    """
    print(submission)


if __name__ == "__main__":
    import argparse

    queuePath = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'queue')

    def grade(realATxtName, aTxtName):
        print(LDCalc.distanceCalc(realATxtName, aTxtName))

    parser = argparse.ArgumentParser(description='LPCVC UAV Track Submission Queue and Grader',
        epilog="The suggested way to start the queue is by using the /etc/init.d script. "
               "Please use that instead to start and stop the queue in production. This "
               "script is primarily used as a library for that script and for testing.")
    subs = parser.add_subparsers()

    r_parser = subs.add_parser('r', help='start the queue')
    r_parser.set_defaults(func=startQueue, queuePath=queuePath, sleepTime=120)

    r_parser.add_argument('queuePath', help="directory on the system to store the queue", nargs='?')
    r_parser.add_argument('sleepTime', help="amount of time to sleep in between rounds of tests", nargs='?', type=float)

    t_parser = subs.add_parser('t', help='test a single submission')
    t_parser.set_defaults(func=testSubmission, submission='test.pyz', video='flex1')
    t_parser.add_argument('submission', help="file name of the submission", nargs='?')
    t_parser.add_argument('video', help="name of the video to test on", nargs='?')

    g_parser = subs.add_parser('g', help='grade an answers.txt file')
    g_parser.set_defaults(func=grade)
    g_parser.add_argument('realATxtName', help="path of the real answers.txt file")
    g_parser.add_argument('aTxtName', help="path of the submitted answers.txt file")
    args = parser.parse_args()

    if not hasattr(args, 'func'):
        parser.print_help()
        exit()

    if args.func is not grade and checkIfProcessRunning(sys.argv[0].split('/')[-1]):
        print("A queue process is already running. Please wait for it to finish.")
        exit(1)

    func = args.func
    del args.func
    func(**vars(args))
