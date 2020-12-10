# -*- coding: utf-8 -*-
"""
Created on Wed Oct 28 11:21:29 2020

@author: Jakub Lukaszczyk
"""
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.properties import StringProperty
from kivy.app import App

from global_objects import cam

class TabLayout(GridLayout):
    def __init__(self,**kwargs):
        super(TabLayout, self).__init__(**kwargs)

class TabConnectCam(TabLayout):
    #detect_cameras = StringProperty([])
    def __init__(self,**kwargs):
        super(TabConnectCam, self).__init__(**kwargs)
        scroll_view = ScrollView()
        self.add_widget(scroll_view)
        
        
        #scroll view does not work
    def detect_cameras(self,):
        cameras = cam.get_camera_list()
        self.clear_widgets(children=self.children[:-1])
        if not cameras:
            self.add_widget(Label(text='No cameras found'))
        else:
            for camera in cameras:
                self.add_widget(CameraLabel(camera, text=camera.vendor + ' - ' + camera.model))
            print(cameras)
        


class TabCamParameters(TabLayout):
    def __init__(self,**kwargs):
        super(TabCamParameters, self).__init__(**kwargs)
        self.add_widget(Button(text='TabCamParameters'))

    
class TabOptions(TabLayout):
    def __init__(self,**kwargs):
        super(TabOptions, self).__init__(**kwargs)
        self.add_widget(Button(text='TabOptions'))
    
class TabHelp(TabLayout):
    def __init__(self,**kwargs):
        super(TabHelp, self).__init__(**kwargs)
        self.add_widget(Button(text='Pls Help me :o'))

class RefreshButton(Button):
    def __init__(self,**kwargs):
        super(RefreshButton, self).__init__(**kwargs)
        self.text = 'Refresh cameras'

class CameraLabel(Label):
    def __init__(self,camera_info, **kwargs):
        super(CameraLabel, self).__init__(**kwargs)
        self.camera_info = camera_info
        
    def on_touch_down(self, touch):
        if touch.is_double_tap:
            print('double')
            cam.select_camera(self.camera_info.id_)
            self.color = [1,0,0,1]