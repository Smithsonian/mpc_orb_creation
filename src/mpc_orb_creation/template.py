'''
The initial approach taken w.r.t. establishing a schema for the mpc_orb
format was to use the genson package to create one via the use of
sample versions.

However, we have now shifted to using a version of the schema
that haw been highly edited (by hand). As such, the schema from
mpc_orb is taken to be the defining sample.

This template code simply returns a template dict/JSON that conforms to
the defining schema.
'''
# standard imports 
import sys, os 

# local imports
from mpc_orb_creation import io
from mpc_orb_creation.filepaths import filepath_dict


# ------- Sample / Template Dictionary --------
def get_template_json():
    ''' A template dict/JSON that conforms to
        the defining schema in filepaths.filepath_dict['mpcorb_schema']
    '''
    return io.load_json( filepath_dict['mpcorb_template'] )
    
