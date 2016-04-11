#!/bin/bash
#echo Creating dict of names of reps
echo Generating json name listing
python generateList.py
echo Adding files to archive
zip package.zip main.py config.py memberNames.py congressNames.json
echo Generating Congressman name slot
python generateRepSlot.py
