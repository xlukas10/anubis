# -*- coding: utf-8 -*-
"""
Created on Tue Nov  3 13:37:38 2020

@author: Jakub Lukaszczyk
"""

from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.config import Config
from kivy.uix.image import Image

from kivy.uix.tabbedpanel import TabbedPanel
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import StringProperty
from kivy.graphics.texture import Texture #drawing image from camera

import main_menu
import tabs as tb
import camera_control_elements

import cv2

class MainMenu(BoxLayout):
    """
    Defines main selections of categories
    """
    active_tab = StringProperty()
    def __init__(self, **kwargs):

        super(MainMenu, self).__init__(**kwargs)

class MainLayout(FloatLayout):
    """
    Draws window in basic app layout
    """
    def __init__(self, **kwargs):
        super(MainLayout, self).__init__(**kwargs)

class CameraImage(Image):
    """
    Placeholder for widget which will draw image from camera
    """
    def __init__(self, **kwargs):
        super(CameraImage, self).__init__(**kwargs)

    def draw(self, frame):
        # Frame is converted to texture, so it fits app window regardless of camera's resolution
        frame_1D = frame.tostring() # converts frame to a format expected by blit_buffer method
        print(frame)
        frame_texture = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='rgb')
        frame_texture.blit_buffer(frame_1D, colorfmt='rgb', bufferfmt='ubyte')
        # display image from the texture
        self.texture = frame_texture

class CameraSettings(BoxLayout):
    """
    Contains all modifiable parameters for opened camera
    """
    def __init__(self, **kwargs):
        super(CameraSettings, self).__init__(**kwargs)

class CameraControls(GridLayout):
    """
    A set of controls used to manipulate with CameraImage window
    """
    def __init__(self, **kwargs):
        super(CameraControls, self).__init__(**kwargs)

class Tabs(BoxLayout):
    tab = StringProperty('')
    def __init__(self, **kwargs):
        super(Tabs, self).__init__(**kwargs)
        
        self.menu = (tb.TabConnectCam(), 
                     tb.TabCamParameters(), 
                     tb.TabOptions(), 
                     tb.TabHelp())
        self.show_menu(0)

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