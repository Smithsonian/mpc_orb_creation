# standard imports 
import os, sys
import glob 
import json 

# marsden imports
from mpc_orb_creation import create_output_dictionariesNEW2022_03_XX as cod #create_output_dictionaries as cod 
from mpc_orb_creation import utility_fetch_orbit_results as fetch 

# directories...
test_dir = os.path.dirname(os.path.realpath(__file__))
code_dir = os.path.dirname(test_dir)
data_dir = os.path.join(code_dir, 'test_data')

# utility functionalities 
# ---------------------

def create_input_dict(workdir, arg_dict ,args):
    ''' Create input dictionary required for cod.create_output_dictionaries()
        Stolen from /sa/orbit_utils/preliminary_orbit.py 
                 &  /sa/orbit_wrappers/orbit_wrappers/generate_standardized_output.py  
    '''
    workdir = workdir if workdir[-1] == '/' else workdir + '/'

    input_dict = {
        #'eq0file' : None,
        #'eq1file' : None,
        #'rwofile' : None,
        #'moidsfile' :None,
	'direct_dict_input' : False, 
        'eq0dict' : None, 
	'eq1dict' : None, 
        'rwodict' : None, 
	'moidsdict' : None, 
        'workdir' : workdir,
        'orbfit_main' : 'neocp',
        'iod_neocp_opt' : False,
        'iod_nominalfile' : None,
        'iod_mcmcfile' : None,
        'orbfit_unpacked_desig' : None,
        'trksub' : None,
        'unpacked_provid' : None,
        'unpacked_permid' : None,
        'packed_provid' : None,
        'packed_permid' : None,
        'bad_trk_params' : {}
    }
    
 
    input_dict['orbfit_main'] = 'neocp'
    input_dict['iod_neocp_opt'] = args['neocp'] # <<-- Is it an NEOCP object
    #No numbered objects
    input_dict['unpacked_permid'] = None
    input_dict['bad_trk_params'] = args['bad_trk_dict']

    return input_dict





# test functions ...
# ---------------------
def test_create_input_dict():
  ''' 
  The *create_output_dictionaries...* function takes as input a particular dictionary format
  Here we test the creation of that input_dict
  Note that the tests at this stage are minimal / non-existant : we just get SOMETHING out of the *create_input_dict* func 
  '''
  # orbfit-results directory to test
  dirs = [os.path.join(data_dir,_) for _ in os.listdir(data_dir) if os.path.isdir( os.path.join(data_dir,_)) and 'MPan' not in _]

  # Loop through the test-data directories ...
  for d in dirs[:1]:
    print(d)
    # Call the function to create the arg-dict ...
    args = {       'neocp' : "N" ,
                                                                'istrksub':"N" if ... else "Y" ,
                                                                'bad_trk_dict':{'bad_obs_weight':5.0,
                                                                                'fraction_bad':  0.5,
                                                                                'bad_obs_threshhold':1.0
                                                                                },
    	   }
    arg_dict = {
      'packed_primary_provisional_designation_list' : [], 
    }
    input_dict = create_input_dict( d, arg_dict ,args)
    assert input_dict



def test_create_output_dict():
  ''' 
  We use the input_dict created by the *create_input_dict* function to call the *create_output_dictionaries* function
  Note that the tests of the returned orbfit_output_dict are minimal at present. 

  ''' 
  # orbfit-results directory to test
  dirs = [os.path.join(data_dir,_) for _ in os.listdir(data_dir) if os.path.isdir( os.path.join(data_dir,_))  and 'MPan' not in _]

  # Loop through the test-data directories ...
  for d in dirs[:1]:
    print(d)
    # Call the function to create the arg-dict ...
    args = {       'neocp' : "N" ,
                                                                'istrksub':"N" if ... else "Y" ,
                                                                'bad_trk_dict':{'bad_obs_weight':5.0,
                                                                                'fraction_bad':  0.5,
                                                                                'bad_obs_threshhold':1.0
                                                                                },
           }
    arg_dict = {
      'packed_primary_provisional_designation_list' : [],
    }
    input_dict = create_input_dict( d, arg_dict ,args)
    assert input_dict

    # Call the function to create the big output dictionary from the various orbfit files
    orbfit_output_dict = cod.create_output_dictionaries( input_dict )  
    assert isinstance(orbfit_output_dict, dict)
    print(orbfit_output_dict)      


def test_dict_input_A():
  '''
  We provide dictionaries as input to the ... function
  We test that the ... function returns a dict as expected
  '''
  # Fetch the dictionaries from the database ...
  rwo_dict , mid_epoch_dict,  standard_epoch_dict = fetch.get_dictionaries( unpacked = None , packed = 'K05SG8D') 
  assert rwo_dict and mid_epoch_dict and  standard_epoch_dict

  # Create the default input dictionary (just copied from *test_create_output_dict*, above)
  args = {       'neocp' : "N" ,
                                                                'istrksub':"N" if ... else "Y" ,
                                                                'bad_trk_dict':{'bad_obs_weight':5.0,
                                                                                'fraction_bad':  0.5,
                                                                                'bad_obs_threshhold':1.0
                                                                                },
           }
  arg_dict = {
      'packed_primary_provisional_designation_list' : ['K05SG8D'],
    }
  input_dict = create_input_dict( 'no_directory', arg_dict ,args)
  assert input_dict

  # Add dictionaries from the database to the input_dict, and set the appropriate variable(s) ...
  input_dict['direct_dict_input'] = True 
  input_dict['eq0dict'] = mid_epoch_dict
  input_dict['eq1dict'] = standard_epoch_dict
  input_dict['rwodict'] = rwo_dict
  input_dict['moidsdict'] = {} 


  # Call the function to create the big output dictionary from the input dictionaries ...
  orbfit_output_dict = cod.create_output_dictionaries( input_dict )
  assert isinstance(orbfit_output_dict, dict)

def test_dict_input_B():
  ''' As per def test_dict_input_A(), but save to file '''

  # Fetch the dictionaries from the database ...
  packed = 'K05SG8D'
  rwo_dict , mid_epoch_dict,  standard_epoch_dict = fetch.get_dictionaries( unpacked = None , packed = packed)
  assert rwo_dict and mid_epoch_dict and  standard_epoch_dict

  # Create the default input dictionary (just copied from *test_create_output_dict*, above)
  args = {       'neocp' : "N" ,
                                                                'istrksub':"N" if ... else "Y" ,
                                                                'bad_trk_dict':{'bad_obs_weight':5.0,
                                                                                'fraction_bad':  0.5,
                                                                                'bad_obs_threshhold':1.0
                                                                                },
           }
  arg_dict = {
      'packed_primary_provisional_designation_list' : ['K05SG8D'],
    }
  input_dict = create_input_dict( 'no_directory', arg_dict ,args)
  assert input_dict

  # Add dictionaries from the database to the input_dict, and set the appropriate variable(s) ...
  input_dict['direct_dict_input'] = True
  input_dict['eq0dict'] = mid_epoch_dict
  input_dict['eq1dict'] = standard_epoch_dict
  input_dict['rwodict'] = rwo_dict
  input_dict['moidsdict'] = {}


  # Call the function to create the big output dictionary from the input dictionaries ...
  orbfit_output_dict = cod.create_output_dictionaries( input_dict )
  assert isinstance(orbfit_output_dict, dict)

  # Save json to file
  filepath = os.path.join( '/sa/orbfit_output_dictionary/test_data/', packed + '.json')
  if os.path.isfile(filepath): os.remove(filepath)
  with open(filepath, 'w') as fp:
    json.dump(orbfit_output_dict, fp, sort_keys=True, indent=4)
  assert os.path.isfile(filepath)

# ---------------------
if __name__ == '__main__':
  test_dict_input_B()

