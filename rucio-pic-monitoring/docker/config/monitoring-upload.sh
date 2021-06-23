#! /bin/bash
while true
do  
  
  /usr/bin/python3 /Rucio-upload-monitoring.py -s > /dev/null 2>&1
  
  sleep 3600

done

