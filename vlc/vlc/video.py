# Copyright (C) 2020 Daniël van Adrichem <daniel5gh@spiet.nl>
#https://gist.github.com/daniel5gh/36f6a802451c02d3434f9aab730c1828
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston MA 02110-1301, USA.

import logging                                                                                                                                                                                                
import time                                                                                                                                                                                                   
import ctypes                                                                                                                                                                                                 
from threading import Lock                                                                                                                                                                                    
                                                                                                                                                                                                              
import numpy as np                                                                                                                                                                                            
from OpenGL.GL import (                                                                                                                                                                                       
    GL_TEXTURE_2D, glTexSubImage2D, glTexImage2D,                                                                                                                                                             
    GL_BGRA, GL_RGBA, GL_BGR, GL_RGB,                                                                                                                                                                         
    GL_UNSIGNED_BYTE)                                                                                                                                                                                         
import vlc                                                                                                                                                                                                    

# patched ctypes func definitions because ones provided in vlc.py are incorrect
# NOTE: this is no longer needed if you use a recent version (>=3.0.8112)
_CorrectVideoLockCb = ctypes.CFUNCTYPE(ctypes.c_void_p, ctypes.c_void_p, ctypes.POINTER(ctypes.c_void_p))                                                                                                     
_CorrectVideoUnlockCb = ctypes.CFUNCTYPE(                                                                                                                                                                     
    ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p, ctypes.POINTER(ctypes.c_void_p))                                                                                                                       
                                                                                                                                                                                                              
                                                                                                                                                                                                              
class Surface(object):                                                                                                                                                                                        
    """A lockable image buffer                                                                                                                                                                                
    """                                                                                                                                                                                                       
    def __init__(self, w, h):                                                                                                                                                                                 
        self._width = w                                                                                                                                                                                       
        self._height = h                                                                                                                                                                                      
                                                                                                                                                                                                              
        # size in bytes when RV32 *4 or RV24 * 3                                                                                                                                                              
        self._row_size = self._width * 3                                                                                                                                                                      
        self._buf_size = self._height * self._row_size                                                                                                                                                        
        # allocate buffer                                                                                                                                                                                     
        self._buf1 = np.zeros(self._buf_size, dtype=np.ubyte)                                                                                                                                                 
        # get pointer to buffer                                                                                                                                                                               
        self._buf_p = self._buf1.ctypes.data_as(ctypes.c_void_p)                                                                                                                                              
        self._lock = Lock()                                                                                                                                                                                   
        #_log.debug(self.buf_pointer)                                                                                                                                                                          
        #_log.debug(self.buf)                                                                                                                                                                                  

    def update_gl(self):                                                                                                                                                                                      
        # with self._lock:                                                                                                                                                                                    
        glTexSubImage2D(GL_TEXTURE_2D,                                                                                                                                                                        
                        0, 0, 0,                                                                                                                                                                              
                        self._width,
                        self._height,
                        GL_BGR,                                                                                                                                                                               
                        GL_UNSIGNED_BYTE,                                                                                                                                                                     
                        self._buf1)                                                                                                                                                                           
                                                                                                                                                                                                              
    def create_texture_gl(self):                                                                                                                                                                              
        glTexImage2D(GL_TEXTURE_2D,                                                                                                                                                                           
                     0,                                                                                                                                                                                       
                     GL_RGB,                                                                                                                                                                                  
                     self._width,  # width                                                                                                                                                                    
                     self._height,  # height                                                                                                                                                                  
                     0,                                                                                                                                                                                       
                     GL_BGR,                                                                                                                                                                                  
                     GL_UNSIGNED_BYTE,                                                                                                                                                                        
                     None)                                                                                                                                                                                    
                                                                                                                                                                                                              
    @property                                                                                                                                                                                                 
    def width(self):                                                                                                                                                                                          
        return self._width                                                                                                                                                                                    
                                                                                                                                                                                                              
    @property                                                                                                                                                                                                 
    def height(self):                                                                                                                                                                                         
        return self._height                                                                                                                                                                                   
                                                                                                                                                                                                              
    @property                                                                                                                                                                                                 
    def row_size(self):                                                                                                                                                                                       
        return self._row_size                                                                                                                                                                                 
                                                                                                                                                                                                              
    @property                                                                                                                                                                                                 
    def buf(self):                                                                                                                                                                                            
        return self._buf1                                                                                                                                                                                     
                                                                                                                                                                                                              
    @property                                                                                                                                                                                                 
    def buf_pointer(self):                                                                                                                                                                                    
        return self._buf_p                                                                                                                                                                                    
                                                                                                                                                                                                              
    def lock(self):                                                                                                                                                                                           
        self._lock.acquire()                                                                                                                                                                                  
                                                                                                                                                                                                              
    def unlock(self):                                                                                                                                                                                         
        self._lock.release()                                                                                                                                                                                  

    def __enter__(self, *args):                                                                                                                                                                               
        return self._lock.__enter__(*args)                                                                                                                                                                    
                                                                                                                                                                                                              
    def __exit__(self, *args):                                                                                                                                                                                
        return self._lock.__exit__(*args)                                                                                                                                                                     
                                                                                                                                                                                                              
    def get_libvlc_lock_callback(self):                                                                                                                                                                       
        @_CorrectVideoLockCb                                                                                                                                                                                  
        def _cb(opaque, planes):                                                                                                                                                                              
            self._lock.acquire()                                                                                                                                                                              
            planes[0] = self._buf_p                                                                                                                                                                           
                                                                                                                                                                                                              
        return _cb                                                                                                                                                                                            
                                                                                                                                                                                                              
    def get_libvlc_unlock_callback(self):                                                                                                                                                                     
        @_CorrectVideoUnlockCb                                                                                                                                                                                
        def _cb(opaque, picta, planes):                                                                                                                                                                       
            self._lock.release()                                                                                                                                                                              
                                                                                                                                                                                                              
        return _cb                                                                                                                                                                                            

class main(object):                                                                                                                                                                                        
    """A lockable image buffer                                                                                                                                                                                
    """                                                                                                                                                                                                       
    def __init__(self):  
        # I use this surface with something like:

        self.player = vlc.MediaPlayer("rtsp://admin:123456@10.43.3.200:554/ch01/0")
        # play and stop so video_get_size gets a correct value                                                                                                                                                
        # setting all callbacks to None prevents a window being created on play                                                                                                                               
        self.player.video_set_callbacks(None, None, None, None)  
        # play and stop so video_get_size gets a correct value
        self.player.play()                                                                                                                                                                                    
        time.sleep(1)                                                                                                                                                                                         
        self.player.stop()   
        w, h = self.player.video_get_size()
        self.surface = Surface(w, h)
        # need to keep a reference to the CFUNCTYPEs or else it will get GCed                                                                                                                                 
        self._lock_cb = self.surface.get_libvlc_lock_callback()                                                                                                                                               
        self._unlock_cb = self.surface.get_libvlc_unlock_callback()                                                                                                                                           
        self.player.video_set_callbacks(self._lock_cb, self._unlock_cb, None, None)                                                                                                                           
        self.player.video_set_format(                                                                                                                                                                         
                    "RV24",                                                                                                                                                                                           
                    self.surface.width,                                                                                                                                                                               
                    self.surface.height,                                                                                                                                                                              
                    self.surface.row_size)                                                                                                                                                                            
        # this starts populating the surface's buf with pixels, from another thread
        self.player.play()
        # in main thread, where gl context is current:
        self.v.surface.update_gl()


a = main()