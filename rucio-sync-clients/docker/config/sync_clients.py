#!/usr/bin/env python

import json
import sys
import traceback

from rucio.api.vo import add_vo
from rucio.client import Client
from rucio.common.config import config_get, config_get_bool
from rucio.common.exception import Duplicate
from rucio.core.account import add_account_attribute
from rucio.common.types import InternalAccount


if __name__ == '__main__':
    if config_get_bool('common', 'multi_vo', raise_exception=False, default=False):
        vo = {'vo': config_get('client', 'vo', raise_exception=False, default='tst')}
        try:
            add_vo(new_vo=vo['vo'], issuer='super_root', description='A VO to test multi-vo features', email='N/A', vo='def')
        except Duplicate:
            print('VO {} already added'.format(vo['vo']) % locals())
    else:
        vo = {}

    # parameters
    if argv:
        rse_repo_file = argv[0]
    else:
        rse_repo_file = '/rse_repository.json'
    json_data = open(rse_repo_file)
    repo_data = json.load(json_data)
    json_data.close()

    c = Client()
    for client in repo_data:
        print(client)
