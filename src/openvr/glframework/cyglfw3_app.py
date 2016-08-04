#!/bin env python

import cyglfw3 as glfw

"""
Tow cyglfw3 application for use with "hello world" examples demonstrating pyopenvr
"""

class CyGLFW3App(object):
    """
    Uses the glfw library via the cyglfw3 bindings to create an opengl context, listen to keyboard
    and VR HMD/controller events, and clean up
    """

    def __init__(self, renderer, title="CyGLFW3 test"):
        self.renderer = renderer
        self.title = title
        self._is_initialized = False
        self.window = None

    def __enter__(self):
        """setup for 'with' keyword"""
        return self

    def __exit__(self, type_arg, value, traceback):
        """cleanup for 'with' keyword"""
        self.dispose_gl()

    def init_gl(self):
        if self._is_initialized:
            return
        if not glfw.Init():
            raise RuntimeError("GLFW Initialization failed")
        glfw.WindowHint(glfw.CONTEXT_VERSION_MAJOR, 4)
        glfw.WindowHint(glfw.CONTEXT_VERSION_MINOR, 1)
        glfw.WindowHint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
        glfw.WindowHint(glfw.DOUBLEBUFFER, False)
        glfw.SwapInterval(0)
        self.window = glfw.CreateWindow(self.renderer.window_size[0], self.renderer.window_size[1],
                                        self.title)
        if self.window is None:
            glfw.Terminate()
            raise RuntimeError("GLFW Window creation failed")
        glfw.SetKeyCallback(self.window, self.key_callback)
        glfw.MakeContextCurrent(self.window)
        if self.renderer is not None:
            self.renderer.init_gl()
        self._is_initialized = True

    def render_scene(self):
        "render scene one time"
        self.init_gl()
        glfw.MakeContextCurrent(self.window)
        self.renderer.render_scene()
        glfw.SwapBuffers(self.window)
        glfw.PollEvents()

    def dispose_gl(self):
        if self.window is not None:
            glfw.MakeContextCurrent(self.window)
            if self.renderer is not None:
                self.renderer.dispose_gl()
        glfw.Terminate()
        self._is_initialized = False

    def key_callback(self, window, key, scancode, action, mods):
        """press ESCAPE to quite the application"""
        if key == glfw.KEY_ESCAPE and action == glfw.PRESS:
            glfw.SetWindowShouldClose(self.window, True)

    def run_loop(self):
        """keep rendering until the user presses escape"""
        while not glfw.WindowShouldClose(self.window):
            self.render_scene()
