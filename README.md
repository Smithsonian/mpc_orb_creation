# mpc_orb_creation

Code to create validation schema for orbfit-jsons and mpcorb-jsons

This repo is intended for internal MPC usage. 

It is likely to only work on specific MPC machines with specific internal libraries available (e.g. "marsden") 

There is a partner repo, "...mpc_orb" that contains the code intended for public use (validating and parsing mpc_orb.json files)

## Repo Structure ...

### demos
Demonstrations of code usage 
		
### json_files	
All of the json files used through the repo, both for schema creation and for tests, demos, etc

### mpc_orb		
The main code base

### tests
Some tests. Very little implmented at present



## Main Code ...  

See mpc_orb_creation/mpc_orb_creation/README.md for a more detailed description of the contained code

(i) Create validation schema for orbfit-jsons and mpcorb-jsons

It is expected that this functionality will be used rarely and only internally by the MPC. 
These are the functions required to take us from ~nothing, to having fully specified schema for all file types

The code that performs these taskss can be found in "mpc_orb_creation/mpc_orb_creation/bootstrap.py" and "mpc_orb_creation/mpc_orb_creation/convert.py"


(ii) Provide validation functions

 - It is expected that these validation functionalities will typically be used as part of the "parse" functions described in (iii) below. I.e. it is *not* expected that the end-user will directly access the validation functions themselves, but rather, the validation functions are called under-the-hood by the mpc_orb/parse.py routines. 

 - The code that performs the validation can be found in mpc_orb_creation/mpc_orb_creation/schema.py

 - Overlaps with the code available in the public mpc_orb repo

 - Development note: need CI-type functionality to ensure that mpc_orb_creation & mpc_orb are kept in sync
   

