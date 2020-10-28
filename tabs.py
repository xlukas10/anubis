# -*- coding: utf-8 -*-
"""
Created on Wed Oct 28 11:21:29 2020

@author: Jakub Lukaszczyk
"""
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button

class TabLayout(GridLayout):
    def __init__(self,**kwargs):
        super(TabLayout, self).__init__(**kwargs)

class TabConnectCam(TabLayout):
    def __init__(self,**kwargs):
        super(TabConnectCam, self).__init__(**kwargs)
        self.add_widget(Button(text='TabConnectCam'))


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

