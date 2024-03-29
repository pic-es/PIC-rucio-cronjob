#!/usr/bin/python
# coding: utf-8

# In[1]:


# from __future__ import absolute_import, division, print_function

__author__ = "Agustin Bruzzese"
__copyright__ = "Copyright (C) 2020 Agustin Bruzzese"

__revision__ = "$Id$"
__version__ = "0.2"

import sys
sys.path.append("/usr/lib64/python3.6/site-packages/")

import gfal2
import io
import json
import linecache
import logging
import numpy as np 
import os
import os.path
import random
import re
import time
import uuid
import zipfile
import string
import pathlib
import time 
import pytz
from urllib.parse import urlunsplit

from dateutil import parser
from datetime import (
    datetime,
    tzinfo,
    timedelta,
    timezone,
)
from gfal2 import (
    Gfal2Context,
    GError,
)
from io import StringIO

# Set Rucio virtual environment configuration 
os.environ['RUCIO_HOME']=os.path.expanduser('~/Rucio-v2/rucio')
from rucio.rse import rsemanager as rsemgr
from rucio.client.client import Client
from rucio.client.didclient import DIDClient
from rucio.client.replicaclient import ReplicaClient
import rucio.rse.rsemanager as rsemgr
# from rucio.client import RuleClient
from rucio.client.ruleclient import RuleClient

from rucio.common.exception import (AccountNotFound, Duplicate, RucioException, DuplicateRule, InvalidObject, DataIdentifierAlreadyExists, FileAlreadyExists, RucioException,
                                    AccessDenied)

from rucio.common.utils import adler32, detect_client_location, execute, generate_uuid, md5, send_trace, GLOBALLY_SUPPORTED_CHECKSUMS

import graphyte, socket

# Import Magic naming 
# from lfn2pfn import *

gfal2.set_verbose(gfal2.verbose_level.debug)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
account='root'
auth_type='x509'

# account=account, auth_type=auth_type
client = Client(account=account)

gfal = Gfal2Context()
    
json_file = 'Rucio-data.json'

# Predifine origin RSE 
DEFAULT_ORIGIN_RSE = 'PIC-NON-DET'

# Use a predefine folder to create random data 
# DEFAULT_PATH = os.path.join(get_rse_url(DEFAULT_ORIGIN_RSE), my_folder_test)

# Predifine scope
DEFAULT_SCOPE = 'test-root'

# Rucio settings 
rulesClient = RuleClient()


# In[2]:


rules = list(client.list_account_rules(account=account))

# Get list of all RSEs 
default_rses = list(client.list_rses())
rses_lists = []
for single_rse in default_rses :
    rses_lists.append(single_rse['rse'])


# In[3]:


# In[4]:


# Load grafan configuration for PIC

gr_prefix = [line for line in open('/etc/collectd.d/write_graphite-config.conf', 'r').readlines() if "Prefix" in line][0].strip().split()[1].strip('"')


# In[5]:


# Functions to gather data for Grapahana ploting 

def stats_rules(rules) :
    '''
    Gather general information about 
    total number of rules, and stats.
    '''
    RUCIOPIC = dict()
    if rules : 
        for rule in rules :
            if 'outdated_replication_dataset' not in rule['name'] :
                if 'Rules' not in RUCIOPIC :
                    RUCIOPIC['Rules'] = {
                        'total_stuck' : 0, 
                        'total_replicating' : 0,
                        'total_ok' : 0,
                        'total_rules': 0, 
                        'total_test_stuck' : 0, 
                        'total_test_replicating' : 0,
                        'total_test_ok' : 0,
                        'total_test_rules': 0 
                    }

                    if '-test' not in rule['scope']:
                        RUCIOPIC['Rules']['total_rules'] += 1
                        if rule['state'] == 'REPLICATING' : 
                            RUCIOPIC['Rules']['total_replicating'] += 1
                        elif rule['state'] == 'STUCK' :
                            RUCIOPIC['Rules']['total_stuck'] += 1
                        elif rule['state'] == 'OK' :
                            RUCIOPIC['Rules']['total_ok'] += 1
                    else :
                        RUCIOPIC['Rules']['total_test_rules'] += 1
                        if rule['state'] == 'REPLICATING' : 
                            RUCIOPIC['Rules']['total_test_replicating'] += 1
                        elif rule['state'] == 'STUCK' :
                            RUCIO['Rules']['total_test_stuck'] += 1
                        elif rule['state'] == 'OK' :
                            RUCIO['Rules']['total_test_ok'] += 1
                else :
                    if '-test' not in rule['scope']:
                        RUCIOPIC['Rules']['total_rules'] += 1
                        if rule['state'] == 'REPLICATING' : 
                            RUCIOPIC['Rules']['total_replicating'] += 1
                        elif rule['state'] == 'STUCK' :
                            RUCIOPIC['Rules']['total_stuck'] += 1
                        elif rule['state'] == 'OK' :
                            RUCIOPIC['Rules']['total_ok'] += 1
                    else:
                        RUCIOPIC['Rules']['total_test_rules'] += 1
                        if rule['state'] == 'REPLICATING' : 
                            RUCIOPIC['Rules']['total_test_replicating'] += 1
                        elif rule['state'] == 'STUCK' :
                            RUCIOPIC['Rules']['total_test_stuck'] += 1
                        elif rule['state'] == 'OK' :
                            RUCIOPIC['Rules']['total_test_ok'] += 1                       

            if 'AllRules' not in RUCIOPIC : 
                RUCIOPIC['AllRules'] = {
                    'total_stuck' : 0, 
                    'total_replicating' : 0,
                    'total_ok' : 0,
                    'total_rules': 0, 
                    'total_inject': 0,
                    'total_test_stuck' : 0, 
                    'total_test_replicating' : 0,
                    'total_test_ok' : 0,
                    'total_test_rules': 0, 
                    'total_test_inject': 0, 
                }
                
                RUCIOPIC['AllRules']['total_rules'] += 1
                if rule['state'] == 'REPLICATING' : 
                    RUCIOPIC['AllRules']['total_replicating'] += 1
                elif rule['state'] == 'STUCK' :
                    RUCIOPIC['AllRules']['total_stuck'] += 1
                elif rule['state'] == 'OK' :
                    RUCIOPIC['AllRules']['total_ok'] += 1
                elif rule['state'] == 'INJECT' :
                    RUCIOPIC['AllRules']['total_inject'] += 1                    
            else :     
                if '-test' not in rule['scope']:
                    RUCIOPIC['AllRules']['total_rules'] += 1
                    if rule['state'] == 'REPLICATING' : 
                        RUCIOPIC['AllRules']['total_replicating'] += 1
                    elif rule['state'] == 'STUCK' :
                        RUCIOPIC['AllRules']['total_stuck'] += 1
                    elif rule['state'] == 'OK' :
                        RUCIOPIC['AllRules']['total_ok'] += 1
                else:
                    RUCIOPIC['AllRules']['total_test_rules'] += 1
                    if rule['state'] == 'REPLICATING' : 
                        RUCIOPIC['AllRules']['total_test_replicating'] += 1
                    elif rule['state'] == 'STUCK' :
                        RUCIOPIC['AllRules']['total_test_stuck'] += 1
                    elif rule['state'] == 'OK' :
                        RUCIOPIC['AllRules']['total_test_ok'] += 1       
                    elif rule['state'] == 'INJECT' :
                        RUCIOPIC['AllRules']['total_test_inject'] += 1   
                        
            ##################
            if 'Grouping' not in RUCIOPIC : 
                RUCIOPIC['Grouping'] = {
                    'file' : 0, 
                    'dataset' : 0,
                    'container' : 0,
                    'test_file' : 0, 
                    'test_dataset' : 0,
                    'test_container' : 0 
                }
                
                if '-test' not in rule['scope']:
                    if rule['did_type'] == 'CONTAINER' : 
                        RUCIOPIC['Grouping']['container'] += 1
                    elif rule['did_type'] == 'DATASET' :
                        RUCIOPIC['Grouping']['dataset'] += 1
                    elif rule['did_type'] == 'FILE' :
                        RUCIOPIC['Grouping']['file'] += 1
                else :
                    if rule['did_type'] == 'CONTAINER' : 
                        RUCIOPIC['Grouping']['test_container'] += 1
                    elif rule['did_type'] == 'DATASET' :
                        RUCIOPIC['Grouping']['test_dataset'] += 1
                    elif rule['did_type'] == 'FILE' :
                        RUCIOPIC['Grouping']['test_file'] += 1                     
            else :  
                if '-test' not in rule['scope']:
                    if rule['did_type'] == 'CONTAINER' : 
                        RUCIOPIC['Grouping']['container'] += 1
                    elif rule['did_type'] == 'DATASET' :
                        RUCIOPIC['Grouping']['dataset'] += 1
                    elif rule['did_type'] == 'FILE' :
                        RUCIOPIC['Grouping']['file'] += 1 
                else:
                    if rule['did_type'] == 'CONTAINER' : 
                        RUCIOPIC['Grouping']['test_container'] += 1
                    elif rule['did_type'] == 'DATASET' :
                        RUCIOPIC['Grouping']['test_dataset'] += 1
                    elif rule['did_type'] == 'FILE' :
                        RUCIOPIC['Grouping']['test_file'] += 1                     
        return(RUCIOPIC)

def stats_replica_rules(rules) :

    '''
    Gather specific information about 
    state and number of replicas.
    '''
    REPLICAS = dict()
    REPLICAS['RSE'] = {}
    if rules : 
        # Creates a key for all the RSEs that we have replicas
        for rule in rules :
            # if the RSE is not in the dictionary
            #print(rule['rse_expression'], REPLICAS['RSE'])

            #print(rule['scope'])
            #print(rule)
            if rule['rse_expression'] not in REPLICAS['RSE'] : 
                if '-test' not in rule['scope']:
                    REPLICAS['RSE'][rule['rse_expression']] = { 
                        'total_replica_stuck' : rule['locks_stuck_cnt'], 
                        'total_replica_replicating' : rule['locks_replicating_cnt'],
                        'total_replica_ok' : rule['locks_ok_cnt'],
                        'total_test_replica_stuck' : 0, 
                        'total_test_replica_replicating' : 0,
                        'total_test_replica_ok' : 0
                    } 
                    
                else :
                    REPLICAS['RSE'][rule['rse_expression']] = { 
                        'total_replica_stuck' : 0, 
                        'total_replica_replicating' : 0,
                        'total_replica_ok' : 0,
                        'total_test_replica_stuck' : rule['locks_stuck_cnt'], 
                        'total_test_replica_replicating' : rule['locks_replicating_cnt'],
                        'total_test_replica_ok' : rule['locks_ok_cnt']
                    } 
            # else if it  is, update replica numbers
            else :
                if '-test' not in rule['scope']:
                    REPLICAS['RSE'][rule['rse_expression']]['total_replica_stuck'] += rule['locks_stuck_cnt']
                    REPLICAS['RSE'][rule['rse_expression']]['total_replica_replicating'] += rule['locks_replicating_cnt']
                    REPLICAS['RSE'][rule['rse_expression']]['total_replica_ok'] += rule['locks_ok_cnt']
                    REPLICAS['RSE'][rule['rse_expression']]['total_test_replica_stuck'] += 0
                    REPLICAS['RSE'][rule['rse_expression']]['total_test_replica_replicating'] += 0
                    REPLICAS['RSE'][rule['rse_expression']]['total_test_replica_ok'] += 0
                    
                else : 
                    REPLICAS['RSE'][rule['rse_expression']]['total_replica_stuck'] += 0
                    REPLICAS['RSE'][rule['rse_expression']]['total_replica_replicating'] += 0
                    REPLICAS['RSE'][rule['rse_expression']]['total_replica_ok'] += 0
                    REPLICAS['RSE'][rule['rse_expression']]['total_test_replica_stuck'] += rule['locks_stuck_cnt']
                    REPLICAS['RSE'][rule['rse_expression']]['total_test_replica_replicating'] += rule['locks_replicating_cnt']
                    REPLICAS['RSE'][rule['rse_expression']]['total_test_replica_ok'] += rule['locks_ok_cnt']   
                    
        print(REPLICAS)
        return(REPLICAS)

def stats_usage_rules(all_rses=rses_lists) :    
    STORAGE = dict()
    STORAGE['USAGE'] = {}
    for x_rse in all_rses :
        rses = list(client.get_local_account_usage(account=account,rse=x_rse))[0]
        if rses['bytes'] != 0 :
            if rses['rse'] not in STORAGE['USAGE'] : 
                STORAGE['USAGE'][rses['rse']] = { 
                    'total_bytes_used' : rses['bytes']
                } 
            # else if it  is, update replica numbers
            else :
                STORAGE['USAGE'][rses['rse']]['total_bytes_used'] += rses['bytes']
                
                
    return(STORAGE)


# In[6]:


# Posible way to plot 

## Prepare data for plots replicas 
def prepare_grafana(dictionary, string='RUCIOPIC.') :
    metric_list = []
    for key in dictionary.keys() :
        if isinstance(dictionary[key],int):
            #print(str(string+key), dictionary[key])
            metric_list.append((str(string+key),dictionary[key]) )

        elif isinstance(dictionary[key],dict):
            #print(prepare_grafana(dictionary[key], str(string+key+'.')))
            metric_list.extend(prepare_grafana(dictionary[key], str(string+key+'.')))       
    return(metric_list)


# In[7]:


def send_to_graf(dictionary, myport=2013, myprotocol='udp') : 
    for key in prepare_grafana(dictionary):
        if (key[0], key[1]) is not None : 
            print(key[0].lower(),key[1])
            graphyte.Sender('graphite01.pic.es', port=myport, protocol=myprotocol, prefix=gr_prefix + socket.gethostname().replace(".","_")).send(key[0].lower(), key[1])
            graphyte.Sender('graphite02.pic.es', port=myport, protocol=myprotocol, prefix=gr_prefix + socket.gethostname().replace(".","_")).send(key[0].lower(), key[1])


# In[8]:



# 1) Plot general state of rules 
send_to_graf(stats_rules(rules))

# 2) Plot state of replicas per RSE
send_to_graf(stats_replica_rules(rules))

# 3) Plot RSE usage 
send_to_graf(stats_usage_rules())

