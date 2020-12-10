# -*- coding: utf-8 -*-
"""
Created on Wed Dec  9 21:17:17 2020

@author: Jakub Lukaszczyk
"""

from queue import Queue
from camera_communication import Camera

frame_queue = Queue()

cam = Camera('C:/Programy/Allied Vision/Vimba_4.0/VimbaGigETL/Bin/Win64/VimbaGigETL.cti')
#'C:/Programy/Allied Vision/Vimba_4.0/VimbaGigETL/Bin/Win64/VimbaGigETL.cti'
