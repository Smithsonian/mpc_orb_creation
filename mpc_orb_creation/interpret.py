"""
mpc_orb/interpret.py
A convenience func to interpret an input argument as some kind of json-related input
I.e. looks to see whether its a filepath, a dictionary
"""

# Import third-party packages
import json
from os.path import isfile


def interpret(arg):
    """
    convenience func to interpret input arg as some kind of json-related input
    returns dict
    """
    
    # try to interpret input as a json-filepath
    if isinstance(arg, str) and isfile(arg):
        try:
            with open(arg) as f:
                json_dict       = json.load(f)
                input_filepath  = arg
        except Exception as e:
            pass
    
    # if its a dictionary, use that
    elif isinstance(arg, dict):
        json_dict       = arg
        input_filepath  = None
    # no other options yet implemented
    else:
        print(f"Input {arg}\nis of type {type(arg)} and cannot be interpreted as json-dict")
        raise  Exception(f"Input {arg}\nis of type {type(arg)} and cannot be interpreted as json-dict")
    
    # return the contents of the json file in dict form
    return json_dict,input_filepath

