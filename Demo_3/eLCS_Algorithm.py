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
from eLCS_Prediction import *
from eLCS_OutputFileManager import OutputFileManager
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
                self.learnTrackOut.write("Explore_Iteration\tMacroPopSize\tMicroPopSize\tAccuracy_Estimate\tAveGenerality\tExpRules\tTime(min)\n")
            
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
            
            #-------------------------------------------------------------------------------------------------------------------------------
            # EVALUATIONS OF ALGORITHM
            #-------------------------------------------------------------------------------------------------------------------------------
            #-------------------------------------------------------
            # TRACK LEARNING ESTIMATES
            #-------------------------------------------------------
            if (self.exploreIter%cons.trackingFrequency) == (cons.trackingFrequency - 1) and self.exploreIter > 0:
                self.population.runPopAveEval(self.exploreIter) 
                trackedAccuracy = sum(self.correct)/float(cons.trackingFrequency) #Accuracy over the last "trackingFrequency" number of iterations.
                self.learnTrackOut.write(self.population.getPopTrack(trackedAccuracy, self.exploreIter+1,cons.trackingFrequency)) #Report learning progress to standard out and tracking file.
            
            #-------------------------------------------------------
            # CHECKPOINT - OUTPUT CURRENT POPULATION
            #-------------------------------------------------------
            if (self.exploreIter + 1) in cons.learningCheckpoints:
                print("------------------------------------------------------------------------------------------------------------------------------------------------------")
                print("Output rule population after " + str(self.exploreIter + 1)+ " iterations.")
                
                self.population.runPopAveEval(self.exploreIter)
                self.population.runAttGeneralitySum(True)

                #Write output files----------------------------------------------------------------------------------------------------------
                OutputFileManager().writePopStats(cons.outFileName, self.exploreIter + 1, self.population, self.correct)
                OutputFileManager().writePop(cons.outFileName, self.exploreIter + 1, self.population)
                #----------------------------------------------------------------------------------------------------------------------------

                print("Continue Learning...")
                print("------------------------------------------------------------------------------------------------------------------------------------------------------")
            
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
        # MAKE A PREDICTION - utilized here for tracking estimated learning progress.  Typically used in the explore phase of many LCS algorithms.
        #-----------------------------------------------------------------------------------------------------------------------------------------
        prediction = Prediction(self.population)
        phenotypePrediction = prediction.getDecision()  
        #-------------------------------------------------------
        # PREDICTION NOT POSSIBLE
        #-------------------------------------------------------
        if phenotypePrediction == None or phenotypePrediction == 'Tie': 
            if cons.env.formatData.discretePhenotype:
                phenotypePrediction = random.choice(cons.env.formatData.phenotypeList)
            else:
                phenotypePrediction = random.randrange(cons.env.formatData.phenotypeList[0],cons.env.formatData.phenotypeList[1],(cons.env.formatData.phenotypeList[1]-cons.env.formatData.phenotypeList[0])/float(1000))
        else: #Prediction Successful
            #-------------------------------------------------------
            # DISCRETE PHENOTYPE PREDICTION
            #-------------------------------------------------------
            if cons.env.formatData.discretePhenotype:
                if phenotypePrediction == state_phenotype[1]:
                    self.correct[exploreIter%cons.trackingFrequency] = 1
                else:
                    self.correct[exploreIter%cons.trackingFrequency] = 0
            #-------------------------------------------------------
            # CONTINUOUS PHENOTYPE PREDICTION
            #-------------------------------------------------------
            else:
                predictionError = math.fabs(phenotypePrediction - float(state_phenotype[1]))
                phenotypeRange = cons.env.formatData.phenotypeList[1] - cons.env.formatData.phenotypeList[0]
                accuracyEstimate = 1.0 - (predictionError / float(phenotypeRange))
                self.correct[exploreIter%cons.trackingFrequency] = accuracyEstimate
        #-----------------------------------------------------------------------------------------------------------------------------------------
        # FORM A CORRECT SET
        #-----------------------------------------------------------------------------------------------------------------------------------------
        self.population.makeCorrectSet(state_phenotype[1])
        #-----------------------------------------------------------------------------------------------------------------------------------------
        # UPDATE PARAMETERS
        #-----------------------------------------------------------------------------------------------------------------------------------------
        self.population.updateSets(exploreIter)
        #-----------------------------------------------------------------------------------------------------------------------------------------
        # RUN THE GENETIC ALGORITHM - Discover new offspring rules from a selected pair of parents
        #-----------------------------------------------------------------------------------------------------------------------------------------
        self.population.runGA(exploreIter, state_phenotype[0], state_phenotype[1])

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
        #---------------------------------------------------
        try: #Obtain correct track
            f = open(cons.popRebootPath+"_PopStats.txt", 'r')
        except Exception as inst:
            print(type(inst))
            print(inst.args)
            print(inst)
            print('cannot open', cons.popRebootPath+"_PopStats.txt")
            raise 
        else:
            correctRef = 14 #File reference position
            tempLine = None
            for i in range(correctRef):
                tempLine = f.readline()
            tempList = tempLine.strip().split('\t')
            self.correct = tempList
            if cons.env.formatData.discretePhenotype:
                for i in range(len(self.correct)):
                    self.correct[i] = int(self.correct[i])
            else:
                for i in range(len(self.correct)):
                    self.correct[i] = float(self.correct[i])
            f.close()
        