"""
mpc_orb_creation/data_samples.py
 - Convenience code to get samples of orbfit-output data (json format)
 and save it to mpc_orb_creation/json_files
 - Expected to be used rarely (only during initialization of schema)
 - Expected to only be used internally by the MPC
 - As written requires (internal) access to MPC database

Author(s)
This module: MJP
"""


# Import third-party packages
# -----------------------
import json
from os.path import join, dirname, abspath, isfile
import psycopg2

# mpc imports
# -----------------------
import mpc_psql

# local imports
# -----------------------
#import schema
#import convert
#import interpret
from filepaths import filepath_dict


# Main functionality to extract samples or orbfit-results from MPC database
# -----------------------

class DBConnect():
    '''
    Class to allow
    (a) connection to the database
    (b) execution of canned queries
    '''
    def __init__(self, db_host='marsden.cfa.harvard.edu', db_user ='postgres', db_name='vmsops'):

        try:
            self.dbConn = mpc_psql.connect_to_vmsops(database=db_name,host=db_host)
            self.dbCur = self.dbConn.cursor()
            print("self.dbConn=",self.dbConn)
        except (Exception, psycopg2.Error) as error :
            print ("Error while connecting to PostgreSQL", error)
            


    def get_samples( self, n_samples , good=True):
        '''
        Get n_samples from the database
        
        At the time of writing the db table looked like ...
        vmsops=# \d orbfit_results
                                                           Table "public.orbfit_results"
                      Column                  |            Type             | Collation | Nullable |                  Default
    ------------------------------------------+-----------------------------+-----------+----------+--------------------------------------------
     id                                       | integer                     |           | not null | nextval('orbfit_results_id_seq'::regclass)
     packed_primary_provisional_designation   | text                        |           | not null |
     unpacked_primary_provisional_designation | text                        |           | not null |
     rwo_json                                 | json                        |           | not null |
     standard_epoch_json                      | json                        |           | not null |
     mid_epoch_json                           | json                        |           | not null |
     quality_json                             | json                        |           | not null |
     created_at                               | timestamp without time zone |           |          | timezone('utc'::text, now())
     updated_at                               | timestamp without time zone |           |          | timezone('utc'::text, now())
        '''
        
        # Sql query against orbfit_results table
        sql_str = f"""
            SELECT
                packed_primary_provisional_designation,
                unpacked_primary_provisional_designation,
                standard_epoch_json,
                rwo_json
            FROM
                orbfit_results
            WHERE
                quality_json->>'std_epoch' = 'ok' limit {n_samples}
            ;
            """
            
        print(sql_str)

        # Execute query
        return mpc_psql.psql_execute_query(sql_str , cnx_in = self.dbConn)
