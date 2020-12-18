# -*- coding: utf-8 -*-
"""
Created on Mon Oct 19 09:08:58 2020

@author: Jakub Lukaszczyk
"""

import sys
from PyQt5 import QtGui, QtCore, QtWidgets
#importing controls defined for controlling the camera.
#used in the .kv file


from gui_elements import CameraImage
import threading
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

class Window(QtWidgets.QMainWindow):
    def __init__(self):
        super(Window,self).__init__()
        self.setGeometry(50, 50, 800,450)
        self.setWindowTitle('Anubis')
        self.layout()
        self.show()
        
    def layout(self):
        preview = CameraImage()
        self.show()



if __name__ == '__main__':
    anubis_app = QtWidgets.QApplication(sys.argv)
    gui = Window()
    sys.exit(anubis_app.exec_())
    
    