from PyQt5 import QtGui, QtWidgets 
import global_camera
from PyQt5.QtCore import pyqtSignal as Signal
from vimba import *

class Tab_connect(QtWidgets.QWidget):
    #signals
    ##Used to send status message to the GUI
    send_status_msg = Signal(str, int)
    ##Signals current state of camera connection
    connection_update = Signal(bool, int, str)#connected, state - 0=disconnected 1=standby 2=busy, camera name

    def __init__(self):
        super(Tab_connect, self).__init__()

        self.v = Vimba.get_instance()
        self.v._startup()
        self.connected = False

        self.add_widgets()
        self.connect_actions()
        self.set_texts()

    def add_widgets(self):
        self.setObjectName("tab_connect")
        self.layout_main = QtWidgets.QVBoxLayout(self)
        self.layout_main.setObjectName("layout_main")
        self.widget_4 = QtWidgets.QWidget(self)
        self.widget_4.setObjectName("widget_4")
        self.layout_buttons = QtWidgets.QHBoxLayout(self.widget_4)
        self.layout_buttons.setObjectName("layout_buttons")
        self.btn_connect_camera = QtWidgets.QPushButton(self.widget_4)
        self.btn_connect_camera.setObjectName("btn_connect_camera")
        self.layout_buttons.addWidget(self.btn_connect_camera)
        self.btn_refresh_cameras = QtWidgets.QPushButton(self.widget_4)
        self.btn_refresh_cameras.setObjectName("btn_refresh_cameras")
        self.layout_buttons.addWidget(self.btn_refresh_cameras)
        self.btn_disconnect_camera = QtWidgets.QPushButton(self.widget_4)
        self.btn_disconnect_camera.setObjectName("btn_disconnect_camera")
        self.layout_buttons.addWidget(self.btn_disconnect_camera)
        self.layout_main.addWidget(self.widget_4)
        self.list_detected_cameras = QtWidgets.QListWidget(self)
        self.list_detected_cameras.setObjectName("list_detected_cameras")
        
        self.layout_main.addWidget(self.list_detected_cameras)
        
        self.frame_cti = QtWidgets.QFrame(self)
        self.frame_cti.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_cti.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_cti.setObjectName("frame_cti")
        self.layout_cti_settings = QtWidgets.QGridLayout(self.frame_cti)
        self.layout_cti_settings.setObjectName("gridLayout_7")
        self.btn_remove_cti = QtWidgets.QPushButton(self.frame_cti)
        self.btn_remove_cti.setObjectName("btn_remove_cti")
        self.layout_cti_settings.addWidget(self.btn_remove_cti, 0, 3, 1, 1)
        self.btn_add_cti = QtWidgets.QPushButton(self.frame_cti)
        self.btn_add_cti.setObjectName("btn_add_cti")
        self.layout_cti_settings.addWidget(self.btn_add_cti, 0, 2, 1, 1)
        self.tip_add_cti = QtWidgets.QLabel(self.frame_cti)
        self.tip_add_cti.setWordWrap(True)
        self.tip_add_cti.setObjectName("tip_add_cti")
        self.layout_cti_settings.addWidget(self.tip_add_cti, 0, 0, 2, 1)
        self.combo_remove_cti = QtWidgets.QComboBox(self.frame_cti)
        self.combo_remove_cti.setObjectName("combo_remove_cti")
        self.layout_cti_settings.addWidget(self.combo_remove_cti, 1, 2, 1, 2)
        self.layout_main.addWidget(self.frame_cti)

    def connect_actions(self):
        self.btn_refresh_cameras.clicked.connect(self.refresh_cameras)
        self.btn_add_cti.clicked.connect(self.add_cti)
        self.btn_remove_cti.clicked.connect(self.remove_cti)
        
        self.btn_connect_camera.clicked.connect(
            lambda: self.connect_camera(self.list_detected_cameras.currentRow()))
        
        self.list_detected_cameras.itemDoubleClicked.connect(
            lambda: self.connect_camera(self.list_detected_cameras.currentRow()))
        #možná lambda s indexem itemu
        
        self.btn_disconnect_camera.clicked.connect(self.disconnect_camera)

    def set_texts(self):
        self.btn_connect_camera.setText("Connect")
        self.btn_refresh_cameras.setText("Refresh")
        self.btn_disconnect_camera.setText("Disconnect")
        self.tip_add_cti.setText("Tip: If you can\'t detect your camera try adding new .cti file from your camera vendor")
        self.btn_add_cti.setText("Add a new .cti file")
        self.btn_remove_cti.setText("Remove selected .cti")
        

    def add_cti(self):
        """!@brief Used to load a new GenTL producer file.
        @details User can select a new file using file dialog.
        """
        path = QtWidgets.QFileDialog.getOpenFileName(self,
                                                     "Load GenTL producer",
                                                     filter="CTI files (*.cti)")
        
        #If user changes his/her mind and closes the file dialog, don't
        #add empty producer
        if(path[0]):
            cti_files = global_camera.cams.add_gentl_producer(path[0])
            try:
                self.combo_remove_cti.clear()
                self.combo_remove_cti.addItems(cti_files)
            except:
                pass
            
            self.send_status_msg.emit("File added", 0)
    
    def remove_cti(self):
        """!@brief Used to remove selected GenTL producer file.
        @details User can select file from combo box.
        """
        
        cti_files, removed = global_camera.cams.remove_gentl_producer(self.combo_remove_cti.currentText())
        if(removed):
            self.send_status_msg.emit("File removed", 0)
            self.combo_remove_cti.clear()
            self.combo_remove_cti.addItems(cti_files)
    
    def refresh_cameras(self):
        """!@brief Calls function to detect connected cameras and prints them
        as items in a list.
        @details If no cameras are present nothing will happen. If cameras are
        detected, all previous item are cleared and cameras detected in this call
        are printed.
        """
        #set status message
        self.send_status_msg.emit("Searching for cameras", 1500)
        
        #clear the list so the cameras won't appear twice or more
        self.list_detected_cameras.clear()
        
        #Get a list of cameras and inser each one to the interface as an 
        #entry in the list.
        self.detected = global_camera.cams.search_for_cameras()
        for device in self.detected:
            output = device['mechanism'] + ': ' + device['model']
#in  the future maybe add icon based on interface type
            self.list_detected_cameras.addItem(output)
    
    def connect_camera(self, index):
        """!@brief Connect to selected camera
        @details This method is called either by double clicking camera in a 
        list or by pressing connect button
        @param[in] index index of selected camera in the list
        """
        #Something must be selected
        if index != -1:
            
            #If some camera is connected, disconnect it first
            if self.connected:
               self.disconnect_camera()
                          
            #set green background to the selected camera
            self.list_detected_cameras.item(index).setBackground(QtGui.QColor('#70BF4E'))
            
            #Print status message
            self.send_status_msg.emit("Connecting camera", 0)
            
            #Connect camera
            global_camera.change_active_cam(global_camera.cams.select_camera(self.detected[index]['mechanism'], self.detected[index]['id_']))
            
            self.send_status_msg.emit("Camera connected", 0)
            
            #Set up the status bar
            
            self.connected = True
            self.connection_update.emit(True, 1, self.detected[index]['model'])
    
    def disconnect_camera(self):
        """!@brief Disconnect current camera
        @details Method disconnects camera and sets all statusbar items to 
        their default state.
        """
        #Disconnect only if already connected
        if self.connected:
            #Get default states
            self.connected = False
            self.connection_update.emit(False, 0, "Not connected")
            
            self.send_status_msg.emit("Disconnecting camera", 0)
            
            
            #Disconnect camera
            global_camera.cams.disconnect_camera(int(global_camera.active_cam))
            
            self.send_status_msg.emit("Camera disconnected", 0)
            
            #Imidiately search for new cameras
            self.refresh_cameras()