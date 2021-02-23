# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'anubis.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets
import threading
import time
import win32api #determine refresh rate

#tmp 
import cv2

from global_camera import cam
from global_queue import active_frame_queue

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        #VARIABLES
        
        """
        !@brief Variable used to store device information of detected cameras
        """
        self.detected = []
        self.connected = False
        
        self.interupt_flag = threading.Event()
        self.recording = False
        self.preview_live = False
        
        self.icon_offline = QtGui.QPixmap("./icons/icon_offline.png")
        self.icon_standby = QtGui.QPixmap("./icons/icon_standby.png")
        self.icon_busy = QtGui.QPixmap("./icons/icon_busy.png")
        
        self.status_timer = QtCore.QTimer()
        self.status_timer.timeout.connect(self.clear_status)
        
        
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1005, 610)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        
        #Definition of basic layout
        #----------------------------------------------------------------
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")
        
        self.preview_and_control = QtWidgets.QWidget(self.centralwidget)
        self.preview_and_control.setObjectName("preview_and_control")
        
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.preview_and_control)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        
        #Window with camera preview
        #-------------------------------------------------------------------
        self.preview_area = QtWidgets.QScrollArea(self.preview_and_control)
        self.camera_preview = QtWidgets.QLabel(self.preview_area)
        self.camera_preview.setAutoFillBackground(False)
        self.camera_preview.setText("")
        self.camera_preview.setPixmap(QtGui.QPixmap("default_preview.png"))
        self.camera_preview.setScaledContents(True)
        self.camera_preview.setIndent(-1)
        self.camera_preview.setObjectName("camera_preview")
        self.preview_area.setWidget(self.camera_preview)
        self.verticalLayout_2.addWidget(self.preview_area)
        
        #Definition of buttons to control camera (bottom right)
        #-------------------------------------------------------------------
        self.widget_controls = QtWidgets.QWidget(self.preview_and_control)
        self.widget_controls.setObjectName("widget_controls")
        
        self.gridLayout_4 = QtWidgets.QGridLayout(self.widget_controls)
        self.gridLayout_4.setObjectName("gridLayout_4")
        
        self.btn_define_roi = QtWidgets.QPushButton(self.widget_controls)
        self.btn_define_roi.setObjectName("btn_define_roi")
        self.gridLayout_4.addWidget(self.btn_define_roi, 1, 3, 1, 1)
        
        self.btn_single_frame = QtWidgets.QPushButton(self.widget_controls)
        self.btn_single_frame.setObjectName("btn_single_frame")
        self.btn_single_frame.clicked.connect(self.single_frame)
        self.gridLayout_4.addWidget(self.btn_single_frame, 1, 0, 1, 1)
        
        self.btn_zoom_in = QtWidgets.QPushButton(self.widget_controls)
        self.btn_zoom_in.setObjectName("btn_zoom_in")
        self.gridLayout_4.addWidget(self.btn_zoom_in, 1, 1, 1, 1)
        
        self.btn_zoom_out = QtWidgets.QPushButton(self.widget_controls)
        self.btn_zoom_out.setObjectName("btn_zoom_out")
        self.gridLayout_4.addWidget(self.btn_zoom_out, 1, 2, 1, 1)
        
        self.btn_start_preview = QtWidgets.QPushButton(self.widget_controls)
        self.btn_start_preview.setObjectName("btn_start_preview")
        self.btn_start_preview.clicked.connect(self.preview)
        self.gridLayout_4.addWidget(self.btn_start_preview, 0, 0, 1, 2)
        
        self.btn_start_recording = QtWidgets.QPushButton(self.widget_controls)
        self.btn_start_recording.setObjectName("btn_start_recording")
        self.btn_start_recording.clicked.connect(self.record)
        self.gridLayout_4.addWidget(self.btn_start_recording, 0, 2, 1, 2)
        
        self.verticalLayout_2.addWidget(self.widget_controls)
        self.gridLayout.addWidget(self.preview_and_control, 0, 2, 1, 1)
        
        #Definition of all the tabs on the left side of the UI
        #--------------------------------------------------------------------
        self.tabs = QtWidgets.QTabWidget(self.centralwidget)
        self.tabs.setAccessibleName("")
        self.tabs.setAccessibleDescription("")
        self.tabs.setObjectName("tabs")
        
        #Tab - Connect camera
        self.tab_connect = QtWidgets.QWidget()
        self.tab_connect.setObjectName("tab_connect")
        self.verticalLayout_4 = QtWidgets.QVBoxLayout(self.tab_connect)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.widget_4 = QtWidgets.QWidget(self.tab_connect)
        self.widget_4.setObjectName("widget_4")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout(self.widget_4)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.btn_connect_camera = QtWidgets.QPushButton(self.widget_4)
        self.btn_connect_camera.setObjectName("btn_connect_camera")
        self.horizontalLayout_3.addWidget(self.btn_connect_camera)
        self.btn_refresh_cameras = QtWidgets.QPushButton(self.widget_4)
        self.btn_refresh_cameras.setObjectName("btn_refresh_cameras")
        self.horizontalLayout_3.addWidget(self.btn_refresh_cameras)
        self.btn_disconnect_camera = QtWidgets.QPushButton(self.widget_4)
        self.btn_disconnect_camera.setObjectName("btn_disconnect_camera")
        self.horizontalLayout_3.addWidget(self.btn_disconnect_camera)
        self.verticalLayout_4.addWidget(self.widget_4)
        self.list_detected_cameras = QtWidgets.QListWidget(self.tab_connect)
        self.list_detected_cameras.setObjectName("list_detected_cameras")
        
        
            #Connect refresh camera to the UI
        
        self.btn_refresh_cameras.clicked.connect(self.refresh_cameras)
        
        self.btn_connect_camera.clicked.connect(
            lambda: self.connect_camera(self.list_detected_cameras.currentRow()))
        
        self.list_detected_cameras.itemDoubleClicked.connect(
            lambda: self.connect_camera(self.list_detected_cameras.currentRow()))
        #možná lambda s indexem itemu
        
        self.btn_disconnect_camera.clicked.connect(self.disconnect_camera)
        
        
        
        self.verticalLayout_4.addWidget(self.list_detected_cameras)
        self.tip_add_cti = QtWidgets.QLabel(self.tab_connect)
        self.tip_add_cti.setWordWrap(True)
        self.tip_add_cti.setObjectName("tip_add_cti")
        self.verticalLayout_4.addWidget(self.tip_add_cti)
        self.tabs.addTab(self.tab_connect, "")
        
        #Tab - Configure camera
    #read present parameters on tab change and when read parameters button (To be added) is pressed
        
    
        self.tab_config = QtWidgets.QWidget()
        self.tab_config.setObjectName("tab_config")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.tab_config)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        
        
        self.parameters_scroll = QtWidgets.QScrollArea(self.tab_config)
        
        self.parameters_scroll.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        #self.parameters_scroll.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustToContents)
        self.parameters_scroll.setWidgetResizable(True)
        self.parameters_scroll.setObjectName("parameters_scroll")
        
        self.parameters_layout_widget = QtWidgets.QWidget()
        self.parameters_layout_widget.setGeometry(QtCore.QRect(0, 0, 580, 504))
        self.parameters_layout_widget.setObjectName("parameters_layout_widget")
        
        self.parameters_layout = QtWidgets.QFormLayout(self.parameters_layout_widget)
        self.parameters_layout.setObjectName("parameters_layout")
        l =self.parameters_layout.contentsMargins().left()
        r =self.parameters_layout.contentsMargins().right()
        geom = self.parameters_scroll.geometry()
        geom.adjust(l,0,r,0)
        self.parameters_layout.setGeometry(geom)
        
        
        self.parameters_scroll.setWidget(self.parameters_layout_widget)
        self.verticalLayout_3.addWidget(self.parameters_scroll)
        
        
        self.widget_3 = QtWidgets.QWidget(self.tab_config)
        self.widget_3.setObjectName("widget_3")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.widget_3)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        
        self.btn_save_config = QtWidgets.QPushButton(self.widget_3)
        self.btn_save_config.setObjectName("btn_save_config")
        self.btn_save_config.clicked.connect(self.save_cam_config)
        self.horizontalLayout_2.addWidget(self.btn_save_config)
        
        self.btn_load_config = QtWidgets.QPushButton(self.widget_3)
        self.btn_load_config.setObjectName("btn_load_config")
        self.horizontalLayout_2.addWidget(self.btn_load_config)
        
        self.verticalLayout_3.addWidget(self.widget_3)
        self.tabs.addTab(self.tab_config, "")
        
        #Tab - Configure recording
        self.tab_recording_config = QtWidgets.QWidget()
        self.tab_recording_config.setObjectName("tab_recording_config")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.tab_recording_config)
        self.verticalLayout.setObjectName("verticalLayout")
        
        self.widget_sequence_name = QtWidgets.QWidget(self.tab_recording_config)
        self.widget_sequence_name.setObjectName("widget_sequence_name")
        
        self.formLayout_4 = QtWidgets.QFormLayout(self.widget_sequence_name)
        self.formLayout_4.setObjectName("formLayout_4")
        
        self.label_file_name_recording = QtWidgets.QLabel(self.widget_sequence_name)
        self.label_file_name_recording.setObjectName("label_file_name_recording")
        self.formLayout_4.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.label_file_name_recording)
        
        self.line_edit_sequence_name = QtWidgets.QLineEdit(self.widget_sequence_name)
        self.line_edit_sequence_name.setObjectName("line_edit_sequence_name")
        self.formLayout_4.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.line_edit_sequence_name)
        
        self.verticalLayout.addWidget(self.widget_sequence_name)
        
        self.label_sequence_name = QtWidgets.QLabel(self.tab_recording_config)
        self.label_sequence_name.setObjectName("label_sequence_name")
        self.verticalLayout.addWidget(self.label_sequence_name)
        
        self.widget_sequence_save = QtWidgets.QWidget(self.tab_recording_config)
        self.widget_sequence_save.setObjectName("widget_sequence_save")
        self.formLayout_3 = QtWidgets.QFormLayout(self.widget_sequence_save)
        self.formLayout_3.setObjectName("formLayout_3")
        
        self.file_manager_save_location = QtWidgets.QPushButton(self.widget_sequence_save)
        self.file_manager_save_location.setObjectName("file_manager_save_location")
        self.file_manager_save_location.clicked.connect(self.set_record_path)
        self.formLayout_3.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.file_manager_save_location)
        
        self.line_edit_save_location = QtWidgets.QLineEdit(self.widget_sequence_save)
        self.line_edit_save_location.setObjectName("line_edit_save_location")
        self.formLayout_3.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.line_edit_save_location)
        
        self.verticalLayout.addWidget(self.widget_sequence_save)
        
        self.widget_duration = QtWidgets.QWidget(self.tab_recording_config)
        self.widget_duration.setObjectName("widget_duration")
        self.formLayout_2 = QtWidgets.QFormLayout(self.widget_duration)
        self.formLayout_2.setObjectName("formLayout_2")
        
        self.label_sequence_duration = QtWidgets.QLabel(self.widget_duration)
        self.label_sequence_duration.setObjectName("label_sequence_duration")
        self.formLayout_2.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.label_sequence_duration)
        
        self.line_edit_sequence_duration = QtWidgets.QLineEdit(self.widget_duration)
        self.line_edit_sequence_duration.setObjectName("line_edit_sequence_duration")
        #accept only numbers
        validator = QtGui.QDoubleValidator()
        self.line_edit_sequence_duration.setValidator(validator)
        self.formLayout_2.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.line_edit_sequence_duration)
        
        self.verticalLayout.addWidget(self.widget_duration)
        
        self.label_sequence_duration_tip = QtWidgets.QLabel(self.tab_recording_config)
        self.label_sequence_duration_tip.setObjectName("label_sequence_duration_tip")
        self.verticalLayout.addWidget(self.label_sequence_duration_tip)
        
        spacerItem1 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem1)
        
        self.btn_save_sequence_settings = QtWidgets.QPushButton(self.tab_recording_config)
        self.btn_save_sequence_settings.setObjectName("btn_save_sequence_settings")
        self.btn_save_sequence_settings.clicked.connect(self.save_seq_settings)
        self.verticalLayout.addWidget(self.btn_save_sequence_settings)
        
        self.btn_reset_sequence_settings = QtWidgets.QPushButton(self.tab_recording_config)
        self.btn_reset_sequence_settings.setObjectName("btn_reset_sequence_settings")
        self.btn_reset_sequence_settings.clicked.connect(self.reset_seq_settings)
        self.verticalLayout.addWidget(self.btn_reset_sequence_settings)
        
        self.tabs.addTab(self.tab_recording_config, "")
        
        #Tab - Keras/Tensorflow/Learning,Classification
        self.tab_tensorflow = QtWidgets.QWidget()
        self.tab_tensorflow.setObjectName("tab_tensorflow")
        self.radioButton = QtWidgets.QRadioButton(self.tab_tensorflow)
        self.radioButton.setGeometry(QtCore.QRect(130, 190, 95, 20))
        self.radioButton.setObjectName("radioButton")
        self.tabs.addTab(self.tab_tensorflow, "")
        
        
        self.gridLayout.addWidget(self.tabs, 0, 0, 2, 1)
        #methods to call on tab change
        self.tabs.currentChanged.connect(self.tab_changed)
        #Menubar buttons
        #-------------------------------------------------------------------
        MainWindow.setCentralWidget(self.centralwidget)
        
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1005, 26))
        self.menubar.setObjectName("menubar")
        
        self.menuFile = QtWidgets.QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")
        
        self.menuOptions = QtWidgets.QMenu(self.menubar)
        self.menuOptions.setObjectName("menuOptions")
        
        self.menuHelp = QtWidgets.QMenu(self.menubar)
        self.menuHelp.setObjectName("menuHelp")
        
        MainWindow.setMenuBar(self.menubar)
        
        #Define statusbar
        #------------------------------------------------
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        
        #added manually
        self.status_label = QtWidgets.QLabel()
        self.status_label.setObjectName("status_label")
        self.statusbar.addWidget(self.status_label,stretch=40)
        
        self.camera_icon = QtWidgets.QLabel()
        self.camera_icon.setObjectName("camera_icon")
        self.camera_icon.setScaledContents(True)
        self.statusbar.addPermanentWidget(self.camera_icon)
        
        self.camera_status = QtWidgets.QLabel()
        self.camera_status.setObjectName("camera_status")
        self.statusbar.addPermanentWidget(self.camera_status,stretch=30)
        
        self.fps_status = QtWidgets.QLabel()
        self.fps_status.setObjectName("fps_status")
        self.statusbar.addPermanentWidget(self.fps_status,stretch=10)
        
        self.receive_status = QtWidgets.QLabel()
        self.receive_status.setObjectName("receive_status")
        self.statusbar.addPermanentWidget(self.receive_status,stretch=20)
        
        MainWindow.setStatusBar(self.statusbar)
        
        #Adding individual items to menus in menubar
        #-------------------------------------------------------------
        self.actionAdd_Remove_cti_file = QtWidgets.QAction(MainWindow)
        self.actionAdd_Remove_cti_file.setObjectName("actionAdd_Remove_cti_file")
        
        self.actionOpen_Help = QtWidgets.QAction(MainWindow)
        self.actionOpen_Help.setObjectName("actionOpen_Help")
        
        self.actionRemove_cti_file = QtWidgets.QAction(MainWindow)
        self.actionRemove_cti_file.setObjectName("actionRemove_cti_file")
        
        self.actionSave_frame = QtWidgets.QAction(MainWindow)
        self.actionSave_frame.setObjectName("actionSave_frame")
        
        self.menuFile.addAction(self.actionSave_frame)
        self.menuOptions.addAction(self.actionAdd_Remove_cti_file)
        self.menuOptions.addAction(self.actionRemove_cti_file)
        self.menuHelp.addAction(self.actionOpen_Help)
        
        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuOptions.menuAction())
        self.menubar.addAction(self.menuHelp.menuAction())
        #----------------------------------------------------------------
        
        #--------------------------------------------------------------
        self.retranslateUi(MainWindow)
        self.read_config()
        self.tabs.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
        

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.btn_define_roi.setText(_translate("MainWindow", "Define ROI"))
        self.btn_start_recording.setText(_translate("MainWindow", "Start/Stop recording"))
        self.btn_start_preview.setText(_translate("MainWindow", "Start/Stop preview"))
        self.btn_single_frame.setText(_translate("MainWindow", "Single frame"))
        self.btn_zoom_in.setText(_translate("MainWindow", "Zoom In"))
        self.btn_zoom_out.setText(_translate("MainWindow", "Zoom Out"))
        self.btn_connect_camera.setText(_translate("MainWindow", "Connect"))
        self.btn_refresh_cameras.setText(_translate("MainWindow", "Refresh"))
        self.btn_disconnect_camera.setText(_translate("MainWindow", "Disconnect"))
        self.tip_add_cti.setText(_translate("MainWindow", "Tip: If you can\'t detect your camera try adding new .cti file from your camera vendor (Options->Add .cti file)"))
        self.tabs.setTabText(self.tabs.indexOf(self.tab_connect), _translate("MainWindow", "Connect Camera"))
        self.btn_save_config.setText(_translate("MainWindow", "Save Configuration"))
        self.btn_load_config.setText(_translate("MainWindow", "Load Configuration"))
        self.tabs.setTabText(self.tabs.indexOf(self.tab_config), _translate("MainWindow", "Camera Configuration"))
        self.label_file_name_recording.setText(_translate("MainWindow", "File name"))
        self.label_sequence_name.setText(_translate("MainWindow", "Tip: Use %n for sequence number, %d for date and %t for time stamp "))
        self.file_manager_save_location.setText(_translate("MainWindow", "Save Location"))
        self.label_sequence_duration.setText(_translate("MainWindow", "Sequence duration [s]"))
        self.label_sequence_duration_tip.setText(_translate("MainWindow", "Tip: Leave empty for manual control using Start/Stop recording buttons"))
        self.btn_save_sequence_settings.setText(_translate("MainWindow", "Save settings"))
        self.btn_reset_sequence_settings.setText(_translate("MainWindow", "Default settings"))
        self.tabs.setTabText(self.tabs.indexOf(self.tab_recording_config), _translate("MainWindow", "Recording Configuration"))
        self.radioButton.setText(_translate("MainWindow", "Not ready"))
        self.tabs.setTabText(self.tabs.indexOf(self.tab_tensorflow), _translate("MainWindow", "Tensorflow"))
        self.menuFile.setTitle(_translate("MainWindow", "File"))
        self.menuOptions.setTitle(_translate("MainWindow", "Options"))
        self.menuHelp.setTitle(_translate("MainWindow", "Help"))
        self.actionAdd_Remove_cti_file.setText(_translate("MainWindow", "Add .cti file"))
        self.actionOpen_Help.setText(_translate("MainWindow", "Open Help"))
        self.actionRemove_cti_file.setText(_translate("MainWindow", "Remove .cti file"))
        self.actionSave_frame.setText(_translate("MainWindow", "Save frame"))
        #added manually
        self.camera_status.setText("Camera: Not connected")
        self.receive_status.setText("Received frames: 0")
        self.fps_status.setText("FPS: 0")
        self.camera_icon.setPixmap(self.icon_offline)
        
    
    
    #Start of custom methods (not generated by QtDesigner)
    def refresh_cameras(self):
        """!@brief Calls function to detect connected cameras and prints them
        as items in a list.
        @details If no cameras are present nothing will happen. If cameras are
        detected, all previous item are cleared and cameras detected in this call
        are printed.
        """
        #set status message
        self.set_status_msg("Searching for cameras")
        
        #clear the list so the cameras won't appear twice or more
        self.list_detected_cameras.clear()
        
        #Get a list of cameras and inser each one to the interface as an 
        #entry in the list.
        self.detected = cam.get_camera_list()
        for device in self.detected:
            output = device['model']
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
            
            #Print status message
            self.set_status_msg("Connecting camera")
            
            #Connect camera
            cam.select_camera(self.detected[index]['id_'])
            
            #Change packet size for ethernet camera
#In the future this will happen only for ethernet cameras
            p = cam.get_parameters()
            cam.set_parameter(p['GVSPPacketSize'],1500)
            
            #Set up the status bar
            self.camera_icon.setPixmap(self.icon_standby)
            self.camera_status.setText("Camera: "+self.detected[index]['model'])
            self.connected = True
        
    def record(self):
        """!@brief Starts and stops recording
        @details Is called by start/stop button. Recording is always started 
        manually. Recording ends with another button click or after time set 
        in self.line_edit_sequence_duration passes. Save location and name is 
        determined by the text in self.line_edit_save_location and 
        self.line_edit_sequence_name.
        @TODO method in camera default save location if nothing is defined
        """
        if self.connected:
            if(not self.recording):
                #Change status icon and print status message
                self.camera_icon.setPixmap(self.icon_busy)
                self.set_status_msg("Starting recording")
                
                #Start new recording with defined name and save path
                cam.start_recording(self.line_edit_save_location.text(),
                                    self.line_edit_sequence_name.text(),
                                    'nothing')
                
                self.recording = True
                
                #If automatic sequence duration is set, create thread that will
                #automatically terminate the recording
                if(float(self.line_edit_sequence_duration.text()) > 0):
                    self.interupt_flag.clear()
                    self.seq_duration_thread = threading.Thread(target=self.seq_duration_wait)
                    self.seq_duration_thread.start()
                
                #Start live preview in a new thread
                self.show_preview_thread = threading.Thread(target=self.show_preview)
                self.show_preview_thread.start()
            else:
                #Set status message and standby icon
                self.camera_icon.setPixmap(self.icon_standby)
                self.set_status_msg("Stopping recording")
                
                #Tell automatic sequence duration thread to end
                self.interupt_flag.set()
                
                #End recording
                cam.stop_recording()
                self.recording = False
    
    def seq_duration_wait(self):
        """!@brief Automatic recording interrupt
        @details Let camera record for defined time and if the recording is not
        manually terminated stop the recording
        """
        #wait for the first frame to be received
        while active_frame_queue.empty():
            time.sleep(0.001)
        
        #print status message
        self.set_status_msg("Recording for "+self.line_edit_sequence_duration.text()+"s started")
        
        #wait either for manual recording stop or wait for defined time
        self.interupt_flag.wait(float(self.line_edit_sequence_duration.text()))
        
        #If the recording is still running (not terminated manually), stop 
        #the recording.
        if(self.recording):
            self.record()
    
    def preview(self):
        """!@brief Starts live preview
        @details Unlike recording method, this method does not save frames to 
        drive. Preview picture is rendered in separate thread.
        """
        #continue only if camera is connected
        if self.connected:
            if(not self.preview_live):
                #Set status message and icon
                self.camera_icon.setPixmap(self.icon_busy)
                self.set_status_msg("Starting preview")
                
                #Start camera frame acquisition (not recording)
                cam.start_acquisition()
                
                self.preview_live = True
                
                #Create and run thread to draw frames to gui
                self.show_preview_thread = threading.Thread(target=self.show_preview)
                self.show_preview_thread.start()
            else:
                #Reset status icon and print message
                self.camera_icon.setPixmap(self.icon_standby)
                self.set_status_msg("Stopping preview")
                
                #Stop receiving frames
                cam.stop_acquisition()
                
                self.preview_live = False
        
    def single_frame(self):
        """!@brief Acquire and draw a single frame.
        @details Acquire and draw a single frame.
        """
        #Method runs only if camera is connected
        if self.connected:
            #Set status icon and message
            self.set_status_msg("Receiving single frame")
            self.camera_icon.setPixmap(self.icon_busy)
            
            #Get image
            image = cam.get_single_frame()
            
            #Convert image to proper format fo PyQt
            h, w, ch = image.shape
            bytes_per_line = ch * w
            image = QtGui.QImage(image.data, w, h, bytes_per_line, QtGui.QImage.Format_Grayscale8)
#TODO Get color format dynamically
            image_scaled = image.scaled(self.camera_preview.size().width(), 
                                        self.camera_preview.size().height(), 
                                        QtCore.Qt.KeepAspectRatio)
            
            #Set image to gui
            self.camera_preview.setPixmap(QtGui.QPixmap.fromImage(image_scaled))
            self.camera_preview.show()
            
            #Reset status icon
            self.camera_icon.setPixmap(self.icon_standby)
                
    def show_preview(self):
        """!@brief Draws image from camera in real time.
        @details Acquires images from camera and draws them in real time at 
        the same rate as is display refresh_rate. If the frames come too fast,
        only one at the time is drawn and the rest is dumped
        """
        #Determine refresh rate of used display. This way the method will not
        #run too slowly or redundantly fast.
        device = win32api.EnumDisplayDevices()
        refresh_rate = win32api.EnumDisplaySettings(device.DeviceName, -1).DisplayFrequency
        
        #runs as long as the camera is recording or preview is active
        while self.recording or self.preview_live:
            #Draw only if thre is at least 1 frame to draw
            if not active_frame_queue.qsize() == 0:
                image = active_frame_queue.get_nowait()
                
                #Dump all remaining frames (If frames are received faster than 
                #refresh_rate).
                while not active_frame_queue.qsize() == 0:
                    active_frame_queue.get_nowait()
                
                #Convert image to proper format fo PyQt
                h, w, ch = image.shape
                bytes_per_line = ch * w
                image = QtGui.QImage(image.data, w, h, bytes_per_line, QtGui.QImage.Format_Grayscale8)
#TODO Get color format dynamically

                image_scaled = image.scaled(self.camera_preview.size().width(), 
                                            self.camera_preview.size().height(), 
                                            QtCore.Qt.KeepAspectRatio)
                
                #Set image to gui
                self.camera_preview.setPixmap(QtGui.QPixmap.fromImage(image_scaled))
                self.camera_preview.show()
            #Wait for next display frame
            time.sleep(1/refresh_rate)
    
    def tab_changed(self):
        """!@brief Called when tab changes
        @details Used to do actions when entering specific tab.
        """
        index = self.tabs.currentIndex()
        
        if index == 0:
            pass
        if index == 1:#Camera configuration tab
            #Request parameters from camera and show them in gui
            self.show_parameters()
        
    def show_parameters(self):
        """!@brief Fills layout with feature name and value pairs
        @details Based on the feature type a new label, text area, checkbox or
        combo box is created. In this version all available parameters are shown.
        TODO config level and command feature type
        """
        #Start filling features in only on connected camera
        if self.connected:
            #Status message
            self.set_status_msg("Reading features")
            
            params = cam.get_parameters()
            
            #Keeps track of line in the layout
            num = 0
            
            #Contains all dynamically created widgets
            self.feat_widgets = {}
            
            for param_name, param in params.items():
                
                #Create a new label with name of the feature
                label = QtWidgets.QLabel(self.tab_config)
                label.setObjectName(param["name"])
                label.setText(param["attr_name"])
                
                #If the feature has a tooltip, set it.
                try:
                    label.setToolTip(param["attr_tooltip"])
                finally:
                    pass
                
                #Place the label on the num line of the layout
                self.parameters_layout.setWidget(num, QtWidgets.QFormLayout.LabelRole, label)
                
                #If the feature does not have a value, set it to 0
                if param["attr_value"] == None:
                    param["attr_value"] = 0
                    
                #Based on the feature type, right widget is chosen to hold the
                #feature's value
                
                if param["attr_type"] == "IntFeature":
                    #For int feature a Line edit field is created, but only 
                    #integers can be written in.
                    self.feat_widgets[param["name"]] = QtWidgets.QLineEdit(self.tab_config)
                    validator = QtGui.QIntValidator()
                    self.feat_widgets[param["name"]].setValidator(validator)
                    
                    #Set text to the current value of the feature
                    self.feat_widgets[param["name"]].setText(str(param["attr_value"]))
                    
                    #Call feature change for this feature when enter is pressed in this field.
                    #Text is the value that will be set to the feature.
                    self.feat_widgets[param["name"]].returnPressed.connect(lambda param=param: cam.set_parameter(param,int(self.feat_widgets[param["name"]].text())))
                elif param["attr_type"] == "FloatFeature":
                    #For float feature a Line edit field is created, but only 
                    #real numbers can be written in.
                    self.feat_widgets[param["name"]] = QtWidgets.QLineEdit(self.tab_config)
                    validator = QtGui.QDoubleValidator()
                    self.feat_widgets[param["name"]].setValidator(validator)
                    
                    #Set text to the current value of the feature
                    self.feat_widgets[param["name"]].setText(str(param["attr_value"]))
                    
                    #Call feature change for this feature when enter is pressed in this field.
                    #Text is the value that will be set to the feature.
                    self.feat_widgets[param["name"]].returnPressed.connect(lambda param=param: cam.set_parameter(param,float(self.feat_widgets[param["name"]].text())))
                elif param["attr_type"] == "StringFeature":
                    #For string feature a Line edit field is created.
                    self.feat_widgets[param["name"]] = QtWidgets.QLineEdit(self.tab_config)
                    
                    #Set text to the current value of the feature
                    self.feat_widgets[param["name"]].setText(param["attr_value"])
                    
                    #Call feature change for this feature when enter is pressed in this field.
                    #Text is the value that will be set to the feature.
                    self.feat_widgets[param["name"]].returnPressed.connect(lambda param=param: cam.set_parameter(param,self.feat_widgets[param["name"]].text()))            
                elif param["attr_type"] == "BoolFeature":
                    #For bool feature a checkbox is created.
                    self.feat_widgets[param["name"]] = QtWidgets.QCheckBox(self.tab_config)
                    
                    #If value is true the checkbox is ticked otherwise remains empty
                    self.feat_widgets[param["name"]].setChecked(param["attr_value"])
                    
                    #When state of the checkbox change, the feature is sent to 
                    #the camera and changed to the new state
                    self.feat_widgets[param["name"]].stateChanged.connect(lambda state, param=param: cam.set_parameter(param,self.feat_widgets[param["name"]].isChecked()))
                elif param["attr_type"] == "EnumFeature":
                    #For enum feature a combo box is created.
                    self.feat_widgets[param["name"]] = QtWidgets.QComboBox(self.tab_config)
                    
                    #All available enum states are added as options to the
                    #combo box.
                    for enum in param["attr_enums"]:
                        self.feat_widgets[param["name"]].addItem(str(enum))
                    
                    #Search the options and find the index of the active value
                    index = self.feat_widgets[param["name"]].findText(str(param["attr_value"]), QtCore.Qt.MatchFixedString)
                    
                    #Set found index to be the active one
                    if index >= 0:
                        self.feat_widgets[param["name"]].setCurrentIndex(index)
                    
                    #When different option is selected change the given enum in
                    #the camera
                    self.feat_widgets[param["name"]].activated.connect(lambda state, param=param: cam.set_parameter(param,self.feat_widgets[param["name"]].currentText()))
                else:
                    #If the feature type is not recognized, create a label with 
                    #the text error
                    self.feat_widgets[param["name"]] = QtWidgets.QLabel(self.tab_config)
                    self.feat_widgets[param["name"]].setText("Error")
                    
                #Add newly created widget to the layout on the num line
                self.parameters_layout.setWidget(num, QtWidgets.QFormLayout.FieldRole, self.feat_widgets[param["name"]])
                num = num + 1
                        
    def save_cam_config(self):
        """!@brief Opens file dialog for user to select where to save camera 
        configuration.
        @details Called by Save configuration button. Configuration is saved 
        as an .xml file and its contents are dependent on module used in Camera 
        class to save the config.
        """
        #Open file dialog for choosing a save location and name
        name = QtWidgets.QFileDialog.getSaveFileName(self.centralwidget,
                                                     "Save Configuration",
                                                     filter="XML files (*.xml)",
                                                     directory="config.xml")
        
        #Save camera config to path specified in name (0 index)
        cam.save_config(name[0])
        
    def set_record_path(self):
        """!@brief Opens file dialog for user to set path to save frames.
        @details Method is called by Save Location button. Path is written to 
        the label next to the button and can be further modified.
        """
        #Open file dialog for choosing a folder
        name = QtWidgets.QFileDialog.getExistingDirectory(self.centralwidget,
                                                     "Select Folder",
                                                     )
        
        #Set label text to chosen folder path
        self.line_edit_save_location.setText(name)
        
    def read_config(self):
        """!@brief Loads configuration from config.ini file
        @details This method is called on startup and loads all modifications
        user made to applications default state.
        @TODO load cti files from config
        """
        with open("config.ini", 'r') as config:
            for line in config:
                #reading configuration for recording
                line = line.rstrip('\n')
                if(line.startswith("filename=")):
                    self.line_edit_sequence_name.setText(line.replace("filename=", "", 1))
                elif(line.startswith("save_location=")):
                    self.line_edit_save_location.setText(line.replace("save_location=", "", 1))
                elif(line.startswith("sequence_duration=")):
                    self.line_edit_sequence_duration.setText(line.replace("sequence_duration=", "", 1))
#TODO reading and adding cti files
        
        #Set status update
        self.set_status_msg("Configuration loaded",500)
                
    def reset_seq_settings(self):
        """!@brief Restores default recording settings
        @details Settings are saved to config.ini file. Defaults are hard-coded
        in this method.
        """
        file_contents = []
        
        #Open config file and load its contents
        with open("config.ini", 'r') as config:
            file_contents = config.readlines()
        
        #Find end of Recording config part of the file
        end_of_rec_conf = file_contents.index("CTI_FILES_PATHS\n")
            
        with open("config.ini", 'w') as config:
            #Write default states to the file
            config.write("RECORDING\n")
            config.write("filename=img(%n)\n")
            config.write("save_location=Recording\n")
#maybe set to the documents folder
            config.write("sequence_duration=0\n")
            
            #When at the end of recording config part, just copy the rest of
            #the initial file.
            if(end_of_rec_conf):
                for line in file_contents[end_of_rec_conf:]:
                    config.write(line)
        
        #Fill the Recording tab with updated values
        self.read_config()
        
        #Print status msg
        self.set_status_msg("Configuration restored")
    
    def save_seq_settings(self):
        """!@brief Saves recording settings
        @details Settings are saved to config.ini file. Parameters saved are:
        file name, save, location and sequence duration.
        """
        file_contents = []
        
        #Open config file and load its contents
        with open("config.ini", 'r') as config:
            file_contents = config.readlines()
        
        #Open config file for writing
        with open("config.ini", 'w') as config:
            
            for line in file_contents:
                #Reading configuration for recording
                if(line.startswith("filename=")):
                    config.write("filename=" + self.line_edit_sequence_name.text() + "\n")
                elif(line.startswith("save_location=")):
                    config.write("save_location=" + self.line_edit_save_location.text() + "\n")
                elif(line.startswith("sequence_duration=")):
                    config.write("sequence_duration=" + self.line_edit_sequence_duration.text() + "\n")
                else:
                    #All content not concerning recording is written back without change
                    config.write(line)
        self.set_status_msg("Configuration saved")
                
    def disconnect_camera(self):
        """!@brief Disconnect current camera
        @details Method disconnects camera and setts all statusbar items to 
        their default state.
        """
        #Disconnect only if already connected
        if self.connected:
            #Det default states
            self.connected = False
            self.camera_icon.setPixmap(self.icon_offline)
            self.camera_status.setText("Camera: Not connected")
            self.set_status_msg("Disconnecting camera")
            
            #Disconnect camera
            cam.disconnect_camera()
        
    
    def set_status_msg(self, message, timeout=1500):
        """!@brief Shows message in status bar
        @details Method is called when other methods need to send the user 
        some confrimation or status update.
        @param[in] message Contains text to be displayed in the status bar
        @param[in] timeout For how long should the message be displayed. 
        Defaults to 1.5sec.
        """
        self.status_label.setText(message)
        
        #When time out is reached, connected method 
        #(self.clear_status) is called.
        self.status_timer.start(timeout)
        
    def clear_status(self):
        """!@brief Empties self.status_label in self.statusbar.
        @details Method is called after active message times out.
        """
        self.status_label.setText("")