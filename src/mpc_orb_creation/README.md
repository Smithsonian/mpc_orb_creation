# mpc_orb/mpc_orb

The main code directory for the mpc_orb package

As of 2021-06-25 most/all of this code can be blamed on MJP

### Contains the following main components

(1) bootstrap.py 
 - The function calls required to take us from ~nothing, to having fully specified schema for all file types
 - This is the means by which the schema are defined / created
 - Expected to be used rarely 
 - Expected to only be used internally by the MPC 
 - Essentially a convenience wrapper around the functionalities in schema.py

(2) convert.py
 - The functions that are required to convert orbfit fel-files (in json format) to an mpc_orb.json
 - Expected to be used frequently to convert the output from orbfit
 - As written it requires modules that are likely to only be available on internal MPC machines

(3) filepaths.py
 - Simple file to define the directory structure & filepaths of this package

(4) interpret.py
 - Convenience func to interpret input arg as some kind of json-related input

(5) parse.py
 - ***THIS CODE DUPLICATES CODE IN mpc_orb : NEED TO DECIDE WHICH TO KEEP AS PRIMARY CODEBASE ***
 - Code to parse an mpc_orb json file
 - Expected to be used frequently to read the contents of an mpc_orb.json
 - Expected to be of use to the external community as well as to the MPC
 - Some simple demos of this code can be found in "demos/Example_parse_mpcorb_json.ipynb" and "demos/demo_parse.py"


(6) schema.py
 - Code to *create* the required three types of schema file using supplied defining json-files
 - Code to *validate* a candidate json-file against a schema file
 - ***THIS CODE IS STILL BEING DEVELOPED***
