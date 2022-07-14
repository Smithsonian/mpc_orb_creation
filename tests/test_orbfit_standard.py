# standard imports
import os, sys
import pprint ; pp = pprint.PrettyPrinter(indent=4)

# local imports
from mpc_orb_creation import template
from mpc_orb_creation import schema
from mpc_orb_creation import construct
from mpc_orb_creation.filepaths import filepath_dict

# ---- Tests ----
def test_read():
  ''' '''
  # get filepath(s) of sample standardized orbfit output dict/json 
  fps = filepath_dict['test_pass_orbfit_standard']
  assert fps

  # loop through it/them ...
  for fp in fps : 
    assert os.path.isfile(fp) 


def test_construct_A():
  ''' ''' 
  # loop through filepath(s) of sample standardized orbfit output dict/json 
  for fp in filepath_dict['test_pass_orbfit_standard']: 
    print('fp=', fp)
    
    # call the construct module...
    result = construct.construct(fp)
    print('result=...')
    pp.pprint(result)
if __name__ == '__main__':
  test_construct_A() 
