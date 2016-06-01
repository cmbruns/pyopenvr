#/bin/env python

'''
Created on May 31, 2016

@author: cmbruns
'''

from ctypes import byref

from OpenGL.GL import *
from OpenGL.GLUT import *

import openvr


class PinkWorld(object):
    "Demo GL application that simply colors the whole universe pink"
    
    def __init__(self):
        # Glut
        glutInit()
        glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE)
        glutInitWindowSize(400, 400)
        glutInitWindowPosition(50, 50)
        win = glutCreateWindow("Pink world")
        glutDisplayFunc(self.display)
        glutIdleFunc(self.display)
        glutReshapeFunc(self.resize_gl)
        glutKeyboardFunc(self.key_press)
        # OpenVR
        self.vr_system = openvr.init(openvr.VRApplication_Scene)
        self.compositor = openvr.VRCompositor()
        if self.compositor is None:
            raise Exception("Unable to create compositor") 
        poses_t = openvr.TrackedDevicePose_t * openvr.k_unMaxTrackedDeviceCount
        self.poses = poses_t()
        #
        self.frame_count = 0
   
    def __enter__(self):
        return self
    
    def __exit__(self, type_arg, value, traceback):
        if self.vr_system is not None:
            openvr.shutdown
            self.vr_system = None
    
    def display(self):
        self.compositor.waitGetPoses(byref(self.poses[0]), openvr.k_unMaxTrackedDeviceCount, None, 0)
        hmd_pose0 = self.poses[openvr.k_unTrackedDeviceIndex_Hmd]
        if not hmd_pose0.bPoseIsValid:
            return
        hmd_pose = hmd_pose0.mDeviceToAbsoluteTracking
        self.frame_count += 1
        print("pose %d" % self.frame_count)
        # TODO
        glClearColor(1, 0.8, 0.8, 0) # Pink background
        glClear(GL_COLOR_BUFFER_BIT)
        glutSwapBuffers()
        glBindFramebuffer(GL_FRAMEBUFFER, 0)
        
    def key_press(self, key, x, y):
        if ord(key) == 27:
            # print "Escape!"
            if bool(glutLeaveMainLoop):
                glutLeaveMainLoop()
            else:
                raise Exception("Application quit")
            
    def resize_gl(self, width, height):
        glViewport(0, 0, width, height)
            

if __name__ == "__main__":
    with PinkWorld() as pink_world:
        glutMainLoop()

