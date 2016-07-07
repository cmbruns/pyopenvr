#!/bin/env python

# file sdl_app.py

import ctypes

from OpenGL.GL import glFlush  # @UnusedWildImport # this comment squelches an IDE warning
from sdl2 import * # @UnusedWildImport


"""
Minimal sdl programming example which colored OpenGL cube scene that can be closed by pressing ESCAPE.
"""

class SdlAppQuit(Exception):
	pass

class SdlApp(object):
	"SdlApp uses sdl2 library to create an opengl context, listen to keyboard events, and clean up"
	renderer = None
	title = None
	_is_initialized = False
	window = None
	context = None
	running = False
	_sdl_event_handlers = None

	def __init__(self, renderer, title="SDL test"):
		"Creates an OpenGL context and a window, and acquires OpenGL resources"
		self.renderer = renderer
		self.title = title
		self._is_initialized = False # keep track of whether self.init_gl() has been called
		self.window = None
		self._sdl_event_handlers = {
			SDL_WINDOWEVENT: self.on_sdl_window_event,
			SDL_KEYDOWN: self.on_sdl_keydown,
			SDL_QUIT: self.on_sdl_quit,
		}
	
	def __enter__(self):
		"setup for RAII using 'with' keyword"
		return self
	
	def __exit__(self, type_arg, value, traceback):
		"cleanup for RAII using 'with' keyword"
		print('SdlApp exiting')
		self.dispose_gl()
	
	def init_gl(self):
		if self._is_initialized:
			return # only initialize once
		result = SDL_Init(SDL_INIT_VIDEO)
		if result < 0:
			raise Exception("SDL Initialization error: {}".format(SDL_GetError()))
		# Get OpenGL 4.1 context
		SDL_GL_SetAttribute(SDL_GL_CONTEXT_MAJOR_VERSION, 4)
		SDL_GL_SetAttribute(SDL_GL_CONTEXT_MINOR_VERSION, 1)
		SDL_GL_SetAttribute(SDL_GL_CONTEXT_PROFILE_MASK, SDL_GL_CONTEXT_PROFILE_CORE)
		SDL_GL_SetAttribute( SDL_GL_RED_SIZE, 5 )
		SDL_GL_SetAttribute( SDL_GL_GREEN_SIZE, 5 )
		SDL_GL_SetAttribute( SDL_GL_BLUE_SIZE, 5 )
		SDL_GL_SetAttribute( SDL_GL_DEPTH_SIZE, 16 )
		SDL_GL_SetAttribute( SDL_GL_DOUBLEBUFFER, 0 )
		self.window = SDL_CreateWindow (
			self.title.encode('utf-8'),
			SDL_WINDOWPOS_CENTERED, SDL_WINDOWPOS_CENTERED,
			self.renderer.window_size[0], self.renderer.window_size[1], SDL_WINDOW_SHOWN|SDL_WINDOW_OPENGL)
		if self.window is None:
			SDL_Quit()
			raise Exception("SDL window creation error: {}".format(SDL_GetError()))
		self.context = SDL_GL_CreateContext(self.window)
		SDL_GL_MakeCurrent ( self.window, self.context )
		if self.renderer is not None:
			self.renderer.init_gl()
		self._is_initialized = True
	
	def render_scene(self):
		"render scene one time"
		self.init_gl() # should be a no-op after the first frame is rendered
		SDL_GL_MakeCurrent ( self.window, self.context )
		self.renderer.render_scene()
		# Done rendering
		# SDL_GL_SwapWindow(self.window)
		glFlush()
	
	def dispose_gl(self):
		if self.window is not None:
			SDL_GL_MakeCurrent ( self.window, self.context )
			if self.renderer is not None:
				self.renderer.dispose_gl()
			if self.context is not None:
				SDL_GL_DeleteContext(self.context)
			SDL_DestroyWindow(self.window)
		SDL_Quit()
		self._is_initialized = False
	
	def on_sdl_window_event ( self, event ):
		if event.window.event == SDL_WINDOWEVENT_RESIZED:
			width, height = SDL_GL_GetDrawableSize ( self.window )
			self.renderer.size_callback ( self.window, width, height )
	
	def on_sdl_keydown ( self, event ):
		"press ESCAPE to quit the application"
		key = event.key.keysym.sym
		if key == SDLK_ESCAPE:
			self.running = False
	
	def on_sdl_quit ( self, event ):
		self.running = False
		raise SdlAppQuit()
	
	def run_loop(self):
		"keep rendering until the user says quit"
		self.running = True
		event = SDL_Event()
		try:
			while self.running:
				while SDL_PollEvent(ctypes.byref(event)) != 0:
					f = self._sdl_event_handlers.get(event.type)
					if f is not None:
						f ( event )
				self.render_scene()
		except SdlAppQuit as e:
			pass
