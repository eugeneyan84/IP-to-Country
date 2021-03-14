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
    """Validate top-count parameter to be an integer between 1 and 100."""
    top_count_regex = r'^[1-9][0-9]?$|^100$'
    return re.match(top_count_regex, input)


def init_data():
    """
    Performs the following steps:

    1) Retrieves latest epoch value from http://software77.net/geo-ip/history/
    2) If retrieved epoch value is larger than what is saved in DB, proceed to download file for data extraction
    3) If data is successfully put into DB, update the latest epoch value into DB too
    """
    latest_epoch = dbutil.get_last_file_epoch()
    result = wutil.get_ip_to_country_data(latest_epoch)
    
    # result is a dictionary:
    # 'data' holds a dataframe of records extracted from CSV file
    # 'epoch' holds the epoch value of the downloaded CSV file (available in gzip filename that held the CSV file)
    if result['data'] is not None:
        dbutil.update_data_table(result['data'], result['epoch'])


def process_results(input):
    if input is not None:
        parsed = json.loads(input)
        print(json.dumps(parsed, indent=4))
    else:
        print('No result found.')

def get_country_from_ip(ip_address_str):
    if iputil.validate_ip(ip_address_str):
        init_data()
        
        numberic_ip = iputil.compute_ip_to_numeric(ip_address_str)
        result = dbutil.get_country_from_numeric_ip(numberic_ip)

        print('\nSearch result for {}:'.format(args.ip))
        process_results(result)
    else:
        print('Invalid IPv4 address [{}]'.format(args.ip))


def get_top_n_countries(top_count):
    if validate_top_count(top_count):
        init_data()
        
        result = dbutil.get_top_n_countries_by_largest_ip_range(int(top_count))
        
        print('\nSearch result for top {}:'.format(top_count))
        process_results(result)
    else:
        print('Invalid number parameter.')


if __name__ == "__main__":
    if args.ip is not None:
        get_country_from_ip(args.ip)
    elif args.n is not None:
        get_top_n_countries(args.n)