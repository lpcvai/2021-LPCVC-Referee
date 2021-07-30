import os
import sys

from .common import pi_run_command, pi_set_allow_firewall, pi_get_submission, get_pi_command_from_meter, \
    get_file_from_pi, get_power_results

PI_TEST_DIR = os.getenv('LPCVC_PI_TEST_DIR', '/home/dvideo/contestant-sol')
SHELL = os.getenv('LPCVC_SHELL', 'bash')
SHELL_EXT = '' if SHELL == 'bash' else '.' + SHELL
SITE = os.getenv('LPCVC_SITE', os.path.expanduser('~/sites/lpcv.ai'))
SUBMISSION_DIR = os.getenv('LPCVC_SUBMISSION_DIR', SITE + '/submissions/2021LPCVC/21lpcvc_video')


def create_test_directory():
    command = """
    rm -rf {} &&
    mkdir -p {}
    """.format(PI_TEST_DIR, PI_TEST_DIR)
    return pi_run_command(command, use_p_open=True)


def install_dependencies(env_name):
    pi_set_allow_firewall(True)
    command = """
    cd {} && 
    echo {} > ../env_name.txt &&
    conda env create -f environment.yml --name {} &&
    exit
    """.format(os.path.join(PI_TEST_DIR, 'solution'), env_name, env_name)
    response = pi_run_command(SHELL, arguments=[command], use_p_open=True)
    pi_set_allow_firewall(False)
    return response


def put_submission_in_test_directory(submission):
    submission_location = "{}/{}".format(SUBMISSION_DIR, submission)
    submission_destination = "{}/solution.pyz".format(PI_TEST_DIR)
    pi_get_submission(submission_location, submission_destination)


def setup_submission(submission):
    if create_test_directory() != 0:
        print("ERROR: Raspberry Pi mysteriously disconnected or incorrectly set up", file=sys.stderr)
        exit(1)

    put_submission_in_test_directory(submission)
    unzip_arguments = ["{}/solution.pyz".format(PI_TEST_DIR), "-d", "{}/solution".format(PI_TEST_DIR)]
    if pi_run_command("unzip", arguments=unzip_arguments, use_p_open=True) != 0:
        print("ERROR: Cannot unzip the solution", file=sys.stderr)

    if install_dependencies(submission[:-4]) != 0:
        print("ERROR: Cannot install the requirements", file=sys.stderr)
        return False

    return True


def remove_output():
    pi_run_command("rm -rf {}/outputs && mkdir -p {}/outputs".format(PI_TEST_DIR, PI_TEST_DIR))


def run_on_video(video):
    remove_output()
    run_command = "conda activate $(cat {}/env_name.txt) && run_solution {}/solution {}".format(PI_TEST_DIR, PI_TEST_DIR, video)
    if get_pi_command_from_meter(timeout=4500, commands=run_command, use_p_open=True) != 0:
        print("FATAL: Cannot start power meter", file=sys.stderr)
        exit(1)
    else:
        base_name = os.path.splitext(video)[0]
        program_output = "{}/outputs/{}_out.csv".format(PI_TEST_DIR, base_name)
        destination = SITE + "/results/"
        get_file_from_pi(program_output, destination)
        get_power_results()


def finish_submission(submission, sub_file_name):
    os.rename(submission, SUBMISSION_DIR + "/" + sub_file_name + ".csv")
