# -*- coding: utf-8 -*-
"""
Created on Sat Feb 27 09:00:50 2021

@author: Jakub Lukaszczyk
"""

from tensorflow import keras
from tensorflow.python.keras.utils import tf_utils
import numpy as np
import cv2
import os
import random
import threading
import time

class Computer_vision():
    def __init__(self,plot):
        """!@brief Initialize object and its variables
        @param[in] plot The class needs to have a reference to the GUI object the
        classification results will be shown in.
        """
        self.model = None
        self.width = 1
        self.height =  1
        self.categories = []
        self.plot = plot
        self.split = 0
        self.busy = False
        
        self.x = []
        self.y = []
        
        self.training_data = []
        
    def load_model(self,path):
        """!@brief Load Keras model.
        @details Model is loaded from the path and variables defining input
        dimensions of the model are set.
        @param[in] path Path to the folder with saved model.
        @return True if loading is successful else False.
        """
        if(self.model):
            keras.backend.clear_session()
            self.model = None
        
        
        try:
            self.model = keras.models.load_model(path)
            input_dim = list(self.model.get_layer(index=0).input_shape)
            self.width = input_dim[1]
            self.height = input_dim[2]
            
            return [self.width, self.height]
        except:
            self.model = None
            return False
    
    def save_model(self,path):
        """!@brief Save model to defined path
        @param[in] path Path to the folder where model will be saved.
        @return True if loading is successful else False.
        """
        if(self.model):
            self.model.save(path)
            return True
        else:
            return False
    
    def train(self, epochs, train_vals, split, progress_flag, training_flag):
        """!@brief Start training loaded model
        @details If the object is not busy, the tensorflow/Keras training will
            start. During training the callback object will push current values of 
            training variavles int the references passed in train_vals.
        @param[in] epochs How many times should the dataset be introduced to
            the network.
        @param[in] train_vals Reference to variables used in callback to inform
            calling functions about training progress
        @param[in] split Fraction of dataset to be used as validation data (float).
        @param[in] progress_flag Signal to tell that it is time to update
            progress values
        @param[in] training_flag Used to announce finished training
        """
        if(self.model != None and not self.busy):
            self.busy = True
            if(split):
                self.split = split
            else:
                self.split = 0
            callback = Gui_callback(train_vals,progress_flag)
           
            self.model.fit(self.x,
                           self.y,
                           batch_size=32,
                           validation_split=self.split,epochs=epochs,
                           callbacks=[callback])
            self.busy = False
            training_flag.clear()
             
    def classify(self,frame,prediction_flag):
        """!@brief Classify image using trained model
        @details This method does not change the behavior of the network but
            only uses it to make prediction about what is in the picture. The
            result is shown in the plot passed by reference in the __init__ method.
        @param[in] frame OpenCV image that the prediction will be done for.
        @param[in] predition_flag Announces that the prediction was completed
        """
        
        #get current frame
        if self.model != None:
            input_dim = list(self.model.get_layer(index=0).input_shape)
            
            if(self.model.get_layer(index=-1).output_shape[1] != len(self.categories)):
                #Add reading categories
                for ctg in range(0,self.model.get_layer(index=-1).output_shape[1]):
                    self.categories.append(f'ctg {ctg}')
                self.plot.add_categories(self.categories)
                
            
            if(input_dim[0] == None):
                input_dim[0] = -1
            
            frame_data = cv2.resize(frame,(input_dim[1],input_dim[2]))
            #maybe change dimensions according to model
            frame_data = np.array(frame_data)
            frame_data = frame_data.reshape(input_dim)
            #transform it to numpy array
            
            #run .predict
            out_data = self.model.predict([frame_data])
            self.plot.write_probability(out_data[0].tolist())
            #save output to variable and write it to the plot
            
            
            prediction_flag.clear()
    
    def process_dataset(self, path, process_perc , categories=[], process_flag = None, callback_flag = None):
        """!@brief Prepare dataset to be used as input and desired output.
        @details The method will proceed only if a model is loaded and path is valid.
        dimensions of the model are set.
        @param[in] path Path to the dataset
        @param[in] process_perc Reference to the progress variable in the 
            calling function. Value should be read during callbacks
        @param[in] categories Names of the individual folders containing data
            for different categories.
        @param[in] process_flag When processing finishes the flag is raised.
        @param[in] callback_flag Threading event telling the calling function
            to update progress based on the valu in process_perc
        @return True if loading is successful else False.
        """
        
        if(path != None and self.model != None and not self.busy):
            self.busy = True
            del self.x
            del self.y
            
            self.x = []
            self.y = []
            
            if(self._create_training_data(path,categories, callback_flag,  process_perc)):
            
                for features,label in self.training_data:
                    self.x.append(features)
                    self.y.append(label)
                
                self.x = np.array(self.x).reshape(-1, self.width, self.height, 1)
                self.y = np.array(self.y)
    
                self.busy = False
                process_flag.set()
                return True
            else:
                self.busy = False
                process_flag.set()
                return False
        
    def _create_training_data(self, path, categories, callback_flag, process_perc):
        """!@brief Auxiliary method to resize all input data to the size of input
        of the loaded model.
        dimensions of the model are set.
        @param[in] path Path to the dataset
        @param[in] categories Names of the individual folders containing data
            for different categories.
        @param[in] callback_flag Threading event telling the calling function
            to update progress based on the valu in process_perc
        @param[in] process_perc Reference to the progress variable in the 
            calling function. Value should be read during callbacks
        @return True if loading is successful else False.
        """
        
        self.training_data.clear()
        items = 0
        process_perc[0] = 0
        callback_flag.set()
        
        try:
            for category in categories:
                path_cat = os.path.join(path, category)
                items += len(os.listdir(path_cat))
        except:
            return False
            
        percent = int(items/100)
        items_done = 0

        for category in categories:
            path_cat = os.path.join(path, category)
            class_num = categories.index(category)
            for img in os.listdir(path_cat):
                try:
                    img_array = cv2.imread(os.path.join(path_cat,img),cv2.IMREAD_GRAYSCALE)
                    new_array = cv2.resize(img_array, (self.width, self.height))
                    self.training_data.append([new_array,class_num])
                    items_done += 1
                    if(items_done % percent == 0):
                        process_perc[0] = items_done/percent
                        callback_flag.set()
                except Exception as e:
                    pass
        process_perc[0] = 100
        callback_flag.set()
        random.shuffle(self.training_data)
        
        return True

        
class Gui_callback(keras.callbacks.Callback):
    def __init__(self, train_vals, progress_flag, count_mode='samples', stateful_metrics=None):
        super(Gui_callback, self).__init__()
        
        self.train_vals = train_vals
        self.progress_flag = progress_flag
        
        self._supports_tf_logs = True
        if count_mode == 'samples':
          self.use_steps = False
        elif count_mode == 'steps':
          self.use_steps = True
        else:
          raise ValueError('Unknown `count_mode`: ' + str(count_mode))
        # Defaults to all Model's metrics except for loss.
        self.stateful_metrics = set(stateful_metrics) if stateful_metrics else None
    
        self.seen = 0
        self.active_epoch = 0
        self.progbar = None
        self.target = None
        self.verbose = 1
        self.epochs = 1
    
        self._called_in_fit = False

    def set_params(self, params):
        self.verbose = params['verbose']
        self.epochs = params['epochs']
        self.target = params['steps']


    def on_train_begin(self, logs=None):
        # When this logger is called inside `fit`, validation is silent.
        self._called_in_fit = True




#Pass in label for epochs
    def on_epoch_begin(self, epoch, logs=None):
        self.active_epoch = epoch

    def on_train_batch_end(self, batch, logs=None):
        self._update_progbar(batch, logs)

    def on_test_batch_end(self, batch, logs=None):
        if not self._called_in_fit:
            self._update_progbar(batch, logs)

    def on_predict_batch_end(self, batch, logs=None):
    # Don't pass prediction results.
        self._update_progbar(batch, None)

    def on_epoch_end(self, epoch, logs=None):
        self._update_progbar(logs=logs)

    def on_test_end(self, logs=None):
        if not self._called_in_fit:
            self._update_progbar(logs=logs)

    def on_predict_end(self, logs=None):
        self._update_progbar(logs=logs)

#CHNG
    def _reset_progbar(self):
        self.train_vals['progress'] = 0
        self.progress_flag.set()
        self.seen = 0

    def _maybe_init_progbar(self):
        if self.stateful_metrics is None:
            if self.model:
                self.stateful_metrics = (set(m.name for m in self.model.metrics))
        else:
            self.stateful_metrics = set()
        

    def _update_progbar(self, batch=None, logs=None):
        """Updates the progbar."""
        logs = logs or {}
        self._maybe_init_progbar()
        self.seen += 1
        logs = tf_utils.to_numpy_or_python_type(logs)
        
        # Only block async when verbose = 1.
        if(self.target == None):
            self.target = 0
        
        percentage = int( (self.seen)/((self.target*self.epochs)/100))
        try:
            self.train_vals['loss'] = format(float(logs['loss']),'.3f')
        except:
            pass
        try:
            self.train_vals['val_loss'] = format(float(logs['val_loss']),'.3f')
        except:
            pass
        try:
            self.train_vals['acc'] = format(float(logs['accuracy']),'.3f')
        except:
            pass
        try:
            self.train_vals['val_acc'] = format(float(logs['val_accuracy']),'.3f')
        except:
            pass
        self.train_vals['progress'] = percentage
        self.train_vals['max_epoch'] = self.epochs
        self.train_vals['epoch'] = self.active_epoch + 1
        self.progress_flag.set()
