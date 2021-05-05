# -*- coding: utf-8 -*-
"""
Created on Mon Oct 19 09:08:58 2020

@author: Jakub Lukaszczyk
"""

"""!@brief Main application file used to start and properly close the application
"""

from PyQt5 import QtWidgets
from interface import Ui_MainWindow

#Start the app. UI and its behavior is defined in interface.py
if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
