#!/bin/bash

yum install -y fts-client 
yum install -y fts-rest
yum install -y python-setuptools
yum install -y python-requests
yum install -y fts-rest-cli
yum install -y nano

/usr/bin/python3.6 -m pip install --upgrade pip
/usr/bin/python3.6 -m pip install --upgrade wheel
/usr/bin/python3.6 -m pip install --upgrade rucio-clients
/usr/bin/python3.6 -m pip install --upgrade numpy
/usr/bin/python3.6 -m pip install --upgrade pytz
/usr/bin/python3.6 -m pip install --upgrade graphyte
