# standard imports
import json
import os, sys

# IO functions
# -----------------------
def load_json( json_filepath ):
    """ """
    with open( json_filepath ) as f:
        return json.load(f)
        
def save_json( json_filepath , data_dict, VERBOSE=False ):
    """ Being very careful here as any jsons saved by this module will be the main standardizing schema """
    if VERBOSE:
        print('-------schema.save_json()---------')

    if os.path.isfile(json_filepath):
        raise Exception(f"The important json file {json_filepath} already exists ... To prevent accidental over-writes, this routine will go no further ... ")
    else:
        with open( json_filepath , 'w' ) as f:
            json.dump(data_dict , f , indent=4)

