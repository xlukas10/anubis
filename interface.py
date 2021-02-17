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
        
        self.interupt_flag = threading.Event()
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
            cam.start_recording(self.line_edit_save_location.text(),
                                self.line_edit_sequence_name.text(),
                                'nic')
            
            self.recording = True
            
            if(float(self.line_edit_sequence_duration.text()) > 0):
                print("starting automated seq")
                self.interupt_flag.clear()
                self.seq_duration_thread = threading.Thread(target=self.seq_duration_wait)
                self.seq_duration_thread.start()
            
            self.show_preview_thread = threading.Thread(target=self.show_preview)
            self.show_preview_thread.start()
            
            
        else:
            self.interupt_flag.set()
            cam.stop_recording()
            self.recording = False
    
    def seq_duration_wait(self):
        print("waiting on dur")
        #wait for acquisitiioon to truly begin
        while active_frame_queue.empty():
            time.sleep(0.001)
        self.interupt_flag.wait(float(self.line_edit_sequence_duration.text()))
        print("timeout or interupt")
        if(self.recording):
            print("should be only timeout")
            self.record()
    
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
    
    def tab_changed(self):
        index = self.tabs.currentIndex()
        
        if index == 0:
            pass
        if index == 1:
            #Connect tab change to configure to trigger parameter refresh
            print("showing")
            self.show_parameters()
        
    def show_parameters(self):
        #FeatureTypes = Union[IntFeature, FloatFeature, StringFeature, BoolFeature, EnumFeature,CommandFeature, RawFeature]
        params = cam.get_parameters()
        num = 0
        self.feat_widgets = {}
        for param_name, param in params.items():
            label = QtWidgets.QLabel(self.tab_config)
            label.setObjectName(param["name"])
            #if(param["attr_unit"] != None):
            #    label.setText(param["attr_name"] + "[" + param["attr_unit"] + "]")
            #else:
            #    label.setText(param["attr_name"])
            label.setText(param["attr_name"])
            try:
                label.setToolTip(param["attr_tooltip"])
            finally:
                pass
            self.parameters_layout.setWidget(num, QtWidgets.QFormLayout.LabelRole, label)
            
            
            widget = None
            if param["attr_value"] == None:
                param["attr_value"] = 0
            if param["attr_type"] == "IntFeature":
                self.feat_widgets[param["name"]] = QtWidgets.QLineEdit(self.tab_config)
                validator = QtGui.QIntValidator()
                self.feat_widgets[param["name"]].setValidator(validator)
                self.feat_widgets[param["name"]].setText(str(param["attr_value"]))
                
                self.feat_widgets[param["name"]].returnPressed.connect(lambda param=param: cam.set_parameter(param,int(self.feat_widgets[param["name"]].text())))
            elif param["attr_type"] == "FloatFeature":
                self.feat_widgets[param["name"]] = QtWidgets.QLineEdit(self.tab_config)
                validator = QtGui.QDoubleValidator()
                self.feat_widgets[param["name"]].setValidator(validator)
                self.feat_widgets[param["name"]].setText(str(param["attr_value"]))
                
                self.feat_widgets[param["name"]].returnPressed.connect(lambda param=param: cam.set_parameter(param,float(self.feat_widgets[param["name"]].text())))
            elif param["attr_type"] == "StringFeature":
                self.feat_widgets[param["name"]] = QtWidgets.QLineEdit(self.tab_config)
                self.feat_widgets[param["name"]].setText(param["attr_value"])
                
                self.feat_widgets[param["name"]].returnPressed.connect(lambda param=param: cam.set_parameter(param,self.feat_widgets[param["name"]].text()))            
            elif param["attr_type"] == "BoolFeature":
                self.feat_widgets[param["name"]] = QtWidgets.QCheckBox(self.tab_config)
                self.feat_widgets[param["name"]].setChecked(param["attr_value"])
                
                self.feat_widgets[param["name"]].stateChanged.connect(lambda state, param=param: cam.set_parameter(param,self.feat_widgets[param["name"]].isChecked()))
            elif param["attr_type"] == "EnumFeature":
                self.feat_widgets[param["name"]] = QtWidgets.QComboBox(self.tab_config)
                for enum in param["attr_enums"]:
                    self.feat_widgets[param["name"]].addItem(str(enum))
                index = self.feat_widgets[param["name"]].findText(str(param["attr_value"]), QtCore.Qt.MatchFixedString)
                if index >= 0:
                    self.feat_widgets[param["name"]].setCurrentIndex(index)
                #add reamining options
                
                self.feat_widgets[param["name"]].activated.connect(lambda state, param=param: cam.set_parameter(param,self.feat_widgets[param["name"]].currentText()))
            
            else:
                self.feat_widgets[param["name"]] = QtWidgets.QLabel(self.tab_config)
                self.feat_widgets[param["name"]].setText("Error")
            self.parameters_layout.setWidget(num, QtWidgets.QFormLayout.FieldRole, self.feat_widgets[param["name"]])
            num = num + 1
            
            #self.parameters_layout
            #param["name"] label
            #if param type bool
                #param["value"] combo box 
                    #options - param["možne hodnoty"]
            #else if param type int
                #param[value] number box?
                    #if new value > max value
                        #new valie = max value
    
                        
    def save_cam_config(self):
        name = QtWidgets.QFileDialog.getSaveFileName(self.centralwidget,
                                                     "Save Configuration",
                                                     filter="XML files (*.xml)",
                                                     directory="config.xml")
        cam.save_config(name[0])
        
    def set_record_path(self):
        name = QtWidgets.QFileDialog.getExistingDirectory(self.centralwidget,
                                                     "Select Folder",
                                                     )
        print(name)
        self.line_edit_save_location.setText(name)
        
        #cam.save_config(name[0])
    def read_config(self):
        with open("config.ini", 'r') as config:
            #reading configuration for recording
            for line in config:
                #reading configuration for recording
                line = line.rstrip('\n')
                if(line.startswith("filename=")):
                    self.line_edit_sequence_name.setText(line.replace("filename=", "", 1))
                elif(line.startswith("save_location=")):
                    self.line_edit_save_location.setText(line.replace("save_location=", "", 1))
                elif(line.startswith("sequence_duration=")):
                    self.line_edit_sequence_duration.setText(line.replace("sequence_duration=", "", 1))
                #reading and adding cti files
            
                
    def reset_seq_settings(self):
        file_contents = []
        with open("config.ini", 'r') as config:
            file_contents = config.readlines()
        end_of_rec_conf = file_contents.index("CTI_FILES_PATHS\n")
            
        with open("config.ini", 'w') as config:
            config.write("RECORDING\n")
            config.write("filename=img(%n)\n")
            config.write("save_location=Recording\n")#maybe se to the documents folder
            config.write("sequence_duration=0\n")
            if(end_of_rec_conf):
                for line in file_contents[end_of_rec_conf:]:
                    config.write(line)
        self.read_config()
    
    def save_seq_settings(self):
        file_contents = []
        with open("config.ini", 'r') as config:
            file_contents = config.readlines()
            
        with open("config.ini", 'w') as config:
            #reading configuration for recording
            for line in file_contents:
                #reading configuration for recording
                if(line.startswith("filename=")):
                    config.write("filename=" + self.line_edit_sequence_name.text() + "\n")
                elif(line.startswith("save_location=")):
                    config.write("save_location=" + self.line_edit_save_location.text() + "\n")
                elif(line.startswith("sequence_duration=")):
                    config.write("sequence_duration=" + self.line_edit_sequence_duration.text() + "\n")
                else:
                    config.write(line)
                #reading and adding cti files
        