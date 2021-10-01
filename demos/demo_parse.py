
# Ensure the code-directory is in the path
from os.path import join, dirname, abspath
import sys
pack_dir  = dirname(abspath('')) # Package directory
code_dir  = join(pack_dir, 'mpc_orb')
sys.path.append(code_dir)


# Import the MPCORB class from the parse module in the mpc_orb directory ...
from parse import MPCORB

# Import the convenience filepath-defn dictionary
from filepaths import filepath_dict

### Define a filepath to an example json file in the mpcorb format
filepath = filepath_dict['test_pass_mpcorb'][0]
print(f'filepath=\n {filepath} \n')

### Instantiate an MPCORB object & use it to parse the above json file
### NB The parsing is done by default "behind-the-scenes" upon instantiation
M = MPCORB(filepath)

# Demonstrate the available variables
print('-'*22)
print('\n Top level variables in MPCORB dictionary ... ')
for k,v in M.__dict__.items():
    print(f'\t{k} : {v}\n')

# Demonstrate the key-value pairs available in the "COM" coordinate dictionary
print('-'*22)
print('\n Variables in COM dictionary ... ')
for k,v in M.COM.items():
    print(f'\t{k} : {v}\n')


# Demonstrate accessing the Cometary orbit elements from the MPCORB object in different ways
# (1) Demonstrate dictionary access
print('\n Dictionary of elements (format = COM = Cometary) ... ')
print(M.COM['elements'] )

# (2) Demonstrate array access
print('\n Array of elements (format = COM = Cometary) ... ')
print(M.COM['element_array'] )

# (2b) Demonstrate print-out of array ordering
print('\n Name of elements (format = COM = Cometary) ... ')
print(M.COM['element_order'] )
