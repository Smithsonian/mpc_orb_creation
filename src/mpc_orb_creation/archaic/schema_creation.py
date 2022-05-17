'''
schema_creation.py

These functions were initially used to create some schema from sample input files.
These functions were initially located in the "schema.py" module.
These functions have been located here to emphasize that these function are ...
    ARCHAIC and
    PROBABLY WILL NOT NEED TO BE USED ANYMORE


'''
# local imports
from io import load_json, save_json

# Schema Creation functions
# -----------------------
def get_schema_from_builder(list_of_sample_dicts , VERBOSE=False ):
    """
    This code uses the "genson" package to create a json "schema" dictionary
    The schema is created by reading from a list of defining sample dicts,
    and using those as the basis for the schema.
    """

    if VERBOSE:
        print('-------schema.get_schema_from_builder()---------')

    # Instantiate Genson object : https://pypi.org/project/genson/
    builder = SchemaBuilder()
    builder.add_schema({"type": "object", "properties": {}})

    # Add data from defining sample file
    assert isinstance(list_of_sample_dicts , list)
    for n, d in enumerate(list_of_sample_dicts):
        assert isinstance(d, dict)
        builder.add_object(d)

    # Convert to schema
    return builder.to_schema()

def create_orbfit_felfile_schema_from_defining_sample_json( VERBOSE=False ):
    """
    Use predefined sample json(s) as the basis to construct json schema for the orbfit felfiles
    
    NB(1) Some "by-hand" modifications are done to the basic schema generated from the defining sample
    NB(2) Two different schema are created ( one general, one conversion-specific)
    The results are saved-to, and thus define, the standard schema files
    
    *** IT IS EXPECTED THAT THIS WILL BE USED EXTREMELY RARELY ONCE WE HAVE EVERYTHING SET-UP ***
    """

    if VERBOSE:
        print('-------schema.create_orbfit_felfile_schema_from_defining_sample_json()---------')

    # load defining sample
    list_of_sample_dicts_general = [load_json( _ ) for _ in filepath_dict['orbfit_defining_sample_general'] ]
    list_of_sample_dicts_convert = [load_json( _ ) for _ in filepath_dict['orbfit_defining_sample_convert'] ]

    # instantiate "builder" & use to convert json-dict to an (initial) schema
    schema_dict_general = get_schema_from_builder(list_of_sample_dicts_general , VERBOSE=VERBOSE)
    schema_dict_convert = get_schema_from_builder(list_of_sample_dicts_convert , VERBOSE=VERBOSE)

    # do orbfit-specific modifications
    schema_dict_general  = do_orbfit_general_schema_mods(schema_dict_general,    VERBOSE=VERBOSE)
    schema_dict_convert  = do_orbfit_conversion_schema_mods(schema_dict_convert, VERBOSE=VERBOSE)

    # Save schema-dict to file
    save_json( filepath_dict['orbfit_general_schema'] ,    schema_dict_general )
    save_json( filepath_dict['orbfit_conversion_schema'] , schema_dict_convert )

    return True

def do_orbfit_general_schema_mods(schema_dict , VERBOSE=False ):
    """
    No schema mods currently implemented
    Additional modifications likely to be required to refine the definition/schema
    """
    if VERBOSE:
        print('-------schema.do_orbfit_general_schema_mods()---------')
    return schema_dict

def do_orbfit_conversion_schema_mods(schema_dict , VERBOSE=False ):
    """
    Minimal schema mods currently implemented
    Additional modifications likely to be required to refine the definition/schema
    """
    if VERBOSE:
        print('-------schema.do_orbfit_conversion_schema_mods()---------')

    # (1) Require "CAR" and "COM" coords, other coords are optional
    schema_dict["required"] = [ "CAR" , "COM" ]
    return schema_dict

def create_mpcorb_schema_from_defining_sample_json(VERBOSE=False ):
    """
    Use a predefined sample json as the basis to construct a json schema for the mpc_orb files
    Note that some "by-hand" modifications are done to the basic schema generated from the defining sample
    The result is saved and thus defines the standard schema file
    *** IT IS EXPECTED THAT THIS WILL BE USED EXTREMELY RARELY ***
    """
    if VERBOSE:
        print('-------schema.create_mpcorb_schema_from_defining_sample_json()---------')

    # load defining sample
    list_of_sample_dicts = [load_json( _ ) for _ in filepath_dict['mpcorb_defining_sample'] ]

    # instantiate "builder" & use to convert json-dict to an (initial) schema
    schema_dict = get_schema_from_builder(list_of_sample_dicts)

    # do mpc_orb-specific modifications
    schema_dict = do_mpcorb_schema_mods(schema_dict)
    
    # Save schema-dict to file
    save_json( filepath_dict['mpcorb_schema'] , schema_dict )
    
    return True

def do_mpcorb_schema_mods(schema_dict , VERBOSE=False ):
    """
    Minimal schema mods currently implemented
    Additional modifications likely to be required to refine the definition/schema
    """
    if VERBOSE:
        print('-------schema.do_mpcorb_schema_mods()---------')

    # Recursively walk through the levels of the schema, adding
    #     requirements & descriptions where possible
    walk(schema_dict, mpcorb_description_dict)

    # Any other alterations to be made ???

    return schema_dict

def walk( schema_d , description_d , VERBOSE=False ):
    ''' Recursively walk through the levels of the schema, adding requirements & descriptions where possible
    
    inputs:
    -------
    schema_d : dictionary
     - entire json schema dict, or a subset of the json schema dict
    description_d : dictionary
     - dictionary to describe the entire json schema dict, or a subset of that description dictionary

    outputs:
    --------
    
    '''
    if VERBOSE:
        print('-------schema.walk()---------')

    if "properties" in schema_d.keys() :
    
        # (a) See if there is a "required" and/or "description" to be added ...
        for label in ["required","description"]:
            if label in description_d : schema_d[label] = description_d[label]

        # (b) Descend and repeat (properties => a lower level of 1-or-more further data types)
        for key in schema_d["properties"].keys() :
            walk( schema_d["properties"][key] , description_d["properties"][key] )
        

'''
# *** This dictionary provides the DESCRIPTIONS and REQUIREMENTS that I want to add to the schema ***
#
# This dictionary has the same overall structure that we expect to
# form from the *create_mpcorb_schema_from_defining_sample_json* function.
#
# This dictionary was formed by using *create_mpcorb_schema_from_defining_sample_json*
# WITHOUT any added descriptions or requirements.
# (NB many requirements are generated by default by the genson routine)
# MJP subsequently added in the "description" fields by hand, as well
#     as sometimes editing the "requirement" fields
#
# *** MORE WORK REQUIRED TO RIGOROUSLY DESCRIBE THE VARIOUS FIELDS ***
#
# This dictionary will have to be iteratively evolved if/when we change the
# defining schema
'''
mpcorb_description_dict = {

    # ------------------------------------------
    # Top level Specification
    # N.B. Explicitly editing requirements so that we
    # require "CAR" and "COM" coords, leaving other coords to be optional
    "required": [   "CAR",
                    "COM",
                    "system_data",
                    "designation_data",
                    "orbit_fit_statistics",
                    "nongrav_data",
                    "magnitude_data",
                    "epoch_data" ],
    "description" : "Standardized JSON orbit exchange format. Designed to communicate the best-fit orbit for a single minor planet or comet. ",
    # ------------------------------------------

    "properties": {
        "CAR": {
            # ------------------------------------------
            # Cartesian Element Specification
            "description" : "Description of the best-fit orbit based on a cartesian coordinate system (plus any non-gravs). Contains the best-fit orbit and covariance matrix.",
            # ------------------------------------------
            "properties": {
                "element_units" : {
                    # ------------------------------------------
                    # element_units Specification
                    "description" : "Physical Units associated with cartesian orbital elements ",
                    # ------------------------------------------
                    "type": "object",
                    "properties": {
                        "posn": {
                            "type": "string",
                            "enum": ["au"]
                        },
                        "vel": {
                            "type": "string",
                            "enum": ["au/day"]
                        },
                    },
                    "required": ["posn","vel"]
                },
                "non_grav_units" : {
                    # ------------------------------------------
                    # non_grav_units Specification
                    "description" : "Physical Units associated with non-gravitational fit-parameters ",
                    # ------------------------------------------
                    "type": "object",
                    "properties": {
                        "yarkovsky": {
                            "type": "string",
                            "enum": ["???"]
                        },
                        "srp": {
                            "type": "string",
                            "enum": ["???"]
                        },
                        "A1": {
                            "type": "string",
                            "enum": ["???"]
                        },
                        "A2": {
                            "type": "string",
                            "enum": ["???"]
                        },
                        "A3": {
                            "type": "string",
                            "enum": ["???"]
                        },
                        "DT": {
                            "type": "string",
                            "enum": ["???"]
                        },                    },
                    "required": [   "yarkovsky",
                                    "srp",
                                    "A1",
                                    "A2",
                                    "A3",
                                    "DT"]
                },
                "eigval": {
                    # ------------------------------------------
                    # eigval Specification
                    "description" : "Eigenvalues for the cartesian orbital elements (and any non-gravitational parameters). Of length 6 if gravity-only, or 7-10 if we have non-gravs",
                    # ------------------------------------------
                    "type": "array",
                    "items": {
                        "type": "number"
                    }
                },
                "rms": {  # We want this always to be of length 6: the non-gravs are separate
                    # ------------------------------------------
                    # rms Specification
                    "description" : "RMS values for the cartesian orbital elements (and any non-gravitational parameters). Of length 6 if gravity-only, or 7-10 if we have non-gravs",
                    # ------------------------------------------
                    "type": "array",
                    "items": {
                        "type": "number"
                    }
                },
                "covariance": { # Of size 6x6 (if grav-only), or 7^2-10^2 if we have non-gravs
                    # ------------------------------------------
                    # covariance Specification
                    "description" : "Covariance matrix elements (upper triangular) for the cartesian orbital elements (and any non-gravitational parameters). Reconstructed square matrix is of size 6x6 if gravity-only, or 7x7 -to- 10x10 if we have non-grav parameters.",
                    # ------------------------------------------
                    "type": "object",
                    "properties": {
                        "cov00": {
                            "type": "number"
                        },
                        "cov01": {
                            "type": "number"
                        },
                        "cov02": {
                            "type": "number"
                        },
                        "cov03": {
                            "type": "number"
                        },
                        "cov04": {
                            "type": "number"
                        },
                        "cov05": {
                            "type": "number"
                        },
                        "cov06": {
                            "type": "number"
                        },
                        "cov07": {
                            "type": "number"
                        },
                        "cov08": {
                            "type": "number"
                        },
                        "cov09": {
                            "type": "number"
                        },
                        "cov11": {
                            "type": "number"
                        },
                        "cov12": {
                            "type": "number"
                        },
                        "cov13": {
                            "type": "number"
                        },
                        "cov14": {
                            "type": "number"
                        },
                        "cov15": {
                            "type": "number"
                        },
                        "cov16": {
                            "type": "number"
                        },
                        "cov17": {
                            "type": "number"
                        },
                        "cov18": {
                            "type": "number"
                        },
                        "cov19": {
                            "type": "number"
                        },

                        "cov22": {
                            "type": "number"
                        },
                        "cov23": {
                            "type": "number"
                        },
                        "cov24": {
                            "type": "number"
                        },
                        "cov25": {
                            "type": "number"
                        },
                        "cov26": {
                            "type": "number"
                        },
                        "cov27": {
                            "type": "number"
                        },
                        "cov28": {
                            "type": "number"
                        },
                        "cov29": {
                            "type": "number"
                        },
                        
                        "cov33": {
                            "type": "number"
                        },
                        "cov34": {
                            "type": "number"
                        },
                        "cov35": {
                            "type": "number"
                        },
                        "cov36": {
                            "type": "number"
                        },
                        "cov37": {
                            "type": "number"
                        },
                        "cov38": {
                            "type": "number"
                        },
                        "cov39": {
                            "type": "number"
                        },
                        
                        "cov44": {
                            "type": "number"
                        },
                        "cov45": {
                            "type": "number"
                        },
                        "cov46": {
                            "type": "number"
                        },
                        "cov47": {
                            "type": "number"
                        },
                        "cov48": {
                            "type": "number"
                        },
                        "cov49": {
                            "type": "number"
                        },
                        
                        "cov55": {
                            "type": "number"
                        },
                        "cov56": {
                            "type": "number"
                        },
                        "cov57": {
                            "type": "number"
                        },
                        "cov58": {
                            "type": "number"
                        },
                        "cov59": {
                            "type": "number"
                        },
                        
                        "cov66": {
                            "type": "number"
                        },
                        "cov67": {
                            "type": "number"
                        },
                        "cov68": {
                            "type": "number"
                        },
                        "cov69": {
                            "type": "number"
                        },
                        "cov77": {
                            "type": "number"
                        },
                        "cov78": {
                            "type": "number"
                        },
                        "cov79": {
                            "type": "number"
                        },
                        "cov88": {
                            "type": "number"
                        },
                        "cov89": {
                            "type": "number"
                        },
                        "cov99": {
                            "type": "number"
                        },
                    },
                    "required": [
                        "cov00",
                        "cov01",
                        "cov02",
                        "cov03",
                        "cov04",
                        "cov05",
                        "cov11",
                        "cov12",
                        "cov13",
                        "cov14",
                        "cov15",
                        "cov22",
                        "cov23",
                        "cov24",
                        "cov25",
                        "cov33",
                        "cov34",
                        "cov35",
                        "cov44",
                        "cov45",
                        "cov55"
                    ]
                },
                "elements": {
                    # ------------------------------------------
                    # elements Specification
                    "description" : "Best fit values for the cartesian orbital elements.",
                    # ------------------------------------------
                    "type": "object",
                    "properties": {
                        "x": {
                            "type": "number"
                        },
                        "y": {
                            "type": "number"
                        },
                        "z": {
                            "type": "number"
                        },
                        "vx": {
                            "type": "number"
                        },
                        "vy": {
                            "type": "number"
                        },
                        "vz": {
                            "type": "number"
                        }
                    },
                    "required": [
                        "vx",
                        "vy",
                        "vz",
                        "x",
                        "y",
                        "z"
                    ]
                },
                "non_grav_coefficients": {
                    # ------------------------------------------
                    # non_grav_coefficients Specification
                    "description" : "Best fit values for any non-gravitational elements employed in the fit.",
                    # ------------------------------------------
                    "type": "object",
                    "properties": {
                        "yarkovsky_coeff": {
                            "type": [
                                "null",
                                "number"
                            ]
                        },
                        "srp_coeff": {
                            "type": [
                                "null",
                                "number"
                            ]
                        },
                        "A1_coeff": {
                            "type": [
                                "null",
                                "number"
                            ]
                        },
                        "A2_coeff": {
                            "type": [
                                "null",
                                "number"
                            ]
                        },
                        "A3_coeff": {
                            "type": [
                                "null",
                                "number"
                            ]
                        },
                        "DT_coeff": {
                            "type": [
                                "null",
                                "number"
                            ]
                        }
                    },
                    "required": [
                        "yarkovsky_coeff"
                        "srp_coeff",
                        "A1_coeff",
                        "A2_coeff",
                        "A3_coeff",
                        "DT_coeff",
                    ]
                }
            },
            "required": [
                "eigval",
                "rms",
                "elements",
                "non_grav_coefficients"
                "covariance",
                "element_units",
                "non_grav_units",
            ]
        },
        "COM": {
            # ------------------------------------------
            # Cometary Element Specification
            "description" : "Description of the best-fit orbit based on the 'cometary' coordinate system (plus any non-gravs). Contains the best-fit orbit and covariance matrix.",
            # ------------------------------------------
            "properties": {
                "element_units" : {
                    # ------------------------------------------
                    # element_units Specification
                    "description" : "Physical Units associated with cartesian orbital elements ",
                    # ------------------------------------------
                    "type": "object",
                    "properties": {
                        "posn": {
                            "type": "string",
                            "enum": ["au"]
                        },
                        "ang": {
                            "type": "string",
                            "enum": ["deg"]
                        },
                    },
                    "required": ["posn","ang"]
                },
                "non_grav_units" : {
                    # ------------------------------------------
                    # non_grav_units Specification
                    "description" : "Physical Units associated with non-gravitational fit-parameters ",
                    # ------------------------------------------
                    "type": "object",
                    "properties": {
                        "yarkovsky": {
                            "type": "string",
                            "enum": ["???"]
                        },
                        "srp": {
                            "type": "string",
                            "enum": ["???"]
                        },
                        "A1": {
                            "type": "string",
                            "enum": ["???"]
                        },
                        "A2": {
                            "type": "string",
                            "enum": ["???"]
                        },
                        "A3": {
                            "type": "string",
                            "enum": ["???"]
                        },
                        "DT": {
                            "type": "string",
                            "enum": ["???"]
                        },                    },
                    "required": [   "yarkovsky",
                                    "srp",
                                    "A1",
                                    "A2",
                                    "A3",
                                    "DT"]
                },
                "eigval": {
                    # ------------------------------------------
                    # eigval Specification
                    "description" : "Eigenvalues for the cometary orbital elements (and any non-gravitational parameters). Of length 6 if gravity-only, or 7-10 if we have non-gravs.",
                    # ------------------------------------------
                    "type": "array",
                    "items": {
                        "type": "number"
                    }
                },
                "rms": {
                    # ------------------------------------------
                    # rms Specification
                    "description" : "RMS values for the cartesian orbital elements (and any non-gravitational parameters). Of length 6 if gravity-only, or 7-10 if we have non-gravs",
                    # ------------------------------------------
                    "type": "array",
                    "items": {
                        "type": "number"
                    }
                },
                "covariance": {
                    # ------------------------------------------
                    # covariance Specification
                    "description" : "Covariance matrix elements (upper triangular) for the cartesian orbital elements (and any non-gravitational parameters). Reconstructed square matrix is of size 6x6 if gravity-only, or 7x7 -to- 10x10 if we have non-grav parameters.",
                    # ------------------------------------------
                    "type": "object",
                    "properties": {
                        "cov00": {
                            "type": "number"
                        },
                        "cov01": {
                            "type": "number"
                        },
                        "cov02": {
                            "type": "number"
                        },
                        "cov03": {
                            "type": "number"
                        },
                        "cov04": {
                            "type": "number"
                        },
                        "cov05": {
                            "type": "number"
                        },
                        "cov06": {
                            "type": "number"
                        },
                        "cov07": {
                            "type": "number"
                        },
                        "cov08": {
                            "type": "number"
                        },
                        "cov09": {
                            "type": "number"
                        },

                        
                        "cov11": {
                            "type": "number"
                        },
                        "cov12": {
                            "type": "number"
                        },
                        "cov13": {
                            "type": "number"
                        },
                        "cov14": {
                            "type": "number"
                        },
                        "cov15": {
                            "type": "number"
                        },
                        "cov16": {
                            "type": "number"
                        },
                        "cov17": {
                            "type": "number"
                        },
                        "cov18": {
                            "type": "number"
                        },
                        "cov19": {
                            "type": "number"
                        },

                        "cov22": {
                            "type": "number"
                        },
                        "cov23": {
                            "type": "number"
                        },
                        "cov24": {
                            "type": "number"
                        },
                        "cov25": {
                            "type": "number"
                        },
                        "cov26": {
                            "type": "number"
                        },
                        "cov27": {
                            "type": "number"
                        },
                        "cov28": {
                            "type": "number"
                        },
                        "cov29": {
                            "type": "number"
                        },
                        
                        "cov33": {
                            "type": "number"
                        },
                        "cov34": {
                            "type": "number"
                        },
                        "cov35": {
                            "type": "number"
                        },
                        "cov36": {
                            "type": "number"
                        },
                        "cov37": {
                            "type": "number"
                        },
                        "cov38": {
                            "type": "number"
                        },
                        "cov39": {
                            "type": "number"
                        },
                        
                        "cov44": {
                            "type": "number"
                        },
                        "cov45": {
                            "type": "number"
                        },
                        "cov46": {
                            "type": "number"
                        },
                        "cov47": {
                            "type": "number"
                        },
                        "cov48": {
                            "type": "number"
                        },
                        "cov49": {
                            "type": "number"
                        },
                        
                        "cov55": {
                            "type": "number"
                        },
                        "cov56": {
                            "type": "number"
                        },
                        "cov57": {
                            "type": "number"
                        },
                        "cov58": {
                            "type": "number"
                        },
                        "cov59": {
                            "type": "number"
                        },
                        
                        "cov66": {
                            "type": "number"
                        },
                        "cov67": {
                            "type": "number"
                        },
                        "cov68": {
                            "type": "number"
                        },
                        "cov69": {
                            "type": "number"
                        },
                        "cov77": {
                            "type": "number"
                        },
                        "cov78": {
                            "type": "number"
                        },
                        "cov79": {
                            "type": "number"
                        },
                        "cov88": {
                            "type": "number"
                        },
                        "cov89": {
                            "type": "number"
                        },
                        "cov99": {
                            "type": "number"
                        },
                    },
                    "required": [ # Larger than 6 coefficients is "optional"
                        "cov00",
                        "cov01",
                        "cov02",
                        "cov03",
                        "cov04",
                        "cov05",
                        "cov11",
                        "cov12",
                        "cov13",
                        "cov14",
                        "cov15",
                        "cov22",
                        "cov23",
                        "cov24",
                        "cov25",
                        "cov33",
                        "cov34",
                        "cov35",
                        "cov44",
                        "cov45",
                        "cov55"
                    ]
                },
                "elements": {
                    # ------------------------------------------
                    # elements Specification
                    "description" : "Best fit values for the cometary orbital elements.",
                    # ------------------------------------------
                    "type": "object",
                    "properties": {
                        "q": {
                            "type": "number"
                        },
                        "e": {
                            "type": "number"
                        },
                        "i": {
                            "type": "number"
                        },
                        "node": {
                            "type": "number"
                        },
                        "argperi": {
                            "type": "number"
                        },
                        "peri_time": {
                            "type": "number"
                        }
                    },
                    "required": [
                        "q",
                        "e",
                        "i",
                        "node",
                        "argperi",
                        "peri_time"
                    ]
                },
                "non_grav_coefficients": {
                    # ------------------------------------------
                    # non_grav_coefficients Specification
                    "description" : "Best fit values for any non-gravitational elements employed in the fit.",
                    # ------------------------------------------
                    "type": "object",
                    "properties": {
                        "yarkovsky_coeff": {
                            "type": [
                                "null",
                                "number"
                            ]
                        },
                        "srp_coeff": {
                            "type": [
                                "null",
                                "number"
                            ]
                        },
                        "A1_coeff": {
                            "type": [
                                "null",
                                "number"
                            ]
                        },
                        "A2_coeff": {
                            "type": [
                                "null",
                                "number"
                            ]
                        },
                        "A3_coeff": {
                            "type": [
                                "null",
                                "number"
                            ]
                        },
                        "DT_coeff": {
                            "type": [
                                "null",
                                "number"
                            ]
                        }
                    },
                    "required": [
                        "yarkovsky_coeff"
                        "srp_coeff",
                        "A1_coeff",
                        "A2_coeff",
                        "A3_coeff",
                        "DT_coeff",
                    ]
                }
            },
            "required": [
                "covariance",
                "eigval",
                "elements",
                "rms",
                "element_units",
                "non_grav_units",
                "non_grav_coefficients"
            ]
        },
        "software_data" : {
            # ------------------------------------------
            # software_data Specification
            "description" : "Details of the software used to perform orbital fit",
            # ------------------------------------------
            "properties": {
                "software_name": {
                    "type": "string",
                    "enum": ["orbfit"]
                },
                "software_version": { # E.g. v.1.0.a.2
                    "type": "string"
                }
                "run_datetime": { # When was this file made?
                    "type": "string"
                },
            "required": [
                "software_name",
                "software_version",
                "run_datetime"
            ]
        },
        
        "system_data": {
            # ------------------------------------------
            # system_data Specification
            "description" : "Ephemeris model assumed when integrating the motion of the object, and the frame of reference used to specify the best-fit orbital elements. ",
            # ------------------------------------------
            "properties": {
                "eph": {
                    # ------------------------------------------
                    # eph Specification
                    "description" : "The ephemeris model used in the orbit-fit, E.g. DE431",
                    # ------------------------------------------
                    "type": "string",
                    "enum": ["DE431","DE441"]
                },
                "refsys": {
                    # ------------------------------------------
                    # refsys Specification
                    "description" : "The frame of reference for the best-fit orbital elements",
                    # ------------------------------------------
                    "type": "string",
                    "enum": ["Equatorial","Ecliptic"]
                }
                "refframe": {
                    # ------------------------------------------
                    # refframe Specification
                    "description" : "The frame of reference for the best-fit orbital elements",
                    # ------------------------------------------
                    "type": "string",
                    "enum": ["ICRF"]
                },
                "force_model": {
                    # ------------------------------------------
                    # refframe Specification
                    "description" : "The planetary / asteroidal perturbers that were used in the orbit-fit. [need to decide exactly how to popuulate: url-link?]",
                    # ------------------------------------------
                    "type": "string",
                    "enum": ["????"]
                },
                "required": [
                    "eph",
                    "refsys",
                    "refframe",
                    "force_model"
            ]
        },
        "designation_data": {
            # ------------------------------------------
            # designation_data Specification
            "description" : "The designations, numbers and names that may be associated with the object",
            # ------------------------------------------
            "properties": {
                "permid": {
                    "type": "string"
                },
                "packed_primary_provisional_designation": {
                    "type": "string"
                },
                "unpacked_primary_provisional_designation": {
                    "type": "string"
                },
                "orbfit_name": {
                    "type": "string"
                },
                "packed_secondary_provisional_designations": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    }
                },
                "unpacked_secondary_provisional_designations": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    }
                },
                "iau_name": {
                    "type": "string"
                }
            },
            "required": [
                "iau_name",
                "orbfit_name",
                "packed_primary_provisional_designation",
                "permid",
                "unpacked_primary_provisional_designation",
                "packed_secondary_provisional_designations",
                "unpacked_secondary_provisional_designations"
            ]
        },
        "orbit_fit_statistics":{
            # ------------------------------------------
            # orbit_fit_statistics Specification
            "description" : "Summary fit statistics associated with the best-fit orbit, the observations used, etc",
            # ------------------------------------------
            "properties": {
                "sig_to_noise_ratio" : {    #SNR of the orbital parameters
                    "type": "array",
                    "items": {
                        "type": "number"
                    },
                "snr_below_3"         : { #True if any value in the SNR list is <3, False otherwise
                    "type": "boolean"
                },
                "snr_below_1:"        : { #True if any value in the SNR list is <1, False otherwise
                    "type": "boolean"
                },
                "U_param"             : { #U parameter per https://minorplanetcenter.net/iau/info/UValue.html
                        "type": "number"
                },
                "score1"              : { # 1st Meaningless score for numbering ...
                        "type": "number"
                },
                "score2"              : { # 2nd Meaningless score for numbering ...
                        "type": "number"
                },
                "orbit_quality"      : {      #Orbit quality: good, poor, unreliable, no orbit (def = 'good')
                    "type": "string"
                },
                "normalized_RMS"     : {      #Normalized RMS (def = 0)
                    "type": "number"
                },
                "not_normalized_RMS" : {      #Not normalized RMS (def=0)
                    "type": "number"
                },
                "nobs_total"       : {      #Total number of all observations (optical + radar) available
                    "type": "number"
                },
                "nobs_total_sel"   : {      #Total number of all observations (optical + radar) selected
                    "type": "number"
                },
                "nobs_optical"       : {    #Total number of optical observations available
                    "type": "number"
                },
                "nobs_optical_sel"   : {    #Total number of optical observations selected
                    "type": "number"
                },
                "nobs_radar"       : {      #Total number of radar observations available
                    "type": "number"
                },
                "nobs_radar_sel"   : {      #Total number of radar observations selected
                    "type": "number"
                },
                "arc_length_total"  : {      #Arc length over nobs_total
                    "type": "number"
                },
                "arc_length_sel"    : {      #Arc length over nobs_total_sel
                    "type": "number"
                },
                "nopp"               : {      #Number of oppositions
                    "type": "number"
                },
                "numparams": {                # Number of parameters used for fit: E.g. 6-orbital params plus N-non_grav params
                    "type": "integer"
                },

        },

        "nongrav_data": {
            # ------------------------------------------
            # nongrav Specification
            "description" : "Booleans to indicate whether any non-gravitational parameters are used in the orbit-fit. The actual fitted values and their covariance properties are reported within the 'CAR' and 'COT' parameter sections.",
            # ------------------------------------------
            "properties": {
                "non_gravs": {
                    # ------------------------------------------
                    # non_gravs Specification
                    "description" : "Boolean to indicate whether any non-gravitational parameters are used in the orbit-fit.",
                    # ------------------------------------------
                    "type": "boolean"
                },
                "non_grav_booleans": {
                    # ------------------------------------------
                    # non_grav_booleans Specification
                    "description" : "Booleans to indicate which specific non-gravitational parameters are used in the orbit-fit.",
                    # ------------------------------------------
                    "type": "object",
                    "properties": {
                        "yarkovsky": {
                            "type": "boolean"
                        },
                        "srp": {
                            "type": "boolean"
                        },
                        "marsden": {
                            "type": "boolean"
                        },
                        "yc": { # Yoemans & Chodas
                            "type": "boolean"
                        },
                        "yabushita": {
                            "type": "boolean"
                        },
                        "A1": {
                            "type": "boolean"
                        },
                        "A2": {
                            "type": "boolean"
                        },
                        "A3": {
                            "type": "boolean"
                        },
                        "DT": {
                            "type": "boolean"
                        }
                    },
                    "required": [
                        "yarkovsky",
                        "srp",
                        "marsden",
                        "yc",
                        "yabushita",
                        "A1",
                        "A2",
                        "A3",
                        "DT"
                    ]
                },
                
            },
            "required": [
                "non_gravs",
                "non_grav_booleans",
            ]
        },
        "magnitude_data": {
            # ------------------------------------------
            # refsys Specification
            "description" : "The absolute magnitude, H, and slope parameter, G, information derived from the fitted orbit in combination with the observed apparent magnitudes. ",
            # ------------------------------------------
            "properties": {
                "H": {
                    "type": "number"
                },
                "G": {
                    "type": "number"
                },
                "G1": {
                    "type": "number"
                },
                "G2": {
                    "type": "number"
                },
                "G12": {
                    "type": "number"
                },
                "photometric_model" : {
                    "type": "string",
                     "enum": ["????"]
               }
            },
            "required": [
                "photometric_model",
                "H",
                "G"    # <<-- Make this be *Either* G/G1/G2/G12
                ]
        },
        "epoch_data": {
            # ------------------------------------------
            # epoch_data Specification
            "description" : "Data concerning the orbit epoch: I.e. The date at which the best-fit orbital coordinates are correct",
            # ------------------------------------------
            "properties": {
                "timesystem": {
                    "type": "string",
                     "enum": ["TDB","TT"]
                },
                "timeform": {
                    "type": "string",
                    "enum": ["JD","MJD"]
                },
                "epoch": {
                    "type": "number"
                }
            },
            "required": [
                "epoch",
                "timesystem",
                "timeform"
            ]
        }
        "moid_data": {
            # ------------------------------------------
            # moid_data Specification
            "description" : "Calculated MOIDs (Minimum Orbital Interception Distances) at Epoch",
            # ------------------------------------------
            "properties": {
                "Venus": {
                    "type": "number"
                },
                "Earth": {
                    "type": "number"
                },
                "Mars": {
                    "type": "number"
                },
                "Jupiter": {
                    "type": "number"
                }
                "moid_units" :{
                    "type": "string",
                    "enum": ["au"]
                },
            },
            "required": [
                "Earth",
                "moid_units"
            ]
        }
        "categorization": {
            # ------------------------------------------
            # categorization Specification
            "description" : "Various different ways to categorize / sub-set orbit / object types",
            # ------------------------------------------
            "properties": {
                "object_type_str": {      # Minor-Planet / Comet / Dual-Status / Binary MP / ...
                    "type": "string"
                },
                "object_type_int": {      #     0            10       20          1
                    "type": "number"
                },
                "orbit_type_str": {       # NEAs / MBAs / TNOs / ...
                    "type": "string"
                },
                "orbit_type_int": {       # 0 /1/2/3/4
                    "type": "number"
                },
                "orbit_subtype_str": {    # Apollo / Amor / ...
                    "type": "string"
                },
                "orbit_subtype_int": {    # ...
                    "type": "number"
                },
                "parent_planet_str" : {  # For Nat-Sats
                    "type": "string"
                }
                "parent_planet_int" : {  # For Nat-Sats
                    "type": "number"
                }
            }
            },
            "required": [
                "object_type_str",
                "object_type_int",
                "orbit_type_str",
                "orbit_type_int",
                "orbit_subtype_str",
                "orbit_subtype_int"
            ]
        }
    },

}



