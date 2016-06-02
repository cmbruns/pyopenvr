#!/bin/env python

# file hello_glfw.py


from OpenGL.GL import *  # @UnusedWildImport # this comment squelches an IDE warning
import glfw

import openvr

"""
Minimal glfw programming example which creates a blue OpenGL window that can be closed by pressing ESCAPE.
"""


class GlfwApp(object):
    "GlfwApp uses glfw library to create an opengl context, listen to keyboard events, and clean up"

    def __init__(self, renderer):
        "Creates an OpenGL context and a window, and acquires OpenGL resources"
        self.renderer = renderer
        self._is_initialized = False # keep track of whether self.init_gl() has been called
        self.window = None

    def __enter__(self):
        "setup for RAII using 'with' keyword"
        return self

    def __exit__(self, type_arg, value, traceback):
        "cleanup for RAII using 'with' keyword"
        self.dispose_gl()

    def init_gl(self):
        if self._is_initialized:
            return # only initialize once
        if not glfw.init():
            raise Exception("GLFW Initialization error")
        # Get OpenGL 4.1 context
        glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 4)
        glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 1)
        glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
        self.window = glfw.create_window(800, 600, "GLFW test", None, None)
        if self.window is None:
            glfw.terminate()
            raise Exception("GLFW window creation error")
        glfw.set_key_callback(self.window, self.key_callback)
        glfw.make_context_current(self.window)
        if self.renderer is not None:
            self.renderer.init_gl()
        self._is_initialized = True

    def display_gl(self):
        "render scene one time"
        self.init_gl() # should be a no-op after the first frame is rendered
        glfw.make_context_current(self.window)
        self.renderer.display_gl()
        # Done rendering
        glfw.swap_buffers(self.window)
        glfw.poll_events()

    def dispose_gl(self):
        if self.window is not None:
            glfw.make_context_current(self.window)
            if self.renderer is not None:
                self.renderer.dispose_gl()
        glfw.terminate()
        self._is_initialized = False

    def key_callback(self, window, key, scancode, action, mods):
        "press ESCAPE to quit the application"
        if key == glfw.KEY_ESCAPE and action == glfw.PRESS:
            glfw.set_window_should_close(self.window, True)

    def run_loop(self):
        "keep rendering until the user says quit"
        while not glfw.window_should_close(self.window):
            self.display_gl()


class BasicGlResource(object):
    "No-op OpenGL object to be used as an abstract base class for OpenGL actors"

    def init_gl(self):
        "allocate OpenGL resources"
        pass

    def display_gl(self):
        "render scene one time"
        pass

    def dispose_gl(self):
        "delete OpenGL resources"
        pass


class OpenVrGlRenderer(BasicGlResource):
    "Renders to virtual reality headset using OpenVR and OpenGL APIs"

    def __init__(self, actor):
        self.actor = actor

    def init_gl(self):
        "allocate OpenGL resources"
        self.actor.init_gl()
        self.vr_system = openvr.init(openvr.VRApplication_Scene)
        self.vr_width, self.vr_height = self.vr_system.getRecommendedRenderTargetSize()
        self.compositor = openvr.VRCompositor()
        if self.compositor is None:
            raise Exception("Unable to create compositor") 
        poses_t = openvr.TrackedDevicePose_t * openvr.k_unMaxTrackedDeviceCount
        self.poses = poses_t()
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

    def display_gl(self):
        self.compositor.waitGetPoses(self.poses, openvr.k_unMaxTrackedDeviceCount, None, 0)
        hmd_pose0 = self.poses[openvr.k_unTrackedDeviceIndex_Hmd]
        if not hmd_pose0.bPoseIsValid:
            return
        # hmd_pose = hmd_pose0.mDeviceToAbsoluteTracking
        # TODO: use the pose to compute things
        # 1) On-screen render:
        self.actor.display_gl()
        # 2) VR render
        # TODO: render different things to each eye
        glBindFramebuffer(GL_FRAMEBUFFER, self.fb)
        self.actor.display_gl()
        glBindFramebuffer(GL_FRAMEBUFFER, 0)
        #
        # TODO: use different textures for each eye
        self.compositor.submit(openvr.Eye_Left, self.texture)
        self.compositor.submit(openvr.Eye_Right, self.texture)
        glBindFramebuffer(GL_FRAMEBUFFER, 0)

    def dispose_gl(self):
        self.actor.dispose_gl()
        if self.vr_system is not None:
            openvr.shutdown()
            self.vr_system = None
        glDeleteTextures([self.texture_id])
        glDeleteRenderbuffers(1, [self.depth_buffer])
        glDeleteFramebuffers([self.fb])
        self.fb = 0


class BlueBackgroundActor(BasicGlResource):
    "Simplest possible renderer just paints the whole universe blue"

    def display_gl(self):
        "render scene one time"
        glClearColor(0.5, 0.5, 1.0, 0.0)
        glClear(GL_COLOR_BUFFER_BIT)


if __name__ == "__main__":
    # Show a blue OpenGL window
    actor0 = BlueBackgroundActor()
    renderer0 = OpenVrGlRenderer(actor0)
    with GlfwApp(renderer0) as glfwApp:
        glfwApp.run_loop()
