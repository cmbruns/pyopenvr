#!/bin/env python

# file openvr_gl_renderer.py

from OpenGL.GL import *  # @UnusedWildImport # this comment squelches an IDE warning
import numpy

import openvr

"""
Renders OpenGL scenes to virtual reality headsets using OpenVR API
"""


# TODO: matrixForOpenVrMatrix() is not general, it is specific the perspective and 
# modelview matrices used in this example
def matrixForOpenVrMatrix(mat):
    if len(mat.m) == 4: # HmdMatrix44_t?
        result = numpy.matrix(
                ((mat.m[0][0], mat.m[1][0], mat.m[2][0], mat.m[3][0]),
                 (mat.m[0][1], mat.m[1][1], mat.m[2][1], mat.m[3][1]), 
                 (mat.m[0][2], mat.m[1][2], mat.m[2][2], mat.m[3][2]), 
                 (mat.m[0][3], mat.m[1][3], mat.m[2][3], mat.m[3][3]),)
            , numpy.float32)
        return result
    elif len(mat.m) == 3: # HmdMatrix34_t?
        result = numpy.matrix(
                ((mat.m[0][0], mat.m[1][0], mat.m[2][0], 0.0),
                 (mat.m[0][1], mat.m[1][1], mat.m[2][1], 0.0), 
                 (mat.m[0][2], mat.m[1][2], mat.m[2][2], 0.0), 
                 (mat.m[0][3], mat.m[1][3], mat.m[2][3], 1.0),)
            , numpy.float32)  
        return result


class OpenVrFramebuffer(object):
    "Framebuffer for rendering one eye"
    
    def __init__(self, width, height, multisample = 0):
        self.fb = 0
        self.depth_buffer = 0
        self.texture_id = 0
        self.width = width
        self.height = height
        self.compositor = None
        self.multisample = multisample
        
    def init_gl(self):
        # Set up framebuffer and render textures
        self.fb = glGenFramebuffers(1)
        glBindFramebuffer(GL_FRAMEBUFFER, self.fb)
        self.depth_buffer = glGenRenderbuffers(1)
        glBindRenderbuffer(GL_RENDERBUFFER, self.depth_buffer)
        if self.multisample > 0:
            glRenderbufferStorageMultisample(GL_RENDERBUFFER, self.multisample, GL_DEPTH24_STENCIL8, self.width, self.height)
        else:
            glRenderbufferStorage(GL_RENDERBUFFER, GL_DEPTH24_STENCIL8, self.width, self.height)
        glFramebufferRenderbuffer(GL_FRAMEBUFFER, GL_DEPTH_STENCIL_ATTACHMENT, GL_RENDERBUFFER, self.depth_buffer)
        self.texture_id = int(glGenTextures(1))
        if self.multisample > 0:
            glBindTexture(GL_TEXTURE_2D_MULTISAMPLE, self.texture_id)
            glTexImage2DMultisample(GL_TEXTURE_2D_MULTISAMPLE, self.multisample, GL_RGBA8, self.width, self.height, True)
            glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D_MULTISAMPLE, self.texture_id, 0)
        else:
            glBindTexture(GL_TEXTURE_2D, self.texture_id)
            glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA8, self.width, self.height, 0, GL_RGBA, GL_UNSIGNED_BYTE, None)
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
        # Resolver framebuffer in case of multisample antialiasing
        if self.multisample > 0:
            self.resolve_fb = glGenFramebuffers(1)
            glBindFramebuffer(GL_FRAMEBUFFER, self.resolve_fb)
            self.resolve_texture_id = int(glGenTextures(1))
            glBindTexture(GL_TEXTURE_2D, self.resolve_texture_id)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAX_LEVEL, 0)
            glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA8, self.width, self.height, 0, GL_RGBA, GL_UNSIGNED_BYTE, None)
            glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, self.resolve_texture_id, 0)
            status = glCheckFramebufferStatus(GL_FRAMEBUFFER)
            if status != GL_FRAMEBUFFER_COMPLETE:
                glBindFramebuffer(GL_FRAMEBUFFER, 0)
                raise Exception("Incomplete framebuffer")
        glBindFramebuffer(GL_FRAMEBUFFER, 0)   
        # OpenVR texture data
        self.texture = openvr.Texture_t()
        if self.multisample > 0:
            self.texture.handle = self.resolve_texture_id
        else:
            self.texture.handle = self.texture_id
        self.texture.eType = openvr.TextureType_OpenGL
        self.texture.eColorSpace = openvr.ColorSpace_Gamma
        
    def submit(self, eye):
        if self.multisample > 0:
            glBindFramebuffer(GL_READ_FRAMEBUFFER, self.fb)
            glBindFramebuffer(GL_DRAW_FRAMEBUFFER, self.resolve_fb)
            glBlitFramebuffer(0, 0, self.width, self.height, 
                              0, 0, self.width, self.height,
                              GL_COLOR_BUFFER_BIT, GL_LINEAR)
            glBindFramebuffer(GL_READ_FRAMEBUFFER, 0)
            glBindFramebuffer(GL_DRAW_FRAMEBUFFER, 0)
        openvr.VRCompositor().submit(eye, self.texture)
        
    def dispose_gl(self):
        glDeleteTextures([self.texture_id])
        glDeleteRenderbuffers(1, [self.depth_buffer])
        glDeleteFramebuffers(1, [self.fb])
        self.fb = 0
        if self.multisample > 0:
            glDeleteTextures([self.resolve_texture_id])
            glDeleteFramebuffers(1, [self.resolve_fb])


class OpenVrGlRenderer(list):
    "Renders to virtual reality headset using OpenVR and OpenGL APIs"

    def __init__(self, actor=None, window_size=(800,600), multisample=0):
        self.vr_system = None
        self.left_fb = None
        self.right_fb = None
        self.window_size = window_size
        poses_t = openvr.TrackedDevicePose_t * openvr.k_unMaxTrackedDeviceCount
        self.poses = poses_t()
        if actor is not None:
            try:
                len(actor)
                self.extend(actor)
            except TypeError:
                self.append(actor)
        self.do_mirror = False
        self.multisample = multisample      

    def init_gl(self):
        "allocate OpenGL resources"
        self.vr_system = openvr.init(openvr.VRApplication_Scene)
        w, h = self.vr_system.getRecommendedRenderTargetSize()
        self.left_fb = OpenVrFramebuffer(w, h, multisample=self.multisample)
        self.right_fb = OpenVrFramebuffer(w, h, multisample=self.multisample)
        self.compositor = openvr.VRCompositor()
        if self.compositor is None:
            raise Exception("Unable to create compositor") 
        self.left_fb.init_gl()
        self.right_fb.init_gl()
        # Compute projection matrix
        zNear = 0.2
        zFar = 500.0
        self.projection_left = numpy.asarray(matrixForOpenVrMatrix(self.vr_system.getProjectionMatrix(
                openvr.Eye_Left, 
                zNear, zFar)))
        self.projection_right = numpy.asarray(matrixForOpenVrMatrix(self.vr_system.getProjectionMatrix(
                openvr.Eye_Right, 
                zNear, zFar)))
        self.view_left = matrixForOpenVrMatrix(
            self.vr_system.getEyeToHeadTransform(openvr.Eye_Left)).I  # head_X_eye in Kane notation
        self.view_right = matrixForOpenVrMatrix(
            self.vr_system.getEyeToHeadTransform(openvr.Eye_Right)).I  # head_X_eye in Kane notation
        for actor in self:
            actor.init_gl()

    def render_scene(self):
        if self.compositor is None:
            return
        self.compositor.waitGetPoses(self.poses, openvr.k_unMaxTrackedDeviceCount, None, 0)
        hmd_pose0 = self.poses[openvr.k_unTrackedDeviceIndex_Hmd]
        if not hmd_pose0.bPoseIsValid:
            return
        hmd_pose1 = hmd_pose0.mDeviceToAbsoluteTracking # head_X_room in Kane notation
        hmd_pose = matrixForOpenVrMatrix(hmd_pose1).I # room_X_head in Kane notation
        # Use the pose to compute things
        modelview = hmd_pose
        mvl = modelview * self.view_left # room_X_eye(left) in Kane notation
        mvr = modelview * self.view_right # room_X_eye(right) in Kane notation
        # Repack the resulting matrices to have default stride, to avoid
        # problems with weird strides and OpenGL
        mvl = numpy.asarray(numpy.matrix(mvl, dtype=numpy.float32))
        mvr = numpy.asarray(numpy.matrix(mvr, dtype=numpy.float32))
        # 1) On-screen render:
        if self.do_mirror:
            glViewport(0, 0, self.window_size[0], self.window_size[1])
            # Display left eye view to screen
            self.display_gl(mvl, self.projection_left)
        # 2) VR render
        # Left eye view
        glBindFramebuffer(GL_FRAMEBUFFER, self.left_fb.fb)
        glViewport(0, 0, self.left_fb.width, self.left_fb.height)
        self.display_gl(mvl, self.projection_left)
        self.left_fb.submit(openvr.Eye_Left)
        # self.compositor.submit(openvr.Eye_Left, self.left_fb.texture)
        # Right eye view
        glBindFramebuffer(GL_FRAMEBUFFER, self.right_fb.fb)
        self.display_gl(mvr, self.projection_right)
        self.right_fb.submit(openvr.Eye_Right)
        # self.compositor.submit(openvr.Eye_Right, self.right_fb.texture)
        glBindFramebuffer(GL_FRAMEBUFFER, 0)
        
    def display_gl(self, modelview, projection):
        glClearColor(0.5, 0.5, 0.5, 0.0) # gray background
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        for actor in self:
            actor.display_gl(modelview, projection)

    def dispose_gl(self):
        for actor in self:
            actor.dispose_gl()
        if self.vr_system is not None:
            openvr.shutdown()
            self.vr_system = None
        if self.left_fb is not None:
            self.left_fb.dispose_gl()
            self.right_fb.dispose_gl()
