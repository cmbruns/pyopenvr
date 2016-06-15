#!/bin/env python

# file color_cube_actor.py

from textwrap import dedent

import numpy
from OpenGL.GL import *  # @UnusedWildImport # this comment squelches an IDE warning
from OpenGL.GL.shaders import compileShader, compileProgram
from OpenGL.arrays import vbo


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
            
            layout(location = 0) uniform mat4 Projection = mat4(1);
            layout(location = 4) uniform mat4 ModelView = mat4(1);
            
            void main() {
              vec3 vertex = in_Position;
              gl_Position = Projection * ModelView * vec4(vertex, 1.0);
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
        #
        self.vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        vertices = numpy.array([
            [0, 0, 0],
            [0.5, 0, 0],
            [0.5, 0.8, 0],
            ], dtype='float32')
        self.vertexPositions = vbo.VBO(vertices)
        indices = numpy.array([0, 1, 2], dtype=numpy.int32)
        self.indexPositions = vbo.VBO(indices, target=GL_ELEMENT_ARRAY_BUFFER)
        glBufferData(GL_ARRAY_BUFFER, vertices, GL_STATIC_DRAW)
        glEnable(GL_DEPTH_TEST)
        
    def display_gl(self, modelview, projection):
        glClearColor(0.3, 0.3, 0.3, 0.0) # gray background
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glUseProgram(self.shader)
        glUniformMatrix4fv(0, 1, False, projection)
        glUniformMatrix4fv(4, 1, False, modelview)
        self.indexPositions.bind()
        self.vertexPositions.bind()
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, False, 0, None)
        glDrawElements(GL_TRIANGLES, 3, GL_UNSIGNED_INT, None)
    
    def dispose_gl(self):
        glDeleteProgram(self.shader)
        self.shader = 0
        glDeleteBuffers(1, (self.vbo,))
        self.vbo = 0
