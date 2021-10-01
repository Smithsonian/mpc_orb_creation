"""
Defining filepaths used by mpc_orb
"""

# Import third-party packages
# -----------------------
import glob
from os.path import join, dirname, abspath
import os

# filepaths
# -----------------------
pack_dir  = dirname(dirname(abspath(__file__))) # Package directory

json_dir  = join(pack_dir, 'json_files')        # All of the json-files
code_dir  = join(pack_dir, 'mpc_orb')           # All of the packages python code
test_dir  = join(pack_dir, 'tests')             # All of the test code
demo_dir  = join(pack_dir, 'demos')             # Some demos/examples

def_gen_dir  = join(json_dir, 'defining_sample_json/general')
def_con_dir  = join(json_dir, 'defining_sample_json/convert')
def_mpc_dir  = join(json_dir, 'defining_sample_json/mpcorb')
sch_dir      = join(json_dir, 'schema_json')
tj_dir       = join(json_dir, 'test_jsons')

# start with the defining felfiles for orbfit (string) jsons ...
orbfit_defining_files_general      = glob.glob( def_gen_dir + "/*str.json" )
orbfit_defining_files_general.extend(glob.glob( def_gen_dir + "/*orig.json" ))

orbfit_defining_files_convert      = glob.glob( def_con_dir + "/*str.json" )
orbfit_defining_files_convert.extend(glob.glob( def_con_dir + "/*orig.json" ))


# Put everything into a dictionary ...
filepath_dict = {
    'orbfit_defining_sample_general'    : orbfit_defining_files_general,
    'orbfit_defining_sample_convert'    : orbfit_defining_files_convert,
    'mpcorb_defining_sample'    : [ join(def_mpc_dir , os.path.split(_)[-1][:os.path.split(_)[-1].rfind("_")+1] ) + "num.json" for _ in orbfit_defining_files_convert],
    
    'orbfit_general_schema'     : join(sch_dir, 'orbfit_general_schema.json'),
    'orbfit_conversion_schema'  : join(sch_dir, 'orbfit_conversion_schema.json'),
    'mpcorb_schema'             : join(sch_dir, 'mpcorb_schema.json'),

    'test_fail_mpcorb'          : glob.glob( tj_dir + "/fail_mpcorb/*" ),
    'test_fail_orbfit_convert'  : glob.glob( tj_dir + "/fail_orbfit_convert/*" ),
    'test_fail_orbfit_general'  : glob.glob( tj_dir + "/fail_orbfit_general/*" ),
    'test_pass_mpcorb'          : glob.glob( tj_dir + "/pass_mpcorb/*" ),
    'test_pass_orbfit_convert'  : glob.glob( tj_dir + "/pass_orbfit_convert/*" ),
    'test_pass_orbfit_general'  : glob.glob( tj_dir + "/pass_orbfit_general/*" ),

}


