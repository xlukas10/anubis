from PyQt5 import QtCore, QtWidgets 
import global_camera
from PyQt5.QtCore import pyqtSignal as Signal
import os
import threading
from queue import Queue
from config_level import Config_level

class Tab_configure(QtWidgets.QWidget):
    #signals
    ##Used to send status message to the GUI
    send_status_msg = Signal(str, int)

    def __init__(self):
        super(Tab_configure, self).__init__()
        self.preview_live = False
        self.recording = False
        ##Holds parameter category paths for tree widget
        self.top_items = {}
        ##Holds children widgets for tree widget
        self.children_items = {}

        ##Flag is not set while the application is getting parameters from the cam object
        self.param_flag = threading.Event()

        ##Flag used when running various parameter refreshing methods
        self.update_flag = threading.Event()
        ##Flag used when running various parameter refreshing methods
        self.update_completed_flag = threading.Event()
        self.update_completed_flag.set()


        ##Used to store values of parameters when automatically refreshing them
        self.parameter_values = {}

        self.tab_index = 0
        
        ##Contains all dynamically created widgets for parameters
        self.feat_widgets = {}
        ##Contains all dynamically created labels of parameters
        self.feat_labels = {}
        ##Stores dictionaries of every parameter until they are processed to the GUI
        self.feat_queue = Queue()

        self.connected = False
        ##Widget used to transfer GUI changes from thread into the main thread while showing parameters
        self.parameters_signal = QtWidgets.QLineEdit()
        self.parameters_signal.textChanged.connect(self.show_parameters)

        self.add_widgets()
        self.connect_actions()
        self.set_texts()

    def add_widgets(self):
        self.setObjectName("tab_configure")
        self.layout_main = QtWidgets.QVBoxLayout(self)
        self.layout_main.setObjectName("layout_main")
        
        self.frame_config_level = QtWidgets.QFrame(self)
        self.frame_config_level.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_config_level.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_config_level.setObjectName("frame_config_level")
        self.layout_config_level = QtWidgets.QHBoxLayout(self.frame_config_level)
        self.layout_config_level.setObjectName("layout_config_level")
        self.label_config_level = QtWidgets.QLabel(self.frame_config_level)
        self.label_config_level.setObjectName("label_config_level")
        self.layout_config_level.addWidget(self.label_config_level)
        self.combo_config_level = QtWidgets.QComboBox(self.frame_config_level)
        self.combo_config_level.setObjectName("combo_config_level")
        self.combo_config_level.addItem("")
        self.combo_config_level.addItem("")
        self.combo_config_level.addItem("")
        
        self.layout_config_level.addWidget(self.combo_config_level)
        self.layout_main.addWidget(self.frame_config_level)
        
        
        self.tree_features = QtWidgets.QTreeWidget(self)
        self.tree_features.setObjectName("tree_features")
        self.tree_features.setColumnWidth(0,250)
        self.layout_main.addWidget(self.tree_features)
        
        
        self.widget_3 = QtWidgets.QWidget(self)
        self.widget_3.setObjectName("widget_3")
        self.layout_save_load_conf = QtWidgets.QHBoxLayout(self.widget_3)
        self.layout_save_load_conf.setObjectName("layout_save_load_conf")
        
        self.btn_save_config = QtWidgets.QPushButton(self.widget_3)
        self.btn_save_config.setObjectName("btn_save_config")
        
        self.layout_save_load_conf.addWidget(self.btn_save_config)
        
        self.btn_load_config = QtWidgets.QPushButton(self.widget_3)
        self.btn_load_config.setObjectName("btn_load_config")
        self.layout_save_load_conf.addWidget(self.btn_load_config)
        
        self.layout_main.addWidget(self.widget_3)
        
    def connect_actions(self):
        self.combo_config_level.currentIndexChanged.connect(self.load_parameters)
        self.btn_save_config.clicked.connect(self.save_cam_config)
        self.btn_load_config.clicked.connect(self.load_cam_config)

    def set_texts(self):
        self.label_config_level.setText("Configuration level")
        self.combo_config_level.setItemText(0, "Beginner")
        self.combo_config_level.setItemText(1, "Expert")
        self.combo_config_level.setItemText(2, "Guru")
        self.tree_features.headerItem().setText(0, "Feature")
        self.tree_features.headerItem().setText(1, "Value")
        self.btn_save_config.setText("Save Configuration")
        self.btn_load_config.setText("Load Configuration")

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
            
                self.feat_labels[param["name"]] = QtWidgets.QLabel(self)
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
                    self.feat_widgets[param["name"]] = QtWidgets.QSpinBox(self)
                    if(param["attr_range"]):
                        self.feat_widgets[param["name"]].setRange(
                                                param["attr_range"][0],
                                                param["attr_range"][1])
                    
                    #Set text to the current value of the feature
                    self.feat_widgets[param["name"]].setValue(param["attr_value"])
                    
                    #Call feature change for this feature when enter is pressed in this field.
                    #Text is the value that will be set to the feature.
                    self.feat_widgets[param["name"]].valueChanged.connect(lambda new_val,param=param: global_camera.cams.active_devices[global_camera.active_cam].set_parameter(param["name"],new_val))
                elif param["attr_type"] == "FloatFeature":
                    #For float feature a Line edit field is created, but only 
                    #real numbers can be written in.
                    self.feat_widgets[param["name"]] = QtWidgets.QDoubleSpinBox(self)
                    if(param["attr_range"]):
                        self.feat_widgets[param["name"]].setRange(
                                                param["attr_range"][0],
                                                param["attr_range"][1])
                    
                    #Set text to the current value of the feature
                    self.feat_widgets[param["name"]].setValue(param["attr_value"])
                    
                    #Call feature change for this feature when enter is pressed in this field.
                    #Text is the value that will be set to the feature.
                    self.feat_widgets[param["name"]].valueChanged.connect(lambda new_val,param=param: global_camera.cams.active_devices[global_camera.active_cam].set_parameter(param["name"],new_val))
                elif param["attr_type"] == "StringFeature":
                    #For string feature a Line edit field is created.
                    self.feat_widgets[param["name"]] = QtWidgets.QLineEdit(self)
                    
                    #Set text to the current value of the feature
                    self.feat_widgets[param["name"]].setText(param["attr_value"])
                    
                    #Call feature change for this feature when enter is pressed in this field.
                    #Text is the value that will be set to the feature.
                    self.feat_widgets[param["name"]].returnPressed.connect(lambda new_val,param=param: global_camera.cams.active_devices[global_camera.active_cam].set_parameter(param["name"],new_val))            
                elif param["attr_type"] == "BoolFeature":
                    #For bool feature a checkbox is created.
                    self.feat_widgets[param["name"]] = QtWidgets.QCheckBox(self)
                    
                    #If value is true the checkbox is ticked otherwise remains empty
                    self.feat_widgets[param["name"]].setChecked(param["attr_value"])
                    
                    #When state of the checkbox change, the feature is sent to 
                    #the camera and changed to the new state
                    self.feat_widgets[param["name"]].stateChanged.connect(lambda new_val,param=param: global_camera.cams.active_devices[global_camera.active_cam].set_parameter(param["name"],new_val))
                elif param["attr_type"] == "EnumFeature":
                    #For enum feature a combo box is created.
                    self.feat_widgets[param["name"]] = QtWidgets.QComboBox(self)
                    
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
                    self.feat_widgets[param["name"]].activated.connect(lambda new_val,param=param: global_camera.cams.active_devices[global_camera.active_cam].set_parameter(param["name"],new_val+1))
                elif param["attr_type"] == "CommandFeature":
                    #If the feature type is not recognized, create a label with 
                    #the text error
                    self.feat_widgets[param["name"]] = QtWidgets.QPushButton(self)
                    self.feat_widgets[param["name"]].setText("Execute command")
                    self.feat_widgets[param["name"]].clicked.connect(lambda val,param=param: global_camera.cams.active_devices[global_camera.active_cam].execute_command(param["name"]))
                else:
                    #If the feature type is not recognized, create a label with 
                    #the text error
                    self.feat_widgets[param["name"]] = QtWidgets.QLabel(self)
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
        if (self.feat_widgets and self.connected and self.tab_index == 1 and
            not(self.preview_live or self.recording) and 
            not self.param_flag.is_set() and self.update_completed_flag.is_set()):
            
            self.update_completed_flag.clear()
            
            self.update_thread = threading.Thread(target=self.get_new_val_parameters)
            self.update_thread.daemon = True
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
            if(global_camera.cams.active_devices[global_camera.active_cam].get_parameters(params, 
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
               self.tab_index == 1):
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
            self.tab_index == 1 and
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
            
            self.send_status_msg.emit("Reading features", 0)
            
            #empty feature queue
            self.get_params_thread = threading.Thread(
                target=global_camera.cams.active_devices[global_camera.active_cam].get_parameters,
                kwargs={'feature_queue': self.feat_queue,
                        'flag': self.param_flag,
                        'visibility': Config_level(self.combo_config_level.currentIndex()+1)})
            self.param_callback_thread = threading.Thread(target=self.callback_parameters)
            
            self.param_callback_thread.daemon = True
            self.get_params_thread.daemon = True

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
            name = QtWidgets.QFileDialog.getSaveFileName(self,
                                                         "Save Configuration",
                                                         filter="XML files (*.xml)",
                                                         directory="config.xml")
            
            #Save camera config to path specified in name (0 index)
            global_camera.cams.active_devices[global_camera.active_cam].save_config(name[0])
    
    def load_cam_config(self):
        """!@brief Allows a user to choose saved xml configuration and load it
        into the camera
        @details Allowes only xml file in the file dialog and after loading prints
        a status message
        """
        if self.connected:
            if(not self.recording and not self.preview_live):
                name = QtWidgets.QFileDialog.getOpenFileName(self,
                                                             "Load Configuration",
                                                             filter="XML files (*.xml)")
               
                #Set label text to chosen folder path
                if(name[0]):
                    tries = 0
                    while(tries <= 10):
                        if(global_camera.cams.active_devices[global_camera.active_cam].load_config(name[0])):
                            self.send_status_msg.emit("Configuration loaded", 0)
                            return
                        else:
                            tries += 1
                    self.send_status_msg.emit("Loading failed", 2500)
            else:
                self.send_status_msg.emit("Stop recording and preview before loading config", 0)
        
    def callback_parameters(self):
        """!@brief Auxiliary method used to transfer thread state change into
        the main thread.
        """
        self.param_flag.wait()
        
        if(self.parameters_signal.text() != "A"):
            self.parameters_signal.setText("A")
        else:
            self.parameters_signal.setText("B")
    
   
 