#!/bin/bash

for date in {11..18}
do
	echo "Date : $date"
	python -u runner.py --nogui --numClients 4 --date $date | tee logs/adaptive_time.$date.log& \
	python fog.py --jId j > logs/adaptive_time.$date.timings.j.log& \
	python fog.py --jId a > logs/adaptive_time.$date.timings.a.log& \
	python fog.py --jId r > logs/adaptive_time.$date.timings.r.log
done
