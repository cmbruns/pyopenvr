#!/bin/env python

# file hello_glfw.py

from openvr.glframework.cyglfw3_app import CyGLFW3App
from openvr.gl_renderer import OpenVrGlRenderer
from openvr.color_cube_actor import ColorCubeActor
from openvr.tracked_devices_actor import TrackedDevicesActor

"""
Minimal glfw programming example which colored OpenGL cube scene that can be closed by pressing ESCAPE.
"""


if __name__ == "__main__":
    renderer = OpenVrGlRenderer(multisample=2)
    renderer.append(ColorCubeActor())
    controllers = TrackedDevicesActor(renderer.poses)
    controllers.show_controllers_only = False
    renderer.append(controllers)
    with CyGLFW3App(renderer, "glfw OpenVR color cube") as app:
        app.run_loop()
