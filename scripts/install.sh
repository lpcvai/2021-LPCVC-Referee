cd ~/referee
git fetch origin
git reset --hard origin master
python3 setup.py install
pip show cam2-referee