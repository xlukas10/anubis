# -*- coding: utf-8 -*-
"""
Created on Mon Oct 19 09:08:58 2020

@author: Jakub Lukaszczyk
"""

from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.config import Config
from kivy.core.window import Window

#importing controls defined for controlling the camera.
#used in the .kv file
import camera_control_elements

#from harvesters import Harvester

#Determine if there is a config file present and read it.
#If the config file is not found a new one is made

######Config.read('PATH TO .INI FILE')
#set config
######Config.write()


#function to change tabs

#classes defining individual tabs for kivy

#function handeling file saving

#function for import of an .xml config file

#funcitoun for export of an .xml file

#opening camera
#   firewire
#   gige
#   usb

#drawing camera image

#play/pause

#magnifying glass

#Tensorflow

#kivy UI

#help - probably just open html help page

#app settings save/load

#maybe language settings


class MenuButton(Button):
    """
    Definition of appearenco of main menu buttons
    """
    def __init__(self, **kwargs):
        super(MenuButton, self).__init__(**kwargs)

class MainMenu(BoxLayout):
    """
    Defines main selections of categories
    """
    def __init__(self, **kwargs):
        super(MainMenu, self).__init__(**kwargs)

class MainLayout(FloatLayout):
    """
    Draws window in basic app layout
    """
    def __init__(self, **kwargs):
        super(MainLayout, self).__init__(**kwargs)

class CameraImage(Button):
    """
    Placeholder for widget which will draw image from camera
    """
    def __init__(self, **kwargs):
        super(CameraImage, self).__init__(**kwargs)

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

class AnubisApp(App):
    def build(self):
        return MainLayout()

Window.size = (800, 450)
Window.minimum_width, Window.minimum_height = Window.size

if __name__ == '__main__':
    AnubisApp().run()