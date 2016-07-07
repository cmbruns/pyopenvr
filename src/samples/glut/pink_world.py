#/bin/env python

'''
Simple "Pink World" example for pyopenvr python bindings for OpenVR virtual reality SDK.
Colors the whole world pink, demonstrating OpenGL rendering, without any of
the spatial algebra needed to actually draw scene items.

This is more interesting than you might think, if you have the
HTC Vive set up for room-scale with chaperone bounds. The bounds give
you something to look at, at least.

Created on May 31, 2016

@author: Christopher Bruns
'''


# This demo uses OpenGL and GLUT for rendering
from OpenGL.GL import * # @UnusedWildImport # this comment squelches IDE warnings
from OpenGL.GLUT import * # @UnusedWildImport

# OpenVR is the virtual reality API we are demonstrating here today
import openvr


class PinkWorld(object):
    "Demo GL application that simply colors the whole universe pink"
    
    def __init__(self):
        "One time initialization"
        # Glut
        glutInit()
        glutInitDisplayMode(GLUT_RGBA)
        # Create a regular desktop window, just so we can have an OpenGL context to play with
        glutInitWindowSize(400, 400)
        glutInitWindowPosition(50, 50)
        self.win = glutCreateWindow(b"Pink world")
        # Set up callback methods for use during the GLUT main loop
        glutDisplayFunc(self.display)
        glutIdleFunc(self.display)
        glutReshapeFunc(self.resize_gl)
        glutKeyboardFunc(self.key_press)
        # OpenVR
        self.vr_system = openvr.init(openvr.VRApplication_Scene)
        self.vr_width, self.vr_height = self.vr_system.getRecommendedRenderTargetSize()
        self.compositor = openvr.VRCompositor()
        if self.compositor is None:
            raise Exception("Unable to create compositor") 
        poses_t = openvr.TrackedDevicePose_t * openvr.k_unMaxTrackedDeviceCount
        self.poses = poses_t()
        #
        # Set up framebuffer and render textures
        self.fb = glGenFramebuffers(1)
        glBindFramebuffer(GL_FRAMEBUFFER, self.fb)
        self.depth_buffer = glGenRenderbuffers(1)
        glBindRenderbuffer(GL_RENDERBUFFER, self.depth_buffer)
        glRenderbufferStorage(GL_RENDERBUFFER, GL_DEPTH24_STENCIL8, self.vr_width, self.vr_height)
        glFramebufferRenderbuffer(GL_FRAMEBUFFER, GL_DEPTH_STENCIL_ATTACHMENT, GL_RENDERBUFFER, self.depth_buffer)
        self.texture_id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.texture_id)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA8, self.vr_width, self.vr_height, 0, GL_RGBA, GL_UNSIGNED_BYTE, None)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAX_LEVEL, 0)  
        glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, self.texture_id, 0)
        status = glCheckFramebufferStatus(GL_FRAMEBUFFER)
        if status != GL_FRAMEBUFFER_COMPLETE:
            glBindFramebuffer(GL_FRAMEBUFFER, 0)
            raise Exception("Incomplete framebuffer")
        glBindFramebuffer(GL_FRAMEBUFFER, 0)
        # OpenVR texture data
        self.texture = openvr.Texture_t()
        self.texture.handle = self.texture_id
        self.texture.eType = openvr.API_OpenGL
        self.texture.eColorSpace = openvr.ColorSpace_Gamma 
   
    def __enter__(self):
        "For lexically scoped cleanup, using the 'with' keyword"
        return self
    
    def __exit__(self, type_arg, value, traceback):
        "For lexically scoped cleanup, using the 'with' keyword"
        if self.vr_system is not None:
            openvr.shutdown
            self.vr_system = None
        glDeleteTextures([self.texture_id])
        glDeleteRenderbuffers([self.depth_buffer])
        glDeleteFramebuffers([self.fb])
        self.fb = 0
    
    def display(self):
        "Renders the scene once every refresh"
        self.compositor.waitGetPoses(self.poses, openvr.k_unMaxTrackedDeviceCount, None, 0)
        hmd_pose0 = self.poses[openvr.k_unTrackedDeviceIndex_Hmd]
        if not hmd_pose0.bPoseIsValid:
            return
        # hmd_pose = hmd_pose0.mDeviceToAbsoluteTracking
        # 1) On-screen render:
        if True:
            glClearColor(0.8, 0.4, 0.4, 0) # Pink background
            glClear(GL_COLOR_BUFFER_BIT)
            # glutSwapBuffers()
            glFlush() # Single buffer
        # 2) VR render
        # TODO: render different things to each eye
        glBindFramebuffer(GL_FRAMEBUFFER, self.fb)
        glClearColor(0.8, 0.4, 0.4, 0) # Pink background
        glClear(GL_COLOR_BUFFER_BIT)
        glBindFramebuffer(GL_FRAMEBUFFER, 0)
        #
        # TODO: use different textures for each eye
        self.compositor.submit(openvr.Eye_Left, self.texture)
        self.compositor.submit(openvr.Eye_Right, self.texture)
        glBindFramebuffer(GL_FRAMEBUFFER, 0)
        
    def key_press(self, key, x, y):
        "Close the application when the player presses ESCAPE"
        if ord(key) == 27:
            # print "Escape!"
            if bool(glutLeaveMainLoop):
                glutLeaveMainLoop()
            else:
                raise Exception("Application quit")
            
    def resize_gl(self, width, height):
        "Called every time the on-screen window is resized"
        glViewport(0, 0, width, height)
            

if __name__ == "__main__":
    "Use 'with' keyword to be sure we clean up after ourselved at the end"
    with PinkWorld() as pink_world:
        glutMainLoop()
