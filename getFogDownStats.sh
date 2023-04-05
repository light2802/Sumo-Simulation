#!/bin/bash

for date in {11..18}
do
	echo "Date : $date"
	python runner.py -u --nogui --date $date | tee logs/fog_down.$date.log& \
	python fog.py --jId j --prob 0.2 > logs/fog_down.$date.timings.j.log& \
	python fog.py --jId a --prob 0.2 > logs/fog_down.$date.timings.a.log& \
	python fog.py --jId r --prob 0.2 > logs/fog_down.$date.timings.r.log
done
