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

# Import the objects / functions to be demonstrated ...
from filepaths import filepath_dict  # convenience filepath-defn dictionary ...
import bootstrap                     # create all schema JSONs ...


def filepath_demo():
    ''' The file mpc_orb_creation/mpc_orb_creation/filepaths.py defines the locations of
        many important files and directories within the repo
        
        The filepaths.py file has a number of comments to describe what is in the various locations, but this filepath_demo() function simply highlights a few key areas '''
    print('-------filepath_demo---------')
    
    
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
    print('-------bootstrap_demo---------')
    
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
    bootstrap.bootstap( VERBOSE=True )
    
    # Demonstrate that the files we deleted above have now been reconstructed
    for f in filepath_dict['mpcorb_defining_sample']:
        assert isfile(f) , f'{f} does not exist'
    for f in ['orbfit_general_schema','orbfit_conversion_schema', 'mpcorb_schema']:
        assert isfile(filepath_dict[f]), f'{filepath_dict[f]} does not exist'




if __name__ == "__main__":
    filepath_demo()
    bootstrap_demo()
