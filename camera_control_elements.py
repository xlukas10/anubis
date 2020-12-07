# -*- coding: utf-8 -*-
"""
Created on Thu Oct 22 07:09:54 2020

@author: Jakub Lukaszczyk
"""
from kivy.uix.button import Button
from anubis import cam
from anubis import frame_queue
from kivy.app import App

import kivy_elements
import threading

class PlayPause(Button):
    def __init__(self, **kwargs):
        super(PlayPause, self).__init__(**kwargs)
    
    def on_press(self):
        super(PlayPause, self).on_press()
        print('Here')
        if cam.acquisition_running:
            cam.stop_acquisition()
        else:
            cam.start_acquisition(frame_queue)
            self._frame_producer_thread = threading.Thread(target=self._live_preview)
            self._frame_producer_thread.start()
            self.acquisition_running = True
        
        
    #function to stop or resume frame drawing in real time
    
    
    def _live_preview(self):
        #method name is a subject to change
        while cam.acquisition_running:
            #maybe test for queue not empty
            try:
                if not frame_queue.empty():
                    frame = frame_queue.get_nowait()
                    App.get_running_app().root.ids.camera_image.draw(frame)
            finally:
                pass
        
    

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