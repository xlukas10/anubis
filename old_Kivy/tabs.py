# -*- coding: utf-8 -*-
"""
Created on Wed Oct 28 11:21:29 2020

@author: Jakub Lukaszczyk
"""
from PyQt5 import QtGui, QtWidgets 
from PyQt5.QtWidgets import QLabel, QGridLayout

from global_camera import cam

class TabLayout(QGridLayout):
    def __init__(self):
        super(TabLayout, self).__init__()

class TabConnectCam(TabLayout):
    #detect_cameras = StringProperty([])
    def __init__(self):
        super(TabConnectCam, self).__init__()
        #scroll_view = ScrollView()
        #self.add_widget(scroll_view)
        
        
        
        #scroll view does not work
    def detect_cameras(self):
        cameras = cam.get_camera_list()
        self.clear_widgets(children=self.children[:-1])
        if not cameras:
            label = QLabel('No cameras found')
        else:
            for camera in cameras:
                label = CameraLabel(camera, text=camera.vendor + ' - ' + camera.model)
            print(cameras)
        


class TabCamParameters(TabLayout):
    def __init__(self):
        super(TabCamParameters, self).__init__()
        self.btn = QWidgets.QPushButton('TabCamParameters',self)
        self.btn.clicked.connect(self.tmp)
        
    def tmp(self):
        pass

    
class TabOptions(TabLayout):
    def __init__(self,**kwargs):
        super(TabOptions, self).__init__(**kwargs)
        self.btn = QWidgets.QPushButtonton('TabOptions',self)
        self.btn.clicked.connect(self.tmp)
        
    def tmp(self):
        pass
    
class TabHelp(TabLayout):
    def __init__(self,**kwargs):
        super(TabHelp, self).__init__(**kwargs)
        self.btn = QWidgets.QPushButton('Pls Help me :o',self)
        self.btn.clicked.connect(self.tmp)
        
    def tmp(self):
        pass

class RefreshButton(QtWidgets.QPushButton):
    def __init__(self,**kwargs):
        super(RefreshButton, self).__init__(**kwargs)
        self.text = 'Refresh cameras'

class CameraLabel(QLabel):
    def __init__(self,camera_info, **kwargs):
        super(CameraLabel, self).__init__(**kwargs)
        self.camera_info = camera_info
        
    def on_touch_down(self, touch):
        if touch.is_double_tap:
            print('double')
            cam.select_camera(self.camera_info.id_)
            self.color = [1,0,0,1]