#! /usr/bin/env python3

import argparse
import csv
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
    print('\u001b[1m\u001b[4mCopying submission to Pi\u001b[0m')
    os.system('ssh pi@referee.local "rm -r ~/Documents/run_sub/*"')
    os.system('scp ./test_sub pi@referee.local:~/Documents/run_sub/test_sub')
    os.system('ssh pi@referee.local "chmod +x ~/Documents/run_sub/test_sub"')

    #send user submission from ~/sites/lpcv.ai/submissions/ to r_pi
    os.system("scp " + SITE + "/submissions/2020CVPR/20lpcvc_video/" + submission + " pi@referee.local:~/Documents/run_sub/solution.pyz")
    print('\u001b[1m\u001b[4mExtracting submission on Pi\u001b[0m')
    os.system('ssh pi@referee.local "unzip ~/Documents/run_sub/solution.pyz -d ~/Documents/run_sub/solution"')

    #pip install requirements
    print('\u001b[1m\u001b[4mPIP installing requirements\u001b[0m')
    os.system('ssh pi@referee.local "cd ~/Documents/run_sub; . ~/20cvpr/myenv/bin/activate.fish; pip3 install -r solution/requirements.txt"')

    #copy test video and question to r_pi
    print('\u001b[1m\u001b[4mCopying test footage and questions to Pi\u001b[0m')
    os.system("scp -r test_data/%s/pi pi@referee.local:~/Documents/run_sub/test_data" % (video,))

    #step 2: start meter.py on laptop, download pi_metrics.csv through http
    #account for pcms crashing
    print('\u001b[1m\u001b[4mRunning submission\u001b[0m')
    with open(SITE + "/results/power.csv", "w") as power:
        s = requests.Session()
        r = s.get("http://meter.local/")
        error = r.headers['Program-Termination-Reason']
        runtime = float(r.headers['Program-Runtime'])
        power.write(r.text)


    #step 4: copy answer_txt from pi
    # name of output file? Currently any .txt file
    print('\u001b[1m\u001b[4mScoring answers\u001b[0m')
    os.system("scp pi@referee.local:~/Documents/run_sub/*.txt " + SITE + "/results")

    return error, runtime

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

        queue = sorted(map(str, Path(queuePath).iterdir()), key=os.path.getctime, reverse=True) #build queue
        while queue:
            submission = queue.pop()
            with open(submission, 'w') as scoreCSVFile:
                scoreCSV = csv.writer(scoreCSVFile)
                scoreCSV.writerow(["video_name", "accuracy", "energy", "error_status", "run_time", "perfomance_score"])
                subfile = str(submission).split('/')[-1]
                for video, videoLength in videos:
                    error, runtime = testSubmission(subfile, video)
                    crunchScore(video, subfile, scoreCSV, videoLength, error, runtime)
                    if killer.kill_now:
                        exit()
                reportScore(subfile, scoreCSV)
                os.rename(submission, SITE + "/submissions/2020CVPR/20lpcvc_video/" + subfile + ".csv")

        killer.shutdown_withold = False
        time.sleep(120)

    exit()


def crunchScore(video, submission, scoreCSV, videoLength, error, runtime):
    """
    Process power.csv and dist.txt to get (video_name, accuracy, energy, score)
    """
    ldAccuracy, power, final_score_a = calc_final_score("test_data/%s/realA.txt" % (video,), SITE + "/results/answers.txt", SITE + "/results/power.csv")
    scoreCSV.writerow([video, ldAccuracy, power, error, runtime, final_score_a])


def reportScore(submission, scoreCSV):
    """
    TODO: Tell the server to store the average result into the database
    """
    print(submission + " has been scored!")


def testAndGrade(submission, video):
    error, run_time = testSubmission(submission, video)
    ldAccuracy, power, final_score_a, final_score_b = calc_final_score("test_data/%s/realA.txt" % (video,), SITE + "/results/answers.txt", SITE + "/results/power.csv")
    return ldAccuracy, power, error, run_time, final_score_a


if __name__ == "__main__":
    import argparse
    from LDCalc import distanceCalc

    class SiteBasedPath(str):
        def build(self, SITE):
            return os.path.join(str(SITE), self)

    queuePath = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'queue')

    parser = argparse.ArgumentParser(description='LPCVC UAV Track Submission Queue and Grader',
        epilog="The suggested way to start the queue is by using the /etc/init.d script. "
               "Please use that instead to start and stop the queue in production. This "
               "script is primarily used as a library for that script and for testing.")
    parser.add_argument('--site', help="folder location of the lpcv.ai website", nargs='?')
    subs = parser.add_subparsers()

    tG_parser = subs.add_parser('', help='default option for compatibility; test and grade a single submission')
    tG_parser.set_defaults(func=testAndGrade, submission='test.pyz', video='flex1')
    tG_parser.add_argument('submission', help="file name of the submission", nargs='?')
    tG_parser.add_argument('video', help="name of the video to test on", nargs='?')

    r_parser = subs.add_parser('r', help='start the queue')
    r_parser.set_defaults(func=startQueue, queuePath=queuePath, sleepTime=120)

    r_parser.add_argument('queuePath', help="directory on the system to store the queue", nargs='?')
    r_parser.add_argument('sleepTime', help="amount of time to sleep in between rounds of tests", nargs='?', type=float)

    t_parser = subs.add_parser('t', help='test a single submission')
    t_parser.set_defaults(func=testSubmission, submission='test.pyz', video='flex1')
    t_parser.add_argument('submission', help="file name of the submission", nargs='?')
    t_parser.add_argument('video', help="name of the video to test on", nargs='?')

    g_parser = subs.add_parser('g', help='grade an answers.txt file')
    g_parser.set_defaults(func=distanceCalc, aTxtName=SiteBasedPath("results/answers.csv"))
    g_parser.add_argument('realATxtName', help="path of the real answers.txt file")
    g_parser.add_argument('aTxtName', help="path of the submitted answers.txt file", nargs='?')

    G_parser = subs.add_parser('G', help='grade using all files')
    G_parser.set_defaults(func=calc_final_score, submissionFile=SiteBasedPath("results/answers.txt"), powerFile=SiteBasedPath("results/power.csv"), videoLength=300)
    G_parser.add_argument('groundTruthFile', help="path of the real answers.txt file")
    G_parser.add_argument('submissionFile', help="path of the submitted answers.txt file", nargs='?')
    G_parser.add_argument('powerFile', help="path of the power.csv file", nargs='?')
    G_parser.add_argument('videoLength', help="length of the video in seconds (default 300)", nargs='?', type=int)
    args = parser.parse_args()

    if hasattr(args, 'site') and args.site is not None:
        SITE = args.site
    del args.site

    #if not hasattr(args, 'func'):
        #parser.print_help()
        #exit()

    if args.func in (startQueue, testSubmission) and checkIfProcessRunning(sys.argv[0].split('/')[-1]):
        print("A queue process is already running. Please wait for it to finish.")
        exit(1)

    func = args.func
    del args.func
    output = func(**{k: v.build(SITE) if isinstance(v, SiteBasedPath) else v for k, v in vars(args).items()})
    if output is not None:
        print("Operation returned " + str(output))
