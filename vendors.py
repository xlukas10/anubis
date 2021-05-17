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

"""!@brief In this file there are defined all implemented vendors or more precisely their
enum names.
"""
import enum

class Vendors(enum.IntEnum):
    Other = 0
    Allied_Vision_Technologies = 1