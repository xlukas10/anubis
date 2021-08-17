#    Anubis is a program to control industrial cameras and train and use artificial neural networks
#    Copyright (C) 2021 Lukaszczyk Jakub
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.

#Will be neccessary?

from queue import Queue

frame_queue = {"0": Queue()}
active_frame_queue = {"0": Queue()}

def add_frame_queue(cam_id):
    frame_queue[str(cam_id)] = Queue()
    active_frame_queue[str(cam_id)] = Queue()

def remove_frame_queue(cam_id):
    del frame_queue[str(cam_id)]
    del active_frame_queue[str(cam_id)]