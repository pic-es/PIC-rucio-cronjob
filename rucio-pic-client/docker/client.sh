#!/bin/bash
docker pull bruzzese/rucio-client:latest
docker run -e RUCIO_ACCOUNT=root -e RUCIO_CFG_AUTH_TYPE=userpass -e RUCIO_CFG_USERNAME=ddmlab -e RUCIO_CFG_PASSWORD=secret -it -d --name=rucio-client bruzzese/rucio-client

