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



from PyQt5 import QtCore, QtGui, QtWidgets
from tab_connect import Tab_connect
from tab_recording import Tab_recording
from tab_tensorflow import Tab_tensorflow
import threading
import time
import win32api
import os
from queue import Queue
import webbrowser


from global_camera import cam
from global_queue import active_frame_queue
from computer_vision import Computer_vision
from config_level import Config_level


class Ui_MainWindow(QtCore.QObject):
    """!@brief Main class for user interface
    @details This file implements Ui_MainWindow class which defines the application's
    graphical user interface. Methods setupUi and retranslateUi are generated from
    QtDesigner using pyuic5 tool. When modifying the GUI these methods should be
    carefully edited with regards to calls at their ends which are used to bind
    methods to the widgets and initialize other variables.
    Methods in the class are mainly used to check some conditions and run methods
    of other connected classes like Camera and Computer_vision.
    """
    def __init__(self):
        """!@brief Initialize the class and all its variables
        """
        
        super(Ui_MainWindow,self).__init__()
        
        ##Automatic feature refresh timer
        self.feat_refresh_timer  = QtCore.QTimer(self)
        self.feat_refresh_timer.setInterval(4000)
        self.feat_refresh_timer.timeout.connect(self.update_parameters)
        self.feat_refresh_timer.timeout.connect(self.start_refresh_parameters)
        self.feat_refresh_timer.start()
        
        ##Holds current frame displayed in the GUI
        self.image_pixmap = None
        ##Width of the preview area
        self.w_preview = 0
        ##Height of the preview area
        self.h_preview = 0
        
        ##Is tensorflow model loaded
        self.model_loaded = False
                    
        ##Last value of the dragging in the preview area - x axis
        self.move_x_prev = 0
        ##Last value of the dragging in the preview area - y axis
        self.move_y_prev = 0
        ##Used to store values of parameters when automatically refreshing them
        self.parameter_values = {}
        
        ##Flag used when running various parameter refreshing methods
        self.update_completed_flag = threading.Event()
        self.update_completed_flag.set()
        
        ##Flag used when running various parameter refreshing methods
        self.update_flag = threading.Event()
        
        ##Value of current preview zoom in %/100
        self.preview_zoom = 1
        ##Resizing image to preview area size instead of using zoom
        self.preview_fit = True
        
        ##Holds parameter category paths for tree widget
        self.top_items = {}
        ##Holds children widgets for tree widget
        self.children_items = {}
        
        ##Contains all dynamically created widgets for parameters
        self.feat_widgets = {}
        ##Contains all dynamically created labels of parameters
        self.feat_labels = {}
        ##Stores dictionaries of every parameter until they are processed to the GUI
        self.feat_queue = Queue()
        
        ##List of detected cameras
        self.detected = []
        ##Is camera connected
        self.connected = False
        
        ##Widget used to transfer GUI changes from thread into the main thread while updating preview
        self.resize_signal = QtWidgets.QLineEdit()
        self.resize_signal.textChanged.connect(self.update_img)
        
        ##Widget used to transfer GUI changes from thread into the main thread while showing parameters
        self.parameters_signal = QtWidgets.QLineEdit()
        self.parameters_signal.textChanged.connect(self.show_parameters)
        
        ##Signals that a recording was stopped, either by timer or manually
        self.interupt_flag = threading.Event()
        
        ##State of recording
        self.recording = False
        ##State of live preview
        self.preview_live = False
        
        ##Holds image of offline state of a camera
        self.icon_offline = QtGui.QPixmap("./icons/icon_offline.png")
        ##Holds image of standby state of a camera
        self.icon_standby = QtGui.QPixmap("./icons/icon_standby.png")
        ##Holds image of busy state of a camera
        self.icon_busy = QtGui.QPixmap("./icons/icon_busy.png")
        
        ##Current frames per second received from the camera
        self.fps = 0.0
        ##Total sum of received frames for active camera session
        self.received = 0
        
        ##Timer used to show a status messages for specific time window
        self.status_timer = QtCore.QTimer()
        
        
        
    def setupUi(self, MainWindow):
        """!@brief Create GUI widgets
        @details Excluding section marked as added manually, the whole 
        method is generated by pyuic5 tool and should not be modified otherwise
        because the changes are hard to track outside added manually section. 
        In this method all widgets, tabs, buttons etc. are created but not 
        named yet.
        """
        
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
        #disables scrollbars in preview window
        #self.preview_area.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        #self.preview_area.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.preview_area.installEventFilter(self)
        
        self.camera_preview = QtWidgets.QLabel(self.preview_area)
        self.camera_preview.setAutoFillBackground(False)
        self.camera_preview.setText("")
        self.camera_preview.setSizePolicy(QtWidgets.QSizePolicy.Ignored, QtWidgets.QSizePolicy.Ignored)
        self.camera_preview.setPixmap(QtGui.QPixmap("default_preview.png"))
        self.camera_preview.setScaledContents(False)
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
        
        self.btn_zoom_in = QtWidgets.QPushButton(self.widget_controls)
        self.btn_zoom_in.setObjectName("btn_zoom_in")
        self.gridLayout_4.addWidget(self.btn_zoom_in, 0, 2, 1, 1)
        
        self.btn_zoom_out = QtWidgets.QPushButton(self.widget_controls)
        self.btn_zoom_out.setObjectName("btn_zoom_out")
        self.gridLayout_4.addWidget(self.btn_zoom_out, 0, 3, 1, 1)
        
        self.btn_zoom_100 = QtWidgets.QPushButton(self.widget_controls)
        self.btn_zoom_100.setObjectName("btn_zoom_100")
        self.gridLayout_4.addWidget(self.btn_zoom_100, 1, 3, 1, 1)
        
        self.btn_zoom_fit = QtWidgets.QPushButton(self.widget_controls)
        self.btn_zoom_fit.setObjectName("btn_zoom_fit")
        self.gridLayout_4.addWidget(self.btn_zoom_fit, 1, 2, 1, 1)
        
        self.btn_single_frame = QtWidgets.QPushButton(self.widget_controls)
        self.btn_single_frame.setObjectName("btn_single_frame")
        self.gridLayout_4.addWidget(self.btn_single_frame, 1, 0, 1, 1)
        
        self.btn_start_preview = QtWidgets.QPushButton(self.widget_controls)
        self.btn_start_preview.setObjectName("btn_start_preview")
        
        self.gridLayout_4.addWidget(self.btn_start_preview, 0, 0, 1, 1)
        
        self.btn_start_recording = QtWidgets.QPushButton(self.widget_controls)
        self.btn_start_recording.setObjectName("btn_start_recording")
        
        self.gridLayout_4.addWidget(self.btn_start_recording, 0, 1, 1, 1)
        
        self.verticalLayout_2.addWidget(self.widget_controls)
        self.gridLayout.addWidget(self.preview_and_control, 0, 2, 1, 1)
        
        #Definition of all the tabs on the left side of the UI
        #--------------------------------------------------------------------
        self.tabs = QtWidgets.QTabWidget(self.centralwidget)
        self.tabs.setAccessibleName("")
        self.tabs.setAccessibleDescription("")
        self.tabs.setObjectName("tabs")
        
        #Tab - Connect camera

        self.tab_connect = Tab_connect()
        self.tabs.addTab(self.tab_connect, "")


        #Tab - Configure camera
    #read present parameters on tab change and when read parameters button (To be added) is pressed
        
    
        self.tab_config = QtWidgets.QWidget()
        self.tab_config.setObjectName("tab_config")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.tab_config)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        
        self.frame_config_level = QtWidgets.QFrame(self.tab_config)
        self.frame_config_level.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_config_level.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_config_level.setObjectName("frame_config_level")
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout(self.frame_config_level)
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.label_config_level = QtWidgets.QLabel(self.frame_config_level)
        self.label_config_level.setObjectName("label_config_level")
        self.horizontalLayout_5.addWidget(self.label_config_level)
        self.combo_config_level = QtWidgets.QComboBox(self.frame_config_level)
        self.combo_config_level.setObjectName("combo_config_level")
        self.combo_config_level.addItem("")
        self.combo_config_level.addItem("")
        self.combo_config_level.addItem("")
        
        self.horizontalLayout_5.addWidget(self.combo_config_level)
        self.verticalLayout_3.addWidget(self.frame_config_level)
        
        
        self.tree_features = QtWidgets.QTreeWidget(self.tab_config)
        self.tree_features.setObjectName("tree_features")
        self.tree_features.setColumnWidth(0,250)
        self.verticalLayout_3.addWidget(self.tree_features)
        
        
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
        
        

        self.tab_recording_config = Tab_recording()
        self.tabs.addTab(self.tab_recording_config, "")
        #Tab - Keras/Tensorflow/Learning,Classification
        
        self.tab_tensorflow = Tab_tensorflow()
        self.tabs.addTab(self.tab_tensorflow, "")
        
        self.gridLayout.addWidget(self.tabs, 0, 0, 2, 1)
        #methods to call on tab change
        self.tabs.currentChanged.connect(self.tab_changed)
        #Menubar buttons
        #-------------------------------------------------------------------
        MainWindow.setCentralWidget(self.centralwidget)
        
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1208, 26))
        self.menubar.setObjectName("menubar")
        self.menuFile = QtWidgets.QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")
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
        
        self.action_save_frame = QtWidgets.QAction(MainWindow)
        self.action_save_frame.setObjectName("action_save_frame")
        
        self.action_save_settings = QtWidgets.QAction(MainWindow)
        self.action_save_settings.setObjectName("action_save_settings")
        
        self.actionAbout_Anubis = QtWidgets.QAction(MainWindow)
        self.actionAbout_Anubis.setObjectName("actionAbout_Anubis")
        
        self.actionGit_Repository = QtWidgets.QAction(MainWindow)
        self.actionGit_Repository.setObjectName("actionGit_Repository")
        
        self.actionSave_camera_config = QtWidgets.QAction(MainWindow)
        self.actionSave_camera_config.setObjectName("actionSave_camera_config")
        
        self.actionLoad_camera_config = QtWidgets.QAction(MainWindow)
        self.actionLoad_camera_config.setObjectName("actionLoad_camera_config")
        
        self.menuFile.addAction(self.actionSave_camera_config)
        self.menuFile.addAction(self.actionLoad_camera_config)
        self.menuFile.addAction(self.actionAdd_Remove_cti_file)
        self.menuFile.addAction(self.actionRemove_cti_file)
        
        self.menuFile.addSeparator()
        
        self.menuFile.addAction(self.action_save_settings)
        self.menuHelp.addAction(self.actionOpen_Help)
        
        self.menuHelp.addSeparator()
        
        self.menuHelp.addAction(self.actionAbout_Anubis)
        self.menuHelp.addAction(self.actionGit_Repository)
        
        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuHelp.menuAction())
        #----------------------------------------------------------------
        
        #--------------------------------------------------------------
        
        self.setup_validators()
        self.connect_actions()
        self.retranslateUi(MainWindow)
        self.read_config()
        self.tabs.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
        
    
    def retranslateUi(self, MainWindow):
        """!@brief Sets names of widgets.
        @details Widgets are created in setupUi method, this method sets text
        of the buttons, tabs and default texts for all of these widgets.
        """
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Anubis"))
        self.btn_zoom_100.setText(_translate("MainWindow", "Zoom to 100%"))
        self.btn_zoom_fit.setText(_translate("MainWindow", "Fit to window"))
        self.btn_start_recording.setText(_translate("MainWindow", "Start/Stop recording"))
        self.btn_start_preview.setText(_translate("MainWindow", "Start/Stop preview"))
        self.btn_single_frame.setText(_translate("MainWindow", "Single frame"))
        self.btn_zoom_in.setText(_translate("MainWindow", "Zoom In"))
        self.btn_zoom_out.setText(_translate("MainWindow", "Zoom Out"))
        self.tabs.setTabText(self.tabs.indexOf(self.tab_connect), _translate("MainWindow", "Connect Camera"))
        self.label_config_level.setText(_translate("MainWindow", "Configuration level"))
        self.combo_config_level.setItemText(0, _translate("MainWindow", "Beginner"))
        self.combo_config_level.setItemText(1, _translate("MainWindow", "Expert"))
        self.combo_config_level.setItemText(2, _translate("MainWindow", "Guru"))
        self.tree_features.headerItem().setText(0, _translate("MainWindow", "Feature"))
        self.tree_features.headerItem().setText(1, _translate("MainWindow", "Value"))
        self.btn_save_config.setText(_translate("MainWindow", "Save Configuration"))
        self.btn_load_config.setText(_translate("MainWindow", "Load Configuration"))
        self.tabs.setTabText(self.tabs.indexOf(self.tab_config), _translate("MainWindow", "Configure Camera"))
        self.tabs.setTabText(self.tabs.indexOf(self.tab_recording_config), _translate("MainWindow", "Configure Recording"))
        self.tabs.setTabText(self.tabs.indexOf(self.tab_tensorflow), _translate("MainWindow", "Tensorflow"))
        
        #self.tabs.setTabText(self.tabs.indexOf(self.tab_tensorflow), _translate("MainWindow", "Tensorflow"))
        self.menuFile.setTitle(_translate("MainWindow", "File"))
        self.menuHelp.setTitle(_translate("MainWindow", "Help"))
        self.actionAdd_Remove_cti_file.setText(_translate("MainWindow", "Add .cti file"))
        self.actionOpen_Help.setText(_translate("MainWindow", "Open Help"))
        self.actionRemove_cti_file.setText(_translate("MainWindow", "Remove .cti file"))
        self.action_save_frame.setText(_translate("MainWindow", "Save frame"))
        self.action_save_settings.setText(_translate("MainWindow", "Save app state"))
        self.action_save_settings.setToolTip(_translate("MainWindow", "Save modifications made to application settings"))
        self.actionAbout_Anubis.setText(_translate("MainWindow", "About Anubis"))
        self.actionGit_Repository.setText(_translate("MainWindow", "Git Repository"))
        self.actionSave_camera_config.setText(_translate("MainWindow", "Save camera config"))
        self.actionLoad_camera_config.setText(_translate("MainWindow", "Load camera config"))
        
        #added manually
        self.camera_status.setText("Camera: Not connected")
        self.receive_status.setText("Received frames: 0")
        self.fps_status.setText("FPS: 0")
        self.camera_icon.setPixmap(self.icon_offline)
    
#Start of custom methods (not generated by QtDesigner)
    def connect_actions(self):
        """!@brief Connect method calls to appropriate widgets
        @details All static widgets are connected to some method either in this
        class or call method of another object. In this method all such bindings
        done excluding dynamically created widgets like camera's features
        """
        
        self.btn_zoom_out.clicked.connect(lambda: self.set_zoom(-1))
        self.btn_zoom_fit.clicked.connect(lambda: self.set_zoom(0))
        self.btn_zoom_in.clicked.connect(lambda: self.set_zoom(1))
        self.btn_zoom_100.clicked.connect(lambda: self.set_zoom(100))
        self.btn_single_frame.clicked.connect(self.single_frame)
        self.btn_start_preview.clicked.connect(self.preview)
        self.btn_start_recording.clicked.connect(self.record)

        #CONNECTING TAB
        self.tab_connect.send_status_msg.connect(self.set_status_msg)
        self.tab_connect.connection_update.connect(self.update_camera_status)
        self.status_timer.timeout.connect(self.clear_status)

        self.tab_recording_config.send_status_msg.connect(self.set_status_msg)
        self.tab_tensorflow.send_status_msg.connect(self.set_status_msg)


        self.combo_config_level.currentIndexChanged.connect(self.load_parameters)
        self.btn_save_config.clicked.connect(self.save_cam_config)
        self.btn_load_config.clicked.connect(self.load_cam_config)
        
        self.action_save_settings.triggered.connect(self.save_cti_config)
        self.actionRemove_cti_file.triggered.connect(self.tab_connect.remove_cti)
        self.actionAdd_Remove_cti_file.triggered.connect(self.tab_connect.add_cti)
        self.actionSave_camera_config.triggered.connect(self.save_cam_config)
        self.actionLoad_camera_config.triggered.connect(self.load_cam_config)
        self.actionOpen_Help.triggered.connect(lambda: 
                            webbrowser.open(
                                os.path.dirname(os.path.realpath(__file__)) + 
                                "/Help//index.html",
                                new=2))
        self.actionGit_Repository.triggered.connect(lambda: 
                            webbrowser.open("https://github.com/xlukas10/anubis",new=2))
        self.actionAbout_Anubis.triggered.connect(self.about)
    
    def setup_validators(self):
        """!@brief create input constrains for various widgets
        @details if a text widget needs certain input type, the validators are
        set up here. For example setting prohibited characters of the file saved.
        """
        pass
    
    def eventFilter(self, obj, event):
        """!@brief Implements dragging inside preview area
        @details whin user cliks and drags inside of a preview area, this 
        method is called and do the scrolling based on the distance dragged in
        each direction.
        """
        if (obj == self.preview_area):
            if(event.type() == QtCore.QEvent.MouseMove ):
    
                if self.move_x_prev == 0:
                    self.move_x_prev = event.pos().x()
                if self.move_y_prev == 0:
                    self.move_y_prev = event.pos().y()
    
                dist_x = self.move_x_prev - event.pos().x()
                dist_y = self.move_y_prev - event.pos().y()
                self.preview_area.verticalScrollBar().setValue(
                    self.preview_area.verticalScrollBar().value() + dist_y)
                self.preview_area.horizontalScrollBar().setValue(
                    self.preview_area.horizontalScrollBar().value() + dist_x)
                #self.preview_area.scrollContentsBy(dist_x,dist_y)
                self.move_x_prev = event.pos().x()
                self.move_y_prev = event.pos().y()

            elif event.type() == QtCore.QEvent.MouseButtonRelease:
                self.last_time_move = 0
        return QtWidgets.QWidget.eventFilter(self, obj, event)
    
#-----------Common methods--------------------
    def tab_changed(self):
        """!@brief Called when tab changes
        @details Used to do actions when entering specific tab.
        """
        index = self.tabs.currentIndex()
        
        if index == 0:
            pass
        if index == 1:#Camera configuration tab
            #Request parameters from camera and show them in gui
            self.load_parameters()
    
    def set_status_msg(self, message, timeout=0):
        """!@brief Shows message in status bar
        @details Method is called when other methods need to send the user 
        some confrimation or status update.
        @param[in] message Contains text to be displayed in the status bar
        @param[in] timeout For how long should the message be displayed [ms]. Defaults to infinity.
        """
        self.status_timer.stop()
        self.status_label.setText(message)
        #When time out is reached, connected method 
        #(self.clear_status) is called.
        if(timeout > 0):
            self.status_timer.start(timeout)
    
    def clear_status(self):
        """!@brief Empties self.status_label in self.statusbar.
        @details Method is called after active message times out.
        """
        self.status_label.setText("")
    
    def get_directory(self, line_output = None):
        #set_record_path
        """!@brief Opens file dialog for user to set path to save frames.
        @details Method is called by Save Location button. Path is written to 
        the label next to the button and can be further modified.
        """
        #Open file dialog for choosing a folder
        name = QtWidgets.QFileDialog.getExistingDirectory(self.centralwidget,
                                                     "Select Folder",
                                                     )
        
        #Set label text to chosen folder path
        if(line_output):
            line_output.setText(name)
        return name
    
    def read_config(self):
        """!@brief Loads configuration from config.ini file
        @details This method is called on startup and loads all modifications
        user made to applications default state.                                 
        """
        
        cti_files = False
        loaded_cti = None
        filename = None,
        save_location = None,
        sequence_duration = None
        

        with open("config.ini", 'r') as config:
            for line in config:
                #reading configuration for recording
                line = line.rstrip('\n')
                if(line.startswith("filename=")):
                    filename = line.replace("filename=", "", 1)
                    #self.line_edit_sequence_name.setText(line.replace("filename=", "", 1))
                elif(line.startswith("save_location=")):
                    save_location = line.replace("save_location=", "", 1)
                    #self.line_edit_save_location.setText(line.replace("save_location=", "", 1))
                elif(line.startswith("sequence_duration=")):
                    sequence_duration = line.replace("sequence_duration=", "", 1)
                    #self.line_edit_sequence_duration.setText(line.replace("sequence_duration=", "", 1))
                elif(line.startswith("CTI_FILES_PATHS")):
                    cti_files = True
                elif(cti_files == True):
                    loaded_cti = cam.add_gentl_producer(line)
            
        self.tab_recording_config.load_config(filename, save_location, sequence_duration)
        #if no cti path is present in the config adding files will be skipped
        try:
            self.combo_remove_cti.addItems(loaded_cti)
        except:
            pass
        
        #Set status update
        self.set_status_msg("Configuration loaded",1500)
    
    def save_cti_config(self):
        """!@brief Saves all currently loaded GenTL producers to the config 
        file.
        @details When the program starts, the saved producers are loaded 
        from the config file. Save method overwrites any previous configuration.
        """
        paths = cam.get_gentl_producers()
        config = []
        
        
        with open("config.ini", 'r') as file:
            for line in file:
                config.append(line)
        
        with open("config.ini", 'w') as file:
            for line in config:
                #reading configuration for recording
                if(line.startswith("CTI_FILES_PATHS")):
                    file.write(line)
                    break
                else:
                    file.write(line)
                    
            if isinstance(paths, str):
                file.write(paths + '\n')
            else:
                if(paths):
                    for path in paths:
                        file.write(path + '\n')
        
        self.set_status_msg("Configuration saved")
        
    def about(self):
        """!@brief Shows simple about dialog
        @details About dialog contains informations about version, author etc.
        """
        QtWidgets.QMessageBox.about(self.centralwidget, "About", 
                                    "<p>Author: Jakub Lukaszczyk</p>" +
                                    "<p>Version: 1.0</p>" + 
                                    "<p>Original release: 2021</p>" +
                                    "<p>Gui created using Qt</p>")
    
    #-------------Camera control buttons and image-----------------
    def record(self):
        """!@brief Starts and stops recording
        @details Is called by start/stop button. Recording is always started 
        manually. Recording ends with another button click or after time set 
        in self.line_edit_sequence_duration passes. Save location and name is 
        determined by the text in self.line_edit_save_location and 
        self.line_edit_sequence_name.
        """
        if self.connected:
            if(not self.recording):
                #Change status icon and print status message
                self.camera_icon.setPixmap(self.icon_busy)
                self.set_status_msg("Starting recording")
                
                
                self.recording = True
                
                #Start new recording with defined name and save path
                cam.start_recording(self.line_edit_save_location.text(),
                                    self.line_edit_sequence_name.text(),
                                    'nothing')
                
                
                #If automatic sequence duration is set, create thread that will
                #automatically terminate the recording
                if(float(self.line_edit_sequence_duration.text()) > 0):
                    self.interupt_flag.clear()
                    self.seq_duration_thread = threading.Thread(target=self.seq_duration_wait)
                    self.seq_duration_thread.start()
                
                #Start live preview in a new thread
                self.show_preview_thread = threading.Thread(target=self.show_preview)
                self.show_preview_thread.start()
                self.set_status_msg("Recording",0)
            else:
                #Set status message and standby icon
                self.camera_icon.setPixmap(self.icon_standby)
                self.set_status_msg("Stopping recording")
                
                #Tell automatic sequence duration thread to end
                self.interupt_flag.set()
                
                #End recording
                cam.stop_recording()
                self.recording = False
                self.preview_live = False
                self.set_status_msg("Recording stopped", 3500)
    
    def seq_duration_wait(self):
        """!@brief Automatic recording interrupt.
        @details Let camera record for defined time and if the recording is not
        manually terminated stop the recording.
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
        @details Unlike recording method, this method does not save frames to a
        drive. Preview picture is rendered in separate thread.
        """
        #continue only if camera is connected
        if self.connected:
            if(not self.preview_live):
                #Set status message and icon
                self.camera_icon.setPixmap(self.icon_busy)
                self.set_status_msg("Starting preview",1500)
                
                
                self.preview_live = True
                
                #Start camera frame acquisition (not recording)
                cam.start_acquisition()
                
                
                #Create and run thread to draw frames to gui
                self.show_preview_thread = threading.Thread(target=self.show_preview)
                self.show_preview_thread.start()
            else:
                #Reset status icon and print message
                self.camera_icon.setPixmap(self.icon_standby)
                self.set_status_msg("Stopping preview",1500)
                
                #Stop receiving frames
                cam.stop_acquisition()
                
                self.preview_live = False
    
    def set_zoom(self, flag):
        """!@brief Set the zoom amount of the image previewed
        @details This method only sets the zooming variable, actual resizing
        is done in other methods.
        @param[in] flag Is used to define type of zoom. 
        1  - zoom in
        -1 - zoom out
        0  - zoom fit
        100- zoom reset
        """
        #flag 1 zoom in, -1 zoom out, 0 zoom fit, 100 zoom reset
        if(flag == -1 and self.preview_zoom > 0.1):
            self.preview_fit = False
            self.preview_zoom -= 0.1
        elif(flag == 1):
            self.preview_fit = False
            self.preview_zoom += 0.1
        elif(flag == 0):
            self.preview_fit = True
        elif(flag == 100):
            self.preview_fit = False
            self.preview_zoom = 1
    
    def single_frame(self):
        """!@brief Acquire and draw a single frame.
        @details Unlike the live preview, this method runs in the main thread 
        and therefore can modify frontend variables. The method may block whole
        application but its execution should be fast enough to not make a 
        difference.
        """
        #Method runs only if camera is connected
        if self.connected and not(self.preview_live or self.recording):
            #Set status icon and message
            self.set_status_msg("Receiving single frame",1500)
            self.camera_icon.setPixmap(self.icon_busy)
            
            #Get image
            image, pixel_format = cam.get_single_frame()
            
            #Try to run prediction
            self.predict(image)
            
            #Set up a new value of received frames in the statusbar
            self.received = self.received + 1
            self.receive_status.setText("Received frames: " + str(self.received))
            
            #Convert image to proper format fo PyQt
            h, w, ch = image.shape
            bytes_per_line = ch * w
            image = QtGui.QImage(image.data, w, h, bytes_per_line, self._get_QImage_format(pixel_format))

            
            #get size of preview window
            w_preview = self.preview_area.size().width()
            h_preview = self.preview_area.size().height()
            
            image_scaled = image.scaled(w_preview, 
                                        h_preview, 
                                        QtCore.Qt.KeepAspectRatio)
            
            #Set image to gui
            self.camera_preview.resize(w_preview,
                                       h_preview)
            self.camera_preview.setPixmap(QtGui.QPixmap.fromImage(image_scaled))
            self.camera_preview.show()
            
            #Reset status icon
            self.camera_icon.setPixmap(self.icon_standby)
    
    def show_preview(self):
        """!@brief Draws image from camera in real time.
        @details Acquires images from camera and draws them in real time at 
        the same rate as is display refresh_rate. If the frames come too fast,
        only one at the most recent one is drawn and the rest is dumped. During 
        this method an attempt to classify the image is called using predict method.
        """
        #Determine refresh rate of used display. This way the method will not
        #run too slowly or redundantly fast.
        device = win32api.EnumDisplayDevices()
        refresh_rate = win32api.EnumDisplaySettings(device.DeviceName, -1).DisplayFrequency
        
        #Auxiliary variables for fps calculation
        frames = 0
        cycles = 0
        
        color_format = QtGui.QImage.Format_Invalid
        str_color = None
        time_fps = time.monotonic_ns()
        #runs as long as the camera is recording or preview is active
        while self.recording or self.preview_live:
            cycles = cycles + 1
            
            #Draw only if thre is at least 1 frame to draw
            if not active_frame_queue.qsize() == 0:
                image = active_frame_queue.get_nowait()
                self.received = self.received + 1
                
                frames += 1
                
                #Dump all remaining frames (If frames are received faster than 
                #refresh_rate).
                while not active_frame_queue.qsize() == 0:
                    frames += 1
                    self.received = self.received + 1
                    active_frame_queue.get_nowait()
                
                #Try to run a prediction
                self.predict(image[0])
                
                #Set up a new value of received frames in the statusbar
                self.receive_status.setText("Received frames: " + str(self.received))
                
#Change to time dependency instead of cycle#More cycles -> more exact fps calculation (value is more stable in gui)
                
                if cycles > 30:
                    time_now = time.monotonic_ns()
                    time_passed = time_now - time_fps
                    time_fps = time_now
                    #[frames*Hz/c] -> [frames/s]
                    self.fps = round(frames/(time_passed/1_000_000_000),1)
                    self.fps_status.setText("FPS: " + str(self.fps))
                    
                    cycles = 0
                    frames = 0
                
                #Convert image to proper format for PyQt
                h, w, ch = image[0].shape
                bytes_per_line = ch * w
                
                
                if(str_color != image[1]):
                    str_color = image[1]
                    color_format = self._get_QImage_format(str_color)
                    
                if(color_format == QtGui.QImage.Format_Invalid):
                    self.set_status_msg("Used image format is not supported")
                
                
                image = QtGui.QImage(image[0].data, w, h, bytes_per_line, color_format)
#TODO Get color format dynamically
                
                #get size of preview window if zoom fit is selected
                if(self.preview_fit == True):
                    self.w_preview = self.preview_area.size().width()
                    self.h_preview = self.preview_area.size().height()
                    image_scaled = image.scaled(self.w_preview, 
                                                self.h_preview, 
                                                QtCore.Qt.KeepAspectRatio)
                else:#else use zoom percentage
                    self.w_preview = w*self.preview_zoom
                    self.h_preview = w*self.preview_zoom
                    image_scaled = image.scaled(self.w_preview,
                                         self.w_preview,
                                         QtCore.Qt.KeepAspectRatio)
                
                self.image_pixmap = QtGui.QPixmap.fromImage(image_scaled)
                self.preview_callback()
                #Set image to gui
            #Wait for next display frame
            time.sleep(1/refresh_rate)
        
        #When recording stops, change fps to 0
        self.fps = 0.0
        self.fps_status.setText("FPS: " + str(self.fps))
    
    def preview_callback(self):
        """!@brief Auxiliary method used to transfer thread state change into
        the main thread.
        """
        if(self.resize_signal.text() != "A"):
            self.resize_signal.setText("A")
        else:
            self.resize_signal.setText("B")
    
    def update_img(self):
        """!@brief update image in the live preview window.
        @details This method must run in the main thread as it modifies frontend
        data of the gui.
        """
        #Resize preview label if preview window size changed
        if(self.w_preview != self.camera_preview.size().width() or
                   self.h_preview != self.camera_preview.size().height()):
            self.camera_preview.resize(self.w_preview,
                                       self.h_preview)
        
        #set a new image to the preview area
        self.camera_preview.setPixmap(self.image_pixmap)
        self.camera_preview.show()
    
    def _get_QImage_format(self, format_string):
        """!@brief The image format provided by camera object (according to 
        GenICam standard) is transoformed to one of the color formats supported
        by PyQt.
        @param[in] format_string text containing color format defined by GenICam
        or another standard.
        """
        image_format = None
        
        if(format_string == 'Format_Mono'):
            image_format = QtGui.QImage.Format_Mono
        elif(format_string == 'Format_MonoLSB'):
            image_format = QtGui.QImage.Format_MonoLSB
        elif(format_string == 'Format_Indexed8'):
            image_format = QtGui.QImage.Format_Indexed8
        elif(format_string == 'Format_RGB32'):
            image_format = QtGui.QImage.Format_RGB32
        elif(format_string == 'Format_ARGB32'):
            image_format = QtGui.QImage.Format_ARGB32
        elif(format_string == 'Format_ARGB32_Premultiplied'):
            image_format = QtGui.QImage.Format_ARGB32_Premultiplied
        elif(format_string == 'Format_RGB16'):
            image_format = QtGui.QImage.Format_RGB16
        elif(format_string == 'Format_ARGB8565_Premultiplied'):
            image_format = QtGui.QImage.Format_ARGB8565_Premultiplied
        elif(format_string == 'Format_RGB666'):
            image_format = QtGui.QImage.Format_RGB666
        elif(format_string == 'Format_ARGB6666_Premultiplied'):
            image_format = QtGui.QImage.Format_ARGB6666_Premultiplied
        elif(format_string == 'Format_RGB555'):
            image_format = QtGui.QImage.Format_RGB555
        elif(format_string == 'Format_ARGB8555_Premultiplied'):
            image_format = QtGui.QImage.Format_ARGB8555_Premultiplied
        elif(format_string == 'Format_RGB888' or format_string == 'RGB8'):
            image_format = QtGui.QImage.Format_RGB888
        elif(format_string == 'Format_RGB444'):
            image_format = QtGui.QImage.Format_RGB444
        elif(format_string == 'Format_ARGB4444_Premultiplied'):
            image_format = QtGui.QImage.Format_ARGB4444_Premultiplied
        elif(format_string == 'Format_RGBX8888'):
            image_format = QtGui.QImage.Format_RGBX8888
        elif(format_string == 'Format_RGBA8888' or format_string == 'RGBa8'):
            image_format = QtGui.QImage.Format_RGBA8888
        elif(format_string == 'Format_RGBA8888_Premultiplied'):
            image_format = QtGui.QImage.Format_RGBA8888_Premultiplied
        elif(format_string == 'Format_BGR30'):
            image_format = QtGui.QImage.Format_BGR30
        elif(format_string == 'Format_A2BGR30_Premultiplied'):
            image_format = QtGui.QImage.Format_A2BGR30_Premultiplied
        elif(format_string == 'Format_RGB30'):
            image_format = QtGui.QImage.Format_RGB30
        elif(format_string == 'Format_A2RGB30_Premultiplied'):
            image_format = QtGui.QImage.Format_A2RGB30_Premultiplied
        elif(format_string == 'Format_Alpha8'):
            image_format = QtGui.QImage.Format_Alpha8
        elif(format_string == 'Format_Grayscale8' or format_string == 'Mono8'):
            image_format = QtGui.QImage.Format_Grayscale8
        elif(format_string == 'Format_Grayscale16' or format_string == 'Mono16'):
            image_format = QtGui.QImage.Format_Grayscale16
        elif(format_string == 'Format_RGBX64'):
            image_format = QtGui.QImage.Format_RGBX64
        elif(format_string == 'Format_RGBA64'):
            image_format = QtGui.QImage.Format_RGBA64
        elif(format_string == 'Format_RGBA64_Premultiplied'):
            image_format = QtGui.QImage.Format_RGBA64_Premultiplied
        elif(format_string == 'Format_BGR888' or format_string == 'BGR8'):
            image_format = QtGui.QImage.Format_BGR888
        else:
            image_format = QtGui.QImage.Format_Invalid
        
        return image_format
        
        '''
        SFNC OPTIONS not yet implemented
        Mono1p
        Mono2p, Mono4p, Mono8s, Mono10, Mono10p, Mono12, Mono12p, Mono14, 
        , R8, G8, B8, , RGB8_Planar, , RGB10, RGB10_Planar, 
        RGB10p32, RGB12, RGB12_Planar, RGB16, RGB16_Planar, RGB565p, BGR10, 
        BGR12, BGR16, BGR565p, , BGRa8, YUV422_8, YCbCr411_8, YCbCr422_8, 
        YCbCr601_422_8, YCbCr709_422_8, YCbCr8, BayerBG8, BayerGB8, BayerGR8, 
        BayerRG8, BayerBG10, BayerGB10, BayerGR10, BayerRG10, BayerBG12, 
        BayerGB12, BayerGR12, BayerRG12, BayerBG16, BayerGB16, BayerGR16, 
        BayerRG16, Coord3D_A8, Coord3D_B8, Coord3D_C8, Coord3D_ABC8, 
        Coord3D_ABC8_Planar, Coord3D_A16, Coord3D_B16, Coord3D_C16, 
        Coord3D_ABC16, Coord3D_ABC16_Planar, Coord3D_A32f, Coord3D_B32f, 
        Coord3D_C32f, Coord3D_ABC32f, Coord3D_ABC32f_Planar, Confidence1, 
        Confidence1p, Confidence8, Confidence16, Confidence32f, Raw8, Raw16, 
        Device-specific
        - GigE Vision Specific:
        Mono12Packed, BayerGR10Packed, BayerRG10Packed, BayerGB10Packed, 
        BayerBG10Packed, BayerGR12Packed, BayerRG12Packed, BayerGB12Packed, 
        BayerBG12Packed, RGB10V1Packed, RGB12V1Packed, 
        - Deprecated:
            will not be implemented for now as they are not used in genicam anymore
        '''
        '''
        SFNC OPTIONS - all
        Mono1p
        Mono2p, Mono4p, Mono8, Mono8s, Mono10, Mono10p, Mono12, Mono12p, Mono14, 
        Mono16, R8, G8, B8, RGB8, RGB8_Planar, RGBa8, RGB10, RGB10_Planar, 
        RGB10p32, RGB12, RGB12_Planar, RGB16, RGB16_Planar, RGB565p, BGR10, 
        BGR12, BGR16, BGR565p, BGR8, BGRa8, YUV422_8, YCbCr411_8, YCbCr422_8, 
        YCbCr601_422_8, YCbCr709_422_8, YCbCr8, BayerBG8, BayerGB8, BayerGR8, 
        BayerRG8, BayerBG10, BayerGB10, BayerGR10, BayerRG10, BayerBG12, 
        BayerGB12, BayerGR12, BayerRG12, BayerBG16, BayerGB16, BayerGR16, 
        BayerRG16, Coord3D_A8, Coord3D_B8, Coord3D_C8, Coord3D_ABC8, 
        Coord3D_ABC8_Planar, Coord3D_A16, Coord3D_B16, Coord3D_C16, 
        Coord3D_ABC16, Coord3D_ABC16_Planar, Coord3D_A32f, Coord3D_B32f, 
        Coord3D_C32f, Coord3D_ABC32f, Coord3D_ABC32f_Planar, Confidence1, 
        Confidence1p, Confidence8, Confidence16, Confidence32f, Raw8, Raw16, 
        Device-specific
        - GigE Vision Specific:
        Mono12Packed, BayerGR10Packed, BayerRG10Packed, BayerGB10Packed, 
        BayerBG10Packed, BayerGR12Packed, BayerRG12Packed, BayerGB12Packed, 
        BayerBG12Packed, RGB10V1Packed, RGB12V1Packed, 
        - Deprecated:
        Mono8Signed (Deprecated, use Mono8s)
        RGB8Packed (Deprecated, use RGB8) ,BGR8Packed (Deprecated, use BGR8), 
        RGBA8Packed (Deprecated, use RGBa8), BGRA8Packed (Deprecated, use BGRa8), 
        RGB10Packed (Deprecated, use RGB10), BGR10Packed (Deprecated, use BGR10), 
        RGB12Packed (Deprecated, use RGB12), BGR12Packed (Deprecated, use BGR12), 
        RGB16Packed (Deprecated, use RGB16), BGR16Packed (Deprecated, use BGR16), 
        RGB10V2Packed (Deprecated, use RGB10p32), BGR10V2Packed (Deprecated, use BGR10p32), 
        RGB565Packed (Deprecated, use RGB565p), BGR565Packed (Deprecated, use BGR565p), 
        YUV411Packed (Deprecated, use YUV411_8_UYYVYY), YUV422Packed (Deprecated, use YUV422_8_UYVY), 
        YUV444Packed (Deprecated, use YUV8_UYV), YUYVPacked (Deprecated, use YUV422_8), 
        RGB8Planar (Deprecated, use RGB8_Planar), RGB10Planar (Deprecated, use RGB10_Planar),
        RGB12Planar (Deprecated, use RGB12_Planar), RGB16Planar (Deprecated, use RGB16_Planar), 
        '''
    

    #------------Camera config tab--------------------------
    def show_parameters(self):
        """!@brief Loads all camera's features and creates dynamic widgets for
        every feature.
        @details This method is called when user first enters parameters tab or
        when the configuration level changes. All the widgets are created dynamically
        and based on the type of the feature, proper widget type is selected. Also
        these widgets have method to change their value associated with them
        when created.
        """
        num = 0
        
        categories = []
        self.top_items = {}
        self.children_items = {}
        
        self.tree_features.clear()
        
        for name in self.feat_widgets:
            self.feat_widgets[name].deleteLater()
        
        for name in self.feat_labels:
            self.feat_labels[name].deleteLater()
        
        self.feat_widgets.clear()
        self.feat_labels.clear()
        
        while not self.feat_queue.empty():
            try:
                param = self.feat_queue.get()
                param['attr_cat'] = param['attr_cat'].lstrip('/')
                ctgs = param['attr_cat'].split('/')
                for i, ctg in enumerate(ctgs):
                    if(not(ctg in categories)):
                        if(i == 0):
                            self.top_items[ctg] = QtWidgets.QTreeWidgetItem([ctg])
                            self.tree_features.addTopLevelItem(self.top_items[ctg])
                        else:
                            self.top_items[ctg] = QtWidgets.QTreeWidgetItem([ctg])
                            self.top_items[ctgs[i-1]].addChild(self.top_items[ctg])
                        categories.append(ctg)
            #Create a new label with name of the feature
            
                self.feat_labels[param["name"]] = QtWidgets.QLabel(self.tab_config)
                self.feat_labels[param["name"]].setObjectName(param["name"])
                self.feat_labels[param["name"]].setText(param["attr_name"])
                #If the feature has a tooltip, set it.
                try:
                    self.feat_labels[param["name"]].setToolTip(param["attr_tooltip"])
                except:
                    pass
                
                #Place the label on the num line of the layout
                #self.parameters_layout.setWidget(num, QtWidgets.QFormLayout.LabelRole, self.feat_labels[param["name"]])
                
                #If the feature does not have a value, set it to 0
                if param["attr_value"] == None:
                    param["attr_value"] = 0
                    
                #Based on the feature type, right widget is chosen to hold the
                #feature's value
                
                if param["attr_type"] == "IntFeature":
                    #For int feature a Line edit field is created, but only 
                    #integers can be written in.
                    self.feat_widgets[param["name"]] = QtWidgets.QSpinBox(self.tab_config)
                    if(param["attr_range"]):
                        self.feat_widgets[param["name"]].setRange(
                                                param["attr_range"][0],
                                                param["attr_range"][1])
                    
                    #Set text to the current value of the feature
                    self.feat_widgets[param["name"]].setValue(param["attr_value"])
                    
                    #Call feature change for this feature when enter is pressed in this field.
                    #Text is the value that will be set to the feature.
                    self.feat_widgets[param["name"]].valueChanged.connect(lambda new_val,param=param: cam.set_parameter(param["name"],new_val))
                elif param["attr_type"] == "FloatFeature":
                    #For float feature a Line edit field is created, but only 
                    #real numbers can be written in.
                    self.feat_widgets[param["name"]] = QtWidgets.QDoubleSpinBox(self.tab_config)
                    if(param["attr_range"]):
                        self.feat_widgets[param["name"]].setRange(
                                                param["attr_range"][0],
                                                param["attr_range"][1])
                    
                    #Set text to the current value of the feature
                    self.feat_widgets[param["name"]].setValue(param["attr_value"])
                    
                    #Call feature change for this feature when enter is pressed in this field.
                    #Text is the value that will be set to the feature.
                    self.feat_widgets[param["name"]].valueChanged.connect(lambda new_val,param=param: cam.set_parameter(param["name"],new_val))
                elif param["attr_type"] == "StringFeature":
                    #For string feature a Line edit field is created.
                    self.feat_widgets[param["name"]] = QtWidgets.QLineEdit(self.tab_config)
                    
                    #Set text to the current value of the feature
                    self.feat_widgets[param["name"]].setText(param["attr_value"])
                    
                    #Call feature change for this feature when enter is pressed in this field.
                    #Text is the value that will be set to the feature.
                    self.feat_widgets[param["name"]].returnPressed.connect(lambda new_val,param=param: cam.set_parameter(param["name"],new_val))            
                elif param["attr_type"] == "BoolFeature":
                    #For bool feature a checkbox is created.
                    self.feat_widgets[param["name"]] = QtWidgets.QCheckBox(self.tab_config)
                    
                    #If value is true the checkbox is ticked otherwise remains empty
                    self.feat_widgets[param["name"]].setChecked(param["attr_value"])
                    
                    #When state of the checkbox change, the feature is sent to 
                    #the camera and changed to the new state
                    self.feat_widgets[param["name"]].stateChanged.connect(lambda new_val,param=param: cam.set_parameter(param["name"],new_val))
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
                    self.feat_widgets[param["name"]].activated.connect(lambda new_val,param=param: cam.set_parameter(param["name"],new_val+1))
                elif param["attr_type"] == "CommandFeature":
                    #If the feature type is not recognized, create a label with 
                    #the text error
                    self.feat_widgets[param["name"]] = QtWidgets.QPushButton(self.tab_config)
                    self.feat_widgets[param["name"]].setText("Execute command")
                    self.feat_widgets[param["name"]].clicked.connect(lambda val,param=param: cam.execute_command(param["name"]))
                else:
                    #If the feature type is not recognized, create a label with 
                    #the text error
                    self.feat_widgets[param["name"]] = QtWidgets.QLabel(self.tab_config)
                    self.feat_widgets[param["name"]].setText("Unknown feature type")
                
                self.feat_widgets[param["name"]].setEnabled(param["attr_enabled"])
                
                #Add newly created widget to the layout on the num line
                new_item = QtWidgets.QTreeWidgetItem(self.top_items[ctgs[-1]] ,['', ''])
                #add new item to the last subcategory of its category tree
                self.tree_features.setItemWidget(new_item, 0,self.feat_labels[param["name"]])
                self.tree_features.setItemWidget(new_item, 1,self.feat_widgets[param["name"]])
                #new_item = QtWidgets.QTreeWidgetItem(self.top_items[param['attr_cat']] ,[self.feat_labels[param["name"]], self.feat_widgets[param["name"]]])
                self.children_items[param["name"]] = new_item
                #self.parameters_layout.setWidget(num, QtWidgets.QFormLayout.FieldRole, self.feat_widgets[param["name"]])
                num += 1
            except:
                pass
                #we'll get here when queue is empty
        self.param_flag.clear()
    
    def start_refresh_parameters(self):
        """!@brief Called automatically when feat_refresh_timer runs out
        @details used to start a thread to refresh parameters values. Not
        called by user but automatically.
        """
        #called every 4 seconds
        if (self.feat_widgets and self.connected and self.tabs.currentIndex() == 1 and
            not(self.preview_live or self.recording) and 
            not self.param_flag.is_set() and self.update_completed_flag.is_set()):
            
            self.update_completed_flag.clear()
            
            self.update_thread = threading.Thread(target=self.get_new_val_parameters)
            self.update_thread.start()
    
    def get_new_val_parameters(self):
        """!@brief Check for new parameter value
        @details after camera features are loaded, this method periodically 
        calls for the most recent value of each parameter.
        """
        if(not self.feat_widgets):
            self.update_completed_flag.set()
            return
        
        params = Queue()
        tries = 0
        while(tries <= 10):
            if(cam.get_parameters(params, 
                    threading.Event(), 
                    self.combo_config_level.currentIndex()+1)):
                break
            else:
                tries += 1
                
        if(tries >= 10):
            self.update_completed_flag.set()
            return
        
        while(not params.empty()):
            parameter = params.get()
            if(not(self.preview_live or self.recording) and 
               self.tabs.currentIndex() == 1):
                self.parameter_values[parameter["name"]] = parameter["attr_value"]
            else:
                self.update_completed_flag.set()
                return
        self.update_flag.set()
    
    def update_parameters(self):
        """!@brief Writes new values of the parameters to the GUI.
        @details After get_new_val_parameters finishes, the update_flag is set 
        and this method can transfer the new values of the parameters to the GUI. 
        Like start_refresh_parameters, this method is bound to the timer.
        """
        if (self.connected and not self.param_flag.is_set() and 
            self.tabs.currentIndex() == 1 and
            self.update_flag.is_set() and not(self.preview_live or self.recording)):
            
            self.update_flag.clear()
            
            for parameter in self.feat_widgets:
                try:
                    value = self.parameter_values[parameter]
                    widget = self.feat_widgets[parameter]
                    if(value == None):
                        continue
                    
                    if(type(widget) == QtWidgets.QLineEdit):
                        widget.setText(str(value))
                    elif(type(widget) == QtWidgets.QComboBox):
                        index = widget.findText(str(value), QtCore.Qt.MatchFixedString)
                        #Set found index to be the active one
                        if index >= 0:
                            widget.setCurrentIndex(index)
                    elif(type(widget) == QtWidgets.QDoubleSpinBox or
                         type(widget) == QtWidgets.QSpinBox):
                        widget.setValue(value)
                    elif(type(widget) == QtWidgets.QCheckBox):
                        widget.setChecked(value)
                except:
                    pass
            self.update_completed_flag.set()
    
    def load_parameters(self):
        """!@brief Fills layout with feature name and value pairs
        @details Based on the feature type a new label, text area, checkbox or
        combo box is created. In this version all available parameters are shown.
        """
        
        #Start filling features in only with connected camera
        if self.connected and not self.param_flag.is_set():
            #Status message
            
            self.set_status_msg("Reading features")
            
            #empty feature queue
            self.get_params_thread = threading.Thread(
                target=cam.get_parameters,
                kwargs={'feature_queue': self.feat_queue,
                        'flag': self.param_flag,
                        'visibility': Config_level(self.combo_config_level.currentIndex()+1)})
            self.param_callback_thread = threading.Thread(target=self.callback_parameters)
            
            
            self.param_callback_thread.start()
            self.get_params_thread.start()
    
    def save_cam_config(self):
        """!@brief Opens file dialog for user to select where to save camera 
        configuration.
        @details Called by Save configuration button. Configuration is saved 
        as an .xml file and its contents are dependent on module used in Camera 
        class to save the config.
        """
        
        if(self.connected):
            #Open file dialog for choosing a save location and name
            name = QtWidgets.QFileDialog.getSaveFileName(self.centralwidget,
                                                         "Save Configuration",
                                                         filter="XML files (*.xml)",
                                                         directory="config.xml")
            
            #Save camera config to path specified in name (0 index)
            cam.save_config(name[0])
    
    def load_cam_config(self):
        """!@brief Allows a user to choose saved xml configuration and load it
        into the camera
        @details Allowes only xml file in the file dialog and after loading prints
        a status message
        """
        if self.connected:
            if(not self.recording and not self.preview_live):
                name = QtWidgets.QFileDialog.getOpenFileName(self.centralwidget,
                                                             "Load Configuration",
                                                             filter="XML files (*.xml)")
               
                #Set label text to chosen folder path
                if(name[0]):
                    tries = 0
                    while(tries <= 10):
                        if(cam.load_config(name[0])):
                            self.set_status_msg("Configuration loaded")
                            return
                        else:
                            tries += 1
                    self.set_status_msg("Loading failed", 2500)
            else:
                self.set_status_msg("Stop recording and preview before loading config")
        
    def callback_parameters(self):
        """!@brief Auxiliary method used to transfer thread state change into
        the main thread.
        """
        self.param_flag.wait()
        
        if(self.parameters_signal.text() != "A"):
            self.parameters_signal.setText("A")
        else:
            self.parameters_signal.setText("B")
    
   

#____________________NEW METHODS


    def update_camera_status(self, connected, state, name):
        """!@brief Updates camera status variables and status bar
        @details This method is called when tab_connect sends its update signal.
        The method will change camera state icons and name. If the camera is being 
        disconnected, the fps and received frames will be reseted.
        @param[in] connected The new status of camera (connected or disconnected)
        @param[in] state Numeric state of the camera (0=disconnected, 1=standby, 2=busy)
        @param[in] name Connected camera name. If the camera is being disconnected
        the name is "Not connected"
        """
        self.connected = connected
        self.camera_status.setText("Camera: " + name)

        if(state == 1):
            self.camera_icon.setPixmap(self.icon_standby)
        if(state == 2):
            self.camera_icon.setPixmap(self.icon_busy)
        else:
            self.received = 0
            self.fps = 0.0
            
            self.receive_status.setText("Received frames: " + str(self.received))
            self.fps_status.setText("FPS: " + str(self.fps))
            self.camera_icon.setPixmap(self.icon_offline)
            self.preview_live = False
            self.recording = False

        