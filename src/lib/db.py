#import datetime
import os
import sys
import psycopg2
import psycopg2.errorcodes
from psycopg2 import sql
import re
import time

sys.path.append(os.path.join(os.path.dirname(__file__), "../.."))

import local_settings as settings

show_times = True
debug = False

def open_db(conn_string, transaction=True):
    '''
    initialize postgres session
    '''
    
    pconn = re.sub(r'password=[^ ]*', 'password=***', conn_string)
    print("Connecting:", pconn)
    conn = psycopg2.connect(conn_string)

    if transaction:
        conn.set_session(isolation_level=psycopg2.extensions.ISOLATION_LEVEL_READ_COMMITTED, autocommit=False)

    return conn

def do_sql(cursor, query, params=None, p=True):
    '''
    run SQL and print if desired
    '''
    if params:
        # apply parameters
        query = cursor.mogrify(query, params)

    # if we got bytes convert to unicode
    if isinstance(query, bytes):
        query = query.decode('utf-8')

    if p or debug:
        # debug output
        if isinstance(query, psycopg2.sql.Composable):
            print("SQL: %s" % query.as_string(cursor))
        elif isinstance(query, str):
            print("SQL: %s" % query)
        else:
            print("SQL: %s" % query.decode('utf-8'))
    
    if show_times:
        start = time.time()

    # returns None
    cursor.execute(query)

    if show_times:
        end = time.time()
        print("Took: %s seconds" % (end - start))    

def sql_from_file(cursor, file, args):
        '''
        Load, format and run an SQL template file
        file - sql file name
        args - dict of psycopg2.sql composable types
        '''
        with open(file, 'r') as i:
            # read and format
            query = sql.SQL(i.read()).format(**args)
        
        do_sql(cursor, query)
