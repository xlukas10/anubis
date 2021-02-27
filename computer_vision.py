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
        
    def load_model(self,path):
        self.model = keras.models.load_model(path)
    
    def save_model(self,path):
        self.model.save(path)
    
    def classify(self,frame,prediction_flag):
        #get current frame
        if self.model != None:
            frame_data = cv2.resize(frame,(self.SIZE,self.SIZE))
            #maybe change dimensions according to model
            frame_data = np.array(frame_data)
            frame_data = frame_data.reshape(-1, self.SIZE, self.SIZE, 1)
            #transform it to numpy array
            
            #run .predict
            h = self.model.predict(frame_data)
            print(h)
            #save output to variable and write it to the plot
            prediction_flag.clear()
        
    def learn(self):
        pass