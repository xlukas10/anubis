# -*- coding: utf-8 -*-
"""
Created on Fri Oct 23 15:25:27 2020

@author: Jakub Lukaszczyk
"""
from harvesters.core import Harvester

class Camera:
    def __init__(self, producer_path = 'ZDE VLOZIT DEFAULTNI CESTU'):
        self.h = Harvester()
        self.set_gentl_producer(producer_path)

        return self.get_camera_list()

    def get_camera_list(self,):
        return self.h.update()
    
    def select_camera(self,selected_device):
        self.cam = self.h.create_image_acquirer(selected_device)
        self.cam.remote_device.node_map.Width.value = 8 #WHY
        self.cam.remote_device.node_map.Height.value = 8 #WHY
        self.cam.remote_device.node_map.PixelFormat.value = 'Mono8'
        
    
    
    def get_image(self,):#should be called regularly from kivy frontend
        self.buffer = self.cam.fetch_buffer().payload.components[0]
        return self.buffer.data
    
    def set_parameters(self,**kwargs):
        return 42
    
    def get_available_parameters(self,):
        return dir(self.cam.remote_device.node_map)
    
    def read_parameters(self,):
        return 42
    
    def save_parameters(self,):
        return 42
    
    def start_recording(self,):
        self.cam.start_acquisition()
    
    def stop_recording(self,):
        self.cam.stop_acquisition()
        self.cam.destroy()
    
    def save_recording(self,path):
        return 42
    
    def set_gentl_producer(self,producer_path):
        self.h.add_file(producer_path)
    
    def remove_gentl_producer(self,producer_path):
        self.h.remove_file(producer_path)

    def disconnect_camera(self,):
        self.h.reset()
#add update camera list function h.update()