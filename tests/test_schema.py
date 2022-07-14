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
    
    
def test_validate_mpcorb_A():
    '''
        Test the template (empty) mpcorb validates against the schema
        NB(1): In order to get this to work, the schema has to allow "Null"/"None"
                values for a number of fields
        NB(2): This test essentially assumes that "test_template.test_template_validates()" passes
    '''
    # Load the template into a dict
    template_data = io.load_json( filepath_dict['mpcorb_template'] )
    
    # Pass template-dict to validator and assert is True (i.e. is valid)
    assert schema.validate_mpcorb(template_data)

    # Pass template-string to validator and assert is True (i.e. is valid)
    # - This works because the *validate_mpcorb* func will also try to load a
    #   json from a supplied string (i.e. assumes it's a filepath)
    assert schema.validate_mpcorb(template_data)

def test_validate_mpcorb_B():
    '''
        Test a sample mpcorb file validates against the schema
    '''
    assert False


def test_validate_orbfit_result_A():
    '''
        ...
    '''
    assert False
    
