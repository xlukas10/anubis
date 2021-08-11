#    Anubis is a program to control industrial cameras and train and use artificial neural networks
#    Copyright (C) 2021 Lukaszczyk Jakub
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.

from abc import abstractmethod
from vimba import *
import threading
import cv2
import os #for working with save path
from datetime import datetime

from global_queue import frame_queue

from config_level import Config_level

class Camera_template:
    """!@brief This class implements backend for the communication with cameras using
    Harvester and any other implemented API. Currently the app contains Harvester
    and API Vimba.
    @details Abstract methods must be implemented when inheriting from this class
    """
    def __init__(self):
        """!@brief Initialize Camera object"""

        ##The name of the acquisition mechanism
        self.name = "Undefined"
        ##Recording state
        self.is_recording = False
        ##Image acquisition state
        self.acquisition_running = False
        ##Detected devices
        self.devices_info = []
        ##Index of active camera for active API
        self.active_camera = 0
        

    @abstractmethod    
    def select_camera(self,selected_device):
        """!@brief choose camera to connect to
        @details Select camera you will be using and set Camera object accordingly
        @param[in] selected_device ID of a camera you want to connect to
        """

    @abstractmethod
    def get_camera_list(self,):
        """!@brief Connected camera discovery
        @return List of Dictionaries cantaining informations about cameras
        """

    @abstractmethod
    def get_parameters(self,feature_queue, flag, visibility = Config_level.Unknown):
        """!@brief Read parameters from camera
        @details Loads all available camera parameters
        @param[in] feature_queue each parameter's dictionary is put into 
            this queue
        @param[in] flag used to signal that the method finished (threading object)
        @param[in] visibility Defines level of parameters that should be put in
            the queue
        @return True if success else False
        """
        
    @abstractmethod
    def read_param_value(self,param_name):
        """!@brief Used to get value of one parameter based on its name
        @param[in] param_name Name of the parametr whose value we want to read
        @return A value of the selected parameter
        """

    @abstractmethod
    def set_parameter(self,parameter_name, new_value):
        """!@brief Method for setting camera's parameters
        @details Sets parameter to value defined by new_value
        @param[in] parameter_name A name of the parameter to be changed
        @param[in] new_value Variable compatible with value key in parameter
        @return True if success else returns False
        """

    @abstractmethod
    def execute_command(self, command_feature):
        """@brief Execute command feature type
        @param[in] command_feature Name of the selected command feature
        """
        
    @abstractmethod
    def get_single_frame(self,):
        """!@brief Grab single frame from camera
        @return Unmodified frame from camera
        """
               
    @abstractmethod
    def load_config(self,path):
        """!@brief Load existing camera configuration
        @param[in] path Defines a path and a name of the file containing the
            configuration of the camera
        @return True if success else False
        """
        
    @abstractmethod
    def save_config(self,path):
        """!@brief Saves configuration of a camera to .xml file
        @param[in] path A path where the file will be saved
        """
        
    @abstractmethod
    def _frame_producer(self):
        """!@brief Gets frames from camera while continuous acquisition is active
        @details Loads frames from camera as they come and stores them
            in a frame queue for consumer thread to process. The thread 
            runs until stream_stop_switch is set
        """
    
    def get_name(self):
        """!@brief Returns name of used mechanism. The name is used to identify it in GUI
        @return Name of the mechanism"""
        return self.name

    def start_acquisition(self,):
        """!@brief Starts continuous acquisition of image frames
        @details Creates a threading object for the right API and starts frame 
            acquisition in that thread (producer thread)
        """
        if not self.acquisition_running:
            self._stream_stop_switch = threading.Event()
            self._frame_producer_thread = threading.Thread(target=self._frame_producer)
            self._frame_producer_thread.daemon = True
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
        self._frame_consumer_thread.daemon = True
        self._frame_consumer_thread.start()
        self.is_recording = True
    
    def stop_recording(self,):
        """!@brief Stops continuous acquisition of image frames and closes all files
        """
        self.stop_acquisition()
        self.is_recording = False

    def disconnect_camera(self):
        """!@brief Disconnect camera and restores the object to its initial state"""
        
        self.stop_recording()
        self.__init__()

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
    
    def _frame_handler(self,cam ,frame):
        """!@brief Defines how to process incoming frames
        @details Is defined for Vimba and defines how to acquire
            whole frame and put into the frame_queue
        """
        raise NotImplementedError
        
    