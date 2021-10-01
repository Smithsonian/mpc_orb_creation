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


def filepath_demo():
    ''' The file mpc_orb_creation/mpc_orb_creation/filepaths.py defines the locations of
        many important files and directories within the repo
        
        The filepaths.py file has a number of comments to describe what is in the various locations, but this filepath_demo() function simply highlights a few key areas '''
    
    # Import the convenience filepath-defn dictionary
    from filepaths import filepath_dict
    
    # List of defining JSONs that represent generally valid fel-files
    print( filepath_dict['orbfit_defining_sample_general'] )
