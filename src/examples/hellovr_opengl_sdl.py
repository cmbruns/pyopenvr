
import time

import openvr


def threadSleep( nMilliseconds ):
	seconds = nMilliseconds / 1000.0
	time.sleep(seconds)


class CGLRenderModel:
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
        glGenVertexArrays( 1, self.m_glVertArray )
        glBindVertexArray( self.m_glVertArray )
        # Populate a vertex buffer
        glGenBuffers( 1, self.m_glVertBuffer )
        glBindBuffer( GL_ARRAY_BUFFER, self.m_glVertBuffer )
        glBufferData( GL_ARRAY_BUFFER, sizeof( openvr.RenderModel_Vertex_t ) * vrModel.unVertexCount, vrModel.rVertexData, GL_STATIC_DRAW )
        # Identify the components in the vertex buffer
        glEnableVertexAttribArray( 0 )
        glVertexAttribPointer( 0, 3, GL_FLOAT, GL_FALSE, sizeof( openvr.RenderModel_Vertex_t ), offsetof( openvr.RenderModel_Vertex_t, vPosition ) )
        glEnableVertexAttribArray( 1 )
        glVertexAttribPointer( 1, 3, GL_FLOAT, GL_FALSE, sizeof( openvr.RenderModel_Vertex_t ), offsetof( openvr.RenderModel_Vertex_t, vNormal ) )
        glEnableVertexAttribArray( 2 )
        glVertexAttribPointer( 2, 2, GL_FLOAT, GL_FALSE, sizeof( openvr.RenderModel_Vertex_t ), offsetof( openvr.RenderModel_Vertex_t, rfTextureCoord ) )
        # Create and populate the index buffer
        glGenBuffers( 1, self.m_glIndexBuffer )
        glBindBuffer( GL_ELEMENT_ARRAY_BUFFER, self.m_glIndexBuffer )
        glBufferData( GL_ELEMENT_ARRAY_BUFFER, sizeof( uint16_t ) * vrModel.unTriangleCount * 3, vrModel.rIndexData, GL_STATIC_DRAW )
        glBindVertexArray( 0 )
        # create and populate the texture
        glGenTextures(1, self.m_glTexture )
        glBindTexture( GL_TEXTURE_2D, self.m_glTexture )
        glTexImage2D( GL_TEXTURE_2D, 0, GL_RGBA, vrDiffuseTexture.unWidth, vrDiffuseTexture.unHeight,
            0, GL_RGBA, GL_UNSIGNED_BYTE, vrDiffuseTexture.rubTextureMapData )
        # If this renders black ask McJohn what's wrong.
        glGenerateMipmap(GL_TEXTURE_2D)
        glTexParameteri( GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE )
        glTexParameteri( GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE )
        glTexParameteri( GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR )
        glTexParameteri( GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR )
        fLargest = glGetFloatv( GL_MAX_TEXTURE_MAX_ANISOTROPY_EXT, fLargest )
        glTexParameterf( GL_TEXTURE_2D, GL_TEXTURE_MAX_ANISOTROPY_EXT, fLargest )
        glBindTexture( GL_TEXTURE_2D, 0 )
        self.m_unVertexCount = vrModel.unTriangleCount * 3
        return True

    def cleanup(self):
        "Purpose: Frees the GL resources for a render model"
        if self.m_glVertBuffer != 0:
            glDeleteBuffers(1, self.m_glIndexBuffer)
            glDeleteVertexArrays( 1, self.m_glVertArray )
            glDeleteBuffers(1, self.m_glVertBuffer)
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


g_bPrintf = True


class CMainApplication:
    def __init__(self, argv):
        self.m_pWindow = None
        self.m_pContext = None
        self.m_nWindowWidth =  1280 
        self.m_nWindowHeight =  720 
        self.m_unSceneProgramID =  0 
        self.m_unLensProgramID =  0 
        self.m_unControllerTransformProgramID =  0 
        self.m_unRenderModelProgramID =  0 
        self.m_pHMD =  None 
        self.m_pRenderModels =  None 
        self.m_bDebugOpenGL =  False 
        self.m_bVerbose =  False 
        self.m_bPerf =  False 
        self.m_bVblank =  False 
        self.m_bGlFinishHack =  True 
        self.m_glControllerVertBuffer =  0 
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
            printf("%s - SDL could not initialize! SDL Error: %s\n", __FUNCTION__, SDL_GetError())
            return False
        # Loading the SteamVR Runtime
        try:
            openvr.init(openvr.VRApplication_Scene)
        except:
            self.m_pHMD = None
            msg = "Unable to init VR runtime: %s" % openvr.VR_GetVRInitErrorAsEnglishDescription( eError )
            SDL_ShowSimpleMessageBox( SDL_MESSAGEBOX_ERROR, "VR_Init Failed", msg, None )
            return False
        self.m_pRenderModels = openvr.VR_GetGenericInterface( openvr.IVRRenderModels_Version, eError )
        if self.m_pRenderModels is None:
            self.m_pHMD = None
            openvr.shutdown()
            msg = "Unable to get render model interface: %s" % openvr.VR_GetVRInitErrorAsEnglishDescription( eError )
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
            printf( "%s - Window could not be created! SDL Error: %s\n", __FUNCTION__, SDL_GetError() )
            return False
        self.m_pContext = SDL_GL_CreateContext(self.m_pWindow)
        if self.m_pContext is None:
            printf( "%s - OpenGL context could not be created! SDL Error: %s\n", __FUNCTION__, SDL_GetError() )
            return False
        glewExperimental = GL_TRUE
        nGlewError = glewInit()
        if nGlewError != GLEW_OK:
            printf( "%s - Error initializing GLEW! %s\n", __FUNCTION__, glewGetErrorString( nGlewError ) )
            return False
        glGetError() # to clear the error caused deep in GLEW
        swap_interval = 1 if self.m_bVblank else 0
        if SDL_GL_SetSwapInterval( swap_interval ) < 0:
            printf( "%s - Warning: Unable to set VSync! SDL Error: %s\n", __FUNCTION__, SDL_GetError() )
            return False
        self.m_strDriver = "No Driver"
        self.m_strDisplay = "No Display"
        self.m_strDriver = GetTrackedDeviceString( self.m_pHMD, openvr.k_unTrackedDeviceIndex_Hmd, openvr.Prop_TrackingSystemName_String )
        self.m_strDisplay = GetTrackedDeviceString( self.m_pHMD, openvr.k_unTrackedDeviceIndex_Hmd, openvr.Prop_SerialNumber_String )
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
        if not BInitGL():
            printf("%s - Unable to initialize OpenGL!\n", __FUNCTION__)
            return False
        if not BInitCompositor():
            printf("%s - Failed to initialize VR Compositor!\n", __FUNCTION__)
            return False
        return True
        
    def bInitGL(self):
        if self.m_bDebugOpenGL:
            glDebugMessageCallback( DebugCallback, None)
            glDebugMessageControl( GL_DONT_CARE, GL_DONT_CARE, GL_DONT_CARE, 0, None, GL_TRUE )
            glEnable(GL_DEBUG_OUTPUT_SYNCHRONOUS)
        if not self.createAllShaders():
            return False
        self.setupTexturemaps()
        self.setupScene()
        self.setupCameras()
        self.setupStereoRenderTargets()
        self.setupDistortion()
        self.setupRenderModels()
        return True
        
        
    bool BInitCompositor()

    void SetupRenderModels()

    void Shutdown()

    void RunMainLoop()
    bool HandleInput()
    void ProcessVREvent( const openvr.VREvent_t & event )
    void RenderFrame()

    bool SetupTexturemaps()

    void SetupScene()
    void AddCubeToScene( Matrix4 mat, std.vector<float> vertdata )
    void AddCubeVertex( float fl0, float fl1, float fl2, float fl3, float fl4, std.vector<float> vertdata )

    void DrawControllers()

    bool SetupStereoRenderTargets()
    void SetupDistortion()
    void SetupCameras()

    void RenderStereoTargets()
    void RenderDistortion()
    void RenderScene( openvr.Hmd_Eye nEye )

    Matrix4 GetHMDMatrixProjectionEye( openvr.Hmd_Eye nEye )
    Matrix4 GetHMDMatrixPoseEye( openvr.Hmd_Eye nEye )
    Matrix4 GetCurrentViewProjectionMatrix( openvr.Hmd_Eye nEye )
    void UpdateHMDMatrixPose()

    Matrix4 ConvertSteamVRMatrixToMatrix4( const openvr.HmdMatrix34_t matPose )

    GLuint CompileGLShader( const char pchShaderName, const char pchVertexShader, const char pchFragmentShader )
    bool CreateAllShaders()

    void SetupRenderModelForTrackedDevice( openvr.TrackedDeviceIndex_t unTrackedDeviceIndex )
    CGLRenderModel FindOrLoadRenderModel( const char pchRenderModelName )

    bool self.m_bDebugOpenGL
    bool self.m_bVerbose
    bool self.m_bPerf
    bool self.m_bVblank
    bool self.m_bGlFinishHack

    openvr.IVRSystem self.m_pHMD
    openvr.IVRRenderModels self.m_pRenderModels
    std.string self.m_strDriver
    std.string self.m_strDisplay
    openvr.TrackedDevicePose_t self.m_rTrackedDevicePose[ openvr.k_unMaxTrackedDeviceCount ]
    Matrix4 self.m_rmat4DevicePose[ openvr.k_unMaxTrackedDeviceCount ]
    bool self.m_rbShowTrackedDevice[ openvr.k_unMaxTrackedDeviceCount ]

    # SDL bookkeeping
    SDL_Window self.m_pWindow
    uint32_t self.m_nWindowWidth
    uint32_t self.m_nWindowHeight

    SDL_GLContext self.m_pContext

    # OpenGL bookkeeping
    int self.m_iTrackedControllerCount
    int self.m_iTrackedControllerCount_Last
    int self.m_iValidPoseCount
    int self.m_iValidPoseCount_Last
    bool self.m_bShowCubes

    std.string self.m_strPoseClasses                            # what classes we saw poses for this frame
    char self.m_rDevClassChar[ openvr.k_unMaxTrackedDeviceCount ]   # for each device, a character representing its class

    int self.m_iSceneVolumeWidth
    int self.m_iSceneVolumeHeight
    int self.m_iSceneVolumeDepth
    float self.m_fScaleSpacing
    float self.m_fScale
    
    int self.m_iSceneVolumeInit                                  # if you want something other than the default 20x20x20
    
    float self.m_fNearClip
    float self.m_fFarClip

    GLuint self.m_iTexture

    unsigned int self.m_uiVertcount

    GLuint self.m_glSceneVertBuffer
    GLuint self.m_unSceneVAO
    GLuint self.m_unLensVAO
    GLuint self.m_glIDVertBuffer
    GLuint self.m_glIDIndexBuffer
    unsigned int self.m_uiIndexSize

    GLuint self.m_glControllerVertBuffer
    GLuint self.m_unControllerVAO
    unsigned int self.m_uiControllerVertcount

    Matrix4 self.m_mat4HMDPose
    Matrix4 self.m_mat4eyePosLeft
    Matrix4 self.m_mat4eyePosRight

    Matrix4 self.m_mat4ProjectionCenter
    Matrix4 self.m_mat4ProjectionLeft
    Matrix4 self.m_mat4ProjectionRight

    struct VertexDataScene
    
        Vector3 position
        Vector2 texCoord
    

    struct VertexDataLens
    
        Vector2 position
        Vector2 texCoordRed
        Vector2 texCoordGreen
        Vector2 texCoordBlue
    

    GLuint self.m_unSceneProgramID
    GLuint self.m_unLensProgramID
    GLuint self.m_unControllerTransformProgramID
    GLuint self.m_unRenderModelProgramID

    GLint self.m_nSceneMatrixLocation
    GLint self.m_nControllerMatrixLocation
    GLint self.m_nRenderModelMatrixLocation

    struct FramebufferDesc
    
        GLuint self.m_nDepthBufferId
        GLuint self.m_nRenderTextureId
        GLuint self.m_nRenderFramebufferId
        GLuint self.m_nResolveTextureId
        GLuint self.m_nResolveFramebufferId
    
    FramebufferDesc leftEyeDesc
    FramebufferDesc rightEyeDesc

    bool CreateFrameBuffer( int nWidth, int nHeight, FramebufferDesc framebufferDesc )
    
    uint32_t self.m_nRenderWidth
    uint32_t self.m_nRenderHeight

    std.vector< CGLRenderModel * > self.m_vecRenderModels
    CGLRenderModel self.m_rTrackedDeviceToRenderModel[ openvr.k_unMaxTrackedDeviceCount ]


#-----------------------------------------------------------------------------
# Purpose:
#-----------------------------------------------------------------------------
void dprintf( const char fmt, ... )

    va_list args
    char buffer[ 2048 ]

    va_start( args, fmt )
    vsprintf_s( buffer, fmt, args )
    va_end( args )

    if ( g_bPrintf )
        printf( "%s", buffer )

    OutputDebugStringA( buffer )


#-----------------------------------------------------------------------------
# Purpose: Helper to get a string from a tracked device property and turn it
#            into a std.string
#-----------------------------------------------------------------------------
std.string GetTrackedDeviceString( openvr.IVRSystem pHmd, openvr.TrackedDeviceIndex_t unDevice, openvr.TrackedDeviceProperty prop, openvr.TrackedPropertyError peError = None )

    uint32_t unRequiredBufferLen = pHmd.GetStringTrackedDeviceProperty( unDevice, prop, None, 0, peError )
    if( unRequiredBufferLen == 0 )
        return ""

    char pchBuffer = char[ unRequiredBufferLen ]
    unRequiredBufferLen = pHmd.GetStringTrackedDeviceProperty( unDevice, prop, pchBuffer, unRequiredBufferLen, peError )
    std.string sResult = pchBuffer
    delete [] pchBuffer
    return sResult



#-----------------------------------------------------------------------------
# Purpose:
#-----------------------------------------------------------------------------
bool CMainApplication.BInit()

    if ( SDL_Init( SDL_INIT_VIDEO | SDL_INIT_TIMER ) < 0 )
    
        printf("%s - SDL could not initialize! SDL Error: %s\n", __FUNCTION__, SDL_GetError())
        return False
    

    # Loading the SteamVR Runtime
    openvr.EVRInitError eError = openvr.VRInitError_None
    self.m_pHMD = openvr.VR_Init( eError, openvr.VRApplication_Scene )

    if ( eError != openvr.VRInitError_None )
    
        self.m_pHMD = None
        char buf[1024]
        sprintf_s( buf, sizeof( buf ), "Unable to init VR runtime: %s", openvr.VR_GetVRInitErrorAsEnglishDescription( eError ) )
        SDL_ShowSimpleMessageBox( SDL_MESSAGEBOX_ERROR, "VR_Init Failed", buf, None )
        return False
    


    self.m_pRenderModels = (openvr.IVRRenderModels *)openvr.VR_GetGenericInterface( openvr.IVRRenderModels_Version, eError )
    if( !self.m_pRenderModels )
    
        self.m_pHMD = None
        openvr.VR_Shutdown()

        char buf[1024]
        sprintf_s( buf, sizeof( buf ), "Unable to get render model interface: %s", openvr.VR_GetVRInitErrorAsEnglishDescription( eError ) )
        SDL_ShowSimpleMessageBox( SDL_MESSAGEBOX_ERROR, "VR_Init Failed", buf, None )
        return False
    

    int nWindowPosX = 700
    int nWindowPosY = 100
    self.m_nWindowWidth = 1280
    self.m_nWindowHeight = 720
    Uint32 unWindowFlags = SDL_WINDOW_OPENGL | SDL_WINDOW_SHOWN

    SDL_GL_SetAttribute( SDL_GL_CONTEXT_MAJOR_VERSION, 4 )
    SDL_GL_SetAttribute( SDL_GL_CONTEXT_MINOR_VERSION, 1 )
    #SDL_GL_SetAttribute( SDL_GL_CONTEXT_PROFILE_MASK, SDL_GL_CONTEXT_PROFILE_COMPATIBILITY )
    SDL_GL_SetAttribute( SDL_GL_CONTEXT_PROFILE_MASK, SDL_GL_CONTEXT_PROFILE_CORE )

    SDL_GL_SetAttribute( SDL_GL_MULTISAMPLEBUFFERS, 0 )
    SDL_GL_SetAttribute( SDL_GL_MULTISAMPLESAMPLES, 0 )
    if( self.m_bDebugOpenGL )
        SDL_GL_SetAttribute( SDL_GL_CONTEXT_FLAGS, SDL_GL_CONTEXT_DEBUG_FLAG )

    self.m_pWindow = SDL_CreateWindow( "hellovr_sdl", nWindowPosX, nWindowPosY, self.m_nWindowWidth, self.m_nWindowHeight, unWindowFlags )
    if (self.m_pWindow == None)
    
        printf( "%s - Window could not be created! SDL Error: %s\n", __FUNCTION__, SDL_GetError() )
        return False
    

    self.m_pContext = SDL_GL_CreateContext(self.m_pWindow)
    if (self.m_pContext == None)
    
        printf( "%s - OpenGL context could not be created! SDL Error: %s\n", __FUNCTION__, SDL_GetError() )
        return False
    

    glewExperimental = GL_TRUE
    GLenum nGlewError = glewInit()
    if (nGlewError != GLEW_OK)
    
        printf( "%s - Error initializing GLEW! %s\n", __FUNCTION__, glewGetErrorString( nGlewError ) )
        return False
    
    glGetError() # to clear the error caused deep in GLEW

    if ( SDL_GL_SetSwapInterval( self.m_bVblank ? 1 : 0 ) < 0 )
    
        printf( "%s - Warning: Unable to set VSync! SDL Error: %s\n", __FUNCTION__, SDL_GetError() )
        return False
    


    self.m_strDriver = "No Driver"
    self.m_strDisplay = "No Display"

    self.m_strDriver = GetTrackedDeviceString( self.m_pHMD, openvr.k_unTrackedDeviceIndex_Hmd, openvr.Prop_TrackingSystemName_String )
    self.m_strDisplay = GetTrackedDeviceString( self.m_pHMD, openvr.k_unTrackedDeviceIndex_Hmd, openvr.Prop_SerialNumber_String )

    std.string strWindowTitle = "hellovr_sdl - " + self.m_strDriver + " " + self.m_strDisplay
    SDL_SetWindowTitle( self.m_pWindow, strWindowTitle.c_str() )
    
    # cube array
     self.m_iSceneVolumeWidth = self.m_iSceneVolumeInit
     self.m_iSceneVolumeHeight = self.m_iSceneVolumeInit
     self.m_iSceneVolumeDepth = self.m_iSceneVolumeInit
         
     self.m_fScale = 0.3f
     self.m_fScaleSpacing = 4.0f
 
     self.m_fNearClip = 0.1f
     self.m_fFarClip = 30.0f
 
     self.m_iTexture = 0
     self.m_uiVertcount = 0
 
#         self.m_MillisecondsTimer.start(1, this)
#         self.m_SecondsTimer.start(1000, this)
    
    if (!BInitGL())
    
        printf("%s - Unable to initialize OpenGL!\n", __FUNCTION__)
        return False
    

    if (!BInitCompositor())
    
        printf("%s - Failed to initialize VR Compositor!\n", __FUNCTION__)
        return False
    

    return True



#-----------------------------------------------------------------------------
# Purpose:
#-----------------------------------------------------------------------------
void APIENTRY DebugCallback(GLenum source, GLenum type, GLuint id, GLenum severity, GLsizei length, const char* message, const void* userParam)

    dprintf( "GL Error: %s\n", message )


#-----------------------------------------------------------------------------
# Purpose:
#-----------------------------------------------------------------------------
bool CMainApplication.BInitCompositor()

    openvr.EVRInitError peError = openvr.VRInitError_None

    if ( !openvr.VRCompositor() )
    
        printf( "Compositor initialization failed. See log file for details\n" )
        return False
    

    return True



#-----------------------------------------------------------------------------
# Purpose:
#-----------------------------------------------------------------------------
void CMainApplication.Shutdown()

    if( self.m_pHMD )
    
        openvr.VR_Shutdown()
        self.m_pHMD = None
    

    for( std.vector< CGLRenderModel * >.iterator i = self.m_vecRenderModels.begin() i != self.m_vecRenderModels.end() i++ )
    
        delete (*i)
    
    self.m_vecRenderModels.clear()
    
    if( self.m_pContext )
    
        glDebugMessageControl( GL_DONT_CARE, GL_DONT_CARE, GL_DONT_CARE, 0, None, GL_FALSE )
        glDebugMessageCallback(None, None)
        glDeleteBuffers(1, self.m_glSceneVertBuffer)
        glDeleteBuffers(1, self.m_glIDVertBuffer)
        glDeleteBuffers(1, self.m_glIDIndexBuffer)

        if ( self.m_unSceneProgramID )
        
            glDeleteProgram( self.m_unSceneProgramID )
        
        if ( self.m_unControllerTransformProgramID )
        
            glDeleteProgram( self.m_unControllerTransformProgramID )
        
        if ( self.m_unRenderModelProgramID )
        
            glDeleteProgram( self.m_unRenderModelProgramID )
        
        if ( self.m_unLensProgramID )
        
            glDeleteProgram( self.m_unLensProgramID )
        

        glDeleteRenderbuffers( 1, leftEyeDesc.self.m_nDepthBufferId )
        glDeleteTextures( 1, leftEyeDesc.self.m_nRenderTextureId )
        glDeleteFramebuffers( 1, leftEyeDesc.self.m_nRenderFramebufferId )
        glDeleteTextures( 1, leftEyeDesc.self.m_nResolveTextureId )
        glDeleteFramebuffers( 1, leftEyeDesc.self.m_nResolveFramebufferId )

        glDeleteRenderbuffers( 1, rightEyeDesc.self.m_nDepthBufferId )
        glDeleteTextures( 1, rightEyeDesc.self.m_nRenderTextureId )
        glDeleteFramebuffers( 1, rightEyeDesc.self.m_nRenderFramebufferId )
        glDeleteTextures( 1, rightEyeDesc.self.m_nResolveTextureId )
        glDeleteFramebuffers( 1, rightEyeDesc.self.m_nResolveFramebufferId )

        if( self.m_unLensVAO != 0 )
        
            glDeleteVertexArrays( 1, self.m_unLensVAO )
        
        if( self.m_unSceneVAO != 0 )
        
            glDeleteVertexArrays( 1, self.m_unSceneVAO )
        
        if( self.m_unControllerVAO != 0 )
        
            glDeleteVertexArrays( 1, self.m_unControllerVAO )
        
    

    if( self.m_pWindow )
    
        SDL_DestroyWindow(self.m_pWindow)
        self.m_pWindow = None
    

    SDL_Quit()


#-----------------------------------------------------------------------------
# Purpose:
#-----------------------------------------------------------------------------
bool CMainApplication.HandleInput()

    SDL_Event sdlEvent
    bool bRet = False

    while ( SDL_PollEvent( sdlEvent ) != 0 )
    
        if ( sdlEvent.type == SDL_QUIT )
        
            bRet = True
        
        else if ( sdlEvent.type == SDL_KEYDOWN )
        
            if ( sdlEvent.key.keysym.sym == SDLK_ESCAPE 
                 || sdlEvent.key.keysym.sym == SDLK_q )
            
                bRet = True
            
            if( sdlEvent.key.keysym.sym == SDLK_c )
            
                self.m_bShowCubes = !self.m_bShowCubes
            
        
    

    # Process SteamVR events
    openvr.VREvent_t event
    while( self.m_pHMD.PollNextEvent( event, sizeof( event ) ) )
    
        ProcessVREvent( event )
    

    # Process SteamVR controller state
    for( openvr.TrackedDeviceIndex_t unDevice = 0 unDevice < openvr.k_unMaxTrackedDeviceCount unDevice++ )
    
        openvr.VRControllerState_t state
        if( self.m_pHMD.GetControllerState( unDevice, state ) )
        
            self.m_rbShowTrackedDevice[ unDevice ] = state.ulButtonPressed == 0
        
    

    return bRet


#-----------------------------------------------------------------------------
# Purpose:
#-----------------------------------------------------------------------------
void CMainApplication.RunMainLoop()

    bool bQuit = False

    SDL_StartTextInput()
    SDL_ShowCursor( SDL_DISABLE )

    while ( !bQuit )
    
        bQuit = HandleInput()

        RenderFrame()
    

    SDL_StopTextInput()



#-----------------------------------------------------------------------------
# Purpose: Processes a single VR event
#-----------------------------------------------------------------------------
void CMainApplication.ProcessVREvent( const openvr.VREvent_t & event )

    switch( event.eventType )
    
    case openvr.VREvent_TrackedDeviceActivated:
        
            SetupRenderModelForTrackedDevice( event.trackedDeviceIndex )
            dprintf( "Device %u attached. Setting up render model.\n", event.trackedDeviceIndex )
        
        break
    case openvr.VREvent_TrackedDeviceDeactivated:
        
            dprintf( "Device %u detached.\n", event.trackedDeviceIndex )
        
        break
    case openvr.VREvent_TrackedDeviceUpdated:
        
            dprintf( "Device %u updated.\n", event.trackedDeviceIndex )
        
        break
    



#-----------------------------------------------------------------------------
# Purpose:
#-----------------------------------------------------------------------------
void CMainApplication.RenderFrame()

    # for now as fast as possible
    if ( self.m_pHMD )
    
        DrawControllers()
        RenderStereoTargets()
        RenderDistortion()

        openvr.Texture_t leftEyeTexture = (void*)leftEyeDesc.self.m_nResolveTextureId, openvr.API_OpenGL, openvr.ColorSpace_Gamma 
        openvr.VRCompositor().Submit(openvr.Eye_Left, leftEyeTexture )
        openvr.Texture_t rightEyeTexture = (void*)rightEyeDesc.self.m_nResolveTextureId, openvr.API_OpenGL, openvr.ColorSpace_Gamma 
        openvr.VRCompositor().Submit(openvr.Eye_Right, rightEyeTexture )
    

    if ( self.m_bVblank && self.m_bGlFinishHack )
    
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
    if ( self.m_bVblank )
    
        glFlush()
        glFinish()
    

    # Spew out the controller and pose count whenever they change.
    if ( self.m_iTrackedControllerCount != self.m_iTrackedControllerCount_Last || self.m_iValidPoseCount != self.m_iValidPoseCount_Last )
    
        self.m_iValidPoseCount_Last = self.m_iValidPoseCount
        self.m_iTrackedControllerCount_Last = self.m_iTrackedControllerCount
        
        dprintf( "PoseCount:%d(%s) Controllers:%d\n", self.m_iValidPoseCount, self.m_strPoseClasses.c_str(), self.m_iTrackedControllerCount )
    

    UpdateHMDMatrixPose()



#-----------------------------------------------------------------------------
# Purpose: Compiles a GL shader program and returns the handle. Returns 0 if
#            the shader couldn't be compiled for some reason.
#-----------------------------------------------------------------------------
GLuint CMainApplication.CompileGLShader( const char pchShaderName, const char pchVertexShader, const char pchFragmentShader )

    GLuint unProgramID = glCreateProgram()

    GLuint nSceneVertexShader = glCreateShader(GL_VERTEX_SHADER)
    glShaderSource( nSceneVertexShader, 1, pchVertexShader, None)
    glCompileShader( nSceneVertexShader )

    GLint vShaderCompiled = GL_FALSE
    glGetShaderiv( nSceneVertexShader, GL_COMPILE_STATUS, vShaderCompiled)
    if ( vShaderCompiled != GL_TRUE)
    
        dprintf("%s - Unable to compile vertex shader %d!\n", pchShaderName, nSceneVertexShader)
        glDeleteProgram( unProgramID )
        glDeleteShader( nSceneVertexShader )
        return 0
    
    glAttachShader( unProgramID, nSceneVertexShader)
    glDeleteShader( nSceneVertexShader ) # the program hangs onto this once it's attached

    GLuint  nSceneFragmentShader = glCreateShader(GL_FRAGMENT_SHADER)
    glShaderSource( nSceneFragmentShader, 1, pchFragmentShader, None)
    glCompileShader( nSceneFragmentShader )

    GLint fShaderCompiled = GL_FALSE
    glGetShaderiv( nSceneFragmentShader, GL_COMPILE_STATUS, fShaderCompiled)
    if (fShaderCompiled != GL_TRUE)
    
        dprintf("%s - Unable to compile fragment shader %d!\n", pchShaderName, nSceneFragmentShader )
        glDeleteProgram( unProgramID )
        glDeleteShader( nSceneFragmentShader )
        return 0    
    

    glAttachShader( unProgramID, nSceneFragmentShader )
    glDeleteShader( nSceneFragmentShader ) # the program hangs onto this once it's attached

    glLinkProgram( unProgramID )

    GLint programSuccess = GL_TRUE
    glGetProgramiv( unProgramID, GL_LINK_STATUS, programSuccess)
    if ( programSuccess != GL_TRUE )
    
        dprintf("%s - Error linking program %d!\n", pchShaderName, unProgramID)
        glDeleteProgram( unProgramID )
        return 0
    

    glUseProgram( unProgramID )
    glUseProgram( 0 )

    return unProgramID



#-----------------------------------------------------------------------------
# Purpose: Creates all the shaders used by HelloVR SDL
#-----------------------------------------------------------------------------
bool CMainApplication.CreateAllShaders()

    self.m_unSceneProgramID = CompileGLShader( 
        "Scene",

        # Vertex Shader
        "#version 410\n"
        "uniform mat4 matrix\n"
        "layout(location = 0) in vec4 position\n"
        "layout(location = 1) in vec2 v2UVcoordsIn\n"
        "layout(location = 2) in vec3 v3NormalIn\n"
        "out vec2 v2UVcoords\n"
        "void main()\n"
        "\n"
        "    v2UVcoords = v2UVcoordsIn\n"
        "    gl_Position = matrix * position\n"
        "\n",

        # Fragment Shader
        "#version 410 core\n"
        "uniform sampler2D mytexture\n"
        "in vec2 v2UVcoords\n"
        "out vec4 outputColor\n"
        "void main()\n"
        "\n"
        "   outputColor = texture(mytexture, v2UVcoords)\n"
        "\n"
        )
    self.m_nSceneMatrixLocation = glGetUniformLocation( self.m_unSceneProgramID, "matrix" )
    if( self.m_nSceneMatrixLocation == -1 )
    
        dprintf( "Unable to find matrix uniform in scene shader\n" )
        return False
    

    self.m_unControllerTransformProgramID = CompileGLShader(
        "Controller",

        # vertex shader
        "#version 410\n"
        "uniform mat4 matrix\n"
        "layout(location = 0) in vec4 position\n"
        "layout(location = 1) in vec3 v3ColorIn\n"
        "out vec4 v4Color\n"
        "void main()\n"
        "\n"
        "    v4Color.xyz = v3ColorIn v4Color.a = 1.0\n"
        "    gl_Position = matrix * position\n"
        "\n",

        # fragment shader
        "#version 410\n"
        "in vec4 v4Color\n"
        "out vec4 outputColor\n"
        "void main()\n"
        "\n"
        "   outputColor = v4Color\n"
        "\n"
        )
    self.m_nControllerMatrixLocation = glGetUniformLocation( self.m_unControllerTransformProgramID, "matrix" )
    if( self.m_nControllerMatrixLocation == -1 )
    
        dprintf( "Unable to find matrix uniform in controller shader\n" )
        return False
    

    self.m_unRenderModelProgramID = CompileGLShader( 
        "render model",

        # vertex shader
        "#version 410\n"
        "uniform mat4 matrix\n"
        "layout(location = 0) in vec4 position\n"
        "layout(location = 1) in vec3 v3NormalIn\n"
        "layout(location = 2) in vec2 v2TexCoordsIn\n"
        "out vec2 v2TexCoord\n"
        "void main()\n"
        "\n"
        "    v2TexCoord = v2TexCoordsIn\n"
        "    gl_Position = matrix * vec4(position.xyz, 1)\n"
        "\n",

        #fragment shader
        "#version 410 core\n"
        "uniform sampler2D diffuse\n"
        "in vec2 v2TexCoord\n"
        "out vec4 outputColor\n"
        "void main()\n"
        "\n"
        "   outputColor = texture( diffuse, v2TexCoord)\n"
        "\n"

        )
    self.m_nRenderModelMatrixLocation = glGetUniformLocation( self.m_unRenderModelProgramID, "matrix" )
    if( self.m_nRenderModelMatrixLocation == -1 )
    
        dprintf( "Unable to find matrix uniform in render model shader\n" )
        return False
    

    self.m_unLensProgramID = CompileGLShader(
        "Distortion",

        # vertex shader
        "#version 410 core\n"
        "layout(location = 0) in vec4 position\n"
        "layout(location = 1) in vec2 v2UVredIn\n"
        "layout(location = 2) in vec2 v2UVGreenIn\n"
        "layout(location = 3) in vec2 v2UVblueIn\n"
        "noperspective  out vec2 v2UVred\n"
        "noperspective  out vec2 v2UVgreen\n"
        "noperspective  out vec2 v2UVblue\n"
        "void main()\n"
        "\n"
        "    v2UVred = v2UVredIn\n"
        "    v2UVgreen = v2UVGreenIn\n"
        "    v2UVblue = v2UVblueIn\n"
        "    gl_Position = position\n"
        "\n",

        # fragment shader
        "#version 410 core\n"
        "uniform sampler2D mytexture\n"

        "noperspective  in vec2 v2UVred\n"
        "noperspective  in vec2 v2UVgreen\n"
        "noperspective  in vec2 v2UVblue\n"

        "out vec4 outputColor\n"

        "void main()\n"
        "\n"
        "    float fBoundsCheck = ( (dot( vec2( lessThan( v2UVgreen.xy, vec2(0.05, 0.05)) ), vec2(1.0, 1.0))+dot( vec2( greaterThan( v2UVgreen.xy, vec2( 0.95, 0.95)) ), vec2(1.0, 1.0))) )\n"
        "    if( fBoundsCheck > 1.0 )\n"
        "     outputColor = vec4( 0, 0, 0, 1.0 ) \n"
        "    else\n"
        "    \n"
        "        float red = texture(mytexture, v2UVred).x\n"
        "        float green = texture(mytexture, v2UVgreen).y\n"
        "        float blue = texture(mytexture, v2UVblue).z\n"
        "        outputColor = vec4( red, green, blue, 1.0  ) \n"
        "\n"
        )


    return self.m_unSceneProgramID != 0 
        && self.m_unControllerTransformProgramID != 0
        && self.m_unRenderModelProgramID != 0
        && self.m_unLensProgramID != 0



#-----------------------------------------------------------------------------
# Purpose:
#-----------------------------------------------------------------------------
bool CMainApplication.SetupTexturemaps()

    std.string sExecutableDirectory = Path_StripFilename( Path_GetExecutablePath() )
    std.string strFullPath = Path_MakeAbsolute( "../cube_texture.png", sExecutableDirectory )
    
    std.vector<unsigned char> imageRGBA
    unsigned nImageWidth, nImageHeight
    unsigned nError = lodepng.decode( imageRGBA, nImageWidth, nImageHeight, strFullPath.c_str() )
    
    if ( nError != 0 )
        return False

    glGenTextures(1, self.m_iTexture )
    glBindTexture( GL_TEXTURE_2D, self.m_iTexture )

    glTexImage2D( GL_TEXTURE_2D, 0, GL_RGBA, nImageWidth, nImageHeight,
        0, GL_RGBA, GL_UNSIGNED_BYTE, imageRGBA[0] )

    glGenerateMipmap(GL_TEXTURE_2D)

    glTexParameteri( GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE )
    glTexParameteri( GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE )
    glTexParameteri( GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR )
    glTexParameteri( GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR )

    GLfloat fLargest
    glGetFloatv(GL_MAX_TEXTURE_MAX_ANISOTROPY_EXT, fLargest)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAX_ANISOTROPY_EXT, fLargest)
         
    glBindTexture( GL_TEXTURE_2D, 0 )

    return ( self.m_iTexture != 0 )



#-----------------------------------------------------------------------------
# Purpose: create a sea of cubes
#-----------------------------------------------------------------------------
void CMainApplication.SetupScene()

    if ( !self.m_pHMD )
        return

    std.vector<float> vertdataarray

    Matrix4 matScale
    matScale.scale( self.m_fScale, self.m_fScale, self.m_fScale )
    Matrix4 matTransform
    matTransform.translate(
        -( (float)self.m_iSceneVolumeWidth * self.m_fScaleSpacing ) / 2.f,
        -( (float)self.m_iSceneVolumeHeight * self.m_fScaleSpacing ) / 2.f,
        -( (float)self.m_iSceneVolumeDepth * self.m_fScaleSpacing ) / 2.f)
    
    Matrix4 mat = matScale * matTransform

    for( int z = 0 z< self.m_iSceneVolumeDepth z++ )
    
        for( int y = 0 y< self.m_iSceneVolumeHeight y++ )
        
            for( int x = 0 x< self.m_iSceneVolumeWidth x++ )
            
                AddCubeToScene( mat, vertdataarray )
                mat = mat * Matrix4().translate( self.m_fScaleSpacing, 0, 0 )
            
            mat = mat * Matrix4().translate( -((float)self.m_iSceneVolumeWidth) * self.m_fScaleSpacing, self.m_fScaleSpacing, 0 )
        
        mat = mat * Matrix4().translate( 0, -((float)self.m_iSceneVolumeHeight) * self.m_fScaleSpacing, self.m_fScaleSpacing )
    
    self.m_uiVertcount = vertdataarray.size()/5
    
    glGenVertexArrays( 1, self.m_unSceneVAO )
    glBindVertexArray( self.m_unSceneVAO )

    glGenBuffers( 1, self.m_glSceneVertBuffer )
    glBindBuffer( GL_ARRAY_BUFFER, self.m_glSceneVertBuffer )
    glBufferData( GL_ARRAY_BUFFER, sizeof(float) * vertdataarray.size(), vertdataarray[0], GL_STATIC_DRAW)

    glBindBuffer( GL_ARRAY_BUFFER, self.m_glSceneVertBuffer )

    GLsizei stride = sizeof(VertexDataScene)
    uintptr_t offset = 0

    glEnableVertexAttribArray( 0 )
    glVertexAttribPointer( 0, 3, GL_FLOAT, GL_FALSE, stride , (const void *)offset)

    offset += sizeof(Vector3)
    glEnableVertexAttribArray( 1 )
    glVertexAttribPointer( 1, 2, GL_FLOAT, GL_FALSE, stride, (const void *)offset)

    glBindVertexArray( 0 )
    glDisableVertexAttribArray(0)
    glDisableVertexAttribArray(1)




#-----------------------------------------------------------------------------
# Purpose:
#-----------------------------------------------------------------------------
void CMainApplication.AddCubeVertex( float fl0, float fl1, float fl2, float fl3, float fl4, std.vector<float> vertdata )

    vertdata.push_back( fl0 )
    vertdata.push_back( fl1 )
    vertdata.push_back( fl2 )
    vertdata.push_back( fl3 )
    vertdata.push_back( fl4 )



#-----------------------------------------------------------------------------
# Purpose:
#-----------------------------------------------------------------------------
void CMainApplication.AddCubeToScene( Matrix4 mat, std.vector<float> vertdata )

    # Matrix4 mat( outermat.data() )

    Vector4 A = mat * Vector4( 0, 0, 0, 1 )
    Vector4 B = mat * Vector4( 1, 0, 0, 1 )
    Vector4 C = mat * Vector4( 1, 1, 0, 1 )
    Vector4 D = mat * Vector4( 0, 1, 0, 1 )
    Vector4 E = mat * Vector4( 0, 0, 1, 1 )
    Vector4 F = mat * Vector4( 1, 0, 1, 1 )
    Vector4 G = mat * Vector4( 1, 1, 1, 1 )
    Vector4 H = mat * Vector4( 0, 1, 1, 1 )

    # triangles instead of quads
    AddCubeVertex( E.x, E.y, E.z, 0, 1, vertdata ) #Front
    AddCubeVertex( F.x, F.y, F.z, 1, 1, vertdata )
    AddCubeVertex( G.x, G.y, G.z, 1, 0, vertdata )
    AddCubeVertex( G.x, G.y, G.z, 1, 0, vertdata )
    AddCubeVertex( H.x, H.y, H.z, 0, 0, vertdata )
    AddCubeVertex( E.x, E.y, E.z, 0, 1, vertdata )
                     
    AddCubeVertex( B.x, B.y, B.z, 0, 1, vertdata ) #Back
    AddCubeVertex( A.x, A.y, A.z, 1, 1, vertdata )
    AddCubeVertex( D.x, D.y, D.z, 1, 0, vertdata )
    AddCubeVertex( D.x, D.y, D.z, 1, 0, vertdata )
    AddCubeVertex( C.x, C.y, C.z, 0, 0, vertdata )
    AddCubeVertex( B.x, B.y, B.z, 0, 1, vertdata )
                    
    AddCubeVertex( H.x, H.y, H.z, 0, 1, vertdata ) #Top
    AddCubeVertex( G.x, G.y, G.z, 1, 1, vertdata )
    AddCubeVertex( C.x, C.y, C.z, 1, 0, vertdata )
    AddCubeVertex( C.x, C.y, C.z, 1, 0, vertdata )
    AddCubeVertex( D.x, D.y, D.z, 0, 0, vertdata )
    AddCubeVertex( H.x, H.y, H.z, 0, 1, vertdata )
                
    AddCubeVertex( A.x, A.y, A.z, 0, 1, vertdata ) #Bottom
    AddCubeVertex( B.x, B.y, B.z, 1, 1, vertdata )
    AddCubeVertex( F.x, F.y, F.z, 1, 0, vertdata )
    AddCubeVertex( F.x, F.y, F.z, 1, 0, vertdata )
    AddCubeVertex( E.x, E.y, E.z, 0, 0, vertdata )
    AddCubeVertex( A.x, A.y, A.z, 0, 1, vertdata )
                    
    AddCubeVertex( A.x, A.y, A.z, 0, 1, vertdata ) #Left
    AddCubeVertex( E.x, E.y, E.z, 1, 1, vertdata )
    AddCubeVertex( H.x, H.y, H.z, 1, 0, vertdata )
    AddCubeVertex( H.x, H.y, H.z, 1, 0, vertdata )
    AddCubeVertex( D.x, D.y, D.z, 0, 0, vertdata )
    AddCubeVertex( A.x, A.y, A.z, 0, 1, vertdata )

    AddCubeVertex( F.x, F.y, F.z, 0, 1, vertdata ) #Right
    AddCubeVertex( B.x, B.y, B.z, 1, 1, vertdata )
    AddCubeVertex( C.x, C.y, C.z, 1, 0, vertdata )
    AddCubeVertex( C.x, C.y, C.z, 1, 0, vertdata )
    AddCubeVertex( G.x, G.y, G.z, 0, 0, vertdata )
    AddCubeVertex( F.x, F.y, F.z, 0, 1, vertdata )



#-----------------------------------------------------------------------------
# Purpose: Draw all of the controllers as X/Y/Z lines
#-----------------------------------------------------------------------------
void CMainApplication.DrawControllers()

    # don't draw controllers if somebody else has input focus
    if( self.m_pHMD.IsInputFocusCapturedByAnotherProcess() )
        return

    std.vector<float> vertdataarray

    self.m_uiControllerVertcount = 0
    self.m_iTrackedControllerCount = 0

    for ( openvr.TrackedDeviceIndex_t unTrackedDevice = openvr.k_unTrackedDeviceIndex_Hmd + 1 unTrackedDevice < openvr.k_unMaxTrackedDeviceCount ++unTrackedDevice )
    
        if ( !self.m_pHMD.IsTrackedDeviceConnected( unTrackedDevice ) )
            continue

        if( self.m_pHMD.GetTrackedDeviceClass( unTrackedDevice ) != openvr.TrackedDeviceClass_Controller )
            continue

        self.m_iTrackedControllerCount += 1

        if( !self.m_rTrackedDevicePose[ unTrackedDevice ].bPoseIsValid )
            continue

        const Matrix4 & mat = self.m_rmat4DevicePose[unTrackedDevice]

        Vector4 center = mat * Vector4( 0, 0, 0, 1 )

        for ( int i = 0 i < 3 ++i )
        
            Vector3 color( 0, 0, 0 )
            Vector4 point( 0, 0, 0, 1 )
            point[i] += 0.05f  # offset in X, Y, Z
            color[i] = 1.0  # R, G, B
            point = mat * point
            vertdataarray.push_back( center.x )
            vertdataarray.push_back( center.y )
            vertdataarray.push_back( center.z )

            vertdataarray.push_back( color.x )
            vertdataarray.push_back( color.y )
            vertdataarray.push_back( color.z )
        
            vertdataarray.push_back( point.x )
            vertdataarray.push_back( point.y )
            vertdataarray.push_back( point.z )
        
            vertdataarray.push_back( color.x )
            vertdataarray.push_back( color.y )
            vertdataarray.push_back( color.z )
        
            self.m_uiControllerVertcount += 2
        

        Vector4 start = mat * Vector4( 0, 0, -0.02f, 1 )
        Vector4 end = mat * Vector4( 0, 0, -39.f, 1 )
        Vector3 color( .92f, .92f, .71f )

        vertdataarray.push_back( start.x )vertdataarray.push_back( start.y )vertdataarray.push_back( start.z )
        vertdataarray.push_back( color.x )vertdataarray.push_back( color.y )vertdataarray.push_back( color.z )

        vertdataarray.push_back( end.x )vertdataarray.push_back( end.y )vertdataarray.push_back( end.z )
        vertdataarray.push_back( color.x )vertdataarray.push_back( color.y )vertdataarray.push_back( color.z )
        self.m_uiControllerVertcount += 2
    

    # Setup the VAO the first time through.
    if ( self.m_unControllerVAO == 0 )
    
        glGenVertexArrays( 1, self.m_unControllerVAO )
        glBindVertexArray( self.m_unControllerVAO )

        glGenBuffers( 1, self.m_glControllerVertBuffer )
        glBindBuffer( GL_ARRAY_BUFFER, self.m_glControllerVertBuffer )

        GLuint stride = 2 * 3 * sizeof( float )
        GLuint offset = 0

        glEnableVertexAttribArray( 0 )
        glVertexAttribPointer( 0, 3, GL_FLOAT, GL_FALSE, stride, (const void *)offset)

        offset += sizeof( Vector3 )
        glEnableVertexAttribArray( 1 )
        glVertexAttribPointer( 1, 3, GL_FLOAT, GL_FALSE, stride, (const void *)offset)

        glBindVertexArray( 0 )
    

    glBindBuffer( GL_ARRAY_BUFFER, self.m_glControllerVertBuffer )

    # set vertex data if we have some
    if( vertdataarray.size() > 0 )
    
        #$ TODO: Use glBufferSubData for this...
        glBufferData( GL_ARRAY_BUFFER, sizeof(float) * vertdataarray.size(), vertdataarray[0], GL_STREAM_DRAW )
    



#-----------------------------------------------------------------------------
# Purpose:
#-----------------------------------------------------------------------------
void CMainApplication.SetupCameras()

    self.m_mat4ProjectionLeft = GetHMDMatrixProjectionEye( openvr.Eye_Left )
    self.m_mat4ProjectionRight = GetHMDMatrixProjectionEye( openvr.Eye_Right )
    self.m_mat4eyePosLeft = GetHMDMatrixPoseEye( openvr.Eye_Left )
    self.m_mat4eyePosRight = GetHMDMatrixPoseEye( openvr.Eye_Right )



#-----------------------------------------------------------------------------
# Purpose:
#-----------------------------------------------------------------------------
bool CMainApplication.CreateFrameBuffer( int nWidth, int nHeight, FramebufferDesc framebufferDesc )

    glGenFramebuffers(1, framebufferDesc.self.m_nRenderFramebufferId )
    glBindFramebuffer(GL_FRAMEBUFFER, framebufferDesc.self.m_nRenderFramebufferId)

    glGenRenderbuffers(1, framebufferDesc.self.m_nDepthBufferId)
    glBindRenderbuffer(GL_RENDERBUFFER, framebufferDesc.self.m_nDepthBufferId)
    glRenderbufferStorageMultisample(GL_RENDERBUFFER, 4, GL_DEPTH_COMPONENT, nWidth, nHeight )
    glFramebufferRenderbuffer(GL_FRAMEBUFFER, GL_DEPTH_ATTACHMENT, GL_RENDERBUFFER,    framebufferDesc.self.m_nDepthBufferId )

    glGenTextures(1, framebufferDesc.self.m_nRenderTextureId )
    glBindTexture(GL_TEXTURE_2D_MULTISAMPLE, framebufferDesc.self.m_nRenderTextureId )
    glTexImage2DMultisample(GL_TEXTURE_2D_MULTISAMPLE, 4, GL_RGBA8, nWidth, nHeight, True)
    glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D_MULTISAMPLE, framebufferDesc.self.m_nRenderTextureId, 0)

    glGenFramebuffers(1, framebufferDesc.self.m_nResolveFramebufferId )
    glBindFramebuffer(GL_FRAMEBUFFER, framebufferDesc.self.m_nResolveFramebufferId)

    glGenTextures(1, framebufferDesc.self.m_nResolveTextureId )
    glBindTexture(GL_TEXTURE_2D, framebufferDesc.self.m_nResolveTextureId )
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAX_LEVEL, 0)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA8, nWidth, nHeight, 0, GL_RGBA, GL_UNSIGNED_BYTE, None)
    glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, framebufferDesc.self.m_nResolveTextureId, 0)

    # check FBO status
    GLenum status = glCheckFramebufferStatus(GL_FRAMEBUFFER)
    if (status != GL_FRAMEBUFFER_COMPLETE)
    
        return False
    

    glBindFramebuffer( GL_FRAMEBUFFER, 0 )

    return True



#-----------------------------------------------------------------------------
# Purpose:
#-----------------------------------------------------------------------------
bool CMainApplication.SetupStereoRenderTargets()

    if ( !self.m_pHMD )
        return False

    self.m_pHMD.GetRecommendedRenderTargetSize( self.m_nRenderWidth, self.m_nRenderHeight )

    CreateFrameBuffer( self.m_nRenderWidth, self.m_nRenderHeight, leftEyeDesc )
    CreateFrameBuffer( self.m_nRenderWidth, self.m_nRenderHeight, rightEyeDesc )
    
    return True



#-----------------------------------------------------------------------------
# Purpose:
#-----------------------------------------------------------------------------
void CMainApplication.SetupDistortion()

    if ( !self.m_pHMD )
        return

    GLushort self.m_iLensGridSegmentCountH = 43
    GLushort self.m_iLensGridSegmentCountV = 43

    float w = (float)( 1.0/float(self.m_iLensGridSegmentCountH-1))
    float h = (float)( 1.0/float(self.m_iLensGridSegmentCountV-1))

    float u, v = 0

    std.vector<VertexDataLens> vVerts(0)
    VertexDataLens vert

    #left eye distortion verts
    float Xoffset = -1
    for( int y=0 y<self.m_iLensGridSegmentCountV y++ )
    
        for( int x=0 x<self.m_iLensGridSegmentCountH x++ )
        
            u = x*w v = 1-y*h
            vert.position = Vector2( Xoffset+u, -1+2*y*h )

            openvr.DistortionCoordinates_t dc0 = self.m_pHMD.ComputeDistortion(openvr.Eye_Left, u, v)

            vert.texCoordRed = Vector2(dc0.rfRed[0], 1 - dc0.rfRed[1])
            vert.texCoordGreen =  Vector2(dc0.rfGreen[0], 1 - dc0.rfGreen[1])
            vert.texCoordBlue = Vector2(dc0.rfBlue[0], 1 - dc0.rfBlue[1])

            vVerts.push_back( vert )
        
    

    #right eye distortion verts
    Xoffset = 0
    for( int y=0 y<self.m_iLensGridSegmentCountV y++ )
    
        for( int x=0 x<self.m_iLensGridSegmentCountH x++ )
        
            u = x*w v = 1-y*h
            vert.position = Vector2( Xoffset+u, -1+2*y*h )

            openvr.DistortionCoordinates_t dc0 = self.m_pHMD.ComputeDistortion( openvr.Eye_Right, u, v )

            vert.texCoordRed = Vector2(dc0.rfRed[0], 1 - dc0.rfRed[1])
            vert.texCoordGreen = Vector2(dc0.rfGreen[0], 1 - dc0.rfGreen[1])
            vert.texCoordBlue = Vector2(dc0.rfBlue[0], 1 - dc0.rfBlue[1])

            vVerts.push_back( vert )
        
    

    std.vector<GLushort> vIndices
    GLushort a,b,c,d

    GLushort offset = 0
    for( GLushort y=0 y<self.m_iLensGridSegmentCountV-1 y++ )
    
        for( GLushort x=0 x<self.m_iLensGridSegmentCountH-1 x++ )
        
            a = self.m_iLensGridSegmentCountH*y+x +offset
            b = self.m_iLensGridSegmentCountH*y+x+1 +offset
            c = (y+1)*self.m_iLensGridSegmentCountH+x+1 +offset
            d = (y+1)*self.m_iLensGridSegmentCountH+x +offset
            vIndices.push_back( a )
            vIndices.push_back( b )
            vIndices.push_back( c )

            vIndices.push_back( a )
            vIndices.push_back( c )
            vIndices.push_back( d )
        
    

    offset = (self.m_iLensGridSegmentCountH)*(self.m_iLensGridSegmentCountV)
    for( GLushort y=0 y<self.m_iLensGridSegmentCountV-1 y++ )
    
        for( GLushort x=0 x<self.m_iLensGridSegmentCountH-1 x++ )
        
            a = self.m_iLensGridSegmentCountH*y+x +offset
            b = self.m_iLensGridSegmentCountH*y+x+1 +offset
            c = (y+1)*self.m_iLensGridSegmentCountH+x+1 +offset
            d = (y+1)*self.m_iLensGridSegmentCountH+x +offset
            vIndices.push_back( a )
            vIndices.push_back( b )
            vIndices.push_back( c )

            vIndices.push_back( a )
            vIndices.push_back( c )
            vIndices.push_back( d )
        
    
    self.m_uiIndexSize = vIndices.size()

    glGenVertexArrays( 1, self.m_unLensVAO )
    glBindVertexArray( self.m_unLensVAO )

    glGenBuffers( 1, self.m_glIDVertBuffer )
    glBindBuffer( GL_ARRAY_BUFFER, self.m_glIDVertBuffer )
    glBufferData( GL_ARRAY_BUFFER, vVerts.size()*sizeof(VertexDataLens), vVerts[0], GL_STATIC_DRAW )

    glGenBuffers( 1, self.m_glIDIndexBuffer )
    glBindBuffer( GL_ELEMENT_ARRAY_BUFFER, self.m_glIDIndexBuffer )
    glBufferData( GL_ELEMENT_ARRAY_BUFFER, vIndices.size()*sizeof(GLushort), vIndices[0], GL_STATIC_DRAW )

    glEnableVertexAttribArray( 0 )
    glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, sizeof(VertexDataLens), offsetof( VertexDataLens, position ) )

    glEnableVertexAttribArray( 1 )
    glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, sizeof(VertexDataLens), offsetof( VertexDataLens, texCoordRed ) )

    glEnableVertexAttribArray(2)
    glVertexAttribPointer(2, 2, GL_FLOAT, GL_FALSE, sizeof(VertexDataLens), offsetof( VertexDataLens, texCoordGreen ) )

    glEnableVertexAttribArray(3)
    glVertexAttribPointer(3, 2, GL_FLOAT, GL_FALSE, sizeof(VertexDataLens), offsetof( VertexDataLens, texCoordBlue ) )

    glBindVertexArray( 0 )

    glDisableVertexAttribArray(0)
    glDisableVertexAttribArray(1)
    glDisableVertexAttribArray(2)
    glDisableVertexAttribArray(3)

    glBindBuffer(GL_ARRAY_BUFFER, 0)
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, 0)



#-----------------------------------------------------------------------------
# Purpose:
#-----------------------------------------------------------------------------
void CMainApplication.RenderStereoTargets()

    glClearColor( 0.15f, 0.15f, 0.18f, 1.0f ) # nice background color, but not black
    glEnable( GL_MULTISAMPLE )

    # Left Eye
    glBindFramebuffer( GL_FRAMEBUFFER, leftEyeDesc.self.m_nRenderFramebufferId )
     glViewport(0, 0, self.m_nRenderWidth, self.m_nRenderHeight )
     RenderScene( openvr.Eye_Left )
     glBindFramebuffer( GL_FRAMEBUFFER, 0 )
    
    glDisable( GL_MULTISAMPLE )
         
     glBindFramebuffer(GL_READ_FRAMEBUFFER, leftEyeDesc.self.m_nRenderFramebufferId)
    glBindFramebuffer(GL_DRAW_FRAMEBUFFER, leftEyeDesc.self.m_nResolveFramebufferId )

    glBlitFramebuffer( 0, 0, self.m_nRenderWidth, self.m_nRenderHeight, 0, 0, self.m_nRenderWidth, self.m_nRenderHeight, 
        GL_COLOR_BUFFER_BIT,
         GL_LINEAR )

     glBindFramebuffer(GL_READ_FRAMEBUFFER, 0)
    glBindFramebuffer(GL_DRAW_FRAMEBUFFER, 0 )    

    glEnable( GL_MULTISAMPLE )

    # Right Eye
    glBindFramebuffer( GL_FRAMEBUFFER, rightEyeDesc.self.m_nRenderFramebufferId )
     glViewport(0, 0, self.m_nRenderWidth, self.m_nRenderHeight )
     RenderScene( openvr.Eye_Right )
     glBindFramebuffer( GL_FRAMEBUFFER, 0 )
     
    glDisable( GL_MULTISAMPLE )

     glBindFramebuffer(GL_READ_FRAMEBUFFER, rightEyeDesc.self.m_nRenderFramebufferId )
    glBindFramebuffer(GL_DRAW_FRAMEBUFFER, rightEyeDesc.self.m_nResolveFramebufferId )
    
    glBlitFramebuffer( 0, 0, self.m_nRenderWidth, self.m_nRenderHeight, 0, 0, self.m_nRenderWidth, self.m_nRenderHeight, 
        GL_COLOR_BUFFER_BIT,
         GL_LINEAR  )

     glBindFramebuffer(GL_READ_FRAMEBUFFER, 0)
    glBindFramebuffer(GL_DRAW_FRAMEBUFFER, 0 )



#-----------------------------------------------------------------------------
# Purpose:
#-----------------------------------------------------------------------------
void CMainApplication.RenderScene( openvr.Hmd_Eye nEye )

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glEnable(GL_DEPTH_TEST)

    if( self.m_bShowCubes )
    
        glUseProgram( self.m_unSceneProgramID )
        glUniformMatrix4fv( self.m_nSceneMatrixLocation, 1, GL_FALSE, GetCurrentViewProjectionMatrix( nEye ).get() )
        glBindVertexArray( self.m_unSceneVAO )
        glBindTexture( GL_TEXTURE_2D, self.m_iTexture )
        glDrawArrays( GL_TRIANGLES, 0, self.m_uiVertcount )
        glBindVertexArray( 0 )
    

    bool bIsInputCapturedByAnotherProcess = self.m_pHMD.IsInputFocusCapturedByAnotherProcess()

    if( !bIsInputCapturedByAnotherProcess )
    
        # draw the controller axis lines
        glUseProgram( self.m_unControllerTransformProgramID )
        glUniformMatrix4fv( self.m_nControllerMatrixLocation, 1, GL_FALSE, GetCurrentViewProjectionMatrix( nEye ).get() )
        glBindVertexArray( self.m_unControllerVAO )
        glDrawArrays( GL_LINES, 0, self.m_uiControllerVertcount )
        glBindVertexArray( 0 )
    

    # ----- Render Model rendering -----
    glUseProgram( self.m_unRenderModelProgramID )

    for( uint32_t unTrackedDevice = 0 unTrackedDevice < openvr.k_unMaxTrackedDeviceCount unTrackedDevice++ )
    
        if( !self.m_rTrackedDeviceToRenderModel[ unTrackedDevice ] || !self.m_rbShowTrackedDevice[ unTrackedDevice ] )
            continue

        const openvr.TrackedDevicePose_t & pose = self.m_rTrackedDevicePose[ unTrackedDevice ]
        if( !pose.bPoseIsValid )
            continue

        if( bIsInputCapturedByAnotherProcess && self.m_pHMD.GetTrackedDeviceClass( unTrackedDevice ) == openvr.TrackedDeviceClass_Controller )
            continue

        const Matrix4 & matDeviceToTracking = self.m_rmat4DevicePose[ unTrackedDevice ]
        Matrix4 matMVP = GetCurrentViewProjectionMatrix( nEye ) * matDeviceToTracking
        glUniformMatrix4fv( self.m_nRenderModelMatrixLocation, 1, GL_FALSE, matMVP.get() )

        self.m_rTrackedDeviceToRenderModel[ unTrackedDevice ].Draw()
    

    glUseProgram( 0 )



#-----------------------------------------------------------------------------
# Purpose:
#-----------------------------------------------------------------------------
void CMainApplication.RenderDistortion()

    glDisable(GL_DEPTH_TEST)
    glViewport( 0, 0, self.m_nWindowWidth, self.m_nWindowHeight )

    glBindVertexArray( self.m_unLensVAO )
    glUseProgram( self.m_unLensProgramID )

    #render left lens (first half of index array )
    glBindTexture(GL_TEXTURE_2D, leftEyeDesc.self.m_nResolveTextureId )
    glTexParameteri( GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE )
    glTexParameteri( GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE )
    glTexParameteri( GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR )
    glTexParameteri( GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR )
    glDrawElements( GL_TRIANGLES, self.m_uiIndexSize/2, GL_UNSIGNED_SHORT, 0 )

    #render right lens (second half of index array )
    glBindTexture(GL_TEXTURE_2D, rightEyeDesc.self.m_nResolveTextureId  )
    glTexParameteri( GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE )
    glTexParameteri( GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE )
    glTexParameteri( GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR )
    glTexParameteri( GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR )
    glDrawElements( GL_TRIANGLES, self.m_uiIndexSize/2, GL_UNSIGNED_SHORT, (const void *)(self.m_uiIndexSize) )

    glBindVertexArray( 0 )
    glUseProgram( 0 )



#-----------------------------------------------------------------------------
# Purpose:
#-----------------------------------------------------------------------------
Matrix4 CMainApplication.GetHMDMatrixProjectionEye( openvr.Hmd_Eye nEye )

    if ( !self.m_pHMD )
        return Matrix4()

    openvr.HmdMatrix44_t mat = self.m_pHMD.GetProjectionMatrix( nEye, self.m_fNearClip, self.m_fFarClip, openvr.API_OpenGL)

    return Matrix4(
        mat.m[0][0], mat.m[1][0], mat.m[2][0], mat.m[3][0],
        mat.m[0][1], mat.m[1][1], mat.m[2][1], mat.m[3][1], 
        mat.m[0][2], mat.m[1][2], mat.m[2][2], mat.m[3][2], 
        mat.m[0][3], mat.m[1][3], mat.m[2][3], mat.m[3][3]
    )



#-----------------------------------------------------------------------------
# Purpose:
#-----------------------------------------------------------------------------
Matrix4 CMainApplication.GetHMDMatrixPoseEye( openvr.Hmd_Eye nEye )

    if ( !self.m_pHMD )
        return Matrix4()

    openvr.HmdMatrix34_t matEyeRight = self.m_pHMD.GetEyeToHeadTransform( nEye )
    Matrix4 matrixObj(
        matEyeRight.m[0][0], matEyeRight.m[1][0], matEyeRight.m[2][0], 0.0, 
        matEyeRight.m[0][1], matEyeRight.m[1][1], matEyeRight.m[2][1], 0.0,
        matEyeRight.m[0][2], matEyeRight.m[1][2], matEyeRight.m[2][2], 0.0,
        matEyeRight.m[0][3], matEyeRight.m[1][3], matEyeRight.m[2][3], 1.0f
        )

    return matrixObj.invert()



#-----------------------------------------------------------------------------
# Purpose:
#-----------------------------------------------------------------------------
Matrix4 CMainApplication.GetCurrentViewProjectionMatrix( openvr.Hmd_Eye nEye )

    Matrix4 matMVP
    if( nEye == openvr.Eye_Left )
    
        matMVP = self.m_mat4ProjectionLeft * self.m_mat4eyePosLeft * self.m_mat4HMDPose
    
    else if( nEye == openvr.Eye_Right )
    
        matMVP = self.m_mat4ProjectionRight * self.m_mat4eyePosRight *  self.m_mat4HMDPose
    

    return matMVP



#-----------------------------------------------------------------------------
# Purpose:
#-----------------------------------------------------------------------------
void CMainApplication.UpdateHMDMatrixPose()

    if ( !self.m_pHMD )
        return

    openvr.VRCompositor().WaitGetPoses(self.m_rTrackedDevicePose, openvr.k_unMaxTrackedDeviceCount, None, 0 )

    self.m_iValidPoseCount = 0
    self.m_strPoseClasses = ""
    for ( int nDevice = 0 nDevice < openvr.k_unMaxTrackedDeviceCount ++nDevice )
    
        if ( self.m_rTrackedDevicePose[nDevice].bPoseIsValid )
        
            self.m_iValidPoseCount++
            self.m_rmat4DevicePose[nDevice] = ConvertSteamVRMatrixToMatrix4( self.m_rTrackedDevicePose[nDevice].mDeviceToAbsoluteTracking )
            if (self.m_rDevClassChar[nDevice]==0)
            
                switch (self.m_pHMD.GetTrackedDeviceClass(nDevice))
                
                case openvr.TrackedDeviceClass_Controller:        self.m_rDevClassChar[nDevice] = 'C' break
                case openvr.TrackedDeviceClass_HMD:               self.m_rDevClassChar[nDevice] = 'H' break
                case openvr.TrackedDeviceClass_Invalid:           self.m_rDevClassChar[nDevice] = 'I' break
                case openvr.TrackedDeviceClass_Other:             self.m_rDevClassChar[nDevice] = 'O' break
                case openvr.TrackedDeviceClass_TrackingReference: self.m_rDevClassChar[nDevice] = 'T' break
                default:                                       self.m_rDevClassChar[nDevice] = '?' break
                
            
            self.m_strPoseClasses += self.m_rDevClassChar[nDevice]
        
    

    if ( self.m_rTrackedDevicePose[openvr.k_unTrackedDeviceIndex_Hmd].bPoseIsValid )
    
        self.m_mat4HMDPose = self.m_rmat4DevicePose[openvr.k_unTrackedDeviceIndex_Hmd].invert()
    



#-----------------------------------------------------------------------------
# Purpose: Finds a render model we've already loaded or loads a new one
#-----------------------------------------------------------------------------
CGLRenderModel CMainApplication.FindOrLoadRenderModel( const char pchRenderModelName )

    CGLRenderModel pRenderModel = None
    for( std.vector< CGLRenderModel * >.iterator i = self.m_vecRenderModels.begin() i != self.m_vecRenderModels.end() i++ )
    
        if( !stricmp( (*i).GetName().c_str(), pchRenderModelName ) )
        
            pRenderModel = i
            break
        
    

    # load the model if we didn't find one
    if( !pRenderModel )
    
        openvr.RenderModel_t pModel
        openvr.EVRRenderModelError error
        while ( 1 )
        
            error = openvr.VRRenderModels().LoadRenderModel_Async( pchRenderModelName, pModel )
            if ( error != openvr.VRRenderModelError_Loading )
                break

            ThreadSleep( 1 )
        

        if ( error != openvr.VRRenderModelError_None )
        
            dprintf( "Unable to load render model %s - %s\n", pchRenderModelName, openvr.VRRenderModels().GetRenderModelErrorNameFromEnum( error ) )
            return None # move on to the next tracked device
        

        openvr.RenderModel_TextureMap_t pTexture
        while ( 1 )
        
            error = openvr.VRRenderModels().LoadTexture_Async( pModel.diffuseTextureId, pTexture )
            if ( error != openvr.VRRenderModelError_Loading )
                break

            ThreadSleep( 1 )
        

        if ( error != openvr.VRRenderModelError_None )
        
            dprintf( "Unable to load render texture id:%d for render model %s\n", pModel.diffuseTextureId, pchRenderModelName )
            openvr.VRRenderModels().FreeRenderModel( pModel )
            return None # move on to the next tracked device
        

        pRenderModel = CGLRenderModel( pchRenderModelName )
        if ( !pRenderModel.BInit( pModel, pTexture ) )
        
            dprintf( "Unable to create GL model from render model %s\n", pchRenderModelName )
            delete pRenderModel
            pRenderModel = None
        
        else
        
            self.m_vecRenderModels.push_back( pRenderModel )
        
        openvr.VRRenderModels().FreeRenderModel( pModel )
        openvr.VRRenderModels().FreeTexture( pTexture )
    
    return pRenderModel



#-----------------------------------------------------------------------------
# Purpose: Create/destroy GL a Render Model for a single tracked device
#-----------------------------------------------------------------------------
void CMainApplication.SetupRenderModelForTrackedDevice( openvr.TrackedDeviceIndex_t unTrackedDeviceIndex )

    if( unTrackedDeviceIndex >= openvr.k_unMaxTrackedDeviceCount )
        return

    # try to find a model we've already set up
    std.string sRenderModelName = GetTrackedDeviceString( self.m_pHMD, unTrackedDeviceIndex, openvr.Prop_RenderModelName_String )
    CGLRenderModel pRenderModel = FindOrLoadRenderModel( sRenderModelName.c_str() )
    if( !pRenderModel )
    
        std.string sTrackingSystemName = GetTrackedDeviceString( self.m_pHMD, unTrackedDeviceIndex, openvr.Prop_TrackingSystemName_String )
        dprintf( "Unable to load render model for tracked device %d (%s.%s)", unTrackedDeviceIndex, sTrackingSystemName.c_str(), sRenderModelName.c_str() )
    
    else
    
        self.m_rTrackedDeviceToRenderModel[ unTrackedDeviceIndex ] = pRenderModel
        self.m_rbShowTrackedDevice[ unTrackedDeviceIndex ] = True
    



#-----------------------------------------------------------------------------
# Purpose: Create/destroy GL Render Models
#-----------------------------------------------------------------------------
void CMainApplication.SetupRenderModels()

    memset( self.m_rTrackedDeviceToRenderModel, 0, sizeof( self.m_rTrackedDeviceToRenderModel ) )

    if( !self.m_pHMD )
        return

    for( uint32_t unTrackedDevice = openvr.k_unTrackedDeviceIndex_Hmd + 1 unTrackedDevice < openvr.k_unMaxTrackedDeviceCount unTrackedDevice++ )
    
        if( !self.m_pHMD.IsTrackedDeviceConnected( unTrackedDevice ) )
            continue

        SetupRenderModelForTrackedDevice( unTrackedDevice )
    




#-----------------------------------------------------------------------------
# Purpose: Converts a SteamVR matrix to our local matrix class
#-----------------------------------------------------------------------------
Matrix4 CMainApplication.ConvertSteamVRMatrixToMatrix4( const openvr.HmdMatrix34_t matPose )

    Matrix4 matrixObj(
        matPose.m[0][0], matPose.m[1][0], matPose.m[2][0], 0.0,
        matPose.m[0][1], matPose.m[1][1], matPose.m[2][1], 0.0,
        matPose.m[0][2], matPose.m[1][2], matPose.m[2][2], 0.0,
        matPose.m[0][3], matPose.m[1][3], matPose.m[2][3], 1.0f
        )
    return matrixObj


#-----------------------------------------------------------------------------
# Purpose:
#-----------------------------------------------------------------------------
int main(int argc, char argv[])

    CMainApplication pMainApplication = CMainApplication( argc, argv )

    if (!pMainApplication.BInit())
    
        pMainApplication.Shutdown()
        return 1
    

    pMainApplication.RunMainLoop()

    pMainApplication.Shutdown()

    return 0

