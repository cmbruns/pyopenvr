#!/bin/env python

# file color_cube_actor.py

from textwrap import dedent

from OpenGL.GL import *  # @UnusedWildImport # this comment squelches an IDE warning
from OpenGL.GL.shaders import compileShader, compileProgram


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
            #line 36
            
            // Adapted from @jherico's RiftDemo.py in pyovr
            
            layout(location = 0) uniform mat4 Projection = mat4(1);
            layout(location = 4) uniform mat4 ModelView = mat4(1);
            
            // Minimum Y value is zero, so cube sits on the floor in room scale
            const vec3 UNIT_CUBE[8] = vec3[8](
              vec3(-0.3, -0.0, -0.3), // 0: lower left rear
              vec3(+0.3, -0.0, -0.3), // 1: lower right rear
              vec3(-0.3, +0.6, -0.3), // 2: upper left rear
              vec3(+0.3, +0.6, -0.3), // 3: upper right rear
              vec3(-0.3, -0.0, +0.3), // 4: lower left front
              vec3(+0.3, -0.0, +0.3), // 5: lower right front
              vec3(-0.3, +0.6, +0.3), // 6: upper left front
              vec3(+0.3, +0.6, +0.3)  // 7: upper right front
            );
            
            const int CUBE_INDICES[36] = int[36](
              0, 1, 2, 2, 1, 3, // front
              4, 6, 5, 6, 5, 7, // back
              0, 2, 4, 4, 2, 6, // left
              1, 3, 5, 5, 3, 7, // right
              2, 6, 3, 6, 3, 7, // top
              0, 1, 4, 4, 1, 5  // bottom
            );
            
            void main() {
              int vertexIndex = CUBE_INDICES[gl_VertexID];
              gl_Position = Projection * ModelView * vec4(UNIT_CUBE[vertexIndex], 1.0);
            }
            """), 
            GL_VERTEX_SHADER)
        fragment_shader = compileShader(dedent(
            """\
            #version 450 core
            #line 93
            
            out vec4 fragColor;
            
            void main() {
              fragColor = vec4(0.5, 0.5, 0.2, 1.0);
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
