#!/bin/env python

# file hello_wx.py

from openvr.gl_renderer import OpenVrGlRenderer
from openvr.color_cube_actor import ColorCubeActor
from openvr.tracked_devices_actor import TrackedDevicesActor
from openvr.glframework.wx_app import WxApp


"""
Minimal wxPython programming example which colored OpenGL cube scene that can be closed by pressing ESCAPE.
"""


if __name__ == "__main__":
	renderer = OpenVrGlRenderer()
	renderer.append(ColorCubeActor())
	renderer.append(TrackedDevicesActor(renderer.poses))
	with WxApp(renderer, "wx OpenVR color cube") as app:
		app.run_loop()
