from camera_template import Camera_template
from config_level import Config_level
from vimba import *
import global_queue
import copy

class Camera_vimba(Camera_template):

    def __init__(self):
        super(Camera_vimba, self).__init__()

        self.name = "Vimba"
        self.vimba = None
        self.cam = None

    
    
    def get_camera_list(self,):
        """!@brief Connected camera discovery
        @details Uses vimba instance to discover all connected cameras
        @return List of Dictionaries cantaining informations about cameras
        """
        self.devices_info.clear()
        with Vimba.get_instance() as vimba:
            cams = vimba.get_all_cameras()
            print(cams)
            for index, camera in enumerate(cams):
                d = {   'id_': camera.get_id(),
                        'model': camera.get_model()
                        }
                self.devices_info.append(d)
        return self.devices_info
     
    def select_camera(self,selected_device):
        """!@brief choose camera to connect to
        @details Select camera you will be using and set Camera object accordingly
        @param[in] selected_device ID of a camera you want to connect to
        """
        with Vimba.get_instance() as vimba:
            cams = vimba.get_all_cameras()
            for index, camera in enumerate(cams):
                if(selected_device == camera.get_id()):
                    self.active_camera = index

        self.vimba = Vimba.get_instance()
        self.vimba._startup()

        cams = vimba.get_all_cameras()
        self.cam = cams[self.active_camera]
        self.cam._open()
        try:
            #Makes sure that the camera won't send packets larger 
            #than destination pc can raceive.
            self.cam.GVSPAdjustPacketSize.run()
            while not self.cam.GVSPAdjustPacketSize.is_done():
                pass
        except (AttributeError, VimbaFeatureError):
                pass

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
        try:
            
            features = self.cam.get_all_features()
            for feature in features:
                feat_vis = int(feature.get_visibility())
                if(feat_vis > 0 and feat_vis <= visibility ):
                    name = feature.get_name()
                    
                    features_out = {}
                    features_out['name'] = name
                    
                    disp_name = feature.get_display_name()
                    features_out['attr_name'] = disp_name
                    
                    #if feature does not have read permission,
                    #go to next iteration
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
                    
                    feature_queue.put(features_out)
            flag.set()
            return True
        except:
            return False

    
    def read_param_value(self,param_name):
        """!@brief Used to get value of one parameter based on its name
        @param[in] param_name Name of the parametr whose value we want to read
        @return A value of the selected parameter
        """
        try:
            return getattr(self.cam, param_name).get()
        except:
            return None
    
    def set_parameter(self,parameter_name, new_value):
        """!@brief Method for setting camera's parameters
        @details Sets parameter to value defined by new_value
        @param[in] parameter_name A name of the parameter to be changed
        @param[in] new_value Variable compatible with value key in parameter
        @return True if success else returns False
        """
       
        try:
            getattr(self.cam, parameter_name).set(new_value)
        except (AttributeError, VimbaFeatureError):
            return False

    def execute_command(self, command_feature):
        """@brief Execute command feature type
        @param[in] command_feature Name of the selected command feature
        """
        
        try:
            getattr(self.cam, command_feature).run()
        except:
            pass
        
    
    def get_single_frame(self,):
        """!@brief Grab single frame from camera
        @return Unmodified frame from camera
        """
        while(True):
            try:
                
                frame = self.cam.get_frame()
                pixel_format = str(frame.get_pixel_format())
                return [frame.as_opencv_image(), pixel_format]
            except:
                pass
            
    
    def load_config(self,path):
        """!@brief Load existing camera configuration
        @param[in] path Defines a path and a name of the file containing the
            configuration of the camera
        @return True if success else False
        """
        try:
            
            self.cam.load_settings(path, PersistType.NoLUT)
            return True
        except:
            return False
    
    
    def save_config(self,path):
        """!@brief Saves configuration of a camera to .xml file
        @param[in] path A path where the file will be saved
        """
        self.cam.save_settings(path, PersistType.NoLUT)
        
    
    def _frame_producer(self):
        """!@brief Gets frames from camera while continuous acquisition is active
        @details Loads frames from camera as they come and stores them
            in a frame queue for consumer thread to process. The thread 
            runs until stream_stop_switch is set
        """
        while(True):
            #if an error occurs, the program will try again until the 
            #stream is established
            try:
                
                try:
                    self.cam.start_streaming(handler=self._frame_handler)
                    self._stream_stop_switch.wait()
                finally:
                    self.cam.stop_streaming()
                    return
            except:
                pass

    def _frame_handler(self,cam ,frame):
        """!@brief Defines how to process incoming frames
        @details Is defined for Vimba and defines how to acquire
            whole frame and put into the frame_queue
        """
        try:
            if not global_queue.frame_queue[self.cam_id].full() and frame.get_status() == FrameStatus.Complete:
                frame_copy = copy.deepcopy(frame)
                if self.is_recording:
                    global_queue.frame_queue[self.cam_id].put_nowait([frame_copy.as_opencv_image(),
                                            str(frame_copy.get_pixel_format())])
                global_queue.active_frame_queue[self.cam_id].put_nowait([frame_copy.as_opencv_image(),
                                               str(frame_copy.get_pixel_format())])
            else:
                pass
            cam.queue_frame(frame)
        except:
            pass

    def disconnect_camera(self):
        """!@brief Disconnect camera and restores the object to its initial state"""
        
        self.stop_recording()
        self.cam._close()
        self.vimba._shutdown()
        global_queue.remove_frame_queue(self.cam_id)
        self.__init__()
    