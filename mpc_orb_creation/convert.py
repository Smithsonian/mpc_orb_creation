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

# Third party imports
# -----------------------
import copy
import json
import sys, os

# MPC module imports
# -----------------------
try:
    import get_ids as ids
    import mpc_convert as mc
    import mpcdev_psql as mpc_psql
    
    sys.path.append('/sa/orbit_utils')
    import orbfit_to_dict as o2d
except:
    raise Exception("This conversion routine is intended for internal MPC usage and requires modules that are likely to only be available on internal MPC machines")

# local imports
# -----------------------
from .  import interpret
from .schema import validate_orbfit_conversion, validate_mpcorb , validate_orbfit_construction
from .  import template

# -------------------------------------------------------------------
# Main code to run conversion/construction from orbfit-to-mpc_orb
# -------------------------------------------------------------------

def construct(orbfit_input , output_filepath = None ):
    """
    Convert direct-output orbfit elements dictionary to standard format for external consumption
    
    inputs:
    -------
    orbfit_input: dict
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
    
    try:
        # Test whether supplied input is a valid example of single, large orbfit-results dictionary containing a large variety of sub-dictionaries.
        assert validate_orbfit_result(orbfit_dict):

        # Get the template dict/json
        mpcorb_template = template.get_template_json()
    
        # Populate the template from the orbfit_input
        # - This is the heart of the routine
        mpcorb_populated = populate(orbfit_dict, mpcorb_template)
        
        # Check the result is valid
        return validate_mpcorb(mpcorb_populated)
        
    except Exception as e :
        return False
        

# -------------------------------------------------------------------
# Function to populate mpcorb_dict from orbfit_dict(s)
# -------------------------------------------------------------------
def populate(orbfit_dict, mpcorb_template):
    """
    Function to populate mpcorb_dict from orbfit_dict(s)
    Replaces *std_format_els* function
    
    inputs:
    -------
    orbfit_dict: dict-of-dicts
        - Expected Structure of input orbfit data
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
    orbfit_dict = to_nums(orbfit_dict)

    # Populate best-fit orbit data (CAR & COM components)
    populate_CAR_COM(orbfit_dict['eq1dict'], mpcorb_populated)
    
    # Populate non-grav data
    populate_nongravs(orbfit_dict['eq1dict'], mpcorb_populated)

    # Populate software data
    populate_software_data(orbfit_dict, mpcorb_populated)

    # Populate system data
    populate_system_data(orbfit_dict, mpcorb_populated)

    # Populate designation_data
    populate_designation_data(orbfit_dict, mpcorb_populated)

    # Populate orbit_fit_statistics
    populate_orbit_fit_statistics()

    # Populate magnitude_data
    populate_magnitude_data(orbfit_dict['eq1dict'] , mpcorb_populated)

    # Populate epoch_data
    populate_epoch_data(orbfit_dict['eq1dict'] , mpcorb_populated)

    # Populate moid_data
    populate_moid_data(orbfit_dict, mpcorb_populated  )

    # Populate categorization
    populate_categorization(orbfit_dict, mpcorb_populated  )



# ------------------------------------
# Sub-Funcs to populate main sections
# of the mpcorb json
# ------------------------------------

def populate_CAR_COM( eq1dict, mpcorb_populated):
    '''
    # Populate best-fit orbit data (CAR & COM components)
    '''
    # Loop over the "coordtype" dictionaries that are required to be present
    for coordtype in ['CAR','COM']:
        if coordtype in eq1dict.keys() and eq1dict[coordtype]:

            # check that covariances are numbered correctly, and place into covariance sub-dictionary
            # (a) we expect to see numbering from cov00 ...
            if 'cov00' in eq1dict[coordtype].keys():
                covariance = {}
                cov_keys = [key for key in eq1dict.keys() if key[:3]=='cov' and key[3:].isnumeric()]
                for key in cov_keys:
                    mpcorb_populated[coordtype]["covariance"][key] = eq1dict[key]
                    
            # (b) older versions have different numbering (see cov10 in *std_format_els*)
            # - *** Not dealing with that for now ***
            

            # rename elements according to coordtype
            populate_els(mpcorb_populated[coordtype]["elements"], eq1dict[coordtype], coordtype)
                
            
def populate_els(mpcorb_element_dict, orbfit_component_dict, coordtype):
    """
    Rename elements to be human-readable
    """
    orbfit_element_names = [ "element" + str(_) for _ in range(6)]
    
    if coordtype == 'CAR':
        elslist = ['x','y','z','vx','vy','vz']
    elif coordtype == 'COM':
        elslist = ['q','e','i','node','argperi','peri_time']
    else:
        print('rename_els : '+coordtype+' : unknown coordtype?')
        elslist = []

    if elslist:
        for orbfit_element_name, mpcorb_name in zip(orbfit_element_names, elslist ):
            mpcorb_element_dict[mpcorb_name] = orbfit_component_dict[orbfit_element_name]

def populate_nongravs( eq1dict , mpcorb_populated ):
    """
    Function to populate nongrav data in the appropriate sections of the mpcorb_populated dict
    """

    # Loop over the "coordtype" dictionaries that are required to be present
    for coordtype in ['CAR','COM']:
        if coordtype in eq1dict.keys() and eq1dict[coordtype]:
            d = eq1dict[coordtype]
            
            # Do we have any non-gravs ?
            if d["numparams"] == 6 and d["nongrav_model"] == 0:
                mpcorb_populated['non_grav_data']['non_gravs'] = False
            elif d["numparams"] > 6 and d["nongrav_model"] > 0:
                mpcorb_populated['non_grav_data']['non_gravs'] = True
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
            if mpcorb_populated['non_grav_data']['non_gravs']:
                
                # Asteroidal ...
                if   d["nongrav_model"] == 1 and d["nongrav_params"] == 2:
                
                    # Solar Radn Pressure
                    if  1 in d["nongrav_type"] and d["numparams"] in [7,8]:
                        mpcorb_populated['non_grav_data']['non_grav_booleans']['srp']   = True
                        mpcorb_populated[coordtype]['non_grav_coefficients']['srp_coeff']   = d["nongrav_vals"][0]

                    # Yarkovski
                    if 2 in d["nongrav_type"] and d["numparams"] in [7,8]:
                        mpcorb_populated['non_grav_data']['non_grav_booleans']['yarkovski'] = True
                        mpcorb_populated[coordtype]['non_grav_coefficients']['yarkovski_coeff'] = d["nongrav_vals"][1]

                    # Error
                    if d["numparams"] not in [7,8] or d["nongrav_type"] not in [[1],[2],[1,2]]:
                        print(f'd["numparams"]={d["numparams"]} , d["nongrav_type"]={d["nongrav_type"]}')
                        raise Exception

                # Cometary ...
                elif   d["nongrav_model"] in [1,2,3]  and d["nongrav_params"] in [3,4]:
                    
                    # Marsden
                    if d["nongrav_model"] == 1:
                        mpcorb_populated['non_grav_data']['non_grav_booleans']['marsden'] = True

                    # Yeomans and Chodas
                    elif d["nongrav_model"] == 2:
                        mpcorb_populated['non_grav_data']['non_grav_booleans']['yc'] = True

                    # Yabushita
                    elif d["nongrav_model"] == 3:
                        mpcorb_populated['non_grav_data']['non_grav_booleans']['yabushita'] = True

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
                                bool_name = v[i]
                                coeff_name= v[i]+'_coeff'
                                # Set bool
                                mpcorb_populated['non_grav_data']['non_grav_booleans'][bool_name] = True
                                # Set coeff
                                mpcorb_populated[coordtype]['non_grav_coefficients'][coeff_name] = d["nongrav_vals"][i]
                
                # Error
                else:
                    raise Exception

    return True
    
    
def populate_software_data(orbfit_dict, mpcorb_populated):
    '''
    # Populate software data
    '''
    pass

def populate_system_data(orbfit_dict, mpcorb_populated  ):
    '''
    # Populate system data
    '''
    pass
    
def generate_system_dictionary(elsdict):
    """ put system data into a dictionary """
    # THE CHECKS WILL BECOME UNNECESSARY GIVEN VALIDATION
    return {    "eph"    : 'JPLDE431'   if not elsdict['eph']   else elsdict['eph'],
                "refsys" : 'ECLM J2000' if not elsdict['refsys'] else elsdict['refsys']}


def populate_designation_data(orbfit_dict, mpcorb_populated):
    '''
    # Populate designation_data
    *** Requires access to internal MPC routines / database ***
    '''
    if 'permid' in orbfit_dict['stats_dict'] and orbfit_dict['stats_dict']['permid']:
        orbfitdes = orbfit_dict['stats_dict']['permid']
    else:
        orbfitdes = orbfit_dict['stats_dict']['provid']

    mpcorb_populated['designation_data'] = to_names_dict( orbfitdes )

def populate_orbit_fit_statistics(orbfit_dict, mpcorb_populated):
    '''
    # Populate orbit_fit_statistics
    '''
    # Extract from orbit_quality_metrics ...
    for key in ['sig_to_noise_ratio',
                'snr_below_3',
                'snr_below_1',
                'U_param',
                'score1',
                'score2'
                ]:
        mpcorb_populated['orbit_fit_statistics'][key] = orbfit_dict['orbit_quality_metrics'][key]
        
    # Extract from stats_dict ...
    for key in ['orbit_quality',
                'normalized_RMS',
                'not_normalized_RMS',
                'nopp',
                'score1',
                'score2'
                ]:
        mpcorb_populated['orbit_fit_statistics'][key] = orbfit_dict['stats_dict'][key]

    # Extract from elsewhere ...
    mpcorb_populated['orbit_fit_statistics']['numparams'] = orbfit_dict['CAR']['numparams']

    # Quantities not yet populated ...
    '''
                "nobs_total"            : 0,
                "nobs_total_sel"        : 0,
                "nobs_optical"          : 0,
                "nobs_optical_sel"      : 0,
                "nobs_radar"            : 0,
                "nobs_radar_sel"        : 0,
                "arc_length_total"      : 0,
                "arc_length_sel"        : 0,
    '''
    


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
    mpcorb_populated["epoch_data"]["timeform"]      = eq1dict["CAR"]["MJD"]
    mpcorb_populated["epoch_data"]["epoch"]         = eq1dict["CAR"]["epoch"]


def populate_moid_data(orbfit_dict, mpcorb_populated  ):
    '''
    # Populate moid_data
    '''
    pass

def populate_categorization(orbfit_dict, mpcorb_populated  ):
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
    else:
        raise Exception(f"Unexpected type of variable in *to_nums* : {type(v)} ")
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
        

# ------------------------------------
# Designation Functions
# - Hopefully can be replaced by API-call
# ------------------------------------

def orbfitdes_to_packeddes(desig_up):
    """
    Convert orbfit name to packed desig for numbered objects and prov desigs only
    Requires access to internal MPC routines
    """

    if desig_up.isnumeric():
        desig = mc.unpacked_to_packed_desig('('+desig_up+')')
    elif desig_up[:4].isnumeric() and len(desig_up) > 4:
        desig = mc.unpacked_to_packed_desig(desig_up[:4]+' '+desig_up[4:])
    elif desig_up[0] in ['A','C','P']:
        if desig_up[0] == 'A' and desig_up[1:4].isnumeric() and not desig_up[4].isnumeric():
            desig = mc.unpacked_to_packed_desig(desig_up[:4]+' '+desig_up[4:])
        elif len(desig_up) > 5:
            desig = mc.unpacked_to_packed_desig(desig_up[0]+'/'+desig_up[1:5]+' '+desig_up[5:])
        else:
            desig = mc.unpacked_to_packed_desig(desig_up[0]+'/'+desig_up[1:])
    elif len(desig_up) < 5 and desig_up[-1] in ['P','I']:
        desig = '0'*(5-len(desig_up)) + desig_up[-1]
    else:
        desig = desig_up
    
    return desig


def to_names_dict(orbfitdes):

    """
    Convert orbfit name to provisional/permanent desig, store in dictionary
    *** Requires access to internal MPC routines / database ***
    """

    result = {}

    if isinstance(orbfitdes,int):

        # this is numbered object, get provid out of numbered_identifications
        result['permid'] = str(orbfitdes)
        sqlstr = f"SELECT packed_primary_provisional_designation,iau_name FROM numbered_identifications WHERE permid='{orbfitdes}'"
        try:
            desig,name = mpc_psql.psql_execute_query(sqlstr)[0]
            primdesig = ids.get_id_list(desig,all=True)[0]
            if not name:
                name = ''
        except:
            print(orbfitdes+' : not in numbered_identifications?')
            primdesig = ''
            name = ''
    else:

        # orbfitdes is a provisional desig, so
        # 1) check if this is the primary provisional desig
        # 2) check if this is numbered object
        desig = orbfitdes_to_packeddes(orbfitdes)
        try:
            primdesig = ids.get_id_list(desig)[0]
        except:
            print(orbfitdes+' : not in identifications table?')
            primdesig = desig
        try:
            sqlstr = f"SELECT permid,iau_name FROM numbered_identifications WHERE packed_primary_provisional_designation='{orbfitdes}';"
            permid,name = mpc_psql.psql_execute_query(sqlstr)[0]
            if not permid:
                permid = ''
            if not name:
                name = ''
        except:
            permid = ''
            name = ''
        result['permid'] = permid

    # create names dictionary
    result['packed_primary_provisional_designation'] = primdesig
    if mc.packed_to_unpacked_desig(primdesig):
        result['unpacked_primary_provisional_designation'] = mc.packed_to_unpacked_desig(primdesig)
    else:
        result['unpacked_primary_provisional_designation'] = desig
    result['orbfit_name'] = orbfitdes
    result['iau_name'] = name

    return result
    





# ------------------------------------
# Archaic Functions
# ------------------------------------
'''
def save_to_file(standard_format_dict , output_filepath):
    """ """
    with open(output_filepath, 'w') as f:
        json.dump(standard_format_dict, f, indent=4)

'''

'''
def renumber_cov(covdict,numparams):
    """
    Renumber covariances to have index ij for covariance between element i and element j
    """
    
    indexlist = get_indexlist(numparams)

    newcovdict = {}
    for ind in range(len(indexlist)):
        try:
            newcovdict['cov'+indexlist[ind]] = covdict['cov'+'{:02d}'.format(ind)]
        except:
            print('renumber_cov : missing covariance entry cov'+'{:02d}'.format(ind))

    return newcovdict
'''

'''
def get_indexlist(numparams):
    """
    Compute indexes ij for covariance entries sigma_ij when extracting them from orbfit's compressed format
    """
    
    indexes = []
    if numparams >=6:
            for ii in range(numparams):
                for jj in range(ii,numparams):
                    indexes.append(str(ii)+str(jj))
    else:
        print("get_indexlist : can't deal with this value of numparams ("+numparams+')')

    return indexes
'''


def std_format_els(oldelsdict):
    """
    Convert direct-output orbfit elements dictionary to standard format for external consumption
    """
    
    elsdict = copy.deepcopy(oldelsdict)
    
    # THESE LINES WILL BECOME UNNECESSARY GIVEN VALIDATION
    if not elsdict['name']:
        print("missing object name, can't convert")
    elif 'CAR' not in elsdict.keys() or 'COM' not in elsdict.keys():
        print("missing Cartesian and/or cometary elements, can't convert")
    else:
        
        elsdict = to_nums(elsdict)

        # delete unneeded global info
        del elsdict['rectype']
        del elsdict['format']
           
        # Construct a "System data" dictionary
        elsdict["system_data"] = generate_system_dictionary(elsdict)
        for key in ['resys','eph']:
            if key in elsdict.keys(): del elsdict[key]

        # Construct names dictionary
        elsdict['designation_data'] = to_names_dict(elsdict['name'])
        del elsdict['name']
        
        # Loop over the "coordtype" dictionaries that may be present
        for coordtype in ['EQU','KEP','CAR','COM','COT']:

            if coordtype in elsdict.keys() and elsdict[coordtype]:
                thiscoorddict = copy.deepcopy(elsdict[coordtype])

                # delete unneeded info
                del thiscoorddict['coordtype']
                if 'nor00' in thiscoorddict.keys():
                    nor_keys = [key for key in thiscoorddict.keys() if key[:3]=='nor' and key[3:].isnumeric()]
                    for key in nor_keys:
                        del thiscoorddict[key]
                if 'wea' in thiscoorddict.keys():
                    del thiscoorddict['wea']

                # check that covariances are numbered correctly, and place into covariance sub-dictionary
                if 'cov00' in thiscoorddict.keys():
                    covariance = {}
                    cov_keys = [key for key in thiscoorddict.keys() if key[:3]=='cov' and key[3:].isnumeric()]
                    for key in cov_keys:
                        covariance[key] = thiscoorddict[key]
                        del thiscoorddict[key]
                    thiscoorddict['covariance'] = covariance
                if 'cov10' in thiscoorddict['covariance'].keys():
                    thiscoorddict['covariance'] = renumber_cov(thiscoorddict['covariance'],int(thiscoorddict['numparams']))

                # rename elements according to coordtype
                thiscoorddict = rename_els(thiscoorddict,coordtype)
                    
                # convert nongrav info to human-readable format,
                # and move the non-grav info to the top level
                # (NB If multiple coordtypes, then this top-level will be overwritten. SHouldn't matter)
                elsdict['nongrav_data'] = translate_nongravs(thiscoorddict)
                for key in ['nongrav_type','nongrav_params','nongrav_model','nongrav_vals']:
                    if key in thiscoorddict.keys(): del thiscoorddict[key]
                
                # move the magnitude info to the toplevel
                # (NB If multiple coordtypes, then this top-level will be overwritten. SHouldn't matter)
                elsdict['magnitude_data'] = generate_magnitude_dictionary(thiscoorddict)
                for key in ['g','h']:
                    if key in thiscoorddict.keys(): del thiscoorddict[key]

                # move the eopch info to the top level
                # (NB If multiple coordtypes, then this top-level will be overwritten. SHouldn't matter)
                elsdict['epoch_data'] = generate_epoch_dictionary(thiscoorddict)
                for key in ['timesystem','epoch']:
                    if key in thiscoorddict.keys(): del thiscoorddict[key]

                
                # over-write the coordtype dict at the top level
                elsdict[coordtype] = thiscoorddict
        
    return elsdict
        
'''
def convert(orbfit_input , output_filepath = None ):
    """
    Convert direct-output orbfit elements dictionary to standard format for external consumption
    
    *** --------------------------------------------
    *** THIS IS THE ORIGINAL VERSION
    *** PURE "CONVERSION" FROM eq0-to-mpc_orb.json
    *** WILL BE REPLACED BY "CONSTRUCTION" ABOVE
    *** --------------------------------------------

    
    inputs:
    -------
    orbfit_input: dict or filepath
     - valid convertible orbfit felfile dict/file
    
    returns:
    --------
    standard_format_dict
     - mpc_orb.json compatible
    
    optionally:
    -----------
    if an output filepath is supplied, then the output-dictionary will also be saved to file
    
    """

    # interpret the input (allow dict or filepath)
    orbfit_dict, input_filepath = interpret.interpret(orbfit_input)

    # check the input is valid
    if not validate_orbfit_conversion(orbfit_dict):
        return False

    # do the conversion (this is the heart of the routine)
    try:
        standard_format_dict = std_format_els(orbfit_dict)
    except:
        return False
        
    # check the result is valid
    if not validate_mpcorb(standard_format_dict):
        return False
        
    # save to file (if required)
    if input_filepath is not None or output_filepath is not None:
        input_stem = input_filepath[:input_filepath.rfind(".json")]
        output_filepath = output_filepath if output_filepath is not None else os.path.join(input_stem,"_mpcorb_",".json")
        save_to_file(standard_format_dict , output_filepath)

    return standard_format_dict
'''
