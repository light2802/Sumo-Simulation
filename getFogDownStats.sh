#!/bin/bash

for date in {11..18}
do
	for prob in 0.0 0.05 0.1  0.15 0.2  0.25 0.3  0.35 0.4  0.45 0.5 0.55 0.6  0.65 0.7  0.75 0.8  0.85 0.9  0.95;
	do
		echo "Date : $date"
		echo "Probability : $prob"
		python -u runner.py --nogui --numClients 4 --date $date | tee logs/fog_down.$date.$prob.log& \
		python fog.py --jId j --prob $prob --date $date > logs/fog_down.$date.$prob.timings.j.log& \
		python fog.py --jId a --prob $prob --date $date > logs/fog_down.$date.$prob.timings.a.log& \
		python fog.py --jId r --prob $prob --date $date > logs/fog_down.$date.$prob.timings.r.log
	done
done
