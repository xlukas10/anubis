from PyQt5 import QtCore, QtGui, QtWidgets 
from PyQt5.QtCore import pyqtSignal as Signal

class Tab_recording(QtWidgets.QWidget):
    #signals
    ##Used to send status message to the GUI
    send_status_msg = Signal(str, int)
    ##Signal configuration change to the GUI
    configuration_update = Signal(str, str, float)#name, location, duration

    def __init__(self):
        super(Tab_recording, self).__init__()

        self.add_widgets()
        self.connect_actions()
        self.set_texts()

    def add_widgets(self):
        self.setObjectName("tab_recording_config")
        self.layout_main = QtWidgets.QVBoxLayout(self)
        self.layout_main.setObjectName("layout_main")
        
        self.widget_sequence_name = QtWidgets.QWidget(self)
        self.widget_sequence_name.setObjectName("widget_sequence_name")
        
        self.layout_sequence_name = QtWidgets.QFormLayout(self.widget_sequence_name)
        self.layout_sequence_name.setObjectName("layout_sequence_name")
        
        self.label_file_name_recording = QtWidgets.QLabel(self.widget_sequence_name)
        self.label_file_name_recording.setObjectName("label_file_name_recording")
        self.layout_sequence_name.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.label_file_name_recording)
        
        self.line_edit_sequence_name = QtWidgets.QLineEdit(self.widget_sequence_name)
        self.line_edit_sequence_name.setObjectName("line_edit_sequence_name")
        self.layout_sequence_name.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.line_edit_sequence_name)
        
        self.layout_main.addWidget(self.widget_sequence_name)
        
        self.label_sequence_name = QtWidgets.QLabel(self)
        self.label_sequence_name.setObjectName("label_sequence_name")
        self.layout_main.addWidget(self.label_sequence_name)
        
        self.widget_sequence_save = QtWidgets.QWidget(self)
        self.widget_sequence_save.setObjectName("widget_sequence_save")
        self.layout_save = QtWidgets.QFormLayout(self.widget_sequence_save)
        self.layout_save.setObjectName("layout_save")
        
        self.file_manager_save_location = QtWidgets.QPushButton(self.widget_sequence_save)
        self.file_manager_save_location.setObjectName("file_manager_save_location")
        
        self.layout_save.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.file_manager_save_location)
        
        self.line_edit_save_location = QtWidgets.QLineEdit(self.widget_sequence_save)
        self.line_edit_save_location.setObjectName("line_edit_save_location")
        self.layout_save.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.line_edit_save_location)
        
        self.layout_main.addWidget(self.widget_sequence_save)
        
        self.widget_duration = QtWidgets.QWidget(self)
        self.widget_duration.setObjectName("widget_duration")
        self.layout_duration = QtWidgets.QFormLayout(self.widget_duration)
        self.layout_duration.setObjectName("layout_duration")
        
        self.label_sequence_duration = QtWidgets.QLabel(self.widget_duration)
        self.label_sequence_duration.setObjectName("label_sequence_duration")
        self.layout_duration.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.label_sequence_duration)
        
        self.line_edit_sequence_duration = QtWidgets.QDoubleSpinBox(self.widget_duration)
        self.line_edit_sequence_duration.setObjectName("line_edit_sequence_duration")
        #accept only numbers
        
        self.layout_duration.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.line_edit_sequence_duration)
        
        self.layout_main.addWidget(self.widget_duration)
        
        self.label_sequence_duration_tip = QtWidgets.QLabel(self)
        self.label_sequence_duration_tip.setObjectName("label_sequence_duration_tip")
        self.layout_main.addWidget(self.label_sequence_duration_tip)
        
        spacerItem1 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.layout_main.addItem(spacerItem1)
        
        self.btn_save_sequence_settings = QtWidgets.QPushButton(self)
        self.btn_save_sequence_settings.setObjectName("btn_save_sequence_settings")
        self.layout_main.addWidget(self.btn_save_sequence_settings)
        
        self.btn_reset_sequence_settings = QtWidgets.QPushButton(self)
        self.btn_reset_sequence_settings.setObjectName("btn_reset_sequence_settings")
        
        self.layout_main.addWidget(self.btn_reset_sequence_settings)
        
        self.file_manager_save_location.clicked.connect(lambda: self.get_directory(self.line_edit_save_location))
        self.btn_save_sequence_settings.clicked.connect(self.save_seq_settings)
        self.btn_reset_sequence_settings.clicked.connect(self.reset_seq_settings)


    def connect_actions(self):
        self.line_edit_save_location.textChanged.connect(self.send_conf_update)
        self.line_edit_sequence_duration.valueChanged.connect(self.send_conf_update)
        self.line_edit_sequence_name.textChanged.connect(self.send_conf_update)

    def set_texts(self):
        self.label_file_name_recording.setText("File name")
        self.label_sequence_name.setText("Tip: Use %n for sequence number, %d for date and %t for time stamp ")
        self.file_manager_save_location.setText("Save Location")
        self.label_sequence_duration.setText("Sequence duration [s]")
        self.label_sequence_duration_tip.setText("Tip: Leave empty for manual control using Start/Stop recording buttons")
        self.btn_save_sequence_settings.setText("Save settings")
        self.btn_reset_sequence_settings.setText("Default settings")
        
    def setup_validators(self):
        """!@brief create input constrains for various widgets
        @details if a text widget needs certain input type, the validators are
        set up here. For example setting prohibited characters of the file saved.
        """
        self.line_edit_sequence_duration.setValidator(QtGui.QDoubleValidator(0,16777216,5))
        expression = QtCore.QRegExp("^[^\\\\/:*?\"<>|]*$")
        self.line_edit_sequence_name.setValidator(QtGui.QRegExpValidator(expression))

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
        self.load_config("img(%n)", "Recording", "0")
        
        #Print status msg
        self.send_status_msg.emit("Configuration restored",2500)
    
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
        self.send_status_msg.emit("Configuration saved", 0)
    

    def load_config(self, filename=None , save_location=None, sequence_duration=None):
        """!@brief Fills in saved values for recording configuration
        @param[in] filename Template for naming saved files
        @param[in] save_location Where should the images be saved
        @param[in] sequence_duration Length of a recording sequence
        """
        try:
            sequence_duration = float(sequence_duration)
        except ValueError:
            sequence_duration = 0
    
        if(filename):
            self.line_edit_sequence_name.setText(filename)
        if(save_location):
            self.line_edit_save_location.setText(save_location)
        if(sequence_duration):
            self.line_edit_sequence_duration.setValue(sequence_duration)

    def get_directory(self, line_output = None):
        """!@brief Opens file dialog for user to set path to save frames.
        @details Method is called by Save Location button. Path is written to 
        the label next to the button and can be further modified.
        """
        #Open file dialog for choosing a folder
        name = QtWidgets.QFileDialog.getExistingDirectory(self,
                                                     "Select Folder",
                                                     )
        
        #Set label text to chosen folder path
        if(line_output):
            line_output.setText(name)
        return name
    
    def send_conf_update(self):
        """!@brief Used to emit configuration update signal based on current values of line edits"""
        self.configuration_update.emit(self.line_edit_sequence_name.text(), 
                                        self.line_edit_save_location.text(), 
                                        self.line_edit_sequence_duration.value())
                                        
