#!/bin/env python

# file hello_glfw.py

import numpy
from numpy.linalg import inv
import itertools
from textwrap import dedent
from ctypes import cast, c_float, c_void_p, sizeof

# from OpenGL.GL import *  # @UnusedWildImport # this comment squelches an IDE warning
from OpenGL.GL import GL_FLOAT, GL_ELEMENT_ARRAY_BUFFER, GL_FRAGMENT_SHADER, GL_TRIANGLES, GL_UNSIGNED_INT, GL_VERTEX_SHADER
from OpenGL.GL import glUniformMatrix4fv, glUseProgram, glVertexAttribPointer, glDrawElements, glBindVertexArray, glGenVertexArrays, glEnableVertexAttribArray, glDeleteVertexArrays
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

class MyTransform(object):
    "4x4 linear Transform for use by OpenGL"
    def __init__(self, template=None):
        if template is None:
            self._m = numpy.identity(4, dtype=numpy.float32)
        else:
            self._m = numpy.array(template, dtype=numpy.float32)

    def __add__(self, rhs):
        return MyTransform(self._m + rhs)

    def __getitem__(self, key):
        return self._m[key]
        
    def __iadd__(self, rhs):
        self._m += rhs

    def __invert__(self):
        return MyTransform(inv(self._m))

    def __isub__(self, rhs):
        self._m -= rhs

    def __iter__(self):
        return self._m.__iter__()

    def __len__(self):
        return len(self._m)

    def __mul__(self, rhs):
        "matrix multiplication"
        return MyTransform(numpy.dot(self._m, rhs))
    
    def __neg__(self):
        return MyTransform(-self._m)
    
    def __pos__(self):
        return self
    
    def __radd__(self, lhs):
        return MyTransform(self._m + lhs)

    def __rmul__(self, lhs):
        "matrix multiplication"
        return MyTransform(numpy.dot(lhs, self._m))
    
    def __rsub__(self, lhs):
        return MyTransform(lhs - self._m)

    def __setitem__(self, key, value):
        self._m[key] = value
    
    def __sub__(self, rhs):
        return MyTransform(self._m - rhs)

    @staticmethod
    def fromOpenVrMatrix34(mat):
        return MyTransform( 
                ((mat.m[0][0], mat.m[1][0], mat.m[2][0], 0.0),
                 (mat.m[0][1], mat.m[1][1], mat.m[2][1], 0.0), 
                 (mat.m[0][2], mat.m[1][2], mat.m[2][2], 0.0), 
                 (mat.m[0][3], mat.m[1][3], mat.m[2][3], 1.0),)
                )

    def pack(self):
        "create a packed copy, ready for use by OpenGL calls"
        return numpy.asarray(self._m, dtype=numpy.float32)
        
    @staticmethod
    def translation(x, y, z):
        return MyTransform( (
                             (1, 0, 0, 0),
                             (0, 1, 0, 0),
                             (0, 0, 1, 0),
                             (x, y, z, 1),) )
    
    def transpose(self):
        return MyTransform(self._m.T)


# TODO - subdivide this example into
# * mesh
# * actor
# * material
# * lighting
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
        self.model_matrix = MyTransform()

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
        
        # TODO: Adjust modelview matrix
        modelview0 = self.model_matrix * modelview
        # modelview0 = numpy.asarray(numpy.matrix(modelview0, dtype=numpy.float32))
        # print(modelview0[3,0])
        
        glUniformMatrix4fv(4, 1, False, modelview0.pack())
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


class ControllerState(object):
    def __init__(self, name):
        self.name = name
        self.is_dragging = False
        self.device_index = None
        self.current_pose = None
        self.previous_pose = None
        
    def check_drag(self, poses):
        if self.device_index is None:
            return
        self.current_pose = poses[self.device_index]
        is_good_drag = True # start optimistic
        if not self.is_dragging:
            is_good_drag = False
            self.previous_pose = None
        if self.previous_pose is None:
            is_good_drag = False
        elif not self.previous_pose.bPoseIsValid:
            is_good_drag = False
        if not self.current_pose.bPoseIsValid:
            is_good_drag = False
        if is_good_drag:
            X0 = self.previous_pose.mDeviceToAbsoluteTracking
            X1 = self.current_pose.mDeviceToAbsoluteTracking
            # Translation only, for now
            dx = X1.m[0][3] - X0.m[0][3]
            dy = X1.m[1][3] - X0.m[1][3]
            dz = X1.m[2][3] - X0.m[2][3]
            # print("%+7.4f, %+7.4f, %+7.4f" % (dx, dy, dz))
            do_translation_only = True
            if do_translation_only:
                result = MyTransform.translation(dx, dy, dz)
            else:
                result = ~MyTransform.fromOpenVrMatrix34(X0) * MyTransform.fromOpenVrMatrix34(X1)
        else:
            result = None
        # Create a COPY of the current pose for comparison next time
        self.previous_pose = openvr.TrackedDevicePose_t(self.current_pose.mDeviceToAbsoluteTracking)
        self.previous_pose.bPoseIsValid = self.current_pose.bPoseIsValid
        return result


left_controller = ControllerState("left controller")
right_controller = ControllerState("right controller")
def check_controller_drag(event):
    dix = new_event.trackedDeviceIndex
    device_class = openvr.VRSystem().getTrackedDeviceClass(dix)
    # We only want to watch controller events
    if device_class != openvr.TrackedDeviceClass_Controller:
        return
    bix = event.data.controller.button
    # Pay attention to trigger presses only
    if bix != openvr.k_EButton_SteamVR_Trigger:
        return
    role = openvr.VRSystem().getControllerRoleForTrackedDeviceIndex(dix)
    if role == openvr.TrackedControllerRole_RightHand:
        controller = right_controller
        # print("  right controller trigger %s" % action)
    else:
        controller = left_controller
        # print("  left controller trigger %s" % action)
    controller.device_index = dix
    t = event.eventType
    # "Touch" event happens earlier than "Press" event,
    # so allow a light touch for grabbing here
    if t == openvr.VREvent_ButtonTouch:
        controller.is_dragging = True
    elif t == openvr.VREvent_ButtonUntouch:
        controller.is_dragging = False

if __name__ == "__main__":
    obj = ObjMesh(open("root_997.obj", 'r'))
    # invert up/down
    obj.model_matrix *= ((1,0,0,0),
                         (0,-1,0,0),
                         (0,0,-1,0),
                         (-0.5,1.5,0.5,1),
                         )
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
            # Update controller drag state when buttons are pushed
            while openvr.VRSystem().pollNextEvent(new_event):
                check_controller_drag(new_event)
            tx1 = right_controller.check_drag(renderer.poses)
            tx2 = left_controller.check_drag(renderer.poses)
            if tx1 is None and tx2 is None:
                pass # No dragging this time
            elif tx1 is not None and tx2 is not None:
                # TODO - combined transform
                obj.model_matrix *= 0.5 * (tx1 + tx2)
            elif tx1 is not None:
                obj.model_matrix *= tx1
            else:
                obj.model_matrix *= tx2
