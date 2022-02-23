"""
mpc_orb_creation/convert.py
 - The functions that are required to convert orbfit fel-files (in json format) to an mpc_orb.json
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
from .schema import validate_orbfit_conversion, validate_mpcorb

# Main code to run routine
# -----------------------
def convert(orbfit_input , output_filepath = None ):
    """
    Convert direct-output orbfit elements dictionary to standard format for external consumption
    
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
    Requires access to internal MPC routines / database
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


def rename_els(coorddict,coordtype):
    """
    Rename elements to be human-readable
    """
    
    if coordtype == 'EQU':
        elslist = ['a','e_sin_argperi','e_cos_argperi','tan_i/2_sin_node','tan_i/2_cos_node','mean_long']
    elif coordtype == 'KEP':
        elslist = ['a','e','i','node','argperi','mean_anomaly']
    elif coordtype == 'CAR':
        elslist = ['x','y','z','vx','vy','vz']
    elif coordtype == 'COM':
        elslist = ['q','e','i','node','argperi','peri_time']
    elif coordtype == 'COT':
        elslist = ['q','e','i','node','argperi','true_anomaly']
    else:
        print('rename_els : '+coordtype+' : unknown coordtype?')
        elslist = []

    if elslist:
        elements = {}
        for ind in range(6):
            elements[elslist[ind]] = coorddict['element'+str(ind)]
            del coorddict['element'+str(ind)]
        coorddict['elements'] = elements

    coorddict['element_order'] = elslist
        
    return coorddict


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

        
# Define a default non-grav dict
# Default values are set for *NO* non-grav forces
default_non_grav_params = {
    'non_gravs' :   False,
    'booleans'      : {
        'yarkovski' :   False,
        'srp'       :   False,
        'marsden'   :   False,
        'yc'        :   False,
        'yabushita' :   False,
        'A1'        :   False,
        'A2'        :   False,
        'A3'        :   False,
        'DT'        :   False
        },
    'coefficients'  : {
        'yarkovski' :   None,
        'srp'       :   None,
        'A1'        :   None,
        'A2'        :   None,
        'A3'        :   None,
        'DT'        :   None
    }
}


def translate_nongravs( d ):
    """
    Function to read overall dict, find extract the non-grav params, and calculate a "translated non-grav dict"
    Does *not* replace the non-grav parames, simply returns the translated non-grav dict
    (by M. Payne)
    """

    translated_dict = default_non_grav_params
    
    # Do we have any non-gravs ?
    if d["numparams"] == 6 and d["nongrav_model"] == 0:
        translated_dict['non_gravs'] = False
    elif d["numparams"] > 6 and d["nongrav_model"] > 0:
        translated_dict['non_gravs'] = True
    else:
        raise Exception("Unexpected combination of nongrav parameters...")

    # If we have non-gravs, then change various parameters
    #   in the default-dict, according to the values in the input dict
    #
    # Example non-grav params from Margaret's json ...
    #
    #"numparams": "7",        <<-- Total number of variational parameters ( 6 for the state, plus 0-4 for the non-gravs)
    #"nongrav_model": "1",    <<-- 1 => Asteroidal or Cometary:Marsden, 2=> Cometary:YC, 3=> Cometary: Yabushita
    #"nongrav_params": "2",   <<-- Maximum number of non-grav params allowed in this model
    #"nongrav_type": ["2"],   <<-- List of the coefficients that are used
    #"nongrav_vals": [
    #    "0.00000000000000E+00",
    #    "-2.84420523316711E-03"
    #],
    #
    # We only need to do any work if there are non-gravs
    # (the default is correct for standard integrations which lack non-gravs)
    if translated_dict['non_gravs']:
        
        # Asteroidal ...
        if   d["nongrav_model"] == 1 and d["nongrav_params"] == 2:
        
            # Solar Radn Pressure
            if  1 in d["nongrav_type"] and d["numparams"] in [7,8]:
                translated_dict['booleans']['srp']              = True
                translated_dict['coefficients']['srp']          = d["nongrav_vals"][0]
            
            # Yarkovski
            if 2 in d["nongrav_type"] and d["numparams"] in [7,8]:
                translated_dict['booleans']['yarkovski']        = True
                translated_dict['coefficients']['yarkovski']    = d["nongrav_vals"][1]

            # Error
            if d["numparams"] not in [7,8] or d["nongrav_type"] not in [[1],[2],[1,2]]:
                print(f'd["numparams"]={d["numparams"]} , d["nongrav_type"]={d["nongrav_type"]}')
                raise Exception

        # Cometary:)
        elif   d["nongrav_model"] in [1,2,3]  and d["nongrav_params"] in [3,4]:
            
            # Marsden
            if d["nongrav_model"] == 1:
                translated_dict['booleans']['marsden']          = True
            
            # Yeomans and Chodas
            elif d["nongrav_model"] == 2:
                translated_dict['booleans']['yc']               = True

            # Yabushita
            elif d["nongrav_model"] == 3:
                translated_dict['booleans']['yabushita']        = True

            # Error
            else:
                raise Exception
                
            
            # Parameters
            assert d["nongrav_type"] in [ [1,2],[1,2,3],[1,2,3,4] ]
            for i in range(4):
                if i in d["nongrav_type"]:
                    param_name = 'DT' if i == 4 else 'A%d'%i
                    translated_dict['booleans'][param_name]        = True
                    translated_dict['coefficients'][param_name]    = d["nongrav_vals"][i]

            
        
        # Error
        else:
            raise Exception

    return translated_dict

def generate_system_dictionary(elsdict):
    """ put system data into a dictionary """
    # THE CHECKS WILL BECOME UNNECESSARY GIVEN VALIDATION
    return {    "eph"    : 'JPLDE431'   if not elsdict['eph']   else elsdict['eph'],
                "refsys" : 'ECLM J2000' if not elsdict['refsys'] else elsdict['refsys']}

def generate_magnitude_dictionary(coorddict):
    """ put magnitude data into a dictionary """
    return { "h" : coorddict["h"] ,  "g" : coorddict["g"]  }

def generate_epoch_dictionary(coorddict):
    """ put epoch data into a dictionary """
    return { "timesystem" : coorddict["timesystem"] ,  "epoch" : coorddict["epoch"]  }

def save_to_file(standard_format_dict , output_filepath):
    """ """
    with open(output_filepath, 'w') as f:
        json.dump(standard_format_dict, f, indent=4)
