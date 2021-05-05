# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 11:53:06 2021

@author: Jakub Lukaszczyk
"""


import enum

class Config_level(enum.IntEnum):
    """!@brief This class defines configuration levels that are defined by the GenICam standard
    """
    Unknown = 0
    Beginner = 1
    Expert = 2
    Guru = 3
    Invisible = 4