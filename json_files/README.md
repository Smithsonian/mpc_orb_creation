# json_files

Directory to store various json files.

I intend that there be *no* json files at the top-level

The contained directories have the following intended usages

### (i) defining_sample_json

Various example json files that are defined to be valid.

As per the schema_json description below, there are multiple different sets of defining files. 

These samples are used as the basis to construct the validation schema json files below. 


### (ii) schema_json

The validation schema files constructed from the above defining samples. 

There are three different schema files:

(a) general orbfit : 
 - validation schema for json-versions of an orbfit fel-file

(b) convertable orbfit : 
- validation schema for json-versions of an orbfit fel-file that are intended to be convertible to an mpc_orb file

(c) mpc_orb : 
- validation schema for the mpc's mpc_orb-json format



### (iii) test_jsons
 
 Various example json files to test the code.
 Some are deliberately valid, some deliberately invalid. 
