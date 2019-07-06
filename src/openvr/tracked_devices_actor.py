#!/bin/env python

# file tracked_devices_actor.py

import time
from ctypes import cast, c_float, c_void_p, sizeof

import numpy
from OpenGL import GL
from OpenGL.GL.shaders import compileShader, compileProgram
from OpenGL.arrays import vbo
from OpenGL.GL.EXT.texture_filter_anisotropic import GL_TEXTURE_MAX_ANISOTROPY_EXT, GL_MAX_TEXTURE_MAX_ANISOTROPY_EXT

import openvr
from openvr.gl_renderer import matrixForOpenVrMatrix
from openvr.glframework import shader_string

"""
Tracked item (controllers, lighthouses, etc) actor for "hello world" openvr apps
"""


class TrackedDeviceMesh(object):
    def __init__(self, model_name):
        """This constructor must only be called with a live OpenGL context"""
        self.model_name = model_name
        self.model_is_loaded = False
        self.texture_is_loaded = False
        self.vao = None
        self.vbo = None
        self._try_load_model()
        self.vertexPositions = None

    def _try_load_model(self):
        try:
            model = openvr.VRRenderModels().loadRenderModel_Async(self.model_name)
        except openvr.error_code.RenderModelError_Loading:
            return
        vertices0 = list()
        indices0 = list()
        if model is not None:
            for v in range(model.unVertexCount):
                vd = model.rVertexData[v]
                vertices0.append(float(vd.vPosition.v[0]))  # position X
                vertices0.append(float(vd.vPosition.v[1]))  # position Y
                vertices0.append(float(vd.vPosition.v[2]))  # position Z
                vertices0.append(float(vd.vNormal.v[0]))  # normal X
                vertices0.append(float(vd.vNormal.v[1]))  # normal Y
                vertices0.append(float(vd.vNormal.v[2]))  # normal Z
                vertices0.append(float(vd.rfTextureCoord[0]))  # texture coordinate U
                vertices0.append(float(vd.rfTextureCoord[1]))  # texture coordinate V
            for i in range(model.unTriangleCount * 3):
                index = model.rIndexData[i]
                indices0.append(int(index))
        vertices0 = numpy.array(vertices0, dtype=numpy.float32)
        indices0 = numpy.array(indices0, dtype=numpy.uint32)
        #
        self.vertexPositions = vbo.VBO(vertices0)
        self.indexPositions = vbo.VBO(indices0, target=GL.GL_ELEMENT_ARRAY_BUFFER)
        # http://stackoverflow.com/questions/14365484/how-to-draw-with-vertex-array-objects-and-gldrawelements-in-pyopengl
        self.vao = GL.glGenVertexArrays(1)
        GL.glBindVertexArray(self.vao)
        self.vertexPositions.bind()
        self.indexPositions.bind()
        # Vertices
        GL.glEnableVertexAttribArray(0)
        fsize = sizeof(c_float)
        GL.glVertexAttribPointer(0, 3, GL.GL_FLOAT, False, 8 * fsize, cast(0 * fsize, c_void_p))
        # Normals
        GL.glEnableVertexAttribArray(1)
        GL.glVertexAttribPointer(1, 3, GL.GL_FLOAT, False, 8 * fsize, cast(3 * fsize, c_void_p))
        # Texture coordinates    
        GL.glEnableVertexAttribArray(2)
        GL.glVertexAttribPointer(2, 2, GL.GL_FLOAT, False, 8 * fsize, cast(6 * fsize, c_void_p))
        GL.glBindVertexArray(0)
        self.model = model
        self.model_is_loaded = True
        self._try_load_texture()

    def _try_load_texture(self):
        # Surface texture
        try:
            texture_map = openvr.VRRenderModels().loadTexture_Async(self.model.diffuseTextureId)
        except openvr.error_code.RenderModelError_Loading:
            return
        self.texture_map = texture_map
        self.diffuse_texture = GL.glGenTextures(1)
        GL.glBindTexture(GL.GL_TEXTURE_2D, self.diffuse_texture)
        GL.glTexImage2D(GL.GL_TEXTURE_2D, 0, GL.GL_RGBA, self.texture_map.unWidth, self.texture_map.unHeight,
                        0, GL.GL_RGBA,
                        GL.GL_UNSIGNED_BYTE, self.texture_map.rubTextureMapData)
        GL.glGenerateMipmap(GL.GL_TEXTURE_2D)
        GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_WRAP_S, GL.GL_CLAMP_TO_EDGE)
        GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_WRAP_T, GL.GL_CLAMP_TO_EDGE)
        GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MAG_FILTER, GL.GL_LINEAR)
        GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MIN_FILTER, GL.GL_LINEAR_MIPMAP_LINEAR)
        fLargest = GL.glGetFloatv(GL_MAX_TEXTURE_MAX_ANISOTROPY_EXT)
        GL.glTexParameterf(GL.GL_TEXTURE_2D, GL_TEXTURE_MAX_ANISOTROPY_EXT, fLargest)
        GL.glBindTexture(GL.GL_TEXTURE_2D, 0)
        self.texture_is_loaded = True

    def display_gl(self, modelview, projection, pose):
        if not self.model_is_loaded:
            self._try_load_model()
            return
        if not self.texture_is_loaded:
            self._try_load_texture()
            return
        controller_X_room = pose.mDeviceToAbsoluteTracking
        controller_X_room = matrixForOpenVrMatrix(controller_X_room)
        modelview0 = controller_X_room * modelview
        # Repack before use, just in case
        modelview0 = numpy.asarray(numpy.matrix(modelview0, dtype=numpy.float32))
        GL.glUniformMatrix4fv(4, 1, False, modelview0)
        normal_matrix = numpy.asarray(controller_X_room)
        GL.glUniformMatrix4fv(8, 1, False, normal_matrix)
        GL.glActiveTexture(GL.GL_TEXTURE0)
        GL.glBindTexture(GL.GL_TEXTURE_2D, self.diffuse_texture)
        GL.glBindVertexArray(self.vao)
        GL.glDrawElements(GL.GL_TRIANGLES, len(self.indexPositions), GL.GL_UNSIGNED_INT, None)
        GL.glBindVertexArray(0)

    def dispose_gl(self):
        if self.vao is not None:
            GL.glDeleteVertexArrays(1, (self.vao,))
            self.vao = None
        self.vbo = None
        if self.vertexPositions is not None:
            self.vertexPositions.delete()
            self.vertexPositions = None
            self.indexPositions.delete()
            self.indexPositions = None


class TrackedDevicesActor(object):
    """
    Draws Vive controllers and lighthouses.
    """

    def __init__(self, pose_array):
        self.shader = 0
        self.poses = pose_array
        self.meshes = dict()
        self.show_controllers_only = True

    def _check_devices(self):
        "Enumerate OpenVR tracked devices and check whether any need to be initialized"
        for i in range(1, len(self.poses)):
            pose = self.poses[i]
            if not pose.bDeviceIsConnected:
                continue
            if not pose.bPoseIsValid:
                continue
            if self.show_controllers_only:
                device_class = openvr.VRSystem().getTrackedDeviceClass(i)
                if not device_class == openvr.TrackedDeviceClass_Controller:
                    continue
            model_name = openvr.VRSystem().getStringTrackedDeviceProperty(i, openvr.Prop_RenderModelName_String)
            # Create a new mesh object, if necessary
            if model_name not in self.meshes:
                self.meshes[model_name] = TrackedDeviceMesh(model_name)

    def init_gl(self):
        vertex_shader = compileShader(
            shader_string("""
            layout(location = 0) in vec3 in_Position;
            layout(location = 1) in vec3 in_Normal;
            layout(location = 2) in vec2 in_TexCoord;
            
            layout(location = 0) uniform mat4 projection = mat4(1);
            layout(location = 4) uniform mat4 model_view = mat4(1);
            layout(location = 8) uniform mat4 normal_matrix = mat4(1);
            
            out vec3 color;
            out vec2 fragTexCoord;
            
            void main() {
              gl_Position = projection * model_view * vec4(in_Position, 1.0);
              vec3 normal = normalize((normal_matrix * vec4(in_Normal, 0)).xyz);
              color = (normal + vec3(1,1,1)) * 0.5; // color by normal
              fragTexCoord = in_TexCoord;
              // color = vec3(in_TexCoord, 0.5); // color by texture coordinate
            }
            """),
            GL.GL_VERTEX_SHADER)
        fragment_shader = compileShader(
            shader_string("""
            uniform sampler2D diffuse;
            in vec3 color;
            in vec2 fragTexCoord;
            out vec4 fragColor;
            
            void main() {
              // fragColor = vec4(color, 1.0);
              fragColor = texture(diffuse, fragTexCoord);
            }
            """),
            GL.GL_FRAGMENT_SHADER)
        self.shader = compileProgram(vertex_shader, fragment_shader)
        self._check_devices()
        GL.glEnable(GL.GL_DEPTH_TEST)

    def display_gl(self, modelview, projection):
        self._check_devices()
        GL.glEnable(GL.GL_DEPTH_TEST)
        GL.glUseProgram(self.shader)
        GL.glUniformMatrix4fv(0, 1, False, projection)
        for i in range(1, len(self.poses)):
            pose = self.poses[i]
            if not pose.bPoseIsValid:
                continue
            model_name = openvr.VRSystem().getStringTrackedDeviceProperty(i, openvr.Prop_RenderModelName_String)
            if model_name not in self.meshes:
                continue  # Come on, we already tried to load it a moment ago. Maybe next time.
            mesh = self.meshes[model_name]
            mesh.display_gl(modelview, projection, pose)

    def dispose_gl(self):
        GL.glDeleteProgram(self.shader)
        self.shader = 0
        for key in list(self.meshes):
            mesh = self.meshes[key]
            mesh.dispose_gl()
            del self.meshes[key]
