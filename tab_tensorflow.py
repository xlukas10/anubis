from PyQt5 import QtCore, QtGui, QtWidgets 
from PyQt5.QtCore import pyqtSignal as Signal
from prediction_graph import Prediction_graph
from computer_vision import Computer_vision
import os
import threading

class Tab_tensorflow(QtWidgets.QWidget):
    #signals
    send_status_msg = Signal(str, int)
    #connection_update = Signal(bool, int, str)#connected, state - 0=disconnected 1=standby 2=busy, camera name

    def __init__(self):
        super(Tab_tensorflow, self).__init__()

        ##Widget used to transfer GUI changes from thread into the main thread while training
        self.callback_train_signal = QtWidgets.QLineEdit()
        self.callback_train_signal.textChanged.connect(self.update_training)
        
        ##Widget used to transfer GUI changes from thread into the main thread while processing dataset
        self.callback_process_signal = QtWidgets.QLineEdit()
        self.callback_process_signal.textChanged.connect(self.update_processing)

        ##Is true while the tensorflow training is running
        self.training_flag = threading.Event()
        
        
        ##Signals that computer vision class is still processing dataset
        self.process_flag = threading.Event()
        ##Signal used to tell the main thread to update dataset progress
        self.process_prog_flag = threading.Event()

        ##Signal used to tell the main thread to update training progress
        self.progress_flag = threading.Event()
        
        ##dictionary holding variables used in a callback while training
        self.train_vals = {'progress': 0,
                           'loss': 0,
                           'acc': 0,
                           'val_loss': 0,
                           'val_acc': 0,
                           'max_epoch': 0,
                           'epoch': 0}
                           
        ##Progress percentage of dataset loading/preprocessing
        self.process_perc = [0]

        ##Signals that prediction was completed and a new one can be made
        self.prediction_flag = threading.Event()

        self.add_widgets()
        self.connect_actions()
        self.set_texts()

    def add_widgets(self):
        self.setObjectName("tab_tensorflow")
        
        self.layout_main = QtWidgets.QGridLayout(self)
        self.layout_main.setObjectName("layout_main")
        
        self.btn_save_model = QtWidgets.QPushButton(self)
        self.btn_save_model.setObjectName("btn_save_model")
        
        self.layout_main.addWidget(self.btn_save_model, 0, 1, 1, 1)
        
        self.line_edit_model_name = QtWidgets.QLineEdit(self)
        self.line_edit_model_name.setObjectName("line_edit_model_name")
        self.line_edit_model_name.setEnabled(False)
        self.layout_main.addWidget(self.line_edit_model_name, 1, 0, 1, 2)
        
        self.btn_load_model = QtWidgets.QPushButton(self)
        self.btn_load_model.setObjectName("btn_load_model")
        
        self.layout_main.addWidget(self.btn_load_model, 0, 0, 1, 1)
        #----------------------------------------
        self.tensorflow_tabs = QtWidgets.QTabWidget(self)
        self.tensorflow_tabs.setObjectName("tensorflow_tabs")
        
        self.tab_classify = QtWidgets.QWidget()
        self.tab_classify.setObjectName("tab_classify")
        self.layout_classification = QtWidgets.QGridLayout(self.tab_classify)
        self.layout_classification.setObjectName("layout_classification")
        
        self.predictions = Prediction_graph()
        
        self.layout_classification.addWidget(self.predictions, 0, 0, 1, 1)
        
        self.tensorflow_tabs.addTab(self.tab_classify, "")
        #------------------------------------------------------
        self.tab_train = QtWidgets.QWidget()
        self.tab_train.setObjectName("tab_train")
        
        self.layout_training = QtWidgets.QGridLayout(self.tab_train)
        self.layout_training.setObjectName("layout_training")
        
        spacerItem1 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.layout_training.addItem(spacerItem1, 2, 0, 1, 1)
        
        self.frame_train_stats = QtWidgets.QFrame(self.tab_train)
        self.frame_train_stats.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_train_stats.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_train_stats.setObjectName("frame_train_stats")
        
        self.layout_train_progress = QtWidgets.QGridLayout(self.frame_train_stats)
        self.layout_train_progress.setObjectName("layout_train_progress")
        
        self.label_val_acc = QtWidgets.QLabel(self.frame_train_stats)
        self.label_val_acc.setObjectName("label_val_acc")
        self.layout_train_progress.addWidget(self.label_val_acc, 6, 3, 1, 1)
        
        self.line_edit_acc = QtWidgets.QLineEdit(self.frame_train_stats)
        self.line_edit_acc.setEnabled(False)
        self.line_edit_acc.setObjectName("line_edit_acc")
        self.layout_train_progress.addWidget(self.line_edit_acc, 6, 2, 1, 1)
        
        self.label_acc = QtWidgets.QLabel(self.frame_train_stats)
        self.label_acc.setObjectName("label_acc")
        self.layout_train_progress.addWidget(self.label_acc, 6, 0, 1, 1)
        
        self.label_val_loss = QtWidgets.QLabel(self.frame_train_stats)
        self.label_val_loss.setObjectName("label_val_loss")
        self.layout_train_progress.addWidget(self.label_val_loss, 2, 3, 1, 1)
        
        self.line_edit_val_acc = QtWidgets.QLineEdit(self.frame_train_stats)
        self.line_edit_val_acc.setEnabled(False)
        self.line_edit_val_acc.setObjectName("line_edit_val_acc")
        self.layout_train_progress.addWidget(self.line_edit_val_acc, 6, 4, 1, 1)
        
        self.line_edit_val_loss = QtWidgets.QLineEdit(self.frame_train_stats)
        self.line_edit_val_loss.setEnabled(False)
        self.line_edit_val_loss.setObjectName("line_edit_val_loss")
        self.layout_train_progress.addWidget(self.line_edit_val_loss, 2, 4, 1, 1)
        
        self.label_epoch = QtWidgets.QLabel(self.frame_train_stats)
        self.label_epoch.setObjectName("label_epoch")
        self.layout_train_progress.addWidget(self.label_epoch, 1, 0, 1, 1)
        
        self.label_active_epoch = QtWidgets.QLabel(self.frame_train_stats)
        self.label_active_epoch.setObjectName("label_active_epoch")
        self.layout_train_progress.addWidget(self.label_active_epoch, 1, 2, 1, 1)
        
        self.line_edit_loss = QtWidgets.QLineEdit(self.frame_train_stats)
        self.line_edit_loss.setEnabled(False)
        self.line_edit_loss.setObjectName("line_edit_loss")
        self.layout_train_progress.addWidget(self.line_edit_loss, 2, 2, 1, 1)
        
        self.label_loss = QtWidgets.QLabel(self.frame_train_stats)
        self.label_loss.setObjectName("label_loss")
        self.layout_train_progress.addWidget(self.label_loss, 2, 0, 1, 1)
        
        self.btn_train_cancel = QtWidgets.QPushButton(self.frame_train_stats)
        self.btn_train_cancel.setObjectName("btn_train_cancel")
        self.layout_train_progress.addWidget(self.btn_train_cancel, 0, 0, 1, 1)
        
        self.progress_bar_train = QtWidgets.QProgressBar(self.frame_train_stats)
        self.progress_bar_train.setProperty("value", 0)
        self.progress_bar_train.setObjectName("progress_bar_train")
        self.layout_train_progress.addWidget(self.progress_bar_train, 0, 2, 1, 3)
        
        self.layout_training.addWidget(self.frame_train_stats, 3, 0, 1, 1)
        
        self.frame_train_preprocess = QtWidgets.QFrame(self.tab_train)
        self.frame_train_preprocess.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_train_preprocess.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_train_preprocess.setObjectName("frame_train_preprocess")
        
        self.layout_dataset_settings = QtWidgets.QGridLayout(self.frame_train_preprocess)
        self.layout_dataset_settings.setObjectName("layout_dataset_settings")
        self.label_img_resize = QtWidgets.QLabel(self.frame_train_preprocess)
        self.label_img_resize.setObjectName("label_img_resize")
        self.layout_dataset_settings.addWidget(self.label_img_resize, 1, 0, 1, 1)
        
        self.btn_load_dataset = QtWidgets.QPushButton(self.frame_train_preprocess)
        self.btn_load_dataset.setObjectName("btn_load_dataset")
        self.layout_dataset_settings.addWidget(self.btn_load_dataset, 0, 0, 1, 1)
        
        self.label_val_split = QtWidgets.QLabel(self.frame_train_preprocess)
        self.label_val_split.setObjectName("label_val_split")
        self.layout_dataset_settings.addWidget(self.label_val_split, 4, 0, 1, 1)
        
        self.spin_box_val_split = QtWidgets.QDoubleSpinBox(self.frame_train_preprocess)
        self.spin_box_val_split.setMaximum(100.0)
        self.spin_box_val_split.setProperty("value", 20.0)
        self.spin_box_val_split.setObjectName("spin_box_val_split")
        self.layout_dataset_settings.addWidget(self.spin_box_val_split, 4, 1, 1, 1)
        
        self.spin_box_epochs = QtWidgets.QSpinBox(self.frame_train_preprocess)
        self.spin_box_epochs.setMaximum(1024)
        self.spin_box_epochs.setProperty("value", 5)
        self.spin_box_epochs.setObjectName("spin_box_epochs")
        self.layout_dataset_settings.addWidget(self.spin_box_epochs, 5, 1, 1, 1)
        
        self.label_train_epochs = QtWidgets.QLabel(self.frame_train_preprocess)
        self.label_train_epochs.setObjectName("label_train_epochs")
        self.layout_dataset_settings.addWidget(self.label_train_epochs, 5, 0, 1, 1)
        
        self.btn_preprocess = QtWidgets.QPushButton(self.frame_train_preprocess)
        self.btn_preprocess.setObjectName("btn_preprocess")
        self.layout_dataset_settings.addWidget(self.btn_preprocess, 6, 0, 1, 1)
        
        self.progress_bar_preprocess = QtWidgets.QProgressBar(self.frame_train_preprocess)
        self.progress_bar_preprocess.setProperty("value", 0)
        self.progress_bar_preprocess.setObjectName("progress_bar_preprocess")
        self.layout_dataset_settings.addWidget(self.progress_bar_preprocess, 6, 1, 1, 2)
        
        self.label_res_width = QtWidgets.QLabel(self.frame_train_preprocess)
        self.label_res_width.setObjectName("label_res_width")
        self.layout_dataset_settings.addWidget(self.label_res_width, 2, 0, 1, 1, QtCore.Qt.AlignRight)
        
        self.label_res_height = QtWidgets.QLabel(self.frame_train_preprocess)
        self.label_res_height.setObjectName("label_res_height")
        self.layout_dataset_settings.addWidget(self.label_res_height, 3, 0, 1, 1, QtCore.Qt.AlignRight)
        
        self.line_edit_res_width = QtWidgets.QLineEdit(self.frame_train_preprocess)
        self.line_edit_res_width.setEnabled(False)
        self.line_edit_res_width.setInputMethodHints(QtCore.Qt.ImhDigitsOnly)
        self.line_edit_res_width.setObjectName("line_edit_res_width")
        self.layout_dataset_settings.addWidget(self.line_edit_res_width, 2, 1, 1, 1)
        
        self.line_edit_res_height = QtWidgets.QLineEdit(self.frame_train_preprocess)
        self.line_edit_res_height.setEnabled(False)
        self.line_edit_res_height.setInputMethodHints(QtCore.Qt.ImhDigitsOnly)
        self.line_edit_res_height.setObjectName("line_edit_res_height")
        self.layout_dataset_settings.addWidget(self.line_edit_res_height, 3, 1, 1, 1)
        
        spacerItem2 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.layout_dataset_settings.addItem(spacerItem2, 2, 2, 1, 1)
        self.line_edit_dataset_path = QtWidgets.QLineEdit(self.frame_train_preprocess)
        self.line_edit_dataset_path.setObjectName("line_edit_dataset_path")
        self.layout_dataset_settings.addWidget(self.line_edit_dataset_path, 0, 1, 1, 2)
        
        self.layout_training.addWidget(self.frame_train_preprocess, 1, 0, 1, 1)
        self.tensorflow_tabs.addTab(self.tab_train, "")
        self.layout_main.addWidget(self.tensorflow_tabs, 2, 0, 1, 2)
        self.vision = Computer_vision(self.predictions)
        
    def connect_actions(self):
        self.btn_save_model.clicked.connect(self.save_model)
        self.btn_load_model.clicked.connect(self.load_model)
        self.btn_load_dataset.clicked.connect(self.choose_dataset)
        self.btn_preprocess.clicked.connect(self.preprocess_dataset)
        self.btn_train_cancel.clicked.connect(self.train_model)

    def set_texts(self):
        self.btn_save_model.setText("Save model")
        self.line_edit_model_name.setText("Select a model to load")
        self.btn_load_model.setText("Load model")
        self.tensorflow_tabs.setTabText(self.tensorflow_tabs.indexOf(self.tab_classify),"Classify")
        self.tensorflow_tabs.setTabText(self.tensorflow_tabs.indexOf(self.tab_classify), "Classify")
        self.label_val_acc.setText("Validation Accuracy")
        self.label_acc.setText("Accuracy")
        self.label_val_loss.setText("Validation Loss")
        self.label_epoch.setText("Epoch: ")
        self.label_active_epoch.setText("0/0")
        self.label_loss.setText("Loss")
        self.btn_train_cancel.setText("Train")
        self.label_img_resize.setText("Resize dimensions")
        self.btn_load_dataset.setText("Select Dataset")
        self.label_val_split.setText("Data for a validation [%]")
        self.label_train_epochs.setText("Train epochs")
        self.btn_preprocess.setText("Load Data")
        self.label_res_width.setText("Width")
        self.label_res_height.setText("Height")
        self.tensorflow_tabs.setTabText(self.tensorflow_tabs.indexOf(self.tab_train), "Train")

    def load_model(self):
        """!@brief When user wants to load a tensorflow model, this method will
        open a file dialog and makes sure the path provided actually contains
        a tensorflow model.
        """
        #Open file dialog for choosing a folder
        name = self.get_directory(self.line_edit_model_name)
        
        dim = self.vision.load_model(name)
        #Set label text to chosen folder path
        if(dim):
            self.line_edit_res_width.setText(str(dim[0]))
            self.line_edit_res_height.setText(str(dim[1]))
            self.send_status_msg.emit("Model loaded", 0)
            self.model_loaded = True
        else:
            self.send_status_msg.emit("Failed to load model", 0)
            self.line_edit_model_name.setText("Select a model to load")
    
    def save_model(self):
        """!@brief If tensorflow model is loaded, the file dialog is opened
        for user to choose save location.
        """
        #Open file dialog for choosing a folder
        if(not self.model_loaded):
            return
        
        name = QtWidgets.QFileDialog.getSaveFileName(self,
                                                    "Save Model",
                                                    filter="Keras model folder (*.model)",
                                                    )
        #Set label text to chosen folder path
        if(name[0]):
            saved = self.vision.save_model(name[0])
            if(saved):
                self.send_status_msg.emit("Model saved", 0)
            else:
                self.send_status_msg.emit("Failed to save model", 0)
    
    def choose_dataset(self):
        """!@brief Get dataset path and reenable preprocess button.
        """
        self.get_directory(self.line_edit_dataset_path)
        self.btn_preprocess.setEnabled(True)
        
    def preprocess_dataset(self):
        """!@brief Is called after user chooses dataset and clicks the load button.
        @details This method will proceed only if some path to the dataset has
        been provided. From the names of the folders the category names are derived.
        The data are then processed and modified to be suitable as inputs to
        the loaded neural network. Preprocessing runs in its own thread and 
        provides callback to the GUI.
        """
        if(self.line_edit_dataset_path.text() and self.model_loaded):
            try:
                self.btn_preprocess.setEnabled(False)
                path = self.line_edit_dataset_path.text()
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
                            'categories': categories,
                            'process_flag': self.process_flag,
                            'callback_flag': self.process_prog_flag})
                self.callback_preprocess_thread = threading.Thread(target=self.preprocess_callback)
                
                self.callback_preprocess_thread.start().daemon = True
                self.preprocess_thread.start().daemon = True

                self.callback_preprocess_thread.start()
                self.preprocess_thread.start()
            except:
                self.process_prog_flag.clear()
                self.process_flag.clear()
    
    def preprocess_callback(self):
        """!@brief Auxiliary method used to transfer thread state changes into
        the main thread.
        """
        while(not self.process_flag.is_set()):
            self.process_prog_flag.wait(2)
            if(not self.process_prog_flag.is_set()):
                continue
            self.process_prog_flag.clear()
            if(self.callback_process_signal.text() != "A"):
                self.callback_process_signal.setText("A")
            else:
                self.callback_process_signal.setText("B")
                
        self.send_status_msg.emit("Dataset preprocess completed", 0)
    
    def update_processing(self):
        """!@brief While the dataset is being processed this method shows the
        progress to the user. Method must run in the main thread
        """
        self.progress_bar_preprocess.setValue(int(self.process_perc[0]))
    
    def train_model(self):
        """!@brief When the train button is pressed, this methods makes sure the 
        training will start correctly.
        @details The method starts the training only if it is not already in 
        progress. The training is started in its own thread and all progress
        variables are passed into the training method. At the same time, another
        thread is created for controling the progress status updates and callbacks.
        """
        if(not self.training_flag.is_set()):
            self.training_flag.set()
            
            split = self.spin_box_val_split.value()/100
            
            self.train_thread = threading.Thread(target=self.vision.train, kwargs={
                'epochs': self.spin_box_epochs.value(),
                'train_vals': self.train_vals,
                'split': split,
                'progress_flag': self.progress_flag,
                'training_flag': self.training_flag})
            
            self.callback_train_thread = threading.Thread(target=self.training_callback)
            
            self.train_thread.daemon = True
            self.callback_train_thread.daemon = True

            self.callback_train_thread.start()
            self.train_thread.start()
        else:
            #stop training prematurely
            #self.training_flag.clear()
            pass
            
    def training_callback(self):
        """!@brief Auxiliary method used to transfer thread state changes into
        the main thread.
        """
        while(self.training_flag.is_set()):
            self.progress_flag.wait(2)
            if(not self.progress_flag.is_set()):
                continue
            self.progress_flag.clear()
            if(self.callback_train_signal.text() != "A"):
                self.callback_train_signal.setText("A")
            else:
                self.callback_train_signal.setText("B")
        self.send_status_msg.emit("Training ended", 0)
    
    def update_training(self):
        """!@brief Updates training progress in the GUI.
        @details Is called as a result of training_callback change. All variables
        are set up in other threads and this method reads them and update the 
        GUI in the main application thread.
        """
        
        self.progress_bar_train.setValue(self.train_vals['progress'])
        self.line_edit_loss.setText(str(self.train_vals['loss']))
        self.line_edit_acc.setText(str(self.train_vals['acc']))
        self.line_edit_val_loss.setText(str(self.train_vals['val_loss']))
        self.line_edit_val_acc.setText(str(self.train_vals['val_acc']))
        self.label_active_epoch.setText(str(self.train_vals['epoch']) + '/' + str(self.train_vals['max_epoch']))
    
    def predict(self,frame):
        """!@brief Starts a thread used to classify images from live camera feed
        @details This method should only be called when the last prediction
        ended. That means not every frame will be classified if the computer 
        can't keep up in the real time.
        @param[in] frame Picture to be classified. The format is OpenCV image.
        """
        #Tensorflow index is 3, if the gui changes, this may need to chage as well
        if(self.tensorflow_tabs.currentIndex() == 0):
            if(not self.prediction_flag.is_set() and self.model_loaded == True):
                self.prediction_flag.set()
                
                self.prediction_thread = threading.Thread(
                    target=self.vision.classify, kwargs={'frame': frame, 'prediction_flag': self.prediction_flag})

                self.prediction_thread.daemon = True
                self.prediction_thread.start()

    def get_directory(self, line_output = None):
        #set_record_path
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