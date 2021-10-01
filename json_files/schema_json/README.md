# schema_json

Directory to store schema json files..

These schema are designed to be used as the standard against which newly-constructed orbit-jsons are validated. 

These schema files are constructed from the defining json files in the "../defining_sample_json/" directory using the code in the mpc_orb_creation/mpc_orb_creation/bootstrap.py module.

There are three different sets of schema files constructed:

### (i) general

Schema for valid *general* orbfit fel-files (in json format).

### (ii) convert

Schema for valid *convertible* orbfit fel-files (in json format). 
I.e. a file that should successfully convert to the mpc_orb format below

### (iii) mpcorb
 
Schema for valid *mpc_orb* json files.
