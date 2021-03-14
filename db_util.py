from io import StringIO
import psycopg2
import pandas as pd
import json


config = json.load(open('./config.json'))
CONFIG_TABLE = config['DB_TABLE_CONFIG']
DATA_TABLE = config['DB_TABLE_DATA']
DB_NAME = config['DB_NAME']
DB_USER = config['DB_USER']
DB_HOST = config['DB_HOST']
DB_PORT = config['DB_PORT']
DB_PWD = config['DB_PWD']


def validate(input_df):
    if input_df is not None:
        row_count, col_count = input_df.shape
        #print('row_count: {}, col_count: {}'.format(row_count, col_count))
        if col_count != 10:
            return 'Malformed dataframe, expecting 10 columns'
        if row_count == 0:
            return 'No records in dataframe'
        return None
    else:
        return 'No dataframe'


def get_conn():
    return psycopg2.connect(
        dbname = DB_NAME,
        user = DB_USER,
        host = DB_HOST,
        port = DB_PORT,
        password = DB_PWD
    )


def get_last_file_epoch():
    """
    Retrieves LATEST_FILE_EPOCH configuration record from config table in DB.
    """
    conn = None
    result = -1
    try:
        conn = get_conn()

        df = pd.read_sql_query(f"SELECT param_value FROM {CONFIG_TABLE} WHERE key_id='LATEST_FILE_EPOCH'", conn)

        if df is not None and df.shape[0] > 0:
            result = int(df.loc[:,'param_value'].values[0])
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()

    return result


def update_last_file_epoch(epoch_value, con=None):
    """
    Updates LATEST_FILE_EPOCH configuration record with specified epoch_value
    """
    updated_rows = 0
    try:
        conn = get_conn() if con is None else con

        cur = conn.cursor()

        cur.execute(f"UPDATE {CONFIG_TABLE} SET param_value={epoch_value} WHERE key_id='LATEST_FILE_EPOCH';")

        updated_rows = cur.rowcount

        conn.commit()
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()

    return updated_rows

def update_data_table(input_df, epoch_value):
    """
    Performs bulk-insert of records in dataframe to data table in DB.
    Also updates the epoch_value to config table if bulk-insert operation
    is successful.
    """
    result = False
    validation_result = validate(input_df)
    if validation_result is not None:
        raise Exception(validation_result)

    strio = StringIO()
    strio.write(input_df.to_csv(index=None, header=None))  # Write the dataframe as csv to the io-buffer
    strio.seek(0)  # reset the cursor position to start of stream

    conn = get_conn()
    with conn.cursor() as cur:
        cur.execute(f"DELETE FROM {DATA_TABLE};") # clear the table first
        cur.copy_from(strio, DATA_TABLE, columns=input_df.columns, sep=',')
        conn.commit()
        result = (update_last_file_epoch(epoch_value, conn) == 1)

    return result


def get_country_from_numeric_ip(input: int):
    """
    Uses the numeric format of an IPv4 address to search data table and attempt to retrieve country and respective IP range.
    """
    conn = None
    result = None
    try:
        conn = get_conn()

        COUNTRY_QUERY = f"SELECT country, CONCAT(ip_from_str, ' - ', ip_to_str) AS ip_range FROM {DATA_TABLE} WHERE {input} BETWEEN ip_from AND ip_to;"
        df = pd.read_sql_query(COUNTRY_QUERY, conn)
        if df is not None:
            result = df.to_json(orient='records')
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
    
    return result

def get_top_n_countries_by_largest_ip_range(top_count):
    """
    Retrieves top N countries sorted by the cumulative quantity of unique IPs assigned to them respectively.
    """
    conn = None
    result = None
    try:
        conn = get_conn()

        IP_RANGE_RANK_QUERY = f"""
            with cte as (
                select (titc.ip_to - titc.ip_from + 1) as num_unique_ips,
                titc.country 
                from {DATA_TABLE} titc 
            )
            select 
                c.country, 
                sum(c.num_unique_ips) as total_num_unique_ips,
                RANK () OVER ( 
                    ORDER BY sum(c.num_unique_ips) DESC
                ) ip_range_size_rank 
            from cte c
            group by c.country
            limit {top_count}
        """
        df = pd.read_sql_query(IP_RANGE_RANK_QUERY, conn)
        df.loc[:,'total_num_unique_ips'] = df.loc[:,'total_num_unique_ips'].astype(int)
        result = df.to_json(orient="records")
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
    
    return result