import json
# Import parser 
import argparse

parser = argparse.ArgumentParser()

parser.add_argument('--load_json',
    help='Load settings from file in json format. Command line options override values in file.')

args = parser.parse_args()

if args.load_json:
    with open(args.load_json) as f:
        json_string = f.read()
        try:
            parsed_json = json.loads(json_string)
            formatted_json = json.dumps(parsed_json, indent = 4,sort_keys=True)
            with open(args.load_json,"w") as f:
                f.write(formatted_json)
        except Exception as e:
            print(repr(e))
