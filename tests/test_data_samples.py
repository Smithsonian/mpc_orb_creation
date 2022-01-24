"""
Testing the mpc_orb_creation/data_samples.py functions
 - These are intended to get samples of orbfit-output data (json format)
 and save it to mpc_orb_creation/json_file
 
"""

# Local imports
# -----------------------
from os.path import join, dirname, abspath, isfile
from os import remove

import sys
pack_dir  = dirname(dirname(abspath(__file__))) # Package directory
code_dir  = join(pack_dir, 'mpc_orb_creation')
sys.path.append(code_dir)

from filepaths import filepath_dict
import data_samples

# Tests
# -----------------------
def test_get_samples_A():
    n_samples = 5
    result = data_samples.DBConnect().get_samples( n_samples )
    
    assert len(result) == n_samples
    print(result)

test_get_samples_A()
