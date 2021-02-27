# -*- coding: utf-8 -*-
"""
Created on Sat Feb 27 09:00:50 2021

@author: Jakub Lukaszczyk
"""

from tensorflow import keras
import numpy as np

class Computer_vision():
    def __init__(self,plot):
        pass
        
    def load_model(self,path):
        self.model = keras.models.load_model(path)
    
    def save_model(self,path):
        self.model.save(path)
    
    def classify(self,frame,prediction_flag):
        #get current frame
        #frame_data = 
        print(self.model.get_layer(index=0))
        #maybe change dimensions according to model
        #transform it to numpy array
        
        #run .predict
        #self.model.predict(frame_data)
        #save output to variable and write it to the plot
        prediction_flag.clear()
        
    def learn(self):
        pass