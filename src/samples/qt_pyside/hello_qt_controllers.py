#!/bin/env python

# file qt_pyside_app.py

import sys

from openvr.glframework.qt_pyside_app import QtPysideApp


"""
Toy PySide application for use with "hello world" examples demonstrating pyopenvr
"""


if __name__ == "__main__":
    from openvr.gl_renderer import OpenVrGlRenderer
    from openvr.color_cube_actor import ColorCubeActor
    from openvr.tracked_devices_actor import TrackedDevicesActor
    renderer = OpenVrGlRenderer()
    renderer.append(ColorCubeActor())
    renderer.append(TrackedDevicesActor(renderer.poses))
    with QtPysideApp(renderer, "PySide OpenVR color cube") as qtPysideApp:
        qtPysideApp.run_loop()
