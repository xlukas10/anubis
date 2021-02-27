# -*- coding: utf-8 -*-
"""
Created on Sat Feb 27 09:00:50 2021

@author: Jakub Lukaszczyk
"""

from tensorflow import keras
import numpy as np
import cv2

class Computer_vision():
    def __init__(self,plot):
        self.model = None
        self.SIZE = 50
        self.categories = []
        self.plot = plot
        
    def load_model(self,path):
        self.model = keras.models.load_model(path)
    
    def save_model(self,path):
        self.model.save(path)
    
    def classify(self,frame,prediction_flag):
        #get current frame
        if self.model != None:
            input_dim = list(self.model.get_layer(index=0).input_shape)
            
            if(list(self.model.get_layer(index=-1).output_shape) != self.categories):
                self.categories = list(self.model.get_layer(index=-1).output_shape)
                self.plot.add_categories(self.categories)
                
            
            if(input_dim[0] == None):
                input_dim[0] = -1
            
            frame_data = cv2.resize(frame,(input_dim[1],input_dim[2]))
            #maybe change dimensions according to model
            frame_data = np.array(frame_data)
            frame_data = frame_data.reshape(input_dim)
            #transform it to numpy array
            
            #run .predict
            out_data = self.model.predict([frame_data])
            
            self.plot.write_probability(out_data)
            #save output to variable and write it to the plot
            
            
            prediction_flag.clear()
        
    def learn(self):
        pass