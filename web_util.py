from bs4 import BeautifulSoup
import requests
import re
import os
import json
import gzip
import pandas as pd
import ip_util as iputil


config = json.load(open('./config.json'))
IP_TO_COUNTRY_URL = config['IP_TO_COUNTRY_URL']


def extract_data(target_file: str):
    """Downloads gzip file, decompresses it and performs data-extraction from CSV payload and returns records in a dataframe."""
    
    # capture response from the full URL to download the gzip file
    r = requests.get(''.join([IP_TO_COUNTRY_URL, target_file]))
    
    # write the gzip file to current working directory
    gz_file_path = './'+target_file
    with open(gz_file_path, 'wb') as f:
        f.write(r.content)

    # define column names that correspond to the 7 features in the CSV file
    original_headers = ['ip_from','ip_to','registry','assigned','ctry','cntry','country']

    # Read the CSV data from the gzip file. Values are comma-separated and enclosed within
    # double quotes. 
    df = pd.read_csv(
        gz_file_path, 
        compression='gzip', 
        sep=',', 
        quotechar='"', 
        comment='#', 
        keep_default_na=False,
        names=original_headers, 
        encoding='ISO-8859-1')
    
    # Map the numeric IP values to common string format for both `ip_from` and `ip_to` fields
    df.loc[:,'ip_from_str'] = df.loc[:,'ip_from'].apply(iputil.compute_numeric_to_ip)
    df.loc[:,'ip_to_str'] = df.loc[:,'ip_to'].apply(iputil.compute_numeric_to_ip)
    df.loc[:, 'id'] = df.index
    df = df.loc[:,['id', 'ip_from', 'ip_from_str', 'ip_to', 'ip_to_str', 'registry','assigned','ctry','cntry','country']]
    
    # clean up the gzip file
    os.remove(gz_file_path)

    return df


def get_ip_to_country_data(last_epoch_value=0):
    """
    Retrieves latest file and associated epoch value from IP-to-country website.
    Data extraction method would be called if the associated epoch value is larger
    than the databse value passed to this method.
    """

    # filename format of ip-to-country compressed file
    GZ_FILE_REGEX = r'^IpToCountry\.[0-9]+\.csv\.gz$'
    current_epoch = 0
    result = {'data': None, 'epoch': current_epoch }

    page = requests.get(IP_TO_COUNTRY_URL)

    if page.status_code == 200:
        target_filename = None
        soup = BeautifulSoup(page.content, 'html.parser')
        for item in soup.find_all('a', href = re.compile(GZ_FILE_REGEX)):

            # numerical value in filename is the epoch value that denotes
            # the timestamp of the data. The higher the numerical value, 
            # the more recent the file is, i.e. the latest file would have
            # the largest numerical value. It is compared against the database
            # value, and is taken as the new reference is it is larger.
            if int(item['href'].split('.')[-3]) > last_epoch_value:
                current_epoch = int(item['href'].split('.')[-3])
                target_filename = item['href']

        if target_filename:
            df = extract_data(target_filename)
            result['data'] = df
            result['epoch'] = current_epoch
    
    return result