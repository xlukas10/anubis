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
        self.is_recording = False

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
    
    def get_single_frame(self,):
        '''
        Returns unmodified image data from camera.
        -------
        Uses selected camera to acquire single frame with active settings.
        '''
        if(self.vendor == 'Allied Vision Technologies'):
            with Vimba.get_instance() as vimba:
                cams = vimba.get_all_cameras()
                with cams [self.active_camera] as cam:
                    frame = cam.get_frame()
                    return frame
        else:
#to do
            self.buffer = self.cam.fetch_buffer().payload.components[0]
            return self.buffer.data
    
    def set_parameters(self,**kwargs):
        if(self.vendor == 'Allied Vision Technologies'):
#EDIT to work well with new parameter dictionary (name, value, maximum etc.)
            with Vimba.get_instance() as vimba:
                cams = vimba.get_all_cameras()
                with cams[self.active_camera] as cam:
                    for key, value in kwargs.items():
                        getattr(cam, key).set(value)
        else:                
            return 42
    
    def get_parameters(self,):
        if(self.vendor == 'Allied Vision Technologies'):
            with Vimba.get_instance() as vimba:
                cams = vimba.get_all_cameras ()
                with cams[self.active_camera] as cam:
                    features = cam.get_all_features()
                    features_out = {}
                    for feature in features:
                        name = feature.get_name()
                        features_out[name] = {}
                        
                        #Get feature's type if it exists
                        try:
                            attr = feature.get_type()
                        except (AttributeError, VimbaFeatureError):
                            attr = None
                        
                        features_out[name]['attr_type'] = attr
                        
                        #Get feature's value if it exists
                        try:
                            attr = feature.get_value()
                        except (AttributeError, VimbaFeatureError):
                            attr = None
                        
                        features_out[name]['attr_value'] = attr
                        
                        #Get feature's range if it exists
                        try:
                            attr = feature.get_range()
                        except (AttributeError, VimbaFeatureError):
                            attr = None
                        
                        features_out[name]['attr_range'] = attr
                        
                        #Get feature's increment if it exists
                        try:
                            attr = feature.get_increment()
                        except (AttributeError, VimbaFeatureError):
                            attr = None
                        
                        features_out[name]['attr_increment'] = attr
                        
                        #Get feature's max length if it exists
                        try:
                            attr = feature.get_max_length()
                        except (AttributeError, VimbaFeatureError):
                            attr = None
                        
                        features_out[name]['attr_max_length'] = attr
                        
                    return features_out
        else:
            return dir(self.cam.remote_device.node_map)
    
    def read_param_values(self,):
        '''
        
        Returns
        -------
        values[]
            Returns list of parameter dictionaries each containing information about parameters.
            
        '''
#This method may turn out to be redundant (for Vimba it is not needed, depends on harvester implementation)
        values = []
        
        if(self.vendor == 'Allied Vision Technologies'):
            return self.get_parameters()
        else:
            return 42
    
    def save_parameters(self,):
        return 42
    
    
    def start_acquisition():
        #create threading object for vimba, harvester or future api and start the thread
        pass
    
    def stop_acquisition():
        #stop threas created by start_acquisition
        pass
    
    def start_recording(self,):
        self.cam.start_acquisition()
        self.is_recording = True
    
    def stop_recording(self,):
        self.cam.stop_acquisition()
        self.cam.destroy()
        self.is_recording = False
    
    def configure_recording(self,path):
#to-do image format, extension, fps...
        pass
    
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
print(kamera.get_single_frame())
p = kamera.get_parameters()

for param in p:
    print(param)
    
val = kamera.read_param_values()

for v in val:
    print(f'{v} HAS FEATURES: {val[v]}')
