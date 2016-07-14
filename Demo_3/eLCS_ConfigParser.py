"""
Name:        eLCS_ConfigPars.py
Authors:     Ryan Urbanowicz - Written at Dartmouth College, Hanover, NH, USA
Contact:     ryan.j.urbanowicz@darmouth.edu
Created:     November 1, 2013
Description: Manages the configuration file, by loading it, parsing it and passing values to the 'Constants' module.
             
---------------------------------------------------------------------------------------------------------------------------------------------------------
eLCS: Educational Learning Classifier System - A basic LCS coded for educational purposes.  This LCS algorithm uses supervised learning, and thus is most 
similar to "UCS", an LCS algorithm published by Ester Bernado-Mansilla and Josep Garrell-Guiu (2003) which in turn is based heavily on "XCS", an LCS 
algorithm published by Stewart Wilson (1995).  

Copyright (C) 2013 Ryan Urbanowicz 
This program is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the 
Free Software Foundation; either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABLILITY 
or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program; if not, write to the Free Software Foundation, 
Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA
---------------------------------------------------------------------------------------------------------------------------------------------------------
"""

#Import Required Modules----------
from eLCS_Constants import *
import os
import copy
#---------------------------------

class ConfigParser:
    def __init__(self, filename):
        self.commentChar = '#'
        self.paramChar =  '='
        self.parameters = self.parseConfig(filename) #Parse the configuration file and get all parameters.
        cons.setConstants(self.parameters) #Store run parameters in the 'Constants' module.
        
 
    def parseConfig(self, filename):
        """ Parses the configuration file. """
        parameters = {}
        try:
            f = open(filename)
        except Exception as inst:
            print(type(inst))
            print(inst.args)
            print(inst)
            print('cannot open', filename)
            raise 
        else:
            for line in f:
                #Remove text after comment character.
                if self.commentChar in line:
                    line, comment = line.split(self.commentChar, 1) #Split on comment character, keep only the text before the character
                    
                #Find lines with parameters (param=something)
                if self.paramChar in line:
                    parameter, value = line.split(self.paramChar, 1) #Split on parameter character
                    parameter = parameter.strip() #Strip spaces
                    value = value.strip()
                    parameters[parameter] = value #Store parameters in a dictionary
                    
            f.close()
        
        return parameters
    
    