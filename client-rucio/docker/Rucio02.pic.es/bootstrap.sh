#!/bin/bash
# Copyright 2019 CERN for the benefit of the ATLAS collaboration.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# Authors:
# - Mario Lassnig <mario.lassnig@cern.ch>, 2019

rucio-admin account add abruzzese 
rucio-admin scope add --account abruzzese --scope test-abruzzese
rucio-admin identity add --account abruzzese --type USERPASS --id abruzzese_user --password pwd123 --email bruzzese@pic.es
rucio-admin identity add --account abruzzese --type X509 --id '/DC=org/DC=terena/DC=tcs/C=ES/O=Port dInformacio Cientifica/CN=Agustin Bruzzese bruzzese@pic.es' --email bruzzese@pic.es
rucio-admin identity add --account abruzzese --type X509 --id '/DC=org/DC=terena/DC=tcs/C=ES/L=Cerdanyola del Valles/O=Institut de Fisica d. Altes Energies/CN=rucio03.pic.es' --email bruzzese@pic.es
rucio-admin account list-identities abruzzese

rucio-admin scope add --account root --scope test-root
rucio-admin identity add --account root --type X509 --id '/DC=org/DC=terena/DC=tcs/C=ES/O=Port dInformacio Cientifica/CN=Agustin Bruzzese bruzzese@pic.es' --email bruzzese@pic.es
rucio-admin identity add --account root --type X509 --id '/DC=org/DC=terena/DC=tcs/C=ES/L=Cerdanyola del Valles/O=Institut de Fisica d. Altes Energies/CN=rucio03.pic.es' --email bruzzese@pic.es
rucio-admin identity add --account root --type X509 --id '/DC=org/DC=terena/DC=tcs/C=ES/L=Cerdanyola del Valles/O=Institut de Fisica d. Altes Energies/CN=pic01-rucio-server.pic.es' --email bruzzese@pic.es
rucio-admin account list-identities root
