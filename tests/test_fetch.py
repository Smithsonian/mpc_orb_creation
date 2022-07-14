# standard imports 
import os, sys
import glob 
import json 

# local imports
from mpc_orb_creation import utility_fetch_orbit_results as fetch

# directories...
test_dir = os.path.dirname(os.path.realpath(__file__))
code_dir = os.path.dirname(test_dir)
data_dir = os.path.join(code_dir, 'test_data')

# utility functionalities 
# ---------------------
def test_fetch_unpacked_desig_list_A():
  '''
  '''
  # Fetch the list of designations
  for n_max in [10,100,1000]: 
    result = fetch.query_unpacked_orbfit_results(n_max=n_max)
    assert len(result) == n_max 

def test_fetch_dict_A():
  '''
  '''
  # Fetch the dictionaries from the database ...
  rwo_dict , mid_epoch_dict,  standard_epoch_dict = fetch.get_dictionaries( unpacked = None , packed = 'K05SG8D') 
  assert rwo_dict and mid_epoch_dict and  standard_epoch_dict

if __name__ == '__main__':
  test_fetch_unpacked_desig_list_A()
  test_fetch_dict_A()
  print('tests complete')
