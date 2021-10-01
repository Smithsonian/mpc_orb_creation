'''
Quick demo file to illustrate various key points of how to use these "creation" functions

Is far from complete: will need filling out with more info. as I progress.
May also want to split into some different smaller demos in the future

MJP : 2021-10-01
'''


# Ensure the code-directory is in the path
from os.path import join, dirname, abspath
import sys
pack_dir  = dirname(dirname(abspath(__file__))) # Package directory
code_dir  = join(pack_dir, 'mpc_orb_creation')  # Code dir
sys.path.append(code_dir)
from os.path import join, dirname, abspath, isfile
from os import remove


# Import the objects / functions to be demonstrated ...
from filepaths import filepath_dict  # convenience filepath-defn dictionary ...
import bootstrap                     # create all schema JSONs ...
import schema


def filepath_demo():
    ''' The file mpc_orb_creation/mpc_orb_creation/filepaths.py defines the locations of
        many important files and directories within the repo
        
        The filepaths.py file has a number of comments to describe what is in the various locations, but this filepath_demo() function simply highlights a few key areas '''
    print('\n'*3, '-------filepath_demo---------')
    
    
    # ---- (1) ---- List of defining JSONs that represent generally valid fel-files
    print()
    filelist= filepath_dict['orbfit_defining_sample_general']
    assert len(filelist) >= 5 # We expect there to be many files ...
    print(f'N_files in orbfit_defining_sample_general = ... {len(filelist)}')
    for f in filelist : print(f)
    
    # ---- (2) ---- List of defining JSONs that represent valid fel-files that are good to convert to mpc_orb format
    print()
    filelist= filepath_dict['orbfit_defining_sample_convert']
    assert len(filelist) >= 5 # We expect there to be many files ...
    print(f'N_files in orbfit_defining_sample_convert = ... {len(filelist)}')
    for f in filelist : print(f)
    

def bootstrap_demo():
    '''
    The bootstap.bootstrap() function does everything we need to take us from
    an initial set of defining files, to having a full set of validation
    schema files
    
    Here we demonstrate how to use it and what it does
    '''
    print('\n'*3, '-------bootstrap_demo---------')
    
    # Explicitly delete any of the schema files and/or "numerical conversion" files ...
    # that have previously been generated from the above defining samples
    print('Removing previously generated files ... ')
    for f in filepath_dict['mpcorb_defining_sample']:
        if isfile(f) :
            remove(f)
    for f in ['orbfit_general_schema','orbfit_conversion_schema', 'mpcorb_schema']:
        if isfile(filepath_dict[f]) :
            remove(filepath_dict[f])
            
    # Call the bootstap function
    bootstrap.bootstrap( VERBOSE=True )
    
    # Demonstrate that the files we deleted above have now been reconstructed
    for f in filepath_dict['mpcorb_defining_sample']:
        assert isfile(f) , f'{f} does not exist'
    for f in ['orbfit_general_schema','orbfit_conversion_schema', 'mpcorb_schema']:
        assert isfile(filepath_dict[f]), f'{filepath_dict[f]} does not exist'




def orbfit_results_query_demo():
    '''
    The /sa/orbit_pipeline/db_query_orbits.py module has code that queries the orbfit_results table
    
    Here I demonstrate how to use it...
    
    (This is outside the scope of this mpc_orb_creation module, but I just want to remind myself how to use the code...)
    
    '''
    print('\n'*3, '-------orbfit_results_query_demo---------')
    
    # Import library ...
    sys.path.append('/sa/orbit_pipeline/')
    import db_query_orbits

    # Query table for desig: expect a dictionary to be returned...
    # - dict_keys(['id', 'packed_primary_provisional_designation', 'unpacked_primary_provisional_designation', 'rwo_json', 'standard_epoch_json', 'mid_epoch_json', 'quality_json', 'created_at', 'updated_at'])
    unpacked_primary_desig = '2020 AB1'
    result = db_query_orbits.QueryOrbfitResults().get_orbit_row( unpacked_primary_desig )
    for k,v in result.items():
        print(k,":",v)
        
        
def schema_validation_demo_1():
    '''
    
    '''
    print('\n'*3, '-------schema_validation_demo_1---------')
    
    # Query orbfit_table as per *orbfit_results_query_demo* above
    sys.path.append('/sa/orbit_pipeline/')
    import db_query_orbits
    unpacked_primary_desig = '2020 AB1'
    result_dict = db_query_orbits.QueryOrbfitResults().get_orbit_row( unpacked_primary_desig )

    standard_epoch_dict = result_dict['standard_epoch_json']

    # Attempt to stick the orbfit results dictionary through the validation routines
    print('Attempting validation...')
    
    # We expect thefollowing 2 to pass ...
    schema.validate_orbfit_general(standard_epoch_dict , VERBOSE=True )
    schema.validate_orbfit_conversion(standard_epoch_dict , VERBOSE=True )
    # We expect the following to fail
    print('***WE EXPECT A FAILURE !!!***')
    schema.validate_mpcorb(standard_epoch_dict , VERBOSE=True )

if __name__ == "__main__":
    filepath_demo()
    bootstrap_demo()
    orbfit_results_query_demo()
    schema_validation_demo_1()
    
    
