from vimba import *
import atexit

v = Vimba.get_instance()
v._startup()

def close_vimba():
    global v
    v._shutdown()

atexit.register(close_vimba)
