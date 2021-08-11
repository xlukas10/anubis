
from camera_vimba import Camera_vimba
from camera_harvester import Camera_harvester


class Camera_connector:
    """!@brief This class is used to offer a bridge between a user interface and implemented
    mechanisms for connecting various cameras
    @details All connected cameras are stored within instance of this class and the class communicate
    with different mechanism by implementing them as a children of the camera_template class"""
    def __init__(self):
        ##Instances of camera control mechanisms. These are used only to list available cameras
        self.mech1 = Camera_vimba()
        self.mech2 = Camera_harvester()
        
        ##Dictionary of mechanisms created above. Is used for easier manipulation with given objects
        self.mechanisms = { 
            self.mech1.get_name(): self.mech1,
            self.mech2.get_name(): self.mech2
        }

        ##List of currently detected devices
        self.detected_devices = []

        ##Gentl producer paths used by Harvester mechanism
        self.producer_paths = []

        ##Holds all actively connected cameras
        self.active_devices = {}
        ##Number of devices connected while application was running. Will always only increment. Serves as a unique identifier for a device
        self.active_devices_count = 0

    def search_for_cameras(self):
        """!@brief Connected camera discovery
        @details Uses all implemented mechanisms to discover all connected cameras
        @return List of Dictionaries cantaining informations about cameras
        """
        self.detected_devices.clear()
        for mechanism in self.mechanisms:
            devices = self.mechanisms[mechanism].get_camera_list()
            name = self.mechanisms[mechanism].get_name()
            for device in devices:
                device["mechanism"] = name
                self.detected_devices.append(device)
            
            
        return self.detected_devices

    def select_camera(self, mechanism, device_id):
        """!@brief choose camera to connect to
        @details Select camera you will be using and set Camera object accordingly
        @param[in] mechanism Mechanism that should establish the connection
        @param[in] device_id ID of a camera you want to connect to
        """
        self.mechanisms[mechanism].select_camera(device_id)

        if(mechanism == "Harvester"):
            self.active_devices[str(self.active_devices_count)] = Camera_harvester()
            for path in self.producer_paths:
                self.active_devices[str(self.active_devices_count)].add_gentl_producer(path)
        elif(mechanism == "Vimba"):
            self.active_devices[str(self.active_devices_count)] = Camera_vimba()
            
        self.active_devices[str(self.active_devices_count)].get_camera_list()
        self.active_devices[str(self.active_devices_count)].select_camera(device_id)
        self.active_devices_count += 1
        return str(self.active_devices_count - 1)

    def disconnect_camera(self, device):
        """!@brief Disconnect camera removes active camera object"""
        self.active_devices[str(device)].disconnect_camera()
        del self.active_devices[str(device)]

#these are temporary and should be connected to the gui better (probably)
    def add_gentl_producer(self, producer_path):
        """!@brief Add a new frame producer to all harvester objects and to harvester mechanism to list cameras
        @details Adds .cti file specified by producer_path to harvester objects
        @param[in] producer_path Path to a .cti file
        @return list of all active producers
        """
        if(not producer_path in self.producer_paths):
            if(producer_path.endswith(".cti")):
                self.producer_paths.append(producer_path)
                self.mechanisms["Harvester"].add_gentl_producer(producer_path) 
                for cam in self.active_devices:
                    try:
                        self.active_devices[cam].add_gentl_producer(producer_path)
                    except:
                        pass
        return self.producer_paths


    def remove_gentl_producer(self, producer_path):
        """!@brief Remove existing frame producer from all existing harvester objects
        @details Removes .cti file specified by producer_path
        @param[in] producer_path Path to a .cti file
        @return tuple of a list of remaining gentl producers and boolean value signaling whether the removal was succesful
        """
        if(producer_path in self.producer_paths):
            self.producer_paths.remove(producer_path)
            self.h.remove_file(producer_path)
            self.mechanisms["Harvester"].remove_gentl_producer(producer_path)
            for cam in self.active_devices:
                try:
                    self.active_devices[cam].remove_gentl_producer(producer_path)
                except:
                    pass
            return (self.producer_paths, True)
        else:
            return(None, False)
       