from PyQt5 import QtCore, QtGui, QtWidgets 
import global_camera
from PyQt5.QtCore import pyqtSignal as Signal
import threading
import win32api
import time
import numpy as np


from global_queue import active_frame_queue

class Camera_control_gui(QtWidgets.QWidget):
    #signals
    send_status_msg = Signal(str, int)
    connection_update = Signal(bool, int, str)#connected, state - 0=disconnected 1=standby 2=busy, camera name
    recording_update = Signal(bool)
    preview_update = Signal(bool)
    request_prediction = Signal(np.ndarray)
    received_info = Signal(int)
    fps_info = Signal(float)

    def __init__(self):
        super(Camera_control_gui, self).__init__()

        ##Widget used to transfer GUI changes from thread into the main thread while updating preview
        self.resize_signal = QtWidgets.QLineEdit()
        self.resize_signal.textChanged.connect(self.update_img)

        self.save_location = ""
        self.save_filename = ""
        self.sequence_duration = ""

        ##Holds current frame displayed in the GUI
        self.image_pixmap = None
        ##Width of the preview area
        self.w_preview = 0
        ##Height of the preview area
        self.h_preview = 0

        ##Signals that a recording was stopped, either by timer or manually
        self.interrupt_flag = threading.Event()

        ##Current frames per second received from the camera
        self.fps = 0.0
        ##Total sum of received frames for active camera session
        self.received = 0

        ##Last value of the dragging in the preview area - x axis
        self.move_x_prev = 0
        ##Last value of the dragging in the preview area - y axis
        self.move_y_prev = 0

        ##Value of current preview zoom in %/100
        self.preview_zoom = 1
        ##Resizing image to preview area size instead of using zoom
        self.preview_fit = True

        self.connected = False
        self.preview_live = False
        self.recording = False

        self.add_widgets()
        self.connect_actions()
        self.set_texts()

    def add_widgets(self):
        self.setObjectName("preview_and_control")
        
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self)
        self.verticalLayout_2.setObjectName("verticalLayout_2")

        self.preview_area = QtWidgets.QScrollArea(self)
        #disables scrollbars in preview window
        #self.preview_area.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        #self.preview_area.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.preview_area.installEventFilter(self)
        
        self.camera_preview = QtWidgets.QLabel(self.preview_area)
        self.camera_preview.setAutoFillBackground(False)
        self.camera_preview.setText("")
        self.camera_preview.setSizePolicy(QtWidgets.QSizePolicy.Ignored, QtWidgets.QSizePolicy.Ignored)
        self.camera_preview.setPixmap(QtGui.QPixmap("default_preview.png"))
        self.camera_preview.setScaledContents(False)
        self.camera_preview.setIndent(-1)
        self.camera_preview.setObjectName("camera_preview")
        self.preview_area.setWidget(self.camera_preview)
        self.verticalLayout_2.addWidget(self.preview_area)
        
        #Definition of buttons to control camera (bottom right)
        #-------------------------------------------------------------------
        self.widget_controls = QtWidgets.QWidget(self)
        self.widget_controls.setObjectName("widget_controls")
        
        self.gridLayout_4 = QtWidgets.QGridLayout(self.widget_controls)
        self.gridLayout_4.setObjectName("gridLayout_4")
        
        self.btn_zoom_in = QtWidgets.QPushButton(self.widget_controls)
        self.btn_zoom_in.setObjectName("btn_zoom_in")
        self.gridLayout_4.addWidget(self.btn_zoom_in, 0, 2, 1, 1)
        
        self.btn_zoom_out = QtWidgets.QPushButton(self.widget_controls)
        self.btn_zoom_out.setObjectName("btn_zoom_out")
        self.gridLayout_4.addWidget(self.btn_zoom_out, 0, 3, 1, 1)
        
        self.btn_zoom_100 = QtWidgets.QPushButton(self.widget_controls)
        self.btn_zoom_100.setObjectName("btn_zoom_100")
        self.gridLayout_4.addWidget(self.btn_zoom_100, 1, 3, 1, 1)
        
        self.btn_zoom_fit = QtWidgets.QPushButton(self.widget_controls)
        self.btn_zoom_fit.setObjectName("btn_zoom_fit")
        self.gridLayout_4.addWidget(self.btn_zoom_fit, 1, 2, 1, 1)
        
        self.btn_single_frame = QtWidgets.QPushButton(self.widget_controls)
        self.btn_single_frame.setObjectName("btn_single_frame")
        self.gridLayout_4.addWidget(self.btn_single_frame, 1, 0, 1, 1)
        
        self.btn_start_preview = QtWidgets.QPushButton(self.widget_controls)
        self.btn_start_preview.setObjectName("btn_start_preview")
        
        self.gridLayout_4.addWidget(self.btn_start_preview, 0, 0, 1, 1)
        
        self.btn_start_recording = QtWidgets.QPushButton(self.widget_controls)
        self.btn_start_recording.setObjectName("btn_start_recording")
        
        self.gridLayout_4.addWidget(self.btn_start_recording, 0, 1, 1, 1)
        
        self.verticalLayout_2.addWidget(self.widget_controls)
       
        
    def connect_actions(self):
        self.btn_zoom_out.clicked.connect(lambda: self.set_zoom(-1))
        self.btn_zoom_fit.clicked.connect(lambda: self.set_zoom(0))
        self.btn_zoom_in.clicked.connect(lambda: self.set_zoom(1))
        self.btn_zoom_100.clicked.connect(lambda: self.set_zoom(100))
        self.btn_single_frame.clicked.connect(self.single_frame)
        self.btn_start_preview.clicked.connect(self.preview)
        self.btn_start_recording.clicked.connect(self.record)

    def set_texts(self):
        self.btn_zoom_100.setText("Zoom to 100%")
        self.btn_zoom_fit.setText("Fit to window")
        self.btn_start_recording.setText("Start/Stop recording")
        self.btn_start_preview.setText("Start/Stop preview")
        self.btn_single_frame.setText("Single frame")
        self.btn_zoom_in.setText("Zoom In")
        self.btn_zoom_out.setText("Zoom Out")

    def eventFilter(self, obj, event):
        """!@brief Implements dragging inside preview area
        @details whin user cliks and drags inside of a preview area, this 
        method is called and do the scrolling based on the distance dragged in
        each direction.
        """
        if (obj == self.preview_area):
            if(event.type() == QtCore.QEvent.MouseMove ):
    
                if self.move_x_prev == 0:
                    self.move_x_prev = event.pos().x()
                if self.move_y_prev == 0:
                    self.move_y_prev = event.pos().y()
    
                dist_x = self.move_x_prev - event.pos().x()
                dist_y = self.move_y_prev - event.pos().y()
                self.preview_area.verticalScrollBar().setValue(
                    self.preview_area.verticalScrollBar().value() + dist_y)
                self.preview_area.horizontalScrollBar().setValue(
                    self.preview_area.horizontalScrollBar().value() + dist_x)
                #self.preview_area.scrollContentsBy(dist_x,dist_y)
                self.move_x_prev = event.pos().x()
                self.move_y_prev = event.pos().y()

            elif event.type() == QtCore.QEvent.MouseButtonRelease:
                self.last_time_move = 0
        return QtWidgets.QWidget.eventFilter(self, obj, event)

    def record(self):
        """!@brief Starts and stops recording
        @details Is called by start/stop button. Recording is always started 
        manually. Recording ends with another button click or after time set 
        in self.line_edit_sequence_duration passes. Save location and name is 
        determined by the text in self.line_edit_save_location and 
        self.line_edit_sequence_name.
        """
        if self.connected:
            if(not self.recording):
                #Change status icon and print status message
                self.connection_update.emit(True, 2, "-1")
                self.send_status_msg.emit("Starting recording", 0)
                
                
                self.recording_update.emit(True)
                self.recording = True
                
                #Start new recording with defined name and save path
                global_camera.cams.active_devices[global_camera.active_cam].start_recording(self.save_location,
                                    self.save_filename,
                                    'nothing')
                
                
                #If automatic sequence duration is set, create thread that will
                #automatically terminate the recording
                if(self.sequence_duration > 0):
                    self.interrupt_flag.clear()
                    self.seq_duration_thread = threading.Thread(target=self.seq_duration_wait)
                    self.seq_duration_thread.daemon = True
                    self.seq_duration_thread.start()
                
                #Start live preview in a new thread
                self.show_preview_thread = threading.Thread(target=self.show_preview)
                self.show_preview_thread.daemon = True
                self.show_preview_thread.start()
                self.send_status_msg.emit("Recording",0)
            else:
                #Set status message and standby icon
                self.connection_update.emit(True, 1, "-1")
                self.send_status_msg.emit("Stopping recording", 0)
                
                #Tell automatic sequence duration thread to end
                self.interrupt_flag.set()
                
                #End recording
                global_camera.cams.active_devices[global_camera.active_cam].stop_recording()
                self.recording_update.emit(False)
                self.recording = False
                self.preview_live = False
                self.preview_update.emit(False)
                self.send_status_msg.emit("Recording stopped", 3500)
    
    def seq_duration_wait(self):
        """!@brief Automatic recording interrupt.
        @details Let camera record for defined time and if the recording is not
        manually terminated stop the recording.
        """
        #wait for the first frame to be received
        while active_frame_queue.empty():
            time.sleep(0.001)
        
        #print status message
        self.send_status_msg.emit("Recording for "+self.line_edit_sequence_duration.text()+"s started", 0)
        
        #wait either for manual recording stop or wait for defined time
        self.interrupt_flag.wait(float(self.line_edit_sequence_duration.text()))
        
        #If the recording is still running (not terminated manually), stop 
        #the recording.
        if(self.recording):
            self.record()
    
    def preview(self):
        """!@brief Starts live preview
        @details Unlike recording method, this method does not save frames to a
        drive. Preview picture is rendered in separate thread.
        """
        #continue only if camera is connected
        if self.connected:
            if(not self.preview_live):
                #Set status message and icon
                self.connection_update.emit(True, 2, "-1")
                self.send_status_msg.emit("Starting preview",1500)
                
                
                self.preview_update.emit(True)
                self.preview_live = True
                
                #Start camera frame acquisition (not recording)
                global_camera.cams.active_devices[global_camera.active_cam].start_acquisition()
                
                
                #Create and run thread to draw frames to gui
                self.show_preview_thread = threading.Thread(target=self.show_preview)
                self.show_preview_thread.daemon = True
                self.show_preview_thread.start()
            else:
                #Reset status icon and print message
                self.connection_update.emit(True, 1, "-1")
                self.send_status_msg.emit("Stopping preview",1500)
                
                #Stop receiving frames
                global_camera.cams.active_devices[global_camera.active_cam].stop_acquisition()
                
                self.preview_live = False
                self.preview_update.emit(False)
                
    
    def set_zoom(self, flag):
        """!@brief Set the zoom amount of the image previewed
        @details This method only sets the zooming variable, actual resizing
        is done in other methods.
        @param[in] flag Is used to define type of zoom. 
        1  - zoom in
        -1 - zoom out
        0  - zoom fit
        100- zoom reset
        """
        #flag 1 zoom in, -1 zoom out, 0 zoom fit, 100 zoom reset
        if(flag == -1 and self.preview_zoom > 0.1):
            self.preview_fit = False
            self.preview_zoom -= 0.1
        elif(flag == 1):
            self.preview_fit = False
            self.preview_zoom += 0.1
        elif(flag == 0):
            self.preview_fit = True
        elif(flag == 100):
            self.preview_fit = False
            self.preview_zoom = 1
    
    def single_frame(self):
        """!@brief Acquire and draw a single frame.
        @details Unlike the live preview, this method runs in the main thread 
        and therefore can modify frontend variables. The method may block whole
        application but its execution should be fast enough to not make a 
        difference.
        """
        #Method runs only if camera is connected
        if self.connected and not(self.preview_live or self.recording):
            #Set status icon and message
            self.send_status_msg.emit("Receiving single frame",1500)
            self.connection_update.emit(True, 2, "-1")
            
            #Get image
            image, pixel_format = global_camera.cams.active_devices[global_camera.active_cam].get_single_frame()
            
            #Try to run prediction
            self.request_prediction.emit(image)
            
            #Set up a new value of received frames in the statusbar
            self.received = self.received + 1
            self.received_info.emit(self.received)

            #Convert image to proper format fo PyQt
            h, w, ch = image.shape
            bytes_per_line = ch * w
            image = QtGui.QImage(image.data, w, h, bytes_per_line, self._get_QImage_format(pixel_format))

            
            #get size of preview window
            w_preview = self.preview_area.size().width()
            h_preview = self.preview_area.size().height()
            
            image_scaled = image.scaled(w_preview, 
                                        h_preview, 
                                        QtCore.Qt.KeepAspectRatio)
            
            #Set image to gui
            self.camera_preview.resize(w_preview,
                                       h_preview)
            self.camera_preview.setPixmap(QtGui.QPixmap.fromImage(image_scaled))
            self.camera_preview.show()
            
            #Reset status icon
            self.connection_update.emit(True, 1, "-1")
    
    def show_preview(self):
        """!@brief Draws image from camera in real time.
        @details Acquires images from camera and draws them in real time at 
        the same rate as is display refresh_rate. If the frames come too fast,
        only one at the most recent one is drawn and the rest is dumped. During 
        this method an attempt to classify the image is called using predict method.
        """
        #Determine refresh rate of used display. This way the method will not
        #run too slowly or redundantly fast.
        device = win32api.EnumDisplayDevices()
        refresh_rate = win32api.EnumDisplaySettings(device.DeviceName, -1).DisplayFrequency
        
        #Auxiliary variables for fps calculation
        frames = 0
        cycles = 0
        
        color_format = QtGui.QImage.Format_Invalid
        str_color = None
        time_fps = time.monotonic_ns()
        #runs as long as the camera is recording or preview is active
        while self.recording or self.preview_live:
            cycles = cycles + 1
            
            #Draw only if thre is at least 1 frame to draw
            if not active_frame_queue.qsize() == 0:
                image = active_frame_queue.get_nowait()
                self.received = self.received + 1
                
                frames += 1
                
                #Dump all remaining frames (If frames are received faster than 
                #refresh_rate).
                while not active_frame_queue.qsize() == 0:
                    frames += 1
                    self.received = self.received + 1
                    active_frame_queue.get_nowait()
                
                #Try to run a prediction
                self.request_prediction.emit(image[0])
                """if(self.tabs.currentIndex() == 3):
                    self.tab_tensorflow.predict(image[0])"""
                
                #Set up a new value of received frames in the statusbar
                self.received_info.emit(self.received)
                
#Change to time dependency instead of cycle#More cycles -> more exact fps calculation (value is more stable in gui)
                
                if cycles > 30:
                    time_now = time.monotonic_ns()
                    time_passed = time_now - time_fps
                    time_fps = time_now
                    #[frames*Hz/c] -> [frames/s]
                    self.fps = round(frames/(time_passed/1_000_000_000),1)
                    self.fps_info.emit(self.fps)
                    
                    cycles = 0
                    frames = 0
                
                #Convert image to proper format for PyQt
                h, w, ch = image[0].shape
                bytes_per_line = ch * w
                
                
                if(str_color != image[1]):
                    str_color = image[1]
                    color_format = self._get_QImage_format(str_color)
                    
                if(color_format == QtGui.QImage.Format_Invalid):
                    self.send_status_msg.emit("Used image format is not supported", 0)
                
                
                image = QtGui.QImage(image[0].data, w, h, bytes_per_line, color_format)
#TODO Get color format dynamically
                
                #get size of preview window if zoom fit is selected
                if(self.preview_fit == True):
                    self.w_preview = self.preview_area.size().width()
                    self.h_preview = self.preview_area.size().height()
                    image_scaled = image.scaled(self.w_preview, 
                                                self.h_preview, 
                                                QtCore.Qt.KeepAspectRatio)
                else:#else use zoom percentage
                    self.w_preview = w*self.preview_zoom
                    self.h_preview = w*self.preview_zoom
                    image_scaled = image.scaled(self.w_preview,
                                         self.w_preview,
                                         QtCore.Qt.KeepAspectRatio)
                
                self.image_pixmap = QtGui.QPixmap.fromImage(image_scaled)
                self.preview_callback()
                #Set image to gui
            #Wait for next display frame
            time.sleep(1/refresh_rate)
        
        #When recording stops, change fps to 0
        self.fps = 0.0
        self.fps_info.emit(self.fps)
    
    def preview_callback(self):
        """!@brief Auxiliary method used to transfer thread state change into
        the main thread.
        """
        if(self.resize_signal.text() != "A"):
            self.resize_signal.setText("A")
        else:
            self.resize_signal.setText("B")
    
    def update_img(self):
        """!@brief update image in the live preview window.
        @details This method must run in the main thread as it modifies frontend
        data of the gui.
        """
        #Resize preview label if preview window size changed
        if(self.w_preview != self.camera_preview.size().width() or
                   self.h_preview != self.camera_preview.size().height()):
            self.camera_preview.resize(self.w_preview,
                                       self.h_preview)
        
        #set a new image to the preview area
        self.camera_preview.setPixmap(self.image_pixmap)
        self.camera_preview.show()
    
    def _get_QImage_format(self, format_string):
        """!@brief The image format provided by camera object (according to 
        GenICam standard) is transoformed to one of the color formats supported
        by PyQt.
        @param[in] format_string text containing color format defined by GenICam
        or another standard.
        """
        image_format = None
        
        if(format_string == 'Format_Mono'):
            image_format = QtGui.QImage.Format_Mono
        elif(format_string == 'Format_MonoLSB'):
            image_format = QtGui.QImage.Format_MonoLSB
        elif(format_string == 'Format_Indexed8'):
            image_format = QtGui.QImage.Format_Indexed8
        elif(format_string == 'Format_RGB32'):
            image_format = QtGui.QImage.Format_RGB32
        elif(format_string == 'Format_ARGB32'):
            image_format = QtGui.QImage.Format_ARGB32
        elif(format_string == 'Format_ARGB32_Premultiplied'):
            image_format = QtGui.QImage.Format_ARGB32_Premultiplied
        elif(format_string == 'Format_RGB16'):
            image_format = QtGui.QImage.Format_RGB16
        elif(format_string == 'Format_ARGB8565_Premultiplied'):
            image_format = QtGui.QImage.Format_ARGB8565_Premultiplied
        elif(format_string == 'Format_RGB666'):
            image_format = QtGui.QImage.Format_RGB666
        elif(format_string == 'Format_ARGB6666_Premultiplied'):
            image_format = QtGui.QImage.Format_ARGB6666_Premultiplied
        elif(format_string == 'Format_RGB555'):
            image_format = QtGui.QImage.Format_RGB555
        elif(format_string == 'Format_ARGB8555_Premultiplied'):
            image_format = QtGui.QImage.Format_ARGB8555_Premultiplied
        elif(format_string == 'Format_RGB888' or format_string == 'RGB8'):
            image_format = QtGui.QImage.Format_RGB888
        elif(format_string == 'Format_RGB444'):
            image_format = QtGui.QImage.Format_RGB444
        elif(format_string == 'Format_ARGB4444_Premultiplied'):
            image_format = QtGui.QImage.Format_ARGB4444_Premultiplied
        elif(format_string == 'Format_RGBX8888'):
            image_format = QtGui.QImage.Format_RGBX8888
        elif(format_string == 'Format_RGBA8888' or format_string == 'RGBa8'):
            image_format = QtGui.QImage.Format_RGBA8888
        elif(format_string == 'Format_RGBA8888_Premultiplied'):
            image_format = QtGui.QImage.Format_RGBA8888_Premultiplied
        elif(format_string == 'Format_BGR30'):
            image_format = QtGui.QImage.Format_BGR30
        elif(format_string == 'Format_A2BGR30_Premultiplied'):
            image_format = QtGui.QImage.Format_A2BGR30_Premultiplied
        elif(format_string == 'Format_RGB30'):
            image_format = QtGui.QImage.Format_RGB30
        elif(format_string == 'Format_A2RGB30_Premultiplied'):
            image_format = QtGui.QImage.Format_A2RGB30_Premultiplied
        elif(format_string == 'Format_Alpha8'):
            image_format = QtGui.QImage.Format_Alpha8
        elif(format_string == 'Format_Grayscale8' or format_string == 'Mono8'):
            image_format = QtGui.QImage.Format_Grayscale8
        elif(format_string == 'Format_Grayscale16' or format_string == 'Mono16'):
            image_format = QtGui.QImage.Format_Grayscale16
        elif(format_string == 'Format_RGBX64'):
            image_format = QtGui.QImage.Format_RGBX64
        elif(format_string == 'Format_RGBA64'):
            image_format = QtGui.QImage.Format_RGBA64
        elif(format_string == 'Format_RGBA64_Premultiplied'):
            image_format = QtGui.QImage.Format_RGBA64_Premultiplied
        elif(format_string == 'Format_BGR888' or format_string == 'BGR8'):
            image_format = QtGui.QImage.Format_BGR888
        else:
            image_format = QtGui.QImage.Format_Invalid
        
        return image_format
        
        '''
        SFNC OPTIONS not yet implemented
        Mono1p
        Mono2p, Mono4p, Mono8s, Mono10, Mono10p, Mono12, Mono12p, Mono14, 
        , R8, G8, B8, , RGB8_Planar, , RGB10, RGB10_Planar, 
        RGB10p32, RGB12, RGB12_Planar, RGB16, RGB16_Planar, RGB565p, BGR10, 
        BGR12, BGR16, BGR565p, , BGRa8, YUV422_8, YCbCr411_8, YCbCr422_8, 
        YCbCr601_422_8, YCbCr709_422_8, YCbCr8, BayerBG8, BayerGB8, BayerGR8, 
        BayerRG8, BayerBG10, BayerGB10, BayerGR10, BayerRG10, BayerBG12, 
        BayerGB12, BayerGR12, BayerRG12, BayerBG16, BayerGB16, BayerGR16, 
        BayerRG16, Coord3D_A8, Coord3D_B8, Coord3D_C8, Coord3D_ABC8, 
        Coord3D_ABC8_Planar, Coord3D_A16, Coord3D_B16, Coord3D_C16, 
        Coord3D_ABC16, Coord3D_ABC16_Planar, Coord3D_A32f, Coord3D_B32f, 
        Coord3D_C32f, Coord3D_ABC32f, Coord3D_ABC32f_Planar, Confidence1, 
        Confidence1p, Confidence8, Confidence16, Confidence32f, Raw8, Raw16, 
        Device-specific
        - GigE Vision Specific:
        Mono12Packed, BayerGR10Packed, BayerRG10Packed, BayerGB10Packed, 
        BayerBG10Packed, BayerGR12Packed, BayerRG12Packed, BayerGB12Packed, 
        BayerBG12Packed, RGB10V1Packed, RGB12V1Packed, 
        - Deprecated:
            will not be implemented for now as they are not used in genicam anymore
        '''
        '''
        SFNC OPTIONS - all
        Mono1p
        Mono2p, Mono4p, Mono8, Mono8s, Mono10, Mono10p, Mono12, Mono12p, Mono14, 
        Mono16, R8, G8, B8, RGB8, RGB8_Planar, RGBa8, RGB10, RGB10_Planar, 
        RGB10p32, RGB12, RGB12_Planar, RGB16, RGB16_Planar, RGB565p, BGR10, 
        BGR12, BGR16, BGR565p, BGR8, BGRa8, YUV422_8, YCbCr411_8, YCbCr422_8, 
        YCbCr601_422_8, YCbCr709_422_8, YCbCr8, BayerBG8, BayerGB8, BayerGR8, 
        BayerRG8, BayerBG10, BayerGB10, BayerGR10, BayerRG10, BayerBG12, 
        BayerGB12, BayerGR12, BayerRG12, BayerBG16, BayerGB16, BayerGR16, 
        BayerRG16, Coord3D_A8, Coord3D_B8, Coord3D_C8, Coord3D_ABC8, 
        Coord3D_ABC8_Planar, Coord3D_A16, Coord3D_B16, Coord3D_C16, 
        Coord3D_ABC16, Coord3D_ABC16_Planar, Coord3D_A32f, Coord3D_B32f, 
        Coord3D_C32f, Coord3D_ABC32f, Coord3D_ABC32f_Planar, Confidence1, 
        Confidence1p, Confidence8, Confidence16, Confidence32f, Raw8, Raw16, 
        Device-specific
        - GigE Vision Specific:
        Mono12Packed, BayerGR10Packed, BayerRG10Packed, BayerGB10Packed, 
        BayerBG10Packed, BayerGR12Packed, BayerRG12Packed, BayerGB12Packed, 
        BayerBG12Packed, RGB10V1Packed, RGB12V1Packed, 
        - Deprecated:
        Mono8Signed (Deprecated, use Mono8s)
        RGB8Packed (Deprecated, use RGB8) ,BGR8Packed (Deprecated, use BGR8), 
        RGBA8Packed (Deprecated, use RGBa8), BGRA8Packed (Deprecated, use BGRa8), 
        RGB10Packed (Deprecated, use RGB10), BGR10Packed (Deprecated, use BGR10), 
        RGB12Packed (Deprecated, use RGB12), BGR12Packed (Deprecated, use BGR12), 
        RGB16Packed (Deprecated, use RGB16), BGR16Packed (Deprecated, use BGR16), 
        RGB10V2Packed (Deprecated, use RGB10p32), BGR10V2Packed (Deprecated, use BGR10p32), 
        RGB565Packed (Deprecated, use RGB565p), BGR565Packed (Deprecated, use BGR565p), 
        YUV411Packed (Deprecated, use YUV411_8_UYYVYY), YUV422Packed (Deprecated, use YUV422_8_UYVY), 
        YUV444Packed (Deprecated, use YUV8_UYV), YUYVPacked (Deprecated, use YUV422_8), 
        RGB8Planar (Deprecated, use RGB8_Planar), RGB10Planar (Deprecated, use RGB10_Planar),
        RGB12Planar (Deprecated, use RGB12_Planar), RGB16Planar (Deprecated, use RGB16_Planar), 
        '''
   
    def update_recording_config(self, name, location, duration):
        """!@brief This method is used to tell the instance of this class current recording configuration
        @param[in] name Template for naming saved files
        @param[in] location Where should the images be saved
        @param[in] duration Length of a recording sequence
        """

        self.save_location = location
        self.save_filename = name
        self.sequence_duration = duration
    