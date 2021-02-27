# -*- coding: utf-8 -*-
"""
Created on Sat Feb 27 08:38:16 2021

@author: Jakub Lukaszczyk
"""
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg#, NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure

class Prediction_graph(FigureCanvasQTAgg):
    
    def __init__(self, parent=None, width=5,heigth=4,dpi=100):
        figure = Figure()
        
        self.axes = figure.add_axes([0,0,1,1])
        self.categories = []
        self.probability = []
        
        self.axes.bar(self.categories,self.probability)
        #will probably need some resizing
        super(Prediction_graph,self).__init__(figure)
    
    def add_categories(self, categories = []):
        self.categories = categories
        self.axes.bar(self.categories,self.probability)
        pass
    
    def write_probability(self, probability = []):
        self.probability = probability
        self.axes.bar(self.categories,self.probability)
        pass