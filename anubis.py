# -*- coding: utf-8 -*-
"""
Created on Mon Oct 19 09:08:58 2020

@author: Jakub Lukaszczyk
"""

from kivymd.app import MDApp
from kivy.core.window import Window
#importing controls defined for controlling the camera.
#used in the .kv file



import kivy_elements
import threading

import global_objects
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


#set maximum size defined by user (So the app does not eat all of the ram)

class AnubisApp(MDApp):        
    def build(self):
        #global_objects.cam.get_camera_list()
        #global_objects.cam.select_camera(0)
        return kivy_elements.MainLayout()

Window.size = (800, 450)
Window.minimum_width, Window.minimum_height = Window.size

if __name__ == '__main__':
    AnubisApp().run()
    
    