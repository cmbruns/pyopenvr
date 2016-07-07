#!/bin/env python

# file hello_glfw.py

import numpy
import itertools
from textwrap import dedent
from ctypes import cast, c_float, c_void_p

from OpenGL.GL import *  # @UnusedWildImport # this comment squelches an IDE warning
from OpenGL.GL.shaders import compileShader, compileProgram
from OpenGL.arrays import vbo

import glfw
import openvr

from openvr.glframework.glfw_app import GlfwApp
from openvr.gl_renderer import OpenVrGlRenderer
from openvr.tracked_devices_actor import TrackedDevicesActor

"""
Minimal glfw programming example which colored OpenGL cube scene that can be closed by pressing ESCAPE.
"""

class ObjMesh(object):
    def __init__(self, file_stream=None):
        "Create a mesh object from a file stream"
        self.vertices = []
        self.normals = []
        self.texcoords = []
        self.triangles = []
        if file_stream is not None:
            self.load_file_stream(file_stream)
        self.vao = 0
        self.vertexPositions = None
        self.indexPositions = None
        # self.init_gl()

    def _parse_line(self, line):
        fields = line.split()
        if not fields:
            return # skip empty lines
        key = fields[0]
        if key.startswith('#'):
            return # skip comment lines
        if key == 'v':
            self._parse_vertex(fields)
        elif key == 'vn':
            self._parse_normal(fields)
        elif key == 'vt':
            self._parse_texcoord(fields)
        elif key == 'f':
            self._parse_face(fields)
        else:
            raise "Unrecognized data line starting with '%s'" % key

    def _parse_vertex(self, fields):
        x, y, z = map(float, fields[1:4])
        if len(fields) > 4:
            w = float(fields[4])
        else:
            w = 1.0
        v = (x/w, y/w, z/w)
        self.vertices.append( v )
        # print(v)

    def _parse_normal(self, fields):
        self.normals.append( map(float, fields[1:4]) )

    def _parse_face(self, fields):
        face = []
        for v in fields[1:]:
            w = v.split('/')
            face.append(int(w[0]))
        for triangle in range(len(face) - 2):
            self.triangles.append([i-1 for i in face[triangle:triangle+3]])

    def init_gl(self):
        self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)
        # flatten vector arrays
        idx = [item for sublist in self.triangles for item in sublist]
        floats_per_vertex = 3
        # Is there one normal per vertex? If so, pack them together
        use_normals = False
        if len(self.vertices) == len(self.normals):
            use_normals = True
            floats_per_vertex += 3
            # flatten list
            vtx = list(itertools.chain.from_iterable(zip(self.vertices, self.normals)))
            # flatten again, because the structure was three levels deep
            vtx = list(itertools.chain.from_iterable(vtx))
        else:
            vtx = [item for v in self.vertices for item in v]
        # print(vtx)
        self.vertexPositions = vbo.VBO(
            numpy.array(vtx, dtype=numpy.float32))
        self.indexPositions = vbo.VBO(
            numpy.array(idx, dtype=numpy.uint32), 
            target=GL_ELEMENT_ARRAY_BUFFER)
        self.vertexPositions.bind()
        self.indexPositions.bind()
        # Triangle vertices
        glEnableVertexAttribArray(0)
        fsize = sizeof(c_float)
        glVertexAttribPointer(0, 3, GL_FLOAT, False, floats_per_vertex * fsize, cast(0 * fsize, c_void_p))
        if use_normals:
            glEnableVertexAttribArray(1)
            glVertexAttribPointer(1, 3, GL_FLOAT, False, floats_per_vertex * fsize, cast(3 * fsize, c_void_p))
        glBindVertexArray(0)
        # 
        vertex_shader = compileShader(dedent(
            """\
            #version 450 core
            #line 113
            
            layout(location = 0) in vec3 in_Position;
            layout(location = 1) in vec3 in_Normal;
            
            layout(location = 0) uniform mat4 projection = mat4(1);
            layout(location = 4) uniform mat4 model_view = mat4(1);

            const mat4 scale = mat4(mat3(0.0001)); // convert micrometers to millimeters

            out vec3 norm_color;
            
            void main() {
              gl_Position = projection * model_view * scale * vec4(in_Position, 1.0);
              norm_color = 0.5 * (in_Normal + vec3(1));
            }
            """), 
            GL_VERTEX_SHADER)
        fragment_shader = compileShader(dedent(
            """\
            #version 450 core
            #line 134

            in vec3 norm_color;
            out vec4 fragColor;
            
            void main() {
              // fragColor = vec4(0.1, 0.8, 0.1, 1.0);
              fragColor = vec4(norm_color, 1);
            }
            """), 
            GL_FRAGMENT_SHADER)
        self.shader = compileProgram(vertex_shader, fragment_shader)

    def display_gl(self, modelview, projection):
        glUseProgram(self.shader)
        glUniformMatrix4fv(0, 1, False, projection)
        glUniformMatrix4fv(4, 1, False, modelview)
        glBindVertexArray(self.vao)
        glDrawElements(GL_TRIANGLES, len(self.indexPositions), GL_UNSIGNED_INT, None)
        glBindVertexArray(0)

    def dispose_gl(self):
        glDeleteVertexArrays(1, (self.vao,))
        self.vao = 0
        if self.vertexPositions is not None:
            self.vertexPositions.delete()
            self.indexPositions.delete()     

    def load_file_stream(self, file_stream):
        for line in file_stream:
            self._parse_line(line)



if __name__ == "__main__":
    obj = ObjMesh(open("root_997.obj", 'r'))
    # obj = ObjMesh(open("AIv6b_699.obj", 'r'))

    renderer = OpenVrGlRenderer(multisample=2)
    # renderer.append(ColorCubeActor())
    controllers = TrackedDevicesActor(renderer.poses)
    controllers.show_controllers_only = True
    renderer.append(controllers)
    renderer.append(obj)
    new_event = openvr.VREvent_t()
    with GlfwApp(renderer, "mouse brain") as glfwApp:
        while not glfw.window_should_close(glfwApp.window):
            glfwApp.render_scene()
            # TODO poll events
            while openvr.VRSystem().pollNextEvent(new_event):
                dix = new_event.trackedDeviceIndex
                device_class = openvr.VRSystem().getTrackedDeviceClass(dix)
                # We only want to watch controller events
                if device_class != openvr.TrackedDeviceClass_Controller:
                    continue
                # print("device class = %d" % device_class)
                t = new_event.eventType
                # "Touch" event happens earlier than "Press" event,
                # so allow a light touch for grabbing here
                if t == openvr.VREvent_ButtonTouch:
                    # print("Button touched")
                    action = "touched"
                    pass
                elif t == openvr.VREvent_ButtonUntouch:
                    # print("Button detouched")
                    action = "released"
                    pass
                else:
                    continue
                bix = new_event.data.controller.button
                # Pay attention to trigger presses only
                if bix != openvr.k_EButton_SteamVR_Trigger:
                    continue
                role = openvr.VRSystem().getControllerRoleForTrackedDeviceIndex(dix)
                if role == openvr.TrackedControllerRole_RightHand:
                    print("  right controller trigger %s" % action)
                else:
                    print("  left controller trigger %s" % action)
                # print("button %d" % new_event.data.controller.button)
                
