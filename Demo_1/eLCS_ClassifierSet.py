"""
Name:        eLCS_ClassifierSet.py
Authors:     Ryan Urbanowicz - Written at Dartmouth College, Hanover, NH, USA
Contact:     ryan.j.urbanowicz@darmouth.edu
Created:     November 1, 2013
Description: This module handles all classifier sets (population, match set, correct set) along with mechanisms and heuristics that act on these sets.  
             
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

#Import Required Modules---------------------
from eLCS_Constants import *
from eLCS_Classifier import Classifier
import random
import copy
import sys
#--------------------------------------------

class ClassifierSet:
    def __init__(self, a=None):
        """ Overloaded initialization: Handles creation of a new population or a rebooted population (i.e. a previously saved population). """
        # Major Parameters
        self.popSet = []        # List of classifiers/rules
        self.matchSet = []      # List of references to rules in population that match
        self.correctSet = []    # List of references to rules in population that both match and specify correct phenotype
        self.microPopSize = 0   # Tracks the current micro population size 
        
        # Evaluation Parameters-------------------------------
        self.aveGenerality = 0.0
        self.expRules = 0.0
        self.attributeSpecList = []
        self.attributeAccList = []
        self.avePhenotypeRange = 0.0

        # Set Constructors-------------------------------------
        if a==None:
            self.makePop() #Initialize a new population
        elif isinstance(a,str):
            self.rebootPop(a) #Initialize a population based on an existing saved rule population
        else:
            print("ClassifierSet: Error building population.")
            
    #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    # POPULATION CONSTRUCTOR METHODS
    #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    def makePop(self):
        """ Initializes the rule population """
        self.popSet = []
            
            
    def rebootPop(self, remakeFile):
        """ Remakes a previously evolved population from a saved text file. """
        print("Rebooting the following population: " + str(remakeFile)+"_RulePop.txt")
        #*******************Initial file handling**********************************************************
        try:       
            datasetList = []
            f = open(remakeFile+"_RulePop.txt", 'r')
        except Exception as inst:
            print(type(inst))
            print(inst.args)
            print(inst)
            print('cannot open', remakeFile+"_RulePop.txt")
            raise
        else:
            self.headerList = f.readline().rstrip('\n').split('\t')   #strip off first row
            for line in f:
                lineList = line.strip('\n').split('\t')
                datasetList.append(lineList)
            f.close()    
            
        #**************************************************************************************************
        for each in datasetList:
            cl = Classifier(each)
            self.popSet.append(cl) 
            self.microPopSize += 1
        print("Rebooted Rule Population has "+str(len(self.popSet))+" Macro Pop Size.")
        
    #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    # CLASSIFIER SET CONSTRUCTOR METHODS
    #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    def makeMatchSet(self, state_phenotype, exploreIter):
        """ Constructs a match set from the population. Covering is initiated if the match set is empty or a rule with the current correct phenotype is absent. """ 
        #DEMO 1 CODE-------------------------
        print("----------------------------------------------------------------------------------------------------------------")
        print("Current instance from dataset:  " + "State = "+ str(state_phenotype[0]) + "  Phenotype = "+ str(state_phenotype[1]))
        print("--------------------------------------------------------------------------------------")
        print("Matching Classifiers:")
        #------------------------------------------
        #Initial values
        state = state_phenotype[0]
        phenotype = state_phenotype[1]
        doCovering = True # Covering check: Twofold (1)checks that a match is present, and (2) that at least one match dictates the correct phenotype.
        
        #-------------------------------------------------------
        # MATCHING
        #-------------------------------------------------------
        for i in range(len(self.popSet)):           # Go through the population
            cl = self.popSet[i]                     # One classifier at a time
            if cl.match(state):                     # Check for match
                #DEMO 1 CODE-------------------------
                print("Condition: "+ str(cl.reportClassifier()) + "  Phenotype: "+ str(cl.phenotype))
                #------------------------------------------
                self.matchSet.append(i)             # If match - add classifier to match set
                
                #Covering Check--------------------------------------------------------    
                if cons.env.formatData.discretePhenotype:   # Discrete phenotype     
                    if cl.phenotype == phenotype:           # Check for phenotype coverage
                        doCovering = False
                else:                                                                           # Continuous phenotype
                    if float(cl.phenotype[0]) <= float(phenotype) <= float(cl.phenotype[1]):    # Check for phenotype coverage
                        doCovering = False
        if len(self.matchSet) == 0:
            print('None found.')
        #-------------------------------------------------------
        # COVERING
        #-------------------------------------------------------
        while doCovering:
            newCl = Classifier(exploreIter, state, phenotype)
            #DEMO 1 CODE-------------------------
            print("Covering Activated:")
            print("Condition: "+ str(newCl.reportClassifier()) + "  Phenotype: "+ str(newCl.phenotype))
            #------------------------------------------
            self.addClassifierToPopulation(newCl)
            self.matchSet.append(len(self.popSet)-1)  # Add covered classifier to matchset
            doCovering = False
        
        
    def makeCorrectSet(self, phenotype):
        """ Constructs a correct set out of the given match set. """      
        for i in range(len(self.matchSet)):
            ref = self.matchSet[i]
            #-------------------------------------------------------
            # DISCRETE PHENOTYPE
            #-------------------------------------------------------
            if cons.env.formatData.discretePhenotype: 
                if self.popSet[ref].phenotype == phenotype:
                    self.correctSet.append(ref) 
            #-------------------------------------------------------
            # CONTINUOUS PHENOTYPE
            #-------------------------------------------------------
            else: 
                if float(phenotype) <= float(self.popSet[ref].phenotype[1]) and float(phenotype) >= float(self.popSet[ref].phenotype[0]):
                    self.correctSet.append(ref)

    
    #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    # OTHER KEY METHODS
    #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    def addClassifierToPopulation(self, cl):
        """ Adds a classifier to the set and increases the microPopSize value accordingly."""
        self.popSet.append(cl)
        self.microPopSize += 1
            

    def updateSets(self, exploreIter):
        """ Updates all relevant parameters in the current match and correct sets. """
        for ref in self.matchSet:
            self.popSet[ref].updateExperience()    
            if ref in self.correctSet:
                self.popSet[ref].updateCorrect()

            self.popSet[ref].updateAccuracy()
            self.popSet[ref].updateFitness()


    #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    # OTHER METHODS
    #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    def setIterStamps(self, exploreIter):
        """ Sets the time stamp of all classifiers in the set to the current time. The current time
        is the number of exploration steps executed so far.  """
        for i in range(len(self.correctSet)):
            ref = self.correctSet[i]
            self.popSet[ref].updateTimeStamp(exploreIter)
            
     
    def clearSets(self):
        """ Clears out references in the match and correct sets for the next learning iteration. """
        self.matchSet = []
        self.correctSet = []
        
            
    #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    # EVALUTATION METHODS
    #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    def runPopAveEval(self, exploreIter):
        """ Calculates some summary evaluations across the rule population including average generality. """
        genSum = 0
        agedCount = 0
        for cl in self.popSet:
            genSum += ((cons.env.formatData.numAttributes - len(cl.condition)) / float(cons.env.formatData.numAttributes)) 
        if self.microPopSize == 0:
            self.aveGenerality = 'NA'
        else:
            self.aveGenerality = genSum / float(self.microPopSize) 

        #-------------------------------------------------------
        # CONTINUOUS PHENOTYPE
        #-------------------------------------------------------
        if not cons.env.formatData.discretePhenotype:
            sumRuleRange = 0
            for cl in self.popSet:
                sumRuleRange += (cl.phenotype[1] - cl.phenotype[0])
            phenotypeRange = cons.env.formatData.phenotypeList[1] - cons.env.formatData.phenotypeList[0]
            self.avePhenotypeRange = (sumRuleRange / float(self.microPopSize)) / float(phenotypeRange)

              
    def getPopTrack(self, exploreIter, trackingFrequency):
        """ Returns a formated output string to be printed to the Learn Track output file. """
        trackString = str(exploreIter)+ "\t" + str(len(self.popSet)) + "\t" + str(self.aveGenerality)  +  "\n"
        if cons.env.formatData.discretePhenotype: #discrete phenotype
            print(("Iteration: " + str(exploreIter) + "\t PopSize: " + str(len(self.popSet)) + "\t AveGen: " + str(self.aveGenerality)))
        else: # continuous phenotype
            print(("Iteration: " + str(exploreIter) + "\t PopSize: " + str(len(self.popSet)) + "\t AveGen: " + str(self.aveGenerality) + "\t PhenRange: " +str(self.avePhenotypeRange)))
        return trackString
         