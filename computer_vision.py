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
        self.model = None
        self.SIZE = 50
        self.width = 1
        self.height =  1
        self.categories = []
        self.plot = plot
        self.split = 0
        
        self.x = []
        self.y = []
        
        self.training_data = []
        
    def load_model(self,path):
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
        self.model.save(path)
    
    def classify(self,frame,prediction_flag):
        #get current frame
        if self.model != None:
            input_dim = list(self.model.get_layer(index=0).input_shape)
            
            if(list(self.model.get_layer(index=-1).output_shape) != self.categories):
                self.categories = list(self.model.get_layer(index=-1).output_shape)
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
            
            self.plot.write_probability(out_data)
            #save output to variable and write it to the plot
            
            
            prediction_flag.clear()
    
    def process_dataset(self, path, process_perc , split=0, categories=[], process_flag = None, callback_flag = None):
        if(path != None and self.model != None):
            self.split = split
            
            
            del self.x
            del self.y
            
            self.x = []
            self.y = []
            
            print('aaa')
            if(self._create_training_data(path,categories, callback_flag,  process_perc)):
            
                for features,label in self.training_data:
                    self.x.append(features)
                    self.y.append(label)
                
                self.x = np.array(self.x).reshape(-1, self.width, self.height, 1)
                self.y = np.array(self.y)
                
                process_flag.set()
                return True
            else:
                process_flag.set()
                return False
        
    
    def _create_training_data(self, path, categories, callback_flag, process_perc):
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

        
    def train(self,  train_vals, progress_flag, training_flag):
        
        callback = Gui_callback(train_vals,progress_flag)
       
        self.model.fit(self.x,self.y,batch_size=32,validation_split=self.split,epochs=5, callbacks=[callback])
        training_flag.clear()
        
        
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

#done
    def on_train_begin(self, logs=None):
        # When this logger is called inside `fit`, validation is silent.
        self._called_in_fit = True

#done


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
