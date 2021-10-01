"""
mpc_orb/schema.py
 - Code to *create* the required three types of schema file using supplied defining json-files
 - Code to *validate* a candidate json-file against a schema file

Author(s)
MJP
"""

# Import third-party packages
import json
from jsonschema import validate
import genson
from genson import SchemaBuilder
from os.path import join, dirname, abspath, isfile


# local imports
# -----------------------
import interpret
from filepaths import filepath_dict


# IO functions
# -----------------------
def load_json( json_filepath ):
    """ """
    with open( json_filepath ) as f:
        return json.load(f)
        
def save_json( json_filepath , data_dict ):
    """ Being very careful here as any jsons saved by this module will be the main standardizing schema """
    if isfile(json_filepath):
        raise Exception(f"The important json file {json_filepath} already exists ... To prevent accidental over-writes, this routine will go no further ... ")
    else:
        with open( json_filepath , 'w' ) as f:
            json.dump(data_dict , f , indent=4)


# Validation functions
# -----------------------
def validate_orbfit_general(arg):
    """
    Test whether json is a valid example of an orbfit-felfile json
    Input can be json-filepath, or dictionary of json contents
    """

    # interpret the input (allow dict or json-filepath)
    orbfit_dict, input_filepath = interpret.interpret(arg)
    
    # validate
    # NB # If no exception is raised by validate(), the instance is valid.
    validate(instance=orbfit_dict, schema=load_json( filepath_dict['orbfit_general_schema'] ))

    return True

def validate_orbfit_conversion( arg ):
    """
    Test whether json is a valid example of an orbfit-felfile json that is suitable for conversion to mpcorb-format
    Input can be json-filepath, or dictionary of json contents
    """

    # interpret the input (allow dict or json-filepath)
    data, input_filepath = interpret.interpret(arg)

    # validate
    # NB # If no exception is raised by validate(), the instance is valid.
    validate(instance=data, schema=load_json( filepath_dict['orbfit_conversion_schema'] ))
    
    return True

def validate_mpcorb( arg ):
    """
    Test whether json is a valid example of an mpcorb json
    Input can be json-filepath, or dictionary of json contents
    """

    # interpret the input (allow dict or json-filepath)
    data, input_filepath = interpret.interpret(arg)

    # validate
    # NB # If no exception is raised by validate(), the instance is valid.
    validate(instance=data, schema=load_json( filepath_dict['mpcorb_schema'] ))
    
    return True


# Schema Creation functions
# -----------------------
def get_schema_from_builder(list_of_sample_dicts):
    """
    This code uses the "genson" package to create a json "schema" dictionary
    The schema is created by reading from a list of defining sample dicts,
    and using those as the basis for the schema.
    """

    # Instantiate Genson object ...
    # https://pypi.org/project/genson/
    builder = SchemaBuilder()
    builder.add_schema({"type": "object", "properties": {}})

    # Add data from defining sample file
    assert isinstance(list_of_sample_dicts , list)
    for n, d in enumerate(list_of_sample_dicts):
        print(n)
        print(d)
        print()
        assert isinstance(d, dict)
        builder.add_object(d)

    # Convert to schema
    return builder.to_schema()

def create_orbfit_felfile_schema_from_defining_sample_json():
    """
    Use predefined sample json(s) as the basis to construct json schema for the orbfit felfiles
    
    NB(1) Some "by-hand" modifications are done to the basic schema generated from the defining sample
    NB(2) Two different schema are created ( one general, one conversion-specific)
    The results are saved-to, and thus define, the standard schema files
    
    *** IT IS EXPECTED THAT THIS WILL BE USED EXTREMELY RARELY ONCE WE HAVE EVERYTHING SET-UP ***
    """

    # load defining sample
    list_of_sample_dicts_general = [load_json( _ ) for _ in filepath_dict['orbfit_defining_sample_general'] ]
    list_of_sample_dicts_convert = [load_json( _ ) for _ in filepath_dict['orbfit_defining_sample_convert'] ]

    # instantiate "builder" & use to convert json-dict to an (initial) schema
    schema_dict_general = get_schema_from_builder(list_of_sample_dicts_general)
    schema_dict_convert = get_schema_from_builder(list_of_sample_dicts_convert)

    # do orbfit-specific modifications
    schema_dict_general  = do_orbfit_general_schema_mods(schema_dict_general)
    schema_dict_convert  = do_orbfit_conversion_schema_mods(schema_dict_convert)

    # Save schema-dict to file
    save_json( filepath_dict['orbfit_general_schema'] ,    schema_dict_general )
    save_json( filepath_dict['orbfit_conversion_schema'] , schema_dict_convert )

    return True

def do_orbfit_general_schema_mods(schema_dict):
    """
    No schema mods currently implemented
    Additional modifications likely to be required to refine the definition/schema
    """
    return schema_dict

def do_orbfit_conversion_schema_mods(schema_dict):
    """
    Minimal schema mods currently implemented
    Additional modifications likely to be required to refine the definition/schema
    """
    
    # (1) Require "CAR" and "COM" coords, other coords are optional
    schema_dict["required"] = [ "CAR" , "COM" ]
    return schema_dict

def create_mpcorb_schema_from_defining_sample_json():
    """
    Use a predefined sample json as the basis to construct a json schema for the mpc_orb files
    Note that some "by-hand" modifications are done to the basic schema generated from the defining sample
    The result is saved and thus defines the standard schema file
    *** IT IS EXPECTED THAT THIS WILL BE USED EXTREMELY RARELY ***
    """

    # load defining sample
    list_of_sample_dicts = [load_json( _ ) for _ in filepath_dict['mpcorb_defining_sample'] ]

    # instantiate "builder" & use to convert json-dict to an (initial) schema
    schema_dict = get_schema_from_builder(list_of_sample_dicts)

    # do mpc_orb-specific modifications
    schema_dict = do_mpcorb_schema_mods(schema_dict)
    
    # Save schema-dict to file
    save_json( filepath_dict['mpcorb_schema'] , schema_dict )
    
    return True

def do_mpcorb_schema_mods(schema_dict):
    """
    Minimal schema mods currently implemented
    Additional modifications likely to be required to refine the definition/schema
    """
        
    # Recursively walk through the levels of the schema, adding
    #     requirements & descriptions where possible
    walk(schema_dict, mpcorb_description_dict)

    # Any other alterations to be made ???

    return schema_dict

def walk( schema_d , description_d ):
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
#
# NB: I am also using this as a means to define an "extended_description: field
# - This will *not* be used in the json schema, but will be used in documentation
#
# This dictionary will have to be iteratively evolved if/when we change the
# defining schema
'''
mpcorb_description_dict = {

    # ------------------------------------------
    # Top level Specification
    # N.B. Explicitly editing requirements so that we
    # require "CAR" and "COM" coords, leaving other coords to be optional
    "required": [ "CAR","COM" ]
    "description" : "JSON best-fit orbit for single object",
    "extended_description" : "Standardized orbit exchange format. Designed to communicate the best-fit orbit for a single minor planet or comet. ",
    # ------------------------------------------

    "properties": {
        "CAR": {

            # ------------------------------------------
            # Cartesian Element Specification
            "description" : "Cartesian Orbital Elements",
            "extended_description" : "Description of the best-fit orbit using cartesian coordinates. Contains the best-fit orbit and covariance matrix.",
            # ------------------------------------------

            "properties": {
                "eigval": {
                    "type": "array",
                    "items": {
                        "type": "number"
                    }
                },
                "numparams": {
                    "type": "integer"
                },
                "rms": {
                    "type": "array",
                    "items": {
                        "type": "number"
                    }
                },
                "covariance": {
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
                        "cov33": {
                            "type": "number"
                        },
                        "cov34": {
                            "type": "number"
                        },
                        "cov35": {
                            "type": "number"
                        },
                        "cov44": {
                            "type": "number"
                        },
                        "cov45": {
                            "type": "number"
                        },
                        "cov55": {
                            "type": "number"
                        },
                        "cov06": {
                            "type": "number"
                        },
                        "cov07": {
                            "type": "number"
                        },
                        "cov16": {
                            "type": "number"
                        },
                        "cov17": {
                            "type": "number"
                        },
                        "cov26": {
                            "type": "number"
                        },
                        "cov27": {
                            "type": "number"
                        },
                        "cov36": {
                            "type": "number"
                        },
                        "cov37": {
                            "type": "number"
                        },
                        "cov46": {
                            "type": "number"
                        },
                        "cov47": {
                            "type": "number"
                        },
                        "cov56": {
                            "type": "number"
                        },
                        "cov57": {
                            "type": "number"
                        },
                        "cov66": {
                            "type": "number"
                        },
                        "cov67": {
                            "type": "number"
                        },
                        "cov77": {
                            "type": "number"
                        }
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
                "element_order": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    }
                }
            },
            "required": [
                "covariance",
                "eigval",
                "element_order",
                "elements",
                "numparams",
                "rms"
            ]
        },
        "COM": {
            # ------------------------------------------
            # Cometary Element Specification
            "description" : "Cometary Orbital Elements",
            "extended_description" : "Description of the best-fit orbit using 'cometary' coordinates. Contains the best-fit orbit and covariance matrix.",
            # ------------------------------------------
            "properties": {
                "eigval": {
                    "type": "array",
                    "items": {
                        "type": "number"
                    }
                },
                "numparams": {
                    "type": "integer"
                },
                "rms": {
                    "type": "array",
                    "items": {
                        "type": "number"
                    }
                },
                "covariance": {
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
                        "cov33": {
                            "type": "number"
                        },
                        "cov34": {
                            "type": "number"
                        },
                        "cov35": {
                            "type": "number"
                        },
                        "cov44": {
                            "type": "number"
                        },
                        "cov45": {
                            "type": "number"
                        },
                        "cov55": {
                            "type": "number"
                        },
                        "cov06": {
                            "type": "number"
                        },
                        "cov07": {
                            "type": "number"
                        },
                        "cov16": {
                            "type": "number"
                        },
                        "cov17": {
                            "type": "number"
                        },
                        "cov26": {
                            "type": "number"
                        },
                        "cov27": {
                            "type": "number"
                        },
                        "cov36": {
                            "type": "number"
                        },
                        "cov37": {
                            "type": "number"
                        },
                        "cov46": {
                            "type": "number"
                        },
                        "cov47": {
                            "type": "number"
                        },
                        "cov56": {
                            "type": "number"
                        },
                        "cov57": {
                            "type": "number"
                        },
                        "cov66": {
                            "type": "number"
                        },
                        "cov67": {
                            "type": "number"
                        },
                        "cov77": {
                            "type": "number"
                        }
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
                        "argperi",
                        "e",
                        "i",
                        "node",
                        "peri_time",
                        "q"
                    ]
                },
                "element_order": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    }
                }
            },
            "required": [
                "covariance",
                "eigval",
                "element_order",
                "elements",
                "numparams",
                "rms"
            ]
        },
        "COT": {
            # ------------------------------------------
            # ?????? Element Specification
            "description" : "?????? Orbital Elements",
            "extended_description" : "Description of the best-fit orbit using '??????' coordinates. Contains the best-fit orbit and covariance matrix.",
            # ------------------------------------------
            "properties": {
                "eigval": {
                    "type": "array",
                    "items": {
                        "type": "number"
                    }
                },
                "numparams": {
                    "type": "integer"
                },
                "rms": {
                    "type": "array",
                    "items": {
                        "type": "number"
                    }
                },
                "covariance": {
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
                        "cov33": {
                            "type": "number"
                        },
                        "cov34": {
                            "type": "number"
                        },
                        "cov35": {
                            "type": "number"
                        },
                        "cov44": {
                            "type": "number"
                        },
                        "cov45": {
                            "type": "number"
                        },
                        "cov55": {
                            "type": "number"
                        }
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
                        "true_anomaly": {
                            "type": "number"
                        }
                    },
                    "required": [
                        "argperi",
                        "e",
                        "i",
                        "node",
                        "q",
                        "true_anomaly"
                    ]
                },
                "element_order": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    }
                }
            }
        },
        "EQU": {
            # ------------------------------------------
            # ?????? Element Specification
            "description" : "?????? Orbital Elements",
            "extended_description" : "Description of the best-fit orbit using '??????' coordinates. Contains the best-fit orbit and covariance matrix.",
            # ------------------------------------------
            "properties": {
                "eigval": {
                    "type": "array",
                    "items": {
                        "type": "number"
                    }
                },
                "numparams": {
                    "type": "integer"
                },
                "rms": {
                    "type": "array",
                    "items": {
                        "type": "number"
                    }
                },
                "covariance": {
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
                        "cov33": {
                            "type": "number"
                        },
                        "cov34": {
                            "type": "number"
                        },
                        "cov35": {
                            "type": "number"
                        },
                        "cov44": {
                            "type": "number"
                        },
                        "cov45": {
                            "type": "number"
                        },
                        "cov55": {
                            "type": "number"
                        },
                        "cov06": {
                            "type": "number"
                        },
                        "cov07": {
                            "type": "number"
                        },
                        "cov16": {
                            "type": "number"
                        },
                        "cov17": {
                            "type": "number"
                        },
                        "cov26": {
                            "type": "number"
                        },
                        "cov27": {
                            "type": "number"
                        },
                        "cov36": {
                            "type": "number"
                        },
                        "cov37": {
                            "type": "number"
                        },
                        "cov46": {
                            "type": "number"
                        },
                        "cov47": {
                            "type": "number"
                        },
                        "cov56": {
                            "type": "number"
                        },
                        "cov57": {
                            "type": "number"
                        },
                        "cov66": {
                            "type": "number"
                        },
                        "cov67": {
                            "type": "number"
                        },
                        "cov77": {
                            "type": "number"
                        }
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
                    "type": "object",
                    "properties": {
                        "a": {
                            "type": "number"
                        },
                        "e_sin_argperi": {
                            "type": "number"
                        },
                        "e_cos_argperi": {
                            "type": "number"
                        },
                        "tan_i/2_sin_node": {
                            "type": "number"
                        },
                        "tan_i/2_cos_node": {
                            "type": "number"
                        },
                        "mean_long": {
                            "type": "number"
                        }
                    },
                    "required": [
                        "a",
                        "e_cos_argperi",
                        "e_sin_argperi",
                        "mean_long",
                        "tan_i/2_cos_node",
                        "tan_i/2_sin_node"
                    ]
                },
                "element_order": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    }
                }
            }
        },
        "KEP": {
            # ------------------------------------------
            # Keplerian Element Specification
            "description" : "Keplerian Orbital Elements",
            "extended_description" : "Description of the best-fit orbit using 'Keplerian' coordinates. Contains the best-fit orbit and covariance matrix.",
            # ------------------------------------------
            "properties": {
                "eigval": {
                    "type": "array",
                    "items": {
                        "type": "number"
                    }
                },
                "numparams": {
                    "type": "integer"
                },
                "rms": {
                    "type": "array",
                    "items": {
                        "type": "number"
                    }
                },
                "covariance": {
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
                        "cov33": {
                            "type": "number"
                        },
                        "cov34": {
                            "type": "number"
                        },
                        "cov35": {
                            "type": "number"
                        },
                        "cov44": {
                            "type": "number"
                        },
                        "cov45": {
                            "type": "number"
                        },
                        "cov55": {
                            "type": "number"
                        },
                        "cov06": {
                            "type": "number"
                        },
                        "cov07": {
                            "type": "number"
                        },
                        "cov16": {
                            "type": "number"
                        },
                        "cov17": {
                            "type": "number"
                        },
                        "cov26": {
                            "type": "number"
                        },
                        "cov27": {
                            "type": "number"
                        },
                        "cov36": {
                            "type": "number"
                        },
                        "cov37": {
                            "type": "number"
                        },
                        "cov46": {
                            "type": "number"
                        },
                        "cov47": {
                            "type": "number"
                        },
                        "cov56": {
                            "type": "number"
                        },
                        "cov57": {
                            "type": "number"
                        },
                        "cov66": {
                            "type": "number"
                        },
                        "cov67": {
                            "type": "number"
                        },
                        "cov77": {
                            "type": "number"
                        }
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
                    "type": "object",
                    "properties": {
                        "a": {
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
                        "mean_anomaly": {
                            "type": "number"
                        }
                    },
                    "required": [
                        "a",
                        "argperi",
                        "e",
                        "i",
                        "mean_anomaly",
                        "node"
                    ]
                },
                "element_order": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    }
                }
            }
        },
        "refsys": {
            # ------------------------------------------
            # refsys Specification
            "description" : "The frame of reference for the best-fit orbital elements",
            "extended_description" : "The frame of reference for the best-fit orbital elements",
            # ------------------------------------------
        },
        "system_data": {
            # ------------------------------------------
            # refsys Specification
            "description" : "Ephemeris and Frame",
            "extended_description" : "Ephemeris model assumed when integrating the motion of the object, and the frame of reference used to specify the best-fit orbital elements. ",
            # ------------------------------------------
            "properties": {
                "eph": {
                    "type": "string"
                },
                "refsys": {
                    "type": "string"
                }
            },
            "required": [
                "eph",
                "refsys"
            ]
        },
        "designation_data": {
            # ------------------------------------------
            # refsys Specification
            "description" : "Object Designation Identifiers",
            "extended_description" : "The designations, numbers and names that may be associated with the object",
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
                    "type": [
                        "integer",
                        "string"
                    ]
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
                "unpacked_primary_provisional_designation"
            ]
        },
        "nongrav_data": {
            # ------------------------------------------
            # refsys Specification
            "description" : "Description of any non-gravitational parameters used in the orbit-fit.",
            "extended_description" : "Description of any non-gravitational parameters used in the orbit-fit. A variety of different non-gravitational models may be employed.",
            # ------------------------------------------
            "properties": {
                "non_gravs": {
                    "type": "boolean"
                },
                "booleans": {
                    "type": "object",
                    "properties": {
                        "yarkovski": {
                            "type": "boolean"
                        },
                        "srp": {
                            "type": "boolean"
                        },
                        "marsden": {
                            "type": "boolean"
                        },
                        "yc": {
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
                        "A1",
                        "A2",
                        "A3",
                        "DT",
                        "marsden",
                        "srp",
                        "yabushita",
                        "yarkovski",
                        "yc"
                    ]
                },
                "coefficients": {
                    "type": "object",
                    "properties": {
                        "yarkovski": {
                            "type": [
                                "null",
                                "number"
                            ]
                        },
                        "srp": {
                            "type": [
                                "null",
                                "number"
                            ]
                        },
                        "A1": {
                            "type": "null"
                        },
                        "A2": {
                            "type": "null"
                        },
                        "A3": {
                            "type": "null"
                        },
                        "DT": {
                            "type": "null"
                        }
                    },
                    "required": [
                        "A1",
                        "A2",
                        "A3",
                        "DT",
                        "srp",
                        "yarkovski"
                    ]
                }
            },
            "required": [
                "booleans",
                "coefficients",
                "non_gravs"
            ]
        },
        "magnitude_data": {
            # ------------------------------------------
            # refsys Specification
            "description" : "H and G Magnitude Data",
            "extended_description" : "The absolute magnitude, H, and slope parameter, G, information derived from the fitted orbit in combination with the observed apparent magnitudes. ",
            # ------------------------------------------
            "properties": {
                "h": {
                    "type": "number"
                },
                "g": {
                    "type": "number"
                }
            },
            "required": [
                "g",
                "h"
            ]
        },
        "epoch_data": {
            # ------------------------------------------
            # refsys Specification
            "description" : "Orbit Epoch",
            "extended_description" : "The date at which the best-fit orbital coordinates are correct",
            # ------------------------------------------
            "properties": {
                "timesystem": {
                    "type": "string"
                },
                "epoch": {
                    "type": "number"
                }
            },
            "required": [
                "epoch",
                "timesystem"
            ]
        }
    },

}


