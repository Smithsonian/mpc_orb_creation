# standard imports
import os, sys
from jsonschema import validate

# local imports
from mpc_orb_creation import template
from mpc_orb_creation import schema
from mpc_orb_creation import io
from mpc_orb_creation.filepaths import filepath_dict

# ---- Tests ----
def test_get_template_dict():
    ''' Test the template can be read as a dict '''
    try:
        template_dict = template.get_template_dict( )
    except:
        template_dict = {}
    assert template_dict

def test_save_template_dict_to_json():
    ''' Test creation of the template JSON file'''
    # Get the dict & attempt to save to json file
    io.save_json( filepath_dict['mpcorb_template'] , template.get_template_dict( ) )
    # Assert file exists
    assert os.path.isfile(filepath_dict['mpcorb_template'] )
    
def test_template_import():
    ''' Test the template can be read as a json '''
    try:
        template_data = io.load_json( filepath_dict['mpcorb_template'] )
    except:
        template_data = {}
    assert template_data
    print(template_data)
    
def test_template_validates():
    '''
        Test the template validates against the schema
        NB: In order to get this to work, the schema has to allow "Null"/"None" values for a number of fields
    '''
    # NB: If no exception is raised by validate(), the instance is valid.
    validate(   instance    =io.load_json( filepath_dict['mpcorb_template'] ),
                schema      =io.load_json( filepath_dict['mpcorb_schema']   )
                )

