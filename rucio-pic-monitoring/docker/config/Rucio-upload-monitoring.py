#!/usr/bin/env python
# coding: utf-8

# In[1]:


from __future__ import absolute_import, division, print_function

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
import traceback
from urllib.parse import urlunsplit
import graphyte, socket
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
                                    AccessDenied, InsufficientAccountLimit, RuleNotFound, AccessDenied, InvalidRSEExpression,
                                    InvalidReplicationRule, RucioException, DataIdentifierNotFound, InsufficientTargetRSEs,
                                    ReplicationRuleCreationTemporaryFailed, InvalidRuleWeight, StagingAreaRuleRequiresLifetime)

from rucio.common.utils import adler32, detect_client_location, execute, generate_uuid, md5, send_trace, GLOBALLY_SUPPORTED_CHECKSUMS

gfal2.set_verbose(gfal2.verbose_level.debug)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

gfal = Gfal2Context()


account='root'
auth_type='x509_proxy'

# account=account, auth_type=auth_type
CLIENT = Client()
didc = DIDClient()
client = Client()

print(client.whoami())
print(client.ping())

from rucio.client.uploadclient import UploadClient
uploadClient=UploadClient()
# Get list of all RSEs 
default_rses = list(client.list_rses())
rses_lists = []
for single_rse in default_rses :
    rses_lists.append(single_rse['rse'])

print(rses_lists)

DEFAULT_SCOPE = 'test-root'

# Generate a random file : 

def generate_random_file(filename, size, copies = 1):
    """
    generate big binary file with the specified size in bytes
    :param filename: the filename
    :param size: the size in bytes
    :param copies: number of output files to generate
    
    """
    n_files = []
    n_files = np.array(n_files, dtype = np.float32)   
    for i in range(copies):
        file = filename + '-' + str(uuid.uuid4())
        if os.path.exists(file) : 
            print ("File %s already exist" %file)

        else:
            print ("File %s not exist" %file)    
            try : 
                newfile = open(file, "wb")
                newfile.seek(size)
                newfile.write(b"\0")
                newfile.close ()
                os.stat(file).st_size
                print('random file with size %f generated ok'%size)
                n_files = np.append(n_files, file)
            except :
                print('could not be generate file %s'%file)

    return(n_files)

def get_rse_url(rse):
    """
    Return the base path of the rucio url
    """
    rse_settings = rsemgr.get_rse_info(rse)
    protocol = rse_settings['protocols'][0]

    schema = protocol['scheme']
    prefix = protocol['prefix']
    port = protocol['port']
    rucioserver = protocol['hostname']

    if schema == 'srm':
        prefix = protocol['extended_attributes'][
            'web_service_path'] + prefix
    url = schema + '://' + rucioserver
    if port != 0:
        url = url + ':' + str(port)
    rse_url = url + prefix
    #print(rse_url)
    return(rse_url)

list_files = generate_random_file('deletion', 1, 2)     



if rses_lists is not None and list_files is not None : 
    for n in range(0, len(list_files)) :
        for rse in rses_lists: 

            client=Client()
            rulesClient=RuleClient()
            uploadClient=UploadClient()

            name_file = list_files[n]
            filePath="./"+name_file
            # file = {'path': filePath, 'rse': rse, 'did_scope': DEFAULT_SCOPE, 'lifetime':1}

            if client.get_rse(rse)["deterministic"] == True :
                file = {'path': filePath, 'rse': rse, 'did_scope': DEFAULT_SCOPE, 'lifetime':1}
                print(file)
                # perform upload
                uploadClient.upload([file])

            else :
                url_rse = os.path.join(get_rse_url(rse), DEFAULT_SCOPE, name_file)

                file = {'path': filePath, 'rse': rse, 'did_scope': DEFAULT_SCOPE, 'lifetime':1, 'pfn':url_rse}
                print(file)
                uploadClient.upload([file])

        os.remove(filePath)

