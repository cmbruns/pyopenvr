#!/bin/env python

# file color_cube_actor.py

import time
from textwrap import dedent
from ctypes import sizeof, cast, c_float, c_void_p

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
    Draws a Vive controller
    """
    
    def __init__(self):
        self.shader = 0
    
    def init_gl(self):
        vertex_shader = compileShader(dedent(
            """\
            #version 450 core
            #line 40
            
            layout(location = 0) in vec3 in_Position;
            layout(location = 1) in vec3 in_Normal;
            layout(location = 2) in vec2 in_TexCoord;
            
            layout(location = 0) uniform mat4 projection = mat4(1);
            layout(location = 4) uniform mat4 model_view = mat4(1);
            
            out vec3 color;
            
            void main() {
              gl_Position = projection * model_view * vec4(in_Position, 1.0);
              // color = (normalize(in_Normal) + vec3(1,1,1)) * 0.5; // color by normal
              color = vec3(in_TexCoord, 0.5); // color by texture coordinate
            }
            """), 
            GL_VERTEX_SHADER)
        fragment_shader = compileShader(dedent(
            """\
            #version 450 core
            #line 59
            
            in vec3 color;
            out vec4 fragColor;
            
            void main() {
              fragColor = vec4(color, 1.0);
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
                vertices0.append(float(vd.vPosition.v[0])) # position X
                vertices0.append(float(vd.vPosition.v[1])) # position Y
                vertices0.append(float(vd.vPosition.v[2])) # position Z
                vertices0.append(float(vd.vNormal.v[0])) # normal X
                vertices0.append(float(vd.vNormal.v[1])) # normal Y
                vertices0.append(float(vd.vNormal.v[2])) # normal Z
                vertices0.append(float(vd.rfTextureCoord[0])) # texture coordinate U
                vertices0.append(float(vd.rfTextureCoord[1])) # texture coordinate V
            for i in range (model.unTriangleCount * 3):
                index = model.rIndexData[i]
                indices0.append(int(index))
        vertices0 = numpy.array(vertices0, dtype=numpy.float32)
        indices0 = numpy.array(indices0, dtype=numpy.uint32)
        #
        self.vertexPositions = vbo.VBO(vertices0)
        self.indexPositions = vbo.VBO(indices0, target=GL_ELEMENT_ARRAY_BUFFER)
        #
        glEnable(GL_DEPTH_TEST)
        
    def display_gl(self, modelview, projection):
        glUseProgram(self.shader)
        glUniformMatrix4fv(0, 1, False, projection)
        glUniformMatrix4fv(4, 1, False, modelview)
        self.indexPositions.bind()
        self.vertexPositions.bind()
        # Vertices
        glEnableVertexAttribArray(0)
        fsize = sizeof(c_float)
        glVertexAttribPointer(0, 3, GL_FLOAT, False, 8 * fsize, cast(0 * fsize, c_void_p))
        # Normals
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 3, GL_FLOAT, False, 8 * fsize, cast(3 * fsize, c_void_p))
        # Texture coordinates    
        glEnableVertexAttribArray(2)
        glVertexAttribPointer(2, 2, GL_FLOAT, False, 8 * fsize, cast(6 * fsize, c_void_p))
        #
        glDrawElements(GL_TRIANGLES, len(self.indexPositions), GL_UNSIGNED_INT, None)
    
    def dispose_gl(self):
        glDeleteProgram(self.shader)
        self.shader = 0
        glDeleteBuffers(1, (self.vbo,))
        self.vbo = 0
