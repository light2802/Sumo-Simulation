#!/bin/bash

for date in {11..18}
do
	echo "Date : $date"
	python runner.py --nogui --date $date > $date.log
#	python $SUMO_HOME/tools/xml/xml2csv.py tripinfo.xml -o tripinfo.csv
#	awk -F';' '{sum+=$21; ++n} END { print "Avg: "sum"/"n"="sum/n }' < tripinfo.csv
done
