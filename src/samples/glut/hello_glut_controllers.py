#!/bin/env python

# file hello_glut_controllers.py

from glut_app import GlutApp
from openvr.gl_renderer import OpenVrGlRenderer
from openvr.tracked_devices_actor import TrackedDevicesActor
from openvr.color_cube_actor import ColorCubeActor

"""
Minimal glfw programming example which colored OpenGL cube scene that can be closed by pressing ESCAPE.
"""


if __name__ == "__main__":
    renderer = OpenVrGlRenderer()
    actor = TrackedDevicesActor(renderer.poses)
    renderer.append(actor)
    renderer.append(ColorCubeActor())
    with GlutApp(renderer, "Controller test") as glutApp:
        glutApp.run_loop()
