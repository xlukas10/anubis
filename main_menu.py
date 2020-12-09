# -*- coding: utf-8 -*-
"""
Created on Sat Oct 24 09:11:35 2020

@author: Jakub Lukaszczyk
"""

from kivy.uix.button import Button
from kivymd.app import MDApp
from kivy.properties import StringProperty

import camera_control_elements


#import Tabs as tb

class MenuButton(Button):
    """
    Definition of appearence of main menu buttons
    """
    def __init__(self, **kwargs):
        super(MenuButton, self).__init__(**kwargs)

class MenuConnectCam(MenuButton):
    def __init__(self,**kwargs):
        super(MenuConnectCam, self).__init__(**kwargs)
    def on_release(self):
        pass

class MenuCamParameters(MenuButton):
    #active_tab = StringProperty('')
    def __init__(self,**kwargs):
        super(MenuCamParameters, self).__init__(**kwargs)

        
    #def on_release(self):
        #self.active_tab = 'CamParameters'
        #super(MenuCamParameters, self).on_touch_down(touch)
    
class MenuOptions(MenuButton):
    def __init__(self,**kwargs):
        super(MenuOptions, self).__init__(**kwargs)
    
class MenuHelp(MenuButton):
    def __init__(self,**kwargs):
        super(MenuHelp, self).__init__(**kwargs)

