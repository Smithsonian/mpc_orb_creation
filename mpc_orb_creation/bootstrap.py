"""
mpc_orb/bootstrap.py
 - The function calls required to take us from ~nothing, to having fully specified schema for all file types
 - This is the means by which the schema are defined / created
 - Expected to be used rarely
 - Expected to only be used internally by the MPC
 - Essentially a convenience wrapper around the functionalities in schema.py

Author(s)
This module: MJP
"""

# Import third-party packages
# -----------------------
import json
from jsonschema import validate
import genson
from genson import SchemaBuilder
from os.path import join, dirname, abspath, isfile


# local imports
# -----------------------
import schema
import convert
import interpret
from filepaths import filepath_dict


# Main functionality to bootstrap the creation of schema files
# -----------------------

def bootstrap( VERBOSE=False ):
    """
    The function calls required to take us from ~nothing, to having fully specified schema
    
    requires:
     - various defining json files to exist
     - schema-creation code to exist in the schema.py module
     
    creates:
     - schema-json files in ../json_files/schema_json/
    
    """
    if VERBOSE:
        print('-------bootstrap.bootstrap()---------')

    # (1) Create "orbfit felfile" schema from defining sample(s)
    #     NB: This creates 2 kinds of schema file, (i) general and (ii) conversion-specific
    schema.create_orbfit_felfile_schema_from_defining_sample_json( VERBOSE=VERBOSE )


    # (2) Convert "orbfit felfile" defining sample(s) to create defining "mpcorb" defining sample(s)
    for fp_in, fp_out in zip(   filepath_dict['orbfit_defining_sample_convert'],
                                filepath_dict['mpcorb_defining_sample']) :
                                
        if VERBOSE:
            print(f'Converting input-file {fp_in} to output-file {fp_out}')

        # Get the file contents
        orbfit_dict,input_filepath = interpret.interpret(fp_in)
        
        # Validate (unnecessary)
        schema.validate_orbfit_conversion(orbfit_dict)
        
        # Convert to mpc_orb format
        mpcorb_format_dict = convert.std_format_els(orbfit_dict)
        
        # Save to file
        schema.save_json(fp_out, mpcorb_format_dict)


    # (3) Create "mpcorb" schema from defining sample(s)
    schema.create_mpcorb_schema_from_defining_sample_json()

if __name__ == "__main__":
    bootstrap()
