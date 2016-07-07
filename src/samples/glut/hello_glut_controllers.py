#!/bin/env python

# file hello_glut_controllers.py

from openvr.glframework.glut_app import GlutApp
from openvr.gl_renderer import OpenVrGlRenderer
from openvr.tracked_devices_actor import TrackedDevicesActor
from openvr.color_cube_actor import ColorCubeActor

"""
Minimal glut programming example showing a colored OpenGL cube scene that can be closed by pressing ESCAPE.
"""

if __name__ == "__main__":
    renderer = OpenVrGlRenderer(multisample=4)
    renderer.append(ColorCubeActor())
    controllers = TrackedDevicesActor(renderer.poses)
    controllers.show_controllers_only = False
    renderer.append(controllers)
    with GlutApp(renderer, "Controller test") as glutApp:
        glutApp.run_loop()
