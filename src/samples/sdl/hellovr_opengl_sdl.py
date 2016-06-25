#!/bin/env python

# file: hello_vr_opengl_sdl.py
#
# OpenVR example application
# Manually translated from OpenVR C++ example file hellovr_opengl_main.cpp
# by Christopher Bruns
#
# NOTE -- This example does not yet work!!!
# Try hello_sdl2.py instead.

# Python standard library imports
import sys
import os
import time
from textwrap import dedent
import logging

# Third-party module imports
import Image
import ctypes  # @UnusedImport this comment silences eclipse warning
from ctypes import sizeof, byref # @UnusedImport
import numpy
from numpy.linalg import inv
from OpenGL.GL import *  # @UnusedWildImport
from OpenGL.GL.EXT.texture_filter_anisotropic import *  # @UnusedWildImport
from OpenGL.GL.ARB.debug_output import *  # @UnusedWildImport
from sdl2 import *  # @UnusedWildImport

# Local package imports
import openvr


# Configure logging to give similar functionality to C++ parent use of __FUNCTION__
logging.basicConfig(format="%(filename)s:%(funcName)s:%(message)s", level=logging.DEBUG, stream=sys.stderr)
g_bPrintf = True # Global variable affects logging via command-line option


class Vector2(ctypes.Structure):
    "Stand-in for a custom class from the C++ OpenVR example programs"
    
    _fields_ = [
        ("x", ctypes.c_float),
        ("y", ctypes.c_float),
    ]
    
    def __init__(self, vec=None):
        if vec is None:
            vec = [0.0,0.0]
        self.x = vec[0]
        self.y = vec[1]


class Vector3(ctypes.Structure):
    "Stand-in for a custom class from the C++ OpenVR example programs"
    
    _fields_ = [
        ("x", ctypes.c_float),
        ("y", ctypes.c_float),
        ("z", ctypes.c_float),
    ]
    
    def __init__(self, vec=None):
        if vec is None:
            vec = [0.0, 0.0, 0.0]
        self.x = vec[0]
        self.y = vec[1]
        self.z = vec[2]


class VertexDataScene(ctypes.Structure):
    _fields_ = [
        ("position", Vector3),
        ("texCoord", Vector2),
    ]
    
    def __init__(self, position, texCoord):
        self.position = position
        self.texCoord = texCoord

 
class VertexDataLens(ctypes.Structure):
    _fields_ = [
        ("position", Vector2),
        ("texCoordRed", Vector2),
        ("texCoordGreen", Vector2),
        ("texCoordBlue", Vector2),
    ]
    
    def __init__(self, position=Vector2(), texCoordRed=Vector2(), texCoordGreen=Vector2(), texCoordBlue=Vector2()):
        self.position = position
        self.texCoordRed = texCoordRed
        self.texCoordGreen = texCoordGreen
        self.texCoordBlue = texCoordBlue

    def as_floats(self):
        return [float(v) for v in [
                self.position.x,
                self.position.y,
                self.texCoordRed.x,
                self.texCoordRed.y,       
                self.texCoordGreen.x,
                self.texCoordGreen.y,       
                self.texCoordBlue.x,
                self.texCoordBlue.y]]

class Vector4(numpy.ndarray):
    "Stand-in for a custom class from the C++ OpenVR example programs"
    
    def __new__(cls, data=None):
        if data is None: # use identity with empty constructor
            data = [0,0,0,0]
        obj = numpy.ndarray.__new__(cls, shape=(4,1), dtype=numpy.float32)
        obj[:,0] = data[:]
        return obj
    
    def getx(self):
        return self[0,0]
    def setx(self, val):
        self[0,0] = val
    x = property(getx, setx)

    def gety(self):
        return self[1,0]
    def sety(self, val):
        self[1,0] = val
    y = property(gety, sety)

    def getz(self):
        return self[2,0]
    def setz(self, val):
        self[2,0] = val
    z = property(getz, setz)

    def getw(self):
        return self[3,0]
    def setw(self, val):
        self[3,0] = val
    w = property(getw, setw)


class Matrix4(numpy.matrix):
    """
    Stand-in for a custom class from the C++ OpenVR example programs
    """
    
    def __new__(cls, data=None):
        if data is None: # use identity with empty constructor
            data = numpy.identity(4, numpy.float32)
        obj = numpy.matrix.__new__(cls, data, numpy.float32)
        obj.reshape(4,4)
        return obj
    
    def get(self):
        return self
    
    def invert(self):
        return self.I
        
    def scale(self, x, y=None, z=None):
        "Uniform scale, if only sx argument is specified"
        if y is None:
            y = x
        if z is None:
            z = x
        m = self
        for col in range(4):
            # Only the top three rows
            m[0,col] *= x
            m[1,col] *= y
            m[2,col] *= z
        return self
    
    def translate(self, vec):
        m = self
        for col in range(4):
            for row in range(3):
                m[row,col] += m[3,col] * vec[row]
        return self
                
    def __mul__(self, rhs):
        result = None
        try:
            result = numpy.matrix.__mul__(self, rhs)
        except ValueError:
            pass
        # Vector result should be vector type
        if result.shape == (4,1):
            result = result.view(Vector4)
        return result


# Translated from hello_opengl_main.cpp line 21
def threadSleep( nMilliseconds ):
    seconds = nMilliseconds / 1000.0
    time.sleep(seconds)


# Translated from hello_opengl_main.cpp line 30
class CGLRenderModel(object):
    def __init__(self, sRenderModelName):
        self.m_sModelName = sRenderModelName
        self.m_glIndexBuffer = 0
        self.m_glVertArray = 0
        self.m_glVertBuffer = 0
        self.m_glTexture = 0
        
    def __enter__(self):
        "Purpose: Create/destroy GL Render Models"
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        "Purpose: Create/destroy GL Render Models"
        self.cleanup()

    def bInit( self, vrModel, vrDiffuseTexture ):
        "Purpose: Allocates and populates the GL resources for a render model"
        # create and bind a VAO to hold state for this model
        self.m_glVertArray = glGenVertexArrays(1)
        glBindVertexArray( self.m_glVertArray )
        # Populate a vertex buffer
        self.m_glVertBuffer = glGenBuffers(1)
        glBindBuffer( GL_ARRAY_BUFFER, self.m_glVertBuffer )
        glBufferData( GL_ARRAY_BUFFER, sizeof( openvr.RenderModel_Vertex_t ) * vrModel.unVertexCount, vrModel.rVertexData, GL_STATIC_DRAW )
        # Identify the components in the vertex buffer
        glEnableVertexAttribArray( 0 )
        glVertexAttribPointer( 0, 3, GL_FLOAT, False, sizeof( openvr.RenderModel_Vertex_t ), openvr.RenderModel_Vertex_t.vPosition.offset )
        glEnableVertexAttribArray( 1 )
        glVertexAttribPointer( 1, 3, GL_FLOAT, False, sizeof( openvr.RenderModel_Vertex_t ), openvr.RenderModel_Vertex_t.vNormal.offset )
        glEnableVertexAttribArray( 2 )
        glVertexAttribPointer( 2, 2, GL_FLOAT, False, sizeof( openvr.RenderModel_Vertex_t ), openvr.RenderModel_Vertex_t.rfTextureCoord.offset )
        # Create and populate the index buffer
        self.m_glIndexBuffer = glGenBuffers(1)
        glBindBuffer( GL_ELEMENT_ARRAY_BUFFER, self.m_glIndexBuffer )
        glBufferData( GL_ELEMENT_ARRAY_BUFFER, sizeof( ctypes.c_uint16 ) * vrModel.unTriangleCount * 3, vrModel.rIndexData, GL_STATIC_DRAW )
        glBindVertexArray( 0 )
        # create and populate the texture
        self.m_glTexture = glGenTextures(1)
        glBindTexture( GL_TEXTURE_2D, self.m_glTexture )
        glTexImage2D( GL_TEXTURE_2D, 0, GL_RGBA, vrDiffuseTexture.unWidth, vrDiffuseTexture.unHeight,
            0, GL_RGBA, GL_UNSIGNED_BYTE, vrDiffuseTexture.rubTextureMapData )
        # If this renders black ask McJohn what's wrong.
        glGenerateMipmap(GL_TEXTURE_2D)
        glTexParameteri( GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE )
        glTexParameteri( GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE )
        glTexParameteri( GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR )
        glTexParameteri( GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR )
        fLargest = glGetFloatv( GL_MAX_TEXTURE_MAX_ANISOTROPY_EXT )
        glTexParameterf( GL_TEXTURE_2D, GL_TEXTURE_MAX_ANISOTROPY_EXT, fLargest )
        glBindTexture( GL_TEXTURE_2D, 0 )
        self.m_unVertexCount = vrModel.unTriangleCount * 3
        return True

    def cleanup(self):
        "Purpose: Frees the GL resources for a render model"
        if self.m_glVertBuffer != 0:
            glDeleteBuffers(1, (self.m_glIndexBuffer,))
            glDeleteVertexArrays( 1, (self.m_glVertArray,) )
            glDeleteBuffers(1, (self.m_glVertBuffer,))
            self.m_glIndexBuffer = 0
            self.m_glVertArray = 0
            self.m_glVertBuffer = 0
    
    def draw(self):
        "Purpose: Draws the render model"
        glBindVertexArray( self.m_glVertArray )
        glActiveTexture( GL_TEXTURE0 )
        glBindTexture( GL_TEXTURE_2D, self.m_glTexture )
        glDrawElements( GL_TRIANGLES, self.m_unVertexCount, GL_UNSIGNED_SHORT, 0 )
        glBindVertexArray( 0 )
    
    def getName(self):
        return self.m_sModelName 


class FramebufferDesc(object):
    def __init__(self, depthBufferId=0, renderTextureId=0, renderFramebufferId=0, resolveTextureId=0, resolveFramebufferId=0):
        self.m_nDepthBufferId = depthBufferId
        self.m_nRenderTextureId = renderTextureId
        self.m_nRenderFramebufferId = renderFramebufferId
        self.m_nResolveTextureId = resolveTextureId
        self.m_nResolveFramebufferId = resolveFramebufferId


class CMainApplication(object):
    def __init__(self, argv):
        self.m_pWindow = None
        self.m_pContext = None
        self.m_nWindowWidth =  1280 
        self.m_nWindowHeight =  720 
        self.m_uiIndexSize = 1
        self.m_unSceneProgramID =  0 
        self.m_unLensProgramID =  0 
        self.m_unControllerTransformProgramID =  0 
        self.m_unRenderModelProgramID =  0 
        self.m_pHMD =  None 
        self.m_pRenderModels = None 
        self.m_bDebugOpenGL = False 
        self.m_bVerbose = False 
        self.m_bPerf = False 
        self.m_bVblank = False 
        self.m_bGlFinishHack = True 
        self.m_glControllerVertBuffer =  0 
        self.m_glSceneVertBuffer = 0
        self.m_glIDVertBuffer = 0
        self.m_glIDIndexBuffer = 0
        self.m_unControllerVAO =  0 
        self.m_unLensVAO =  0 
        self.m_unSceneVAO =  0 
        self.m_nSceneMatrixLocation =  -1 
        self.m_nControllerMatrixLocation =  -1 
        self.m_nRenderModelMatrixLocation =  -1 
        self.m_iTrackedControllerCount =  0 
        self.m_iTrackedControllerCount_Last =  -1 
        self.m_iValidPoseCount =  0 
        self.m_iValidPoseCount_Last =  -1 
        self.m_iSceneVolumeInit =  20 
        self.m_strPoseClasses = ""
        self.m_bShowCubes =  True
        self.m_strDriver = None
        self.m_strDisplay = None
        pose_array_t = openvr.TrackedDevicePose_t * openvr.k_unMaxTrackedDeviceCount
        self.m_rTrackedDevicePose = pose_array_t()
        self.m_rmat4DevicePose = [Matrix4(),] * openvr.k_unMaxTrackedDeviceCount
        self.m_mat4HMDPose = Matrix4()
        self.m_rbShowTrackedDevice = [False,] * openvr.k_unMaxTrackedDeviceCount
        self.m_vecRenderModels = list()
        self.leftEyeDesc = FramebufferDesc()
        self.rightEyeDesc = FramebufferDesc()
        i = 0
        for arg in argv:
            if arg == "-gldebug":
                self.m_bDebugOpenGL = True
            elif arg == "-verbose":
                self.m_bVerbose = True
            elif arg == "-novblank":
                self.m_bVblank = False
            elif arg == "-noglfinishhack":
                self.m_bGlFinishHack = False
            elif arg == "-noprintf":
                g_bPrintf = False
            elif arg == "-cubevolume" and len(argv) > i + 1 and argv[i + 1] != '-':
                self.m_iSceneVolumeInit = int( argv[i + 1] )
                i += 1
            i += 1
        # other initialization tasks are done in BInit
        self.m_rDevClassChar = list()
        for i in range(openvr.k_unMaxTrackedDeviceCount):
            self.m_rDevClassChar.append(chr(0))
            
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        dprintf("Shutdown")
    
    def bInit(self):
        if SDL_Init( SDL_INIT_VIDEO | SDL_INIT_TIMER ) < 0:
            print("%s - SDL could not initialize! SDL Error: %s\n" % ("CMainApplication.bInit()", SDL_GetError()))
            return False
        # Loading the SteamVR Runtime
        try:
            self.m_pHMD = openvr.init(openvr.VRApplication_Scene)
        except openvr.OpenVRError as eError:
            self.m_pHMD = None
            msg = "Unable to init VR runtime: %s" % str(eError)
            SDL_ShowSimpleMessageBox( SDL_MESSAGEBOX_ERROR, "VR_Init Failed", msg, None )
            return False
        try:
            self.m_pRenderModels = openvr.getGenericInterface(openvr.IVRRenderModels_Version)
        except openvr.OpenVRError as eError:
            self.m_pHMD = None
            openvr.shutdown()
            msg = "Unable to get render model interface: %s" % str(eError)
            SDL_ShowSimpleMessageBox( SDL_MESSAGEBOX_ERROR, "VR_Init Failed", msg, None )
            return False
        nWindowPosX = 700
        nWindowPosY = 100
        self.m_nWindowWidth = 1280
        self.m_nWindowHeight = 720
        unWindowFlags = SDL_WINDOW_OPENGL | SDL_WINDOW_SHOWN
        SDL_GL_SetAttribute( SDL_GL_CONTEXT_MAJOR_VERSION, 4 )
        SDL_GL_SetAttribute( SDL_GL_CONTEXT_MINOR_VERSION, 1 )
        #SDL_GL_SetAttribute( SDL_GL_CONTEXT_PROFILE_MASK, SDL_GL_CONTEXT_PROFILE_COMPATIBILITY )
        SDL_GL_SetAttribute( SDL_GL_CONTEXT_PROFILE_MASK, SDL_GL_CONTEXT_PROFILE_CORE )
        SDL_GL_SetAttribute( SDL_GL_MULTISAMPLEBUFFERS, 0 )
        SDL_GL_SetAttribute( SDL_GL_MULTISAMPLESAMPLES, 0 )
        if self.m_bDebugOpenGL:
            SDL_GL_SetAttribute( SDL_GL_CONTEXT_FLAGS, SDL_GL_CONTEXT_DEBUG_FLAG )
        self.m_pWindow = SDL_CreateWindow( "hellovr_sdl", nWindowPosX, nWindowPosY, self.m_nWindowWidth, self.m_nWindowHeight, unWindowFlags )
        if self.m_pWindow is None:
            logging.error( "Window could not be created! SDL Error: %s\n" % SDL_GetError() )
            return False
        self.m_pContext = SDL_GL_CreateContext(self.m_pWindow)
        if self.m_pContext is None:
            logging.error( "OpenGL context could not be created! SDL Error: %s\n" % SDL_GetError() )
            return False
        glGetError() # to clear the error caused deep in GLEW
        swap_interval = 1 if self.m_bVblank else 0
        if SDL_GL_SetSwapInterval( swap_interval ) < 0:
            logging.error( "Warning: Unable to set VSync! SDL Error: %s\n" % SDL_GetError() )
            return False
        self.m_strDriver = "No Driver"
        self.m_strDisplay = "No Display"
        self.m_strDriver = getTrackedDeviceString( self.m_pHMD, openvr.k_unTrackedDeviceIndex_Hmd, openvr.Prop_TrackingSystemName_String )
        self.m_strDisplay = getTrackedDeviceString( self.m_pHMD, openvr.k_unTrackedDeviceIndex_Hmd, openvr.Prop_SerialNumber_String )
        strWindowTitle = "hellovr_sdl - " + self.m_strDriver + " " + self.m_strDisplay
        SDL_SetWindowTitle( self.m_pWindow, strWindowTitle )
        # cube array
        self.m_iSceneVolumeWidth = self.m_iSceneVolumeInit
        self.m_iSceneVolumeHeight = self.m_iSceneVolumeInit
        self.m_iSceneVolumeDepth = self.m_iSceneVolumeInit
        self.m_fScale = 0.3
        self.m_fScaleSpacing = 4.0
        self.m_fNearClip = 0.1
        self.m_fFarClip = 30.0
        self.m_iTexture = 0
        self.m_uiVertcount = 0
        #     self.m_MillisecondsTimer.start(1, this)
        #     self.m_SecondsTimer.start(1000, this)
        if not self.bInitGL():
            logging.error("Unable to initialize OpenGL!\n")
            return False
        if not self.bInitCompositor():
            logging.error("Failed to initialize VR Compositor!\n")
            return False
        return True
        
    def bInitGL(self):
        if self.m_bDebugOpenGL:
            glDebugMessageCallbackARB( GLDEBUGPROCARB(debugCallback), None)
            glDebugMessageControlARB( GL_DONT_CARE, GL_DONT_CARE, GL_DONT_CARE, 0, None, True )
            glEnable(GL_DEBUG_OUTPUT_SYNCHRONOUS_ARB)
        if not self.createAllShaders():
            return False
        self.setupTexturemaps()
        self.setupScene()
        self.setupCameras()
        self.setupStereoRenderTargets()
        self.setupDistortion()
        self.setupRenderModels()
        return True

    def bInitCompositor(self):
        if not openvr.VRCompositor():
            logging.error( "Compositor initialization failed. See log file for details" )
            return False
        return True

    def setupRenderModels(self):
        "Purpose: Create/destroy GL Render Models"
        self.m_rTrackedDeviceToRenderModel = [None] * openvr.k_unMaxTrackedDeviceCount
        if self.m_pHMD is None:
            return
        for unTrackedDevice in range(openvr.k_unTrackedDeviceIndex_Hmd + 1, openvr.k_unMaxTrackedDeviceCount):
            if not self.m_pHMD.isTrackedDeviceConnected( unTrackedDevice ):
                continue
            self.setupRenderModelForTrackedDevice( unTrackedDevice )

    def shutdown(self):
        if self.m_pHMD is not None:
            openvr.shutdown()
            self.m_pHMD = None       
        self.m_vecRenderModels = list()
        if self.m_pContext is not None:
            glDebugMessageControlARB( GL_DONT_CARE, GL_DONT_CARE, GL_DONT_CARE, 0, None, False )
            glDebugMessageCallbackARB(GLDEBUGPROCARB(0), None)
            glDeleteBuffers(1, (self.m_glSceneVertBuffer,))
            glDeleteBuffers(1, (self.m_glIDVertBuffer,))
            glDeleteBuffers(1, (self.m_glIDIndexBuffer,))
            if self.m_unSceneProgramID:
                glDeleteProgram( self.m_unSceneProgramID )
            if self.m_unControllerTransformProgramID:
                glDeleteProgram( self.m_unControllerTransformProgramID )
            if self.m_unRenderModelProgramID:
                glDeleteProgram( self.m_unRenderModelProgramID )
            if self.m_unLensProgramID:
                glDeleteProgram( self.m_unLensProgramID )
            glDeleteRenderbuffers( 1, (self.leftEyeDesc.m_nDepthBufferId,) )
            glDeleteTextures( (self.leftEyeDesc.m_nRenderTextureId,) )
            glDeleteFramebuffers( 1, (self.leftEyeDesc.m_nRenderFramebufferId,) )
            glDeleteTextures( (self.leftEyeDesc.m_nResolveTextureId,) )
            glDeleteFramebuffers( 1, (self.leftEyeDesc.m_nResolveFramebufferId,) )
            glDeleteRenderbuffers( 1, (self.rightEyeDesc.m_nDepthBufferId,) )
            glDeleteTextures( (self.rightEyeDesc.m_nRenderTextureId,) )
            glDeleteFramebuffers( 1, (self.rightEyeDesc.m_nRenderFramebufferId,) )
            glDeleteTextures( (self.rightEyeDesc.m_nResolveTextureId,) )
            glDeleteFramebuffers( 1, (self.rightEyeDesc.m_nResolveFramebufferId,) )
            if self.m_unLensVAO != 0:
                glDeleteVertexArrays( 1, (self.m_unLensVAO,) )
            if self.m_unSceneVAO != 0:
                glDeleteVertexArrays( 1, (self.m_unSceneVAO,) )
            if self.m_unControllerVAO != 0:
                glDeleteVertexArrays( 1, (self.m_unControllerVAO,) )
        if self.m_pWindow is not None:
            SDL_DestroyWindow(self.m_pWindow)
            self.m_pWindow = None
        SDL_Quit()

    def runMainLoop(self):
        bQuit = False
        SDL_StartTextInput()
        SDL_ShowCursor( SDL_DISABLE )
        while not bQuit:
            bQuit = self.handleInput()
            self.renderFrame()
        SDL_StopTextInput()
        
    def handleInput(self):
        bRet = False
        sdlEvent = SDL_Event()
        while SDL_PollEvent( ctypes.byref(sdlEvent) ) != 0:
            if sdlEvent.type == SDL_QUIT:
                bRet = True
            elif sdlEvent.type == SDL_KEYDOWN:
                if sdlEvent.key.keysym.sym == SDLK_ESCAPE or sdlEvent.key.keysym.sym == SDLK_q:
                    bRet = True
                if sdlEvent.key.keysym.sym == SDLK_c:
                    self.m_bShowCubes = not self.m_bShowCubes
        # Process SteamVR events
        hasEvent, event = self.m_pHMD.pollNextEvent()
        while hasEvent:
            self.processVREvent( event )
            hasEvent, event = self.m_pHMD.pollNextEvent()
        # Process SteamVR controller state
        for unDevice in range(openvr.k_unMaxTrackedDeviceCount):
            result, state = self.m_pHMD.getControllerState( unDevice )
            if result:
                self.m_rbShowTrackedDevice[ unDevice ] = state.ulButtonPressed == 0
        return bRet
        
    def processVREvent(self, event):
        "Purpose: Processes a single VR event"
        et = event.eventType
        if et == openvr.VREvent_TrackedDeviceActivated:
            self.setupRenderModelForTrackedDevice( event.trackedDeviceIndex )
            dprintf( "Device %u attached. Setting up render model.\n" % event.trackedDeviceIndex )
        elif et == openvr.VREvent_TrackedDeviceDeactivated:
            dprintf( "Device %u detached.\n" % event.trackedDeviceIndex )
        elif et == openvr.VREvent_TrackedDeviceUpdated:
            dprintf( "Device %u updated.\n" % event.trackedDeviceIndex )     
        
    def renderFrame(self):
        # for now as fast as possible
        if  self.m_pHMD is not None:
            self.drawControllers()
            self.renderStereoTargets()
            self.renderDistortion()
            leftEyeTexture = openvr.Texture_t(self.leftEyeDesc.m_nResolveTextureId, openvr.API_OpenGL, openvr.ColorSpace_Gamma)
            openvr.VRCompositor().submit(openvr.Eye_Left, leftEyeTexture )
            rightEyeTexture = openvr.Texture_t(self.rightEyeDesc.m_nResolveTextureId, openvr.API_OpenGL, openvr.ColorSpace_Gamma)
            openvr.VRCompositor().submit(openvr.Eye_Right, rightEyeTexture )
        if self.m_bVblank and self.m_bGlFinishHack:
            #$ HACKHACK. From gpuview profiling, it looks like there is a bug where two renders and a present
            # happen right before and after the vsync causing all kinds of jittering issues. This glFinish()
            # appears to clear that up. Temporary fix while I try to get nvidia to investigate this problem.
            # 1/29/2014 mikesart
            glFinish()
        # SwapWindow
        SDL_GL_SwapWindow( self.m_pWindow )
        # Clear
        # We want to make sure the glFinish waits for the entire present to complete, not just the submission
        # of the command. So, we do a clear here right here so the glFinish will wait fully for the swap.
        glClearColor( 0, 0, 0, 1 )
        glClear( GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT )
        # Flush and wait for swap.
        if self.m_bVblank:
            glFlush()
            glFinish()
        # Spew out the controller and pose count whenever they change.
        if self.m_iTrackedControllerCount != self.m_iTrackedControllerCount_Last or self.m_iValidPoseCount != self.m_iValidPoseCount_Last:
            self.m_iValidPoseCount_Last = self.m_iValidPoseCount
            self.m_iTrackedControllerCount_Last = self.m_iTrackedControllerCount
            dprintf( "PoseCount:%d(%s) Controllers:%d\n" % (self.m_iValidPoseCount, self.m_strPoseClasses, self.m_iTrackedControllerCount) )
        self.updateHMDMatrixPose()
        

    def setupTexturemaps(self):
        this_folder = os.path.dirname(os.path.abspath(__file__))
        image_path = os.path.join(this_folder, "cube_texture_small.png")
        img = Image.open(image_path)
        imageRGBA = numpy.array(list(img.getdata()), numpy.uint8)
        self.m_iTexture = glGenTextures(1)
        glBindTexture( GL_TEXTURE_2D, self.m_iTexture )
        glTexImage2D( GL_TEXTURE_2D, 0, GL_RGB, img.size[0], img.size[1],
            0, GL_RGB, GL_UNSIGNED_BYTE, imageRGBA )
        glGenerateMipmap(GL_TEXTURE_2D)
        glTexParameteri( GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE )
        glTexParameteri( GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE )
        glTexParameteri( GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR )
        glTexParameteri( GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR )
        fLargest = glGetFloatv(GL_MAX_TEXTURE_MAX_ANISOTROPY_EXT)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAX_ANISOTROPY_EXT, fLargest)
        glBindTexture( GL_TEXTURE_2D, 0 )
        return self.m_iTexture != 0
        

    def setupScene(self):
        "Purpose: create a sea of cubes"
        if self.m_pHMD is None:
            return
        vertdataarray = list()
        matScale = Matrix4()
        matScale.scale( self.m_fScale, self.m_fScale, self.m_fScale )
        matTransform = Matrix4()
        matTransform.translate([
            -( float(self.m_iSceneVolumeWidth) * self.m_fScaleSpacing ) / 2.0,
            -( float(self.m_iSceneVolumeHeight) * self.m_fScaleSpacing ) / 2.0,
            -( float(self.m_iSceneVolumeDepth) * self.m_fScaleSpacing ) / 2.0 ])
        mat = matScale * matTransform
        for z in range(self.m_iSceneVolumeDepth):  # @UnusedVariable
            for y in range(self.m_iSceneVolumeHeight):  # @UnusedVariable
                for x in range(self.m_iSceneVolumeWidth):  # @UnusedVariable
                    self.addCubeToScene( mat, vertdataarray )
                    mat = mat * Matrix4().translate( [self.m_fScaleSpacing, 0, 0] )
                mat = mat * Matrix4().translate( [-(float(self.m_iSceneVolumeWidth)) * self.m_fScaleSpacing, self.m_fScaleSpacing, 0] )
            mat = mat * Matrix4().translate( [0, -(float(self.m_iSceneVolumeHeight)) * self.m_fScaleSpacing, self.m_fScaleSpacing] )
        self.m_uiVertcount = len(vertdataarray)/5
        self.m_unSceneVAO = glGenVertexArrays(1)
        glBindVertexArray( self.m_unSceneVAO )
        self.m_glSceneVertBuffer = glGenBuffers(1)
        glBindBuffer( GL_ARRAY_BUFFER, self.m_glSceneVertBuffer )
        vertdataarray = numpy.array(vertdataarray, numpy.float32) # convert to numpy array at last possible moment
        glBufferData( GL_ARRAY_BUFFER, sizeof(ctypes.c_float) * len(vertdataarray), vertdataarray, GL_STATIC_DRAW)
        glBindBuffer( GL_ARRAY_BUFFER, self.m_glSceneVertBuffer )
        stride = sizeof(VertexDataScene)
        offset = 0
        glEnableVertexAttribArray( 0 )
        glVertexAttribPointer( 0, 3, GL_FLOAT, False, stride , offset)
        offset += sizeof(Vector3)
        glEnableVertexAttribArray( 1 )
        glVertexAttribPointer( 1, 2, GL_FLOAT, False, stride, offset)
        glBindVertexArray( 0 )
        glDisableVertexAttribArray(0)
        glDisableVertexAttribArray(1)
        
        
    def addCubeToScene( self, mat, vertdata ):
        # Matrix4 mat( outermat.data() )
        A = mat * Vector4( [0, 0, 0, 1] )
        B = mat * Vector4( [1, 0, 0, 1] )
        C = mat * Vector4( [1, 1, 0, 1] )
        D = mat * Vector4( [0, 1, 0, 1] )
        E = mat * Vector4( [0, 0, 1, 1] )
        F = mat * Vector4( [1, 0, 1, 1] )
        G = mat * Vector4( [1, 1, 1, 1] )
        H = mat * Vector4( [0, 1, 1, 1] )
        # triangles instead of quads
        self.addCubeVertex( E.x, E.y, E.z, 0, 1, vertdata ) #Front
        self.addCubeVertex( F.x, F.y, F.z, 1, 1, vertdata )
        self.addCubeVertex( G.x, G.y, G.z, 1, 0, vertdata )
        self.addCubeVertex( G.x, G.y, G.z, 1, 0, vertdata )
        self.addCubeVertex( H.x, H.y, H.z, 0, 0, vertdata )
        self.addCubeVertex( E.x, E.y, E.z, 0, 1, vertdata )
        self.addCubeVertex( B.x, B.y, B.z, 0, 1, vertdata ) #Back
        self.addCubeVertex( A.x, A.y, A.z, 1, 1, vertdata )
        self.addCubeVertex( D.x, D.y, D.z, 1, 0, vertdata )
        self.addCubeVertex( D.x, D.y, D.z, 1, 0, vertdata )
        self.addCubeVertex( C.x, C.y, C.z, 0, 0, vertdata )
        self.addCubeVertex( B.x, B.y, B.z, 0, 1, vertdata )
        self.addCubeVertex( H.x, H.y, H.z, 0, 1, vertdata ) #Top
        self.addCubeVertex( G.x, G.y, G.z, 1, 1, vertdata )
        self.addCubeVertex( C.x, C.y, C.z, 1, 0, vertdata )
        self.addCubeVertex( C.x, C.y, C.z, 1, 0, vertdata )
        self.addCubeVertex( D.x, D.y, D.z, 0, 0, vertdata )
        self.addCubeVertex( H.x, H.y, H.z, 0, 1, vertdata )
        self.addCubeVertex( A.x, A.y, A.z, 0, 1, vertdata ) #Bottom
        self.addCubeVertex( B.x, B.y, B.z, 1, 1, vertdata )
        self.addCubeVertex( F.x, F.y, F.z, 1, 0, vertdata )
        self.addCubeVertex( F.x, F.y, F.z, 1, 0, vertdata )
        self.addCubeVertex( E.x, E.y, E.z, 0, 0, vertdata )
        self.addCubeVertex( A.x, A.y, A.z, 0, 1, vertdata )
        self.addCubeVertex( A.x, A.y, A.z, 0, 1, vertdata ) #Left
        self.addCubeVertex( E.x, E.y, E.z, 1, 1, vertdata )
        self.addCubeVertex( H.x, H.y, H.z, 1, 0, vertdata )
        self.addCubeVertex( H.x, H.y, H.z, 1, 0, vertdata )
        self.addCubeVertex( D.x, D.y, D.z, 0, 0, vertdata )
        self.addCubeVertex( A.x, A.y, A.z, 0, 1, vertdata )
        self.addCubeVertex( F.x, F.y, F.z, 0, 1, vertdata ) #Right
        self.addCubeVertex( B.x, B.y, B.z, 1, 1, vertdata )
        self.addCubeVertex( C.x, C.y, C.z, 1, 0, vertdata )
        self.addCubeVertex( C.x, C.y, C.z, 1, 0, vertdata )
        self.addCubeVertex( G.x, G.y, G.z, 0, 0, vertdata )
        self.addCubeVertex( F.x, F.y, F.z, 0, 1, vertdata )
        
    def addCubeVertex( self, fl0, fl1, fl2, fl3, fl4, vertdata ):
        vertdata.append( fl0 )
        vertdata.append( fl1 )
        vertdata.append( fl2 )
        vertdata.append( fl3 )
        vertdata.append( fl4 )

    def drawControllers(self):
        "Purpose: Draw all of the controllers as X/Y/Z lines"
        # don't draw controllers if somebody else has input focus
        if self.m_pHMD.isInputFocusCapturedByAnotherProcess():
            return
        vertdataarray = list()
        self.m_uiControllerVertcount = 0
        self.m_iTrackedControllerCount = 0
    
        for unTrackedDevice in range(openvr.k_unTrackedDeviceIndex_Hmd + 1, openvr.k_unMaxTrackedDeviceCount):
            if not self.m_pHMD.isTrackedDeviceConnected( unTrackedDevice ):
                continue
            if self.m_pHMD.getTrackedDeviceClass( unTrackedDevice ) != openvr.TrackedDeviceClass_Controller:
                continue
            self.m_iTrackedControllerCount += 1
            if not self.m_rTrackedDevicePose[ unTrackedDevice ].bPoseIsValid:
                continue
            mat = self.m_rmat4DevicePose[unTrackedDevice]
            center = mat * Vector4( 0, 0, 0, 1 )
            for i in range(3):
                color = Vector4( 0, 0, 0 )
                point = Vector4( 0, 0, 0, 1 )
                point[i] += 0.05  # offset in X, Y, Z
                color[i] = 1.0  # R, G, B
                point = mat * point
                vertdataarray.append( center.x )
                vertdataarray.append( center.y )
                vertdataarray.append( center.z )
                vertdataarray.append( color.x )
                vertdataarray.append( color.y )
                vertdataarray.append( color.z )
                vertdataarray.append( point.x )
                vertdataarray.append( point.y )
                vertdataarray.append( point.z )
                vertdataarray.append( color.x )
                vertdataarray.append( color.y )
                vertdataarray.append( color.z )
                self.m_uiControllerVertcount += 2
            start = mat * Vector4( 0, 0, -0.02, 1 )
            end = mat * Vector4( 0, 0, -39., 1 )
            color = Vector3( .92, .92, .71 )
            vertdataarray.append( start.x )
            vertdataarray.append( start.y )
            vertdataarray.append( start.z )
            vertdataarray.append( color.x )
            vertdataarray.append( color.y )
            vertdataarray.append( color.z )
            vertdataarray.append( end.x )
            vertdataarray.append( end.y )
            vertdataarray.append( end.z )
            vertdataarray.append( color.x )
            vertdataarray.append( color.y )
            vertdataarray.append( color.z )
            self.m_uiControllerVertcount += 2
        # Setup the VAO the first time through.
        if self.m_unControllerVAO == 0:        
            self.m_unControllerVAO = glGenVertexArrays(1)
            glBindVertexArray( self.m_unControllerVAO )
            self.m_glControllerVertBuffer = glGenBuffers(1)
            glBindBuffer( GL_ARRAY_BUFFER, self.m_glControllerVertBuffer )
            stride = 2 * 3 * sizeof( ctypes.c_float )
            offset = 0
            glEnableVertexAttribArray( 0 )
            glVertexAttribPointer( 0, 3, GL_FLOAT, False, stride, offset)
            offset += sizeof( Vector3 )
            glEnableVertexAttribArray( 1 )
            glVertexAttribPointer( 1, 3, GL_FLOAT, False, stride, offset)
            glBindVertexArray( 0 )
        glBindBuffer( GL_ARRAY_BUFFER, self.m_glControllerVertBuffer )
        # set vertex data if we have some
        if len(vertdataarray) > 0:
            #$ TODO: Use glBufferSubData for this...
            glBufferData( GL_ARRAY_BUFFER, sizeof(float) * vertdataarray.size(), vertdataarray[0], GL_STREAM_DRAW )

    def setupStereoRenderTargets(self):
        if self.m_pHMD is None:
            return False
        self.m_nRenderWidth, self.m_nRenderHeight = self.m_pHMD.getRecommendedRenderTargetSize()
        self.createFrameBuffer( self.m_nRenderWidth, self.m_nRenderHeight, self.leftEyeDesc )
        self.createFrameBuffer( self.m_nRenderWidth, self.m_nRenderHeight, self.rightEyeDesc )
        return True
    
    def setupDistortion(self):
        if self.m_pHMD is None:
            return
        self.m_iLensGridSegmentCountH = 43
        self.m_iLensGridSegmentCountV = 43
        w = float( 1.0/float(self.m_iLensGridSegmentCountH-1) )
        h = float( 1.0/float(self.m_iLensGridSegmentCountV-1) )
        u, v = 0, 0
        vVerts = list()
        vert = VertexDataLens()
        #left eye distortion verts
        Xoffset = -1
        for y in range(self.m_iLensGridSegmentCountV):
            for x in range(self.m_iLensGridSegmentCountH):
                u = x*w
                v = 1-y*h
                vert.position = Vector2( [Xoffset+u, -1+2*y*h] )
                dc0 = self.m_pHMD.computeDistortion(openvr.Eye_Left, u, v)
                vert.texCoordRed = Vector2([dc0.rfRed[0], 1 - dc0.rfRed[1]])
                vert.texCoordGreen =  Vector2([dc0.rfGreen[0], 1 - dc0.rfGreen[1]])
                vert.texCoordBlue = Vector2([dc0.rfBlue[0], 1 - dc0.rfBlue[1]])
                vVerts.extend( vert.as_floats() )
        #right eye distortion verts
        Xoffset = 0
        for y in range(self.m_iLensGridSegmentCountV):
            for x in range(self.m_iLensGridSegmentCountH):
                u = x*w 
                v = 1-y*h
                vert.position = Vector2( [Xoffset+u, -1+2*y*h] )
                dc0 = self.m_pHMD.computeDistortion( openvr.Eye_Right, u, v )
                vert.texCoordRed = Vector2([dc0.rfRed[0], 1 - dc0.rfRed[1]])
                vert.texCoordGreen = Vector2([dc0.rfGreen[0], 1 - dc0.rfGreen[1]])
                vert.texCoordBlue = Vector2([dc0.rfBlue[0], 1 - dc0.rfBlue[1]])
                vVerts.extend( vert.as_floats() )
        vIndices = list()
        offset = 0
        for y in range(self.m_iLensGridSegmentCountV-1):
            for x in range(self.m_iLensGridSegmentCountH-1):
                a = self.m_iLensGridSegmentCountH*y+x +offset
                b = self.m_iLensGridSegmentCountH*y+x+1 +offset
                c = (y+1)*self.m_iLensGridSegmentCountH+x+1 +offset
                d = (y+1)*self.m_iLensGridSegmentCountH+x +offset
                vIndices.append( a )
                vIndices.append( b )
                vIndices.append( c )
                vIndices.append( a )
                vIndices.append( c )
                vIndices.append( d )
        offset = (self.m_iLensGridSegmentCountH)*(self.m_iLensGridSegmentCountV)
        for y in range(self.m_iLensGridSegmentCountV-1):
            for x in range(self.m_iLensGridSegmentCountH-1):
                a = self.m_iLensGridSegmentCountH*y+x +offset
                b = self.m_iLensGridSegmentCountH*y+x+1 +offset
                c = (y+1)*self.m_iLensGridSegmentCountH+x+1 +offset
                d = (y+1)*self.m_iLensGridSegmentCountH+x +offset
                vIndices.append( a )
                vIndices.append( b )
                vIndices.append( c )
                vIndices.append( a )
                vIndices.append( c )
                vIndices.append( d )
        self.m_uiIndexSize = len(vIndices)
        self.m_unLensVAO = glGenVertexArrays(1)
        glBindVertexArray( self.m_unLensVAO )
        self.m_glIDVertBuffer = glGenBuffers(1)
        glBindBuffer( GL_ARRAY_BUFFER, self.m_glIDVertBuffer )
        vert_data = numpy.array(vVerts, dtype='float32')
        glBufferData( GL_ARRAY_BUFFER, vert_data, GL_STATIC_DRAW )
        self.m_glIDIndexBuffer = glGenBuffers(1)
        glBindBuffer( GL_ELEMENT_ARRAY_BUFFER, self.m_glIDIndexBuffer )
        index_data = numpy.array(vIndices, dtype='float32')
        glBufferData( GL_ELEMENT_ARRAY_BUFFER, index_data, GL_STATIC_DRAW )
        glEnableVertexAttribArray( 0 )
        glVertexAttribPointer(0, 2, GL_FLOAT, False, sizeof(VertexDataLens), VertexDataLens.position.offset )
        glEnableVertexAttribArray( 1 )
        glVertexAttribPointer(1, 2, GL_FLOAT, False, sizeof(VertexDataLens), VertexDataLens.texCoordRed.offset )
        glEnableVertexAttribArray(2)
        glVertexAttribPointer(2, 2, GL_FLOAT, False, sizeof(VertexDataLens), VertexDataLens.texCoordGreen.offset )
        glEnableVertexAttribArray(3)
        glVertexAttribPointer(3, 2, GL_FLOAT, False, sizeof(VertexDataLens), VertexDataLens.texCoordBlue.offset )
        glBindVertexArray( 0 )
        glDisableVertexAttribArray(0)
        glDisableVertexAttribArray(1)
        glDisableVertexAttribArray(2)
        glDisableVertexAttribArray(3)
        glBindBuffer(GL_ARRAY_BUFFER, 0)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, 0)

    def setupCameras(self):
        self.m_mat4ProjectionLeft = self.getHMDMatrixProjectionEye( openvr.Eye_Left )
        self.m_mat4ProjectionRight = self.getHMDMatrixProjectionEye( openvr.Eye_Right )
        self.m_mat4eyePosLeft = self.getHMDMatrixPoseEye( openvr.Eye_Left )
        self.m_mat4eyePosRight = self.getHMDMatrixPoseEye( openvr.Eye_Right )

    def renderStereoTargets(self):
        glClearColor( 0.15, 0.15, 0.18, 1.0 ) # nice background color, but not black
        glEnable( GL_MULTISAMPLE )
        # Left Eye
        glBindFramebuffer( GL_FRAMEBUFFER, self.leftEyeDesc.m_nRenderFramebufferId )
        glViewport(0, 0, self.m_nRenderWidth, self.m_nRenderHeight )
        self.renderScene( openvr.Eye_Left )
        glBindFramebuffer( GL_FRAMEBUFFER, 0 )
        glDisable( GL_MULTISAMPLE )
        glBindFramebuffer(GL_READ_FRAMEBUFFER, self.leftEyeDesc.m_nRenderFramebufferId)
        glBindFramebuffer(GL_DRAW_FRAMEBUFFER, self.leftEyeDesc.m_nResolveFramebufferId )
        glBlitFramebuffer( 0, 0, self.m_nRenderWidth, self.m_nRenderHeight, 0, 0, self.m_nRenderWidth, self.m_nRenderHeight, 
            GL_COLOR_BUFFER_BIT,
            GL_LINEAR )
        glBindFramebuffer(GL_READ_FRAMEBUFFER, 0)
        glBindFramebuffer(GL_DRAW_FRAMEBUFFER, 0 )    
        glEnable( GL_MULTISAMPLE )
        # Right Eye
        glBindFramebuffer( GL_FRAMEBUFFER, self.rightEyeDesc.m_nRenderFramebufferId )
        glViewport(0, 0, self.m_nRenderWidth, self.m_nRenderHeight )
        self.renderScene( openvr.Eye_Right )
        glBindFramebuffer( GL_FRAMEBUFFER, 0 )
        glDisable( GL_MULTISAMPLE )
        glBindFramebuffer(GL_READ_FRAMEBUFFER, self.rightEyeDesc.m_nRenderFramebufferId )
        glBindFramebuffer(GL_DRAW_FRAMEBUFFER, self.rightEyeDesc.m_nResolveFramebufferId )
        glBlitFramebuffer( 0, 0, self.m_nRenderWidth, self.m_nRenderHeight, 0, 0, self.m_nRenderWidth, self.m_nRenderHeight, 
            GL_COLOR_BUFFER_BIT,
            GL_LINEAR  )
        glBindFramebuffer(GL_READ_FRAMEBUFFER, 0)
        glBindFramebuffer(GL_DRAW_FRAMEBUFFER, 0 )

    def renderDistortion(self):
        glDisable(GL_DEPTH_TEST)
        glViewport( 0, 0, self.m_nWindowWidth, self.m_nWindowHeight )
        glBindVertexArray( self.m_unLensVAO )
        glUseProgram( self.m_unLensProgramID )
        #render left lens (first half of index array )
        glBindTexture(GL_TEXTURE_2D, self.leftEyeDesc.m_nResolveTextureId )
        glTexParameteri( GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE )
        glTexParameteri( GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE )
        glTexParameteri( GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR )
        glTexParameteri( GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR )
        glDrawElements( GL_TRIANGLES, self.m_uiIndexSize/2, GL_UNSIGNED_SHORT, 0 )
        #render right lens (second half of index array )
        glBindTexture(GL_TEXTURE_2D, self.rightEyeDesc.m_nResolveTextureId  )
        glTexParameteri( GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE )
        glTexParameteri( GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE )
        glTexParameteri( GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR )
        glTexParameteri( GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR )
        glDrawElements( GL_TRIANGLES, self.m_uiIndexSize/2, GL_UNSIGNED_SHORT, self.m_uiIndexSize )
        glBindVertexArray( 0 )
        glUseProgram( 0 )

    def renderScene(self, nEye):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glEnable(GL_DEPTH_TEST)
        if self.m_bShowCubes:
            glUseProgram( self.m_unSceneProgramID )
            glUniformMatrix4fv( self.m_nSceneMatrixLocation, 1, False, self.getCurrentViewProjectionMatrix( nEye ).get() )
            glBindVertexArray( self.m_unSceneVAO )
            glBindTexture( GL_TEXTURE_2D, self.m_iTexture )
            glDrawArrays( GL_TRIANGLES, 0, self.m_uiVertcount )
            glBindVertexArray( 0 )
        bIsInputCapturedByAnotherProcess = self.m_pHMD.isInputFocusCapturedByAnotherProcess()
        if not bIsInputCapturedByAnotherProcess:
            # draw the controller axis lines
            glUseProgram( self.m_unControllerTransformProgramID )
            glUniformMatrix4fv( self.m_nControllerMatrixLocation, 1, False, self.getCurrentViewProjectionMatrix( nEye ).get() )
            glBindVertexArray( self.m_unControllerVAO )
            glDrawArrays( GL_LINES, 0, self.m_uiControllerVertcount )
            glBindVertexArray( 0 )
        # ----- Render Model rendering -----
        glUseProgram( self.m_unRenderModelProgramID )
        for unTrackedDevice in range(openvr.k_unMaxTrackedDeviceCount):
            if not self.m_rTrackedDeviceToRenderModel[ unTrackedDevice ] or not self.m_rbShowTrackedDevice[ unTrackedDevice ]:
                continue
            pose = self.m_rTrackedDevicePose[ unTrackedDevice ]
            if not pose.bPoseIsValid:
                continue
            if bIsInputCapturedByAnotherProcess and self.m_pHMD.getTrackedDeviceClass( unTrackedDevice ) == openvr.TrackedDeviceClass_Controller:
                continue
            matDeviceToTracking = self.m_rmat4DevicePose[ unTrackedDevice ]
            matMVP = self.getCurrentViewProjectionMatrix( nEye ) * matDeviceToTracking
            glUniformMatrix4fv( self.m_nRenderModelMatrixLocation, 1, False, matMVP.get() )
            self.m_rTrackedDeviceToRenderModel[ unTrackedDevice ].draw()
        glUseProgram( 0 )


    def getHMDMatrixProjectionEye(self, nEye):
        if self.m_pHMD is None:
            return Matrix4()
        mat = self.m_pHMD.getProjectionMatrix( nEye, self.m_fNearClip, self.m_fFarClip, openvr.API_OpenGL)
        return Matrix4( [
            [mat.m[0][0], mat.m[1][0], mat.m[2][0], mat.m[3][0]],
            [mat.m[0][1], mat.m[1][1], mat.m[2][1], mat.m[3][1]], 
            [mat.m[0][2], mat.m[1][2], mat.m[2][2], mat.m[3][2]], 
            [mat.m[0][3], mat.m[1][3], mat.m[2][3], mat.m[3][3]] ] )
        
    def getHMDMatrixPoseEye(self, nEye):
        if self.m_pHMD is None:
            return Matrix4()
        matEyeRight = self.m_pHMD.getEyeToHeadTransform( nEye )
        matrixObj = Matrix4( [
            [matEyeRight.m[0][0], matEyeRight.m[1][0], matEyeRight.m[2][0], 0.0], 
            [matEyeRight.m[0][1], matEyeRight.m[1][1], matEyeRight.m[2][1], 0.0],
            [matEyeRight.m[0][2], matEyeRight.m[1][2], matEyeRight.m[2][2], 0.0],
            [matEyeRight.m[0][3], matEyeRight.m[1][3], matEyeRight.m[2][3], 1.0] ])
        return matrixObj.invert()

    def getCurrentViewProjectionMatrix(self, nEye):
        if nEye == openvr.Eye_Left:
            matMVP = self.m_mat4ProjectionLeft * self.m_mat4eyePosLeft * self.m_mat4HMDPose
        elif nEye == openvr.Eye_Right:
            matMVP = self.m_mat4ProjectionRight * self.m_mat4eyePosRight *  self.m_mat4HMDPose
        return matMVP

    def updateHMDMatrixPose(self):
        if self.m_pHMD is None:
            return
        openvr.VRCompositor().waitGetPoses(self.m_rTrackedDevicePose, openvr.k_unMaxTrackedDeviceCount, None, 0 )
        self.m_iValidPoseCount = 0
        self.m_strPoseClasses = ""
        for nDevice in range(openvr.k_unMaxTrackedDeviceCount):
            if self.m_rTrackedDevicePose[nDevice].bPoseIsValid:
                self.m_iValidPoseCount += 1
                self.m_rmat4DevicePose[nDevice] = self.convertSteamVRMatrixToMatrix4( self.m_rTrackedDevicePose[nDevice].mDeviceToAbsoluteTracking )
                if self.m_rDevClassChar[nDevice]==0:
                    dc = self.m_pHMD.getTrackedDeviceClass(nDevice)
                    if dc == openvr.TrackedDeviceClass_Controller:
                        self.m_rDevClassChar[nDevice] = 'C'
                    elif dc == openvr.TrackedDeviceClass_HMD:
                        self.m_rDevClassChar[nDevice] = 'H'
                    elif dc == openvr.TrackedDeviceClass_Invalid:
                        self.m_rDevClassChar[nDevice] = 'I'
                    elif dc == openvr.TrackedDeviceClass_Other:
                        self.m_rDevClassChar[nDevice] = 'O'
                    elif dc == openvr.TrackedDeviceClass_TrackingReference:
                        self.m_rDevClassChar[nDevice] = 'T'
                    else:
                        self.m_rDevClassChar[nDevice] = '?'
                self.m_strPoseClasses += self.m_rDevClassChar[nDevice]
        if self.m_rTrackedDevicePose[openvr.k_unTrackedDeviceIndex_Hmd].bPoseIsValid:
            self.m_mat4HMDPose = self.m_rmat4DevicePose[openvr.k_unTrackedDeviceIndex_Hmd].invert()
        

    def convertSteamVRMatrixToMatrix4(self, matPose):
        "Purpose: Converts a SteamVR matrix to our local matrix class"
        matrixObj = Matrix4( [
        [matPose.m[0][0], matPose.m[1][0], matPose.m[2][0], 0.0],
        [matPose.m[0][1], matPose.m[1][1], matPose.m[2][1], 0.0],
        [matPose.m[0][2], matPose.m[1][2], matPose.m[2][2], 0.0],
        [matPose.m[0][3], matPose.m[1][3], matPose.m[2][3], 1.0] ] ) 
        return matrixObj


    def compileGLShader(self, pchShaderName, pchVertexShader, pchFragmentShader):
        """
        Purpose: Compiles a GL shader program and returns the handle. Returns 0 if
           the shader couldn't be compiled for some reason.
        """
        unProgramID = glCreateProgram()
        nSceneVertexShader = glCreateShader(GL_VERTEX_SHADER)
        glShaderSource( nSceneVertexShader, pchVertexShader)
        glCompileShader( nSceneVertexShader )
        vShaderCompiled = glGetShaderiv( nSceneVertexShader, GL_COMPILE_STATUS)
        if not vShaderCompiled:
            dprintf("%s - Unable to compile vertex shader %d!\n" % (pchShaderName, nSceneVertexShader) )
            glDeleteProgram( unProgramID )
            glDeleteShader( nSceneVertexShader )
            return 0
        glAttachShader( unProgramID, nSceneVertexShader)
        glDeleteShader( nSceneVertexShader ) # the program hangs onto this once it's attached
        nSceneFragmentShader = glCreateShader(GL_FRAGMENT_SHADER)
        glShaderSource( nSceneFragmentShader, pchFragmentShader)
        glCompileShader( nSceneFragmentShader )
        fShaderCompiled = glGetShaderiv( nSceneFragmentShader, GL_COMPILE_STATUS)
        if not fShaderCompiled:
            dprintf("%s - Unable to compile fragment shader %d!\n" % ( pchShaderName, nSceneFragmentShader) )
            glDeleteProgram( unProgramID )
            glDeleteShader( nSceneFragmentShader )
            return 0
        glAttachShader( unProgramID, nSceneFragmentShader )
        glDeleteShader( nSceneFragmentShader ) # the program hangs onto this once it's attached
        glLinkProgram( unProgramID )
        programSuccess = glGetProgramiv( unProgramID, GL_LINK_STATUS)
        if not programSuccess:
            dprintf("%s - Error linking program %d!\n" % (pchShaderName, unProgramID) )
            glDeleteProgram( unProgramID )
            return 0
        glUseProgram( unProgramID )
        glUseProgram( 0 )
        return unProgramID

    def createAllShaders(self):
        "Purpose: Creates all the shaders used by HelloVR SDL"
        self.m_unSceneProgramID = self.compileGLShader( 
            "Scene",
            # Vertex Shader
            dedent("""\
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
            """),
            # Fragment Shader
            dedent("""\
            #version 410 core
            uniform sampler2D mytexture;
            in vec2 v2UVcoords;
            out vec4 outputColor;
            void main()
            {
               outputColor = texture(mytexture, v2UVcoords);
            }
            """)
            )
        self.m_nSceneMatrixLocation = glGetUniformLocation( self.m_unSceneProgramID, "matrix" )
        if self.m_nSceneMatrixLocation == -1:
            dprintf( "Unable to find matrix uniform in scene shader\n" )
            return False
        self.m_unControllerTransformProgramID = self.compileGLShader(
            "Controller",
            # vertex shader
            dedent("""\
            #version 410
            uniform mat4 matrix;
            layout(location = 0) in vec4 position;
            layout(location = 1) in vec3 v3ColorIn;
            out vec4 v4Color;
            void main()
            {
                v4Color.xyz = v3ColorIn;
                v4Color.a = 1.0;
                gl_Position = matrix * position;
            }
            """),
            # fragment shader
            dedent("""\
            #version 410
            in vec4 v4Color;
            out vec4 outputColor;
            void main()
            {
               outputColor = v4Color;
            }
            """) )
        self.m_nControllerMatrixLocation = glGetUniformLocation( self.m_unControllerTransformProgramID, "matrix" )
        if self.m_nControllerMatrixLocation == -1:
            dprintf( "Unable to find matrix uniform in controller shader\n" )
            return False
        self.m_unRenderModelProgramID = self.compileGLShader( 
            "render model",
            # vertex shader
            dedent("""\
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
            """),
            #fragment shader
            dedent("""\
            #version 410 core
            uniform sampler2D diffuse;
            in vec2 v2TexCoord;
            out vec4 outputColor;
            void main()
            {
               outputColor = texture( diffuse, v2TexCoord);
            }
            """) )
        self.m_nRenderModelMatrixLocation = glGetUniformLocation( self.m_unRenderModelProgramID, "matrix" )
        if self.m_nRenderModelMatrixLocation == -1:
            dprintf( "Unable to find matrix uniform in render model shader\n" )
            return False
        self.m_unLensProgramID = self.compileGLShader(
            "Distortion",
            # vertex shader
            dedent("""\
            #version 410 core
            layout(location = 0) in vec4 position;
            layout(location = 1) in vec2 v2UVredIn;
            layout(location = 2) in vec2 v2UVGreenIn;
            layout(location = 3) in vec2 v2UVblueIn;
            noperspective  out vec2 v2UVred;
            noperspective  out vec2 v2UVgreen;
            noperspective  out vec2 v2UVblue;
            void main()
            {
                v2UVred = v2UVredIn;
                v2UVgreen = v2UVGreenIn;
                v2UVblue = v2UVblueIn;
                gl_Position = position;
            }
            """),
            # fragment shader
            dedent("""\
            #version 410 core
            uniform sampler2D mytexture;
    
            noperspective  in vec2 v2UVred;
            noperspective  in vec2 v2UVgreen;
            noperspective  in vec2 v2UVblue;
    
            out vec4 outputColor;
    
            void main()
            {
                float fBoundsCheck = ( 
                    (dot( vec2( lessThan( v2UVgreen.xy, vec2(0.05, 0.05)) ), vec2(1.0, 1.0))
                    + dot( vec2( greaterThan( v2UVgreen.xy, vec2( 0.95, 0.95)) ), vec2(1.0, 1.0))) 
                    );
                if( fBoundsCheck > 1.0 ) {
                    outputColor = vec4( 0, 0, 0, 1.0 ); 
                } 
                else {
                    float red = texture(mytexture, v2UVred).x;
                    float green = texture(mytexture, v2UVgreen).y;
                    float blue = texture(mytexture, v2UVblue).z;
                    outputColor = vec4( red, green, blue, 1.0  ); 
                }
            }
            """) )
        return self.m_unSceneProgramID != 0 and self.m_unControllerTransformProgramID != 0 and self.m_unRenderModelProgramID != 0 and self.m_unLensProgramID != 0        

    def setupRenderModelForTrackedDevice(self, unTrackedDeviceIndex):
        "Purpose: Create/destroy GL a Render Model for a single tracked device"
        if unTrackedDeviceIndex >= openvr.k_unMaxTrackedDeviceCount:
            return
        # try to find a model we've already set up
        sRenderModelName = getTrackedDeviceString( self.m_pHMD, unTrackedDeviceIndex, openvr.Prop_RenderModelName_String )
        pRenderModel = self.findOrLoadRenderModel( sRenderModelName )
        if pRenderModel is None:        
            sTrackingSystemName = getTrackedDeviceString( self.m_pHMD, unTrackedDeviceIndex, openvr.Prop_TrackingSystemName_String )
            dprintf( "Unable to load render model for tracked device %d (%s.%s)" % (
                    unTrackedDeviceIndex, sTrackingSystemName, sRenderModelName) )
        else:
            self.m_rTrackedDeviceToRenderModel[ unTrackedDeviceIndex ] = pRenderModel
            self.m_rbShowTrackedDevice[ unTrackedDeviceIndex ] = True
        
    def findOrLoadRenderModel(self, pchRenderModelName):
        "Purpose: Finds a render model we've already loaded or loads a new one"
        pRenderModel = None
        for model in self.m_vecRenderModels:
            if model.getName() == pchRenderModelName:
                pRenderModel = model
                break
        # load the model if we didn't find one
        if pRenderModel is None:
            error = openvr.EVRRenderModelError()
            while True:
                error, pModel = openvr.VRRenderModels().loadRenderModel_Async( pchRenderModelName )
                if error != openvr.VRRenderModelError_Loading:
                    break
                threadSleep( 1 )
            if error != openvr.VRRenderModelError_None:
                dprintf( "Unable to load render model %s - %s\n" % (
                        pchRenderModelName, 
                        openvr.VRRenderModels().getRenderModelErrorNameFromEnum( error )) )
                return None # move on to the next tracked device
            while True:
                error, pTexture = openvr.VRRenderModels().loadTexture_Async( pModel.contents.diffuseTextureId )
                if error != openvr.VRRenderModelError_Loading:
                    break
                threadSleep( 1 )
            if error != openvr.VRRenderModelError_None:
                dprintf( "Unable to load render texture id:%d for render model %s\n" % (
                        pModel.contents.diffuseTextureId, pchRenderModelName) )
                openvr.VRRenderModels().FreeRenderModel( pModel )
                return None # move on to the next tracked device
            pRenderModel = CGLRenderModel( pchRenderModelName )
            if not pRenderModel.bInit( pModel.contents, pTexture.contents ):
                dprintf( "Unable to create GL model from render model %s\n" % pchRenderModelName )
                # delete pRenderModel
                pRenderModel = None
            else:
                self.m_vecRenderModels.append( pRenderModel )
            openvr.VRRenderModels().freeRenderModel( pModel )
            openvr.VRRenderModels().freeTexture( pTexture )
        return pRenderModel

    def createFrameBuffer(self, nWidth, nHeight, framebufferDesc):
        framebufferDesc.m_nRenderFramebufferId = glGenFramebuffers(1)
        glBindFramebuffer(GL_FRAMEBUFFER, framebufferDesc.m_nRenderFramebufferId)
        framebufferDesc.m_nDepthBufferId = glGenRenderbuffers(1)
        glBindRenderbuffer(GL_RENDERBUFFER, framebufferDesc.m_nDepthBufferId)
        glRenderbufferStorageMultisample(GL_RENDERBUFFER, 4, GL_DEPTH_COMPONENT, nWidth, nHeight )
        glFramebufferRenderbuffer(GL_FRAMEBUFFER, GL_DEPTH_ATTACHMENT, GL_RENDERBUFFER,    framebufferDesc.m_nDepthBufferId )
        framebufferDesc.m_nRenderTextureId = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D_MULTISAMPLE, framebufferDesc.m_nRenderTextureId )
        glTexImage2DMultisample(GL_TEXTURE_2D_MULTISAMPLE, 4, GL_RGBA8, nWidth, nHeight, True)
        glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D_MULTISAMPLE, framebufferDesc.m_nRenderTextureId, 0)
        framebufferDesc.m_nResolveFramebufferId = glGenFramebuffers(1)
        glBindFramebuffer(GL_FRAMEBUFFER, framebufferDesc.m_nResolveFramebufferId)
        framebufferDesc.m_nResolveTextureId = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, framebufferDesc.m_nResolveTextureId )
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAX_LEVEL, 0)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA8, nWidth, nHeight, 0, GL_RGBA, GL_UNSIGNED_BYTE, None)
        glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, framebufferDesc.m_nResolveTextureId, 0)
        # check FBO status
        status = glCheckFramebufferStatus(GL_FRAMEBUFFER)
        if status != GL_FRAMEBUFFER_COMPLETE:
            return False
        glBindFramebuffer( GL_FRAMEBUFFER, 0 )
        return True


def dprintf( message ):
    if g_bPrintf:
        print( message )
    logging.debug(message)


def getTrackedDeviceString( pHmd, unDevice, prop ):
    """
    Purpose: Helper to get a string from a tracked device property and turn it
    into a std.string
    """
    if pHmd is None:
        return ""
    return pHmd.getStringTrackedDeviceProperty( unDevice, prop )


def debugCallback(source, type_arg, id_arg, severity, length, message, userParam):
    dprintf( "GL Error: %s\n" % message )


if __name__ == "__main__":
    pMainApplication = CMainApplication( sys.argv )
    if not pMainApplication.bInit():
        pMainApplication.shutdown()
        sys.exit(1)
    pMainApplication.runMainLoop()
    pMainApplication.shutdown()
    sys.exit(0)
