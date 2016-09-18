#!/bin/env python

# file hello_cyglfw3.py

from openvr.glframework.cyglfw3_app import CyGLFW3App
from openvr.gl_renderer import OpenVrGlRenderer
from openvr.color_cube_actor import ColorCubeActor

"""
Minimal glfw programming example which colored OpenGL cube scene that can be closed by pressing ESCAPE.
"""


if __name__ == "__main__":
    actor = ColorCubeActor()
    renderer = OpenVrGlRenderer(actor)
    with CyGLFW3App(renderer, "glfw OpenVR color cube") as app:
        app.run_loop()
