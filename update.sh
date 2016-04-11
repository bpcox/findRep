#!/bin/bash
#echo Creating dict of names of reps
echo Generating json name listing
python generateList.py
echo Generating json address listing
python getFullAddress.py
echo Adding files to archive
zip -v package.zip main.py config.py memberNames.py congressNames.json addressDict.json
echo Generating Congressman name slot
python generateRepSlot.py
