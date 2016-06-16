#!/bin/env python

# file glfwapp.py

import glfw
from OpenGL.GL import glFlush


"""
Toy glfw application for use with "hello world" examples demonstrating pyopenvr
"""


class GlfwApp(object):
    "GlfwApp uses glfw library to create an opengl context, listen to keyboard events, and clean up"

    def __init__(self, renderer, title="GLFW test"):
        "Creates an OpenGL context and a window, and acquires OpenGL resources"
        self.renderer = renderer
        self.title = title
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
        # Double buffered screen mirror stalls VR headset rendering,
        # So use single-buffering
        glfw.window_hint(glfw.DOUBLEBUFFER, False)
        glfw.swap_interval(0)
        self.window = glfw.create_window(self.renderer.window_size[0], self.renderer.window_size[1], self.title, None, None)
        if self.window is None:
            glfw.terminate()
            raise Exception("GLFW window creation error")
        glfw.set_key_callback(self.window, self.key_callback)
        glfw.make_context_current(self.window)
        if self.renderer is not None:
            self.renderer.init_gl()
        self._is_initialized = True

    def render_scene(self):
        "render scene one time"
        self.init_gl() # should be a no-op after the first frame is rendered
        glfw.make_context_current(self.window)
        self.renderer.render_scene()
        # Done rendering
        # glfw.swap_buffers(self.window) # avoid double buffering to avoid stalling
        glFlush() # single buffering
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
            self.render_scene()
