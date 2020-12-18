# -*- coding: utf-8 -*-
"""
Created on Thu Oct 22 07:09:54 2020

@author: Jakub Lukaszczyk
"""
from PyQt5 import QtWidgets

from global_camera import cam
from global_queue import frame_queue


import gui_elements
import threading
import cv2

import time #testing only

class PlayPause(QtWidgets.QPushButton):
    def __init__(self):
        super(PlayPause, self).__init__()
        self.acquisition_running = False
        self.clicked.connect(self.on_press)
    
    def on_press(self):
        print('Here')
        if self.acquisition_running:
            cam.stop_acquisition()
            self.acquisition_running = False
        else:
            cam.start_acquisition()
            self._frame_preview_thread = threading.Thread(target=self._live_preview)
            self._frame_preview_thread.start()
            self.acquisition_running = True
        
        
    #function to stop or resume frame drawing in real time
    
    
    def _live_preview(self):
        #method name is a subject to change
        cam_img = App.get_running_app().root.ids.camera_image
        print(frame_queue.qsize())
        
        preview = Clock.schedule_interval(cam_img.draw, 1/60)
        print('preview started')
        cam._stream_stop_switch.wait()
        preview.cancel()
        print('preview stopped')
    

class Record(QtWidgets.QPushButton):
    def __init__(self):
        super(Record, self).__init__()
        self.recording_running = False
        self.clicked.connect(self.on_press)
    
    def on_press(self):
        if self.recording_running:
            cam.stop_recording()
            self.recording_running = False
        else:
            cam.start_recording('C:/Users/Jakub Lukaszczyk/Documents/Test/','nic')
            self.recording_running = True

class ZoomOut(QtWidgets.QPushButton):
    def __init__(self):
        super(ZoomOut, self).__init__()
    
    #def on_touchdown 
    #function to zoom image out by lets say 15%

class ZoomFit(QtWidgets.QPushButton):
    def __init__(self):
        super(ZoomFit, self).__init__()
    
    #def on_touchdown 
    #function to fit camera image to image window

class Zoom100(QtWidgets.QPushButton):
    def __init__(self):
        super(Zoom100, self).__init__()
    
    #def on_touchdown 
    #function to show camera image pixel ratio 1:1