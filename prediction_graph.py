# -*- coding: utf-8 -*-
"""
Created on Sat Feb 27 08:38:16 2021

@author: Jakub Lukaszczyk
"""
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg#, NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import numpy as np

class Prediction_graph(FigureCanvasQTAgg):
    
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.figure = Figure(figsize=(width, height), dpi=dpi)
        
        self.axes = self.figure.add_subplot(111)
        self.N = 0
        self.categories = []
        self.probability = []
        self.w = 1
        self.axes.set_ylim(-1,1)
        #self.indent = np.arange(self.N)
        
        self.axes.bar(self.categories,self.probability,self.w)
        super(Prediction_graph,self).__init__(self.figure)
    
    def add_categories(self, categories = []):
        self.categories.clear()
        
        for category in categories:
            if(category != None):
                self.categories.append(str(category))
    
    def write_probability(self, probability = []):
        self.probability = probability[0]#test with multiple output classes
        self.figure.canvas.axes.clear()
        
        self.axes.bar(self.categories,self.probability,self.w)
        self.figure.canvas.draw()