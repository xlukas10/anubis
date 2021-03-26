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
import os #working with some paths
from queue import Queue

#tmp 
import cv2

from prediction_graph import Prediction_graph
from global_camera import cam
from global_queue import active_frame_queue
from computer_vision import Computer_vision
from config_level import Config_level

class Ui_MainWindow(QtCore.QObject):
    def setupUi(self, MainWindow):
        #VARIABLES
        self.tmp = False
        """
        !@brief Variable used to store device information of detected cameras
        """
        self.feat_refresh_timer  = QtCore.QTimer(self)
        self.feat_refresh_timer.setInterval(2000)
        self.feat_refresh_timer.timeout.connect(self.update_parameters)
        self.feat_refresh_timer.start()
        
        self.image_pixmap = None
        self.w_preview = 0
        self.h_preview = 0
                    
        self.move_x_prev = 0
        self.move_y_prev = 0
        self.process_perc = [0]
        
        
        
        
        self.preview_zoom = 1
        self.preview_fit = True
        
        self.top_items = {}
        self.children_items = {}
        
        #Contains all dynamically created widgets
        self.feat_widgets = {}
        self.feat_labels = {}
        self.feat_queue = Queue()
        
        self.detected = []
        self.connected = False
        self.training_flag = threading.Event()
        self.param_flag = threading.Event()
        self.param_flag = threading.Event()
        self.process_flag = threading.Event()
        self.process_prog_flag = threading.Event()
        
        self.callback_train_signal = QtWidgets.QLineEdit()
        self.callback_train_signal.textChanged.connect(self.update_training)
        
        self.callback_process_signal = QtWidgets.QLineEdit()
        self.callback_process_signal.textChanged.connect(self.update_processing)
        
        self.resize_signal = QtWidgets.QLineEdit()
        self.resize_signal.textChanged.connect(self.update_img)
        
        self.parameters_signal = QtWidgets.QLineEdit()
        self.parameters_signal.textChanged.connect(self.show_parameters)
        
        self.progress_flag = threading.Event()
        self.train_vals = {'progress': 0,
                           'loss': 0,
                           'acc': 0,
                           'val_loss': 0,
                           'val_acc': 0,
                           'max_epoch': 0,
                           'epoch': 0}
        
        self.prediction_flag = threading.Event()
        
        self.interupt_flag = threading.Event()
        self.recording = False
        self.preview_live = False
        
        self.icon_offline = QtGui.QPixmap("./icons/icon_offline.png")
        self.icon_standby = QtGui.QPixmap("./icons/icon_standby.png")
        self.icon_busy = QtGui.QPixmap("./icons/icon_busy.png")
        
        self.fps = 0.0
        self.received = 0
        
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
        self.preview_area.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.preview_area.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
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
        
        
        
        
        self.verticalLayout_4.addWidget(self.list_detected_cameras)
        
        self.frame_cti = QtWidgets.QFrame(self.tab_connect)
        self.frame_cti.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_cti.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_cti.setObjectName("frame_cti")
        self.horizontalLayout_6 = QtWidgets.QHBoxLayout(self.frame_cti)
        self.horizontalLayout_6.setObjectName("horizontalLayout_6")
        self.tip_add_cti = QtWidgets.QLabel(self.frame_cti)
        self.tip_add_cti.setWordWrap(True)
        self.tip_add_cti.setObjectName("tip_add_cti")
        self.horizontalLayout_6.addWidget(self.tip_add_cti)
        self.btn_add_cti = QtWidgets.QPushButton(self.frame_cti)
        self.btn_add_cti.setObjectName("btn_add_cti")
        self.horizontalLayout_6.addWidget(self.btn_add_cti)
        self.verticalLayout_4.addWidget(self.frame_cti)

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
        self.verticalLayout.addWidget(self.btn_save_sequence_settings)
        
        self.btn_reset_sequence_settings = QtWidgets.QPushButton(self.tab_recording_config)
        self.btn_reset_sequence_settings.setObjectName("btn_reset_sequence_settings")
        
        self.verticalLayout.addWidget(self.btn_reset_sequence_settings)
        
        self.tabs.addTab(self.tab_recording_config, "")
        
        #Tab - Keras/Tensorflow/Learning,Classification
        self.tab_tensorflow = QtWidgets.QWidget()
        self.tab_tensorflow.setObjectName("tab_tensorflow")
        
        self.gridLayout_3 = QtWidgets.QGridLayout(self.tab_tensorflow)
        self.gridLayout_3.setObjectName("gridLayout_3")
        
        self.btn_save_model = QtWidgets.QPushButton(self.tab_tensorflow)
        self.btn_save_model.setObjectName("btn_save_model")
        
        self.gridLayout_3.addWidget(self.btn_save_model, 0, 1, 1, 1)
        
        self.line_edit_model_name = QtWidgets.QLineEdit(self.tab_tensorflow)
        self.line_edit_model_name.setObjectName("line_edit_model_name")
        self.line_edit_model_name.setEnabled(False)
        self.gridLayout_3.addWidget(self.line_edit_model_name, 1, 0, 1, 2)
        
        self.btn_load_model = QtWidgets.QPushButton(self.tab_tensorflow)
        self.btn_load_model.setObjectName("btn_load_model")
        
        self.gridLayout_3.addWidget(self.btn_load_model, 0, 0, 1, 1)
        
        self.tensorflow_tabs = QtWidgets.QTabWidget(self.tab_tensorflow)
        self.tensorflow_tabs.setObjectName("tensorflow_tabs")
        
        self.tab_classify = QtWidgets.QWidget()
        self.tab_classify.setObjectName("tab_classify")
        self.gridLayout_5 = QtWidgets.QGridLayout(self.tab_classify)
        self.gridLayout_5.setObjectName("gridLayout_5")
        
        self.predictions = Prediction_graph()
        
        self.gridLayout_5.addWidget(self.predictions, 0, 0, 1, 1)
        
        self.tensorflow_tabs.addTab(self.tab_classify, "")
        
        self.tab_train = QtWidgets.QWidget()
        self.tab_train.setObjectName("tab_train")
        
        self.gridLayout_9 = QtWidgets.QGridLayout(self.tab_train)
        self.gridLayout_9.setObjectName("gridLayout_9")
        
        spacerItem1 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout_9.addItem(spacerItem1, 2, 0, 1, 1)
        
        self.frame_train_stats = QtWidgets.QFrame(self.tab_train)
        self.frame_train_stats.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_train_stats.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_train_stats.setObjectName("frame_train_stats")
        
        self.gridLayout_8 = QtWidgets.QGridLayout(self.frame_train_stats)
        self.gridLayout_8.setObjectName("gridLayout_8")
        
        self.label_val_acc = QtWidgets.QLabel(self.frame_train_stats)
        self.label_val_acc.setObjectName("label_val_acc")
        self.gridLayout_8.addWidget(self.label_val_acc, 6, 3, 1, 1)
        
        self.line_edit_acc = QtWidgets.QLineEdit(self.frame_train_stats)
        self.line_edit_acc.setEnabled(False)
        self.line_edit_acc.setObjectName("line_edit_acc")
        self.gridLayout_8.addWidget(self.line_edit_acc, 6, 2, 1, 1)
        
        self.label_acc = QtWidgets.QLabel(self.frame_train_stats)
        self.label_acc.setObjectName("label_acc")
        self.gridLayout_8.addWidget(self.label_acc, 6, 0, 1, 1)
        
        self.label_val_loss = QtWidgets.QLabel(self.frame_train_stats)
        self.label_val_loss.setObjectName("label_val_loss")
        self.gridLayout_8.addWidget(self.label_val_loss, 2, 3, 1, 1)
        
        self.line_edit_val_acc = QtWidgets.QLineEdit(self.frame_train_stats)
        self.line_edit_val_acc.setEnabled(False)
        self.line_edit_val_acc.setObjectName("line_edit_val_acc")
        self.gridLayout_8.addWidget(self.line_edit_val_acc, 6, 4, 1, 1)
        
        self.line_edit_val_loss = QtWidgets.QLineEdit(self.frame_train_stats)
        self.line_edit_val_loss.setEnabled(False)
        self.line_edit_val_loss.setObjectName("line_edit_val_loss")
        self.gridLayout_8.addWidget(self.line_edit_val_loss, 2, 4, 1, 1)
        
        self.label_epoch = QtWidgets.QLabel(self.frame_train_stats)
        self.label_epoch.setObjectName("label_epoch")
        self.gridLayout_8.addWidget(self.label_epoch, 1, 0, 1, 1)
        
        self.label_active_epoch = QtWidgets.QLabel(self.frame_train_stats)
        self.label_active_epoch.setObjectName("label_active_epoch")
        self.gridLayout_8.addWidget(self.label_active_epoch, 1, 2, 1, 1)
        
        self.line_edit_loss = QtWidgets.QLineEdit(self.frame_train_stats)
        self.line_edit_loss.setEnabled(False)
        self.line_edit_loss.setObjectName("line_edit_loss")
        self.gridLayout_8.addWidget(self.line_edit_loss, 2, 2, 1, 1)
        
        self.label_loss = QtWidgets.QLabel(self.frame_train_stats)
        self.label_loss.setObjectName("label_loss")
        self.gridLayout_8.addWidget(self.label_loss, 2, 0, 1, 1)
        
        self.btn_train_cancel = QtWidgets.QPushButton(self.frame_train_stats)
        self.btn_train_cancel.setObjectName("btn_train_cancel")
        self.gridLayout_8.addWidget(self.btn_train_cancel, 0, 0, 1, 1)
        
        self.progress_bar_train = QtWidgets.QProgressBar(self.frame_train_stats)
        self.progress_bar_train.setProperty("value", 0)
        self.progress_bar_train.setObjectName("progress_bar_train")
        self.gridLayout_8.addWidget(self.progress_bar_train, 0, 2, 1, 3)
        
        self.gridLayout_9.addWidget(self.frame_train_stats, 3, 0, 1, 1)
        
        self.frame_train_preprocess = QtWidgets.QFrame(self.tab_train)
        self.frame_train_preprocess.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_train_preprocess.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_train_preprocess.setObjectName("frame_train_preprocess")
        
        self.gridLayout_6 = QtWidgets.QGridLayout(self.frame_train_preprocess)
        self.gridLayout_6.setObjectName("gridLayout_6")
        self.label_img_resize = QtWidgets.QLabel(self.frame_train_preprocess)
        self.label_img_resize.setObjectName("label_img_resize")
        self.gridLayout_6.addWidget(self.label_img_resize, 1, 0, 1, 1)
        
        self.btn_load_dataset = QtWidgets.QPushButton(self.frame_train_preprocess)
        self.btn_load_dataset.setObjectName("btn_load_dataset")
        self.gridLayout_6.addWidget(self.btn_load_dataset, 0, 0, 1, 1)
        
        self.label_val_split = QtWidgets.QLabel(self.frame_train_preprocess)
        self.label_val_split.setObjectName("label_val_split")
        self.gridLayout_6.addWidget(self.label_val_split, 4, 0, 1, 1)
        
        self.line_edit_val_split = QtWidgets.QLineEdit(self.frame_train_preprocess)
        self.line_edit_val_split.setMaximumSize(QtCore.QSize(186, 16777215))
        self.line_edit_val_split.setInputMethodHints(QtCore.Qt.ImhDigitsOnly)
        self.line_edit_val_split.setObjectName("line_edit_val_split")
        self.gridLayout_6.addWidget(self.line_edit_val_split, 4, 1, 1, 1)
        
        self.line_edit_epochs = QtWidgets.QLineEdit(self.frame_train_preprocess)
        self.line_edit_epochs.setObjectName("line_edit_epochs")
        self.gridLayout_6.addWidget(self.line_edit_epochs, 5, 1, 1, 1)
        
        self.label_train_epochs = QtWidgets.QLabel(self.frame_train_preprocess)
        self.label_train_epochs.setObjectName("label_train_epochs")
        self.gridLayout_6.addWidget(self.label_train_epochs, 5, 0, 1, 1)
        
        self.btn_preprocess = QtWidgets.QPushButton(self.frame_train_preprocess)
        self.btn_preprocess.setObjectName("btn_preprocess")
        self.gridLayout_6.addWidget(self.btn_preprocess, 6, 0, 1, 1)
        
        self.progress_bar_preprocess = QtWidgets.QProgressBar(self.frame_train_preprocess)
        self.progress_bar_preprocess.setProperty("value", 0)
        self.progress_bar_preprocess.setObjectName("progress_bar_preprocess")
        self.gridLayout_6.addWidget(self.progress_bar_preprocess, 6, 1, 1, 2)
        
        self.label_res_width = QtWidgets.QLabel(self.frame_train_preprocess)
        self.label_res_width.setObjectName("label_res_width")
        self.gridLayout_6.addWidget(self.label_res_width, 2, 0, 1, 1, QtCore.Qt.AlignRight)
        
        self.label_res_height = QtWidgets.QLabel(self.frame_train_preprocess)
        self.label_res_height.setObjectName("label_res_height")
        self.gridLayout_6.addWidget(self.label_res_height, 3, 0, 1, 1, QtCore.Qt.AlignRight)
        
        self.line_edit_res_width = QtWidgets.QLineEdit(self.frame_train_preprocess)
        self.line_edit_res_width.setEnabled(False)
        self.line_edit_res_width.setInputMethodHints(QtCore.Qt.ImhDigitsOnly)
        self.line_edit_res_width.setObjectName("line_edit_res_width")
        self.gridLayout_6.addWidget(self.line_edit_res_width, 2, 1, 1, 1)
        
        self.line_edit_res_height = QtWidgets.QLineEdit(self.frame_train_preprocess)
        self.line_edit_res_height.setEnabled(False)
        self.line_edit_res_height.setInputMethodHints(QtCore.Qt.ImhDigitsOnly)
        self.line_edit_res_height.setObjectName("line_edit_res_height")
        self.gridLayout_6.addWidget(self.line_edit_res_height, 3, 1, 1, 1)
        
        spacerItem2 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout_6.addItem(spacerItem2, 2, 2, 1, 1)
        self.line_edit_dataset_path = QtWidgets.QLineEdit(self.frame_train_preprocess)
        self.line_edit_dataset_path.setObjectName("line_edit_dataset_path")
        self.gridLayout_6.addWidget(self.line_edit_dataset_path, 0, 1, 1, 2)
        
        self.gridLayout_9.addWidget(self.frame_train_preprocess, 1, 0, 1, 1)
        self.tensorflow_tabs.addTab(self.tab_train, "")
        
        self.gridLayout_3.addWidget(self.tensorflow_tabs, 2, 0, 1, 2)
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
        
        self.action_save_frame = QtWidgets.QAction(MainWindow)
        self.action_save_frame.setShortcutContext(QtCore.Qt.WindowShortcut)
        self.action_save_frame.setObjectName("action_save_frame")
        
        self.action_save_settings = QtWidgets.QAction(MainWindow)
        self.action_save_settings.setStatusTip("")
        self.action_save_settings.setObjectName("action_save_settings")
        
        self.menuFile.addAction(self.action_save_frame)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.action_save_settings)
        
        self.menuOptions.addAction(self.actionAdd_Remove_cti_file)
        self.menuOptions.addAction(self.actionRemove_cti_file)
        self.menuHelp.addAction(self.actionOpen_Help)
        
        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuOptions.menuAction())
        self.menubar.addAction(self.menuHelp.menuAction())
        #----------------------------------------------------------------
        
        #--------------------------------------------------------------
        
        self.connect_actions()
        self.retranslateUi(MainWindow)
        self.read_config()
        self.tabs.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
        
        
        self.vision = Computer_vision(self.predictions)
        
    
    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.btn_zoom_100.setText(_translate("MainWindow", "Zoom to 100%"))
        self.btn_zoom_fit.setText(_translate("MainWindow", "Fit to window"))
        self.btn_start_recording.setText(_translate("MainWindow", "Start/Stop recording"))
        self.btn_start_preview.setText(_translate("MainWindow", "Start/Stop preview"))
        self.btn_single_frame.setText(_translate("MainWindow", "Single frame"))
        self.btn_zoom_in.setText(_translate("MainWindow", "Zoom In"))
        self.btn_zoom_out.setText(_translate("MainWindow", "Zoom Out"))
        self.btn_connect_camera.setText(_translate("MainWindow", "Connect"))
        self.btn_refresh_cameras.setText(_translate("MainWindow", "Refresh"))
        self.btn_disconnect_camera.setText(_translate("MainWindow", "Disconnect"))
        self.tip_add_cti.setText(_translate("MainWindow", "Tip: If you can\'t detect your camera try adding new .cti file from your camera vendor"))
        self.tabs.setTabText(self.tabs.indexOf(self.tab_connect), _translate("MainWindow", "Connect Camera"))
        self.btn_add_cti.setText(_translate("MainWindow", "Add .cti file"))
        self.label_config_level.setText(_translate("MainWindow", "Configuration level"))
        self.combo_config_level.setItemText(0, _translate("MainWindow", "Beginner"))
        self.combo_config_level.setItemText(1, _translate("MainWindow", "Expert"))
        self.combo_config_level.setItemText(2, _translate("MainWindow", "Guru"))
        self.tree_features.headerItem().setText(0, _translate("MainWindow", "Feature"))
        self.tree_features.headerItem().setText(1, _translate("MainWindow", "Value"))
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
        self.tabs.setTabText(self.tabs.indexOf(self.tab_tensorflow), _translate("MainWindow", "Tensorflow"))
        self.btn_save_model.setText(_translate("MainWindow", "Save model"))
        self.line_edit_model_name.setText(_translate("MainWindow", "Select a model to load"))
        self.btn_load_model.setText(_translate("MainWindow", "Load model"))
        self.tensorflow_tabs.setTabText(self.tensorflow_tabs.indexOf(self.tab_classify), _translate("MainWindow", "Classify"))
        self.tensorflow_tabs.setTabText(self.tensorflow_tabs.indexOf(self.tab_classify), _translate("MainWindow", "Classify"))
        self.label_val_acc.setText(_translate("MainWindow", "Validation Accuracy"))
        self.label_acc.setText(_translate("MainWindow", "Accuracy"))
        self.label_val_loss.setText(_translate("MainWindow", "Validation Loss"))
        self.label_epoch.setText(_translate("MainWindow", "Epoch: "))
        self.label_active_epoch.setText(_translate("MainWindow", "0/0"))
        self.label_loss.setText(_translate("MainWindow", "Loss"))
        self.btn_train_cancel.setText(_translate("MainWindow", "Train"))
        self.label_img_resize.setText(_translate("MainWindow", "Resize dimensions"))
        self.btn_load_dataset.setText(_translate("MainWindow", "Select Dataset"))
        self.label_val_split.setText(_translate("MainWindow", "Data for a validation [%]"))
        self.line_edit_val_split.setText(_translate("MainWindow", "70"))
        self.label_train_epochs.setText(_translate("MainWindow", "Train epochs"))
        self.btn_preprocess.setText(_translate("MainWindow", "Preprocess Data"))
        self.label_res_width.setText(_translate("MainWindow", "Width"))
        self.label_res_height.setText(_translate("MainWindow", "Height"))
        self.tensorflow_tabs.setTabText(self.tensorflow_tabs.indexOf(self.tab_train), _translate("MainWindow", "Train"))
        self.tabs.setTabText(self.tabs.indexOf(self.tab_tensorflow), _translate("MainWindow", "Tensorflow"))
        self.menuFile.setTitle(_translate("MainWindow", "File"))
        self.menuOptions.setTitle(_translate("MainWindow", "Tools"))
        self.menuHelp.setTitle(_translate("MainWindow", "Help"))
        self.actionAdd_Remove_cti_file.setText(_translate("MainWindow", "Add .cti file"))
        self.actionOpen_Help.setText(_translate("MainWindow", "Open Help"))
        self.actionRemove_cti_file.setText(_translate("MainWindow", "Remove .cti file"))
        self.action_save_frame.setText(_translate("MainWindow", "Save frame"))
        self.action_save_settings.setText(_translate("MainWindow", "Save settings"))
        self.action_save_settings.setToolTip(_translate("MainWindow", "Save modifications made to application settings"))
        self.action_save_settings.setShortcut(_translate("MainWindow", "Ctrl+S, Ctrl+S"))
        
        #added manually
        self.camera_status.setText("Camera: Not connected")
        self.receive_status.setText("Received frames: 0")
        self.fps_status.setText("FPS: 0")
        self.camera_icon.setPixmap(self.icon_offline)
        
    
    def connect_actions(self):
        
        self.btn_zoom_out.clicked.connect(lambda: self.set_zoom(-1))
        self.btn_zoom_fit.clicked.connect(lambda: self.set_zoom(0))
        self.btn_zoom_in.clicked.connect(lambda: self.set_zoom(1))
        self.btn_zoom_100.clicked.connect(lambda: self.set_zoom(100))
        self.btn_single_frame.clicked.connect(self.single_frame)
        self.btn_start_preview.clicked.connect(self.preview)
        self.btn_start_recording.clicked.connect(self.record)
        self.btn_refresh_cameras.clicked.connect(self.refresh_cameras)
        self.btn_add_cti.clicked.connect(self.add_cti)
        
        self.btn_connect_camera.clicked.connect(
            lambda: self.connect_camera(self.list_detected_cameras.currentRow()))
        
        self.list_detected_cameras.itemDoubleClicked.connect(
            lambda: self.connect_camera(self.list_detected_cameras.currentRow()))
        #možná lambda s indexem itemu
        
        self.btn_disconnect_camera.clicked.connect(self.disconnect_camera)
        self.combo_config_level.currentIndexChanged.connect(self.load_parameters)
        self.btn_save_config.clicked.connect(self.save_cam_config)
        self.btn_load_config.clicked.connect(self.load_cam_config)
        self.file_manager_save_location.clicked.connect(lambda: self.get_directory(self.line_edit_save_location))
        
        self.btn_save_sequence_settings.clicked.connect(self.save_seq_settings)
        self.btn_reset_sequence_settings.clicked.connect(self.reset_seq_settings)
        self.btn_save_model.clicked.connect(self.save_model)
        self.btn_load_model.clicked.connect(self.load_model)
        self.btn_load_dataset.clicked.connect(lambda: self.get_directory(self.line_edit_dataset_path))
        self.btn_preprocess.clicked.connect(self.preprocess_dataset)
        self.btn_train_cancel.clicked.connect(self.train_model)
        
        self.action_save_settings.triggered.connect(self.save_cti_config)
    #Start of custom methods (not generated by QtDesigner)
    
    def eventFilter(self, obj, event):
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
    
    def add_cti(self):
        path = QtWidgets.QFileDialog.getOpenFileName(self.centralwidget,
                                                     "Load GenTL producer",
                                                     filter="CTI files (*.cti)")
        
        cam.add_gentl_producer(path[0])
        self.set_status_msg("File added")
    
    def refresh_cameras(self):
        """!@brief Calls function to detect connected cameras and prints them
        as items in a list.
        @details If no cameras are present nothing will happen. If cameras are
        detected, all previous item are cleared and cameras detected in this call
        are printed.
        """
        #set status message
        self.set_status_msg("Searching for cameras", 1500)
        
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
            
            #set green background to the selected camera
            self.list_detected_cameras.item(index).setBackground(QtGui.QColor('#70BF4E'))
            
            #Print status message
            self.set_status_msg("Connecting camera")
            
            #Connect camera
            cam.select_camera(self.detected[index]['id_'])
            
            
            self.set_status_msg("Camera connected")
            
            #Change packet size for ethernet camera
#In the future this will happen only for ethernet cameras
           # p = {'name': 'GVSPPacketSize'}
            #cam.set_parameter(p,1500)
#THIS IS NOT WORKING NOW!!! FIX IT
            
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
                self.set_status_msg("Recording stopped", 3500)
    
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
                self.set_status_msg("Starting preview",1500)
                
                #Start camera frame acquisition (not recording)
                cam.start_acquisition()
                
                self.preview_live = True
                
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
        @details Acquire and draw a single frame.
        """
        #Method runs only if camera is connected
        if self.connected:
            #Set status icon and message
            self.set_status_msg("Receiving single frame",1500)
            self.camera_icon.setPixmap(self.icon_busy)
            
            #Get image
            image = cam.get_single_frame()
            
            #Try to run prediction
            self.predict(image)
            
            #Set up a new value of received frames in the statusbar
            self.received = self.received + 1
            self.receive_status.setText("Received frames: " + str(self.received))
            
            #Convert image to proper format fo PyQt
            h, w, ch = image.shape
            bytes_per_line = ch * w
            image = QtGui.QImage(image.data, w, h, bytes_per_line, QtGui.QImage.Format_Grayscale8)
#TODO Get color format dynamically
            
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
        only one at the time is drawn and the rest is dumped
        """
        #Determine refresh rate of used display. This way the method will not
        #run too slowly or redundantly fast.
        device = win32api.EnumDisplayDevices()
        refresh_rate = win32api.EnumDisplaySettings(device.DeviceName, -1).DisplayFrequency
        
        #Auxiliary variables for fps calculation
        frames = 0
        cycles = 0
        #runs as long as the camera is recording or preview is active
        while self.recording or self.preview_live:
            cycles = cycles + 1
            
            #Draw only if thre is at least 1 frame to draw
            if not active_frame_queue.qsize() == 0:
                image = active_frame_queue.get_nowait()
                self.received = self.received + 1
                
                frames = frames + 1
                
                #Dump all remaining frames (If frames are received faster than 
                #refresh_rate).
                while not active_frame_queue.qsize() == 0:
                    frames = frames + 1
                    self.received = self.received + 1
                    active_frame_queue.get_nowait()
                
                #Try to run a prediction
                self.predict(image)
                
                #Set up a new value of received frames in the statusbar
                self.receive_status.setText("Received frames: " + str(self.received))
                
                #More cycles -> more exact fps calculation (value is more stable in gui)
                if cycles > 20:
                    #[frames*Hz/c] -> [frames/s]
                    self.fps = round(frames*(refresh_rate/cycles),1)
                    self.fps_status.setText("FPS: " + str(self.fps))
                    
                    cycles = 0
                    frames = 0
                
                #Convert image to proper format fo PyQt
                h, w, ch = image.shape
                bytes_per_line = ch * w
                image = QtGui.QImage(image.data, w, h, bytes_per_line, QtGui.QImage.Format_Grayscale8)
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
        if(self.resize_signal.text() != "A"):
            self.resize_signal.setText("A")
        else:
            self.resize_signal.setText("B")
    
    def update_img(self):
        #Resize preview label if preview window size changed
        if(self.w_preview != self.camera_preview.size().width() or
                   self.h_preview != self.camera_preview.size().height()):
            self.camera_preview.resize(self.w_preview,
                                       self.h_preview)
        
        self.camera_preview.setPixmap(self.image_pixmap)
        self.camera_preview.show()
        
    def predict(self,frame):
        #Tensorflow index is 3, if the gui changes, this may need to chage as well
        if(self.tabs.currentIndex()==3):
            if(not self.prediction_flag.is_set()):
                self.prediction_flag.set()
                
                self.prediction_thread = threading.Thread(
                    target=self.vision.classify, kwargs={'frame': frame, 'prediction_flag': self.prediction_flag})
                self.prediction_thread.start()
                
    
    
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
        
    def callback_parameters(self):
        self.param_flag.wait()
        
        if(self.parameters_signal.text() != "A"):
            self.parameters_signal.setText("A")
        else:
            self.parameters_signal.setText("B")
        
    def show_parameters(self):
        #Keeps track of line in the layout
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
                    self.feat_widgets[param["name"]].stateChanged.connect(lambda param=param: cam.set_parameter(param,self.feat_widgets[param["name"]].isChecked()))
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
                    self.feat_widgets[param["name"]].activated.connect(lambda param=param: cam.set_parameter(param,self.feat_widgets[param["name"]].currentText()))
                elif param["attr_type"] == "CommandFeature":
                    #If the feature type is not recognized, create a label with 
                    #the text error
                    self.feat_widgets[param["name"]] = QtWidgets.QButton(self.tab_config)
                    self.feat_widgets[param["name"]].setText("Execute command")
                    self.feat_widgets[param["name"]].clicked.connect(lambda param=param: cam.execute_command(param))
                else:
                    #If the feature type is not recognized, create a label with 
                    #the text error
                    self.feat_widgets[param["name"]] = QtWidgets.QLabel(self.tab_config)
                    self.feat_widgets[param["name"]].setText("Error")
                
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
    
    def update_parameters(self):
        if self.connected and not self.param_flag.is_set():
            for parameter in self.feat_widgets:
                value = cam.read_param_value(parameter)
                widget = self.feat_widgets[parameter]
                if(type(widget) == QtWidgets.QLineEdit):
                    widget.setText(str(value))
                elif(type(widget) == QtWidgets.QComboBox):
                    index = widget.findText(str(value), QtCore.Qt.MatchFixedString)
                    #Set found index to be the active one
                    if index >= 0:
                        widget.setCurrentIndex(index)
                elif(type(widget) == QtWidgets.QCheckBox):
                    widget.setChecked(value)
                else:
                    print("Update nott implemented")
        
        
    def load_parameters(self):
        """!@brief Fills layout with feature name and value pairs
        @details Based on the feature type a new label, text area, checkbox or
        combo box is created. In this version all available parameters are shown.
        TODO config level and command feature type
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
        if self.connected:
            name = QtWidgets.QFileDialog.getOpenFileName(self.centralwidget,
                                                         "Load Configuration",
                                                         filter="XML files (*.xml)")
           
            #Set label text to chosen folder path
            cam.load_config(name[0])
            
            self.set_status_msg("Configuration loaded")
        
        
    def get_directory(self, line_output):
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
        line_output.setText(name)
        return name
        
    def read_config(self):
        """!@brief Loads configuration from config.ini file
        @details This method is called on startup and loads all modifications
        user made to applications default state.
        @TODO load cti files from config
        """
        
        cti_files = False
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
                elif(line.startswith("CTI_FILES_PATHS")):
                    cti_files = True
                elif(cti_files == True):
                    cam.add_gentl_producer(line)
#TODO reading and adding cti files
        
        #Set status update
        self.set_status_msg("Configuration loaded",1500)
    
    def load_model(self):
        #Open file dialog for choosing a folder
        name = self.get_directory(self.line_edit_model_name)
        
        dim = self.vision.load_model(name)
        #Set label text to chosen folder path
        if(dim):
            self.line_edit_res_width.setText(str(dim[0]))
            self.line_edit_res_height.setText(str(dim[1]))
            self.set_status_msg("Model loaded")
        else:
            self.set_status_msg("Failed to load model")
            self.line_edit_model_name.setText("Select a model to load")
        
    def save_model(self):
        #Open file dialog for choosing a folder
        name = QtWidgets.QFileDialog.getSaveFileName(self.centralwidget,
                                                     "Save Model",
                                                     filter="Keras model folder (*.model)",
                                                     )
        
        #Set label text to chosen folder path
        self.vision.save_model(name)
        
        self.set_status_msg("Model saved")
    
    def reset_seq_settings(self):
        """!@brief Restores default recording settings
        @details Settings are saved to config.ini file. Defaults are hard-coded
        in this method.
        """
        file_contents = []
        
        #Open config file and load its contents
        with open("config.ini", 'r') as config:
            file_contents = config.readlines()
        
        end_of_rec_conf = None
        #Find end of Recording config part of the file
        #if no delimiter is found a new one is added
        try:
            end_of_rec_conf = file_contents.index("CTI_FILES_PATHS\n")
        except(ValueError):
            file_contents.append("CTI_FILES_PATHS\n")
            end_of_rec_conf = -1
            
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
        self.set_status_msg("Configuration restored",2500)
    
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
            self.received = 0
            self.fps = 0.0
            self.camera_icon.setPixmap(self.icon_offline)
            self.camera_status.setText("Camera: Not connected")
            
            self.receive_status.setText("Received frames: " + str(self.received))
            self.fps_status.setText("FPS: " + str(self.fps))
            self.set_status_msg("Disconnecting camera")
            
            #Disconnect camera
            cam.disconnect_camera()
            
            
            self.set_status_msg("Camera disconnected")
            
            #Imidiately search for new cameras
            self.refresh_cameras()
        
    def preprocess_dataset(self):
        if(self.line_edit_dataset_path.text()):
            try:
                path = self.line_edit_dataset_path.text()
                split = float(self.line_edit_val_split.text())/100
                files = os.scandir(path)
                categories = []
                
                for file in files:
                    if file.is_dir():
                        categories.append(file.name)
                
                self.process_flag.clear()
                
                self.preprocess_thread = threading.Thread(
                    target=self.vision.process_dataset, 
                    kwargs={'path': path,
                            'process_perc': self.process_perc,
                            'split': split, 'categories': categories,
                            'process_flag': self.process_flag,
                            'callback_flag': self.process_prog_flag})
                self.callback_preprocess_thread = threading.Thread(target=self.preprocess_callback)
                
                
                self.callback_preprocess_thread.start()
                self.preprocess_thread.start()
            except:
                self.process_prog_flag.clear()
                self.process_flag.clear()
   
    def preprocess_callback(self):
        while(not self.process_flag.is_set()):
            self.process_prog_flag.wait(2)
            if(not self.process_prog_flag.is_set()):
                continue
            self.process_prog_flag.clear()
            if(self.callback_process_signal.text() != "A"):
                self.callback_process_signal.setText("A")
            else:
                self.callback_process_signal.setText("B")
                
        self.set_status_msg("Dataset preprocess completed")
    
    def update_processing(self):
        self.progress_bar_preprocess.setValue(int(self.process_perc[0]))
        
    def train_model(self):
        if(not self.training_flag.is_set()):
            self.training_flag.set()
            print("hola hola")
            self.train_thread = threading.Thread(target=self.vision.train, kwargs={
                'train_vals': self.train_vals,
                'progress_flag': self.progress_flag,
                'training_flag': self.training_flag})
            
            self.callback_train_thread = threading.Thread(target=self.training_callback)
            
            self.callback_train_thread.start()
            self.train_thread.start()
        else:
            #stop training prematurely
            self.training_flag.clear()
    
    def training_callback(self):
        while(self.training_flag.is_set()):
            self.progress_flag.wait(2)
            if(not self.progress_flag.is_set()):
                continue
            self.progress_flag.clear()
            if(self.callback_train_signal.text() != "A"):
                self.callback_train_signal.setText("A")
            else:
                self.callback_train_signal.setText("B")
        self.set_status_msg("Training ended")
            
            
            
        
    def update_training(self):
        self.progress_bar_train.setValue(self.train_vals['progress'])
        self.line_edit_loss.setText(str(self.train_vals['loss']))
        self.line_edit_acc.setText(str(self.train_vals['acc']))
        self.line_edit_val_loss.setText(str(self.train_vals['val_loss']))
        self.line_edit_val_acc.setText(str(self.train_vals['val_acc']))
        self.label_active_epoch.setText(str(self.train_vals['epoch']) + '/' + str(self.train_vals['max_epoch']))
    
    def save_cti_config(self):
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