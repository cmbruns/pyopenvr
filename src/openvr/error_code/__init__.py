############################################
# Python exceptions for openvr error codes #
############################################


class OpenVRError(Exception):
    """
    OpenVRError is a custom exception type for when OpenVR functions return a failure code.
    Such a specific exception type allows more precise exception handling that does just raising Exception().
    """
    pass


class ErrorCode(OpenVRError):
    error_index = dict()
    is_error = True  # FooError_None classes should override this

    @classmethod
    def check_error_value(cls, error_value, message=''):
        error_class = cls.error_index[int(error_value)]
        if not error_class.is_error:
            return
        raise error_class(error_value, message)
        
    def __init__(this, error_value, message=''):
        super().__init__(message)
        this.error_value = error_value


class BufferTooSmallError(ErrorCode):
    pass


class TrackedPropertyError(ErrorCode):
    error_index = dict()


class TrackedProp_Success(TrackedPropertyError):
    is_error = False


class TrackedProp_WrongDataType(TrackedPropertyError):
    pass


class TrackedProp_WrongDeviceClass(TrackedPropertyError):
    pass


class TrackedProp_BufferTooSmall(TrackedPropertyError, BufferTooSmallError):
    pass


class TrackedProp_UnknownProperty(TrackedPropertyError):
    pass


class TrackedProp_InvalidDevice(TrackedPropertyError):
    pass


class TrackedProp_CouldNotContactServer(TrackedPropertyError):
    pass


class TrackedProp_ValueNotProvidedByDevice(TrackedPropertyError):
    pass


class TrackedProp_StringExceedsMaximumLength(TrackedPropertyError):
    pass


class TrackedProp_NotYetAvailable(TrackedPropertyError):
    pass


class TrackedProp_PermissionDenied(TrackedPropertyError):
    pass


class TrackedProp_InvalidOperation(TrackedPropertyError):
    pass


class TrackedProp_CannotWriteToWildcards(TrackedPropertyError):
    pass


class TrackedProp_IPCReadFailure(TrackedPropertyError):
    pass


class TrackedProp_OutOfMemory(TrackedPropertyError):
    pass


class TrackedProp_InvalidContainer(TrackedPropertyError):
    pass


TrackedPropertyError.error_index[0] = TrackedProp_Success
TrackedPropertyError.error_index[1] = TrackedProp_WrongDataType
TrackedPropertyError.error_index[2] = TrackedProp_WrongDeviceClass
TrackedPropertyError.error_index[3] = TrackedProp_BufferTooSmall
TrackedPropertyError.error_index[4] = TrackedProp_UnknownProperty
TrackedPropertyError.error_index[5] = TrackedProp_InvalidDevice
TrackedPropertyError.error_index[6] = TrackedProp_CouldNotContactServer
TrackedPropertyError.error_index[7] = TrackedProp_ValueNotProvidedByDevice
TrackedPropertyError.error_index[8] = TrackedProp_StringExceedsMaximumLength
TrackedPropertyError.error_index[9] = TrackedProp_NotYetAvailable
TrackedPropertyError.error_index[10] = TrackedProp_PermissionDenied
TrackedPropertyError.error_index[11] = TrackedProp_InvalidOperation
TrackedPropertyError.error_index[12] = TrackedProp_CannotWriteToWildcards
TrackedPropertyError.error_index[13] = TrackedProp_IPCReadFailure
TrackedPropertyError.error_index[14] = TrackedProp_OutOfMemory
TrackedPropertyError.error_index[15] = TrackedProp_InvalidContainer


class HDCPError(ErrorCode):
    error_index = dict()


class HDCPError_None(HDCPError):
    is_error = False


class HDCPError_LinkLost(HDCPError):
    pass


class HDCPError_Tampered(HDCPError):
    pass


class HDCPError_DeviceRevoked(HDCPError):
    pass


class HDCPError_Unknown(HDCPError):
    pass


HDCPError.error_index[0] = HDCPError_None
HDCPError.error_index[1] = HDCPError_LinkLost
HDCPError.error_index[2] = HDCPError_Tampered
HDCPError.error_index[3] = HDCPError_DeviceRevoked
HDCPError.error_index[4] = HDCPError_Unknown


class InputError(ErrorCode):
    error_index = dict()


class InputError_None(InputError):
    is_error = False


class InputError_NameNotFound(InputError):
    pass


class InputError_WrongType(InputError):
    pass


class InputError_InvalidHandle(InputError):
    pass


class InputError_InvalidParam(InputError):
    pass


class InputError_NoSteam(InputError):
    pass


class InputError_MaxCapacityReached(InputError):
    pass


class InputError_IPCError(InputError):
    pass


class InputError_NoActiveActionSet(InputError):
    pass


class InputError_InvalidDevice(InputError):
    pass


class InputError_InvalidSkeleton(InputError):
    pass


class InputError_InvalidBoneCount(InputError):
    pass


class InputError_InvalidCompressedData(InputError):
    pass


class InputError_NoData(InputError):
    pass


class InputError_BufferTooSmall(InputError, BufferTooSmallError):
    pass


class InputError_MismatchedActionManifest(InputError):
    pass


class InputError_MissingSkeletonData(InputError):
    pass


class InputError_InvalidBoneIndex(InputError):
    pass


class InputError_InvalidPriority(InputError):
    pass


class InputError_PermissionDenied(InputError):
    pass


class InputError_InvalidRenderModel(InputError):
    pass


InputError.error_index[0] = InputError_None
InputError.error_index[1] = InputError_NameNotFound
InputError.error_index[2] = InputError_WrongType
InputError.error_index[3] = InputError_InvalidHandle
InputError.error_index[4] = InputError_InvalidParam
InputError.error_index[5] = InputError_NoSteam
InputError.error_index[6] = InputError_MaxCapacityReached
InputError.error_index[7] = InputError_IPCError
InputError.error_index[8] = InputError_NoActiveActionSet
InputError.error_index[9] = InputError_InvalidDevice
InputError.error_index[10] = InputError_InvalidSkeleton
InputError.error_index[11] = InputError_InvalidBoneCount
InputError.error_index[12] = InputError_InvalidCompressedData
InputError.error_index[13] = InputError_NoData
InputError.error_index[14] = InputError_BufferTooSmall
InputError.error_index[15] = InputError_MismatchedActionManifest
InputError.error_index[16] = InputError_MissingSkeletonData
InputError.error_index[17] = InputError_InvalidBoneIndex
InputError.error_index[18] = InputError_InvalidPriority
InputError.error_index[19] = InputError_PermissionDenied
InputError.error_index[20] = InputError_InvalidRenderModel


class SpatialAnchorError(ErrorCode):
    error_index = dict()


class SpatialAnchorError_Success(SpatialAnchorError):
    is_error = False


class SpatialAnchorError_Internal(SpatialAnchorError):
    pass


class SpatialAnchorError_UnknownHandle(SpatialAnchorError):
    pass


class SpatialAnchorError_ArrayTooSmall(SpatialAnchorError):
    pass


class SpatialAnchorError_InvalidDescriptorChar(SpatialAnchorError):
    pass


class SpatialAnchorError_NotYetAvailable(SpatialAnchorError):
    pass


class SpatialAnchorError_NotAvailableInThisUniverse(SpatialAnchorError):
    pass


class SpatialAnchorError_PermanentlyUnavailable(SpatialAnchorError):
    pass


class SpatialAnchorError_WrongDriver(SpatialAnchorError):
    pass


class SpatialAnchorError_DescriptorTooLong(SpatialAnchorError):
    pass


class SpatialAnchorError_Unknown(SpatialAnchorError):
    pass


class SpatialAnchorError_NoRoomCalibration(SpatialAnchorError):
    pass


class SpatialAnchorError_InvalidArgument(SpatialAnchorError):
    pass


class SpatialAnchorError_UnknownDriver(SpatialAnchorError):
    pass


SpatialAnchorError.error_index[0] = SpatialAnchorError_Success
SpatialAnchorError.error_index[1] = SpatialAnchorError_Internal
SpatialAnchorError.error_index[2] = SpatialAnchorError_UnknownHandle
SpatialAnchorError.error_index[3] = SpatialAnchorError_ArrayTooSmall
SpatialAnchorError.error_index[4] = SpatialAnchorError_InvalidDescriptorChar
SpatialAnchorError.error_index[5] = SpatialAnchorError_NotYetAvailable
SpatialAnchorError.error_index[6] = SpatialAnchorError_NotAvailableInThisUniverse
SpatialAnchorError.error_index[7] = SpatialAnchorError_PermanentlyUnavailable
SpatialAnchorError.error_index[8] = SpatialAnchorError_WrongDriver
SpatialAnchorError.error_index[9] = SpatialAnchorError_DescriptorTooLong
SpatialAnchorError.error_index[10] = SpatialAnchorError_Unknown
SpatialAnchorError.error_index[11] = SpatialAnchorError_NoRoomCalibration
SpatialAnchorError.error_index[12] = SpatialAnchorError_InvalidArgument
SpatialAnchorError.error_index[13] = SpatialAnchorError_UnknownDriver


class OverlayError(ErrorCode):
    error_index = dict()


class OverlayError_None(OverlayError):
    is_error = False


class OverlayError_UnknownOverlay(OverlayError):
    pass


class OverlayError_InvalidHandle(OverlayError):
    pass


class OverlayError_PermissionDenied(OverlayError):
    pass


class OverlayError_OverlayLimitExceeded(OverlayError):
    pass


class OverlayError_WrongVisibilityType(OverlayError):
    pass


class OverlayError_KeyTooLong(OverlayError):
    pass


class OverlayError_NameTooLong(OverlayError):
    pass


class OverlayError_KeyInUse(OverlayError):
    pass


class OverlayError_WrongTransformType(OverlayError):
    pass


class OverlayError_InvalidTrackedDevice(OverlayError):
    pass


class OverlayError_InvalidParameter(OverlayError):
    pass


class OverlayError_ThumbnailCantBeDestroyed(OverlayError):
    pass


class OverlayError_ArrayTooSmall(OverlayError):
    pass


class OverlayError_RequestFailed(OverlayError):
    pass


class OverlayError_InvalidTexture(OverlayError):
    pass


class OverlayError_UnableToLoadFile(OverlayError):
    pass


class OverlayError_KeyboardAlreadyInUse(OverlayError):
    pass


class OverlayError_NoNeighbor(OverlayError):
    pass


class OverlayError_TooManyMaskPrimitives(OverlayError):
    pass


class OverlayError_BadMaskPrimitive(OverlayError):
    pass


class OverlayError_TextureAlreadyLocked(OverlayError):
    pass


class OverlayError_TextureLockCapacityReached(OverlayError):
    pass


class OverlayError_TextureNotLocked(OverlayError):
    pass


class OverlayError_TimedOut(OverlayError):
    pass


OverlayError.error_index[0] = OverlayError_None
OverlayError.error_index[10] = OverlayError_UnknownOverlay
OverlayError.error_index[11] = OverlayError_InvalidHandle
OverlayError.error_index[12] = OverlayError_PermissionDenied
OverlayError.error_index[13] = OverlayError_OverlayLimitExceeded
OverlayError.error_index[14] = OverlayError_WrongVisibilityType
OverlayError.error_index[15] = OverlayError_KeyTooLong
OverlayError.error_index[16] = OverlayError_NameTooLong
OverlayError.error_index[17] = OverlayError_KeyInUse
OverlayError.error_index[18] = OverlayError_WrongTransformType
OverlayError.error_index[19] = OverlayError_InvalidTrackedDevice
OverlayError.error_index[20] = OverlayError_InvalidParameter
OverlayError.error_index[21] = OverlayError_ThumbnailCantBeDestroyed
OverlayError.error_index[22] = OverlayError_ArrayTooSmall
OverlayError.error_index[23] = OverlayError_RequestFailed
OverlayError.error_index[24] = OverlayError_InvalidTexture
OverlayError.error_index[25] = OverlayError_UnableToLoadFile
OverlayError.error_index[26] = OverlayError_KeyboardAlreadyInUse
OverlayError.error_index[27] = OverlayError_NoNeighbor
OverlayError.error_index[29] = OverlayError_TooManyMaskPrimitives
OverlayError.error_index[30] = OverlayError_BadMaskPrimitive
OverlayError.error_index[31] = OverlayError_TextureAlreadyLocked
OverlayError.error_index[32] = OverlayError_TextureLockCapacityReached
OverlayError.error_index[33] = OverlayError_TextureNotLocked
OverlayError.error_index[34] = OverlayError_TimedOut


class FirmwareError(ErrorCode):
    error_index = dict()


class FirmwareError_None(FirmwareError):
    is_error = False


class FirmwareError_Success(FirmwareError):
    is_error = False


class FirmwareError_Fail(FirmwareError):
    pass


FirmwareError.error_index[0] = FirmwareError_None
FirmwareError.error_index[1] = FirmwareError_Success
FirmwareError.error_index[2] = FirmwareError_Fail


class NotificationError(ErrorCode):
    error_index = dict()


class NotificationError_OK(NotificationError):
    pass


class NotificationError_InvalidNotificationId(NotificationError):
    pass


class NotificationError_NotificationQueueFull(NotificationError):
    pass


class NotificationError_InvalidOverlayHandle(NotificationError):
    pass


class NotificationError_SystemWithUserValueAlreadyExists(NotificationError):
    pass


NotificationError.error_index[0] = NotificationError_OK
NotificationError.error_index[100] = NotificationError_InvalidNotificationId
NotificationError.error_index[101] = NotificationError_NotificationQueueFull
NotificationError.error_index[102] = NotificationError_InvalidOverlayHandle
NotificationError.error_index[103] = NotificationError_SystemWithUserValueAlreadyExists


class InitError(ErrorCode):
    error_index = dict()


class InitError_None(InitError):
    is_error = False


class InitError_Unknown(InitError):
    pass


class InitError_Init_InstallationNotFound(InitError):
    pass


class InitError_Init_InstallationCorrupt(InitError):
    pass


class InitError_Init_VRClientDLLNotFound(InitError):
    pass


class InitError_Init_FileNotFound(InitError):
    pass


class InitError_Init_FactoryNotFound(InitError):
    pass


class InitError_Init_InterfaceNotFound(InitError):
    pass


class InitError_Init_InvalidInterface(InitError):
    pass


class InitError_Init_UserConfigDirectoryInvalid(InitError):
    pass


class InitError_Init_HmdNotFound(InitError):
    pass


class InitError_Init_NotInitialized(InitError):
    pass


class InitError_Init_PathRegistryNotFound(InitError):
    pass


class InitError_Init_NoConfigPath(InitError):
    pass


class InitError_Init_NoLogPath(InitError):
    pass


class InitError_Init_PathRegistryNotWritable(InitError):
    pass


class InitError_Init_AppInfoInitFailed(InitError):
    pass


class InitError_Init_Retry(InitError):
    pass


class InitError_Init_InitCanceledByUser(InitError):
    pass


class InitError_Init_AnotherAppLaunching(InitError):
    pass


class InitError_Init_SettingsInitFailed(InitError):
    pass


class InitError_Init_ShuttingDown(InitError):
    pass


class InitError_Init_TooManyObjects(InitError):
    pass


class InitError_Init_NoServerForBackgroundApp(InitError):
    pass


class InitError_Init_NotSupportedWithCompositor(InitError):
    pass


class InitError_Init_NotAvailableToUtilityApps(InitError):
    pass


class InitError_Init_Internal(InitError):
    pass


class InitError_Init_HmdDriverIdIsNone(InitError):
    pass


class InitError_Init_HmdNotFoundPresenceFailed(InitError):
    pass


class InitError_Init_VRMonitorNotFound(InitError):
    pass


class InitError_Init_VRMonitorStartupFailed(InitError):
    pass


class InitError_Init_LowPowerWatchdogNotSupported(InitError):
    pass


class InitError_Init_InvalidApplicationType(InitError):
    pass


class InitError_Init_NotAvailableToWatchdogApps(InitError):
    pass


class InitError_Init_WatchdogDisabledInSettings(InitError):
    pass


class InitError_Init_VRDashboardNotFound(InitError):
    pass


class InitError_Init_VRDashboardStartupFailed(InitError):
    pass


class InitError_Init_VRHomeNotFound(InitError):
    pass


class InitError_Init_VRHomeStartupFailed(InitError):
    pass


class InitError_Init_RebootingBusy(InitError):
    pass


class InitError_Init_FirmwareUpdateBusy(InitError):
    pass


class InitError_Init_FirmwareRecoveryBusy(InitError):
    pass


class InitError_Init_USBServiceBusy(InitError):
    pass


class InitError_Init_VRWebHelperStartupFailed(InitError):
    pass


class InitError_Init_TrackerManagerInitFailed(InitError):
    pass


class InitError_Init_AlreadyRunning(InitError):
    pass


class InitError_Init_FailedForVrMonitor(InitError):
    pass


class InitError_Init_PropertyManagerInitFailed(InitError):
    pass


class InitError_Init_WebServerFailed(InitError):
    pass


class InitError_Init_IllegalTypeTransition(InitError):
    pass


class InitError_Init_MismatchedRuntimes(InitError):
    pass


class InitError_Init_InvalidProcessId(InitError):
    pass


class InitError_Init_VRServiceStartupFailed(InitError):
    pass


class InitError_Init_PrismNeedsNewDrivers(InitError):
    pass


class InitError_Init_PrismStartupTimedOut(InitError):
    pass


class InitError_Init_CouldNotStartPrism(InitError):
    pass


class InitError_Init_PrismClientInitFailed(InitError):
    pass


class InitError_Init_PrismClientStartFailed(InitError):
    pass


class InitError_Init_PrismExitedUnexpectedly(InitError):
    pass


class InitError_Init_BadLuid(InitError):
    pass


class InitError_Init_NoServerForAppContainer(InitError):
    pass


class InitError_Init_DuplicateBootstrapper(InitError):
    pass


class InitError_Init_VRDashboardServicePending(InitError):
    pass


class InitError_Init_VRDashboardServiceTimeout(InitError):
    pass


class InitError_Init_VRDashboardServiceStopped(InitError):
    pass


class InitError_Init_VRDashboardAlreadyStarted(InitError):
    pass


class InitError_Init_VRDashboardCopyFailed(InitError):
    pass


class InitError_Init_VRDashboardTokenFailure(InitError):
    pass


class InitError_Init_VRDashboardEnvironmentFailure(InitError):
    pass


class InitError_Init_VRDashboardPathFailure(InitError):
    pass


class InitError_Driver_Failed(InitError):
    pass


class InitError_Driver_Unknown(InitError):
    pass


class InitError_Driver_HmdUnknown(InitError):
    pass


class InitError_Driver_NotLoaded(InitError):
    pass


class InitError_Driver_RuntimeOutOfDate(InitError):
    pass


class InitError_Driver_HmdInUse(InitError):
    pass


class InitError_Driver_NotCalibrated(InitError):
    pass


class InitError_Driver_CalibrationInvalid(InitError):
    pass


class InitError_Driver_HmdDisplayNotFound(InitError):
    pass


class InitError_Driver_TrackedDeviceInterfaceUnknown(InitError):
    pass


class InitError_Driver_HmdDriverIdOutOfBounds(InitError):
    pass


class InitError_Driver_HmdDisplayMirrored(InitError):
    pass


class InitError_Driver_HmdDisplayNotFoundLaptop(InitError):
    pass


class InitError_Driver_PeerDriverNotInstalled(InitError):
    pass


class InitError_Driver_WirelessHmdNotConnected(InitError):
    pass


class InitError_IPC_ServerInitFailed(InitError):
    pass


class InitError_IPC_ConnectFailed(InitError):
    pass


class InitError_IPC_SharedStateInitFailed(InitError):
    pass


class InitError_IPC_CompositorInitFailed(InitError):
    pass


class InitError_IPC_MutexInitFailed(InitError):
    pass


class InitError_IPC_Failed(InitError):
    pass


class InitError_IPC_CompositorConnectFailed(InitError):
    pass


class InitError_IPC_CompositorInvalidConnectResponse(InitError):
    pass


class InitError_IPC_ConnectFailedAfterMultipleAttempts(InitError):
    pass


class InitError_IPC_ConnectFailedAfterTargetExited(InitError):
    pass


class InitError_IPC_NamespaceUnavailable(InitError):
    pass


class InitError_Compositor_Failed(InitError):
    pass


class InitError_Compositor_D3D11HardwareRequired(InitError):
    pass


class InitError_Compositor_FirmwareRequiresUpdate(InitError):
    pass


class InitError_Compositor_OverlayInitFailed(InitError):
    pass


class InitError_Compositor_ScreenshotsInitFailed(InitError):
    pass


class InitError_Compositor_UnableToCreateDevice(InitError):
    pass


class InitError_Compositor_SharedStateIsNull(InitError):
    pass


class InitError_Compositor_NotificationManagerIsNull(InitError):
    pass


class InitError_Compositor_ResourceManagerClientIsNull(InitError):
    pass


class InitError_Compositor_MessageOverlaySharedStateInitFailure(InitError):
    pass


class InitError_Compositor_PropertiesInterfaceIsNull(InitError):
    pass


class InitError_Compositor_CreateFullscreenWindowFailed(InitError):
    pass


class InitError_Compositor_SettingsInterfaceIsNull(InitError):
    pass


class InitError_Compositor_FailedToShowWindow(InitError):
    pass


class InitError_Compositor_DistortInterfaceIsNull(InitError):
    pass


class InitError_Compositor_DisplayFrequencyFailure(InitError):
    pass


class InitError_Compositor_RendererInitializationFailed(InitError):
    pass


class InitError_Compositor_DXGIFactoryInterfaceIsNull(InitError):
    pass


class InitError_Compositor_DXGIFactoryCreateFailed(InitError):
    pass


class InitError_Compositor_DXGIFactoryQueryFailed(InitError):
    pass


class InitError_Compositor_InvalidAdapterDesktop(InitError):
    pass


class InitError_Compositor_InvalidHmdAttachment(InitError):
    pass


class InitError_Compositor_InvalidOutputDesktop(InitError):
    pass


class InitError_Compositor_InvalidDeviceProvided(InitError):
    pass


class InitError_Compositor_D3D11RendererInitializationFailed(InitError):
    pass


class InitError_Compositor_FailedToFindDisplayMode(InitError):
    pass


class InitError_Compositor_FailedToCreateSwapChain(InitError):
    pass


class InitError_Compositor_FailedToGetBackBuffer(InitError):
    pass


class InitError_Compositor_FailedToCreateRenderTarget(InitError):
    pass


class InitError_Compositor_FailedToCreateDXGI2SwapChain(InitError):
    pass


class InitError_Compositor_FailedtoGetDXGI2BackBuffer(InitError):
    pass


class InitError_Compositor_FailedToCreateDXGI2RenderTarget(InitError):
    pass


class InitError_Compositor_FailedToGetDXGIDeviceInterface(InitError):
    pass


class InitError_Compositor_SelectDisplayMode(InitError):
    pass


class InitError_Compositor_FailedToCreateNvAPIRenderTargets(InitError):
    pass


class InitError_Compositor_NvAPISetDisplayMode(InitError):
    pass


class InitError_Compositor_FailedToCreateDirectModeDisplay(InitError):
    pass


class InitError_Compositor_InvalidHmdPropertyContainer(InitError):
    pass


class InitError_Compositor_UpdateDisplayFrequency(InitError):
    pass


class InitError_Compositor_CreateRasterizerState(InitError):
    pass


class InitError_Compositor_CreateWireframeRasterizerState(InitError):
    pass


class InitError_Compositor_CreateSamplerState(InitError):
    pass


class InitError_Compositor_CreateClampToBorderSamplerState(InitError):
    pass


class InitError_Compositor_CreateAnisoSamplerState(InitError):
    pass


class InitError_Compositor_CreateOverlaySamplerState(InitError):
    pass


class InitError_Compositor_CreatePanoramaSamplerState(InitError):
    pass


class InitError_Compositor_CreateFontSamplerState(InitError):
    pass


class InitError_Compositor_CreateNoBlendState(InitError):
    pass


class InitError_Compositor_CreateBlendState(InitError):
    pass


class InitError_Compositor_CreateAlphaBlendState(InitError):
    pass


class InitError_Compositor_CreateBlendStateMaskR(InitError):
    pass


class InitError_Compositor_CreateBlendStateMaskG(InitError):
    pass


class InitError_Compositor_CreateBlendStateMaskB(InitError):
    pass


class InitError_Compositor_CreateDepthStencilState(InitError):
    pass


class InitError_Compositor_CreateDepthStencilStateNoWrite(InitError):
    pass


class InitError_Compositor_CreateDepthStencilStateNoDepth(InitError):
    pass


class InitError_Compositor_CreateFlushTexture(InitError):
    pass


class InitError_Compositor_CreateDistortionSurfaces(InitError):
    pass


class InitError_Compositor_CreateConstantBuffer(InitError):
    pass


class InitError_Compositor_CreateHmdPoseConstantBuffer(InitError):
    pass


class InitError_Compositor_CreateHmdPoseStagingConstantBuffer(InitError):
    pass


class InitError_Compositor_CreateSharedFrameInfoConstantBuffer(InitError):
    pass


class InitError_Compositor_CreateOverlayConstantBuffer(InitError):
    pass


class InitError_Compositor_CreateSceneTextureIndexConstantBuffer(InitError):
    pass


class InitError_Compositor_CreateReadableSceneTextureIndexConstantBuffer(InitError):
    pass


class InitError_Compositor_CreateLayerGraphicsTextureIndexConstantBuffer(InitError):
    pass


class InitError_Compositor_CreateLayerComputeTextureIndexConstantBuffer(InitError):
    pass


class InitError_Compositor_CreateLayerComputeSceneTextureIndexConstantBuffer(InitError):
    pass


class InitError_Compositor_CreateComputeHmdPoseConstantBuffer(InitError):
    pass


class InitError_Compositor_CreateGeomConstantBuffer(InitError):
    pass


class InitError_Compositor_CreatePanelMaskConstantBuffer(InitError):
    pass


class InitError_Compositor_CreatePixelSimUBO(InitError):
    pass


class InitError_Compositor_CreateMSAARenderTextures(InitError):
    pass


class InitError_Compositor_CreateResolveRenderTextures(InitError):
    pass


class InitError_Compositor_CreateComputeResolveRenderTextures(InitError):
    pass


class InitError_Compositor_CreateDriverDirectModeResolveTextures(InitError):
    pass


class InitError_Compositor_OpenDriverDirectModeResolveTextures(InitError):
    pass


class InitError_Compositor_CreateFallbackSyncTexture(InitError):
    pass


class InitError_Compositor_ShareFallbackSyncTexture(InitError):
    pass


class InitError_Compositor_CreateOverlayIndexBuffer(InitError):
    pass


class InitError_Compositor_CreateOverlayVertexBuffer(InitError):
    pass


class InitError_Compositor_CreateTextVertexBuffer(InitError):
    pass


class InitError_Compositor_CreateTextIndexBuffer(InitError):
    pass


class InitError_Compositor_CreateMirrorTextures(InitError):
    pass


class InitError_Compositor_CreateLastFrameRenderTexture(InitError):
    pass


class InitError_Compositor_CreateMirrorOverlay(InitError):
    pass


class InitError_Compositor_FailedToCreateVirtualDisplayBackbuffer(InitError):
    pass


class InitError_Compositor_DisplayModeNotSupported(InitError):
    pass


class InitError_Compositor_CreateOverlayInvalidCall(InitError):
    pass


class InitError_Compositor_CreateOverlayAlreadyInitialized(InitError):
    pass


class InitError_Compositor_FailedToCreateMailbox(InitError):
    pass


class InitError_Compositor_WindowInterfaceIsNull(InitError):
    pass


class InitError_Compositor_SystemLayerCreateInstance(InitError):
    pass


class InitError_Compositor_SystemLayerCreateSession(InitError):
    pass


class InitError_Compositor_CreateInverseDistortUVs(InitError):
    pass


class InitError_Compositor_CreateBackbufferDepth(InitError):
    pass


class InitError_VendorSpecific_UnableToConnectToOculusRuntime(InitError):
    pass


class InitError_VendorSpecific_WindowsNotInDevMode(InitError):
    pass


class InitError_VendorSpecific_OculusLinkNotEnabled(InitError):
    pass


class InitError_VendorSpecific_HmdFound_CantOpenDevice(InitError):
    pass


class InitError_VendorSpecific_HmdFound_UnableToRequestConfigStart(InitError):
    pass


class InitError_VendorSpecific_HmdFound_NoStoredConfig(InitError):
    pass


class InitError_VendorSpecific_HmdFound_ConfigTooBig(InitError):
    pass


class InitError_VendorSpecific_HmdFound_ConfigTooSmall(InitError):
    pass


class InitError_VendorSpecific_HmdFound_UnableToInitZLib(InitError):
    pass


class InitError_VendorSpecific_HmdFound_CantReadFirmwareVersion(InitError):
    pass


class InitError_VendorSpecific_HmdFound_UnableToSendUserDataStart(InitError):
    pass


class InitError_VendorSpecific_HmdFound_UnableToGetUserDataStart(InitError):
    pass


class InitError_VendorSpecific_HmdFound_UnableToGetUserDataNext(InitError):
    pass


class InitError_VendorSpecific_HmdFound_UserDataAddressRange(InitError):
    pass


class InitError_VendorSpecific_HmdFound_UserDataError(InitError):
    pass


class InitError_VendorSpecific_HmdFound_ConfigFailedSanityCheck(InitError):
    pass


class InitError_VendorSpecific_OculusRuntimeBadInstall(InitError):
    pass


class InitError_VendorSpecific_HmdFound_UnexpectedConfiguration_1(InitError):
    pass


class InitError_Steam_SteamInstallationNotFound(InitError):
    pass


class InitError_LastError(InitError):
    pass


InitError.error_index[0] = InitError_None
InitError.error_index[1] = InitError_Unknown
InitError.error_index[100] = InitError_Init_InstallationNotFound
InitError.error_index[101] = InitError_Init_InstallationCorrupt
InitError.error_index[102] = InitError_Init_VRClientDLLNotFound
InitError.error_index[103] = InitError_Init_FileNotFound
InitError.error_index[104] = InitError_Init_FactoryNotFound
InitError.error_index[105] = InitError_Init_InterfaceNotFound
InitError.error_index[106] = InitError_Init_InvalidInterface
InitError.error_index[107] = InitError_Init_UserConfigDirectoryInvalid
InitError.error_index[108] = InitError_Init_HmdNotFound
InitError.error_index[109] = InitError_Init_NotInitialized
InitError.error_index[110] = InitError_Init_PathRegistryNotFound
InitError.error_index[111] = InitError_Init_NoConfigPath
InitError.error_index[112] = InitError_Init_NoLogPath
InitError.error_index[113] = InitError_Init_PathRegistryNotWritable
InitError.error_index[114] = InitError_Init_AppInfoInitFailed
InitError.error_index[115] = InitError_Init_Retry
InitError.error_index[116] = InitError_Init_InitCanceledByUser
InitError.error_index[117] = InitError_Init_AnotherAppLaunching
InitError.error_index[118] = InitError_Init_SettingsInitFailed
InitError.error_index[119] = InitError_Init_ShuttingDown
InitError.error_index[120] = InitError_Init_TooManyObjects
InitError.error_index[121] = InitError_Init_NoServerForBackgroundApp
InitError.error_index[122] = InitError_Init_NotSupportedWithCompositor
InitError.error_index[123] = InitError_Init_NotAvailableToUtilityApps
InitError.error_index[124] = InitError_Init_Internal
InitError.error_index[125] = InitError_Init_HmdDriverIdIsNone
InitError.error_index[126] = InitError_Init_HmdNotFoundPresenceFailed
InitError.error_index[127] = InitError_Init_VRMonitorNotFound
InitError.error_index[128] = InitError_Init_VRMonitorStartupFailed
InitError.error_index[129] = InitError_Init_LowPowerWatchdogNotSupported
InitError.error_index[130] = InitError_Init_InvalidApplicationType
InitError.error_index[131] = InitError_Init_NotAvailableToWatchdogApps
InitError.error_index[132] = InitError_Init_WatchdogDisabledInSettings
InitError.error_index[133] = InitError_Init_VRDashboardNotFound
InitError.error_index[134] = InitError_Init_VRDashboardStartupFailed
InitError.error_index[135] = InitError_Init_VRHomeNotFound
InitError.error_index[136] = InitError_Init_VRHomeStartupFailed
InitError.error_index[137] = InitError_Init_RebootingBusy
InitError.error_index[138] = InitError_Init_FirmwareUpdateBusy
InitError.error_index[139] = InitError_Init_FirmwareRecoveryBusy
InitError.error_index[140] = InitError_Init_USBServiceBusy
InitError.error_index[141] = InitError_Init_VRWebHelperStartupFailed
InitError.error_index[142] = InitError_Init_TrackerManagerInitFailed
InitError.error_index[143] = InitError_Init_AlreadyRunning
InitError.error_index[144] = InitError_Init_FailedForVrMonitor
InitError.error_index[145] = InitError_Init_PropertyManagerInitFailed
InitError.error_index[146] = InitError_Init_WebServerFailed
InitError.error_index[147] = InitError_Init_IllegalTypeTransition
InitError.error_index[148] = InitError_Init_MismatchedRuntimes
InitError.error_index[149] = InitError_Init_InvalidProcessId
InitError.error_index[150] = InitError_Init_VRServiceStartupFailed
InitError.error_index[151] = InitError_Init_PrismNeedsNewDrivers
InitError.error_index[152] = InitError_Init_PrismStartupTimedOut
InitError.error_index[153] = InitError_Init_CouldNotStartPrism
InitError.error_index[154] = InitError_Init_PrismClientInitFailed
InitError.error_index[155] = InitError_Init_PrismClientStartFailed
InitError.error_index[156] = InitError_Init_PrismExitedUnexpectedly
InitError.error_index[157] = InitError_Init_BadLuid
InitError.error_index[158] = InitError_Init_NoServerForAppContainer
InitError.error_index[159] = InitError_Init_DuplicateBootstrapper
InitError.error_index[160] = InitError_Init_VRDashboardServicePending
InitError.error_index[161] = InitError_Init_VRDashboardServiceTimeout
InitError.error_index[162] = InitError_Init_VRDashboardServiceStopped
InitError.error_index[163] = InitError_Init_VRDashboardAlreadyStarted
InitError.error_index[164] = InitError_Init_VRDashboardCopyFailed
InitError.error_index[165] = InitError_Init_VRDashboardTokenFailure
InitError.error_index[166] = InitError_Init_VRDashboardEnvironmentFailure
InitError.error_index[167] = InitError_Init_VRDashboardPathFailure
InitError.error_index[200] = InitError_Driver_Failed
InitError.error_index[201] = InitError_Driver_Unknown
InitError.error_index[202] = InitError_Driver_HmdUnknown
InitError.error_index[203] = InitError_Driver_NotLoaded
InitError.error_index[204] = InitError_Driver_RuntimeOutOfDate
InitError.error_index[205] = InitError_Driver_HmdInUse
InitError.error_index[206] = InitError_Driver_NotCalibrated
InitError.error_index[207] = InitError_Driver_CalibrationInvalid
InitError.error_index[208] = InitError_Driver_HmdDisplayNotFound
InitError.error_index[209] = InitError_Driver_TrackedDeviceInterfaceUnknown
InitError.error_index[211] = InitError_Driver_HmdDriverIdOutOfBounds
InitError.error_index[212] = InitError_Driver_HmdDisplayMirrored
InitError.error_index[213] = InitError_Driver_HmdDisplayNotFoundLaptop
InitError.error_index[214] = InitError_Driver_PeerDriverNotInstalled
InitError.error_index[215] = InitError_Driver_WirelessHmdNotConnected
InitError.error_index[300] = InitError_IPC_ServerInitFailed
InitError.error_index[301] = InitError_IPC_ConnectFailed
InitError.error_index[302] = InitError_IPC_SharedStateInitFailed
InitError.error_index[303] = InitError_IPC_CompositorInitFailed
InitError.error_index[304] = InitError_IPC_MutexInitFailed
InitError.error_index[305] = InitError_IPC_Failed
InitError.error_index[306] = InitError_IPC_CompositorConnectFailed
InitError.error_index[307] = InitError_IPC_CompositorInvalidConnectResponse
InitError.error_index[308] = InitError_IPC_ConnectFailedAfterMultipleAttempts
InitError.error_index[309] = InitError_IPC_ConnectFailedAfterTargetExited
InitError.error_index[310] = InitError_IPC_NamespaceUnavailable
InitError.error_index[400] = InitError_Compositor_Failed
InitError.error_index[401] = InitError_Compositor_D3D11HardwareRequired
InitError.error_index[402] = InitError_Compositor_FirmwareRequiresUpdate
InitError.error_index[403] = InitError_Compositor_OverlayInitFailed
InitError.error_index[404] = InitError_Compositor_ScreenshotsInitFailed
InitError.error_index[405] = InitError_Compositor_UnableToCreateDevice
InitError.error_index[406] = InitError_Compositor_SharedStateIsNull
InitError.error_index[407] = InitError_Compositor_NotificationManagerIsNull
InitError.error_index[408] = InitError_Compositor_ResourceManagerClientIsNull
InitError.error_index[409] = InitError_Compositor_MessageOverlaySharedStateInitFailure
InitError.error_index[410] = InitError_Compositor_PropertiesInterfaceIsNull
InitError.error_index[411] = InitError_Compositor_CreateFullscreenWindowFailed
InitError.error_index[412] = InitError_Compositor_SettingsInterfaceIsNull
InitError.error_index[413] = InitError_Compositor_FailedToShowWindow
InitError.error_index[414] = InitError_Compositor_DistortInterfaceIsNull
InitError.error_index[415] = InitError_Compositor_DisplayFrequencyFailure
InitError.error_index[416] = InitError_Compositor_RendererInitializationFailed
InitError.error_index[417] = InitError_Compositor_DXGIFactoryInterfaceIsNull
InitError.error_index[418] = InitError_Compositor_DXGIFactoryCreateFailed
InitError.error_index[419] = InitError_Compositor_DXGIFactoryQueryFailed
InitError.error_index[420] = InitError_Compositor_InvalidAdapterDesktop
InitError.error_index[421] = InitError_Compositor_InvalidHmdAttachment
InitError.error_index[422] = InitError_Compositor_InvalidOutputDesktop
InitError.error_index[423] = InitError_Compositor_InvalidDeviceProvided
InitError.error_index[424] = InitError_Compositor_D3D11RendererInitializationFailed
InitError.error_index[425] = InitError_Compositor_FailedToFindDisplayMode
InitError.error_index[426] = InitError_Compositor_FailedToCreateSwapChain
InitError.error_index[427] = InitError_Compositor_FailedToGetBackBuffer
InitError.error_index[428] = InitError_Compositor_FailedToCreateRenderTarget
InitError.error_index[429] = InitError_Compositor_FailedToCreateDXGI2SwapChain
InitError.error_index[430] = InitError_Compositor_FailedtoGetDXGI2BackBuffer
InitError.error_index[431] = InitError_Compositor_FailedToCreateDXGI2RenderTarget
InitError.error_index[432] = InitError_Compositor_FailedToGetDXGIDeviceInterface
InitError.error_index[433] = InitError_Compositor_SelectDisplayMode
InitError.error_index[434] = InitError_Compositor_FailedToCreateNvAPIRenderTargets
InitError.error_index[435] = InitError_Compositor_NvAPISetDisplayMode
InitError.error_index[436] = InitError_Compositor_FailedToCreateDirectModeDisplay
InitError.error_index[437] = InitError_Compositor_InvalidHmdPropertyContainer
InitError.error_index[438] = InitError_Compositor_UpdateDisplayFrequency
InitError.error_index[439] = InitError_Compositor_CreateRasterizerState
InitError.error_index[440] = InitError_Compositor_CreateWireframeRasterizerState
InitError.error_index[441] = InitError_Compositor_CreateSamplerState
InitError.error_index[442] = InitError_Compositor_CreateClampToBorderSamplerState
InitError.error_index[443] = InitError_Compositor_CreateAnisoSamplerState
InitError.error_index[444] = InitError_Compositor_CreateOverlaySamplerState
InitError.error_index[445] = InitError_Compositor_CreatePanoramaSamplerState
InitError.error_index[446] = InitError_Compositor_CreateFontSamplerState
InitError.error_index[447] = InitError_Compositor_CreateNoBlendState
InitError.error_index[448] = InitError_Compositor_CreateBlendState
InitError.error_index[449] = InitError_Compositor_CreateAlphaBlendState
InitError.error_index[450] = InitError_Compositor_CreateBlendStateMaskR
InitError.error_index[451] = InitError_Compositor_CreateBlendStateMaskG
InitError.error_index[452] = InitError_Compositor_CreateBlendStateMaskB
InitError.error_index[453] = InitError_Compositor_CreateDepthStencilState
InitError.error_index[454] = InitError_Compositor_CreateDepthStencilStateNoWrite
InitError.error_index[455] = InitError_Compositor_CreateDepthStencilStateNoDepth
InitError.error_index[456] = InitError_Compositor_CreateFlushTexture
InitError.error_index[457] = InitError_Compositor_CreateDistortionSurfaces
InitError.error_index[458] = InitError_Compositor_CreateConstantBuffer
InitError.error_index[459] = InitError_Compositor_CreateHmdPoseConstantBuffer
InitError.error_index[460] = InitError_Compositor_CreateHmdPoseStagingConstantBuffer
InitError.error_index[461] = InitError_Compositor_CreateSharedFrameInfoConstantBuffer
InitError.error_index[462] = InitError_Compositor_CreateOverlayConstantBuffer
InitError.error_index[463] = InitError_Compositor_CreateSceneTextureIndexConstantBuffer
InitError.error_index[464] = InitError_Compositor_CreateReadableSceneTextureIndexConstantBuffer
InitError.error_index[465] = InitError_Compositor_CreateLayerGraphicsTextureIndexConstantBuffer
InitError.error_index[466] = InitError_Compositor_CreateLayerComputeTextureIndexConstantBuffer
InitError.error_index[467] = InitError_Compositor_CreateLayerComputeSceneTextureIndexConstantBuffer
InitError.error_index[468] = InitError_Compositor_CreateComputeHmdPoseConstantBuffer
InitError.error_index[469] = InitError_Compositor_CreateGeomConstantBuffer
InitError.error_index[470] = InitError_Compositor_CreatePanelMaskConstantBuffer
InitError.error_index[471] = InitError_Compositor_CreatePixelSimUBO
InitError.error_index[472] = InitError_Compositor_CreateMSAARenderTextures
InitError.error_index[473] = InitError_Compositor_CreateResolveRenderTextures
InitError.error_index[474] = InitError_Compositor_CreateComputeResolveRenderTextures
InitError.error_index[475] = InitError_Compositor_CreateDriverDirectModeResolveTextures
InitError.error_index[476] = InitError_Compositor_OpenDriverDirectModeResolveTextures
InitError.error_index[477] = InitError_Compositor_CreateFallbackSyncTexture
InitError.error_index[478] = InitError_Compositor_ShareFallbackSyncTexture
InitError.error_index[479] = InitError_Compositor_CreateOverlayIndexBuffer
InitError.error_index[480] = InitError_Compositor_CreateOverlayVertexBuffer
InitError.error_index[481] = InitError_Compositor_CreateTextVertexBuffer
InitError.error_index[482] = InitError_Compositor_CreateTextIndexBuffer
InitError.error_index[483] = InitError_Compositor_CreateMirrorTextures
InitError.error_index[484] = InitError_Compositor_CreateLastFrameRenderTexture
InitError.error_index[485] = InitError_Compositor_CreateMirrorOverlay
InitError.error_index[486] = InitError_Compositor_FailedToCreateVirtualDisplayBackbuffer
InitError.error_index[487] = InitError_Compositor_DisplayModeNotSupported
InitError.error_index[488] = InitError_Compositor_CreateOverlayInvalidCall
InitError.error_index[489] = InitError_Compositor_CreateOverlayAlreadyInitialized
InitError.error_index[490] = InitError_Compositor_FailedToCreateMailbox
InitError.error_index[491] = InitError_Compositor_WindowInterfaceIsNull
InitError.error_index[492] = InitError_Compositor_SystemLayerCreateInstance
InitError.error_index[493] = InitError_Compositor_SystemLayerCreateSession
InitError.error_index[494] = InitError_Compositor_CreateInverseDistortUVs
InitError.error_index[495] = InitError_Compositor_CreateBackbufferDepth
InitError.error_index[1000] = InitError_VendorSpecific_UnableToConnectToOculusRuntime
InitError.error_index[1001] = InitError_VendorSpecific_WindowsNotInDevMode
InitError.error_index[1002] = InitError_VendorSpecific_OculusLinkNotEnabled
InitError.error_index[1101] = InitError_VendorSpecific_HmdFound_CantOpenDevice
InitError.error_index[1102] = InitError_VendorSpecific_HmdFound_UnableToRequestConfigStart
InitError.error_index[1103] = InitError_VendorSpecific_HmdFound_NoStoredConfig
InitError.error_index[1104] = InitError_VendorSpecific_HmdFound_ConfigTooBig
InitError.error_index[1105] = InitError_VendorSpecific_HmdFound_ConfigTooSmall
InitError.error_index[1106] = InitError_VendorSpecific_HmdFound_UnableToInitZLib
InitError.error_index[1107] = InitError_VendorSpecific_HmdFound_CantReadFirmwareVersion
InitError.error_index[1108] = InitError_VendorSpecific_HmdFound_UnableToSendUserDataStart
InitError.error_index[1109] = InitError_VendorSpecific_HmdFound_UnableToGetUserDataStart
InitError.error_index[1110] = InitError_VendorSpecific_HmdFound_UnableToGetUserDataNext
InitError.error_index[1111] = InitError_VendorSpecific_HmdFound_UserDataAddressRange
InitError.error_index[1112] = InitError_VendorSpecific_HmdFound_UserDataError
InitError.error_index[1113] = InitError_VendorSpecific_HmdFound_ConfigFailedSanityCheck
InitError.error_index[1114] = InitError_VendorSpecific_OculusRuntimeBadInstall
InitError.error_index[1115] = InitError_VendorSpecific_HmdFound_UnexpectedConfiguration_1
InitError.error_index[2000] = InitError_Steam_SteamInstallationNotFound
InitError.error_index[2001] = InitError_LastError


class TrackedCameraError(ErrorCode):
    error_index = dict()


class TrackedCameraError_None(TrackedCameraError):
    is_error = False


class TrackedCameraError_OperationFailed(TrackedCameraError):
    pass


class TrackedCameraError_InvalidHandle(TrackedCameraError):
    pass


class TrackedCameraError_InvalidFrameHeaderVersion(TrackedCameraError):
    pass


class TrackedCameraError_OutOfHandles(TrackedCameraError):
    pass


class TrackedCameraError_IPCFailure(TrackedCameraError):
    pass


class TrackedCameraError_NotSupportedForThisDevice(TrackedCameraError):
    pass


class TrackedCameraError_SharedMemoryFailure(TrackedCameraError):
    pass


class TrackedCameraError_FrameBufferingFailure(TrackedCameraError):
    pass


class TrackedCameraError_StreamSetupFailure(TrackedCameraError):
    pass


class TrackedCameraError_InvalidGLTextureId(TrackedCameraError):
    pass


class TrackedCameraError_InvalidSharedTextureHandle(TrackedCameraError):
    pass


class TrackedCameraError_FailedToGetGLTextureId(TrackedCameraError):
    pass


class TrackedCameraError_SharedTextureFailure(TrackedCameraError):
    pass


class TrackedCameraError_NoFrameAvailable(TrackedCameraError):
    pass


class TrackedCameraError_InvalidArgument(TrackedCameraError):
    pass


class TrackedCameraError_InvalidFrameBufferSize(TrackedCameraError):
    pass


TrackedCameraError.error_index[0] = TrackedCameraError_None
TrackedCameraError.error_index[100] = TrackedCameraError_OperationFailed
TrackedCameraError.error_index[101] = TrackedCameraError_InvalidHandle
TrackedCameraError.error_index[102] = TrackedCameraError_InvalidFrameHeaderVersion
TrackedCameraError.error_index[103] = TrackedCameraError_OutOfHandles
TrackedCameraError.error_index[104] = TrackedCameraError_IPCFailure
TrackedCameraError.error_index[105] = TrackedCameraError_NotSupportedForThisDevice
TrackedCameraError.error_index[106] = TrackedCameraError_SharedMemoryFailure
TrackedCameraError.error_index[107] = TrackedCameraError_FrameBufferingFailure
TrackedCameraError.error_index[108] = TrackedCameraError_StreamSetupFailure
TrackedCameraError.error_index[109] = TrackedCameraError_InvalidGLTextureId
TrackedCameraError.error_index[110] = TrackedCameraError_InvalidSharedTextureHandle
TrackedCameraError.error_index[111] = TrackedCameraError_FailedToGetGLTextureId
TrackedCameraError.error_index[112] = TrackedCameraError_SharedTextureFailure
TrackedCameraError.error_index[113] = TrackedCameraError_NoFrameAvailable
TrackedCameraError.error_index[114] = TrackedCameraError_InvalidArgument
TrackedCameraError.error_index[115] = TrackedCameraError_InvalidFrameBufferSize


class ApplicationError(ErrorCode):
    error_index = dict()


class ApplicationError_None(ApplicationError):
    is_error = False


class ApplicationError_AppKeyAlreadyExists(ApplicationError):
    pass


class ApplicationError_NoManifest(ApplicationError):
    pass


class ApplicationError_NoApplication(ApplicationError):
    pass


class ApplicationError_InvalidIndex(ApplicationError):
    pass


class ApplicationError_UnknownApplication(ApplicationError):
    pass


class ApplicationError_IPCFailed(ApplicationError):
    pass


class ApplicationError_ApplicationAlreadyRunning(ApplicationError):
    pass


class ApplicationError_InvalidManifest(ApplicationError):
    pass


class ApplicationError_InvalidApplication(ApplicationError):
    pass


class ApplicationError_LaunchFailed(ApplicationError):
    pass


class ApplicationError_ApplicationAlreadyStarting(ApplicationError):
    pass


class ApplicationError_LaunchInProgress(ApplicationError):
    pass


class ApplicationError_OldApplicationQuitting(ApplicationError):
    pass


class ApplicationError_TransitionAborted(ApplicationError):
    pass


class ApplicationError_IsTemplate(ApplicationError):
    pass


class ApplicationError_SteamVRIsExiting(ApplicationError):
    pass


class ApplicationError_BufferTooSmall(ApplicationError, BufferTooSmallError):
    pass


class ApplicationError_PropertyNotSet(ApplicationError):
    pass


class ApplicationError_UnknownProperty(ApplicationError):
    pass


class ApplicationError_InvalidParameter(ApplicationError):
    pass


class ApplicationError_NotImplemented(ApplicationError):
    pass


ApplicationError.error_index[0] = ApplicationError_None
ApplicationError.error_index[100] = ApplicationError_AppKeyAlreadyExists
ApplicationError.error_index[101] = ApplicationError_NoManifest
ApplicationError.error_index[102] = ApplicationError_NoApplication
ApplicationError.error_index[103] = ApplicationError_InvalidIndex
ApplicationError.error_index[104] = ApplicationError_UnknownApplication
ApplicationError.error_index[105] = ApplicationError_IPCFailed
ApplicationError.error_index[106] = ApplicationError_ApplicationAlreadyRunning
ApplicationError.error_index[107] = ApplicationError_InvalidManifest
ApplicationError.error_index[108] = ApplicationError_InvalidApplication
ApplicationError.error_index[109] = ApplicationError_LaunchFailed
ApplicationError.error_index[110] = ApplicationError_ApplicationAlreadyStarting
ApplicationError.error_index[111] = ApplicationError_LaunchInProgress
ApplicationError.error_index[112] = ApplicationError_OldApplicationQuitting
ApplicationError.error_index[113] = ApplicationError_TransitionAborted
ApplicationError.error_index[114] = ApplicationError_IsTemplate
ApplicationError.error_index[115] = ApplicationError_SteamVRIsExiting
ApplicationError.error_index[200] = ApplicationError_BufferTooSmall
ApplicationError.error_index[201] = ApplicationError_PropertyNotSet
ApplicationError.error_index[202] = ApplicationError_UnknownProperty
ApplicationError.error_index[203] = ApplicationError_InvalidParameter
ApplicationError.error_index[300] = ApplicationError_NotImplemented


class SettingsError(ErrorCode):
    error_index = dict()


class SettingsError_None(SettingsError):
    is_error = False


class SettingsError_IPCFailed(SettingsError):
    pass


class SettingsError_WriteFailed(SettingsError):
    pass


class SettingsError_ReadFailed(SettingsError):
    pass


class SettingsError_JsonParseFailed(SettingsError):
    pass


class SettingsError_UnsetSettingHasNoDefault(SettingsError):
    pass


SettingsError.error_index[0] = SettingsError_None
SettingsError.error_index[1] = SettingsError_IPCFailed
SettingsError.error_index[2] = SettingsError_WriteFailed
SettingsError.error_index[3] = SettingsError_ReadFailed
SettingsError.error_index[4] = SettingsError_JsonParseFailed
SettingsError.error_index[5] = SettingsError_UnsetSettingHasNoDefault


class CompositorError(ErrorCode):
    error_index = dict()


class CompositorError_None(CompositorError):
    is_error = False


class CompositorError_RequestFailed(CompositorError):
    pass


class CompositorError_IncompatibleVersion(CompositorError):
    pass


class CompositorError_DoNotHaveFocus(CompositorError):
    pass


class CompositorError_InvalidTexture(CompositorError):
    pass


class CompositorError_IsNotSceneApplication(CompositorError):
    pass


class CompositorError_TextureIsOnWrongDevice(CompositorError):
    pass


class CompositorError_TextureUsesUnsupportedFormat(CompositorError):
    pass


class CompositorError_SharedTexturesNotSupported(CompositorError):
    pass


class CompositorError_IndexOutOfRange(CompositorError):
    pass


class CompositorError_AlreadySubmitted(CompositorError):
    pass


class CompositorError_InvalidBounds(CompositorError):
    pass


class CompositorError_AlreadySet(CompositorError):
    pass


CompositorError.error_index[0] = CompositorError_None
CompositorError.error_index[1] = CompositorError_RequestFailed
CompositorError.error_index[100] = CompositorError_IncompatibleVersion
CompositorError.error_index[101] = CompositorError_DoNotHaveFocus
CompositorError.error_index[102] = CompositorError_InvalidTexture
CompositorError.error_index[103] = CompositorError_IsNotSceneApplication
CompositorError.error_index[104] = CompositorError_TextureIsOnWrongDevice
CompositorError.error_index[105] = CompositorError_TextureUsesUnsupportedFormat
CompositorError.error_index[106] = CompositorError_SharedTexturesNotSupported
CompositorError.error_index[107] = CompositorError_IndexOutOfRange
CompositorError.error_index[108] = CompositorError_AlreadySubmitted
CompositorError.error_index[109] = CompositorError_InvalidBounds
CompositorError.error_index[110] = CompositorError_AlreadySet


class RenderModelError(ErrorCode):
    error_index = dict()


class RenderModelError_None(RenderModelError):
    is_error = False


class RenderModelError_Loading(RenderModelError):
    pass


class RenderModelError_NotSupported(RenderModelError):
    pass


class RenderModelError_InvalidArg(RenderModelError):
    pass


class RenderModelError_InvalidModel(RenderModelError):
    pass


class RenderModelError_NoShapes(RenderModelError):
    pass


class RenderModelError_MultipleShapes(RenderModelError):
    pass


class RenderModelError_TooManyVertices(RenderModelError):
    pass


class RenderModelError_MultipleTextures(RenderModelError):
    pass


class RenderModelError_BufferTooSmall(RenderModelError, BufferTooSmallError):
    pass


class RenderModelError_NotEnoughNormals(RenderModelError):
    pass


class RenderModelError_NotEnoughTexCoords(RenderModelError):
    pass


class RenderModelError_InvalidTexture(RenderModelError):
    pass


RenderModelError.error_index[0] = RenderModelError_None
RenderModelError.error_index[100] = RenderModelError_Loading
RenderModelError.error_index[200] = RenderModelError_NotSupported
RenderModelError.error_index[300] = RenderModelError_InvalidArg
RenderModelError.error_index[301] = RenderModelError_InvalidModel
RenderModelError.error_index[302] = RenderModelError_NoShapes
RenderModelError.error_index[303] = RenderModelError_MultipleShapes
RenderModelError.error_index[304] = RenderModelError_TooManyVertices
RenderModelError.error_index[305] = RenderModelError_MultipleTextures
RenderModelError.error_index[306] = RenderModelError_BufferTooSmall
RenderModelError.error_index[307] = RenderModelError_NotEnoughNormals
RenderModelError.error_index[308] = RenderModelError_NotEnoughTexCoords
RenderModelError.error_index[400] = RenderModelError_InvalidTexture


class ScreenshotError(ErrorCode):
    error_index = dict()


class ScreenshotError_None(ScreenshotError):
    is_error = False


class ScreenshotError_RequestFailed(ScreenshotError):
    pass


class ScreenshotError_IncompatibleVersion(ScreenshotError):
    pass


class ScreenshotError_NotFound(ScreenshotError):
    pass


class ScreenshotError_BufferTooSmall(ScreenshotError, BufferTooSmallError):
    pass


class ScreenshotError_ScreenshotAlreadyInProgress(ScreenshotError):
    pass


ScreenshotError.error_index[0] = ScreenshotError_None
ScreenshotError.error_index[1] = ScreenshotError_RequestFailed
ScreenshotError.error_index[100] = ScreenshotError_IncompatibleVersion
ScreenshotError.error_index[101] = ScreenshotError_NotFound
ScreenshotError.error_index[102] = ScreenshotError_BufferTooSmall
ScreenshotError.error_index[108] = ScreenshotError_ScreenshotAlreadyInProgress


class IOBufferError(ErrorCode):
    error_index = dict()


class IOBuffer_Success(IOBufferError):
    is_error = False


class IOBuffer_OperationFailed(IOBufferError):
    pass


class IOBuffer_InvalidHandle(IOBufferError):
    pass


class IOBuffer_InvalidArgument(IOBufferError):
    pass


class IOBuffer_PathExists(IOBufferError):
    pass


class IOBuffer_PathDoesNotExist(IOBufferError):
    pass


class IOBuffer_Permission(IOBufferError):
    pass


IOBufferError.error_index[0] = IOBuffer_Success
IOBufferError.error_index[100] = IOBuffer_OperationFailed
IOBufferError.error_index[101] = IOBuffer_InvalidHandle
IOBufferError.error_index[102] = IOBuffer_InvalidArgument
IOBufferError.error_index[103] = IOBuffer_PathExists
IOBufferError.error_index[104] = IOBuffer_PathDoesNotExist
IOBufferError.error_index[105] = IOBuffer_Permission


class DebugError(ErrorCode):
    error_index = dict()


class DebugError_Success(DebugError):
    is_error = False


class DebugError_BadParameter(DebugError):
    pass


DebugError.error_index[0] = DebugError_Success
DebugError.error_index[1] = DebugError_BadParameter
