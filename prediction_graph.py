# -*- coding: utf-8 -*-
"""
Created on Sat Feb 27 08:38:16 2021

@author: Jakub Lukaszczyk
"""
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import numpy as np
import operator

class Prediction_graph(FigureCanvasQTAgg):
    
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        """!@brief Initializes prediction graph
        @details The graph is created as a bar plot with 5 categories all
        initialized to 0.
        @param[in] parent Parent widget
        @param[in] width Width of the created figure
        @param[in] height Height of the created figure
        @param[in] dpi Dots per inch of the created figure
        """
        self.figure = Figure(figsize=(width, height), dpi=dpi)
        
        self.axes = self.figure.add_subplot(111)
        self.N = 0
        self.categories = ["ctg1", "ctg2", "ctg3", "ctg4", "ctg5"]
        self.probability = [0, 0, 0, 0, 0]
        self.w = 1
        self.axes.set_ylim(-1,1)
        
        self.axes.bar(self.categories,self.probability,self.w)
        super(Prediction_graph,self).__init__(self.figure)
    
    def add_categories(self, categories = []):
        """!@brief Changes default categories of the plot to categories from
            method argument
        @details All categories currently in a plot are removed and new ones
            are added in their place. Count is not limited
        @param[in] categories A list with names of the new categories
        """
        self.categories.clear()
        
        for category in categories:
            if(category != None):
                self.categories.append(str(category))
    
    def write_probability(self, probability = []):
        """!@brief Finds top 5 items in given input and plots them
        @details The input probability should have the same dimensions as the 
            categories. after finding the top 5, the categories with the same 
            indices are plotted.
        @param[in] probability Results to be plotted
        """
        top_5 = []
        top_indices = []
        
        if(len(probability) < 5):
            top_5 = probability
            top_indices = range(0, len(probability))
        else:
            for i in range(0, 5): 
                top = 0
                top_index = 0
                  
                for j in range(len(probability)):     
                    if probability[j] > top:
                        top = probability[j];
                        top_index = j
                          
                probability.remove(top);
                top_5.append(top)
                top_indices.append(top_index)
        
        self.probability = top_5#test with multiple output classes
        self.figure.canvas.axes.clear()
        
        self.axes.bar(operator.itemgetter(*top_indices)(self.categories),top_5,self.w)
        self.figure.canvas.draw()