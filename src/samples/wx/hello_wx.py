#!/bin/env python

# file hello_wx.py

from openvr.gl_renderer import OpenVrGlRenderer
from openvr.color_cube_actor import ColorCubeActor
from openvr.glframework.wx_app import WxApp


"""
Minimal wxPython programming example which colored OpenGL cube scene that can be closed by pressing ESCAPE.
"""


if __name__ == "__main__":
	# Show a blue OpenGL window
	actor = ColorCubeActor()
	renderer0 = OpenVrGlRenderer(actor, (800,600))
	with WxApp(renderer0, "wx OpenVR color cube") as app:
		app.run_loop()
