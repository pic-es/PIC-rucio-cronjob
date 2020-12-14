#!/usr/bin/env python

import json
import sys
import traceback

from rucio.client import Client
from rucio.common.exception import Duplicate


UNKNOWN = 3
CRITICAL = 2
WARNING = 1
OK = 0

fts_pic = "https://fts01.pic.es:8446"

def main(argv):
    # parameters
    if argv:
        rse_repo_file = argv[0]
    else:
        rse_repo_file = '/rse_repository.json'

    json_data = open(rse_repo_file)
    repo_data = json.load(json_data)
    json_data.close()

    c = Client()
    for rse in repo_data:
        print(rse)
        try:
            if "deterministic" in repo_data[rse]:
                deterministic = repo_data[rse].get('deterministic', True)
            elif "deterministic" in repo_data[rse] and repo_data[rse]["deterministic"] == False :
                deterministic = repo_data[rse].get('deterministic', False)
            else : 
                deterministic = repo_data[rse].get('deterministic', True)
            volatile = repo_data[rse].get('volatile', False)
            region_code = repo_data[rse].get('region_code')
            country_name = repo_data[rse].get('country_name')
            staging_area = repo_data[rse].get('staging_area')
            continent = repo_data[rse].get('continent')
            time_zone = repo_data[rse].get('time_zone')
            ISP = repo_data[rse].get('ISP')
            print()
            print('Trying to add {} rse'.format(rse)) 
            c.add_rse(rse, deterministic=deterministic, volatile=volatile, region_code=region_code, country_name=country_name, staging_area=staging_area, continent=continent, time_zone=time_zone, ISP=ISP)
            print(deterministic, volatile, region_code, country_name, staging_area, continent, time_zone, ISP) 
        except Duplicate:
            print('%(rse)s already added' % locals())
        except:
            errno, errstr = sys.exc_info()[:2]
            trcbck = traceback.format_exc()
            print('Interrupted processing with %s %s %s.' % (errno, errstr, trcbck))
        for p_id in repo_data[rse]['protocols']['supported']:
            try:
                print(repo_data[rse]['protocols']['supported'][p_id])
                p = repo_data[rse]['protocols']['supported'][p_id]
                p['scheme'] = p_id
                print(p)
                c.add_protocol(rse, p)
            except ValueError as e:
                print(rse, e)
            except Duplicate as e:
                print(rse, e)
            except Exception:
                errno, errstr = sys.exc_info()[:2]
                trcbck = traceback.format_exc()
                print('Interrupted processing for %s with %s %s %s.' % (rse, errno, errstr, trcbck))
        try:
           c.add_rse_attribute(rse, key="fts", value=fts_pic)
           print("Successfully added fts {} to RSE {}".format(fts_pic, rse))
        except: 
           errno, errstr = sys.exc_info()[:2]
           trcbck = traceback.format_exc()
           print('Interrupted processing with %s %s %s.' % (errno, errstr, trcbck))
        try:
           # c.set_rse_limits(rse, name="root", value=-1)
           c.set_local_account_limit(account='root', rse=rse, bytes=-1)
           print("Successfully locally set limits for RSE {}".format(rse))
        except:
           errno, errstr = sys.exc_info()[:2]
           trcbck = traceback.format_exc()
           print('Interrupted processing with %s %s %s.' % (errno, errstr, trcbck))
        
        try:
           # c.set_rse_limits(rse, name="root", value=-1)
           c.set_global_account_limit(account='root', rse_expression=rse, bytes=-1)
           print("Successfully globaly set limits for RSE {}".format(rse))
        except:
           errno, errstr = sys.exc_info()[:2]
           trcbck = traceback.format_exc()
           print('Interrupted processing with %s %s %s.' % (errno, errstr, trcbck))

        rses = c.list_rses()
        for src in rses:
           for dst in rses:
               print("Trying to set distance between RSE {} and {}".format(src['rse'], dst['rse']))
               try:
                  #c.add_distance(source=src['rse'], destination=dst['rse'], parameters={"ranking":1, "distance":1})
                  c.add_distance(source=dst['rse'], destination=src['rse'], parameters={"ranking":1, "distance":1})
                  print("Successfully added distance between RSEs {} and {}".format(src['rse'], dst['rse']))
               except Duplicate:
                  print('{} {} already added'.format(src['rse'], dst['rse'])
               except:
                  errno, errstr = sys.exc_info()[:2]
                  trcbck = traceback.format_exc()
                  print('Interrupted processing with %s %s %s.' % (errno, errstr, trcbck))

               try:
                  c.add_distance(source=src['rse'], destination=dst['rse'], parameters={"ranking":1, "distance":1})
                  #c.add_distance(source=dst['rse'], destination=src['rse'], parameters={"ranking":1, "distance":1})
                  print("Successfully added distance between RSEs {} and {}".format(dst['rse'], src['rse']))
               except Duplicate:
                  print('{} {} already added'.format(dst['rse'], src['rse'])
               except:
                  errno, errstr = sys.exc_info()[:2]
                  trcbck = traceback.format_exc()
                  print('Interrupted processing with %s %s %s.' % (errno, errstr, trcbck))


if __name__ == '__main__':
    main(sys.argv[1:])
