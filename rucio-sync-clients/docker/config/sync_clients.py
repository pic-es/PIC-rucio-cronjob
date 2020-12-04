#!/usr/bin/env python

import json
import sys
import traceback

#from rucio.api.vo import add_vo
from rucio.client import Client
from rucio.common.config import config_get, config_get_bool
from rucio.common.exception import Duplicate
#from rucio.core.account import add_account_attribute
from rucio.common.types import InternalAccount


if __name__ == '__main__':
    
    # parameters
    rse_repo_file = '/account_repository.json'
    json_data = open(rse_repo_file)
    repo_data = json.load(json_data)
    json_data.close()

    c = Client()
    for client in repo_data:
        print(client)
        #try:
        #    c.add_account(client, 'SERVICE', '')
        #except Duplicate:
        #    print('Account {} already added'.format(client))

