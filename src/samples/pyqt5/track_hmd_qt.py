#!/usr/bin/env python2
# Qt-based top-down visualization of OpenVR tracking 
# data for both HMD and controllers. Includes tables of tracking
# values as well.
#
# Dependencies:
# - PyQt4
# - jinja2
# - (pyopenvr)
#
# Paul Melis (paul.melis@surfsara.nl)
# SURFsara Visualization group
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout
from PyQt5.QtCore import QTimer, pyqtSlot, QCoreApplication
from PyQt5.QtWebEngineWidgets import QWebEngineView
from jinja2 import Environment, FileSystemLoader
import openvr

jinja_env = Environment(
        loader=FileSystemLoader('.'),
        auto_reload=True
        )
        
def format_velocity(v):
    s = '%+.1f' % v
    if abs(v) <= 0.05:
        return '<span style="color: black">%s</span>' % s
    elif v >= 0:
        return '<span style="color: green">%s</span>' % s
    else:
        return '<span style="color: red">%s</span>' % s
        
def format_tracking_result(e):
    if e == openvr.TrackingResult_Uninitialized:
        return 'Unitialized'
    elif e == openvr.TrackingResult_Calibrating_InProgress:
        return 'Calibrating (in progress)'
    elif e == openvr.TrackingResult_Calibrating_OutOfRange:
        return 'Calibrating (out of range)'
    elif e == openvr.TrackingResult_Running_OK:
        return 'Running OK'
    elif e == openvr.TrackingResult_Running_OutOfRange:
        return 'Running (out of range)'
    else:
        return 'Unknown (%d)!' % e
        
jinja_env.filters['format_velocity'] = format_velocity
jinja_env.filters['format_tracking_result'] = format_tracking_result

class MainWindow(QWidget):

    def __init__(self):
        QWidget.__init__(self)
        
        self.resize(1600, 940)
        self.setWindowTitle('OpenVR tracking data')
        
        self.webview = QWebEngineView()

        self.button = QPushButton('Quit', self)
        self.button.clicked.connect(self.close)
        layout = QVBoxLayout(self)
        layout.setSpacing(0)
        # layout.setMargin(0)
        layout.addWidget(self.button)
        layout.addWidget(self.webview)
        
        # XXX check result
        openvr.init(openvr.VRApplication_Scene)        
        poses_t = openvr.TrackedDevicePose_t * openvr.k_unMaxTrackedDeviceCount
        self.poses = poses_t()
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_page)
        self.timer.start(200)   # ms
                    
    def update_page(self):
        try:
            openvr.VRCompositor().waitGetPoses(self.poses, None)
        except:
            return

        vrsys = openvr.VRSystem()
        
        poses = {}
        hmd_index = openvr.k_unTrackedDeviceIndex_Hmd
        beacon_indices = []
        controller_indices = []
        
        for i in range(len(self.poses)):       
            
            device_class = vrsys.getTrackedDeviceClass(i)
            if device_class == openvr.TrackedDeviceClass_Invalid:
                continue               
            elif device_class == openvr.TrackedDeviceClass_Controller:
                controller_indices.append(i)
            elif device_class == openvr.TrackedDeviceClass_TrackingReference:
                beacon_indices.append(i)
                
            model_name = vrsys.getStringTrackedDeviceProperty(i, openvr.Prop_RenderModelName_String)            
            pose = self.poses[i]            
            
            poses[i] = dict(
                model_name=model_name,
                device_is_connected=pose.bDeviceIsConnected,
                valid=pose.bPoseIsValid,
                tracking_result=pose.eTrackingResult,
                d2a=pose.mDeviceToAbsoluteTracking,
                velocity=pose.vVelocity,                   # m/s
                angular_velocity=pose.vAngularVelocity     # radians/s?
            )
                    
        template = jinja_env.get_template('status.html')
        html = template.render(poses=poses, hmd_index=hmd_index, controller_indices=controller_indices, beacon_indices=beacon_indices)
                
        self.webview.setHtml(html)
        self.update()

    def closeEvent(self, event):
        self.timer.stop()
        openvr.shutdown()
        super().closeEvent(event)

if __name__ == '__main__':    
    
    app = QApplication(sys.argv)
    window = MainWindow()    
    window.show()
    app.exec_()
    