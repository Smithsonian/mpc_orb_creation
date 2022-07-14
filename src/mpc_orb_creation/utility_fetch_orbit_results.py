#Import standard 
import sys, os 
import psycopg2
import psycopg2.extras

#Import local
import mpc_astro as ma
import mpc_psql

# -----------------------------------------------------------------------------
#Various convenience functions for extracting results from orbfit_results table 
# -----------------------------------------------------------------------------
def query_unpacked_orbfit_results(n_max=None):
  '''
  '''
  # Connect to db
  cnx = mpc_psql.connect_to_vmsops()#database='vmsops',host='localhost')

  # Define the query to be executed 
  limit_str = f"limit {n_max}" if isinstance(n_max,int) else ""
  sql_str   = "SELECT unpacked_primary_provisional_designation FROM orbfit_results " + limit_str + ";"

    # Get a fancy "dictionary cursor"  
  cur = cnx.cursor()#cursor_factory = psycopg2.extras.RealDictCursor)

  # Execute the query 
  cur.execute(sql_str)
  results = cur.fetchall()

  if results : return [_[0] for _ in results]
  else:        return {}
 

def query_desig( unpacked = None, packed = None):
  ''' Query the orbfit_results table for a particular designation ...
  '''
  # Connect to db
  cnx = mpc_psql.connect_to_vmsops()#database='vmsops',host='localhost')

  # Define the query to be executed 
  if unpacked is not None:
    sqlstr = f"SELECT * FROM orbfit_results WHERE unpacked_primary_provisional_designation = '{unpacked}'"
  elif packed is not None:
    sqlstr = f"SELECT * FROM orbfit_results WHERE packed_primary_provisional_designation = '{packed}'"
  else:
    return {}

  # Get a fancy "dictionary cursor"  
  cur = cnx.cursor(cursor_factory = psycopg2.extras.RealDictCursor)
  
  # Execute the query 
  cur.execute(sqlstr)
  results = cur.fetchall()
  
  if results : return results[0]
  else:        return {}


def get_dictionaries(unpacked = None, packed = None):
  ''' gets the 3 main dictionaries ... rwo_dict , mid_epoch_dict,  standard_epoch_dict ... from the db''' 
  row = query_desig( unpacked = unpacked , packed = packed)
  if row: 
    return row['rwo_json'] , row['mid_epoch_json'], row['standard_epoch_json']
  else:
    return {}, {}, {} 

def test_get_dictionaries(unpacked = None, packed = None):
  rwo_dict , mid_epoch_dict,  standard_epoch_dict = get_dictionaries( unpacked = unpacked , packed = packed)
  print('rwo_dict...\n',            rwo_dict, '\n')
  print('mid_epoch_dict...\n',      mid_epoch_dict, '\n')
  print('standard_epoch_dict...\n', standard_epoch_dict, '\n')


if __name__ == '__main__':
  test_get_dictionaries( packed = 'K05SG8D')
