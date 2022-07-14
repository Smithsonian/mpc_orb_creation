"""
mpc_orb_creation/utility_popn
 - The functions that are required to populate the orbfit_result table with mpc_orb_json(b) results
 - Expected to be for the initial population of thetable during development

Author(s)
This module: MJP
"""

# Third party imports
# -----------------------
import copy
import json
import sys, os

# MPC module imports
# -----------------------
try:
    sys.path.append('/sa/python_libs')
    import orbfit_to_dict as o2d
except:
    raise Exception("This conversion routine is intended for internal MPC usage and requires modules that are likely to only be available on internal MPC machines")

# local imports
# -----------------------
from .  import construct

# -------------------------------------------------------------------------
# Utility code to populate orbfit_result table with mpc_orb_json(b) results 
# -------------------------------------------------------------------------

def populate_orbfit_results( n_max = None ):
    """
    ... 
    """

    # Get list of designations to process 
    unpacked_desig_list = get_unpacked_desigs(n_max=n_max )

    # Loop through designations 
    for unpacked in unpacked_desig_list:

      # Get Data for Designation from Database
      rwo_dict , mid_epoch_dict,  standard_epoch_dict = fetch.get_dictionaries( unpacked = None , packed = packed)

      # Convert to standard orbfit dictionary
      orbfit_standard_dict = make_standard_dict(rwo_dict , mid_epoch_dict,  standard_epoch_dict) 

      # Convert to mpc_orb.json
      mpc_orb_dict = construct.construct(orbfit_standard_dict) 

      # Insert binary form of json into database
      # NB: At point of insert, check data is unchanged 

    return True 


def make_standard_dict(rwo_dict , mid_epoch_dict,  standard_epoch_dict):
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
  return orbfit_output_dict 

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


def get_unpacked_desigs( n_max = None):
  ''' Get list of designations from the orbfit_results table ...  
  '''
  # Define query string 
  limit_str = f"limit {n_max}" if isinstance(n_max,int) else "" 
  sql_str   = "SELECT unpacked_primary_provisional_designation FROM orbfit_results " + limit_str + ";" 

  # Execute query 

  # Return list of (unpacked) designations 
  return ... 

  
 
