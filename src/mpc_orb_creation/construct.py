"""
mpc_orb_creation/convert.py
 - The functions that are required to convert orbfit output (in json format) to an mpc_orb.json
 - Expected to be used frequently to convert the output from orbfit
 - As written it requires modules that are likely to only be available on internal MPC machines
 
*** Note added 2022-01-24: May need to add ability to ingest rwo files as part of creation ***

Author(s)
This module: MJP
Many contained functions: MPan
"""

# Standard imports
# -----------------------
import copy
import json
import sys, os
import requests 
from datetime import datetime

# Public-MPC Import!!!
# -----------------------
import mpc_orb

# MPC module imports
# -----------------------
from designation_identifier import identifier
from db_client import DatabaseClient
try:
    sys.path.append('/sa/python_libs')
    import orbfit_to_dict as o2d
    import mpc_astro as ma

except:
    raise Exception("This conversion routine is intended for internal MPC usage and requires modules that are likely to only be available on internal MPC machines")



# local imports
# -----------------------
from .  import interpret
#from .schema import validate_orbfit_standardized , validate_mpcorb # , validate_orbfit_conversion , validate_orbfit_construction
from .  import template

# -------------------------------------------------------------------
# Main code to run conversion/construction from orbfit-to-mpc_orb
# -------------------------------------------------------------------

def construct(eq0dict,eq1dict,rwodict,moidsdict,otherdict , output_filepath = None , VERBOSE=True):
    """
    Convert direct-output orbfit elements dictionary to standard format for external consumption
    
    inputs:
    -------
    orbfit_input: dict or string
     - valid convertible orbfit output dictionary
     - requires multiple different sub-dictionaries, *NOT* just the eq0/eq1 file
    
    returns:
    --------
    standard_format_dict
     - mpc_orb.json compatible
    
    optionally:
    -----------
    if an output filepath is supplied, then the output-dictionary will also be saved to file
    
    """
    if VERBOSE: 
      print(f"Running {__file__}.construct(...)", flush=True)

    try :
        
        # Get the template dict/json
        mpcorb_template = template.get_template_json()
   
        # DEVELOPING: Check that the template is itself valid
        # assert mpc_orb.validate_mpcorb.validate_mpcorb(mpcorb_template)

 
        # Populate the template from the orbfit_input
        # - This is the heart of the routine
        try:
          mpcorb_populated = populate(eq0dict,eq1dict,rwodict,moidsdict,otherdict , mpcorb_template)
        except Exception as e : 
          print(f'Exception in *populate*: \n {e}')
        
        # Check the result is valid and return
        assert mpc_orb.validate_mpcorb.validate_mpcorb(mpcorb_populated) 

        if VERBOSE:
          print(f"Completed {__file__}.construct(...)", flush=True)
        return mpcorb_populated 
 
    except Exception as e :
        print('Exception in ', __file__, '\n', e)
        return {}
        

# -------------------------------------------------------------------
# Function to populate mpcorb_dict from orbfit_dict(s)
# -------------------------------------------------------------------
def populate(eq0dict,eq1dict,rwodict,moidsdict,otherdict , mpcorb_template):
    """
    Function to populate mpcorb_dict from orbfit_dict(s)
    Replaces *std_format_els* function
    
    inputs:
    -------
    orbfit_dict: dict-of-dicts
        - Expected Structure of inpiut orbfit data
            'eq0dict'
            'eq1dict'
            'rwodict'
            'orbit_quality_metrics'
            'bad_trk_dict'
            'ele220_str'
            'moids_dict'
            'mpc_orb_dict' <<-- Expect empty when passed in here !!!
            'stats_dict'
            
    mpcorb_template: dict
        - Structure of mpcorb json that we need to populate
            'CAR'
            'COM'
            'software_data'
            'system_data'
            'designation_data'
            'orbit_fit_statistics'
            'non_grav_data'
            'magnitude_data'
            'epoch_data'
            'moid_data'
            'categorization'
    
    returns:
    --------
    """
    # Copy the structure and the default content
    mpcorb_populated = copy.deepcopy(mpcorb_template)

    # Recursively turn dict values into numbers (where possible)
    eq0dict= to_nums(eq0dict)
    eq1dict= to_nums(eq1dict)
    rwodict= to_nums(rwodict)
    moidsdict= to_nums(moidsdict)
    otherdict= to_nums(otherdict)


    # Populate best-fit orbit data (CAR & COM components)
    # - non-grav data is now populated within this call ...
    populate_CAR_COM( eq1dict, mpcorb_populated)

    # Populate software data
    populate_software_data(otherdict, mpcorb_populated)

    # Populate system data
    populate_system_data(otherdict, mpcorb_populated)

    # Populate designation_data
    # - categorization:object_type also done here
    populate_designation_data(rwodict, mpcorb_populated)

    # Populate orbit_fit_statistics
    populate_orbit_fit_statistics(eq0dict,eq1dict,rwodict,otherdict, mpcorb_populated)

    # Populate magnitude_data
    populate_magnitude_data(eq1dict , mpcorb_populated)

    # Populate epoch_data
    populate_epoch_data(eq1dict , mpcorb_populated)

    # Populate moid_data
    populate_moid_data(moidsdict, mpcorb_populated  )

    # Populate categorization
    populate_categorization(otherdict, mpcorb_populated  )

    return mpcorb_populated

# ------------------------------------
# Sub-Funcs to populate main sections
# of the mpcorb json
# ------------------------------------

def populate_CAR_COM( eq1dict, mpcorb_populated):
    '''
    # Populate best-fit orbit data (CAR & COM components)

    # NB, the template for mpcorb_pop should contain something like ...
        "coefficient_names" :        ["x","y","z","vx","vy","vz","yarkovski"],
        "coefficient_values":        [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        "coefficient_uncertainties": [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        "eigenvalues":               [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        "covariance": {

    '''
    # Loop over the "coordtype" dictionaries that are required to be present
    for coordtype in ["CAR","COM"]:#['CAR','COM']:
        if coordtype in eq1dict.keys() and eq1dict[coordtype]:

            # check that covariances are numbered correctly, and place into covariance sub-dictionary
            # (a) we expect to see numbering from cov00 ...
            if 'cov00' in eq1dict[coordtype].keys():
                covariance = {}
                cov_keys = [key for key in eq1dict[coordtype].keys() if key[:3]=='cov' and key[3:].isnumeric()]
                for key in cov_keys:
                    mpcorb_populated[coordtype]["covariance"][key] = eq1dict[coordtype][key]
            
            # (b) older versions have different numbering (see cov10 in *std_format_els*)
            # - *** Not dealing with that for now ***
            

            # populate the coefficient_names & coefficient_values for the elements 
            populate_els(mpcorb_populated[coordtype], eq1dict[coordtype] , coordtype)

            # populate eigval & uncertainties (NB uncertainties split elements -vs- non-gravs) 
            mpcorb_populated[coordtype]["eigenvalues"] = eq1dict[coordtype]["eigval"]
            mpcorb_populated[coordtype]["coefficient_uncertainties"] = eq1dict[coordtype]["rms"]
            #mpcorb_populated[coordtype]["non_grav_uncertainty"] = eq1dict[coordtype]["rms"][6:]
            #mpcorb_populated[coordtype][] = eq1dict[coordtype]["element_order"]

    # populate non-grav components 
    populate_nongravs(mpcorb_populated , eq1dict) 

def populate_els(mpcorb_element_dict, orbfit_component_dict , coordtype):
    """
    Rename elements to be human-readable
    N.B. This is for a single coordtype (i.e. CAR *or* COM)

    """
    # Here we create a list of the element names that are used in orbfit_component_dict
    orbfit_element_names = [ "element" + str(_) for _ in range(6)]

    # Some of the old dicts from the db may not have the 'element_order' variable ... 
    if 'element_order' not in orbfit_component_dict:
      if coordtype == 'CAR':
        orbfit_component_dict['element_order'] = ['x','y','z','vx','vy','vz']
      if coordtype == 'COM':
        orbfit_component_dict['element_order'] = ['q','e','i','node','argperi','peri_time']


    # Here we extract the human-readable element names
    mpcorb_element_dict["coefficient_names"] = orbfit_component_dict['element_order'] 
    mpcorb_element_dict["coefficient_values"]= [ orbfit_component_dict[_] for _ in orbfit_element_names]



def populate_nongravs( mpcorb_populated , eq1dict ):
    """
    Function to populate nongrav data in the appropriate sections of the mpcorb_populated dict
    """
    # Loop over the "coordtype" dictionaries that are required to be present
    for coordtype in ['CAR','COM']:
        if coordtype in eq1dict.keys() and eq1dict[coordtype]:
            d = eq1dict[coordtype]
   
            # try to instantiate an empty dict ... MJP-2023:01:25
            mpcorb_populated[coordtype]['non_grav_uncertainty'] = {} 
        
            # Do we have any non-gravs ?
            if d["numparams"] == 6 and d["nongrav_model"] == 0:
                mpcorb_populated["non_grav_booleans"]["non_gravs"] = False
            elif d["numparams"] > 6 and d["nongrav_model"] > 0:
                mpcorb_populated["non_grav_booleans"]["non_gravs"] = True
            else:
                raise Exception("Unexpected combination of nongrav parameters...")

            # If we have non-gravs, then change various parameters
            #   in the default-dict, according to the values in the input dict
            #
            # Example non-grav params from Margaret's json ...
            #
            #"numparams": "7",        <<-- Total number of variational parameters
            #                               ( 6 for the state, plus 0-4 for the non-gravs)
            #"nongrav_model": "1",    <<--  1 => Asteroidal or Cometary:Marsden,
            #                               2=> Cometary: YC,
            #                               3=> Cometary: Yabushita
            #"nongrav_params": "2",   <<-- Maximum number of non-grav params allowed in this model
            #"nongrav_type": ["2"],   <<-- List of the coefficients that are used
            #"nongrav_vals": [
            #    "0.00000000000000E+00",
            #    "-2.84420523316711E-03"
            #],
            #
            # We only need to do any work if there are non-gravs
            # (the default/template is correct for standard integrations which lack non-gravs)
            if mpcorb_populated["non_grav_booleans"]["non_gravs"]:
                
                # Asteroidal ...
                if   d["nongrav_model"] == 1 and d["nongrav_params"] == 2:
                
                    # Solar Radn Pressure
                    if  1 in d["nongrav_type"] and d["numparams"] in [7,8]:
                        mpcorb_populated['non_grav_booleans']['non_grav_model']['srp']   = True
                        mpcorb_populated['non_grav_booleans']['non_grav_coefficients']['srp']   = True

                        mpcorb_populated[coordtype]['coefficient_names']  += ['srp']
                        mpcorb_populated[coordtype]['coefficient_values'] += [d["nongrav_vals"][0]]
                        #mpcorb_populated[coordtype]['non_grav_uncertainty']['srp_coeff']    = d["rms"][6] 

                    # Yarkovski
                    if 2 in d["nongrav_type"] and d["numparams"] in [7,8]:
                        mpcorb_populated['non_grav_booleans']['non_grav_model']['yarkovski'] = True
                        mpcorb_populated['non_grav_booleans']['non_grav_coefficients']['yarkovski'] = True

                        mpcorb_populated[coordtype]['coefficient_names']  += ['yarkovski']
                        mpcorb_populated[coordtype]['coefficient_values'] += [d["nongrav_vals"][1]]
                        #mpcorb_populated[coordtype]['non_grav_uncertainty']['yarkovski_coeff'] = d["rms"][6] if d["numparams"] == 7 else d["rms"][7]

                    # Error
                    if d["numparams"] not in [7,8] or d["nongrav_type"] not in [[1],[2],[1,2]]:
                        print(f'd["numparams"]={d["numparams"]} , d["nongrav_type"]={d["nongrav_type"]}')
                        raise Exception

                # Cometary ...
                elif   d["nongrav_model"] in [1,2,3]  and d["nongrav_params"] in [3,4]:
                    
                    # Marsden
                    if d["nongrav_model"] == 1:
                        mpcorb_populated['non_grav_booleans']['non_grav_model']['marsden'] = True

                    # Yeomans and Chodas
                    elif d["nongrav_model"] == 2:
                        mpcorb_populated['non_grav_booleans']['non_grav_model']['yc'] = True

                    # Yabushita
                    elif d["nongrav_model"] == 3:
                        mpcorb_populated['non_grav_booleans']['non_grav_model']['yabushita'] = True

                    # Error
                    else:
                        raise Exception
                        
                    
                    # Parameters
                    orbfit_signatures_to_mpcorb_names =  {
                        [1,2]       : ["A1","A2"],
                        [1,2,3]     : ["A1","A2","A3"],
                        [1,2,3,4]   : ["A1","A2","A3","DT"] }
                    assert d["nongrav_type"] in orbfit_signatures_to_mpcorb_names
                    for k,v in orbfit_signatures_to_mpcorb_names.items() :
                        if k in d["nongrav_type"]:
                            for i,orbfit_sig in enumerate(k):
                                # Extract the desired names
                                # bool_name = v[i]
                                coeff_name= v[i] # +'_coeff'
                                # Set bool
                                mpcorb_populated	['non_grav_booleans']["non_grav_coefficients"][coeff_name] = True
                                # Set coeff
                                mpcorb_populated[coordtype]['coefficient_names']  += [coeff_name]
                                mpcorb_populated[coordtype]['coefficient_values'] += [d["nongrav_vals"][i]]
                                #mpcorb_populated[coordtype]['non_grav_uncertainty'][coeff_name] = d["rms"][6 + i]
                # Error
                else:
                    raise Exception

    return True
    
    
def populate_software_data(orbfit_other_dict, mpcorb_populated):
    '''
    # Populate software data

    "software_data": {
                "fitting_software_name",
                "fitting_software_version",
                "fitting_datetime",
                "mpcorb_version",
                "mpcorb_creation_datetime"
    },

    '''

    mpcorb_populated["software_data"]["fitting_datetime"]         = orbfit_other_dict["orbfit_run_datetime"]
    mpcorb_populated["software_data"]["mpcorb_creation_datetime"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S") 

def populate_system_data(orbfit_other_dict, mpcorb_populated  ):
    '''
    # Populate system data
    '''
    pass
    


def populate_designation_data( rwodict, mpcorb_populated):
    '''
    # Populate designation_data & categorization data  
    '''
    nominal_label = str(rwodict["optical_list"][0]["name"])

    # Query the designation-tables using Nora's designation-identifier service
    # NB: I don't like having to hardpaste all the connection details
    # - I'd prefer to use some default connection func/class: https://github.com/Smithsonian/mpc-software/issues/28
    with DatabaseClient.PostgresClient(host='localhost', port='5432', database='vmsops', user='postgres') as db:
      result = identifier.get_ids( nominal_label, db, verbose=True, use_materialized_view=False)
    
    if result['status'] == 'Found':
      mpcorb_populated['designation_data'].update( result['results'] ) # N.B. We extract the inner dictionary of designations


    # Store the category information 
    if "object_type" in mpcorb_populated['designation_data']:
      mpcorb_populated['categorization']["object_type_int"] = mpcorb_populated['designation_data']["object_type"]["integer"]
      mpcorb_populated['categorization']["object_type_str"] = mpcorb_populated['designation_data']["object_type"]["key"]
      del(mpcorb_populated['designation_data']["object_type"])




def compute_and_populate_orbit_quality_metrics(eq0dict , mpcorb_populated):
    ''' COMPUTE ORBIT QUALITY METRICS
     - Taken from "create_output_dictionaries..." by FS
    # Compute orbit quality metrics from the eq0 file
    # We need to compute the SNR of the orbital elements
    # in 'CARtesian' coordinates
    # and check whether those values are in predefinite ranges
    # Usage:
    #  snr, snr_below_1, snr_below_3 = compute_orbit_quality_metrics(eq0dict)
    # eq0dict = dictionary created from the eq0file
    # Get RMS & then calc SNR
    '''

    car_rms = [float(x) for x in eq0dict['CAR']['rms']]
    car_els = [float(eq0dict['CAR'][x]) for x in ['element0','element1','element2','element3','element4','element5']]
    car_sn = [abs(car_els[ind])/car_rms[ind] for ind in range(6)]
    sig_to_noise_ratio = car_sn
    if any([x<3 for x in car_sn]):
        snr_below_3 = True
        if any([x<1 for x in car_sn]):
               snr_below_1 = True
        else:
            snr_below_1 = False
    else:
        snr_below_3 = False
        snr_below_1 = False

    #Orbit quality metrics dictionary
    mpcorb_populated['orbit_fit_statistics']['sig_to_noise_ratio'] = sig_to_noise_ratio
    mpcorb_populated['orbit_fit_statistics']['snr_below_3'] = snr_below_3
    mpcorb_populated['orbit_fit_statistics']['snr_below_1'] = snr_below_1

    #SNR values to define the orbit quality
    # good if   SNR>3
    # poor if 1<SNR<3
    # unreliable if SNR<1
    if snr_below_1:
        orbit_quality = 'unreliable'
    elif snr_below_3:
        orbit_quality = 'poor'
    else:
        orbit_quality = 'good'

    mpcorb_populated['orbit_fit_statistics']['orbit_quality'] = orbit_quality



def get_and_populate_obs_number(rwodict , mpcorb_populated):
    ''' Counts the number of obs (of various types) used in the orbit
    Taken from *get_obs_number* in "create_output_dictionaries..." by FS
    '''
    mpcorb_populated['orbit_fit_statistics']['nobs_optical'] = len( rwodict['optical_list'] )
    mpcorb_populated['orbit_fit_statistics']['nobs_optical_sel'] = len( [x for x in rwodict['optical_list'] if 'a_select' in x.keys() and x['a_select'] != '0'] )

    mpcorb_populated['orbit_fit_statistics']['nobs_radar'] = len(rwodict['radar_list'])
    mpcorb_populated['orbit_fit_statistics']['nobs_radar_sel'] = len( [x for x in rwodict['radar_list'] if 'a_select' in x.keys() and x['a_select'] != '0' ] )

    mpcorb_populated['orbit_fit_statistics']['nobs_total'] = mpcorb_populated['orbit_fit_statistics']['nobs_optical'] + mpcorb_populated['orbit_fit_statistics']['nobs_radar']
    mpcorb_populated['orbit_fit_statistics']['nobs_total_sel'] = mpcorb_populated['orbit_fit_statistics']['nobs_optical_sel'] + mpcorb_populated['orbit_fit_statistics']['nobs_radar_sel']



def compute_and_populate_arc_lengths(rwodict , mpcorb_populated):
    ''' compute the arc length from the rwo dict 
        Taken from *compute_arc_lengths* in "create_output_dictionaries..." by FS
    ''' 
    
    #List of observations from rwodict
    obslist     = [obs for obs in rwodict['optical_list'] if obs['T'] != 'X']
    obslist_sel = [obs for obs in rwodict['optical_list'] if obs['T'] != 'X' if 'a_select' in obs.keys() and obs['a_select'] != '0' ]

    #ALL OBS: Initial and final time
    timebegin = [int(obslist[0]['year']),int(obslist[0]['month']),float(obslist[0]['day'])]
    timeend = [int(obslist[-1]['year']),int(obslist[-1]['month']),float(obslist[-1]['day'])]
    time_diff = round(ma.to_julian_date(timeend[0],timeend[1],timeend[2])-ma.to_julian_date(timebegin[0],timebegin[1],timebegin[2]))
    if time_diff < 365.25:
        arc_length = str(time_diff)+' days'
    else:
        arc_length = str(timebegin[0])+'-'+str(timeend[0]) # MJP <<-- 

    #SELECTED OBS: Initial and final time
    timebegin = [int(obslist_sel[0]['year']),int(obslist_sel[0]['month']),float(obslist_sel[0]['day'])]
    timeend = [int(obslist_sel[-1]['year']),int(obslist_sel[-1]['month']),float(obslist_sel[-1]['day'])]
    time_diff = round(ma.to_julian_date(timeend[0],timeend[1],timeend[2])-ma.to_julian_date(timebegin[0],timebegin[1],timebegin[2]))
    if time_diff < 365.25:
        arc_length_sel = str(time_diff)+' days'
    else:
        arc_length_sel = str(timebegin[0])+'-'+str(timeend[0]) # MJP <<-- 

    # Populate the dictionary ...
    mpcorb_populated['orbit_fit_statistics']['arc_length_total'] =  arc_length 
    mpcorb_populated['orbit_fit_statistics']['arc_length_sel'] = arc_length_sel 





def populate_orbit_fit_statistics(eq0dict,eq1dict,rwodict,otherdict, mpcorb_populated):
    '''
    # Populate orbit_fit_statistics
    Much of this taken from *define_fit_succ_from_dictionaries* in "create_output_dictionaries..." by FS 


    '''

    '''
    # Extract from orbit_quality_metrics ...
    for key in ['sig_to_noise_ratio',
                'snr_below_3',
                'snr_below_1',
                #'U_param',
                #'score1',
                #'score2'
                ]:
        mpcorb_populated['orbit_fit_statistics'][key] = orbfit_dict['orbit_quality_metrics'][key]
    '''

    # --------- Define whether fit was successful ----------------
    # ------------------------------------------------------------
    # Default: Unsuccessful...
    fit_success = False
    no_orbit    = True

    # Orbit-extension ...
    if otherdict['orbfit_computation_type'] in ['EXTENSION']: # <<-- I.e. orbit-extension
      # Here we are saying that if these three dicts exists and have certain critical fields populated, then we have a successful run:
      if eq0dict and eq1dict and rwodict and \
         'CAR' in eq0dict and 'COM' in eq0dict and \
         'CAR' in eq1dict and 'COM' in eq1dict and \
         'rmsast' in rwodict and rwodict['rmsast'] != '0' :
        fit_success = True
        no_orbit = False

    # IOD 
    # *** NEED TO COME BACK TO THIS AND DECIDE HOW TO DO THE CHECKS FOR MCMCM IN THE CASE OF A NO-ORBIT NEOCP RUN *** 
    if otherdict['orbfit_computation_type'] in ['IOD']:
      pass

    # COMET 
    elif otherdict['orbfit_computation_type'] == 'comet':
      pass

    # fucked-up 
    else:
      pass

    if no_orbit:
      mpcorb_populated['orbit_fit_statistics']['orbit_quality'] = 'no_orbit'


    # --------- Calculate additional top-line stats --------------
    # ------------------------------------------------------------
    if 'fit_success':

        #Orbit quality metrics and orbit quality definition
        # - Populates "sig_to_noise_ratio", "snr_below_3", "snr_below_1", & "orbit_quality" in mpcorb_populated['orbit_fit_statistics']... 
        compute_and_populate_orbit_quality_metrics(eq0dict , mpcorb_populated )

        #Total number of observations, number of observations selected, normalized RMS
        # - Populates 'nobs_total', 'nobs_total_sel', 'nobs_optical', 'nobs_optical_sel', 'nobs_radar' & 'nobs_radar_sel' in mpcorb_populated['orbit_fit_statistics']
        get_and_populate_obs_number( rwodict ,mpcorb_populated )

        # Topline RMS 
        mpcorb_populated['orbit_fit_statistics']['normalized_RMS']     = copy.deepcopy(rwodict['rmsast'])
        mpcorb_populated['orbit_fit_statistics']['not_normalized_RMS'] = None ##<<-- ***NEEDS TO BE CORRECTED TO GET Non-Normalised RMS *** 

        # Number of oppositions 
        mpcorb_populated['orbit_fit_statistics']['nopp']     = otherdict['nopp']

        #Arc length
        compute_and_populate_arc_lengths(rwodict , mpcorb_populated)

        #Bad tracklet identification
        # MJP: 2023-03: Turning this stuff off, as I assume it must have been calculated earlier if an MPC_ORB_JSON is being calculated
        #               (i.e. I assume we only make the mpcorb.json if the orbit is good enough ...)
        #if "bad_trk_dict" not in data_dict: data_dict["bad_trk_dict"] = {}
        #data_dict["stats_dict"]['bad_trk'], data_dict['bad_trk_dict']['bad_trk_list_ids'], data_dict['bad_trk_dict']['bad_trk_list_obs80'] = identify_bad_tracklets(data_dict)
        #data_dict['bad_trk_dict']['bad_trk_params'] = data_dict['otherdict']['badtrk_params']

        #We change the definition of success if nobs_sel < nobs_tot/2
        if mpcorb_populated['orbit_fit_statistics']['nobs_total_sel'] < mpcorb_populated['orbit_fit_statistics']['nobs_total']/2:# and data_dict["stats_dict"]['bad_trk']:
            fit_success = False
            mpcorb_populated['orbit_fit_statistics']['orbit_quality'] = 'no_orbit'



    
    # Extract from elsewhere ...
    mpcorb_populated['orbit_fit_statistics']['numparams'] = eq1dict['CAR']['numparams']



def populate_magnitude_data(eq1dict , mpcorb_populated ):
    '''
    # Populate magnitude_data
    '''
    # NB: Data is replicated in "COM" & "CAR" : Just extract once
    mpcorb_populated["magnitude_data"]["H"] = eq1dict["CAR"]["h"]
    mpcorb_populated["magnitude_data"]["G"] = eq1dict["CAR"]["g"]

def populate_epoch_data(eq1dict , mpcorb_populated ):
    '''
    # Populate epoch_data
    '''
    # NB: Data is replicated in "COM" & "CAR" : Just extract once
    mpcorb_populated["epoch_data"]["timesystem"]    = eq1dict["CAR"]["timesystem"]
    mpcorb_populated["epoch_data"]["timeform"]      = "MJD" # eq1dict["CAR"]["MJD"]
    mpcorb_populated["epoch_data"]["epoch"]         = eq1dict["CAR"]["epoch"]


def populate_moid_data(moidsdict, mpcorb_populated  ):
    '''
    # Populate moid_data

    "moid_data": {
        "Venus": null,
        "Earth": null,
        "Mars": null,
        "Jupiter": null,
        "moid_units": "au"
    },

    '''
    for key,value in moidsdict.items():
      if key in mpcorb_populated["moid_data"]:
        mpcorb_populated["moid_data"][key] = value

def populate_categorization(orbfit_other_dict, mpcorb_populated  ):
    '''
    # Populate categorization
    
    '''
    pass



# ------------------------------------
# Funcs to convert strings-to-numbers
# ------------------------------------

def to_nums(v):
    """
        Recursive function to descend through dicts, lists & tuples and
        transform any numbers from string to int/float
        (by M. Payne)
    """
    if  isinstance(v, dict):
        return {k:to_nums(_) for k,_ in v.items() }
    elif isinstance(v, list):
        return [to_nums(_) for _ in v]
    elif isinstance(v, tuple):
        return (to_nums(_) for _ in v)
    elif isinstance(v, str):
        return attempt_str_conversion(v)
    elif isinstance(v, (int, float, type(None))):
        return v
    else:
        raise Exception(f"Unexpected type of variable in *to_nums* : {type(v)} : {v}")
        return v

def attempt_str_conversion(s):
    """
    Convert strings to numbers where possible
    """
    
    assert isinstance(s,str)
    try:
        f = float(s)
    except:
        # If we are here, then s is non-numeric
        return s
    
    # If we are here, then s is numeric, but we might have 's' ~ '1.0' or ~'1'
    try:
        # Using int's "feature" of barfing when presented with a float-string
        i = int(s)
        return i
    except:
        return f
        






