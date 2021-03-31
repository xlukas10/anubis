# -*- coding: utf-8 -*-
"""
Created on Mon Oct 19 09:08:58 2020

@author: Jakub Lukaszczyk
"""


from PyQt5 import QtWidgets
import threading
from interface import Ui_MainWindow


#Start the app. UI is defined in interface.py
if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())


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
