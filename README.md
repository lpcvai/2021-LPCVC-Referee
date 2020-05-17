# 2020-LPCVC-Referee
The evaluation system (referee) for the 2020 Low Power Computer Vision Challenge.

## Required Hardware and Software
 - Yokogawa WT310 Power Meter (discontinued, substitutable with the [WT310E](https://www.electro-meters.com/yokogawa/yokogawa-power-meters/wt300e/) model)
 - Windows Computer
   - [Yokogawa YKMUSB USB Driver](https://tmi.yokogawa.com/us/library/documents-downloads/software/usb-driver/)
   - [Microsoft Visual Studio](https://visualstudio.microsoft.com/downloads/)
   - [Python 3](https://www.python.org/downloads/windows/)
   - OpenSSH ([Windows 10](https://docs.microsoft.com/en-us/windows-server/administration/openssh/openssh_install_firstuse), [before Windows 10](https://docs.microsoft.com/en-us/windows-server/administration/openssh/openssh_install_firstuse))
   - [HELPS WT310 Controlling Program](https://github.com/anivegesana/WT310)
 - Linux Server
   - LPCVC Referee (this repo)
 - Raspberry Pi
   - [Fedora 32 Minimal](https://fedoraproject.org/wiki/Architectures/ARM/Raspberry_Pi)

## System Setup

### Setting up the Yokogawa WT310 Power Meter
The power meter must be connected so that it can record the power consumption of the Pi.

### Setting up the Windows Computer
After installing Microsoft Visual Studio and Python 3, open the HELPS WT310 Controlling Program solution and build the solution. Update the locations of the Python binary and the Debug folder in the `METER_CMD` and `METER_CSV` variables of the lpcvc.py file in this repository.
Create an SSH key for the computer using the ssh-keygen.exe utility.

### Setting up the Linux Server
Create a virtual environment for this repository and install the requirements from requirements.txt. Create a folder to store the submission files and update the `SUBMISSION_DIR` variable of the lpcvc.py file in this repository.
Create another SSH key for the Linux Server using the ssh-keygen utility.

### Setting up the Raspberry Pi
Create a virtual environment for the solutions. Create an empty folder for the testing of the submissions. Update the `PI_TEST_DIR` variable of the lpcvc.py file in this repository.
Create yet another SSH key for the Linux Server using the ssh-keygen utility. Add all three keys to the authorized_keys file in the ~/.ssh folder using the ssh-add utility. Copy the authorized_keys file across all three machines.
