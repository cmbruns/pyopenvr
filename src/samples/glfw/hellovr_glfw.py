from ctypes import c_float, c_void_p, cast, sizeof
import inspect
import pkg_resources
import sys

import glfw
import numpy
from OpenGL import GL
from OpenGL.GL import shaders
from OpenGL.GL.EXT.texture_filter_anisotropic import GL_MAX_TEXTURE_MAX_ANISOTROPY_EXT, GL_TEXTURE_MAX_ANISOTROPY_EXT
from PIL import Image

import openvr


Left = 0
Right = 1


class CMainApplication(object):
    def __init__(self, argv):
        self.argv = argv
        self.hmd = None
        self.window = None
        self.scene_program = None
        self.scene_matrix_location = None
        self.controller_transform_program = None
        self.controller_matrix_location = None
        self.render_model_program = None
        self.render_model_matrix_location = None
        self.companion_window_program = None
        self.i_texture = None
        self.scene_volume_init = 20
        self.scale_spacing = 4
        self.vertex_data = None
        self.scene_vao = None
        self.vert_count = 0
        self.scene_vert_buffer = None
        self.proj_left = None
        self.proj_right = None
        self.pos_left = None
        self.pos_right = None
        self.render_width = 0
        self.render_height = 0
        self.left_eye_desc = None
        self.right_eye_desc = None
        self.companion_window_index_size = 0
        self.companion_window_vao = None
        self.companion_window_id_vert_buffer = None
        self.companion_window_id_index_buffer = None
        self.hand = (ControllerInfo(), ControllerInfo())
        self.action_hide_cubes = None
        self.action_hide_this_controller = None
        self.action_trigger_haptic = None
        self.action_analog_input = None
        self.action_set_demo = None

    def add_cube_to_scene(self, matrix):
        A = matrix @ (0, 0, 0, 1)
        B = matrix @ (1, 0, 0, 1)
        C = matrix @ (1, 1, 0, 1)
        D = matrix @ (0, 1, 0, 1)
        E = matrix @ (0, 0, 1, 1)
        F = matrix @ (1, 0, 1, 1)
        G = matrix @ (1, 1, 1, 1)
        H = matrix @ (0, 1, 1, 1)
        # triangles instead of quads
        self.add_cube_vertex(E[0], E[1], E[2], 0, 1)  # Front
        self.add_cube_vertex(F[0], F[1], F[2], 1, 1)
        self.add_cube_vertex(G[0], G[1], G[2], 1, 0)
        self.add_cube_vertex(G[0], G[1], G[2], 1, 0)
        self.add_cube_vertex(H[0], H[1], H[2], 0, 0)
        self.add_cube_vertex(E[0], E[1], E[2], 0, 1)
        self.add_cube_vertex(B[0], B[1], B[2], 0, 1)  # Back
        self.add_cube_vertex(A[0], A[1], A[2], 1, 1)
        self.add_cube_vertex(D[0], D[1], D[2], 1, 0)
        self.add_cube_vertex(D[0], D[1], D[2], 1, 0)
        self.add_cube_vertex(C[0], C[1], C[2], 0, 0)
        self.add_cube_vertex(B[0], B[1], B[2], 0, 1)
        self.add_cube_vertex(H[0], H[1], H[2], 0, 1)  # Top
        self.add_cube_vertex(G[0], G[1], G[2], 1, 1)
        self.add_cube_vertex(C[0], C[1], C[2], 1, 0)
        self.add_cube_vertex(C[0], C[1], C[2], 1, 0)
        self.add_cube_vertex(D[0], D[1], D[2], 0, 0)
        self.add_cube_vertex(H[0], H[1], H[2], 0, 1)
        self.add_cube_vertex(A[0], A[1], A[2], 0, 1)  # Bottom
        self.add_cube_vertex(B[0], B[1], B[2], 1, 1)
        self.add_cube_vertex(F[0], F[1], F[2], 1, 0)
        self.add_cube_vertex(F[0], F[1], F[2], 1, 0)
        self.add_cube_vertex(E[0], E[1], E[2], 0, 0)
        self.add_cube_vertex(A[0], A[1], A[2], 0, 1)
        self.add_cube_vertex(A[0], A[1], A[2], 0, 1)  # Left
        self.add_cube_vertex(E[0], E[1], E[2], 1, 1)
        self.add_cube_vertex(H[0], H[1], H[2], 1, 0)
        self.add_cube_vertex(H[0], H[1], H[2], 1, 0)
        self.add_cube_vertex(D[0], D[1], D[2], 0, 0)
        self.add_cube_vertex(A[0], A[1], A[2], 0, 1)
        self.add_cube_vertex(F[0], F[1], F[2], 0, 1)  # Right
        self.add_cube_vertex(B[0], B[1], B[2], 1, 1)
        self.add_cube_vertex(C[0], C[1], C[2], 1, 0)
        self.add_cube_vertex(C[0], C[1], C[2], 1, 0)
        self.add_cube_vertex(G[0], G[1], G[2], 0, 0)
        self.add_cube_vertex(F[0], F[1], F[2], 0, 1)

    def add_cube_vertex(self, x, y, z, a, b):
        self.vertex_data.extend([x, y, z, a, b])

    def b_init(self):
        glfw.init()
        glfw.window_hint(glfw.SAMPLES, 4)
        self.window = glfw.create_window(500, 200, 'hello_vr', None, None)
        glfw.make_context_current(self.window)
        #
        self.hmd = openvr.init(openvr.VRApplication_Scene)
        #
        vr_sys = openvr.VRSystem()
        driver = vr_sys.getStringTrackedDeviceProperty(
            openvr.k_unTrackedDeviceIndex_Hmd,
            openvr.Prop_TrackingSystemName_String,
        )
        display = vr_sys.getStringTrackedDeviceProperty(
            openvr.k_unTrackedDeviceIndex_Hmd,
            openvr.Prop_SerialNumber_String,
        )
        glfw.set_window_title(self.window, f'hello_vr -- {driver} {display}')
        self.b_init_gl()
        assert openvr.VRCompositor()
        action_path = pkg_resources.resource_filename('samples', 'hellovr_actions.json')
        openvr.VRInput().setActionManifestPath(action_path)
        self.action_hide_cubes = openvr.VRInput().getActionHandle('/actions/demo/in/HideCubes')
        self.action_hide_this_controller = openvr.VRInput().getActionHandle('/actions/demo/in/HideThisController')
        self.action_trigger_haptic = openvr.VRInput().getActionHandle('/actions/demo/in/TriggerHaptic')
        self.action_analog_input = openvr.VRInput().getActionHandle('/actions/demo/in/AnalogInput')
        self.action_set_demo = openvr.VRInput().getActionSetHandle('/actions/demo')
        self.hand[Left].action_haptic = openvr.VRInput().getActionHandle('/actions/demo/out/Haptic_Left')
        self.hand[Left].source = openvr.VRInput().getInputSourceHandle('/user/hand/left')
        self.hand[Left].action_pose = openvr.VRInput().getActionHandle('/actions/demo/in/Hand_Left')
        self.hand[Right].action_haptic = openvr.VRInput().getActionHandle('/actions/demo/out/Haptic_Right')
        self.hand[Right].source = openvr.VRInput().getInputSourceHandle('/user/hand/right')
        self.hand[Right].action_pose = openvr.VRInput().getActionHandle('/actions/demo/in/Hand_Right')
        return True

    def b_init_gl(self):
        self.create_all_shaders()
        self.set_up_texture_maps()
        self.set_up_scene()
        self.set_up_cameras()
        self.set_up_stereo_render_targets()
        self.set_up_companion_window()
        return True

    def create_all_shaders(self):
        self.scene_program = shaders.compileProgram(
            shaders.compileShader(source=inspect.cleandoc('''
                #version 410
                uniform mat4 matrix;
                layout(location = 0) in vec4 position;
                layout(location = 1) in vec2 v2UVcoordsIn;
                layout(location = 2) in vec3 v3NormalIn;
                out vec2 v2UVcoords;
                void main()
                {
                    v2UVcoords = v2UVcoordsIn;
                    gl_Position = matrix * position;
                }
            '''), shaderType=GL.GL_VERTEX_SHADER),
            shaders.compileShader(source=inspect.cleandoc('''
                #version 410 core
                uniform sampler2D mytexture;
                in vec2 v2UVcoords;
                out vec4 outputColor;
                void main()
                {
                    outputColor = texture(mytexture, v2UVcoords);
                }
            '''), shaderType=GL.GL_FRAGMENT_SHADER),
        )
        self.scene_matrix_location = GL.glGetUniformLocation(self.scene_program, 'matrix')
        #
        self.controller_transform_program = shaders.compileProgram(
            shaders.compileShader(source=inspect.cleandoc('''
                #version 410
                uniform mat4 matrix;
                layout(location = 0) in vec4 position;
                layout(location = 1) in vec3 v3ColorIn;
                out vec4 v4Color;
                void main()
                {
                    v4Color.xyz = v3ColorIn; v4Color.a = 1.0;
                    gl_Position = matrix * position;
                }
            '''), shaderType=GL.GL_VERTEX_SHADER),
            shaders.compileShader(source=inspect.cleandoc('''
                #version 410
                in vec4 v4Color;
                out vec4 outputColor;
                void main()
                {
                   outputColor = v4Color;
                }
            '''), shaderType=GL.GL_FRAGMENT_SHADER),
        )
        self.controller_matrix_location = GL.glGetUniformLocation(self.controller_transform_program, 'matrix')
        #
        self.render_model_program = shaders.compileProgram(
            shaders.compileShader(source=inspect.cleandoc('''
                #version 410
                uniform mat4 matrix;
                layout(location = 0) in vec4 position;
                layout(location = 1) in vec3 v3NormalIn;
                layout(location = 2) in vec2 v2TexCoordsIn;
                out vec2 v2TexCoord;
                void main()
                {
                    v2TexCoord = v2TexCoordsIn;
                    gl_Position = matrix * vec4(position.xyz, 1);
                }
            '''), shaderType=GL.GL_VERTEX_SHADER),
            shaders.compileShader(source=inspect.cleandoc('''
                #version 410 core
                uniform sampler2D diffuse;
                in vec2 v2TexCoord;
                out vec4 outputColor;
                void main()
                {
                   outputColor = texture( diffuse, v2TexCoord);
                }
            '''), shaderType=GL.GL_FRAGMENT_SHADER),
        )
        self.render_model_matrix_location = GL.glGetUniformLocation(self.render_model_program, 'matrix')
        #
        self.companion_window_program = shaders.compileProgram(
            shaders.compileShader(source=inspect.cleandoc('''
                #version 410 core
                layout(location = 0) in vec4 position;
                layout(location = 1) in vec2 v2UVIn;
                noperspective out vec2 v2UV;
                void main()
                {
                    v2UV = v2UVIn;
                    gl_Position = position;
                }
            '''), shaderType=GL.GL_VERTEX_SHADER),
            shaders.compileShader(source=inspect.cleandoc('''
                #version 410 core
                uniform sampler2D mytexture;
                noperspective in vec2 v2UV;
                out vec4 outputColor;
                void main()
                {
                        outputColor = texture(mytexture, v2UV);
                }
            '''), shaderType=GL.GL_FRAGMENT_SHADER),
        )

    def get_hmd_matrix_projection_eye(self, eye):
        if not self.hmd:
            return numpy.identity(4, dtype=numpy.float32)
        mat = self.hmd.getProjectionMatrix(eEye=eye, fNearZ=0.1, fFarZ=30.0)
        return numpy.array(mat, dtype=numpy.float32).T

    def get_hmd_matrix_pose_eye(self, eye):
        if not self.hmd:
            return numpy.identity(4, dtype=numpy.float32)
        mat = self.hmd.getEyeToHeadTransform(eye)
        return numpy.array((
            (mat[0][0], mat[1][0], mat[2][0], 0.0),
            (mat[0][1], mat[1][1], mat[2][1], 0.0),
            (mat[0][2], mat[1][2], mat[2][2], 0.0),
            (mat[0][3], mat[1][3], mat[2][3], 1.0),
        ), dtype=numpy.float32)

    def run_main_loop(self):
        while not glfw.window_should_close(self.window):
            glfw.swap_buffers(self.window)
            glfw.poll_events()

    def set_up_cameras(self):
        self.proj_left = self.get_hmd_matrix_projection_eye(eye=openvr.Eye_Left)
        self.proj_right = self.get_hmd_matrix_projection_eye(eye=openvr.Eye_Right)
        self.pos_left = self.get_hmd_matrix_pose_eye(eye=openvr.Eye_Left)
        self.pos_right = self.get_hmd_matrix_pose_eye(eye=openvr.Eye_Right)

    def set_up_scene(self):
        self.vertex_data = []
        v = self.scene_volume_init
        s = self.scale_spacing
        mat_scale = numpy.diag(numpy.array([v, v, v, 1], dtype=numpy.float32))
        t = -0.5 * v * s
        mat = mat_scale @ translate(t, t, t)
        for z in range(v):
            for y in range(v):
                for x in range(v):
                    self.add_cube_to_scene(mat)
                    mat = mat @ translate(s, 0, 0)
                mat = mat @ translate(-v * s, s, 0)
            mat = mat @ translate(0, -v * s, s)
        vertex_data = numpy.array(self.vertex_data, dtype=numpy.float32)
        self.vert_count = len(vertex_data) / 5
        self.scene_vao = GL.glGenVertexArrays(1)
        GL.glBindVertexArray(self.scene_vao)
        self.scene_vert_buffer = GL.glGenBuffers(1)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.scene_vert_buffer)
        GL.glBufferData(GL.GL_ARRAY_BUFFER, vertex_data, GL.GL_STATIC_DRAW)
        f_size = sizeof(c_float)
        stride = 5 * f_size
        GL.glEnableVertexAttribArray(0)
        GL.glVertexAttribPointer(0, 3, GL.GL_FLOAT, False, stride, cast(0 * f_size, c_void_p))
        GL.glEnableVertexAttribArray(1)
        GL.glVertexAttribPointer(1, 2, GL.GL_FLOAT, False, stride, cast(3 * f_size, c_void_p))
        GL.glBindVertexArray(0)
        GL.glDisableVertexAttribArray(0)
        GL.glDisableVertexAttribArray(1)

    def set_up_companion_window(self):
        if not self.hmd:
            return
        verts = list()
        # left eye verts
        verts.append( ( (-1, -1), (0, 1)) )
        verts.append( ( (0, -1), (1, 1)) )
        verts.append( ( (-1, 1), (0, 0)) )
        verts.append( ( (0, 1), (1, 0)) )
        # right eye verts
        verts.append( ( (0, -1), (0, 1)) )
        verts.append( ( (1, -1), (1, 1)) )
        verts.append( ( (0, 1), (0, 0)) )
        verts.append( ( (1, 1), (1, 0)) )
        vIndices = numpy.array([0, 1, 3,   0, 3, 2,   4, 5, 7,   4, 7, 6], dtype=numpy.uint8)
        self.companion_window_index_size = len(vIndices)
        self.companion_window_vao = GL.glGenVertexArrays(1)
        GL.glBindVertexArray(self.companion_window_vao)
        #
        self.companion_window_id_vert_buffer = GL.glGenBuffers(1)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.companion_window_id_vert_buffer)
        vVerts = numpy.array(verts, dtype=numpy.float32)
        GL.glBufferData(GL.GL_ARRAY_BUFFER, vVerts, GL.GL_STATIC_DRAW)
        #
        self.companion_window_id_index_buffer = GL.glGenBuffers(1)
        GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, self.companion_window_id_index_buffer)
        GL.glBufferData(GL.GL_ELEMENT_ARRAY_BUFFER, vIndices, GL.GL_STATIC_DRAW)
        #
        f_size = sizeof(c_float)
        GL.glEnableVertexAttribArray(0)
        GL.glVertexAttribPointer(0, 2, GL.GL_FLOAT, False, 4*f_size, cast(0 * f_size, c_void_p))
        #
        GL.glEnableVertexAttribArray(1)
        GL.glVertexAttribPointer(1, 2, GL.GL_FLOAT, False, 4**f_size, cast(2 * f_size, c_void_p))
        #
        GL.glBindVertexArray(0)
        GL.glDisableVertexAttribArray(0)
        GL.glDisableVertexAttribArray(1)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, 0)
        GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, 0)

    def set_up_texture_maps(self):
        ts = pkg_resources.resource_stream('samples', 'cube_texture.png')
        image = Image.open(ts).convert('RGBA')
        width, height = image.size
        image_data = numpy.array(list(image.getdata()), numpy.uint8)
        self.i_texture = GL.glGenTextures(1)
        GL.glBindTexture(GL.GL_TEXTURE_2D, self.i_texture)
        GL.glTexImage2D(
            GL.GL_TEXTURE_2D,
            0,
            GL.GL_RGBA,
            width, height,
            0,
            GL.GL_RGBA,
            GL.GL_UNSIGNED_BYTE,
            image_data,
        )
        GL.glGenerateMipmap(GL.GL_TEXTURE_2D)
        GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_WRAP_S, GL.GL_CLAMP_TO_EDGE)
        GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_WRAP_T, GL.GL_CLAMP_TO_EDGE)
        GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MAG_FILTER, GL.GL_LINEAR)
        GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MIN_FILTER, GL.GL_LINEAR_MIPMAP_LINEAR)
        f_largest = GL.glGetFloatv(GL_MAX_TEXTURE_MAX_ANISOTROPY_EXT)
        GL.glTexParameterf(GL.GL_TEXTURE_2D, GL_TEXTURE_MAX_ANISOTROPY_EXT, f_largest)
        GL.glBindTexture(GL.GL_TEXTURE_2D, 0)

    def set_up_stereo_render_targets(self):
        if not self.hmd:
            return False
        self.render_width, self.render_height = self.hmd.getRecommendedRenderTargetSize()
        self.left_eye_desc = FramebufferDesc(self.render_width, self.render_height)
        self.right_eye_desc = FramebufferDesc(self.render_width, self.render_height)

    def shut_down(self):
        glfw.terminate()


class ControllerInfo(object):
    def __init__(self):
        self.source = openvr.k_ulInvalidInputValueHandle
        self.action_pose = openvr.k_ulInvalidActionHandle
        self.action_haptic = openvr.k_ulInvalidActionHandle
        self.pose = numpy.identity(4, dtype=numpy.float32)
        self.render_model = None
        self.render_model_name = ''
        self.show_controller = False


class FramebufferDesc(object):
    def __init__(self, width, height):
        self.render_framebuffer_id = GL.glGenFramebuffers(1)
        GL.glBindFramebuffer(GL.GL_FRAMEBUFFER, self.render_framebuffer_id)
        # 
        self.depth_buffer_id = GL.glGenRenderbuffers(1)
        GL.glBindRenderbuffer(GL.GL_RENDERBUFFER, self.depth_buffer_id)
        GL.glRenderbufferStorageMultisample(GL.GL_RENDERBUFFER, 4, GL.GL_DEPTH_COMPONENT, width, height)
        GL.glFramebufferRenderbuffer(GL.GL_FRAMEBUFFER, GL.GL_DEPTH_ATTACHMENT, GL.GL_RENDERBUFFER, self.depth_buffer_id)
        #
        self.render_texture_id = GL.glGenTextures(1)
        GL.glBindTexture(GL.GL_TEXTURE_2D_MULTISAMPLE, self.render_texture_id)
        GL.glTexImage2DMultisample(GL.GL_TEXTURE_2D_MULTISAMPLE, 4, GL.GL_RGBA8, width, height, True)
        GL.glFramebufferTexture2D(GL.GL_FRAMEBUFFER, GL.GL_COLOR_ATTACHMENT0, GL.GL_TEXTURE_2D_MULTISAMPLE, self.render_texture_id, 0)
        #
        self.resolve_framebuffer_id = GL.glGenFramebuffers(1)
        GL.glBindFramebuffer(GL.GL_FRAMEBUFFER, self.resolve_framebuffer_id)
        #
        self.resolve_texture_id = GL.glGenTextures(1)
        GL.glBindTexture(GL.GL_TEXTURE_2D, self.resolve_texture_id)
        GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MIN_FILTER, GL.GL_LINEAR)
        GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MAX_LEVEL, 0)
        GL.glTexImage2D(GL.GL_TEXTURE_2D, 0, GL.GL_RGBA8, width, height, 0, GL.GL_RGBA, GL.GL_UNSIGNED_BYTE, None)
        GL.glFramebufferTexture2D(GL.GL_FRAMEBUFFER, GL.GL_COLOR_ATTACHMENT0, GL.GL_TEXTURE_2D, self.resolve_texture_id, 0)
        status = GL.glCheckFramebufferStatus(GL.GL_FRAMEBUFFER)
        assert status == GL.GL_FRAMEBUFFER_COMPLETE


def main(argv):
    print('Hello')
    main_application = CMainApplication(argv)
    if main_application.b_init():
        main_application.run_main_loop()
    main_application.shut_down()
    return 0


def translate(x, y, z):
    return numpy.array([
        [1, 0, 0, x],
        [0, 1, 0, y],
        [0, 0, 1, z],
        [0, 0, 0, 1],
    ], dtype=numpy.float32)


if __name__ == '__main__':
    sys.exit(main(sys.argv))
