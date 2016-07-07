#!/bin/env python

# file hello_wx.py

import sys

import wx
from wx import glcanvas


"""
Minimal wxPython programming example which colored OpenGL cube scene that can be closed by pressing ESCAPE.
"""

class WxApp(wx.App):
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
		print('creating Frame')
		self.window = wx.Frame ( parent=None, id=wx.ID_ANY, title=self.title,
			style=wx.DEFAULT_FRAME_STYLE|wx.WS_EX_PROCESS_IDLE )
		print('creating GLCanvas')
		self.canvas = glcanvas.GLCanvas ( self.window, glcanvas.WX_GL_RGBA )
		print('creating GLContext')
		self.context = glcanvas.GLContext(self.canvas)
		self.canvas.SetFocus()
		self.window.SetSize ( (self.renderer.window_size[0], self.renderer.window_size[1]) )
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
		# self.canvas.SwapBuffers()
		if self.canvas.IsDoubleBuffered():
			self.canvas.SwapBuffers()
			print ("double buffered") # Do not want
		else:
			pass
			# TODO: SwapBuffers() seems required to show on desktop monitor,
			# but causes stalling when monitor is slower than VR headset
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
	
	def OnChar ( self, event ):
		key = event.GetKeyCode()
		# print (key)
		if key == ord('q') or key == ord('Q') or key == wx.WXK_ESCAPE: # Q or ESCAPE
			# print ("closing")
			self.window.Close()
			sys.exit(0) # In non-debug mode, Frame.Close() does not seem to close the application
			return		#self.window.Refresh(False)
		event.Skip()
	
	def run_loop ( self ):
		self.MainLoop()

