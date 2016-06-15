#!/bin/env python

# file color_cube_actor.py

import time
from textwrap import dedent

import numpy
from OpenGL.GL import *  # @UnusedWildImport # this comment squelches an IDE warning
from OpenGL.GL.shaders import compileShader, compileProgram
from OpenGL.arrays import vbo

import openvr

"""
Color cube for use in "hello world" openvr apps
"""


class ControllerActor(object):
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
            #line 38
            
            in vec3 in_Position;
            
            layout(location = 0) uniform mat4 projection = mat4(1);
            layout(location = 4) uniform mat4 model_view = mat4(1);
            
            void main() {
              vec3 vertex = in_Position;
              gl_Position = projection * model_view * vec4(vertex, 1.0);
            }
            """), 
            GL_VERTEX_SHADER)
        fragment_shader = compileShader(dedent(
            """\
            #version 450 core
            #line 54
            
            out vec4 fragColor;
            
            void main() {
              fragColor = vec4(0.5, 0.5, 0.2, 1.0);
            }
            """), 
            GL_FRAGMENT_SHADER)
        self.shader = compileProgram(vertex_shader, fragment_shader)
        # http://stackoverflow.com/questions/14365484/how-to-draw-with-vertex-array-objects-and-gldrawelements-in-pyopengl
        self.vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        # Load controller model
        error = openvr.EVRRenderModelError()
        modelName = openvr.VRSystem().getStringTrackedDeviceProperty(1, openvr.Prop_RenderModelName_String)
        while True:
            error, model = openvr.VRRenderModels().loadRenderModel_Async(modelName)
            if error != openvr.VRRenderModelError_Loading:
                break
            time.sleep(1)
        vertices0 = list()
        indices0 = list()
        if model is not None:
            for v in range (model.unVertexCount):
                vd = model.rVertexData[v]
                vertices0.append(float(vd.vPosition.v[0])) # X
                vertices0.append(float(vd.vPosition.v[1])) # Y
                vertices0.append(float(vd.vPosition.v[2])) # Z
            for i in range (model.unTriangleCount * 3):
                index = model.rIndexData[i]
                indices0.append(int(index))
        vertices0 = numpy.array(vertices0, dtype=numpy.float32)
        indices0 = numpy.array(indices0, dtype=numpy.uint32)
        #
        vertices = numpy.array([
            [0, 0, 0],
            [0.5, 0, 0],
            [0.5, 0.8, 0],
            ], dtype='float32')
        self.vertexPositions = vbo.VBO(vertices0)
        indices = numpy.array([0, 1, 2], dtype=numpy.int32)
        self.indexPositions = vbo.VBO(indices0, target=GL_ELEMENT_ARRAY_BUFFER)
        #
        glEnable(GL_DEPTH_TEST)
        
    def display_gl(self, modelview, projection):
        glUseProgram(self.shader)
        glUniformMatrix4fv(0, 1, False, projection)
        glUniformMatrix4fv(4, 1, False, modelview)
        self.indexPositions.bind()
        self.vertexPositions.bind()
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, False, 0, None)
        glDrawElements(GL_TRIANGLES, len(self.indexPositions), GL_UNSIGNED_INT, None)
    
    def dispose_gl(self):
        glDeleteProgram(self.shader)
        self.shader = 0
        glDeleteBuffers(1, (self.vbo,))
        self.vbo = 0
