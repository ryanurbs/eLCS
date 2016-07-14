"""
Name:        eLCS_Algorithm.py
Authors:     Ryan Urbanowicz - Written at Dartmouth College, Hanover, NH, USA
Contact:     ryan.j.urbanowicz@darmouth.edu
Created:     November 1, 2013
Description: The major controlling module of eLCS.  Includes the major run loop which controls learning over a specified number of iterations.  Also includes
             periodic tracking of estimated performance, and checkpoints where complete evaluations of the eLCS rule population is performed.
             
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

#Import Required Modules-------------------------------
from eLCS_Constants import *
from eLCS_ClassifierSet import ClassifierSet
import copy
import random
import math
#------------------------------------------------------

class eLCS:
    def __init__(self):
        """ Initializes the eLCS algorithm """
        print("eLCS: Initializing Algorithm...")
        #Global Parameters-------------------------------------------------------------------------------------
        self.population = None          # The rule population (the 'solution/model' evolved by eLCS)
        self.learnTrackOut = None       # Output file that will store tracking information during learning
        
        #-------------------------------------------------------
        # POPULATION REBOOT - Begin eLCS learning from an existing saved rule population
        #-------------------------------------------------------
        if cons.doPopulationReboot:    
            self.populationReboot()
            
        #-------------------------------------------------------
        # NORMAL eLCS - Run eLCS from scratch on given data
        #-------------------------------------------------------
        else:
            try:
                self.learnTrackOut = open(cons.outFileName+'_LearnTrack.txt','w')     
            except Exception as inst:
                print(type(inst))
                print(inst.args)
                print(inst)
                print('cannot open', cons.outFileName+'_LearnTrack.txt')
                raise
            else:
                self.learnTrackOut.write("Explore_Iteration\tPopSize\tAveGenerality\n")
            # Instantiate Population---------
            self.population = ClassifierSet()
            self.exploreIter = 0
            self.correct  = [0.0 for i in range(cons.trackingFrequency)]
            
        #Run the eLCS algorithm-------------------------------------------------------------------------------
        self.run_eLCS()


    def run_eLCS(self):
        """ Runs the initialized eLCS algorithm. """
        #--------------------------------------------------------------
        print("Learning Checkpoints: " +str(cons.learningCheckpoints))
        print("Maximum Iterations: " +str(cons.maxLearningIterations))
        print("Beginning eLCS learning iterations.")
        print("------------------------------------------------------------------------------------------------------------------------------------------------------")
        #-------------------------------------------------------
        # MAJOR LEARNING LOOP
        #-------------------------------------------------------
        while self.exploreIter < cons.maxLearningIterations: 
            
            #-------------------------------------------------------
            # GET NEW INSTANCE AND RUN A LEARNING ITERATION
            #-------------------------------------------------------
            state_phenotype = cons.env.getTrainInstance() 
            self.runIteration(state_phenotype, self.exploreIter)
            
            #-------------------------------------------------------
            # TRACK PROGRESS
            #-------------------------------------------------------
            if (self.exploreIter%cons.trackingFrequency) == (cons.trackingFrequency - 1):
                self.population.runPopAveEval(self.exploreIter) 
                self.learnTrackOut.write(self.population.getPopTrack(self.exploreIter+1,cons.trackingFrequency)) #Report learning progress to standard out and tracking file.
            
            #-------------------------------------------------------
            # ADJUST MAJOR VALUES FOR NEXT ITERATION
            #-------------------------------------------------------
            self.exploreIter += 1       # Increment current learning iteration
            cons.env.newInstance(True)  # Step to next instance in training set
            
        self.learnTrackOut.close()

        print("eLCS Run Complete")
        
        
    def runIteration(self, state_phenotype, exploreIter):
        """ Run a single eLCS learning iteration. """
        #-----------------------------------------------------------------------------------------------------------------------------------------
        # FORM A MATCH SET - includes covering
        #-----------------------------------------------------------------------------------------------------------------------------------------
        self.population.makeMatchSet(state_phenotype, exploreIter)
        #-----------------------------------------------------------------------------------------------------------------------------------------
        # FORM A CORRECT SET
        #-----------------------------------------------------------------------------------------------------------------------------------------
        self.population.makeCorrectSet(state_phenotype[1])
        #-----------------------------------------------------------------------------------------------------------------------------------------
        # UPDATE PARAMETERS
        #-----------------------------------------------------------------------------------------------------------------------------------------
        self.population.updateSets(exploreIter)
        self.population.clearSets() #Clears the match and correct sets for the next learning iteration
        
    
    def populationReboot(self):
        """ Manages the reformation of a previously saved eLCS classifier population. """
        #--------------------------------------------------------------------
        try: #Re-open track learning file for continued tracking of progress.
            self.learnTrackOut = open(cons.outFileName+'_LearnTrack.txt','a')     
        except Exception as inst:
            print(type(inst))
            print(inst.args)
            print(inst)
            print('cannot open', cons.outFileName+'_LearnTrack.txt')
            raise

        #Extract last iteration from file name---------------------------------------------
        temp = cons.popRebootPath.split('_')
        iterRef = len(temp)-1
        completedIterations = int(temp[iterRef])
        print("Rebooting rule population after " +str(completedIterations)+ " iterations.")
        self.exploreIter = completedIterations-1
        for i in range(len(cons.learningCheckpoints)):
            cons.learningCheckpoints[i] += completedIterations
        cons.maxLearningIterations += completedIterations

        #Rebuild existing population from text file.--------
        self.population = ClassifierSet(cons.popRebootPath)

        