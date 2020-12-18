# -*- coding: utf-8 -*-
"""
Created on Tue Nov  3 13:37:38 2020

@author: Jakub Lukaszczyk
"""


from PyQt5.QtWidgets import QHBoxLayout, QGridLayout, QLabel
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import pyqtSignal



import main_menu
import tabs as tb
import camera_control_elements
from global_queue import frame_queue

import time #TESTING

import cv2

class MainMenu(QHBoxLayout):
    """
    Defines main selections of categories
    """
    active_menu_signal = pyqtSignal()
    def __init__(self):

        super(MainMenu, self).__init__()

class MainLayout():
    """
    Draws window in basic app layout
    """

class CameraImage(QPixmap):
    """
    Placeholder for widget which will draw image from camera
    """
    def __init__(self):
        super(CameraImage, self).__init__()
        self.image_frame = QLabel()

    def draw(self, dt):
        # Frame is converted to texture, so it fits app window regardless of camera's resolution
        try:
            frame = frame_queue.get_nowait()
            #print(frame_queue.queue)
            image = QtGui.QImage(frame.data, frame.shape[1], frame.shape[0], QtGui.QImage.Format_RGB888).rgbSwapped()
            self.image_frame.setPixmap(QtGui.QPixmap.fromImage(self.image))
            self.show()
            
        except:
            print('kde nic tu nic')
            pass
        #self.ask_update()
        #self.reload()

class CameraSettings(QHBoxLayout):
    """
    Contains all modifiable parameters for opened camera
    """
    def __init__(self):
        super(CameraSettings, self).__init__()

class CameraControls(QGridLayout):
    """
    A set of controls used to manipulate with CameraImage window
    """
    def __init__(self):
        super(CameraControls, self).__init__()

class Tabs(QHBoxLayout):
    def __init__(self):
        super(Tabs, self).__init__()
        
        self.tab_connect_cam = tb.TabConnectCam() 
        self.tab_cam_parameters = tb.TabCamParameters()
        self.tab_tensorflow = tb.TabTensorflow() 
        self.tab_options = tb.TabOptions()
        self.tab_help = tb.TabHelp()
        
        self.tab_connect_cam.activate_tab_0.connect(self.show_menu(0))
        self.tab_connect_cam.activate_tab_1.connect(self.show_menu(1))
        self.tab_connect_cam.activate_tab_2.connect(self.show_menu(2))
        self.tab_connect_cam.activate_tab_3.connect(self.show_menu(3))
        self.tab_connect_cam.activate_tab_4.connect(self.show_menu(4))

    def show_menu(self, menu_index):
        self.clear_widgets()
        self.add_widget(self.menu[menu_index])
        
    def on_tab(self, instance, value):
        if value == 'ConnectCamera':
            self.show_menu(0)
        elif value == 'CamParameters':
            self.show_menu(1)
        elif value == 'Options':
            self.show_menu(2)
        elif value == 'Help':
            self.show_menu(3)