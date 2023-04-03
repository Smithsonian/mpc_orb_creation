"""
mpc_orb/schema.py
 - Code to *validate* a candidate json-file against a schema file

NB
 - Code to *create* the required three types of schema file using supplied defining json-files has been moved
   to the "schema_creation.py" module. Creation code now considered ARCHAIC.


Author(s)
MJP
"""

# Import third-party packages
import json
from jsonschema import validate
import genson
from genson import SchemaBuilder
from os.path import join, dirname, abspath, isfile


# local imports
# -----------------------
from . import interpret
from .filepaths import filepath_dict


# IO functions
# -----------------------
def load_json( json_filepath ):
    """ """
    with open( json_filepath ) as f:
        return json.load(f)
        

# Validation functions
# -----------------------
def validate_orbfit_standardized(arg, VERBOSE=False):
    '''
    Test whether json is a valid example of a "standardized" orbfit output dictionary
    E.g. As expected to be created using ... 
    '''
    return True 

def validate_orbfit_general(arg, VERBOSE=False):
    """
    Test whether json is a valid example of an orbfit-felfile json
    Input can be json-filepath, or dictionary of json contents

    *** MJP 2022-05-17 : May not be needed anymore ***

    """
    if VERBOSE:
        print('-------schema.validate_orbfit_general()---------')

    # interpret the input (allow dict or json-filepath)
    orbfit_dict, input_filepath = interpret.interpret(arg)
    
    # validate
    # NB # If no exception is raised by validate(), the instance is valid.
    try:
        validate(instance=orbfit_dict, schema=load_json( filepath_dict['orbfit_general_schema'] ))
        return True
    except:
        return False

def validate_orbfit_conversion( arg , VERBOSE=False ):
    """
    Test whether json is a valid example of an orbfit-felfile json that is suitable for conversion to mpcorb-format
    Input can be json-filepath, or dictionary of json contents

    *** MJP 2022-05-17 : May not be needed anymore ***

    """
    if VERBOSE:
        print('-------schema.validate_orbfit_conversion()---------')

    # interpret the input (allow dict or json-filepath)
    data, input_filepath = interpret.interpret(arg)

    # validate
    # NB # If no exception is raised by validate(), the instance is valid.
    try:
        validate(instance=data, schema=load_json( filepath_dict['orbfit_conversion_schema'] ))
        return True
    except:
        return False
        
def validate_orbfit_result( arg , VERBOSE=False ):
    """
    Test whether supplied input is a valid example of single, large orbfit-results dictionary containing a large variety of sub-dictionaries.
    
    It is expected that the supplied dictionary has been produced
    by a python wrapper such as create_output_dictionaries.py
    (in its updated form)
    
    Expected Structure of input orbfit data
        'eq0dict'
        'eq1dict'
        'rwodict'
        'orbit_quality_metrics'
        'bad_trk_dict'
        'ele220_str'
        'moids_dict'
        'mpc_orb_dict'
        'stats_dict'

    Input can be json-filepath, or dictionary of json contents
    """
    if VERBOSE:
        print('-------schema.validate_orbfit_result()---------')

    # interpret the input (allow dict or json-filepath)
    data, input_filepath = interpret.interpret(arg)

    # validate
    # NB # If no exception is raised by validate(), the instance is valid.
    try:
        validate(instance=data, schema=load_json( filepath_dict['orbfit_result_metadict'] ))
        return True
    except:
        return False

def validate_mpcorb( arg , VERBOSE=False ):
    """
    Test whether json is a valid example of an mpcorb json
    Input can be json-filepath, or dictionary of json contents
    """
    if VERBOSE:
        print('-------schema.validate_mpcorb()---------', flush=True)

    # interpret the input (allow dict or json-filepath)
    data, input_filepath = interpret.interpret(arg)

    # validate
    # NB # If no exception is raised by validate(), the instance is valid.
    try:
        validate(instance=data, schema=load_json( filepath_dict['mpcorb_schema'] ))
        print(f'Valid!', flush=True)
        return True
    except Exception as e:
        print(f'Exception:\n{e}')
        return False

