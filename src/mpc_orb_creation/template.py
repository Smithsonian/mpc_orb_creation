'''
The initial approach taken w.r.t. establishing a schema for the mpc_orb
format was to use the genson package to create one via the use of
sample versions.

However, we have now shifted to using a version of the schema
that haw been highly edited (by hand). As such, the schema in
filepaths.filepath_dict['mpcorb_schema'] should be taken to be the
defining sample.

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
    if not os.path.isfile(filepath_dict['mpcorb_template'] ):
        io.save_json( filepath_dict['mpcorb_template'] , get_template_dict( ) )
    return io.load_json( filepath_dict['mpcorb_template'] )
    
def get_template_dict():
    ''' Define a template dict/JSON that conforms to
        the defining schema in filepaths.filepath_dict['mpcorb_schema']
    '''
    return {
    # --- (1) --- Cartesian Coords ---
    "CAR": {
            "element_units" : {
                    "posn": "au",
                    "vel": "au/day"
                    },
            "non_grav_units" : {
                    "yarkovsky": "???",
                    "srp": "???",
                    "A1": "au/day^2",
                    "A2":"au/day^2",
                    "A3":"au/day^2",
                    "DT": "day"
                    },
            "eigval":
                [0.0,0.0,0.0,0.0,0.0,0.0],
            "rms":
                [0.0,0.0,0.0,0.0,0.0,0.0],
            "covariance": {
                    "cov00": 0.0,
                    "cov01": 0.0,
                    "cov02": 0.0,
                    "cov03": 0.0,
                    "cov04": 0.0,
                    "cov05": 0.0,
                    "cov06": None,
                    "cov07": None,
                    "cov08": None,
                    "cov09": None,
                    "cov11": 0.0,
                    "cov12": 0.0,
                    "cov13": 0.0,
                    "cov14": 0.0,
                    "cov15": 0.0,
                    "cov16": None,
                    "cov17": None,
                    "cov18": None,
                    "cov19": None,
                    "cov22": 0.0,
                    "cov23": 0.0,
                    "cov24": 0.0,
                    "cov25": 0.0,
                    "cov26": None,
                    "cov27": None,
                    "cov28": None,
                    "cov29": None,
                    "cov33": 0.0,
                    "cov34": 0.0,
                    "cov35": 0.0,
                    "cov36": None,
                    "cov37": None,
                    "cov38": None,
                    "cov39": None,
                    "cov44": 0.0,
                    "cov45": 0.0,
                    "cov46": None,
                    "cov47": None,
                    "cov48": None,
                    "cov49": None,
                    "cov55": 0.0,
                    "cov56": None,
                    "cov57": None,
                    "cov58": None,
                    "cov59": None,
                    "cov66": None,
                    "cov67": None,
                    "cov68": None,
                    "cov69": None,
                    "cov77": None,
                    "cov78": None,
                    "cov79": None,
                    "cov88": None,
                    "cov89": None,
                    "cov99": None,
                },
            "elements": {
                    "x": 0.0,
                    "y": 0.0,
                    "z": 0.0,
                    "vx": 0.0,
                    "vy": 0.0,
                    "vz": 0.0
                },
            "non_grav_coefficients": {
                    "A1_coeff": None,
                    "A2_coeff": None,
                    "A3_coeff": None,
                    "DT_coeff": None,
            },
    },
    # --- (2) --- Cometary Coords ---
    "COM": {
            "element_units" : {
                    "posn": "au",
                    "ang": "deg"
            },
            "non_grav_units" : {
                    "yarkovsky": "???",
                    "srp": "???",
                    "A1": "???",
                    "A2":"???",
                    "A3":"???",
                    "DT": "???"
            },
            "eigval":
                [0.0,0.0,0.0,0.0,0.0,0.0],
            "rms":
                [0.0,0.0,0.0,0.0,0.0,0.0],
            "covariance": {
                    "cov00": 0.0,
                    "cov01": 0.0,
                    "cov02": 0.0,
                    "cov03": 0.0,
                    "cov04": 0.0,
                    "cov05": 0.0,
                    "cov06": None,
                    "cov07": None,
                    "cov08": None,
                    "cov09": None,
                    "cov11": 0.0,
                    "cov12": 0.0,
                    "cov13": 0.0,
                    "cov14": 0.0,
                    "cov15": 0.0,
                    "cov16": None,
                    "cov17": None,
                    "cov18": None,
                    "cov19": None,
                    "cov22": 0.0,
                    "cov23": 0.0,
                    "cov24": 0.0,
                    "cov25": 0.0,
                    "cov26": None,
                    "cov27": None,
                    "cov28": None,
                    "cov29": None,
                    "cov33": 0.0,
                    "cov34": 0.0,
                    "cov35": 0.0,
                    "cov36": None,
                    "cov37": None,
                    "cov38": None,
                    "cov39": None,
                    "cov44": 0.0,
                    "cov45": 0.0,
                    "cov46": None,
                    "cov47": None,
                    "cov48": None,
                    "cov49": None,
                    "cov55": 0.0,
                    "cov56": None,
                    "cov57": None,
                    "cov58": None,
                    "cov59": None,
                    "cov66": None,
                    "cov67": None,
                    "cov68": None,
                    "cov69": None,
                    "cov77": None,
                    "cov78": None,
                    "cov79": None,
                    "cov88": None,
                    "cov89": None,
                    "cov99": None,
            },
            "elements": {
                    "q": 0.0,
                    "e": 0.0,
                    "i": 0.0,
                    "node": 0.0,
                    "argperi": 0.0,
                    "peri_time": 0.0
            },
            "non_grav_coefficients": {
                    "A1_coeff": None,
                    "A2_coeff": None,
                    "A3_coeff": None,
                    "DT_coeff": None,
            }
        },
        "software_data" : {
                "software_name": "orbfit",
                "software_version": "1.0",
                "run_datetime": "2022:03:01",
        },
        "system_data": {
                "eph": "DE431",
                "refsys": "Ecliptic",
                "refframe": "ICRF",
                "force_model": "????"
        },
        "designation_data": {
                "permid": "",
                "packed_primary_provisional_designation": "",
                "unpacked_primary_provisional_designation": "",
                "orbfit_name": "",
                "iau_name": "",
                "packed_secondary_provisional_designations":
                    [""],
                "unpacked_secondary_provisional_designations":
                    [""],
        },
        "orbit_fit_statistics":{
            "description" : "Summary fit statistics associated with the best-fit orbit, the observations used, etc",
            "properties": {
                "sig_to_noise_ratio"    :
                    [0.0,0.0,0.0,0.0,0.0,0.0,],
                "snr_below_3"           : False,
                "snr_below_1:"          : False,
                "U_param"               : 0.0,
                "score1"                : 0.0,
                "score2"                : 0.0,
                "orbit_quality"         : 'good',
                "normalized_RMS"        : 0.0,
                "not_normalized_RMS"    : 0.0,
                "nobs_total"            : 0,
                "nobs_total_sel"        : 0,
                "nobs_optical"          : 0,
                "nobs_optical_sel"      : 0,
                "nobs_radar"            : 0,
                "nobs_radar_sel"        : 0,
                "arc_length_total"      : 0,
                "arc_length_sel"        : 0,
                "nopp"                  : 0,
                "numparams"             : 6
            }
        },
        "non_grav_data": {
                "non_gravs": False,
                "non_grav_booleans": {
                        "yarkovsky": False,
                        "srp": False,
                        "marsden": False,
                        "yc": False,
                        "yabushita": False,
                        "A1": False,
                        "A2": False,
                        "A3": False,
                        "DT": False,
                        }
        },
        "magnitude_data": {
                "H": 0.0,
                "G": 0.0,
                "G1": None,
                "G2": None,
                "G12": None,
                "photometric_model" : "????"
        },
        "epoch_data": {
                "timesystem": "TT",
                "timeform": "MJD",
                "epoch": 0.0,
        },
        "moid_data": {
                "Venus": None,
                "Earth": None,
                "Mars": None,
                "Jupiter": None,
                "moid_units" :"au"
        },
        "categorization": {
                "object_type_str": "",
                "object_type_int": None,
                "orbit_type_str": "",
                "orbit_type_int": None,
                "orbit_subtype_str": "",
                "orbit_subtype_int": None
        }
}


