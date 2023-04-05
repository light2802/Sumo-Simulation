#!/bin/bash

for date in {11..18}
do
	echo "Date : $date"
	python -u runner.py --nogui --date $date | tee logs/static_time.$date.log
done
