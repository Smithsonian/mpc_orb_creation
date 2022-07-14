"""
Defining filepaths used by mpc_orb
"""

# Import third-party packages
# -----------------------
import glob
from os.path import join, dirname, abspath
import os

# Directories
# -----------------------
pack_dir  = dirname(dirname(dirname(abspath(__file__))))    # Package directory

json_dir  = join(pack_dir, 'json_files')           # All of the json-files
code_dir  = join(pack_dir, 'src/mpc_orb_creation') # All of the packaged python code
test_dir  = join(pack_dir, 'tests')                # All of the test code
demo_dir  = join(pack_dir, 'demos')                # Some demos/examples

def_gen_dir  = join(json_dir, 'defining_sample_json/general')   # Dir. containing defining JSONs that represent generally valid fel-files
def_con_dir  = join(json_dir, 'defining_sample_json/convert')   # Dir. containing defining JSONs that represent valid fel-files that are good to convert to mpc_orb format
def_cons_dir = join(json_dir, 'defining_sample_json/construct') # Dir. containing defining JSONs that represent valid orbfit output dictionaries
                                                                # (containing multiple sub-dictionaries) that are good to convert to mpc_orb format
def_mpc_dir  = join(json_dir, 'defining_sample_json/mpcorb')    # Dir. containing defining JSONs that represent valid mpc_orb.json files

sch_dir      = join(json_dir, 'schema_json')                    # Dir. containing validation schema JSON files that created from the above defining samples
tj_dir       = join(json_dir, 'test_jsons')                     # Dir. containing JSONs that get used in unit-tests
tem_dir      = join(json_dir, 'template_json')                  # Dir. containing template JSONs that get used in...




# Files / File-Lists
# -----------------------

# start with the defining felfiles for orbfit (string) jsons ...
orbfit_defining_files_general      = glob.glob( def_gen_dir + "/*str.json" )    # List of defining JSONs that represent generally valid fel-files
orbfit_defining_files_general.extend(glob.glob( def_gen_dir + "/*orig.json" ))

orbfit_defining_files_convert      = glob.glob( def_con_dir + "/*str.json" )    # List of defining JSONs that represent valid fel-files that are good to convert to mpc_orb format
orbfit_defining_files_convert.extend(glob.glob( def_con_dir + "/*orig.json" ))

orbfit_defining_files_construct      = glob.glob( def_cons_dir + "/*str.json" )   # List of defining JSONs that represent valid orbfit output dictionaries
orbfit_defining_files_construct.extend(glob.glob( def_cons_dir + "/*orig.json" )) # (containing multiple sub-dictionaries) that are good to convert to mpc_orb format


# Put all of the files/file-lists into a dictionary ...
# -----------------------
filepath_dict = {
    'orbfit_defining_sample_general'    : orbfit_defining_files_general,          # List of defining JSONs that represent generally valid fel-files
    'orbfit_defining_sample_convert'    : orbfit_defining_files_convert,          # List of defining JSONs that represent valid fel-files that are good to convert to mpc_orb format
    'orbfit_defining_sample_construct'  : orbfit_defining_files_construct,        # List of :wqdefining JSONs that represent valid orbfit output dict-of-dicts...
                                                                                  #     that are good to convert to mpc_orb format
    'mpcorb_defining_sample'     : [ join(def_mpc_dir , os.path.split(_)[-1][:os.path.split(_)[-1].rfind("_")+1] ) + "num.json" for _ in orbfit_defining_files_convert],
    
    'orbfit_general_schema'      : join(sch_dir, 'orbfit_general_schema.json'),      # The validation schema json created from the defining sample (for generally valid fel-files)
    'orbfit_conversion_schema'   : join(sch_dir, 'orbfit_conversion_schema.json'),   # The validation schema json created from the defining sample (for valid convertible fel-files)
    'orbfit_construction_schema' : join(sch_dir, 'orbfit_construction_schema.json'), # The validation schema json created from the defining sample...
                                                                                     #(for valid convertible orbfit-output consisting of a dictionary-of-dictionaries)
    'mpcorb_schema'             : join(sch_dir, 'mpcorb_schema.json'),               # The validation schema json
    'mpcorb_template'           : join(tem_dir, 'mpcorb_template.json'),             # A template mpc_orb json

    'test_fail_mpcorb'          : glob.glob( tj_dir + "/fail_mpcorb/*" ),
    'test_fail_orbfit_convert'  : glob.glob( tj_dir + "/fail_orbfit_convert/*" ),
    'test_fail_orbfit_construct': glob.glob( tj_dir + "/fail_orbfit_construct/*" ),
    'test_fail_orbfit_general'  : glob.glob( tj_dir + "/fail_orbfit_general/*" ),
    'test_pass_mpcorb'          : glob.glob( tj_dir + "/pass_mpcorb/*" ),
    'test_pass_orbfit_convert'  : glob.glob( tj_dir + "/pass_orbfit_convert/*" ),
    'test_pass_orbfit_construct': glob.glob( tj_dir + "/pass_orbfit_construct/*" ),
    'test_pass_orbfit_general'  : glob.glob( tj_dir + "/pass_orbfit_general/*" ),
    'test_pass_orbfit_standard' : glob.glob( tj_dir + "/pass_orbfit_standard/*" ), # Example(s) of new "standard" orbfit output dict 
}
