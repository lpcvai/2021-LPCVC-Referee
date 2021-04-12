import os
from subprocess import Popen

PI_SCRIPTS_DIR = os.getenv('LPCVC_PI_SCRIPTS_DIR', None)
PI_USER = os.getenv('LPCVC_PI_USER', 'dvideo@referee.local')
PI_PASSWORD = os.getenv('LPCVC_PI_PASSWORD', None)
METER_CMD = os.getenv('LPCVC_METER_CMD',
                      'C:\\lpcvc\\python\\python.exe -u '
                      'C:\\lpcvc\\WT310\\Debug\\wt310_client.py --pmtimeout {} --pminf USB '
                      '"C:\\Program Files\\OpenSSH\\ssh" -tt {}')
METER_USER = os.getenv('LPCVC_METER_USER', 'user@meter.local')
METER_CSV = os.getenv('LPCVC_METER_CSV', 'C:\\lpcvc\\WT310\\Debug\\monitor.csv').replace('\\', '\\\\')
SITE = os.getenv('LPCVC_SITE', os.path.expanduser('~/sites/lpcv.ai'))


def setup_pi():
    run_pi_script("setup_pi", PI_USER)


def run_pi_script(name, arguments):
    if PI_SCRIPTS_DIR is not None:
        command = "{}/{}.sh {}".format(PI_SCRIPTS_DIR, name, arguments)
        os.system(command)


def pi_set_allow_firewall(is_allow):
    parameter = "allow" if is_allow else "block"
    pi_run_command("pi_firewall {} {}".format(parameter, PI_PASSWORD), False)


def pi_get_submission(submission_location, submission_destination):
    arguments = "{} {} {}".format(PI_USER, submission_location, submission_destination)
    run_pi_script("send_submission", arguments)


def pi_run_command(command, arguments=None, sudo=False, use_p_open=False):
    if use_p_open:
        p_open_args = arguments if arguments is not None else []
        p_open_args += ['ssh', PI_USER, command]
        return Popen(p_open_args).wait()
    if sudo:
        os.system('ssh ' + PI_USER + ' -tt "echo {} | sudo -S {}"'.format(PI_PASSWORD, command))
    else:
        os.system('ssh ' + PI_USER + ' -tt "{}"'.format(command))
    return 0


def get_pi_command_from_meter(timeout=300, name=None, arguments=None, commands=None, use_p_open=False):
    if use_p_open:
        return Popen(['stdbuf', '-o0', '-e0', "ssh", METER_USER,
                      get_pi_command_from_meter(timeout=timeout, commands=commands)]).wait()
    setup_meter_command = METER_CMD.format(timeout, PI_USER)
    meter_command = None
    if name is not None and arguments is not None and PI_SCRIPTS_DIR is not None:
        meter_command = "{} {}/{}.sh {}".format(setup_meter_command, PI_SCRIPTS_DIR, name, arguments)
    elif commands is not None:
        meter_command = "{} \"{}\"".format(setup_meter_command, commands)
    return meter_command


def get_file_from_pi(pi_source_location, local_destination):
    os.system("scp -T " + PI_USER + ":" + pi_source_location + " " + local_destination)


def get_power_results():
    os.system("scp -T " + METER_USER + ":" + METER_CSV + " " + os.path.join(SITE, "results/power.csv"))
