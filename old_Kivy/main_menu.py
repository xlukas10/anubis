# -*- coding: utf-8 -*-
"""
Created on Sat Oct 24 09:11:35 2020

@author: Jakub Lukaszczyk
"""

from PyQt5 import QtGui, QtWidgets
from PyQt5.QtCore import pyqtSignal

import camera_control_elements
#import Tabs as tb

class MenuButton(QtWidgets.QPushButton):
    """
    Definition of appearence of main menu buttons
    """
    def __init__(self):
        super(MenuButton, self).__init__()

class MenuConnectCam(MenuButton):
    activate_tab_0 = pyqtSignal()
    def __init__(self):
        super(MenuConnectCam, self).__init__()
    def on_release(self):
        pass

class MenuCamParameters(MenuButton):
    #active_tab = StringProperty('')
    activate_tab_1 = pyqtSignal()
    def __init__(self):
        super(MenuCamParameters, self).__init__()

        
    #def on_release(self):
        #self.active_tab = 'CamParameters'
        #super(MenuCamParameters, self).on_touch_down(touch)
        
        
class MenuTensorflow(MenuButton):
    activate_tab_2 = pyqtSignal()
    def __init__(self):
        super(MenuOptions, self).__init__()


class MenuOptions(MenuButton):
    activate_tab_3 = pyqtSignal()
    def __init__(self):
        super(MenuOptions, self).__init__()
    
class MenuHelp(MenuButton):
    activate_tab_4 = pyqtSignal()
    def __init__(self):
        super(MenuHelp, self).__init__()

