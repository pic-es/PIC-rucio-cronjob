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
        
        if 'email' in repo_data[client]: 
            email = repo_data[client]['email']
        else :
            email = 'None'

        if email == None:
            email = 'bruzzese@pic.es'

        try:
            c.add_account(client, 'SERVICE', email)
        except Duplicate:
            print('Account {} already added'.format(client))

        try:
            scope = 'test-' + str(client)
            c.add_scope(client, scope)
        except Duplicate:
            print('Scope {} already added'.format(scope))

        print(list(c.list_identities(client)))
        if 'x509' in repo_data[client]:
            for id in repo_data[client]['x509'] :
               try:
                   c.add_identity(account=client, identity=id, authtype='x509', email=email)
               except Exception:
                   print('Already added: ', id)

        if 'GSS' in repo_data[client]:
            for id in repo_data[client]['GSS'] :
               try:
                   c.add_identity(account=client, identity=id, authtype='GSS', email=email)
               except Exception:
                   print('Already added: ', id)

        if 'GSS' in repo_data[client]:
            for id in repo_data[client]['GSS'] :
                try:
                   c.add_identity(account=client, identity=id, authtype='GSS', email=email)
                except Exception:
                   print('Already added: ', id)

        if 'USERPASS' in repo_data[client]:
            user = repo_data[client]['USERPASS'][0] 
            pswd = repo_data[client]['USERPASS'][1]

            if email == None:
                print('email is null')
                email = 'bruzzese@pic.es'

            try:
                
                print(user,pswd,email)
                c.add_identity(account=client, identity=user, authtype='userpass', password=pswd, email=email)
            
            except Duplicate :
                print('Already added: ', user)

        print(list(c.list_identities(client)))
