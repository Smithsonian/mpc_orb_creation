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
import pprint

# MPC module imports
# -----------------------
sys.path.append('/sa/orbit_utils/')
import create_output_dictionaries2023 as create_output

from count_opps import count_opps


from mpc_orb_creation import construct

import orbfit_to_dict

sys.path.append('/sa/python_libs'); import mpc_psql


# local imports
# -----------------------
#from . import construct
import utility_fetch_orbit_results as fetch  
#from . import create_output_dictionariesNEW2022_03_XX as cod


# -------------------------------------------------------------------------
# Utility code to populate orbfit_result table with mpc_orb_json(b) results 
# -------------------------------------------------------------------------

def populate_orbfit_results( n_max = None ):
    """
    """

    # Get list of designations to process 
    unpacked_desig_list = fetch.query_unpacked_orbfit_results(n_max=n_max )
    print(f'len(unpacked_desig_list)={len(unpacked_desig_list)}')
  
    # Loop through designations 
    for n, unpacked in enumerate(unpacked_desig_list):
      print(n, unpacked) 

      try:
        # Get Data for Designation from Database
        rwo_dict , mid_epoch_dict,  standard_epoch_dict, updated_at, ele220 = fetch.get_dictionaries( unpacked = unpacked )

        # Skip on to the next object if we do not have data to work with ...
        if not (rwo_dict and mid_epoch_dict and mid_epoch_dict):
          continue         

        # "otherdict" to pass in assorted parameters ...
        # NB: Because we are 'back-filling' from the database, some of these other params are going to be untrustworthy
        # - E.g. the badtrk_params *may* NOT be the ones used at the time the orbit wasa evaluated
        otherdict = {}
        otherdict['orbfit_computation_type'] = 'EXTENSION'

        # Use updated_at as the time of orbfit-run (close enough) 
        otherdict['orbfit_run_datetime'] = updated_at.strftime("%Y/%m/%d_%H:%M:%S") if updated_at else ''

        # collect number of oppositions from ele220
        if ele220 is None:
 
          print('HERE: ele220=', ele220)
          orbfit_to_dict.dict_to_rwo(rwo_dict,'2000NB21.rwo')
          orbfit_to_dict.dict_to_fel(standard_epoch_dict,'2000NB21.fel')
          otherdict['nopp'] = count_opps(rwofile='2000NB21.rwo' , elsfile='2000NB21.fel'  )
        else:
          otherdict['nopp'] = int(ele220[140:144].strip())

        moid_dict={}
        mpcorb_dict = construct.construct( mid_epoch_dict, standard_epoch_dict ,rwo_dict, moid_dict, otherdict  )








        # Insert binary form of json into database
        # NB: At point of insert, check data is unchanged 
        insert_mpc_orb_dict(unpacked, updated_at, mpcorb_dict)

      except Exception as e:
        print('Exception processing', n, unpacked )
        print(e)
        print()


      # Clean up any unnecessary files 
      #os.system("rm *elements *oppfile.log *.clo *.err *.fel *.fga *.fop *.fou *.opp *.pro *.rms *.run *rwo fort.10 badtrkfile_*") 

    return True 

def insert_mpc_orb_dict(unpacked, updated_at, mpc_orb_dict):
  ''' '''
  print('insert_mpc_orb_dict')
  # Connect to db
  cnx = mpc_psql.connect_to_vmsops()#database='vmsops',host='localhost')

  # Dump dict to 
  my_json = json.dumps(mpc_orb_dict)
  print(f'type my_json = {type(my_json)}')
  # Construct sql
  sql_str = f"UPDATE orbfit_results SET mpc_orb_jsonb = '{my_json}' WHERE unpacked_primary_provisional_designation = '{unpacked}' and updated_at = '{updated_at}'; " 

  # Execute
  cursor = cnx.cursor()
  cursor.execute(sql_str)
  cnx.commit() 
  print('DONE:insert_mpc_orb_dict')


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

if __name__ == "__main__":
  populate_orbfit_results()
