"""
Name:        eLCS_Classifier.py
Authors:     Ryan Urbanowicz - Written at Dartmouth College, Hanover, NH, USA
Contact:     ryan.j.urbanowicz@darmouth.edu
Created:     November 1, 2013
Description: This module defines an individual classifier within the rule population, along with all respective parameters.
             Also included are classifier-level methods, including constructors(covering, copy, reboot) and matching.
             Parameter update methods are also included.
             
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

#Import Required Modules---------------
from eLCS_Constants import *
import random
import copy
import math
#--------------------------------------

class Classifier:
    def __init__(self,a=None,b=None,c=None,d=None):
        #Major Parameters --------------------------------------------------
        self.specifiedAttList = []      # Attribute Specified in classifier: Similar to Bacardit 2009 - ALKR + GABIL, continuous and discrete rule representation
        self.condition = []             # States of Attributes Specified in classifier: Similar to Bacardit 2009 - ALKR + GABIL, continuous and discrete rule representation
        self.phenotype = None           # Class if the endpoint is discrete, and a continuous phenotype if the endpoint is continuous
        
        self.fitness = cons.init_fit    # Classifier fitness - initialized to a constant initial fitness value
        self.accuracy = 0.0             # Classifier accuracy - Accuracy calculated using only instances in the dataset which this rule matched.
        self.numerosity = 1             # The number of rule copies stored in the population.  (Indirectly stored as incremented numerosity)
        
        #Experience Management ---------------------------------------------
        self.initTimeStamp = None       # Iteration in which the rule first appeared.
        
        #Classifier Accuracy Tracking --------------------------------------
        self.matchCount = 0             # Known in many LCS implementations as experience i.e. the total number of times this classifier was in a match set
        self.correctCount = 0           # The total number of times this classifier was in a correct set
        
        if isinstance(c,list):
            self.classifierCovering(a,b,c,d)
        elif isinstance(a,Classifier):
            self.classifierCopy(a, b)
        elif isinstance(a,list) and b == None:
            self.rebootClassifier(a)
        else:
            print("Classifier: Error building classifier.")
            
    #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    # CLASSIFIER CONSTRUCTION METHODS
    #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------       
    def classifierCovering(self, setSize, exploreIter, state, phenotype):
        """ Makes a new classifier when the covering mechanism is triggered.  The new classifier will match the current training instance. 
        Covering will NOT produce a default rule (i.e. a rule with a completely general condition). """
        #Initialize new classifier parameters----------
        self.initTimeStamp = exploreIter
        dataInfo = cons.env.formatData
        #-------------------------------------------------------
        # DISCRETE PHENOTYPE
        #-------------------------------------------------------
        if dataInfo.discretePhenotype: 
            self.phenotype = phenotype
        #-------------------------------------------------------
        # CONTINUOUS PHENOTYPE
        #-------------------------------------------------------
        else:
            phenotypeRange = dataInfo.phenotypeList[1] - dataInfo.phenotypeList[0]
            rangeRadius = random.randint(25,75)*0.01*phenotypeRange / 2.0 #Continuous initialization domain radius.
            Low = float(phenotype) - rangeRadius
            High = float(phenotype) + rangeRadius
            self.phenotype = [Low,High] #ALKR Representation, Initialization centered around training instance  with a range between 25 and 75% of the domain size.      
        #-------------------------------------------------------
        # GENERATE MATCHING CONDITION
        #-------------------------------------------------------
        while len(self.specifiedAttList) < 1:
            for attRef in range(len(state)):
                if random.random() < cons.p_spec and state[attRef] != cons.labelMissingData:
                    self.specifiedAttList.append(attRef)
                    self.condition.append(self.buildMatch(attRef, state))
        
        
    def rebootClassifier(self, classifierList): 
        """ Rebuilds a saved classifier as part of the population Reboot """
        numAttributes = cons.env.formatData.numAttributes
        attInfo = cons.env.formatData.attributeInfo
        for attRef in range(0,numAttributes):
            if classifierList[attRef] != '#':  #Attribute in rule is not wild
                if attInfo[attRef][0]: #Continuous Attribute
                    valueRange = classifierList[attRef].split(';')
                    self.condition.append(valueRange)
                    self.specifiedAttList.append(attRef)
                else:
                    self.condition.append(classifierList[attRef])
                    self.specifiedAttList.append(attRef)
        #-------------------------------------------------------
        # DISCRETE PHENOTYPE
        #-------------------------------------------------------
        if cons.env.formatData.discretePhenotype: 
            self.phenotype = str(classifierList[numAttributes])
        #-------------------------------------------------------
        # CONTINUOUS PHENOTYPE
        #-------------------------------------------------------
        else:
            self.phenotype = classifierList[numAttributes].split(';')
            for i in range(2): 
                self.phenotype[i] = float(self.phenotype[i])

        self.fitness = float(classifierList[numAttributes+1])
        self.accuracy = float(classifierList[numAttributes+2])
        self.numerosity = int(classifierList[numAttributes+3])
        self.initTimeStamp = int(classifierList[numAttributes+6])
        
        self.correctCount = int(classifierList[numAttributes+9])
        self.matchCount = int(classifierList[numAttributes+10])


    #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    # MATCHING
    #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------  
    def match(self, state):
        """ Returns if the classifier matches in the current situation. """ 
        for i in range(len(self.condition)):
            attributeInfo = cons.env.formatData.attributeInfo[self.specifiedAttList[i]]
            #-------------------------------------------------------
            # CONTINUOUS ATTRIBUTE
            #-------------------------------------------------------
            if attributeInfo[0]:
                instanceValue = state[self.specifiedAttList[i]]
                if self.condition[i][0] < instanceValue < self.condition[i][1] or instanceValue == cons.labelMissingData:
                    pass
                else:
                    return False  
            #-------------------------------------------------------
            # DISCRETE ATTRIBUTE
            #-------------------------------------------------------
            else:
                stateRep = state[self.specifiedAttList[i]]  
                if stateRep == self.condition[i] or stateRep == cons.labelMissingData:
                    pass
                else:
                    return False 
        return True
        
   
    #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    # OTHER METHODS
    #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------  
    def buildMatch(self, attRef, state):
        """ Builds a matching condition for the classifierCovering method. """
        attributeInfo = cons.env.formatData.attributeInfo[attRef]
        #-------------------------------------------------------
        # CONTINUOUS ATTRIBUTE
        #-------------------------------------------------------
        if attributeInfo[0]:
            attRange = attributeInfo[1][1] - attributeInfo[1][0]
            rangeRadius = random.randint(25,75)*0.01*attRange / 2.0 #Continuous initialization domain radius.
            Low = state[attRef] - rangeRadius
            High = state[attRef] + rangeRadius
            condList = [Low,High] #ALKR Representation, Initialization centered around training instance  with a range between 25 and 75% of the domain size.
        #-------------------------------------------------------
        # DISCRETE ATTRIBUTE
        #-------------------------------------------------------
        else: 
            condList = state[attRef] #State already formatted like GABIL in DataManagement
            
        return condList
     

    def equals(self, cl):  
        """ Returns if the two classifiers are identical in condition and phenotype. This works for discrete or continuous attributes or phenotypes. """ 
        if cl.phenotype == self.phenotype and len(cl.specifiedAttList) == len(self.specifiedAttList): #Is phenotype the same and are the same number of attributes specified - quick equality check first.
            clRefs = sorted(cl.specifiedAttList)
            selfRefs = sorted(self.specifiedAttList)
            if clRefs == selfRefs:
                for i in range(len(cl.specifiedAttList)):
                    tempIndex = self.specifiedAttList.index(cl.specifiedAttList[i])
                    if cl.condition[i] == self.condition[tempIndex]:
                        pass
                    else:
                        return False
                return True
        return False


    #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    # PARAMETER UPDATES
    #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------        
    def updateAccuracy(self):
        """ Update the accuracy tracker """
        self.accuracy = self.correctCount / float(self.matchCount)
        
        
    def updateFitness(self):
        """ Update the fitness parameter. """ 
        if cons.env.formatData.discretePhenotype or (self.phenotype[1]-self.phenotype[0])/cons.env.formatData.phenotypeRange < 0.5:
            self.fitness = pow(self.accuracy, cons.nu)
        else:
            if (self.phenotype[1]-self.phenotype[0]) >= cons.env.formatData.phenotypeRange:
                self.fitness = 0.0
            else:
                self.fitness = math.fabs(pow(self.accuracy, cons.nu) - (self.phenotype[1]-self.phenotype[0])/cons.env.formatData.phenotypeRange)

        
    def updateExperience(self):
        """ Increases the experience of the classifier by one. Once an epoch has completed, rule accuracy can't change."""
        self.matchCount += 1 


    def updateCorrect(self):
        """ Increases the correct phenotype tracking by one. Once an epoch has completed, rule accuracy can't change."""
        self.correctCount += 1 


    def updateNumerosity(self, num):
        """ Updates the numberosity of the classifier.  Notice that 'num' can be negative! """
        self.numerosity += num
        
        
    def setAccuracy(self,acc):
        """ Sets the accuracy of the classifier """
        self.accuracy = acc
        
        
    def setFitness(self, fit):
        """  Sets the fitness of the classifier. """
        self.fitness = fit

    def reportClassifier(self):
        """  Transforms the rule representation used to a more standard readable format. """
        numAttributes = cons.env.formatData.numAttributes
        thisClassifier = []
        counter = 0
        for i in range(numAttributes):
            if i in self.specifiedAttList:
                thisClassifier.append(self.condition[counter])
                counter += 1
            else:
                thisClassifier.append('#')
        return thisClassifier