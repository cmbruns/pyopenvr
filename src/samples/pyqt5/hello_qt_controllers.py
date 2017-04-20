#!/bin/env python

# file hello_qt_controllers.py

from openvr.glframework.qt5_app import Qt5App
from openvr.gl_renderer import OpenVrGlRenderer
from openvr.color_cube_actor import ColorCubeActor
from openvr.tracked_devices_actor import TrackedDevicesActor

"""
Toy PyQt5 application for use with "hello world" examples demonstrating pyopenvr
"""


if __name__ == "__main__":
    renderer = OpenVrGlRenderer(multisample=2)
    renderer.append(ColorCubeActor())
    controllers = TrackedDevicesActor(renderer.poses)
    controllers.show_controllers_only = False
    renderer.append(controllers)
    with Qt5App(renderer, "PyQt5 OpenVR color cube") as qt5_app:
        qt5_app.run_loop()
