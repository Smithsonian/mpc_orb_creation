"""
mpc_orb/parse.py
 - Code to parse an mpc_orb json file
 - Expected to be used frequently to read the contents of an mpc_orb.json
 - Expected to be of use to the external community as well as to the MPC

Author(s)
This module: MJP
"""

# Third party imports
# -----------------------
import json
from jsonschema import validate
from os.path import join, dirname, abspath
import glob
import os , sys
import numpy as np

# local imports
# -----------------------
import interpret
from schema import validate_mpcorb


class MPCORB():

    def __init__(self, arg=None ):
        """ On init, if some argument is supplied, go ahead and parse ( & validate ) """
        # initialize some to-be-populated variables
        
        
        # process/parse any supplied json-dict
        if arg is not None:
            self.parse( arg)
            
    def parse(self, arg):
        """
        Parse the supplied argument and make various components of the
        input mpc_orb-dictionary available as attributes of this MPCORB object
        
        inputs:
        -------
        arg: dictionary or json-filepath
        
        action:
        --------
        populates MPCORB attributes
        
        """
        # interpret argument to allow filepaths as well as dicts as input)
        json_dict, input_filepath = interpret.interpret(arg)
        
        # validate supplied json-dict against schema
        validate_mpcorb(json_dict)

        # make top-level quantities available as object attributes
        for k,v in json_dict.items(): self.__dict__[k] = v
        
        # provide other useful quantities as attributes
        self._add_various_attributes()
    

    
    def _add_various_attributes(self,):
        """
        provide other useful quantities as attributes
        assumes *parse* has been run
        """
        
        # These coord-types are both required in a valid input mpc_orb.json
        for coord_attr in ["COM", "CAR"]:
            self._populate_coord_components(coord_attr)
            
        # convenience method to return data to be passed into mpc-integrator
        # *** NOT YET IMPLEMENTED ***
        self._populate_integrator_data()
        
        # Is there some other stuff we want to provide as convenient attributes?
        # - astropy time object ?
        # - ... ?
        
        
    def _populate_coord_components(self,coord_attr):
        """ populate various components for specific representation """
        
        # populate square CoV matricees
        self.__dict__[coord_attr]['covariance_array'] = self._generate_square_CoV( coord_attr )

        # populate element array
        self.__dict__[coord_attr]['element_array'] = self._generate_element_array( coord_attr )

        # provide uncertainty (CoV diag)
        self.__dict__[coord_attr]['uncertainty'] = self._generate_uncertainty( coord_attr )
    
    def _generate_square_CoV(self, coord_attr ):
        """ populate square array from triangular elements """
        num_params       = self.__dict__[coord_attr]['numparams']
        covariance_array = np.empty( [num_params,num_params] )
        print('num_params',num_params, 'covariance_array.shape', covariance_array.shape )
        for i in range(num_params):
            for j in range(i,num_params):
                covariance_array[i,j] = covariance_array[j,i] = self.__dict__[coord_attr]['covariance']['cov%d%d' % (i,j)]
                
        return covariance_array

    def _generate_element_array(self,  coord_attr ):
        """ turn element dict into numpy array (with fixed ordering) """
        return np.array( [ self.__dict__[coord_attr]['elements'][key] for key in self.__dict__[coord_attr]['element_order']] )
        
    def _generate_uncertainty(self, coord_attr ):
        """ extract sqrt of diag elements in CoV-arry as uncertainty array """ 
        return np.sqrt( self.__dict__[coord_attr]['covariance_array'].diagonal() )





    '''
    *** TOO CLEVER : NOT SURE IF USEFUL ***
    def _recursive(self,k,v):
        """
        Add all levels of supplied json-dict data as class attributes
        E.g. if json_dict contains
        { ... , key1: { key2:{ key5:True, key6:False }, key3:[], key4:None}, ... }
        then all keys 1-6 will be available as attributes, with ...
        ... key1 & key2 having associated dictionary ,
        ... key3 having an associated list value,
        ... key4, key5 & key6 having single (non-iterable) values

        NB: Doing this requires unique "keys" across all dictionaries

        """

        # Add this attribute to the instance
        self.__dict__[k]=v

        # If dict, then descend
        if isinstance(v, dict):
            for k,_ in v.items():
                self._recursive(k,_)
    '''


    def _populate_integrator_data(self,):
        """
        Rebound-Ephem Integrator wants certain standard inputs
        This function drags together the parts of the data required from the mpcorb-json ...
        and combines it into a single convenient ... dict?
        
        https://github.com/matthewholman/reboundx/blob/holman/examples/ephem_forces/ephem_forces.py
        def integration_function(tstart, tstep, trange,
                         geocentric,
                         n_particles,
                         instate_arr,
                         n_var,
                         invar_part,
                         invar,
                         epsilon = 1e-8)
        """
        pass
        
