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
from PyQt5 import QtGui
from datetime import datetime
import enum
import time#tmp for testing purposes
from queue import Queue
import genicam

from global_queue import frame_queue
from global_queue import active_frame_queue

from config_level import Config_level
from vendors import Vendors

class Camera:
    """!@brief This class implements backend for the communication with cameras using
    Harvester and any other implemented API. Currently the app contains Harvester
    and API Vimba.
    """
    def __init__(self, producer_paths = None):
        """!@brief Initialize Camera object"""
        ##Harvester object used to communicate with Harvester module
        self.h = Harvester()
        ##paths to GenTL producers
        self.paths = []
        if(producer_paths):
            self.add_gentl_producer(producer_paths)
            
        ##Camera vendor used to select the correct API
        self.vendor = Vendors.Other
        ##Recording state
        self.is_recording = False
        ##Image acquisition state
        self.acquisition_running = False
        ##Detected devices
        self.devices_info = []
        ##Index of active camera for active API
        self.active_camera = 0
        ##Image acquifier object used by Harvester
        self.ia = None
    
    def get_camera_list(self,):
        """!@brief Connected camera discovery
        @details Uses Harvester object to discover all connected cameras
        @return List of Dictionaries cantaining informations about cameras
        """
        #if there is selected camera which uses different API, temporarily start 
        #Harvester to reload the camera list
        if not self.vendor == Vendors.Other:
            self.add_gentl_producer(self.paths)
        self.h.update()
        self.devices_info = []
        for device in self.h.device_info_list:
            d = {'id_': device.id_,
                 'model': device.model,
                 'vendor': device.vendor}
            self.devices_info.append(d)
        if not self.vendor == Vendors.Other:
            self.disconnect_harvester()
        return self.devices_info
    
    def select_camera(self,selected_device):
        """!@brief choose camera to connect to
        @details Select camera you will be using and set Camera object accordingly
        @param[in] selected_device ID of a camera you want to connect to
        """
        
        if not self.vendor == Vendors.Other:
            self.add_gentl_producer(self.paths)
            self.h.update()
        #translate selected device to index in harvester's device info list
        for index, camera in enumerate(self.devices_info):
                if camera['id_'] == selected_device:
                    harvester_index = index
                    break
        if(self.h.device_info_list[harvester_index].vendor == 'Allied Vision Technologies'):
            self.disconnect_harvester()
            self.vendor = Vendors.Allied_Vision_Technologies
            self.active_camera = self._translate_selected_device(selected_device)
            with Vimba.get_instance() as vimba:
                cams = vimba.get_all_cameras()
                with cams [self.active_camera] as cam:
                    try:
                        #Makes sure that the camera won't send packets larger than destination pc
                        #can raceive
                        cam.GVSPAdjustPacketSize.run()
                        while not cam.GVSPAdjustPacketSize.is_done():
                            pass
                    except (AttributeError, VimbaFeatureError):
                            pass
        else:
            self.active_camera = harvester_index
            self.vendor = Vendors.Other
            self.ia = self.h.create_image_acquirer(harvester_index)

            try:
                self.ia.remote_device.node_map.GevSCPSPacketSize.value = 1500
            except:
                pass
    
    def _translate_selected_device(self, selected_device):
        """!@brief attrs camera ID to index in a list of detected cameras
        @details Index is returned according to currently active camera vendor.
            This method must be called in every method where new connection to a camera is made.
        @param[in] selected_device ID of a camera you want to connect to
        """
        if self.vendor == Vendors.Allied_Vision_Technologies:
            with Vimba.get_instance() as vimba:
                cams = vimba.get_all_cameras()
                for index, camera in enumerate(cams):
                    if camera.get_id() == selected_device:
                        return index#Test this if it works right probably different name for id than id_
        else:
            for index, camera in enumerate(h.device_info_list):
                if camera.id_ == selected_device:
                    return index
    
    def get_parameters(self,feature_queue, flag, visibility = Config_level.Unknown):
        """!@brief Read parameters from camera
        @details Based on self.vendor and self.active_camera chooses right API and
            loads all available camera parameters
        @param[in] feature_queue each parameter's dictionary is put into 
            this queue
        @param[in] flag used to signal that the method finished (threading object)
        @param[in] visibility Defines level of parameters that should be put in
            the queue
        @return A dictionary with parameter names as keys. Each key points to 
            dictionary containing given parameter information: name, 
            value, type, range, increment and max_length 
            if given information exist for the parameter
        """
        #categories are defined by GenICam SFNC
        if(self.vendor == Vendors.Allied_Vision_Technologies):
            #Establishing communication
            with Vimba.get_instance() as vimba:
                cams = vimba.get_all_cameras ()
                with cams[self.active_camera] as cam:
                    features = cam.get_all_features()
                    for feature in features:
                        feat_vis = int(feature.get_visibility())
                        if(feat_vis > 0 and feat_vis <= visibility ):
                            name = feature.get_name()
                            
                            features_out = {}
                            features_out['name'] = name
                            
                            disp_name = feature.get_display_name()
                            features_out['attr_name'] = disp_name
                            
                            #if feature does not have read permission, go to next iteration
                            if(not feature.get_access_mode()[0]):
                                continue
                            
                            #Get feature's write mode
                            try:
                                attr = feature.get_access_mode()[1]
                            except (AttributeError, VimbaFeatureError):
                                attr = None
                            
                            features_out['attr_enabled'] = attr
                            
                            #Get feature's type if it exists
                            try:
                                attr = str(feature.get_type())
                                attr = attr.replace("<class 'vimba.feature.", '')
                                attr = attr.replace("'>","")
                            except (AttributeError, VimbaFeatureError):
                                attr = None
                            
                            features_out['attr_type'] = attr
                            
                            #Get availible enums for enum feature type
                            if(features_out['attr_type'] == "EnumFeature"):
                                try:
                                    attr = feature.get_available_entries()
                                except (AttributeError, VimbaFeatureError):
                                    attr = None
                            
                                features_out['attr_enums'] = attr
                            
                            #Get category for the feature
                            try:
                                attr = feature.get_category()
                            except (AttributeError, VimbaFeatureError):
                                attr = None
                        
                            features_out['attr_cat'] = attr
                                
                            #Get feature's value if it exists
                            try:
                                attr = feature.get()
                            except (AttributeError, VimbaFeatureError):
                                attr = None
                            
                            features_out['attr_value'] = attr
                            
                            #Get feature's range if it exists
                            try:
                                attr = feature.get_range()
                            except (AttributeError, VimbaFeatureError):
                                attr = None
                            
                            features_out['attr_range'] = attr
                            
                            #Get feature's increment if it exists
                            try:
                                attr = feature.get_increment()
                            except (AttributeError, VimbaFeatureError):
                                attr = None
                            
                            features_out['attr_increment'] = attr
                            
                            #Get feature's max length if it exists
                            try:
                                attr = feature.get_max_length()
                            except (AttributeError, VimbaFeatureError):
                                attr = None
                            
                            features_out['attr_max_length'] = attr
                            
                            try:
                                attr = feature.get_tooltip()
                            except (AttributeError, VimbaFeatureError):
                                attr = None
                            
                            features_out['attr_tooltip'] = attr
                            
                            
                            '''
                            try:
                                attr = feature.get_unit()
                                print(attr)
                            except (AttributeError, VimbaFeatureError):
                                attr = None
                            
                            features_out[name]['attr_unit'] = attr
                            '''
                            feature_queue.put(features_out)
                    flag.set()
        else:
            features = dir(self.ia.remote_device.node_map)
            
            for feature in features:
                if(feature.startswith('_')):
                    continue
                try:
                    feature_obj = getattr(self.ia.remote_device.node_map, feature).node
                    feature = getattr(self.ia.remote_device.node_map, feature)
                    #Some information is accessible through harvester feature, 
                    #for some information we need to go deeper into Genapi itself
                    feat_acc = feature_obj.get_access_mode()
                except:
                    continue
                
                #according to genicam standard
                #0 - not implemented
                #1 - not availablle
                #3 - write only
                #4 - read only
                #5 - read and write
                if(feat_acc == 0 or feat_acc == 1):
                    continue

                feat_vis = feature_obj.visibility
                print(feat_vis)
                if( feat_vis < visibility ):
                    features_out = {}
                    features_out['name'] = feature_obj.name
                    #disp_name = feature.get_display_name()
                    features_out['attr_name'] = feature_obj.display_name
                    
                    
                    
                    #Set feature's write mode
                    try:
                        if(feat_acc == 5 or feat_acc == 3):
                            attr = False
                        else:
                            attr = True
                        print("sss")
                    except:
                        attr = None
                    
                    features_out['attr_enabled'] = attr
                    
                    #Get feature's type if it exists
                    #intfIValue = 0       #: IValue interface
                    #intfIBase = 1        #: IBase interface
                    #intfIInteger = 2     #: IInteger interface
                    #intfIBoolean = 3     #: IBoolean interface
                    #intfICommand = 4     #: ICommand interface
                    #intfIFloat = 5       #: IFloat interface
                    #intfIString = 6      #: IString interface
                    #intfIRegister = 7    #: IRegister interface
                    #intfICategory = 8    #: ICategory interface
                    #intfIEnumeration = 9 #: IEnumeration interface
                    #ntfIEnumEntry = 10   #: IEnumEntry interface
                    #intfIPort       = 11  #: IPort interface

                    try:
                        attr = feature_obj.principal_interface_type
                        if(attr == 2):
                            attr = "IntFeature"
                        elif(attr == 3):
                            attr = "BoolFeature"
                        elif(attr == 4):
                            attr = "CommandFeature"
                        elif(attr == 5):
                            attr = "FloatFeature"
                        elif(attr == 6):
                            attr = "StringFeature"
                        elif(attr == 9):
                            attr = "EnumFeature"
                            print("found enum")
                        else:
                            attr = None
                        print(feature_obj.name)
#todo category feature
                    except:
                        attr = None
                    
                    features_out['attr_type'] = attr
                    
                    #Get availible enums for enum feature type
                    if(features_out['attr_type'] == "EnumFeature"):
                        pass#Not yet implemetnted
                        #print(dir(feature_obj))
                        #print("here")
                        #attr = feature_obj.selected_features
                        #print(attr)
                    
                        attr = None
                    
                        features_out['attr_enums'] = attr
                    
                    #Get category for the feature
                    try:
                        attr = "category"#feature.category
#not yet implemented
                    except:
                        attr = None
                
                    features_out['attr_cat'] = attr
                        
                    #Get feature's value if it exists
                    try:
                        attr = feature.value
                    except:
                        attr = None
                    
                    features_out['attr_value'] = attr
                    
                    #Get feature's range if it exists
                    try:
                        attr = [feature.min, feature.max]
                    except:
                        attr = None
                    
                    features_out['attr_range'] = attr
                    
                    #Get feature's increment if it exists
                    try:
                        attr = feature.inc
                    except:
                        attr = None
                    
                    features_out['attr_increment'] = attr
                    
                    #Get feature's max length if it exists
                    try:
                        attr = feature.max_length
                    except:
                        attr = None
                    
                    features_out['attr_max_length'] = attr
                    
                    try:
                        attr = feature_obj.tooltip
                    except:
                        attr = None
                    
                    features_out['attr_tooltip'] = attr
                    
                    
                    '''
                    try:
                        attr = feature.get_unit()
                        print(attr)
                    except (AttributeError, VimbaFeatureError):
                        attr = None
                    
                    features_out[name]['attr_unit'] = attr
                    '''
                
                    feature_queue.put(features_out)
            flag.set()
            return
    
    def read_param_value(self,param_name):
        """!@brief Used to get value of one parameter based on its name
        @param[in] param_name Name of the parametr whose value we want to read
        @return A value of the selected parameter
        """

        if(self.vendor == Vendors.Allied_Vision_Technologies):
            try:
                with Vimba.get_instance() as vimba:
                    cams = vimba.get_all_cameras ()
                    with cams[self.active_camera] as cam:
                            return getattr(cam, param_name).get()
            except:
                return None
        else:
            try:
                val = getattr(self.ia.remote_device.node_map, param_name).value
                return val
            except:
                return None
    
    def set_parameter(self,parameter_name, new_value):
        """!@brief Method for setting camera's parameters
        @details Sets parameter to value defined by new_value
        @param[in] parameter_name A name of the parameter to be changed
        @param[in] new_value Variable compatible with value key in parameter
        @return True if success else returns False
        """
        print(parameter_name)
        print(new_value)
        if(self.vendor == Vendors.Allied_Vision_Technologies):
#EDIT to work well with new parameter dictionary (name, value, maximum etc.)
            with Vimba.get_instance() as vimba:
                cams = vimba.get_all_cameras()
                with cams[self.active_camera] as cam:
                    try:
                        getattr(cam, parameter_name).set(new_value)
                    except (AttributeError, VimbaFeatureError):
                        print("ne")
                        return False
        else:
            try:
                getattr(self.ia.remote_device.node_map, parameter_name).value = new_value
            except:
                return False
        
        return True
    
    def execute_command(self, command_feature):
        """@brief Execute command feature type
        @param[in] command_feature Dictionary containing at least 'name' of 
            the selected feature
        """
        #not tested
        if(self.vendor == Vendors.Allied_Vision_Technologies):
            with Vimba.get_instance() as vimba:
                cams = vimba.get_all_cameras ()
                with cams[self.active_camera] as cam:
                    try:
                        getattr(cam, command_feature['name']).run()
                    except:
                        pass
        else:
            try:
                getattr(self.ia.remote_device.node_map, command_feature['name']).execute()
            except:
                pass
    
    def get_single_frame(self,):
        """!@brief Grab single frame from camera
        @details Based on vendor variable chooses right API for acquisition and 
            loads single frame from active_camera
        @return Unmodified frame from camera
        """
        if(self.vendor == Vendors.Allied_Vision_Technologies):
            with Vimba.get_instance() as vimba:
                cams = vimba.get_all_cameras()
                with cams [self.active_camera] as cam:
                    frame = cam.get_frame()
                    pixel_format = str(frame.get_pixel_format())
                    return [frame.as_opencv_image(), pixel_format]
        else:
            self.ia.start_acquisition()
                
            with self.ia.fetch_buffer() as buffer:
                frame = buffer.payload.components[0]
                pixel_format = self.ia.remote_device.node_map.PixelFormat.value
                return [frame.data, pixel_format]
            
            self.ia.stop_acquisition()
    
    def start_acquisition(self,):
        """!@brief Starts continuous acquisition of image frames
        @details Creates a threading object for the right API and starts frame 
            acquisition in that thread (producer thread)
        """
        
        if not self.acquisition_running:
            self._stream_stop_switch = threading.Event()
            self._frame_producer_thread = threading.Thread(target=self._frame_producer)
            self._frame_producer_thread.start()
            self.acquisition_running = True
    
    def stop_acquisition(self,):
        """!@brief Stops continuous acquisition
        @details Sets stream_stop_switch, acquisition running to false and 
            removes inner link to queue object
        """
        #stop threads created by start_acquisition
        if self.acquisition_running == True:
            self._stream_stop_switch.set()
            #this stops producer thread
            self.acquisition_running = False
    
    def start_recording(self,folder_path,name_scheme,configuration,):
        """!@brief Starts continuous acquisition of image frames and saves them to files/video
        @details Calls start_acquisition method and configures camera parameters for optimal acquisition
        @param[in] folder_path Path where the files will be saved
        @param[in] name_scheme Naming template for saved files
        @param[in] configuration Parameters of output files and possibly camera parameters
        """
        self.start_acquisition()
        self._frame_consumer_thread = threading.Thread(target=self._frame_consumer, args=(folder_path,name_scheme,configuration))
        self._frame_consumer_thread.start()
        self.is_recording = True
    
    def stop_recording(self,):
        """!@brief Stops continuous acquisition of image frames and closes all files
        """
        self.stop_acquisition()
        self.is_recording = False
    
    def load_config(self,path):
        """!@brief Load existing camera configuration
        @param[in] path Defines a path and a name of the file containing the
            configuration of the camera
        """
        if self.vendor == Vendors.Allied_Vision_Technologies:
            with Vimba.get_instance() as vimba:
                cams = vimba.get_all_cameras ()
                with cams[self.active_camera] as cam:
                    cam.load_settings(path, PersistType.NoLUT)
        else:
            param = {}
            val = None
            attr_type = None
            with open(path, 'r') as config:
                config_dense = (line for line in config if line) #removes blank lines
                for line in config_dense:
                    line = line.rstrip('\n')
                    if line.startswith('attr_value') and param:
                        val = line.split('=')
                        
                        if(attr_type[1] == 'IntFeature'):
                            self.set_parameter(param, int(val[1]))
                        elif(attr_type[1] == 'FloatFeature'):
                            self.set_parameter(param, float(val[1]))
                        elif(attr_type[1] == 'EnumFeature'):
                            self.set_parameter(param, val[1])
                        elif(attr_type[1] == 'BoolFeature'):
                            if(val[1] == 'True'):
                                self.set_parameter(param, True)
                            else:
                                self.set_parameter(param, False)
                        elif(attr_type[1] == 'StringFeature'):
                            self.set_parameter(param, val[1])
                        
                        val = None
                        param.clear()
                        attr_type = None
                    elif line.startswith('attr_type') and param:
                        attr_type = line.split('=')
                        
                    elif line.startswith('name'):
                        param['name'] = line.split('=')[1]
                        val = None
    
    def save_config(self,path):
        """!@brief Saves configuration of a camera to .xml file
        @param[in] path A path where the file will be saved
        """
        if self.vendor == Vendors.Allied_Vision_Technologies:
            with Vimba.get_instance() as vimba:
                cams = vimba.get_all_cameras ()
                with cams[self.active_camera] as c:
                    #cam.save_settings(path + file_name + '.xml', PersistType.NoLUT)
                    c.save_settings(path, PersistType.NoLUT)
        else:
            #At the time of writing this code not Harvester nor genapi for Python 
            #supported saving .xml config, so the format of saved data created
            #here is nonstandard and simplified for now.
            #More here https://github.com/genicam/harvesters/issues/152
            
            parameters = queue.Queue()
            tmp_flag = threading.Event()
            self.get_parameters(parameters, tmp_flag, Config_level.Invisible)

            with open(path, 'w') as config:
                while not parameters.empty():
                    param = parameters.get_nowait()
                    for key,val in param.items():
                        config.write(key + "=" + str(val) + '\n')
                    config.write('\n')
    
    def add_gentl_producer(self,producer_path):
        """!@brief Add a new frame producer to the harvester object
        @details Adds .cti file specified by producer_path to the harvester object
        @param[in] producer_path Path to a .cti file
        @return list of all active producers
        """
        if(not producer_path in self.paths):
            if(producer_path.endswith(".cti")):
                self.h.add_file(producer_path)
                self.paths.append(producer_path)
        
        return self.paths
    
    def remove_gentl_producer(self,producer_path):
        """!@brief Remove existing frame producer from the harvester object
        @details Removes .cti file specified by producer_path from the harvester object
        @param[in] producer_path Path to a .cti file
        """
        if(producer_path in self.paths):
            self.paths.remove(producer_path)
            self.h.remove_file(producer_path)
            return (self.paths, True)
        else:
            return(None, False)
    
    def get_gentl_producers(self):
        """!@brief Used to get a list of all path used by Harvesters in a
        present moment
        @return List of defined cti file paths
        """
        return self.paths
    
    def disconnect_harvester(self,):
        """!@brief Destroys harvester object so other APIs can access cameras
        """
        self.h.reset()
    
    def disconnect_camera(self):
        """!@brief Disconnect camera and restores the object to its initial state"""
        
        self.stop_recording()
        self.disconnect_harvester()
        self.__init__(self.paths)
    
    def _frame_producer(self):
        """!@brief Gets frames from camera while continuous acquisition is active
        @details Loads frames from camera as they come and stores them
            in a frame queue for consumer thread to process. The thread 
            runs until stream_stop_switch is set
        """
        
        if self.vendor == Vendors.Allied_Vision_Technologies:
            with Vimba.get_instance() as vimba:
                cams = vimba.get_all_cameras()
                with cams[self.active_camera] as c:
                    try:
                        c.start_streaming(handler=self._frame_handler_vimba)
                        self._stream_stop_switch.wait()
                    finally:
                        c.stop_streaming()
        else:
            self.ia.start_acquisition()
            
            while(not self._stream_stop_switch.is_set()):
                with self.ia.fetch_buffer() as buffer:
                    frame = buffer.payload.components[0]
                    pixel_format = self.ia.remote_device.node_map.PixelFormat.value
                    frame_queue.put_nowait([frame.data.copy(), pixel_format])
                    #data should contain numpy array which should be compatible
                    #with opencv image ig not do some conversion here
            self.ia.stop_acquisition()
    
    def _frame_consumer(self, folder_path, name_scheme, additional_config):
        """!@brief Gradually saves frames generated by _frame_producer_thread
        @details Uses openCV to saves images from frame_queue 
            to file_path according to additional_config
        @param[in] folder_path Path where the files will be saved
        @param[in] name_scheme Defines how to name output files
        @param[in] additional_config Reserved.
        """
        if(folder_path[-1] != '/'):
            folder_path = folder_path + '/'
            
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
            
        n = name_scheme.find("%n")
        if(n==-1):
            name_scheme = name_scheme + "(%n)"
            
        num = 0
        extension = '.png'
        print("consuming")
        while self.acquisition_running:
            if not frame_queue.empty(): 
                frame = frame_queue.get_nowait()[0]
                name = name_scheme
                name = name.replace("%t", datetime.now().strftime("%H-%M-%S"))
                name = name.replace("%d", datetime.now().strftime("%d-%m-%Y"))
                name = name.replace("%n", str(num))
                #tranform image to format for ui show
                cv2.imwrite(folder_path + name + extension, frame)
                #because th __frame_handler saves only image data, I can save frame directly here without conversions
                #use rather os.path.join method
                num += 1
    
    def _frame_handler_vimba(self,cam ,frame):
        """!@brief Defines how to process incoming frames
        @details Is defined for Vimba and defines how to acquire
            whole frame and put into the frame_queue
        """
        try:
            if not frame_queue.full() and frame.get_status() == FrameStatus.Complete:
                frame_copy = copy.deepcopy(frame)
                if self.is_recording:
                    frame_queue.put_nowait([frame_copy.as_opencv_image(),
                                            str(frame_copy.get_pixel_format())])
                active_frame_queue.put_nowait([frame_copy.as_opencv_image(),
                                               str(frame_copy.get_pixel_format())])
            else:
                print("queue full")
            cam.queue_frame(frame)
        except:
            pass
    