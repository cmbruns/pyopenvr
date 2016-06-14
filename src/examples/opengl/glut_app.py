#!/bin/env python

# file glfwapp.py

from OpenGL.GL import *  # @UnusedWildImport # this comment squelches an IDE warning
from OpenGL.GLUT import * # @UnusedWildImport

"""
Toy glut application for use with "hello world" examples demonstrating pyopenvr
"""


class GlutApp(object):
    "GlutApp uses freeglut library to create an opengl context, listen to keyboard events, and clean up"

    def __init__(self, renderer, title="GLUT test"):
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
        glutInit()
        glutInitDisplayMode(GLUT_RGBA | GLUT_DEPTH | GLUT_DOUBLE)
        glutInitContextVersion(4, 1)
        # Create a regular desktop window, just so we can have an OpenGL context to play with
        glutInitWindowSize(800, 600)
        glutInitWindowPosition(50, 50)
        self.window = glutCreateWindow(self.title)
        # Set up callback methods for use during the GLUT main loop
        glutDisplayFunc(self.render_scene)
        glutIdleFunc(self.render_scene)
        glutReshapeFunc(self.resize_gl)
        glutKeyboardFunc(self.key_press)

        if self.renderer is not None:
            self.renderer.init_gl()
        self._is_initialized = True

    def render_scene(self):
        "render scene one time"
        self.init_gl() # should be a no-op after the first frame is rendered
        self.renderer.render_scene()

    def dispose_gl(self):
        if self.window is not None:
            if self.renderer is not None:
                self.renderer.dispose_gl()
            self.window = None
        self._is_initialized = False

    def key_callback(self, key, x, y):
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

    def run_loop(self):
        "keep rendering until the user says quit"
        glutMainLoop()
