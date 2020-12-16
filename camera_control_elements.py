# -*- coding: utf-8 -*-
"""
Created on Thu Oct 22 07:09:54 2020

@author: Jakub Lukaszczyk
"""
from kivy.uix.button import Button
from global_objects import cam
from global_objects import frame_queue
from kivy.app import App
from kivy.clock import Clock

import kivy_elements
import threading
import cv2

import time #testing only

class PlayPause(Button):
    def __init__(self, **kwargs):
        super(PlayPause, self).__init__(**kwargs)
        self.acquisition_running = False
    
    def on_press(self):
        super(PlayPause, self).on_press()
        print('Here')
        if False:#self.acquisition_running:
            cam.stop_acquisition()
            self.acquisition_running = False
            pass
        else:
            #cam.start_acquisition(frame_queue)
            self._frame_preview_thread = threading.Thread(target=self._live_preview)
            self._frame_preview_thread.start()
            self.acquisition_running = True
        
        
    #function to stop or resume frame drawing in real time
    
    
    def _live_preview(self):
        #method name is a subject to change
        cam_img = App.get_running_app().root.ids.camera_image
        
        cap = cv2.VideoCapture("./test.mp4")
        x = 0
        while x < 600:
            if cap.grab():
                flag, frame = cap.retrieve()
                frame_queue.put_nowait(frame)
                if not flag:
                    continue
            x += 1
        
        print(frame_queue.qsize())
        
        preview = Clock.schedule_interval(cam_img.draw, 1/60)
        print('preview started')
        time.sleep(5)
        #cam._stream_stop_switch.wait()
        preview.cancel()
        print('preview stopped')
    

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