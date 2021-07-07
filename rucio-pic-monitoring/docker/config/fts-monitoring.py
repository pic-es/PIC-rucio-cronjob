#!/usr/bin/env python
# coding: utf-8

# In[1]:


import os
import io
import re
import sys
import json
import uuid
import gfal2
import time
import errno
import argparse
import logging
import requests
import itertools
import argparse
import json
import fts3.rest.client.easy as fts3
import fts3.rest.client.exceptions as fts3_client_exceptions
from datetime import datetime

# ----------------------------------------------------------
# Rucio variables 
# Set Rucio virtual environment configuration 
os.environ['RUCIO_HOME']=os.path.expanduser('~/rucio')
from rucio.rse import rsemanager as rsemgr
from rucio.client.client import Client
from rucio.client.didclient import DIDClient
from rucio.client.replicaclient import ReplicaClient
import rucio.rse.rsemanager as rsemgr
from rucio.client.ruleclient import RuleClient
from rucio.client.uploadclient import UploadClient
from rucio.client.downloadclient import DownloadClient
from rucio.common.utils import (adler32, detect_client_location, 
                                execute, generate_uuid, md5, 
                                send_trace, GLOBALLY_SUPPORTED_CHECKSUMS)
from rucio.common.exception import (AccountNotFound, Duplicate, RucioException, DuplicateRule, InvalidObject, DataIdentifierAlreadyExists, FileAlreadyExists, RucioException,
                                    AccessDenied, InsufficientAccountLimit, RuleNotFound, AccessDenied, InvalidRSEExpression,
                                    InvalidReplicationRule, RucioException, DataIdentifierNotFound, InsufficientTargetRSEs,
                                    ReplicationRuleCreationTemporaryFailed, InvalidRuleWeight, StagingAreaRuleRequiresLifetime)

# Import Gfal
import sys
sys.path.append("/usr/lib64/python3.6/site-packages/")
import gfal2
from gfal2 import (
    Gfal2Context,
    GError,
)

# ----------------------------------------------------------
# Gfal configuration

def event_callback(event):
    #print event
    print("[%s] %s %s %s" % (event.timestamp, event.domain, event.stage, event.description))

def monitor_callback(src, dst, average, instant, transferred, elapsed):
    print("[%4d] %.2fMB (%.2fKB/s)\r" % (elapsed, transferred / 1048576, average / 1024)),
    sys.stdout.flush()
    
gfal2.set_verbose(gfal2.verbose_level.debug)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
gfal = gfal2.creat_context()
params = gfal.transfer_parameters()
params.event_callback = event_callback
params.monitor_callback = monitor_callback
params.set_checksum = True
params.overwrite = True
params.set_create_parent= True
params.get_create_parent= True 
params.timeout = 300

# ----------------------------------------------------------
# FTS configuration
fts_endpoint = "https://fts01.pic.es:8446"
context = fts3.Context(fts_endpoint, verify=True)


# In[19]:


# General functions for the creation of files
def PrintException():
    import linecache
    exc_type, exc_obj, tb = sys.exc_info()
    f = tb.tb_frame
    lineno = tb.tb_lineno
    filename = f.f_code.co_filename
    linecache.checkcache(filename)
    line = linecache.getline(filename, lineno, f.f_globals)
    print('EXCEPTION IN ({}, LINE {} "{}"): {}'.format(filename, lineno, line.strip(), exc_obj))

# Get RSEs protocol
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
        prefix = protocol['extended_attributes']['web_service_path'] + prefix
    url = schema + '://' + rucioserver
    if port != 0:
        url = url + ':' + str(port)
    rse_url = url + prefix
    
    return(rse_url)

def make_file(file_name, size = 1000000):
    file_create = open(file_name, "wb")
    file_create.seek(size)
    file_create.write(b"\0")
    file_create.close ()

# function to add to JSON 
def write_fts_data(data, filename='fts-file.txt'): 
    with io.open(filename, 'a') as f: 
        # write line to output file
        f.write(data)
        f.write("\n")
    f.close()
    
def _gfal_upload_files(destination, number_files=1):
    
    fts_file = []
    for i in range(number_files):

        filename = 'fts-file-trasnfer-' + str(uuid.uuid4())
        make_file(filename)
        source_gfal = os.path.join(os.getcwd(), filename)
        destination_gfal = os.path.join(get_rse_url(destination),'fts-test')
        gfal.mkdir_rec(destination_gfal, 775)
        
        print(source_gfal, os.path.join(destination_gfal,filename))
        gfal.filecopy(params, 'file:///'+source_gfal, os.path.join(destination_gfal,filename))
        fts_file.append(os.path.join(destination_gfal,filename))
        os.remove(source_gfal)

    return(fts_file)

def _fts_submit_job(sources_fts, destination):

    destinations_fts = os.path.join(get_rse_url(destination),'fts-test')
    gfal.mkdir_rec(destinations_fts, 775)
    
    transfers= []
    for source_fts in sources_fts:
        print(source_fts)
        destination_fts = os.path.join(destinations_fts,os.path.basename(source_fts))
        transfer = fts3.new_transfer(source=source_fts, destination=destination_fts)
        transfers.append(transfer)

    # create job
    job = fts3.new_job(transfers,
                       verify_checksum=True,
                       overwrite=True,
                       timeout=3600,
                       metadata='test fts transfers for monitoring')
    
    job_id = fts3.submit(context, job)
    return(job_id)


# In[20]:


def _fts_check_job(filename='fts-file.txt'):
    print(filename)
    if os.path.isfile(filename):
        file = open(filename, "r+")
        lines = file.readlines()
        count = 0
        # Strips the newline character

        success_transfers = []
        filed_transfers = []
        waiting_transfers = []
        for job in lines:
            count += 1
            print("Line{}: {}".format(count, job.replace("\n", "").strip()))

            # if the fts job has been done during 1h 
            try :
                if job:
                    response = fts3.get_job_status(context, str(job.replace("\n", "")), list_files=True)
                    if response['http_status'] == "200 Ok":
                        if response["job_finished"]:
                            if response['job_state'] == "FINISHED":
                                print('succes')
                                for files in response['files'] : 
                                    gfal.unlink(files['source_surl'])
                                    gfal.unlink(files['dest_surl'])
                            elif response['job_state'] != "FAILED":
                                print('wait')
                            else:
                                print('failed')
                                for files in response['files'] : 
                                    gfal.unlink(files['source_surl'])
                                    gfal.unlink(files['dest_surl'])

            # if the fts job has been done during more than 1h 
            except : 
                response = json.loads(context.get("/jobs/" + str(job.replace("\n", ""))))
                if response['http_status'] == "200 Ok":
                    if response['job_state'] == "FINISHED":
                        success_transfers.append(job.replace("\n", ""))
                    elif response['job_state'] != "FAILED":
                        waiting_transfers.append(job.replace("\n", ""))
                    else:
                        filed_transfers.append(job.replace("\n", ""))

                if len(success_transfers) != 0:
                    if os.path.isfile('fts-success.txt'):
                        os.remove('fts-success.txt') 
                    for transfer in success_transfers :
                        write_fts_data(transfer, filename='fts-success.txt')

                if len(filed_transfers) != 0:
                    if os.path.isfile('fts-failed.txt'):
                        os.remove('fts-failed.txt') 
                    for transfer in filed_transfers :
                        write_fts_data(transfer, filename='fts-failed.txt')

                if os.path.isfile(filename):
                    os.remove(filename) 
                for transfer in waiting_transfers :
                    write_fts_data(job, filename=filename)



# In[24]:

def transfer_file(source, destination, number_of_files, output_name):
    sources_fts = _gfal_upload_files(source, number_of_files)
    fts_ids = _fts_submit_job(sources_fts, destination)
    write_fts_data(fts_ids, output_name)

def check_transfers(output_name):
    _fts_check_job(output_name)
    

def main():
    # Parse arguments from command line
    parser = argparse.ArgumentParser()

    # Set up required arguments this script
    parser.add_argument('function', type=str, choices=['transfer_file', 'check_transfers'], help='function to call')
    # Parse the given arguments
    #args = parser.parse_args()
    args, sub_args = parser.parse_known_args()
    
    # Get the function based on the command line argument and 
    # call it with the other two command line arguments as 
    # function arguments
   
    print(args.function)
    if args.function == 'transfer_file':
        
        parser = argparse.ArgumentParser()
        parser.add_argument('source', type=str, help='source')
        parser.add_argument('destination', type=str, help='destination')
        parser.add_argument('-n', '--number_of_files', type=int, help='number of files to transfers', default=1)    
        parser.add_argument('-o', '--output_name', type=str, help='output file name', default='fts-transfers.txt')
        args = parser.parse_args(sub_args)
        transfer_file(args.source, args.destination, args.number_of_files, args.output_name)
        # eval(args.function)(args.source, args.destination, args.number_of_files, args.output_name)
        
    elif args.function == 'check_transfers': 
        
        parser = argparse.ArgumentParser()
        parser.add_argument('-o', '--output_name', type=str, help='output file name', default='fts-transfers.txt')
        args = parser.parse_args(sub_args)
        check_transfers(args.output_name)        
        #eval(args.function)(args.output_name)

if __name__ == '__main__':
    main()
