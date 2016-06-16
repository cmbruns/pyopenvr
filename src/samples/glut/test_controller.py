#!/bin/env python

# file hello_glfw.py

from glut_app import GlutApp
from openvr.gl_renderer import OpenVrGlRenderer
from test_controller_actor import TrackedDevicesActor

"""
Minimal glfw programming example which colored OpenGL cube scene that can be closed by pressing ESCAPE.
"""


if __name__ == "__main__":
    renderer = OpenVrGlRenderer()
    actor = TrackedDevicesActor(renderer.poses)
    renderer.append(actor)
    with GlutApp(renderer, "Controller test") as glutApp:
        glutApp.run_loop()
