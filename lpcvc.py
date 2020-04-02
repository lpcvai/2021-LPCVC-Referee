#! /usr/bin/env python3

import subprocess
import os
import requests
import LDCalc

SITE = os.path.expanduser('~/sites/lpcv.ai')
usr_sub = "test.pyz"

def findScore(name):
    avgDist = LDCalc.distanceCalc("test_data/%s/realA.txt" % (name,), SITE + "/results/usr_result.txt")

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


def testSubmission(name):
    """
    User submissions are queued then move to '~/sites/lpcv.ai/submissions/' one at a time
    """
    #clear files in ~/Documents/run_sub

    os.system('ssh pi@referee.local "rm -r ~/Documents/run_sub/*"')
    os.system('scp ./test_sub pi@referee.local:~/Documents/run_sub/test_sub')
    os.system('ssh pi@referee.local "chmod +x ~/Documents/run_sub/test_sub"')

    #send user submission from ~/sites/lpcv.ai/submissions/ to r_pi
    os.system("scp " + SITE + "/submissions/2020CVPR/20lpcvc_video/" + usr_sub + " pi@referee.local:~/Documents/run_sub/solution.pyz")
    os.system('ssh pi@referee.local "unzip ~/Documents/run_sub/solution.pyz -d ~/Documents/run_sub/solution"')

    #pip install requirements
    os.system('ssh pi@referee.local "cd ~/Documents/run_sub; . ~/20cvpr/myenv/bin/activate; pip3 install -r solution/requirements.txt"')

    #copy test video and question to r_pi
    os.system("scp -r test_data/%s/pi pi@referee.local:~/Documents/run_sub/test_data" % (name,))

    #step 2: start meter.py on laptop, download pi_metrics.csv through http
    #account for pcms crashing
    with open(SITE + "/results/power.csv", "w") as power:
        s = requests.Session()
        r = s.get("http://meter.local/")
        power.write(r.text)


    #step 4: copy answer_txt from pi
    # name of output file? Currently any .txt file
    os.system("scp pi@referee.local:~/Documents/run_sub/*.txt " + SITE + "/results")

    #step 5: run LDCalc
    findScore(name)





if __name__ == "__main__":
    testSubmission("flex1")

