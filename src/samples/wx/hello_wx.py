#!/bin/env python

# file hello_wx.py

from textwrap import dedent

from OpenGL.GL import *  # @UnusedWildImport # this comment squelches an IDE warning
from OpenGL.GL.shaders import compileShader, compileProgram
from OpenGL.arrays import vbo
import wx
from wx import glcanvas
import numpy

import openvr

"""
Minimal wxPython programming example which colored OpenGL cube scene that can be closed by pressing ESCAPE.
"""

class HelloApp(wx.App):
	"HelloApp uses wxPython library to create an opengl context, listen to keyboard events, and clean up"
	renderer = None
	title = None
	_is_initialized = False
	window = None
	canvas = None
	context = None
	running = False

	def __init__(self, renderer, title="wx test"):
		"Creates an OpenGL context and a window, and acquires OpenGL resources"
		self.renderer = renderer
		self.title = title
		self._is_initialized = False # keep track of whether self.init_gl() has been called
		self.window = None
		
		wx.App.__init__(self, redirect = False)
	
	def OnInit ( self ):
		self.init_gl()
		return True
	
	def OnIdle ( self, evt ):
		self.window.Refresh(False)
		evt.RequestMore()
	
	def __enter__(self):
		"setup for RAII using 'with' keyword"
		return self
	
	def __exit__(self, type_arg, value, traceback):
		"cleanup for RAII using 'with' keyword"
		self.dispose_gl()
	
	def init_gl(self):
		# Get OpenGL 4.1 context
		#SDL_GL_SetAttribute(SDL_GL_CONTEXT_MAJOR_VERSION, 4)
		#SDL_GL_SetAttribute(SDL_GL_CONTEXT_MINOR_VERSION, 1)
		#SDL_GL_SetAttribute(SDL_GL_CONTEXT_PROFILE_MASK, SDL_GL_CONTEXT_PROFILE_CORE)
		print('creating Frame')
		self.window = wx.Frame ( parent=None, id=wx.ID_ANY, title=self.title,
			style=wx.DEFAULT_FRAME_STYLE|wx.WS_EX_PROCESS_IDLE )
		print('creating GLCanvas')
		self.canvas = glcanvas.GLCanvas ( self.window )
		print('creating GLContext')
		self.context = glcanvas.GLContext(self.canvas)
		self.canvas.SetFocus()
		self.window.SetSize ( (self.renderer.width, self.renderer.height) )
		print('showing Frame')
		self.window.Show(True)
		
		print('calling SetTopWindow')
		self.SetTopWindow(self.window)
		
		self.Bind ( wx.EVT_CHAR, self.OnChar )
		self.canvas.Bind ( wx.EVT_SIZE, self.OnCanvasSize )
		self.canvas.Bind ( wx.EVT_PAINT, self.OnCanvasPaint )
		
		wx.IdleEvent.SetMode ( wx.IDLE_PROCESS_SPECIFIED )
		self.Bind ( wx.EVT_IDLE, self.OnIdle )
		
		print('making context current')
		self.canvas.SetCurrent ( self.context )
		self.renderer.init_gl()
	
	def OnCanvasPaint ( self, event ):
		self.render_scene()
	
	def render_scene(self):
		"render scene one time"
		self.canvas.SetCurrent ( self.context )
		self.renderer.render_scene()
		# Done rendering
		self.canvas.SwapBuffers()
	
	def dispose_gl(self):
		pass
	
	def OnCanvasSize ( self, event ):
		wx.CallAfter(self.DoSetViewport)
		event.Skip()
	
	def DoSetViewport ( self ):
		size = self.canvas.GetClientSize()
		#print('DoSetViewport({},{})'.format(size.width,size.height))
		self.canvas.SetCurrent ( self.context )
		self.renderer.size_callback ( self.window, size.width, size.height )
	
	def OnChar ( self, evt ):
		key = evt.GetKeyCode()
		c = chr(key)
		if c == 'q' or key == 27: # Q or ESCAPE
			self.window.Close(True)
			return
		#self.window.Refresh(False)
	
	def run_loop ( self ):
		self.MainLoop()

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
		print ( "size_callback ( {}, {} )".format ( width, height ) )
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
	with HelloApp(renderer0, "wx OpenVR color cube") as app:
		app.run_loop()
