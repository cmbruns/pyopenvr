#!/bin/env python

# file hello_sdl.py

from textwrap import dedent

from OpenGL.GL import *  # @UnusedWildImport # this comment squelches an IDE warning
from OpenGL.GL.shaders import compileShader, compileProgram
from OpenGL.arrays import vbo
from sdl2 import *
import numpy

import openvr

"""
Minimal sdl programming example which colored OpenGL cube scene that can be closed by pressing ESCAPE.
"""

class HelloAppQuit(Exception):
	pass

class HelloApp(object):
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
		print('HelloApp exiting')
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
		SDL_GL_SetAttribute( SDL_GL_DOUBLEBUFFER, 1 )
		self.window = SDL_CreateWindow (
			self.title.encode('utf-8'),
			SDL_WINDOWPOS_CENTERED, SDL_WINDOWPOS_CENTERED,
			self.renderer.width, self.renderer.height, SDL_WINDOW_SHOWN|SDL_WINDOW_OPENGL)
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
		SDL_GL_SwapWindow(self.window)
	
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
		raise HelloAppQuit()
	
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
		except HelloAppQuit as e:
			pass

class BasicGlResource(object):
	"No-op OpenGL object to be used as an abstract base class for OpenGL actors"

	def init_gl(self):
		"allocate OpenGL resources"
		pass

	def display_gl(self, modelview, projection):
		"render scene one time"
		pass

	def dispose_gl(self):
		"delete OpenGL resources"
		pass


# TODO: matrixForOpenVrMatrix() is not general, it is specific the perspective and 
# modelview matrices used in this example
def matrixForOpenVrMatrix(mat, for_whom):
	if len(mat.m) == 4: # HmdMatrix44_t?
		result = numpy.matrix(
				((mat.m[0][0], mat.m[1][0], mat.m[2][0], mat.m[3][0]),
				 (mat.m[0][1], mat.m[1][1], mat.m[2][1], mat.m[3][1]), 
				 (mat.m[0][2], mat.m[1][2], mat.m[2][2], mat.m[3][2]), 
				 (mat.m[0][3], mat.m[1][3], mat.m[2][3], mat.m[3][3]),)
			, numpy.float32)
		return result
	elif len(mat.m) == 3: # HmdMatrix34_t?
		result = numpy.matrix(
				((mat.m[0][0], mat.m[1][0], mat.m[2][0], 0.0),
				 (mat.m[0][1], mat.m[1][1], mat.m[2][1], 0.0), 
				 (mat.m[0][2], mat.m[1][2], mat.m[2][2], 0.0), 
				 (mat.m[0][3], mat.m[1][3], mat.m[2][3], 0.1),)
			, numpy.float32)  
		return result.I


class OpenVrFramebuffer(BasicGlResource):
	"Framebuffer for rendering one eye"
	
	def __init__(self, width, height):
		self.fb = 0
		self.depth_buffer = 0
		self.texture_id = 0
		self.width = width
		self.height = height
		
	def init_gl(self):
		# Set up framebuffer and render textures
		self.fb = glGenFramebuffers(1)
		glBindFramebuffer(GL_FRAMEBUFFER, self.fb)
		self.depth_buffer = glGenRenderbuffers(1)
		glBindRenderbuffer(GL_RENDERBUFFER, self.depth_buffer)
		glRenderbufferStorage(GL_RENDERBUFFER, GL_DEPTH24_STENCIL8, self.width, self.height)
		glFramebufferRenderbuffer(GL_FRAMEBUFFER, GL_DEPTH_STENCIL_ATTACHMENT, GL_RENDERBUFFER, self.depth_buffer)
		self.texture_id = glGenTextures(1)
		glBindTexture(GL_TEXTURE_2D, self.texture_id)
		glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA8, self.width, self.height, 0, GL_RGBA, GL_UNSIGNED_BYTE, None)
		glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
		glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
		glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
		glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
		glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAX_LEVEL, 0)  
		glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, self.texture_id, 0)
		status = glCheckFramebufferStatus(GL_FRAMEBUFFER)
		if status != GL_FRAMEBUFFER_COMPLETE:
			glBindFramebuffer(GL_FRAMEBUFFER, 0)
			raise Exception("Incomplete framebuffer")
		glBindFramebuffer(GL_FRAMEBUFFER, 0)   
		# OpenVR texture data
		self.texture = openvr.Texture_t()
		self.texture.handle = ctypes.cast ( int(self.texture_id), ctypes.c_void_p )
		self.texture.eType = openvr.API_OpenGL
		self.texture.eColorSpace = openvr.ColorSpace_Gamma 
		
	def dispose_gl(self):
		glDeleteTextures([self.texture_id])
		glDeleteRenderbuffers(1, [self.depth_buffer])
		glDeleteFramebuffers(1, [self.fb])
		self.fb = 0


class OpenVrGlRenderer(BasicGlResource):
	"Renders to virtual reality headset using OpenVR and OpenGL APIs"
	width, height = 0, 0

	def __init__(self, width, height, actor):
		self.width = width
		self.height = height
		self.actor = actor
		self.vr_system = None
		self.left_fb = None
		self.right_fb = None

	def init_gl(self):
		"allocate OpenGL resources"
		self.actor.init_gl()
		self.vr_system = openvr.init(openvr.VRApplication_Scene)
		w, h = self.vr_system.getRecommendedRenderTargetSize()
		self.left_fb = OpenVrFramebuffer(w, h)
		self.right_fb = OpenVrFramebuffer(w, h)
		self.compositor = openvr.VRCompositor()
		if self.compositor is None:
			raise Exception("Unable to create compositor") 
		poses_t = openvr.TrackedDevicePose_t * openvr.k_unMaxTrackedDeviceCount
		self.poses = poses_t()
		self.left_fb.init_gl()
		self.right_fb.init_gl()
		# Compute projection matrix
		zNear = 0.1
		zFar = 100.0
		self.projection_left = matrixForOpenVrMatrix(self.vr_system.getProjectionMatrix(
				openvr.Eye_Left, 
				zNear, zFar, 
				openvr.API_OpenGL), "projection_left")
		self.projection_right = matrixForOpenVrMatrix(self.vr_system.getProjectionMatrix(
				openvr.Eye_Right, 
				zNear, zFar, 
				openvr.API_OpenGL), "projection_right")

	def size_callback ( self, window, width, height ):
		self.width = width
		self.height = height

	def render_scene(self):
		self.compositor.waitGetPoses(self.poses, openvr.k_unMaxTrackedDeviceCount, None, 0)
		hmd_pose0 = self.poses[openvr.k_unTrackedDeviceIndex_Hmd]
		if not hmd_pose0.bPoseIsValid:
			return
		hmd_pose1 = hmd_pose0.mDeviceToAbsoluteTracking
		hmd_pose = matrixForOpenVrMatrix(hmd_pose1, "hmd_pose")
		# TODO: use the pose to compute things
		# 1) On-screen render:
		modelview = hmd_pose # TODO: per eye...
		glViewport(0, 0, self.width, self.height)
		self.display_gl(modelview, self.projection_left)
		# 2) VR render
		# Left eye view
		glBindFramebuffer(GL_FRAMEBUFFER, self.left_fb.fb)
		glViewport(0, 0, self.left_fb.width, self.left_fb.height)
		self.display_gl(modelview, self.projection_left)
		self.compositor.submit(openvr.Eye_Left, self.left_fb.texture)
		# Right eye view
		glBindFramebuffer(GL_FRAMEBUFFER, self.right_fb.fb)
		self.display_gl(modelview, self.projection_right)
		self.compositor.submit(openvr.Eye_Right, self.right_fb.texture)
		glBindFramebuffer(GL_FRAMEBUFFER, 0)
		
	def display_gl(self, modelview, projection):
		self.actor.display_gl(modelview, projection)

	def dispose_gl(self):
		self.actor.dispose_gl()
		if self.vr_system is not None:
			openvr.shutdown()
			self.vr_system = None
		if self.left_fb is not None:
			self.left_fb.dispose_gl()
			self.right_fb.dispose_gl()


class BlueBackgroundActor(BasicGlResource):
	"Simplest possible renderer just paints the whole universe blue"

	def display_gl(self, modelview, projection):
		"render scene one time"
		glClearColor(0.5, 0.5, 1.0, 0.0)
		glClear(GL_COLOR_BUFFER_BIT)


class ColorCubeActor(BasicGlResource):
	"""
	Draws a cube
	
	   2________ 3
	   /|      /|
	 6/_|____7/ |
	  | |_____|_| 
	  | /0    | /1
	  |/______|/
	  4       5
	"""
	
	def __init__(self):
		self.shader = 0
	
	def init_gl(self):
		vertex_shader = compileShader(dedent(
			"""\
			#version 450 core
			#line 268
			
			// Adapted from @jherico's RiftDemo.py in pyovr
			
			layout(location = 0) uniform mat4 Projection = mat4(1);
			layout(location = 4) uniform mat4 ModelView = mat4(1);
			layout(location = 8) uniform float Size = 5.0;
			
			// Minimum Y value is zero, so cube sits on the floor in room scale
			const vec3 UNIT_CUBE[8] = vec3[8](
			  vec3(-1.0, -0.0, -1.0), // 0: lower left rear
			  vec3(+1.0, -0.0, -1.0), // 1: lower right rear
			  vec3(-1.0, +2.0, -1.0), // 2: upper left rear
			  vec3(+1.0, +2.0, -1.0), // 3: upper right rear
			  vec3(-1.0, -0.0, +1.0), // 4: lower left front
			  vec3(+1.0, -0.0, +1.0), // 5: lower right front
			  vec3(-1.0, +2.0, +1.0), // 6: upper left front
			  vec3(+1.0, +2.0, +1.0)  // 7: upper right front
			);
			
			const vec3 UNIT_CUBE_NORMALS[6] = vec3[6](
			  vec3(0.0, 0.0, -1.0),
			  vec3(0.0, 0.0, 1.0),
			  vec3(1.0, 0.0, 0.0),
			  vec3(-1.0, 0.0, 0.0),
			  vec3(0.0, 1.0, 0.0),
			  vec3(0.0, -1.0, 0.0)
			);
			
			const int CUBE_INDICES[36] = int[36](
			  0, 1, 2, 2, 1, 3, // front
			  4, 6, 5, 6, 5, 7, // back
			  0, 2, 4, 4, 2, 6, // left
			  1, 3, 5, 5, 3, 7, // right
			  2, 6, 3, 6, 3, 7, // top
			  0, 1, 4, 4, 1, 5  // bottom
			);
			
			out vec3 _color;
			
			void main() {
			  _color = vec3(1.0, 0.0, 0.0);
			  int vertexIndex = CUBE_INDICES[gl_VertexID];
			  int normalIndex = gl_VertexID / 6;
			  
			  _color = UNIT_CUBE_NORMALS[normalIndex];
			  if (any(lessThan(_color, vec3(0.0)))) {
				  _color = vec3(1.0) + _color;
			  }
			
			  gl_Position = Projection * ModelView * vec4(UNIT_CUBE[vertexIndex] * Size, 1.0);
			}
			"""), 
			GL_VERTEX_SHADER)
		fragment_shader = compileShader(dedent(
			"""\
			#version 450 core
			#line 325
			
			in vec3 _color;
			out vec4 FragColor;
			
			void main() {
			  FragColor = vec4(_color, 1.0);
			}
			"""), 
			GL_FRAGMENT_SHADER)
		self.shader = compileProgram(vertex_shader, fragment_shader)
		#
		self.vao = glGenVertexArrays(1)
		glBindVertexArray(self.vao)
		glEnable(GL_DEPTH_TEST)
		
	def display_gl(self, modelview, projection):
		glClearColor(0.3, 0.3, 0.3, 0.0) # gray background
		glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
		#
		glUseProgram(self.shader)
		glUniformMatrix4fv(0, 1, False, projection)
		glUniformMatrix4fv(4, 1, False, modelview)
		glDrawArrays(GL_TRIANGLES, 0, 36)
	
	def dispose_gl(self):
		glDeleteProgram(self.shader)
		self.shader = 0
		glDeleteVertexArrays(1, (self.vao,))
		self.vao = 0


if __name__ == "__main__":
	# Show a blue OpenGL window
	actor0 = ColorCubeActor()
	renderer0 = OpenVrGlRenderer(800, 600, actor0)
	with HelloApp(renderer0, "sdl2 OpenVR color cube") as app:
		app.run_loop()
