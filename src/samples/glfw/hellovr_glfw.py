#!/usr/bin/env python

# Core python modules
from ctypes import c_float, c_uint16, c_void_p, cast, sizeof
import inspect
import pkg_resources
import sys
import time

# Third party modules
import glfw
import numpy
from numpy.linalg import inv
from OpenGL import GL
from OpenGL.GL import shaders
from OpenGL.GL.EXT.texture_filter_anisotropic import GL_MAX_TEXTURE_MAX_ANISOTROPY_EXT, GL_TEXTURE_MAX_ANISOTROPY_EXT
from PIL import Image

# Local modules
import openvr

Left = 0
Right = 1


class CGLRenderModel(object):
    def __init__(self, name, vr_model, vr_diffuse_texture):
        self.name = name
        # create and bind a VAO to hold state for this model
        self.vertex_array = GL.glGenVertexArrays(1)
        GL.glBindVertexArray(self.vertex_array)
        # Populate a vertex buffer
        self.vertex_buffer = GL.glGenBuffers(1)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.vertex_buffer)
        GL.glBufferData(GL.GL_ARRAY_BUFFER,
                        sizeof(openvr.RenderModel_Vertex_t) * vr_model.unVertexCount,
                        vr_model.rVertexData, GL.GL_STATIC_DRAW)
        # Identify the components in the vertex buffer
        GL.glEnableVertexAttribArray(0)
        hv3sz = sizeof(openvr.HmdVector3_t)
        GL.glVertexAttribPointer(0, 3, GL.GL_FLOAT, False, sizeof(openvr.RenderModel_Vertex_t),
                                 cast(0 * hv3sz, c_void_p))
        GL.glEnableVertexAttribArray(1)
        GL.glVertexAttribPointer(1, 3, GL.GL_FLOAT, False, sizeof(openvr.RenderModel_Vertex_t),
                                 cast(1 * hv3sz, c_void_p))
        GL.glEnableVertexAttribArray(2)
        GL.glVertexAttribPointer(2, 2, GL.GL_FLOAT, False, sizeof(openvr.RenderModel_Vertex_t),
                                 cast(2 * hv3sz, c_void_p))
        # Create and populate the index buffer
        self.index_buffer = GL.glGenBuffers(1)
        GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, self.index_buffer)
        GL.glBufferData(GL.GL_ELEMENT_ARRAY_BUFFER,
                        sizeof(c_uint16) * vr_model.unTriangleCount * 3,
                        vr_model.rIndexData, GL.GL_STATIC_DRAW)
        GL.glBindVertexArray(0)
        # create and populate the texture
        self.texture = GL.glGenTextures(1)
        GL.glBindTexture(GL.GL_TEXTURE_2D, self.texture)
        GL.glTexImage2D(GL.GL_TEXTURE_2D, 0, GL.GL_RGBA, vr_diffuse_texture.unWidth, vr_diffuse_texture.unHeight,
                        0, GL.GL_RGBA, GL.GL_UNSIGNED_BYTE, vr_diffuse_texture.rubTextureMapData)
        # If this renders black ask McJohn what's wrong.
        GL.glGenerateMipmap(GL.GL_TEXTURE_2D)
        GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_WRAP_S, GL.GL_CLAMP_TO_EDGE)
        GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_WRAP_T, GL.GL_CLAMP_TO_EDGE)
        GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MAG_FILTER, GL.GL_LINEAR)
        GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MIN_FILTER, GL.GL_LINEAR_MIPMAP_LINEAR)
        f_largest = GL.glGetFloatv(GL_MAX_TEXTURE_MAX_ANISOTROPY_EXT)
        GL.glTexParameterf(GL.GL_TEXTURE_2D, GL_TEXTURE_MAX_ANISOTROPY_EXT, f_largest)
        GL.glBindTexture(GL.GL_TEXTURE_2D, 0)
        self.vertex_count = vr_model.unTriangleCount * 3

    def cleanup(self):
        GL.glDeleteBuffers(1, [self.index_buffer])
        GL.glDeleteVertexArrays(1, [self.vertex_array])
        GL.glDeleteBuffers(1, [self.vertex_buffer])
        self.index_buffer = None
        self.vertex_array = None
        self.vertex_buffer = None

    def draw(self):
        GL.glBindVertexArray(self.vertex_array)
        GL.glActiveTexture(GL.GL_TEXTURE0)
        GL.glBindTexture(GL.GL_TEXTURE_2D, self.texture)
        GL.glDrawElements(GL.GL_TRIANGLES, self.vertex_count, GL.GL_UNSIGNED_SHORT, None)
        GL.glBindVertexArray(0)


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
        self.render_models = dict()
        self.controller_vao = None
        self.poses = []
        self.hmd_pose = None
        self.tracked_controller_count_previous = -1
        self.tracked_controller_count = 0
        self.valid_pose_count = 0
        self.valid_pose_count_previous = -1
        self.show_cubes = True
        self.analog_value = [0, 0]
        self.pose_classes = ''
        self.dev_class_char = dict()
        self.companion_width = 640
        self.companion_height = 320
        self.controller_vertex_count = 0
        self.controller_vertex_buffer = None

    def add_cube_to_scene(self, matrix):
        A = (0, 0, 0, 1) @ matrix
        B = (1, 0, 0, 1) @ matrix
        C = (1, 1, 0, 1) @ matrix
        D = (0, 1, 0, 1) @ matrix
        E = (0, 0, 1, 1) @ matrix
        F = (1, 0, 1, 1) @ matrix
        G = (1, 1, 1, 1) @ matrix
        H = (0, 1, 1, 1) @ matrix
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
        self.window = glfw.create_window(self.companion_width, self.companion_height, 'hello_vr', None, None)
        glfw.set_key_callback(self.window, self.key_callback)
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
                uniform sampler2D myTexture;
                in vec2 v2UVcoords;
                out vec4 outputColor;
                void main()
                {
                    outputColor = texture(myTexture, v2UVcoords);
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
                uniform sampler2D myTexture;
                noperspective in vec2 v2UV;
                out vec4 outputColor;
                void main()
                {
                    outputColor = texture(myTexture, v2UV);
                }
            '''), shaderType=GL.GL_FRAGMENT_SHADER),
        )

    def find_or_load_render_model(self, render_model_name):
        if render_model_name in self.render_models:
            return self.render_models[render_model_name]
        while True:
            try:
                model = openvr.VRRenderModels().loadRenderModel_Async(render_model_name)
                break
            except openvr.error_code.RenderModelError_Loading:
                time.sleep(1)
        while True:
            try:
                texture = openvr.VRRenderModels().loadTexture_Async(model.diffuseTextureId)
                break
            except openvr.error_code.RenderModelError_Loading:
                time.sleep(1)
        render_model = CGLRenderModel(render_model_name, model, texture)
        self.render_models[render_model_name] = render_model
        openvr.VRRenderModels().freeRenderModel(model)
        openvr.VRRenderModels().freeTexture(texture)
        return render_model

    def get_current_view_projection_matrix(self, eye):
        hmd_pose = numpy.identity(4, dtype=numpy.float32)
        if self.hmd_pose is not None:
            hmd_pose = self.hmd_pose
        if eye == openvr.Eye_Left:
            mvp = hmd_pose @ self.pos_left @ self.proj_left
        else:
            mvp = hmd_pose @ self.pos_right @ self.proj_right
        return mvp

    def get_hmd_matrix_projection_eye(self, eye):
        if not self.hmd:
            return numpy.identity(4, dtype=numpy.float32)
        mat = self.hmd.getProjectionMatrix(eye=eye, nearZ=0.1, farZ=30.0)
        mat = numpy.array((
            (mat[0][0], mat[1][0], mat[2][0], mat[3][0]),
            (mat[0][1], mat[1][1], mat[2][1], mat[3][1]),
            (mat[0][2], mat[1][2], mat[2][2], mat[3][2]),
            (mat[0][3], mat[1][3], mat[2][3], mat[3][3]),
        ), dtype=numpy.float32)
        return mat

    def get_hmd_matrix_pose_eye(self, eye):
        if not self.hmd:
            return numpy.identity(4, dtype=numpy.float32)
        mat = self.hmd.getEyeToHeadTransform(eye)
        mat = numpy.array((
            (mat[0][0], mat[1][0], mat[2][0], 0.0),
            (mat[0][1], mat[1][1], mat[2][1], 0.0),
            (mat[0][2], mat[1][2], mat[2][2], 0.0),
            (mat[0][3], mat[1][3], mat[2][3], 1.0),
        ), dtype=numpy.float32)
        return inv(mat)

    def handle_input(self):
        # Note: Key events are handled by glfw in key_callback
        # Process SteamVR events
        event = openvr.VREvent_t()
        has_events = True
        while has_events:
            has_events = self.hmd.pollNextEvent(event)
            self.process_vr_event(event)
        # Process SteamVR action state
        # UpdateActionState is called each frame to update the state of the actions themselves. The application
        # controls which action sets are active with the provided array of VRActiveActionSet_t structs.
        action_sets = (openvr.VRActiveActionSet_t * 1)()
        action_set = action_sets[0]
        action_set.ulActionSet = self.action_set_demo
        openvr.VRInput().updateActionState(action_sets)
        #
        self.show_cubes = not get_digital_action_state(self.action_hide_cubes)[0]
        #
        bH, haptic_device = get_digital_action_rising_edge(self.action_trigger_haptic, True)
        if bH:
            for hand in self.hand:
                if haptic_device == hand.source:
                    openvr.VRInput().triggerHapticVibrationAction(hand.action_haptic, 0, 1, 4, 1, openvr.k_ulInvalidInputValueHandle)
        analog_data = openvr.VRInput().getAnalogActionData(self.action_analog_input, openvr.k_ulInvalidInputValueHandle)
        self.analog_value[0] = analog_data.x
        self.analog_value[1] = analog_data.y  # TODO: these seem to be unused...
        self.hand[Left].show_controller = True
        self.hand[Right].show_controller = True
        do_hide, hide_device = get_digital_action_state(self.action_hide_this_controller, True)
        if do_hide:
            for hand in self.hand:
                if hide_device == hand.source:
                    hand.show_controller = False
        for hand in self.hand:
            pose_data = openvr.VRInput().getPoseActionDataForNextFrame(
                hand.action_pose,
                openvr.TrackingUniverseStanding,
                openvr.k_ulInvalidInputValueHandle,
            )
            if not pose_data.bActive:
                hand.show_controller = False
                continue
            if not pose_data.pose.bPoseIsValid:
                hand.show_controller = False
                continue
            hand.pose = convert_steam_vr_matrix(pose_data.pose.mDeviceToAbsoluteTracking)
            origin_info = openvr.VRInput().getOriginTrackedDeviceInfo(
                pose_data.activeOrigin,
            )
            if origin_info.trackedDeviceIndex != openvr.k_unTrackedDeviceIndexInvalid:
                render_model_name = openvr.VRSystem().getStringTrackedDeviceProperty(
                    origin_info.trackedDeviceIndex,
                    openvr.Prop_RenderModelName_String
                )
                hand.render_model = self.find_or_load_render_model(render_model_name)
                hand.render_model_name = render_model_name

    def key_callback(self, window, key, _scan_code, action, _mods):
        if action == glfw.PRESS:
            if key == glfw.KEY_ESCAPE:
                glfw.set_window_should_close(window, True)
            if key == glfw.KEY_C:
                self.show_cubes = not self.show_cubes

    def process_vr_event(self, event):
        if event.eventType == openvr.VREvent_TrackedDeviceDeactivated:
            print(f'Device {event.trackedDeviceIndex} detached')
        elif event.eventType == openvr.VREvent_TrackedDeviceUpdated:
            print(f'Device {event.trackedDeviceIndex} updated')

    def render_companion_window(self):
        GL.glDisable(GL.GL_DEPTH_TEST)
        GL.glViewport(0, 0, self.companion_width, self.companion_height)
        GL.glBindVertexArray(self.companion_window_vao)
        GL.glUseProgram(self.companion_window_program)
        # render left eye (first half of index array)
        i_size = sizeof(c_uint16)
        count = int(self.companion_window_index_size / 2)
        GL.glBindTexture(GL.GL_TEXTURE_2D, self.left_eye_desc.resolve_texture_id)
        GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_WRAP_S, GL.GL_CLAMP_TO_EDGE)
        GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_WRAP_T, GL.GL_CLAMP_TO_EDGE)
        GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MAG_FILTER, GL.GL_LINEAR)
        GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MIN_FILTER, GL.GL_LINEAR)
        GL.glDrawElements(GL.GL_TRIANGLES, count, GL.GL_UNSIGNED_SHORT, cast(0 * i_size, c_void_p))
        # render right eye (second half of index array)
        GL.glBindTexture(GL.GL_TEXTURE_2D, self.right_eye_desc.resolve_texture_id)
        GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_WRAP_S, GL.GL_CLAMP_TO_EDGE)
        GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_WRAP_T, GL.GL_CLAMP_TO_EDGE)
        GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MAG_FILTER, GL.GL_LINEAR)
        GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MIN_FILTER, GL.GL_LINEAR)
        GL.glDrawElements(GL.GL_TRIANGLES, count, GL.GL_UNSIGNED_SHORT, cast(count * i_size, c_void_p))
        GL.glBindVertexArray(0)
        GL.glUseProgram(0)

    def render_controller_axes(self):
        """
        Purpose: Draw all of the controllers as X/Y/Z lines
        """
        # Don't attempt to update controllers if input is not available
        if not self.hmd.isInputAvailable():
            return
        vertex_data_array = list()
        self.controller_vertex_count = 0
        self.tracked_controller_count = 0
        for hand in self.hand:
            if not hand.show_controller:
                continue
            mat = hand.pose
            center = (0, 0, 0, 1) @ mat
            for i in range(3):
                color = [0, 0, 0]
                point = [0, 0, 0, 1]
                point[i] += 0.05
                color[i] = 1.0
                point = point @ mat
                vertex_data_array.append(center[0])
                vertex_data_array.append(center[1])
                vertex_data_array.append(center[2])
                vertex_data_array.append(color[0])
                vertex_data_array.append(color[1])
                vertex_data_array.append(color[2])
                vertex_data_array.append(point[0])
                vertex_data_array.append(point[1])
                vertex_data_array.append(point[2])
                vertex_data_array.append(color[0])
                vertex_data_array.append(color[1])
                vertex_data_array.append(color[2])
                self.controller_vertex_count += 2
            start = (0, 0, -0.02, 1) @ mat
            end = (0, 0, -39, 1) @ mat
            color = (.92, .92, .71)
            vertex_data_array.append(start[0])
            vertex_data_array.append(start[1])
            vertex_data_array.append(start[2])
            vertex_data_array.append(color[0])
            vertex_data_array.append(color[1])
            vertex_data_array.append(color[2])
            vertex_data_array.append(end[0])
            vertex_data_array.append(end[1])
            vertex_data_array.append(end[2])
            vertex_data_array.append(color[0])
            vertex_data_array.append(color[1])
            vertex_data_array.append(color[2])
            self.controller_vertex_count += 2
        vertex_data_array = numpy.array(vertex_data_array, dtype=numpy.float32)
        # Setup the VAO the first time through.
        if self.controller_vao is None:
            self.controller_vao = GL.glGenVertexArrays(1)
            GL.glBindVertexArray(self.controller_vao)
            self.controller_vertex_buffer = GL.glGenBuffers(1)
            GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.controller_vertex_buffer)
            stride = 2 * 3 * sizeof(c_float)
            offset = 0
            GL.glEnableVertexAttribArray(0)
            GL.glVertexAttribPointer(0, 3, GL.GL_FLOAT, False, stride, cast(offset, c_void_p))
            offset += 3 * sizeof(c_float)
            GL.glEnableVertexAttribArray(1)
            GL.glVertexAttribPointer(1, 3, GL.GL_FLOAT, False, stride, cast(offset, c_void_p))
            GL.glBindVertexArray(0)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.controller_vertex_buffer)
        # set vertex data if we have some
        if len(vertex_data_array) > 0:
            GL.glBufferData(GL.GL_ARRAY_BUFFER, vertex_data_array, GL.GL_STREAM_DRAW)

    def render_frame(self):
        if self.hmd:
            self.render_controller_axes()
            self.render_stereo_targets()
            self.render_companion_window()
            left_eye_texture = openvr.Texture_t(
                handle=self.left_eye_desc.resolve_texture_id,
                eType=openvr.TextureType_OpenGL,
                eColorSpace=openvr.ColorSpace_Gamma,
            )
            right_eye_texture = openvr.Texture_t(
                handle=self.right_eye_desc.resolve_texture_id,
                eType=openvr.TextureType_OpenGL,
                eColorSpace=openvr.ColorSpace_Gamma,
            )
            try:
                openvr.VRCompositor().submit(openvr.Eye_Left, left_eye_texture)
                openvr.VRCompositor().submit(openvr.Eye_Right, right_eye_texture)
            except openvr.error_code.CompositorError_DoNotHaveFocus:
                pass  # First frame fails because waitGetPoses has not been called yet

        if (self.tracked_controller_count != self.tracked_controller_count_previous
                or self.valid_pose_count != self.valid_pose_count_previous):
            self.valid_pose_count_previous = self.valid_pose_count
            self.tracked_controller_count_previous = self.tracked_controller_count
            print(f'PoseCount:{self.valid_pose_count}({self.pose_classes}) Controllers:{self.tracked_controller_count}')
        self.update_hmd_pose()

    def render_stereo_targets(self):
        GL.glClearColor(0, 0, 0, 1)
        GL.glEnable(GL.GL_MULTISAMPLE)
        # Left Eye
        GL.glBindFramebuffer(GL.GL_FRAMEBUFFER, self.left_eye_desc.render_framebuffer_id)
        GL.glViewport(0, 0, self.render_width, self.render_height)
        self.render_scene(openvr.Eye_Left)
        GL.glBindFramebuffer(GL.GL_FRAMEBUFFER, 0)
        GL.glDisable(GL.GL_MULTISAMPLE)
        GL.glBindFramebuffer(GL.GL_READ_FRAMEBUFFER, self.left_eye_desc.render_framebuffer_id)
        GL.glBindFramebuffer(GL.GL_DRAW_FRAMEBUFFER, self.left_eye_desc.resolve_framebuffer_id)
        GL.glBlitFramebuffer(
            0, 0, self.render_width, self.render_height,
            0, 0, self.render_width, self.render_height,
            GL.GL_COLOR_BUFFER_BIT, GL.GL_LINEAR)
        GL.glBindFramebuffer(GL.GL_READ_FRAMEBUFFER, 0)
        GL.glBindFramebuffer(GL.GL_DRAW_FRAMEBUFFER, 0)
        # Right Eye
        GL.glEnable(GL.GL_MULTISAMPLE)
        GL.glBindFramebuffer(GL.GL_FRAMEBUFFER, self.right_eye_desc.render_framebuffer_id)
        GL.glViewport(0, 0, self.render_width, self.render_height)
        self.render_scene(openvr.Eye_Right)
        GL.glBindFramebuffer(GL.GL_FRAMEBUFFER, 0)
        GL.glDisable(GL.GL_MULTISAMPLE)
        GL.glBindFramebuffer(GL.GL_READ_FRAMEBUFFER, self.right_eye_desc.render_framebuffer_id)
        GL.glBindFramebuffer(GL.GL_DRAW_FRAMEBUFFER, self.right_eye_desc.resolve_framebuffer_id)
        GL.glBlitFramebuffer(
            0, 0, self.render_width, self.render_height,
            0, 0, self.render_width, self.render_height,
            GL.GL_COLOR_BUFFER_BIT, GL.GL_LINEAR)
        GL.glBindFramebuffer(GL.GL_READ_FRAMEBUFFER, 0)
        GL.glBindFramebuffer(GL.GL_DRAW_FRAMEBUFFER, 0)

    def render_scene(self, eye):
        GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)
        GL.glEnable(GL.GL_DEPTH_TEST)
        if self.show_cubes:
            GL.glUseProgram(self.scene_program)
            GL.glUniformMatrix4fv(
                self.scene_matrix_location, 1, False,
                self.get_current_view_projection_matrix(eye))
            GL.glBindVertexArray(self.scene_vao)
            GL.glBindTexture(GL.GL_TEXTURE_2D, self.i_texture)
            GL.glDrawArrays(GL.GL_TRIANGLES, 0, int(self.vert_count))
            GL.glBindVertexArray(0)
        b_is_input_available = self.hmd.isInputAvailable()
        if b_is_input_available:
            # draw the controller axis lines
            GL.glUseProgram(self.controller_transform_program)
            GL.glUniformMatrix4fv(self.controller_matrix_location, 1, False, self.get_current_view_projection_matrix(eye))
            GL.glBindVertexArray(self.controller_vao)
            GL.glDrawArrays(GL.GL_LINES, 0, self.controller_vertex_count)
            GL.glBindVertexArray(0)
        # ----- Render Model rendering -----
        GL.glUseProgram(self.render_model_program)
        for hand in self.hand:
            if not hand.show_controller:
                continue
            if hand.render_model is None:
                continue
            mvp = hand.pose @ self.get_current_view_projection_matrix(eye)
            GL.glUniformMatrix4fv(self.render_model_matrix_location, 1, False, mvp)
            hand.render_model.draw()
        GL.glUseProgram(0)

    def run_main_loop(self):
        while not glfw.window_should_close(self.window):
            self.handle_input()
            self.render_frame()
            glfw.swap_buffers(self.window)
            GL.glClearColor(0, 0, 0, 1)
            GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)
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
        scale = 0.3
        mat_scale = numpy.diag(numpy.array([scale, scale, scale, 1], dtype=numpy.float32))
        t = -0.5 * v * s
        mat_translate = translate(t, t, t)
        mat = mat_translate @ mat_scale
        for z in range(v):
            for y in range(v):
                for x in range(v):
                    self.add_cube_to_scene(mat)
                    mat = translate(s, 0, 0) @ mat
                mat = translate(-v * s, s, 0) @ mat
            mat = translate(0, -v * s, s) @ mat
        vertex_data = numpy.array(self.vertex_data, dtype=numpy.float32).flatten()
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
        verts.append(((-1, -1), (0, 0)))
        verts.append(((0, -1), (1, 0)))
        verts.append(((-1, 1), (0, 1)))
        verts.append(((0, 1), (1, 1)))
        # right eye verts
        verts.append(((0, -1), (0, 0)))
        verts.append(((1, -1), (1, 0)))
        verts.append(((0, 1), (0, 1)))
        verts.append(((1, 1), (1, 1)))
        vIndices = numpy.array([0, 1, 3, 0, 3, 2, 4, 5, 7, 4, 7, 6], dtype=numpy.uint16)
        self.companion_window_index_size = len(vIndices)
        self.companion_window_vao = GL.glGenVertexArrays(1)
        GL.glBindVertexArray(self.companion_window_vao)
        #
        self.companion_window_id_vert_buffer = GL.glGenBuffers(1)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.companion_window_id_vert_buffer)
        vVerts = numpy.array(verts, dtype=numpy.float32).flatten()
        GL.glBufferData(GL.GL_ARRAY_BUFFER, vVerts, GL.GL_STATIC_DRAW)
        #
        self.companion_window_id_index_buffer = GL.glGenBuffers(1)
        GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, self.companion_window_id_index_buffer)
        GL.glBufferData(GL.GL_ELEMENT_ARRAY_BUFFER, vIndices, GL.GL_STATIC_DRAW)
        #
        f_size = sizeof(c_float)
        GL.glEnableVertexAttribArray(0)
        GL.glVertexAttribPointer(0, 2, GL.GL_FLOAT, False, 4 * f_size, cast(0 * f_size, c_void_p))
        #
        GL.glEnableVertexAttribArray(1)
        GL.glVertexAttribPointer(1, 2, GL.GL_FLOAT, False, 4 * f_size, cast(2 * f_size, c_void_p))
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
        if self.hmd:
            openvr.shutdown()
            self.hmd = None
        self.render_models = dict()
        if self.scene_vert_buffer:
            GL.glDeleteBuffers(1, [self.scene_vert_buffer])
            self.scene_vert_buffer = None
            self.left_eye_desc.delete()
            self.right_eye_desc.delete()
            if self.companion_window_vao:
                GL.glDeleteVertexArrays(1, [self.companion_window_vao])
                self.companion_window_vao = None
            if self.scene_vao:
                GL.glDeleteVertexArrays(1, [self.scene_vao])
                self.scene_vao = None
            if self.controller_vao:
                GL.glDeleteVertexArrays(1, [self.controller_vao])
                self.controller_vao = None
        glfw.terminate()

    def update_hmd_pose(self):
        if not self.hmd:
            return
        self.poses, _ = openvr.VRCompositor().waitGetPoses(self.poses, None)
        self.valid_pose_count = 0
        self.pose_classes = ''
        for nDevice, pose in enumerate(self.poses):
            if pose.bPoseIsValid:
                self.valid_pose_count += 1
                if nDevice not in self.dev_class_char:
                    c = self.hmd.getTrackedDeviceClass(nDevice)
                    if c == openvr.TrackedDeviceClass_Controller:
                        self.dev_class_char[nDevice] = 'C'
                    elif c == openvr.TrackedDeviceClass_HMD:
                        self.dev_class_char[nDevice] = 'H'
                    elif c == openvr.TrackedDeviceClass_Invalid:
                        self.dev_class_char[nDevice] = 'I'
                    elif c == openvr.TrackedDeviceClass_GenericTracker:
                        self.dev_class_char[nDevice] = 'G'
                    elif c == openvr.TrackedDeviceClass_TrackingReference:
                        self.dev_class_char[nDevice] = 'T'
                    else:
                        self.dev_class_char[nDevice] = '?'
                self.pose_classes += self.dev_class_char[nDevice]
        hp = self.poses[openvr.k_unTrackedDeviceIndex_Hmd]
        if hp.bPoseIsValid:
            p = convert_steam_vr_matrix(hp.mDeviceToAbsoluteTracking)
            self.hmd_pose = inv(p)


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
        GL.glFramebufferRenderbuffer(GL.GL_FRAMEBUFFER, GL.GL_DEPTH_ATTACHMENT, GL.GL_RENDERBUFFER,
                                     self.depth_buffer_id)
        #
        self.render_texture_id = GL.glGenTextures(1)
        GL.glBindTexture(GL.GL_TEXTURE_2D_MULTISAMPLE, self.render_texture_id)
        GL.glTexImage2DMultisample(GL.GL_TEXTURE_2D_MULTISAMPLE, 4, GL.GL_RGBA8, width, height, True)
        GL.glFramebufferTexture2D(GL.GL_FRAMEBUFFER, GL.GL_COLOR_ATTACHMENT0, GL.GL_TEXTURE_2D_MULTISAMPLE,
                                  self.render_texture_id, 0)
        #
        self.resolve_framebuffer_id = GL.glGenFramebuffers(1)
        GL.glBindFramebuffer(GL.GL_FRAMEBUFFER, self.resolve_framebuffer_id)
        #
        self.resolve_texture_id = GL.glGenTextures(1)
        GL.glBindTexture(GL.GL_TEXTURE_2D, self.resolve_texture_id)
        GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MIN_FILTER, GL.GL_LINEAR)
        GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MAX_LEVEL, 0)
        GL.glTexImage2D(GL.GL_TEXTURE_2D, 0, GL.GL_RGBA8, width, height, 0, GL.GL_RGBA, GL.GL_UNSIGNED_BYTE, None)
        GL.glFramebufferTexture2D(GL.GL_FRAMEBUFFER, GL.GL_COLOR_ATTACHMENT0, GL.GL_TEXTURE_2D, self.resolve_texture_id,
                                  0)
        status = GL.glCheckFramebufferStatus(GL.GL_FRAMEBUFFER)
        assert status == GL.GL_FRAMEBUFFER_COMPLETE

    def delete(self):
        GL.glDeleteRenderbuffers(1, [self.depth_buffer_id])
        self.depth_buffer_id = None
        GL.glDeleteTextures(self.render_texture_id)
        self.render_texture_id = None
        GL.glDeleteFramebuffers(1, [self.render_framebuffer_id])
        self.render_framebuffer_id = None
        GL.glDeleteTextures(self.resolve_texture_id)
        self.resolve_texture_id = None
        GL.glDeleteFramebuffers(1, [self.resolve_framebuffer_id])
        self.resolve_framebuffer_id = None


def convert_steam_vr_matrix(pose):
    return numpy.array((
        (pose[0][0], pose[1][0], pose[2][0], 0.0),
        (pose[0][1], pose[1][1], pose[2][1], 0.0),
        (pose[0][2], pose[1][2], pose[2][2], 0.0),
        (pose[0][3], pose[1][3], pose[2][3], 1.0),
    ), dtype=numpy.float32)


def get_digital_action_rising_edge(action, device_path=None):
    """
    Purpose: Returns true if the action is active and had a rising edge
    """
    action_data = openvr.VRInput().getDigitalActionData(action, openvr.k_ulInvalidInputValueHandle)
    if device_path is not None:
        if action_data.bActive:
            origin_info = openvr.VRInput().getOriginTrackedDeviceInfo(action_data.activeOrigin)
            device_path = origin_info.devicePath
    return action_data.bActive and action_data.bChanged and action_data.bState, device_path


def get_digital_action_falling_edge(action, device_path=None):
    """
    Purpose: Returns true if the action is active and had a falling edge
    """
    action_data = openvr.VRInput().getDigitalActionData(action, openvr.k_ulInvalidInputValueHandle)
    if device_path is not None:
        if action_data.bActive:
            origin_info = openvr.VRInput().getOriginTrackedDeviceInfo(action_data.activeOrigin)
            device_path = origin_info.devicePath
    return action_data.bActive and action_data.bChanged and not action_data.bState, device_path


def get_digital_action_state(action, device_path=None):
    """
    Purpose: Returns true if the action is active and its state is true
    """
    action_data = openvr.VRInput().getDigitalActionData(action, openvr.k_ulInvalidInputValueHandle)
    if device_path is not None:
        if action_data.bActive:
            origin_info = openvr.VRInput().getOriginTrackedDeviceInfo(action_data.activeOrigin)
            device_path = origin_info.devicePath
    return action_data.bActive and action_data.bState, device_path


def main(argv):
    main_application = CMainApplication(argv)
    if main_application.b_init():
        main_application.run_main_loop()
    main_application.shut_down()
    return 0


def translate(x, y, z):
    return numpy.array([
        [1, 0, 0, 0],
        [0, 1, 0, 0],
        [0, 0, 1, 0],
        [x, y, z, 1],
    ], dtype=numpy.float32)


if __name__ == '__main__':
    sys.exit(main(sys.argv))
