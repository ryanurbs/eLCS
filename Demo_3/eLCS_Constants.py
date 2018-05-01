"""
Name:        eLCS_Constants.py
Authors:     Ryan Urbanowicz - Written at Dartmouth College, Hanover, NH, USA
Contact:     ryan.j.urbanowicz@darmouth.edu
Created:     November 1, 2013
Description: Stores and manages all algorithm run parameters, making them accessible anywhere in the rest of the algorithm code by (cons.) .
             
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
import os

class Constants:
    def setConstants(self,par):
        """ Takes the parameters parsed as a dictionary from eLCS_ConfigParser and saves them as global constants. """
        
        # Major Run Parameters -----------------------------------------------------------------------------------------
        self.trainFile = os.path.join(par['datasetDirectory'], par['trainFile'])                    #Saved as text
        if par['testFile'] == 'None':
            self.testFile = 'None'                                                                  #Saved as text
        else:
            self.testFile = os.path.join(par['datasetDirectory'], par['testFile'])                  #Saved as text
        self.originalOutFileName = os.path.join(par['outputDirectory'], str(par['outputFile']))     #Saved as text
        self.outFileName = os.path.join(par['outputDirectory'], str(par['outputFile'])+'_eLCS')     #Saved as text
        self.learningIterations = par['learningIterations']                     #Saved as text
        self.N = int(par['N'])                                                  #Saved as integer
        self.p_spec = float(par['p_spec'])                                      #Saved as float
        
        # Logistical Run Parameters ------------------------------------------------------------------------------------
        if par['randomSeed'] == 'False' or par['randomSeed'] == 'false':
            self.useSeed = False                                                #Saved as Boolean
        else:
            self.useSeed = True                                                 #Saved as Boolean
            self.randomSeed = int(par['randomSeed'])                            #Saved as integer
            
        self.labelInstanceID = par['labelInstanceID']                           #Saved as text
        self.labelPhenotype = par['labelPhenotype']                             #Saved as text
        self.labelMissingData = par['labelMissingData']                         #Saved as text
        self.discreteAttributeLimit = int(par['discreteAttributeLimit'])        #Saved as integer
        self.trackingFrequency = int(par['trackingFrequency'])                  #Saved as integer
        
        # Supervised Learning Parameters -------------------------------------------------------------------------------
        self.nu = int(par['nu'])                                                #Saved as integer
        self.chi = float(par['chi'])                                            #Saved as float
        self.upsilon = float(par['upsilon'])                                    #Saved as float
        self.theta_GA = int(par['theta_GA'])                                    #Saved as integer
        self.init_fit = float(par['init_fit'])                                  #Saved as float
        self.fitnessReduction = float(par['fitnessReduction'])                  #Saved as float
        
        # Algorithm Heuristic Options -------------------------------------------------------------------------------
        self.selectionMethod = par['selectionMethod']                           #Saved as text
        self.theta_sel = float(par['theta_sel'])                                #Saved as float
        
        # PopulationReboot -------------------------------------------------------------------------------
        self.doPopulationReboot = bool(int(par['doPopulationReboot']))          #Saved as Boolean
        self.popRebootPath = par['popRebootPath']                               #Saved as text
        
        
    def referenceEnv(self, e):
        """ Store reference to environment object. """
        self.env = e
 
        
    def parseIterations(self):
        """ Parse the 'learningIterations' string to identify the maximum number of learning iterations as well as evaluation checkpoints. """
        checkpoints = self.learningIterations.split('.') 
        for i in range(len(checkpoints)): 
            checkpoints[i] = int(checkpoints[i])
            
        self.learningCheckpoints = checkpoints
        self.maxLearningIterations = self.learningCheckpoints[(len(self.learningCheckpoints)-1)] 
        
        if self.trackingFrequency == 0:
            self.trackingFrequency = self.env.formatData.numTrainInstances  #Adjust tracking frequency to match the training data size - learning tracking occurs once every epoch

#To access one of the above constant values from another module, import GHCS_Constants * and use "cons.something"
cons = Constants() 