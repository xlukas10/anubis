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
        
        self.recording = False
        self.preview_live = False
        
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
        
        self.btn_disconnect_camera.clicked.connect(cam.disconnect_camera)
        
        
        
        self.verticalLayout_4.addWidget(self.list_detected_cameras)
        self.tip_add_cti = QtWidgets.QLabel(self.tab_connect)
        self.tip_add_cti.setWordWrap(True)
        self.tip_add_cti.setObjectName("tip_add_cti")
        self.verticalLayout_4.addWidget(self.tip_add_cti)
        self.tabs.addTab(self.tab_connect, "")
        
        #Tab - Configure camera
        self.tab_config = QtWidgets.QWidget()
        self.tab_config.setObjectName("tab_config")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.tab_config)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.formLayout = QtWidgets.QFormLayout()
        self.formLayout.setObjectName("formLayout")
        self.label_test_parameter1 = QtWidgets.QLabel(self.tab_config)
        self.label_test_parameter1.setObjectName("label_test_parameter1")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.label_test_parameter1)
        self.combo_box_test_parameter1 = QtWidgets.QComboBox(self.tab_config)
        self.combo_box_test_parameter1.setObjectName("combo_box_test_parameter1")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.combo_box_test_parameter1)
        self.label_test_parameter2 = QtWidgets.QLabel(self.tab_config)
        self.label_test_parameter2.setObjectName("label_test_parameter2")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.label_test_parameter2)
        self.combo_box_test_parameter3 = QtWidgets.QComboBox(self.tab_config)
        self.combo_box_test_parameter3.setObjectName("combo_box_test_parameter3")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.combo_box_test_parameter3)
        self.label_test_parameter3 = QtWidgets.QLabel(self.tab_config)
        self.label_test_parameter3.setObjectName("label_test_parameter3")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.label_test_parameter3)
        self.combo_box_test_parameter2 = QtWidgets.QComboBox(self.tab_config)
        self.combo_box_test_parameter2.setObjectName("combo_box_test_parameter2")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.combo_box_test_parameter2)
        self.verticalLayout_3.addLayout(self.formLayout)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_3.addItem(spacerItem)
        self.widget_3 = QtWidgets.QWidget(self.tab_config)
        self.widget_3.setObjectName("widget_3")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.widget_3)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.btn_save_config = QtWidgets.QPushButton(self.widget_3)
        self.btn_save_config.setObjectName("btn_save_config")
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
        self.formLayout_2.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.line_edit_sequence_duration)
        self.verticalLayout.addWidget(self.widget_duration)
        self.label_sequence_duration_tip = QtWidgets.QLabel(self.tab_recording_config)
        self.label_sequence_duration_tip.setObjectName("label_sequence_duration_tip")
        self.verticalLayout.addWidget(self.label_sequence_duration_tip)
        spacerItem1 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem1)
        self.btn_save_sequence_settings = QtWidgets.QPushButton(self.tab_recording_config)
        self.btn_save_sequence_settings.setObjectName("btn_save_sequence_settings")
        self.verticalLayout.addWidget(self.btn_save_sequence_settings)
        self.btn_reset_sequence_settings = QtWidgets.QPushButton(self.tab_recording_config)
        self.btn_reset_sequence_settings.setObjectName("btn_reset_sequence_settings")
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
        
        
        #--------------------------------------------------------------
        self.retranslateUi(MainWindow)
        self.tabs.setCurrentIndex(2)
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
        self.label_test_parameter1.setText(_translate("MainWindow", "TextLabel"))
        self.label_test_parameter2.setText(_translate("MainWindow", "TextLabel"))
        self.label_test_parameter3.setText(_translate("MainWindow", "TextLabel"))
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
        print("dszfsu")
        
    
    
    #Start of custom methods (not generated by QtDesigner)
    def refresh_cameras(self):
        """!@brief Calls function to detect connected cameras and prints them
        as items in a list.
        @details If no cameras are present nothing will happen. If cameras are
        detected, all previous item are cleared and cameras detected in this call
        are printed.
        """
        self.list_detected_cameras.clear()
        self.detected = cam.get_camera_list()
        for device in self.detected:
            output = device['model'] #"Model: " + device.model + "Vendor: " + device.vendor
            #in future maybe add icon based on interface type
            self.list_detected_cameras.addItem(output)
        #change format
    
    def connect_camera(self, index):
        """!@brief Connect to selected camera
        @details This method is called either by double clicking camera in a 
        list or by pressing connect button
        @param[in] index index of selected camera in the list
        """
        cam.select_camera(self.detected[index]['id_'])
        p = cam.get_parameters()
        cam.set_parameter(p['GVSPPacketSize'],1500)
        #above will be automated
        #exception for nothing selected
        
    def record(self):
        #will be also called by automatic recording
        #add reading of path from config
        if(not self.recording):
            cam.start_recording('C:/Users/Jakub Lukaszczyk/Documents/Test/','nic')
            
            self.recording = True
            
            #self.preview_flag = threading.Event()#may be unused
            self.show_preview_thread = threading.Thread(target=self.show_preview)
            #self.show_preview()
            self.show_preview_thread.start()
        else:
            cam.stop_recording()
            self.recording = False
            
    def preview(self):
        #add reading of path from config
        if(not self.preview_live):
            cam.start_acquisition()
            
            self.preview_live = True
            
            #self.preview_flag = threading.Event()#may be unused
            self.show_preview_thread = threading.Thread(target=self.show_preview)
            #self.show_preview()
            self.show_preview_thread.start()
        else:
            cam.stop_acquisition()
            self.preview_live = False
        
    def single_frame(self):
        image = cam.get_single_frame()
        h, w, ch = image.shape
        bytes_per_line = ch * w
        image = QtGui.QImage(image.data, w, h, bytes_per_line, QtGui.QImage.Format_Grayscale8)
        image_scaled = image.scaled(self.camera_preview.size().width(), 
                                    self.camera_preview.size().height(), 
                                    QtCore.Qt.KeepAspectRatio)
        self.camera_preview.setPixmap(QtGui.QPixmap.fromImage(image_scaled))
        self.camera_preview.show()
                
    def show_preview(self):
        device = win32api.EnumDisplayDevices()
        refresh_rate = win32api.EnumDisplaySettings(device.DeviceName, -1).DisplayFrequency
        print(refresh_rate)
        
        while self.recording or self.preview_live:
            if not active_frame_queue.qsize() == 0:
                image = active_frame_queue.get_nowait()
                
                while not active_frame_queue.qsize() == 0:
                    active_frame_queue.get_nowait()
                
                h, w, ch = image.shape
                bytes_per_line = ch * w
                image = QtGui.QImage(image.data, w, h, bytes_per_line, QtGui.QImage.Format_Grayscale8)
                
                image_scaled = image.scaled(self.camera_preview.size().width(), 
                                            self.camera_preview.size().height(), 
                                            QtCore.Qt.KeepAspectRatio)
                self.camera_preview.setPixmap(QtGui.QPixmap.fromImage(image_scaled))
                #self.camera_preview.setAlignment(QtCore.Qt.AlignCenter)
                #self.camera_preview.setScaledContents(True)
                #self.camera_preview.setMinimumSize(1,1)
                self.camera_preview.show()
            time.sleep(1/refresh_rate)
            

