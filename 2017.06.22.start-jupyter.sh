#!/bin/bash
#  chmod u+x scriptname make the script executable
#  place the script under /usr/local/bin folder
#  run the script using just the name of the script

export PYTHONPATH=/home/kaelin_joseph/DataOrganizer/lib/python

nohup jupyter notebook --notebook-dir=/home/kaelin_joseph/DataOrganizer/jupyter-python/ --port 8080 --ip=0.0.0.0 --no-browser   > /home/kaelin_joseph/DataOrganizer/jupyter-python/.log/jupyter.log 2>&1 &
