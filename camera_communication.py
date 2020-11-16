# -*- coding: utf-8 -*-
"""
Created on Fri Oct 23 15:25:27 2020

@author: Jakub Lukaszczyk
"""
from harvesters.core import Harvester
from vimba import *

class Camera:
    def __init__(self, producer_path = 'ZDE VLOZIT DEFAULTNI CESTU'):
        self.h = Harvester()
        self.set_gentl_producer(producer_path)
        self.vendor = 'Other'

    def get_camera_list(self,):
        return self.h.update()
    
    def select_camera(self,selected_device):
        if(self.h.device_info_list[selected_device].vendor == 'Allied Vision Technologies'):
            self.disconnect_harvester()
            self.vendor = 'Allied Vision Technologies'
            #add code transforming harvester camera index to Vimba
            self.active_camera = selected_device
        else:
            self.cam = self.h.create_image_acquirer(selected_device)
    
    def get_image(self,):#should be called regularly from kivy frontend
        if(self.vendor == 'Allied Vision Technologies'):
            with Vimba.get_instance() as vimba:
                cams = vimba.get_all_cameras()
                with cams [self.active_camera] as cam:
                    frame = cam.get_frame()
                    return frame
        else:
            self.buffer = self.cam.fetch_buffer().payload.components[0]
            return self.buffer.data
    
    def set_parameters(self,**kwargs):
        if(self.vendor == 'Allied Vision Technologies'):
            with Vimba.get_instance() as vimba:
                cams = vimba.get_all_cameras()
                with cams[self.active_camera] as cam:
                    for key, value in kwargs.items():
                        getattr(cam, key).set(value)
        else:                
            return 42
    
    def get_available_parameters(self,):
       if(self.vendor == 'Allied Vision Technologies'):
            with Vimba.get_instance() as vimba:
               cams = vimba.get_all_cameras ()
               with cams[self.active_camera] as cam:
                   params = dir(cam)
                   parameters = []
                   for param in params:
                       #filtering parameters that are not to be modified by user
                       if not param.startswith('_'):
                           parameters.append(param)
                   return parameters
       else:
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

    def disconnect_harvester(self,):
        self.h.reset()
#add update camera list function h.update()

kamera = Camera('C:/Programy/Allied Vision/Vimba_4.0/VimbaGigETL/Bin/Win64/VimbaGigETL.cti')
kamera.get_camera_list()
kamera.select_camera(0)
kamera.set_parameters(GVSPPacketSize=1500)
print(kamera.get_image())
p = kamera.get_available_parameters()

for param in p:
    print(param)