# -*- coding: utf-8 -*-
"""
Created on Wed Oct 28 11:21:29 2020

@author: Jakub Lukaszczyk
"""
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button


from kivymd.uix.list import MDList, TwoLineListItem
from kivymd.uix.list import OneLineIconListItem, IconLeftWidget
from kivy.uix.scrollview import ScrollView

from kivy.uix.floatlayout import FloatLayout



class TabLayout(FloatLayout):
    def __init__(self,**kwargs):
        super(TabLayout, self).__init__(**kwargs)


class TabConnectCam(TabLayout):
    def __init__(self, **kwargs):
        super(TabConnectCam, self).__init__(**kwargs)
        # Creating a Simple List
        self.scroll = ScrollView()

        self.list_view = MDList()
        for i in range(20):

            # items = ThreeLineListItem(text=str(i) + ' item',
            #                          secondary_text='This is ' + str(i) + 'th item',
            #                          tertiary_text='hello')

            icons = IconLeftWidget(icon="android")
            items = OneLineIconListItem(text=str(i) + ' item')
            items.add_widget(icons)
            self.list_view.add_widget(items)

        self.scroll.add_widget(self.list_view)
        # End List

        self.add_widget(self.scroll)
    

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

