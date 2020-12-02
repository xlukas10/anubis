# -*- coding: utf-8 -*-
"""
Created on Fri Oct 23 15:25:27 2020

@author: Jakub Lukaszczyk
"""
from harvesters.core import Harvester
from vimba import *
import threading
import queue
import copy

import time#tmp for testing purposes

class Camera:
    def __init__(self, producer_path = 'ZDE VLOZIT DEFAULTNI CESTU'):
        self.h = Harvester()
        self.set_gentl_producer(producer_path)
        self.vendor = 'Other'
        self.is_recording = False
        self.acquisition_running = False
        self.frame_queue = None

    def get_camera_list(self,):
        """!@brief Connected camera discovery
        @details Uses Harvester object to discover all connected cameras
        @return List of Dictionaries cantaining informations about cameras
        @todo WHAT IS THE DICTIONARY FORMAT?
        """
        return self.h.update()
    
    def select_camera(self,selected_device):
        """!@brief choose camera to connect to
        @details Select camera you will be using and set Camera object accordingly
        @param[in] selected_device list index for now in future unique identifier of a camera
        @todo START USING UNIQUE IDENTIFIER
        """
        if(self.h.device_info_list[selected_device].vendor == 'Allied Vision Technologies'):
            self.disconnect_harvester()
            self.vendor = 'Allied Vision Technologies'
            #add code transforming harvester camera index to Vimba
            self.active_camera = selected_device
        else:
            self.cam = self.h.create_image_acquirer(selected_device)
    
    def get_single_frame(self,):
        """!@brief grab single frame from camera
        @details Based on vendor variable chooses right API for acquisition and 
            loads single frame from active_camera
        @return unmodified frame from camera
        """
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
    
    
    
    def set_parameter(self,parameter, new_value):
        """!@brief method for setting camera's parameters
        @details Sets parameter to value defined by new_value
        @param[in] parameter A dictionary with mandatory keys name and value,
                         other keys will be used in later versions
        @param[in] new_value variable compatible with value key in parameter
        """
        if(self.vendor == 'Allied Vision Technologies'):
#EDIT to work well with new parameter dictionary (name, value, maximum etc.)
            with Vimba.get_instance() as vimba:
                cams = vimba.get_all_cameras()
                with cams[self.active_camera] as cam:
                    try:
                        getattr(cam, parameter['name']).set(new_value)
                    except (AttributeError, VimbaFeatureError):
                        pass
        else:                
            return 42
    
    def get_parameters(self,):
        """!@brief Read parameters from camera
        @details Based on self.vendor and self.active_camera chooses right API and
            loads all available camera parameters
        @return A dictionary with parameter names as keys. Each key points to 
            dictionary containing given parameter information: name, 
            value, type, range, increment and max_length 
            if given information exist for the parameter
        """
        if(self.vendor == 'Allied Vision Technologies'):
            with Vimba.get_instance() as vimba:
                cams = vimba.get_all_cameras ()
                with cams[self.active_camera] as cam:
                    features = cam.get_all_features()
                    features_out = {}
                    for feature in features:
                        name = feature.get_name()
                        features_out[name] = {}
                        features_out[name]['name'] = name
                        
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
        """@brief Is not used for now, will be probably removed
        @todo Remove if not changed
        """
#This method may turn out to be redundant (for Vimba it is not needed, depends on harvester implementation)
        values = []
        
        if(self.vendor == 'Allied Vision Technologies'):
            return self.get_parameters()
        else:
            pass
    
    def save_parameters(self,save_path):
        """!@brief saves configuration of a camera to .xml file
        @param[in] save_path A path where the file will be saved
        @todo what will happen if a file already exists
        """
        pass
    
    def start_acquisition(self,frame_queue):
        """!@brief Starts continuous acquisition of image frames
        @details Creates a threading object for the right API and starts frame 
            acquisition in that thread (producer thread)
        @param[in] frame_queue A queue in which the frames will be stored
        """
        #create threading object for vimba, harvester or future api and start the thread
        #this is not nice
        if not self.acquisition_running:
            self.frame_queue = frame_queue
            self._stream_stop_switch = threading.Event()
            self._frame_producer_thread = threading.Thread(target=self._frame_producer)
            self._frame_producer_thread.start()
            self.acquisition_running = True
        pass
    
    def stop_acquisition(self,):
        """!@brief Stops continuous acquisition
        @details Sets stream_stop_switch, acquisition running to false and removes inner link to queue object
        @param[in] parameter A dictionary with mandatory keys name and value,
                         other keys will be used in later versions
        """
        #stop threas created by start_acquisition
        if self.acquisition_running == True:
            self._stream_stop_switch.set()
            #this hopefully stops producer thread
            self.acquisition_running = False
            self.frame_queue = None
        #return is tmp
        return
    
    def _frame_producer(self):
        with Vimba.get_instance() as vimba:
            cams = vimba.get_all_cameras()
            with cams[self.active_camera] as c:
                try:
                    c.start_streaming(handler=self.__frame_handler)
                    self._stream_stop_switch.wait()
                finally:
                    c.stop_streaming()
            pass
        return
    
    def __frame_handler(self,cam ,frame):
        try:
            if frame.get_status() == FrameStatus.Complete:
                if not self.frame_queue.full():
                    frame_copy = copy.deepcopy(frame)
                    self.frame_queue.put_nowait(frame_copy)
            cam.queue_frame(frame)
        except:
            pass
    
    def _frame_consumer(self, file_path, additional_config):
        """!@brief Gradually saves frames generated by _frame_consumer_thread
        @details Uses openCV to saves images from frame_queue 
            to file_path according to additional_config
        @param[in] file_path path where the files will be saved
        @param[in] additional_config unused for now, in future may contain image format, specific naming convention etc.
        @todo If configuration is implemented elsewhere remove this method
        """
        
        
        
    def start_recording(self,file_path,configuration,frame_queue):
        """!@brief Starts continuous acquisition of image frames and saves them to files/video
        @details Calls start_acquisition method and configures camera parameters for optimal acquisition
        @param[in] file_path path where the files will be saved
        @param[in] configuration parameters of output files and possibly camera parameters
        @param[in] frame_queue object to store acquired frames in
        """
        self.cam.start_acquisition()
        self._frame_consumer_thread = threading.Thread(target=self._frame_consumer)
        self._frame_consumer_thread.start()
        self.is_recording = True
    
    def stop_recording(self,):
        """!@brief Stops continuous acquisition of image frames and closes all files
        @details Calls start_acquisition method and configures camera parameters for optimal acquisition
        @param[in] file_path path where the files will be saved
        @param[in] configuration parameters of output files and possibly camera parameters
        @param[in] frame_queue object to store acquired frames in
        """
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
        """!@brief Destroys harvester object so other APIs can access cameras
        """
        self.h.reset()
        

#---------------------------------------------------------------------------
kamera = Camera('C:/Programy/Allied Vision/Vimba_4.0/VimbaGigETL/Bin/Win64/VimbaGigETL.cti')
kamera.get_camera_list()
kamera.select_camera(0)
p = kamera.get_parameters()
kamera.set_parameter(p['GVSPPacketSize'],1500)
print(kamera.get_single_frame())


#for param in p:
#    print(param)
    
val = kamera.read_param_values()

for v in val:
    print(f'{v} HAS FEATURES: {val[v]}')

print('----------------------')
#print(kamera.get_single_frame())    

print('----------------------')
#print(kamera.get_single_frame())

print('----------------------')


fronta = queue.Queue()

kamera.start_acquisition(fronta)
print('Toto se tiskne behem zisku obrazu')
time.sleep(5)
kamera.stop_acquisition()

#fronta.join()



print(fronta.queue)