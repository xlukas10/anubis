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
import cv2
import os #for working with save path

import time#tmp for testing purposes

from global_queue import frame_queue

class Camera:
    def __init__(self, producer_path = 'ZDE VLOZIT DEFAULTNI CESTU'):
        self.h = Harvester()
        self.set_gentl_producer(producer_path)
        self.vendor = 'Other'
        self.is_recording = False
        self.acquisition_running = False

    def get_camera_list(self,):
        """!@brief Connected camera discovery
        @details Uses Harvester object to discover all connected cameras
        @return List of Dictionaries cantaining informations about cameras
        @todo WHAT IS THE DICTIONARY FORMAT?
        """
        self.h.update()
        return self.h.device_info_list
    
    def __translate_selected_device(self, selected_device):
        """!@brief Translates camera ID to index in a list of detected cameras
        @details Index is returned according to currently active camera vendor.
            This method must be called in every method where new connection to a camera is made.
        @param[in] selected_device ID of a camera you want to connect to
        """
        if self.vendor == 'Allied Vision Technologies':
            with Vimba.get_instance() as vimba:
                cams = vimba.get_all_cameras()
                for index, camera in enumerate(cams):
                    if camera.get_id() == selected_device:
                        return index#Test this if it works right probably different name for id than id_
        else:
            for index, camera in enumerate(h.device_info_list):
                if camera.id_ == selected_device:
                    return index
    
    def select_camera(self,selected_device):
        """!@brief choose camera to connect to
        @details Select camera you will be using and set Camera object accordingly
        @param[in] selected_device ID of a camera you want to connect to
        """
        
        #translate selected device to index in harvester's device info list
        for index, camera in enumerate(self.h.device_info_list):
                if camera.id_ == selected_device:
                    harvester_index = index
                    break
        if(self.h.device_info_list[harvester_index].vendor == 'Allied Vision Technologies'):
            self.disconnect_harvester()
            self.vendor = 'Allied Vision Technologies'
            self.active_camera = self.__translate_selected_device(selected_device)
        else:
            self.active_camera = harvester_index
            self.vendor = 'Other'
            self.cam = self.h.create_image_acquirer(harvester_index)
    
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
    
    def load_config(self,path):
        """@brief load existing camera configuration
        """
        pass
    
    def save_config(self,path, file_name):
        """!@brief saves configuration of a camera to .xml file
        @param[in] save_path A path where the file will be saved
        @todo what will happen if a file already exists
        """
        if self.vendor=='Allied Vision Technologies':
            with Vimba.get_instance() as vimba:
                cams = vimba.get_all_cameras ()
                with cams[self.active_camera] as cam:
                    cam.save_settings(path + file_name + '.xml', PersistType.NoLUT)
    
    def start_acquisition(self,):
        """!@brief Starts continuous acquisition of image frames
        @details Creates a threading object for the right API and starts frame 
            acquisition in that thread (producer thread)
        """
        #create threading object for vimba, harvester or future api and start the thread
        if not self.acquisition_running:
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
        #stop threads created by start_acquisition
        if self.acquisition_running == True:
            self._stream_stop_switch.set()
            #this stops producer thread
            self.acquisition_running = False
    
    def _frame_producer(self):
        """!@brief Gets frames from camera while continuous acquisition is active
        @details Loads frames from camera as they come and stores them
            in a frame queue for consumer thread to process. The thread runs until stream_stop_switch is set
        @todo implement for harvesters and define interface for APIs to come
        """
#implement if vendor mechanism
        with Vimba.get_instance() as vimba:
            cams = vimba.get_all_cameras()
            with cams[self.active_camera] as c:
                try:
                    c.start_streaming(handler=self.__frame_handler_vimba)
                    self._stream_stop_switch.wait()
                finally:
                    c.stop_streaming()
            pass
        return
    
    def __frame_handler_vimba(self,cam ,frame):
        """!@brief Defines how to process incoming frames
        @details Currently is defined for Vimba and defines how to acquire
            whole frame and put into the frame_queue
        @todo implement for harvesters and define interface for APIs to come
        """
        try:
            #if frame.get_status() == FrameStatus.Complete:
            if not frame_queue.full():
                frame_copy = copy.deepcopy(frame)
                frame_queue.put_nowait(frame_copy.as_opencv_image())
                #Saving only image data, metadata are lost - is it a problem?
            else:
                print("queue full")
            #else:
            #    print("frame not complete")
            cam.queue_frame(frame)
        except:
            print("Something went wrong.")
    
    def _frame_consumer(self, file_path, additional_config):
        """!@brief Gradually saves frames generated by _frame_consumer_thread
        @details Uses openCV to saves images from frame_queue 
            to file_path according to additional_config
        @param[in] file_path path where the files will be saved
        @param[in] additional_config unused for now, in future may contain image format, specific naming convention etc.
        @todo If configuration is implemented elsewhere remove this method
        @todo Implement for harvester as well
        """
        num = 0
        extension = '.png'
        while self.acquisition_running:
            if not frame_queue.empty(): 
                frame = frame_queue.get_nowait()
                cv2.imwrite(file_path + str(num) + extension, frame)
                #because th __frame_handler saves only image data, I can save frame directly here without conversions
#use rather os.path.join method
                num += 1
        
        
    def start_recording(self,file_path,configuration,):
        """!@brief Starts continuous acquisition of image frames and saves them to files/video
        @details Calls start_acquisition method and configures camera parameters for optimal acquisition
        @param[in] file_path path where the files will be saved
        @param[in] configuration parameters of output files and possibly camera parameters
        """
        self.start_acquisition()
        self._frame_consumer_thread = threading.Thread(target=self._frame_consumer, args=(file_path,configuration))
        self._frame_consumer_thread.start()
        self.is_recording = True
    
    def stop_recording(self,):
        """!@brief Stops continuous acquisition of image frames and closes all files
        @details Calls start_acquisition method and configures camera parameters for optimal acquisition
        @param[in] file_path path where the files will be saved
        @param[in] configuration parameters of output files and possibly camera parameters
        """
        self.stop_acquisition()
        self.is_recording = False
    
    
    def set_gentl_producer(self,producer_path):
        """!@brief Add a new frame producer to the harvester object
        @details adds .cti file specified by producer_path to the harvester object
        @param[in] producer_path path to a .cti file
        @todo producer_path probably should be also attached to
            application configuration for later use
        """
        self.h.add_file(producer_path)
    
    def remove_gentl_producer(self,producer_path):
        """!@brief Remove existing frame producer from the harvester object
        @details removes .cti file specified by producer_path from the harvester object
        @param[in] producer_path path to a .cti file
        @todo producer_path probably should be also removed from
            application configuration
        """
        self.h.remove_file(producer_path)

    def disconnect_harvester(self,):
        """!@brief Destroys harvester object so other APIs can access cameras
        """
        self.h.reset()
        
    def disconnect_camera(self):
        self.__init__()
        

#---------------------------------------------------------------------------

kamera = Camera('C:/Programy/Allied Vision/Vimba_4.0/VimbaGigETL/Bin/Win64/VimbaGigETL.cti')
l = kamera.get_camera_list()
print(l)
print("ajaj")
kamera.select_camera('DEV_000F314C64AE')
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

#kamera.start_acquisition(fronta)
#print('Toto se tiskne behem zisku obrazu')
#time.sleep(5)
#kamera.stop_acquisition()

#fronta.join()



#print(fronta.queue)
kamera.start_recording('C:/Users/Jakub Lukaszczyk/Documents/','nic')
time.sleep(10)
kamera.stop_recording()

kamera.save_config('c:/Users/Jakub Lukaszczyk/Documents/', 'konfigurace1')
