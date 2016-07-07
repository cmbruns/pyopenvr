#!/bin/env python

# file hello_sdl2.py


from openvr.gl_renderer import OpenVrGlRenderer
from openvr.color_cube_actor import ColorCubeActor
from openvr.glframework.sdl_app import SdlApp


"""
Minimal sdl programming example which colored OpenGL cube scene that can be closed by pressing ESCAPE.
"""


if __name__ == "__main__":
	renderer = OpenVrGlRenderer(multisample=2)
	renderer.append(ColorCubeActor())
	with SdlApp(renderer, "sdl2 OpenVR color cube") as app:
		app.run_loop()
