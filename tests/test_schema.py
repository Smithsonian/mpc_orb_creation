# local imports
from mpc_orb_creation import schema
from mpc_orb_creation import io
from mpc_orb_creation.filepaths import filepath_dict


# ---- Tests ----
def test_schema_import():
    ''' Test the mpcorb_schema can be read as a json '''
    try:
        schema_data = io.load_json( filepath_dict['mpcorb_schema'] )
    except:
        schema_data = {}
    assert schema_data
    
    
