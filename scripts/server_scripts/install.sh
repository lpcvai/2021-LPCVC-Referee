#!/usr/bin/env bash
cd "$(dirname "$0")" || exit
cd ../../
git fetch origin
git reset --hard remotes/origin/master
pip uninstall cam2_referee -y
python3.7 setup.py install --user
exit