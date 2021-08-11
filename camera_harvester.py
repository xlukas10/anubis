from camera_template import Camera_template
from config_level import Config_level
from global_queue import frame_queue
from harvesters.core import Harvester
import threading
import queue

class Camera_harvester(Camera_template):

    def __init__(self, producer_paths = None):
        super(Camera_harvester, self).__init__()

        self.name = "Harvester"

        ##Harvester object used to communicate with Harvester module
        self.h = Harvester()

        ##paths to GenTL producers
        self.paths = []
        if(producer_paths):
            for path in producer_paths:
                self.add_gentl_producer(path)
        
        ##Image acquifier object used by Harvester
        self.ia = None
    
    def get_camera_list(self,):
        """!@brief Connected camera discovery
        @details Uses Harvester object to discover all connected cameras
        @return List of Dictionaries cantaining informations about cameras
        """
        
        self.h.update()
        self.devices_info = []
        for device in self.h.device_info_list:
            d = {'id_': device.id_,
                 'model': device.model,
                 'vendor': device.vendor}
            self.devices_info.append(d)
        return self.devices_info
    
    def select_camera(self,selected_device):
        """!@brief choose camera to connect to
        @details Select camera you will be using and set Camera object accordingly
        @param[in] selected_device ID of a camera you want to connect to
        """
        
        #translate selected device to index in harvester's device info list
        for index, camera in enumerate(self.devices_info):
            if camera['id_'] == selected_device:
                harvester_index = index
                break
        
        self.active_camera = harvester_index
        self.ia = self.h.create_image_acquirer(harvester_index)

        try:
            self.ia.remote_device.node_map.GevSCPSPacketSize.value = 1500
        except:
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
                    else:
                        attr = None

                except:
                    attr = None
                
                features_out['attr_type'] = attr
                features_out['attr_enums'] = None
                features_out['attr_cat'] = None
                    
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
                
                
            
                feature_queue.put(features_out)
        flag.set()
        return
        
    
    def read_param_value(self,param_name):
        """!@brief Used to get value of one parameter based on its name
        @param[in] param_name Name of the parametr whose value we want to read
        @return A value of the selected parameter
        """

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
        try:
            getattr(self.ia.remote_device.node_map, parameter_name).value = new_value
        except:
            return False

    def execute_command(self, command_feature):
        """@brief Execute command feature type
        @param[in] command_feature Name of the selected command feature
        """
        try:
            getattr(self.ia.remote_device.node_map, command_feature).execute()
        except:
            pass

    
    def get_single_frame(self,):
        """!@brief Grab single frame from camera
        @return Unmodified frame from camera
        """
        self.ia.start_acquisition()
                
        with self.ia.fetch_buffer() as buffer:
            frame = buffer.payload.components[0]
            pixel_format = self.ia.remote_device.node_map.PixelFormat.value
            return [frame.data, pixel_format]
        
        self.ia.stop_acquisition()
            
    
    def load_config(self,path):
        """!@brief Load existing camera configuration
        @param[in] path Defines a path and a name of the file containing the
            configuration of the camera
        @return True if success else False
        """
        param = {}
        val = None
        attr_type = None
        with open(path, 'r') as config:
            config_dense = (line for line in config if line)
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
                    
            return True

    
    def save_config(self,path):
        """!@brief Saves configuration of a camera to .xml file
        @param[in] path A path where the file will be saved
        """
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
        
    
    def _frame_producer(self):
        """!@brief Gets frames from camera while continuous acquisition is active
        @details Loads frames from camera as they come and stores them
            in a frame queue for consumer thread to process. The thread 
            runs until stream_stop_switch is set
        """
        self.ia.start_acquisition()
            
        while(not self._stream_stop_switch.is_set()):
            with self.ia.fetch_buffer() as buffer:
                frame = buffer.payload.components[0]
                pixel_format = self.ia.remote_device.node_map.PixelFormat.value
                frame_queue.put_nowait([frame.data.copy(), pixel_format])
                #data should contain numpy array which should be compatible
                #with opencv image ig not do some conversion here
        self.ia.stop_acquisition()
    
    def disconnect_camera(self):
        """!@brief Disconnect camera and restores the object to its initial state"""
        
        self.stop_recording()
        self.disconnect_harvester()
        self.__init__()

#______________Unique methods___________________

    def disconnect_harvester(self,):
        """!@brief Destroys harvester object so other APIs can access cameras
        """
        self.h.reset()

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
        @return tuple of a list of remaining gentl producers and boolean value signaling whether the removal was succesful
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


    
    