#! /bin/bash
while true
do  
  
  /usr/bin/python3 /rucio-monitoring.py -s > /dev/null 2>&1
  
  sleep 1

done
