import csv
import os
import time
from pathlib import Path

from .common import setup_pi
from .graceful_killer import GracefulKiller
from .running_submission import setup_submission, run_on_video, finish_submission
from .record_submission import append_video_score, report_score

# You Run it Here
SITE = os.getenv('LPCVC_SITE', os.path.expanduser('~/sites/lpcv.ai'))
REFRESH_RATE = int(os.getenv('LPCVC_REFRESH_RATE', '10'))
TEST_VIDEOS = os.getenv('LPCVC_TEST_VIDEOS', '').split()


def start_queue(queue_path, sleep_time):
    """
    User submissions are queued then move to '~/sites/lpcv.ai/submissions/' one at a time
    """
    try:
        os.mkdir(queue_path)
    except FileExistsError:
        pass
    videos = TEST_VIDEOS
    setup_pi()

    # Create a signal handler to finish as soon as possible
    killer = GracefulKiller()
    while True:
        if killer.kill_now:
            exit()
        killer.shutdown_withhold = True

        # build lpcvc_queue
        queue = sorted(map(str, Path(queue_path).iterdir()), key=os.path.getctime, reverse=True)
        while queue:
            submission = queue.pop()
            sub_file_name = str(submission).split('/')[-1]
            # print('\u001b[1m\u001b[4mRunning submission ' + sub_file_name + '\u001b[0m')
            with open(submission, 'w') as scoreCSVFile:
                score_fp = csv.writer(scoreCSVFile)
                score_fp.writerow(["video_name", "accuracy", "energy", "error_status", "run_time", "performance_score"])
                if setup_submission(sub_file_name):
                    for video in videos:
                        run_on_video(video)
                        append_video_score(video, score_fp)
                else:
                    for video in videos:
                        score_fp.writerow([video, 0, 0, 'CTE', 0, 0])
            finish_submission(submission, sub_file_name)
            report_score(sub_file_name)
            if killer.kill_now:
                exit()

        killer.shutdown_withhold = False
        if sleep_time is None:
            time.sleep(REFRESH_RATE)
        else:
            time.sleep(sleep_time)
