# -*- coding: utf-8 -*-
"""
Created on Thu Oct 22 07:09:54 2020

@author: Jakub Lukaszczyk
"""
from kivy.uix.button import Button

class PlayPause(Button):
    def __init__(self, **kwargs):
        super(PlayPause, self).__init__(**kwargs)
    
    #def on_touchdown 
    #function to stop or resume frame drawing in real time

class ZoomIn(Button):
    def __init__(self, **kwargs):
        super(ZoomIn, self).__init__(**kwargs)
    
    #def on_touchdown 
    #function to zoom image in by lets say 15%

class ZoomOut(Button):
    def __init__(self, **kwargs):
        super(ZoomOut, self).__init__(**kwargs)
    
    #def on_touchdown 
    #function to zoom image out by lets say 15%

class ZoomFit(Button):
    def __init__(self, **kwargs):
        super(ZoomFit, self).__init__(**kwargs)
    
    #def on_touchdown 
    #function to fit camera image to image window

class Zoom100(Button):
    def __init__(self, **kwargs):
        super(Zoom100, self).__init__(**kwargs)
    
    #def on_touchdown 
    #function to show camera image pixel ratio 1:1