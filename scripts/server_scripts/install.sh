#!/usr/bin/env bash
cd "$(dirname "$0")" || exit
cd ../../
git fetch origin
git reset --hard origin/master
pip uninstall cam2_referee -y
python3 setup.py install --user
exit