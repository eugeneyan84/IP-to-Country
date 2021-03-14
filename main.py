import argparse
import json
import re
import ip_util as iputil
import web_util as wutil
import db_util as dbutil

parser = argparse.ArgumentParser()

parser.add_argument(
    "-map", 
    "--ip", 
    help="Maps a specified IPv4 address (e.g. 42.60.163.97) to the country that it is assigned to.")
parser.add_argument(
    "-top", 
    "--n", 
    help="Returns the top N (between 1 to 100) countries ranked by the cumulative quantity of their unique IP assignments.")

args = parser.parse_args()


def validate_top_count(input):
    top_count_regex = r'^[1-9][0-9]?$|^100$'
    return re.match(top_count_regex, input)


def init_data():
    latest_epoch = dbutil.get_last_file_epoch()
    result = wutil.get_ip_to_country_data(latest_epoch)
    
    if result['data'] is not None:
        #print('result[data] is not empty, updating DB now')
        dbutil.update_data_table(result['data'], result['epoch'])

if args.ip is not None:
    if iputil.validate_ip(args.ip):
        init_data()
        
        numberic_ip = iputil.compute_ip_to_numeric(args.ip)
        result = dbutil.get_country_from_numeric_ip(numberic_ip)

        print('\nSearch result for {}:'.format(args.ip))
        if result is not None:
            parsed = json.loads(result)
            print(json.dumps(parsed, indent=4))
        else:
            print('No result found.')
    else:
        print('Invalid IPv4 address [{}]'.format(args.ip))
    print('\n')
elif args.n is not None:
    top_count = args.n
    if validate_top_count(top_count):
        init_data()
        
        result = dbutil.get_top_n_countries_by_largest_ip_range(int(top_count))
        
        print('\nSearch result for top {}:'.format(top_count))
        if result is not None:
            parsed = json.loads(result)
            print(json.dumps(parsed, indent=4))
        else:
            print('No result found.')
    else:
        print('Invalid number parameter.')
    print('\n')