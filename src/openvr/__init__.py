#!/bin/env python

# Unofficial python bindings for OpenVR API version 1.4.18
# from https://github.com/cmbruns/pyopenvr
# based on OpenVR C++ API at https://github.com/ValveSoftware/openvr

import os
import platform
import ctypes
from ctypes import *

from .version import __version__
import openvr.error_code
from openvr.error_code import OpenVRError


class Pack4Structure(Structure):
    _pack_ = 4


if sizeof(c_void_p) != 4 and platform.system() in ('Linux', 'Darwin'):
    PackHackStructure = Pack4Structure
else:
    PackHackStructure = Structure

################################################################
# Load OpenVR shared library, so we can access it using ctypes #
################################################################

# Detect 32-bit vs 64-bit python
# Detect platform
if sizeof(c_void_p) == 4:
    if platform.system() == 'Windows':
        _openvr_lib_name = "libopenvr_api_32"
    elif platform.system() == 'Linux':
        _openvr_lib_name = "libopenvr_api_32.so"
    elif platform.system() == 'Darwin':
        _openvr_lib_name = "libopenvr_api_32.dylib"    
    else:
        raise ValueError("Libraries not available for this platform: " + platform.system())
else:
    if platform.system() == 'Windows':
        _openvr_lib_name = "libopenvr_api_64"
    elif platform.system() == 'Linux':
        _openvr_lib_name = "libopenvr_api_64.so"
    elif platform.system() == 'Darwin':
        _openvr_lib_name = "libopenvr_api_32.dylib"  # Universal 32-bit and 64-bit library.
    else:
        raise ValueError("Libraries not available for this platform: " + platform.system())

# Load library
if platform.system() == 'Windows':
    # Add current directory to PATH, so we can load the DLL from right here.
    os.environ['PATH'] += os.pathsep + os.path.dirname(__file__)
else:
    _openvr_lib_name = os.path.join(os.path.dirname(__file__), _openvr_lib_name)

_openvr = cdll.LoadLibrary(_openvr_lib_name)

# Function pointer table calling convention
if platform.system() == 'Windows':
    OPENVR_FNTABLE_CALLTYPE = WINFUNCTYPE  # __stdcall in openvr_capi.h
else:
    OPENVR_FNTABLE_CALLTYPE = CFUNCTYPE  # __cdecl


def byref(arg):
    if arg is None:
        return None
    else:
        return ctypes.byref(arg)


# Forward declarations to avoid requiring vulkan.h
class VkDevice_T(Structure):
    pass


class VkPhysicalDevice_T(Structure):
    pass


class VkInstance_T(Structure):
    pass


class VkQueue_T(Structure):
    pass


# Forward declarations to avoid requiring d3d12.h
class ID3D12Resource(Structure):
    pass


class ID3D12CommandQueue(Structure):
    pass


####################
# Expose constants #
####################

k_nSteamVRVersionMajor = 1
k_nSteamVRVersionMinor = 4
k_nSteamVRVersionBuild = 18
k_nDriverNone = 0xFFFFFFFF
k_unMaxDriverDebugResponseSize = 32768
k_unTrackedDeviceIndex_Hmd = 0
k_unMaxTrackedDeviceCount = 64
k_unTrackedDeviceIndexOther = 0xFFFFFFFE
k_unTrackedDeviceIndexInvalid = 0xFFFFFFFF
k_ulInvalidPropertyContainer = 0
k_unInvalidPropertyTag = 0
k_ulInvalidDriverHandle = 0
k_unFloatPropertyTag = 1  # Use these tags to set/get common types as struct properties
k_unInt32PropertyTag = 2
k_unUint64PropertyTag = 3
k_unBoolPropertyTag = 4
k_unStringPropertyTag = 5
k_unHmdMatrix34PropertyTag = 20
k_unHmdMatrix44PropertyTag = 21
k_unHmdVector3PropertyTag = 22
k_unHmdVector4PropertyTag = 23
k_unHmdVector2PropertyTag = 24
k_unHmdQuadPropertyTag = 25
k_unHiddenAreaPropertyTag = 30
k_unPathHandleInfoTag = 31
k_unActionPropertyTag = 32
k_unInputValuePropertyTag = 33
k_unWildcardPropertyTag = 34
k_unHapticVibrationPropertyTag = 35
k_unSkeletonPropertyTag = 36
k_unSpatialAnchorPosePropertyTag = 40
k_unJsonPropertyTag = 41
k_unActiveActionSetPropertyTag = 42
k_unOpenVRInternalReserved_Start = 1000
k_unOpenVRInternalReserved_End = 10000
k_unMaxPropertyStringSize = 32*1024  # No string property will ever be longer than this length
k_ulInvalidActionHandle = 0
k_ulInvalidActionSetHandle = 0
k_ulInvalidInputValueHandle = 0
k_unControllerStateAxisCount = 5  # the number of axes in the controller state
k_ulOverlayHandleInvalid = 0
k_unInvalidBoneIndex = -1
k_unMaxDistortionFunctionParameters = 8
k_unScreenshotHandleInvalid = 0
IVRSystem_Version = 'IVRSystem_019'
k_unMaxApplicationKeyLength = 128  # The maximum length of an application key
k_pch_MimeType_HomeApp = 'vr/home'  # Currently recognized mime types
k_pch_MimeType_GameTheater = 'vr/game_theater'
IVRApplications_Version = 'IVRApplications_006'
k_unMaxSettingsKeyLength = 128  # The maximum length of a settings key
IVRSettings_Version = 'IVRSettings_002'
k_pch_SteamVR_Section = 'steamvr'
k_pch_SteamVR_RequireHmd_String = 'requireHmd'
k_pch_SteamVR_ForcedDriverKey_String = 'forcedDriver'
k_pch_SteamVR_ForcedHmdKey_String = 'forcedHmd'
k_pch_SteamVR_DisplayDebug_Bool = 'displayDebug'
k_pch_SteamVR_DebugProcessPipe_String = 'debugProcessPipe'
k_pch_SteamVR_DisplayDebugX_Int32 = 'displayDebugX'
k_pch_SteamVR_DisplayDebugY_Int32 = 'displayDebugY'
k_pch_SteamVR_SendSystemButtonToAllApps_Bool = 'sendSystemButtonToAllApps'
k_pch_SteamVR_LogLevel_Int32 = 'loglevel'
k_pch_SteamVR_IPD_Float = 'ipd'
k_pch_SteamVR_Background_String = 'background'
k_pch_SteamVR_BackgroundUseDomeProjection_Bool = 'backgroundUseDomeProjection'
k_pch_SteamVR_BackgroundCameraHeight_Float = 'backgroundCameraHeight'
k_pch_SteamVR_BackgroundDomeRadius_Float = 'backgroundDomeRadius'
k_pch_SteamVR_GridColor_String = 'gridColor'
k_pch_SteamVR_PlayAreaColor_String = 'playAreaColor'
k_pch_SteamVR_ShowStage_Bool = 'showStage'
k_pch_SteamVR_ActivateMultipleDrivers_Bool = 'activateMultipleDrivers'
k_pch_SteamVR_UsingSpeakers_Bool = 'usingSpeakers'
k_pch_SteamVR_SpeakersForwardYawOffsetDegrees_Float = 'speakersForwardYawOffsetDegrees'
k_pch_SteamVR_BaseStationPowerManagement_Bool = 'basestationPowerManagement'
k_pch_SteamVR_NeverKillProcesses_Bool = 'neverKillProcesses'
k_pch_SteamVR_SupersampleScale_Float = 'supersampleScale'
k_pch_SteamVR_MaxRecommendedResolution_Int32 = 'maxRecommendedResolution'
k_pch_SteamVR_MotionSmoothing_Bool = 'motionSmoothing'
k_pch_SteamVR_MotionSmoothingOverride_Int32 = 'motionSmoothingOverride'
k_pch_SteamVR_ForceFadeOnBadTracking_Bool = 'forceFadeOnBadTracking'
k_pch_SteamVR_DefaultMirrorView_Int32 = 'mirrorView'
k_pch_SteamVR_ShowMirrorView_Bool = 'showMirrorView'
k_pch_SteamVR_MirrorViewGeometry_String = 'mirrorViewGeometry'
k_pch_SteamVR_MirrorViewGeometryMaximized_String = 'mirrorViewGeometryMaximized'
k_pch_SteamVR_StartMonitorFromAppLaunch = 'startMonitorFromAppLaunch'
k_pch_SteamVR_StartCompositorFromAppLaunch_Bool = 'startCompositorFromAppLaunch'
k_pch_SteamVR_StartDashboardFromAppLaunch_Bool = 'startDashboardFromAppLaunch'
k_pch_SteamVR_StartOverlayAppsFromDashboard_Bool = 'startOverlayAppsFromDashboard'
k_pch_SteamVR_EnableHomeApp = 'enableHomeApp'
k_pch_SteamVR_CycleBackgroundImageTimeSec_Int32 = 'CycleBackgroundImageTimeSec'
k_pch_SteamVR_RetailDemo_Bool = 'retailDemo'
k_pch_SteamVR_IpdOffset_Float = 'ipdOffset'
k_pch_SteamVR_AllowSupersampleFiltering_Bool = 'allowSupersampleFiltering'
k_pch_SteamVR_SupersampleManualOverride_Bool = 'supersampleManualOverride'
k_pch_SteamVR_EnableLinuxVulkanAsync_Bool = 'enableLinuxVulkanAsync'
k_pch_SteamVR_AllowDisplayLockedMode_Bool = 'allowDisplayLockedMode'
k_pch_SteamVR_HaveStartedTutorialForNativeChaperoneDriver_Bool = 'haveStartedTutorialForNativeChaperoneDriver'
k_pch_SteamVR_ForceWindows32bitVRMonitor = 'forceWindows32BitVRMonitor'
k_pch_SteamVR_DebugInput = 'debugInput'
k_pch_SteamVR_DebugInputBinding = 'debugInputBinding'
k_pch_SteamVR_DoNotFadeToGrid = 'doNotFadeToGrid'
k_pch_SteamVR_InputBindingUIBlock = 'inputBindingUI'
k_pch_SteamVR_RenderCameraMode = 'renderCameraMode'
k_pch_SteamVR_EnableSharedResourceJournaling = 'enableSharedResourceJournaling'
k_pch_SteamVR_EnableSafeMode = 'enableSafeMode'
k_pch_SteamVR_PreferredRefreshRate = 'preferredRefreshRate'
k_pch_SteamVR_LastVersionNotice = 'lastVersionNotice'
k_pch_SteamVR_LastVersionNoticeDate = 'lastVersionNoticeDate'
k_pch_DirectMode_Section = 'direct_mode'
k_pch_DirectMode_Enable_Bool = 'enable'
k_pch_DirectMode_Count_Int32 = 'count'
k_pch_DirectMode_EdidVid_Int32 = 'edidVid'
k_pch_DirectMode_EdidPid_Int32 = 'edidPid'
k_pch_Lighthouse_Section = 'driver_lighthouse'
k_pch_Lighthouse_DisableIMU_Bool = 'disableimu'
k_pch_Lighthouse_DisableIMUExceptHMD_Bool = 'disableimuexcepthmd'
k_pch_Lighthouse_UseDisambiguation_String = 'usedisambiguation'
k_pch_Lighthouse_DisambiguationDebug_Int32 = 'disambiguationdebug'
k_pch_Lighthouse_PrimaryBasestation_Int32 = 'primarybasestation'
k_pch_Lighthouse_DBHistory_Bool = 'dbhistory'
k_pch_Lighthouse_EnableBluetooth_Bool = 'enableBluetooth'
k_pch_Lighthouse_PowerManagedBaseStations_String = 'PowerManagedBaseStations'
k_pch_Lighthouse_PowerManagedBaseStations2_String = 'PowerManagedBaseStations2'
k_pch_Lighthouse_InactivityTimeoutForBaseStations_Int32 = 'InactivityTimeoutForBaseStations'
k_pch_Lighthouse_EnableImuFallback_Bool = 'enableImuFallback'
k_pch_Lighthouse_NewPairing_Bool = 'newPairing'
k_pch_Null_Section = 'driver_null'
k_pch_Null_SerialNumber_String = 'serialNumber'
k_pch_Null_ModelNumber_String = 'modelNumber'
k_pch_Null_WindowX_Int32 = 'windowX'
k_pch_Null_WindowY_Int32 = 'windowY'
k_pch_Null_WindowWidth_Int32 = 'windowWidth'
k_pch_Null_WindowHeight_Int32 = 'windowHeight'
k_pch_Null_RenderWidth_Int32 = 'renderWidth'
k_pch_Null_RenderHeight_Int32 = 'renderHeight'
k_pch_Null_SecondsFromVsyncToPhotons_Float = 'secondsFromVsyncToPhotons'
k_pch_Null_DisplayFrequency_Float = 'displayFrequency'
k_pch_UserInterface_Section = 'userinterface'
k_pch_UserInterface_StatusAlwaysOnTop_Bool = 'StatusAlwaysOnTop'
k_pch_UserInterface_MinimizeToTray_Bool = 'MinimizeToTray'
k_pch_UserInterface_HidePopupsWhenStatusMinimized_Bool = 'HidePopupsWhenStatusMinimized'
k_pch_UserInterface_Screenshots_Bool = 'screenshots'
k_pch_UserInterface_ScreenshotType_Int = 'screenshotType'
k_pch_Notifications_Section = 'notifications'
k_pch_Notifications_DoNotDisturb_Bool = 'DoNotDisturb'
k_pch_Keyboard_Section = 'keyboard'
k_pch_Keyboard_TutorialCompletions = 'TutorialCompletions'
k_pch_Keyboard_ScaleX = 'ScaleX'
k_pch_Keyboard_ScaleY = 'ScaleY'
k_pch_Keyboard_OffsetLeftX = 'OffsetLeftX'
k_pch_Keyboard_OffsetRightX = 'OffsetRightX'
k_pch_Keyboard_OffsetY = 'OffsetY'
k_pch_Keyboard_Smoothing = 'Smoothing'
k_pch_Perf_Section = 'perfcheck'
k_pch_Perf_PerfGraphInHMD_Bool = 'perfGraphInHMD'
k_pch_Perf_AllowTimingStore_Bool = 'allowTimingStore'
k_pch_Perf_SaveTimingsOnExit_Bool = 'saveTimingsOnExit'
k_pch_Perf_TestData_Float = 'perfTestData'
k_pch_Perf_GPUProfiling_Bool = 'GPUProfiling'
k_pch_CollisionBounds_Section = 'collisionBounds'
k_pch_CollisionBounds_Style_Int32 = 'CollisionBoundsStyle'
k_pch_CollisionBounds_GroundPerimeterOn_Bool = 'CollisionBoundsGroundPerimeterOn'
k_pch_CollisionBounds_CenterMarkerOn_Bool = 'CollisionBoundsCenterMarkerOn'
k_pch_CollisionBounds_PlaySpaceOn_Bool = 'CollisionBoundsPlaySpaceOn'
k_pch_CollisionBounds_FadeDistance_Float = 'CollisionBoundsFadeDistance'
k_pch_CollisionBounds_ColorGammaR_Int32 = 'CollisionBoundsColorGammaR'
k_pch_CollisionBounds_ColorGammaG_Int32 = 'CollisionBoundsColorGammaG'
k_pch_CollisionBounds_ColorGammaB_Int32 = 'CollisionBoundsColorGammaB'
k_pch_CollisionBounds_ColorGammaA_Int32 = 'CollisionBoundsColorGammaA'
k_pch_Camera_Section = 'camera'
k_pch_Camera_EnableCamera_Bool = 'enableCamera'
k_pch_Camera_EnableCameraInDashboard_Bool = 'enableCameraInDashboard'
k_pch_Camera_EnableCameraForCollisionBounds_Bool = 'enableCameraForCollisionBounds'
k_pch_Camera_EnableCameraForRoomView_Bool = 'enableCameraForRoomView'
k_pch_Camera_BoundsColorGammaR_Int32 = 'cameraBoundsColorGammaR'
k_pch_Camera_BoundsColorGammaG_Int32 = 'cameraBoundsColorGammaG'
k_pch_Camera_BoundsColorGammaB_Int32 = 'cameraBoundsColorGammaB'
k_pch_Camera_BoundsColorGammaA_Int32 = 'cameraBoundsColorGammaA'
k_pch_Camera_BoundsStrength_Int32 = 'cameraBoundsStrength'
k_pch_Camera_RoomViewMode_Int32 = 'cameraRoomViewMode'
k_pch_audio_Section = 'audio'
k_pch_audio_OnPlaybackDevice_String = 'onPlaybackDevice'
k_pch_audio_OnRecordDevice_String = 'onRecordDevice'
k_pch_audio_OnPlaybackMirrorDevice_String = 'onPlaybackMirrorDevice'
k_pch_audio_OffPlaybackDevice_String = 'offPlaybackDevice'
k_pch_audio_OffRecordDevice_String = 'offRecordDevice'
k_pch_audio_VIVEHDMIGain = 'viveHDMIGain'
k_pch_Power_Section = 'power'
k_pch_Power_PowerOffOnExit_Bool = 'powerOffOnExit'
k_pch_Power_TurnOffScreensTimeout_Float = 'turnOffScreensTimeout'
k_pch_Power_TurnOffControllersTimeout_Float = 'turnOffControllersTimeout'
k_pch_Power_ReturnToWatchdogTimeout_Float = 'returnToWatchdogTimeout'
k_pch_Power_AutoLaunchSteamVROnButtonPress = 'autoLaunchSteamVROnButtonPress'
k_pch_Power_PauseCompositorOnStandby_Bool = 'pauseCompositorOnStandby'
k_pch_Dashboard_Section = 'dashboard'
k_pch_Dashboard_EnableDashboard_Bool = 'enableDashboard'
k_pch_Dashboard_ArcadeMode_Bool = 'arcadeMode'
k_pch_Dashboard_UseWebDashboard = 'useWebDashboard'
k_pch_Dashboard_UseWebSettings = 'useWebSettings'
k_pch_Dashboard_UseWebIPD = 'useWebIPD'
k_pch_Dashboard_UseWebPowerMenu = 'useWebPowerMenu'
k_pch_modelskin_Section = 'modelskins'
k_pch_Driver_Enable_Bool = 'enable'
k_pch_WebInterface_Section = 'WebInterface'
k_pch_WebInterface_WebEnable_Bool = 'WebEnable'
k_pch_WebInterface_WebPort_String = 'WebPort'
k_pch_VRWebHelper_Section = 'VRWebHelper'
k_pch_VRWebHelper_DebuggerEnabled_Bool = 'DebuggerEnabled'
k_pch_VRWebHelper_DebuggerPort_Int32 = 'DebuggerPort'
k_pch_TrackingOverride_Section = 'TrackingOverrides'
k_pch_App_BindingAutosaveURLSuffix_String = 'AutosaveURL'
k_pch_App_BindingCurrentURLSuffix_String = 'CurrentURL'
k_pch_App_NeedToUpdateAutosaveSuffix_Bool = 'NeedToUpdateAutosave'
k_pch_Trackers_Section = 'trackers'
k_pch_DesktopUI_Section = 'DesktopUI'
k_pch_LastKnown_Section = 'LastKnown'
k_pch_LastKnown_HMDManufacturer_String = 'HMDManufacturer'
k_pch_LastKnown_HMDModel_String = 'HMDModel'
k_pch_DismissedWarnings_Section = 'DismissedWarnings'
IVRChaperone_Version = 'IVRChaperone_003'
IVRChaperoneSetup_Version = 'IVRChaperoneSetup_006'
VRCompositor_ReprojectionReason_Cpu = 0x01
VRCompositor_ReprojectionReason_Gpu = 0x02
VRCompositor_ReprojectionAsync = 0x04  # This flag indicates the async reprojection mode is active,
VRCompositor_ReprojectionMotion = 0x08  # This flag indicates whether or not motion smoothing was triggered for this frame
VRCompositor_PredictionMask = 0x30  # The runtime may predict more than one frame (up to four) ahead if
VRCompositor_ThrottleMask = 0xC0  # Number of frames the compositor is throttling the application.
IVRCompositor_Version = 'IVRCompositor_022'
k_unNotificationTextMaxSize = 256
IVRNotifications_Version = 'IVRNotifications_002'
k_unVROverlayMaxKeyLength = 128  # The maximum length of an overlay key in bytes, counting the terminating null character.
k_unVROverlayMaxNameLength = 128  # The maximum length of an overlay name in bytes, counting the terminating null character.
k_unMaxOverlayCount = 64  # The maximum number of overlays that can exist in the system at one time.
k_unMaxOverlayIntersectionMaskPrimitivesCount = 32  # The maximum number of overlay intersection mask primitives per overlay
IVROverlay_Version = 'IVROverlay_019'
k_pch_Controller_Component_GDC2015 = 'gdc2015'  # Canonical coordinate system of the gdc 2015 wired controller, provided for backwards compatibility
k_pch_Controller_Component_Base = 'base'  # For controllers with an unambiguous 'base'.
k_pch_Controller_Component_Tip = 'tip'  # For controllers with an unambiguous 'tip' (used for 'laser-pointing')
k_pch_Controller_Component_HandGrip = 'handgrip'  # Neutral, ambidextrous hand-pose when holding controller. On plane between neutrally posed index finger and thumb
k_pch_Controller_Component_Status = 'status'  # 1:1 aspect ratio status area, with canonical [0,1] uv mapping
INVALID_TEXTURE_ID = -1
IVRRenderModels_Version = 'IVRRenderModels_006'
IVRExtendedDisplay_Version = 'IVRExtendedDisplay_001'
IVRTrackedCamera_Version = 'IVRTrackedCamera_005'
IVRScreenshots_Version = 'IVRScreenshots_001'
IVRResources_Version = 'IVRResources_001'
IVRDriverManager_Version = 'IVRDriverManager_001'
k_unMaxActionNameLength = 64
k_unMaxActionSetNameLength = 64
k_unMaxActionOriginCount = 16
k_unMaxBoneNameLength = 32
IVRInput_Version = 'IVRInput_006'
k_ulInvalidIOBufferHandle = 0
IVRIOBuffer_Version = 'IVRIOBuffer_002'
k_ulInvalidSpatialAnchorHandle = 0
IVRSpatialAnchors_Version = 'IVRSpatialAnchors_001'

#########################
# Expose enum constants #
#########################

ENUM_TYPE = c_uint32
ENUM_VALUE_TYPE = int

EVREye = ENUM_TYPE
Eye_Left = ENUM_VALUE_TYPE(0)
Eye_Right = ENUM_VALUE_TYPE(1)

ETextureType = ENUM_TYPE
TextureType_Invalid = ENUM_VALUE_TYPE(-1)
TextureType_DirectX = ENUM_VALUE_TYPE(0)
TextureType_OpenGL = ENUM_VALUE_TYPE(1)
TextureType_Vulkan = ENUM_VALUE_TYPE(2)
TextureType_IOSurface = ENUM_VALUE_TYPE(3)
TextureType_DirectX12 = ENUM_VALUE_TYPE(4)
TextureType_DXGISharedHandle = ENUM_VALUE_TYPE(5)
TextureType_Metal = ENUM_VALUE_TYPE(6)

EColorSpace = ENUM_TYPE
ColorSpace_Auto = ENUM_VALUE_TYPE(0)
ColorSpace_Gamma = ENUM_VALUE_TYPE(1)
ColorSpace_Linear = ENUM_VALUE_TYPE(2)

ETrackingResult = ENUM_TYPE
TrackingResult_Uninitialized = ENUM_VALUE_TYPE(1)
TrackingResult_Calibrating_InProgress = ENUM_VALUE_TYPE(100)
TrackingResult_Calibrating_OutOfRange = ENUM_VALUE_TYPE(101)
TrackingResult_Running_OK = ENUM_VALUE_TYPE(200)
TrackingResult_Running_OutOfRange = ENUM_VALUE_TYPE(201)
TrackingResult_Fallback_RotationOnly = ENUM_VALUE_TYPE(300)

ETrackedDeviceClass = ENUM_TYPE
TrackedDeviceClass_Invalid = ENUM_VALUE_TYPE(0)
TrackedDeviceClass_HMD = ENUM_VALUE_TYPE(1)
TrackedDeviceClass_Controller = ENUM_VALUE_TYPE(2)
TrackedDeviceClass_GenericTracker = ENUM_VALUE_TYPE(3)
TrackedDeviceClass_TrackingReference = ENUM_VALUE_TYPE(4)
TrackedDeviceClass_DisplayRedirect = ENUM_VALUE_TYPE(5)
TrackedDeviceClass_Max = ENUM_VALUE_TYPE(6)

ETrackedControllerRole = ENUM_TYPE
TrackedControllerRole_Invalid = ENUM_VALUE_TYPE(0)
TrackedControllerRole_LeftHand = ENUM_VALUE_TYPE(1)
TrackedControllerRole_RightHand = ENUM_VALUE_TYPE(2)
TrackedControllerRole_OptOut = ENUM_VALUE_TYPE(3)
TrackedControllerRole_Treadmill = ENUM_VALUE_TYPE(4)
TrackedControllerRole_Max = ENUM_VALUE_TYPE(5)

ETrackingUniverseOrigin = ENUM_TYPE
TrackingUniverseSeated = ENUM_VALUE_TYPE(0)
TrackingUniverseStanding = ENUM_VALUE_TYPE(1)
TrackingUniverseRawAndUncalibrated = ENUM_VALUE_TYPE(2)

EAdditionalRadioFeatures = ENUM_TYPE
AdditionalRadioFeatures_None = ENUM_VALUE_TYPE(0)
AdditionalRadioFeatures_HTCLinkBox = ENUM_VALUE_TYPE(1)
AdditionalRadioFeatures_InternalDongle = ENUM_VALUE_TYPE(2)
AdditionalRadioFeatures_ExternalDongle = ENUM_VALUE_TYPE(4)

ETrackedDeviceProperty = ENUM_TYPE
Prop_Invalid = ENUM_VALUE_TYPE(0)
Prop_TrackingSystemName_String = ENUM_VALUE_TYPE(1000)
Prop_ModelNumber_String = ENUM_VALUE_TYPE(1001)
Prop_SerialNumber_String = ENUM_VALUE_TYPE(1002)
Prop_RenderModelName_String = ENUM_VALUE_TYPE(1003)
Prop_WillDriftInYaw_Bool = ENUM_VALUE_TYPE(1004)
Prop_ManufacturerName_String = ENUM_VALUE_TYPE(1005)
Prop_TrackingFirmwareVersion_String = ENUM_VALUE_TYPE(1006)
Prop_HardwareRevision_String = ENUM_VALUE_TYPE(1007)
Prop_AllWirelessDongleDescriptions_String = ENUM_VALUE_TYPE(1008)
Prop_ConnectedWirelessDongle_String = ENUM_VALUE_TYPE(1009)
Prop_DeviceIsWireless_Bool = ENUM_VALUE_TYPE(1010)
Prop_DeviceIsCharging_Bool = ENUM_VALUE_TYPE(1011)
Prop_DeviceBatteryPercentage_Float = ENUM_VALUE_TYPE(1012)
Prop_StatusDisplayTransform_Matrix34 = ENUM_VALUE_TYPE(1013)
Prop_Firmware_UpdateAvailable_Bool = ENUM_VALUE_TYPE(1014)
Prop_Firmware_ManualUpdate_Bool = ENUM_VALUE_TYPE(1015)
Prop_Firmware_ManualUpdateURL_String = ENUM_VALUE_TYPE(1016)
Prop_HardwareRevision_Uint64 = ENUM_VALUE_TYPE(1017)
Prop_FirmwareVersion_Uint64 = ENUM_VALUE_TYPE(1018)
Prop_FPGAVersion_Uint64 = ENUM_VALUE_TYPE(1019)
Prop_VRCVersion_Uint64 = ENUM_VALUE_TYPE(1020)
Prop_RadioVersion_Uint64 = ENUM_VALUE_TYPE(1021)
Prop_DongleVersion_Uint64 = ENUM_VALUE_TYPE(1022)
Prop_BlockServerShutdown_Bool = ENUM_VALUE_TYPE(1023)
Prop_CanUnifyCoordinateSystemWithHmd_Bool = ENUM_VALUE_TYPE(1024)
Prop_ContainsProximitySensor_Bool = ENUM_VALUE_TYPE(1025)
Prop_DeviceProvidesBatteryStatus_Bool = ENUM_VALUE_TYPE(1026)
Prop_DeviceCanPowerOff_Bool = ENUM_VALUE_TYPE(1027)
Prop_Firmware_ProgrammingTarget_String = ENUM_VALUE_TYPE(1028)
Prop_DeviceClass_Int32 = ENUM_VALUE_TYPE(1029)
Prop_HasCamera_Bool = ENUM_VALUE_TYPE(1030)
Prop_DriverVersion_String = ENUM_VALUE_TYPE(1031)
Prop_Firmware_ForceUpdateRequired_Bool = ENUM_VALUE_TYPE(1032)
Prop_ViveSystemButtonFixRequired_Bool = ENUM_VALUE_TYPE(1033)
Prop_ParentDriver_Uint64 = ENUM_VALUE_TYPE(1034)
Prop_ResourceRoot_String = ENUM_VALUE_TYPE(1035)
Prop_RegisteredDeviceType_String = ENUM_VALUE_TYPE(1036)
Prop_InputProfilePath_String = ENUM_VALUE_TYPE(1037)
Prop_NeverTracked_Bool = ENUM_VALUE_TYPE(1038)
Prop_NumCameras_Int32 = ENUM_VALUE_TYPE(1039)
Prop_CameraFrameLayout_Int32 = ENUM_VALUE_TYPE(1040)
Prop_CameraStreamFormat_Int32 = ENUM_VALUE_TYPE(1041)
Prop_AdditionalDeviceSettingsPath_String = ENUM_VALUE_TYPE(1042)
Prop_Identifiable_Bool = ENUM_VALUE_TYPE(1043)
Prop_BootloaderVersion_Uint64 = ENUM_VALUE_TYPE(1044)
Prop_AdditionalSystemReportData_String = ENUM_VALUE_TYPE(1045)
Prop_CompositeFirmwareVersion_String = ENUM_VALUE_TYPE(1046)
Prop_ReportsTimeSinceVSync_Bool = ENUM_VALUE_TYPE(2000)
Prop_SecondsFromVsyncToPhotons_Float = ENUM_VALUE_TYPE(2001)
Prop_DisplayFrequency_Float = ENUM_VALUE_TYPE(2002)
Prop_UserIpdMeters_Float = ENUM_VALUE_TYPE(2003)
Prop_CurrentUniverseId_Uint64 = ENUM_VALUE_TYPE(2004)
Prop_PreviousUniverseId_Uint64 = ENUM_VALUE_TYPE(2005)
Prop_DisplayFirmwareVersion_Uint64 = ENUM_VALUE_TYPE(2006)
Prop_IsOnDesktop_Bool = ENUM_VALUE_TYPE(2007)
Prop_DisplayMCType_Int32 = ENUM_VALUE_TYPE(2008)
Prop_DisplayMCOffset_Float = ENUM_VALUE_TYPE(2009)
Prop_DisplayMCScale_Float = ENUM_VALUE_TYPE(2010)
Prop_EdidVendorID_Int32 = ENUM_VALUE_TYPE(2011)
Prop_DisplayMCImageLeft_String = ENUM_VALUE_TYPE(2012)
Prop_DisplayMCImageRight_String = ENUM_VALUE_TYPE(2013)
Prop_DisplayGCBlackClamp_Float = ENUM_VALUE_TYPE(2014)
Prop_EdidProductID_Int32 = ENUM_VALUE_TYPE(2015)
Prop_CameraToHeadTransform_Matrix34 = ENUM_VALUE_TYPE(2016)
Prop_DisplayGCType_Int32 = ENUM_VALUE_TYPE(2017)
Prop_DisplayGCOffset_Float = ENUM_VALUE_TYPE(2018)
Prop_DisplayGCScale_Float = ENUM_VALUE_TYPE(2019)
Prop_DisplayGCPrescale_Float = ENUM_VALUE_TYPE(2020)
Prop_DisplayGCImage_String = ENUM_VALUE_TYPE(2021)
Prop_LensCenterLeftU_Float = ENUM_VALUE_TYPE(2022)
Prop_LensCenterLeftV_Float = ENUM_VALUE_TYPE(2023)
Prop_LensCenterRightU_Float = ENUM_VALUE_TYPE(2024)
Prop_LensCenterRightV_Float = ENUM_VALUE_TYPE(2025)
Prop_UserHeadToEyeDepthMeters_Float = ENUM_VALUE_TYPE(2026)
Prop_CameraFirmwareVersion_Uint64 = ENUM_VALUE_TYPE(2027)
Prop_CameraFirmwareDescription_String = ENUM_VALUE_TYPE(2028)
Prop_DisplayFPGAVersion_Uint64 = ENUM_VALUE_TYPE(2029)
Prop_DisplayBootloaderVersion_Uint64 = ENUM_VALUE_TYPE(2030)
Prop_DisplayHardwareVersion_Uint64 = ENUM_VALUE_TYPE(2031)
Prop_AudioFirmwareVersion_Uint64 = ENUM_VALUE_TYPE(2032)
Prop_CameraCompatibilityMode_Int32 = ENUM_VALUE_TYPE(2033)
Prop_ScreenshotHorizontalFieldOfViewDegrees_Float = ENUM_VALUE_TYPE(2034)
Prop_ScreenshotVerticalFieldOfViewDegrees_Float = ENUM_VALUE_TYPE(2035)
Prop_DisplaySuppressed_Bool = ENUM_VALUE_TYPE(2036)
Prop_DisplayAllowNightMode_Bool = ENUM_VALUE_TYPE(2037)
Prop_DisplayMCImageWidth_Int32 = ENUM_VALUE_TYPE(2038)
Prop_DisplayMCImageHeight_Int32 = ENUM_VALUE_TYPE(2039)
Prop_DisplayMCImageNumChannels_Int32 = ENUM_VALUE_TYPE(2040)
Prop_DisplayMCImageData_Binary = ENUM_VALUE_TYPE(2041)
Prop_SecondsFromPhotonsToVblank_Float = ENUM_VALUE_TYPE(2042)
Prop_DriverDirectModeSendsVsyncEvents_Bool = ENUM_VALUE_TYPE(2043)
Prop_DisplayDebugMode_Bool = ENUM_VALUE_TYPE(2044)
Prop_GraphicsAdapterLuid_Uint64 = ENUM_VALUE_TYPE(2045)
Prop_DriverProvidedChaperonePath_String = ENUM_VALUE_TYPE(2048)
Prop_ExpectedTrackingReferenceCount_Int32 = ENUM_VALUE_TYPE(2049)
Prop_ExpectedControllerCount_Int32 = ENUM_VALUE_TYPE(2050)
Prop_NamedIconPathControllerLeftDeviceOff_String = ENUM_VALUE_TYPE(2051)
Prop_NamedIconPathControllerRightDeviceOff_String = ENUM_VALUE_TYPE(2052)
Prop_NamedIconPathTrackingReferenceDeviceOff_String = ENUM_VALUE_TYPE(2053)
Prop_DoNotApplyPrediction_Bool = ENUM_VALUE_TYPE(2054)
Prop_CameraToHeadTransforms_Matrix34_Array = ENUM_VALUE_TYPE(2055)
Prop_DistortionMeshResolution_Int32 = ENUM_VALUE_TYPE(2056)
Prop_DriverIsDrawingControllers_Bool = ENUM_VALUE_TYPE(2057)
Prop_DriverRequestsApplicationPause_Bool = ENUM_VALUE_TYPE(2058)
Prop_DriverRequestsReducedRendering_Bool = ENUM_VALUE_TYPE(2059)
Prop_MinimumIpdStepMeters_Float = ENUM_VALUE_TYPE(2060)
Prop_AudioBridgeFirmwareVersion_Uint64 = ENUM_VALUE_TYPE(2061)
Prop_ImageBridgeFirmwareVersion_Uint64 = ENUM_VALUE_TYPE(2062)
Prop_ImuToHeadTransform_Matrix34 = ENUM_VALUE_TYPE(2063)
Prop_ImuFactoryGyroBias_Vector3 = ENUM_VALUE_TYPE(2064)
Prop_ImuFactoryGyroScale_Vector3 = ENUM_VALUE_TYPE(2065)
Prop_ImuFactoryAccelerometerBias_Vector3 = ENUM_VALUE_TYPE(2066)
Prop_ImuFactoryAccelerometerScale_Vector3 = ENUM_VALUE_TYPE(2067)
Prop_ConfigurationIncludesLighthouse20Features_Bool = ENUM_VALUE_TYPE(2069)
Prop_AdditionalRadioFeatures_Uint64 = ENUM_VALUE_TYPE(2070)
Prop_CameraWhiteBalance_Vector4_Array = ENUM_VALUE_TYPE(2071)
Prop_CameraDistortionFunction_Int32_Array = ENUM_VALUE_TYPE(2072)
Prop_CameraDistortionCoefficients_Float_Array = ENUM_VALUE_TYPE(2073)
Prop_ExpectedControllerType_String = ENUM_VALUE_TYPE(2074)
Prop_DisplayAvailableFrameRates_Float_Array = ENUM_VALUE_TYPE(2080)
Prop_DisplaySupportsMultipleFramerates_Bool = ENUM_VALUE_TYPE(2081)
Prop_DashboardLayoutPathName_String = ENUM_VALUE_TYPE(2090)
Prop_DriverRequestedMuraCorrectionMode_Int32 = ENUM_VALUE_TYPE(2200)
Prop_DriverRequestedMuraFeather_InnerLeft_Int32 = ENUM_VALUE_TYPE(2201)
Prop_DriverRequestedMuraFeather_InnerRight_Int32 = ENUM_VALUE_TYPE(2202)
Prop_DriverRequestedMuraFeather_InnerTop_Int32 = ENUM_VALUE_TYPE(2203)
Prop_DriverRequestedMuraFeather_InnerBottom_Int32 = ENUM_VALUE_TYPE(2204)
Prop_DriverRequestedMuraFeather_OuterLeft_Int32 = ENUM_VALUE_TYPE(2205)
Prop_DriverRequestedMuraFeather_OuterRight_Int32 = ENUM_VALUE_TYPE(2206)
Prop_DriverRequestedMuraFeather_OuterTop_Int32 = ENUM_VALUE_TYPE(2207)
Prop_DriverRequestedMuraFeather_OuterBottom_Int32 = ENUM_VALUE_TYPE(2208)
Prop_AttachedDeviceId_String = ENUM_VALUE_TYPE(3000)
Prop_SupportedButtons_Uint64 = ENUM_VALUE_TYPE(3001)
Prop_Axis0Type_Int32 = ENUM_VALUE_TYPE(3002)
Prop_Axis1Type_Int32 = ENUM_VALUE_TYPE(3003)
Prop_Axis2Type_Int32 = ENUM_VALUE_TYPE(3004)
Prop_Axis3Type_Int32 = ENUM_VALUE_TYPE(3005)
Prop_Axis4Type_Int32 = ENUM_VALUE_TYPE(3006)
Prop_ControllerRoleHint_Int32 = ENUM_VALUE_TYPE(3007)
Prop_FieldOfViewLeftDegrees_Float = ENUM_VALUE_TYPE(4000)
Prop_FieldOfViewRightDegrees_Float = ENUM_VALUE_TYPE(4001)
Prop_FieldOfViewTopDegrees_Float = ENUM_VALUE_TYPE(4002)
Prop_FieldOfViewBottomDegrees_Float = ENUM_VALUE_TYPE(4003)
Prop_TrackingRangeMinimumMeters_Float = ENUM_VALUE_TYPE(4004)
Prop_TrackingRangeMaximumMeters_Float = ENUM_VALUE_TYPE(4005)
Prop_ModeLabel_String = ENUM_VALUE_TYPE(4006)
Prop_CanWirelessIdentify_Bool = ENUM_VALUE_TYPE(4007)
Prop_Nonce_Int32 = ENUM_VALUE_TYPE(4008)
Prop_IconPathName_String = ENUM_VALUE_TYPE(5000)
Prop_NamedIconPathDeviceOff_String = ENUM_VALUE_TYPE(5001)
Prop_NamedIconPathDeviceSearching_String = ENUM_VALUE_TYPE(5002)
Prop_NamedIconPathDeviceSearchingAlert_String = ENUM_VALUE_TYPE(5003)
Prop_NamedIconPathDeviceReady_String = ENUM_VALUE_TYPE(5004)
Prop_NamedIconPathDeviceReadyAlert_String = ENUM_VALUE_TYPE(5005)
Prop_NamedIconPathDeviceNotReady_String = ENUM_VALUE_TYPE(5006)
Prop_NamedIconPathDeviceStandby_String = ENUM_VALUE_TYPE(5007)
Prop_NamedIconPathDeviceAlertLow_String = ENUM_VALUE_TYPE(5008)
Prop_DisplayHiddenArea_Binary_Start = ENUM_VALUE_TYPE(5100)
Prop_DisplayHiddenArea_Binary_End = ENUM_VALUE_TYPE(5150)
Prop_ParentContainer = ENUM_VALUE_TYPE(5151)
Prop_UserConfigPath_String = ENUM_VALUE_TYPE(6000)
Prop_InstallPath_String = ENUM_VALUE_TYPE(6001)
Prop_HasDisplayComponent_Bool = ENUM_VALUE_TYPE(6002)
Prop_HasControllerComponent_Bool = ENUM_VALUE_TYPE(6003)
Prop_HasCameraComponent_Bool = ENUM_VALUE_TYPE(6004)
Prop_HasDriverDirectModeComponent_Bool = ENUM_VALUE_TYPE(6005)
Prop_HasVirtualDisplayComponent_Bool = ENUM_VALUE_TYPE(6006)
Prop_HasSpatialAnchorsSupport_Bool = ENUM_VALUE_TYPE(6007)
Prop_ControllerType_String = ENUM_VALUE_TYPE(7000)
Prop_ControllerHandSelectionPriority_Int32 = ENUM_VALUE_TYPE(7002)
Prop_VendorSpecific_Reserved_Start = ENUM_VALUE_TYPE(10000)
Prop_VendorSpecific_Reserved_End = ENUM_VALUE_TYPE(10999)
Prop_TrackedDeviceProperty_Max = ENUM_VALUE_TYPE(1000000)

ETrackedPropertyError = ENUM_TYPE
TrackedProp_Success = ENUM_VALUE_TYPE(0)
TrackedProp_WrongDataType = ENUM_VALUE_TYPE(1)
TrackedProp_WrongDeviceClass = ENUM_VALUE_TYPE(2)
TrackedProp_BufferTooSmall = ENUM_VALUE_TYPE(3)
TrackedProp_UnknownProperty = ENUM_VALUE_TYPE(4)
TrackedProp_InvalidDevice = ENUM_VALUE_TYPE(5)
TrackedProp_CouldNotContactServer = ENUM_VALUE_TYPE(6)
TrackedProp_ValueNotProvidedByDevice = ENUM_VALUE_TYPE(7)
TrackedProp_StringExceedsMaximumLength = ENUM_VALUE_TYPE(8)
TrackedProp_NotYetAvailable = ENUM_VALUE_TYPE(9)
TrackedProp_PermissionDenied = ENUM_VALUE_TYPE(10)
TrackedProp_InvalidOperation = ENUM_VALUE_TYPE(11)
TrackedProp_CannotWriteToWildcards = ENUM_VALUE_TYPE(12)
TrackedProp_IPCReadFailure = ENUM_VALUE_TYPE(13)

EVRSubmitFlags = ENUM_TYPE
Submit_Default = ENUM_VALUE_TYPE(0)
Submit_LensDistortionAlreadyApplied = ENUM_VALUE_TYPE(1)
Submit_GlRenderBuffer = ENUM_VALUE_TYPE(2)
Submit_Reserved = ENUM_VALUE_TYPE(4)
Submit_TextureWithPose = ENUM_VALUE_TYPE(8)
Submit_TextureWithDepth = ENUM_VALUE_TYPE(16)

EVRState = ENUM_TYPE
VRState_Undefined = ENUM_VALUE_TYPE(-1)
VRState_Off = ENUM_VALUE_TYPE(0)
VRState_Searching = ENUM_VALUE_TYPE(1)
VRState_Searching_Alert = ENUM_VALUE_TYPE(2)
VRState_Ready = ENUM_VALUE_TYPE(3)
VRState_Ready_Alert = ENUM_VALUE_TYPE(4)
VRState_NotReady = ENUM_VALUE_TYPE(5)
VRState_Standby = ENUM_VALUE_TYPE(6)
VRState_Ready_Alert_Low = ENUM_VALUE_TYPE(7)

EVREventType = ENUM_TYPE
VREvent_None = ENUM_VALUE_TYPE(0)
VREvent_TrackedDeviceActivated = ENUM_VALUE_TYPE(100)
VREvent_TrackedDeviceDeactivated = ENUM_VALUE_TYPE(101)
VREvent_TrackedDeviceUpdated = ENUM_VALUE_TYPE(102)
VREvent_TrackedDeviceUserInteractionStarted = ENUM_VALUE_TYPE(103)
VREvent_TrackedDeviceUserInteractionEnded = ENUM_VALUE_TYPE(104)
VREvent_IpdChanged = ENUM_VALUE_TYPE(105)
VREvent_EnterStandbyMode = ENUM_VALUE_TYPE(106)
VREvent_LeaveStandbyMode = ENUM_VALUE_TYPE(107)
VREvent_TrackedDeviceRoleChanged = ENUM_VALUE_TYPE(108)
VREvent_WatchdogWakeUpRequested = ENUM_VALUE_TYPE(109)
VREvent_LensDistortionChanged = ENUM_VALUE_TYPE(110)
VREvent_PropertyChanged = ENUM_VALUE_TYPE(111)
VREvent_WirelessDisconnect = ENUM_VALUE_TYPE(112)
VREvent_WirelessReconnect = ENUM_VALUE_TYPE(113)
VREvent_ButtonPress = ENUM_VALUE_TYPE(200)
VREvent_ButtonUnpress = ENUM_VALUE_TYPE(201)
VREvent_ButtonTouch = ENUM_VALUE_TYPE(202)
VREvent_ButtonUntouch = ENUM_VALUE_TYPE(203)
VREvent_DualAnalog_Press = ENUM_VALUE_TYPE(250)
VREvent_DualAnalog_Unpress = ENUM_VALUE_TYPE(251)
VREvent_DualAnalog_Touch = ENUM_VALUE_TYPE(252)
VREvent_DualAnalog_Untouch = ENUM_VALUE_TYPE(253)
VREvent_DualAnalog_Move = ENUM_VALUE_TYPE(254)
VREvent_DualAnalog_ModeSwitch1 = ENUM_VALUE_TYPE(255)
VREvent_DualAnalog_ModeSwitch2 = ENUM_VALUE_TYPE(256)
VREvent_DualAnalog_Cancel = ENUM_VALUE_TYPE(257)
VREvent_MouseMove = ENUM_VALUE_TYPE(300)
VREvent_MouseButtonDown = ENUM_VALUE_TYPE(301)
VREvent_MouseButtonUp = ENUM_VALUE_TYPE(302)
VREvent_FocusEnter = ENUM_VALUE_TYPE(303)
VREvent_FocusLeave = ENUM_VALUE_TYPE(304)
VREvent_ScrollDiscrete = ENUM_VALUE_TYPE(305)
VREvent_TouchPadMove = ENUM_VALUE_TYPE(306)
VREvent_OverlayFocusChanged = ENUM_VALUE_TYPE(307)
VREvent_ReloadOverlays = ENUM_VALUE_TYPE(308)
VREvent_ScrollSmooth = ENUM_VALUE_TYPE(309)
VREvent_InputFocusCaptured = ENUM_VALUE_TYPE(400)
VREvent_InputFocusReleased = ENUM_VALUE_TYPE(401)
VREvent_SceneFocusLost = ENUM_VALUE_TYPE(402)
VREvent_SceneFocusGained = ENUM_VALUE_TYPE(403)
VREvent_SceneApplicationChanged = ENUM_VALUE_TYPE(404)
VREvent_SceneFocusChanged = ENUM_VALUE_TYPE(405)
VREvent_InputFocusChanged = ENUM_VALUE_TYPE(406)
VREvent_SceneApplicationSecondaryRenderingStarted = ENUM_VALUE_TYPE(407)
VREvent_SceneApplicationUsingWrongGraphicsAdapter = ENUM_VALUE_TYPE(408)
VREvent_ActionBindingReloaded = ENUM_VALUE_TYPE(409)
VREvent_HideRenderModels = ENUM_VALUE_TYPE(410)
VREvent_ShowRenderModels = ENUM_VALUE_TYPE(411)
VREvent_ConsoleOpened = ENUM_VALUE_TYPE(420)
VREvent_ConsoleClosed = ENUM_VALUE_TYPE(421)
VREvent_OverlayShown = ENUM_VALUE_TYPE(500)
VREvent_OverlayHidden = ENUM_VALUE_TYPE(501)
VREvent_DashboardActivated = ENUM_VALUE_TYPE(502)
VREvent_DashboardDeactivated = ENUM_VALUE_TYPE(503)
VREvent_DashboardRequested = ENUM_VALUE_TYPE(505)
VREvent_ResetDashboard = ENUM_VALUE_TYPE(506)
VREvent_RenderToast = ENUM_VALUE_TYPE(507)
VREvent_ImageLoaded = ENUM_VALUE_TYPE(508)
VREvent_ShowKeyboard = ENUM_VALUE_TYPE(509)
VREvent_HideKeyboard = ENUM_VALUE_TYPE(510)
VREvent_OverlayGamepadFocusGained = ENUM_VALUE_TYPE(511)
VREvent_OverlayGamepadFocusLost = ENUM_VALUE_TYPE(512)
VREvent_OverlaySharedTextureChanged = ENUM_VALUE_TYPE(513)
VREvent_ScreenshotTriggered = ENUM_VALUE_TYPE(516)
VREvent_ImageFailed = ENUM_VALUE_TYPE(517)
VREvent_DashboardOverlayCreated = ENUM_VALUE_TYPE(518)
VREvent_SwitchGamepadFocus = ENUM_VALUE_TYPE(519)
VREvent_RequestScreenshot = ENUM_VALUE_TYPE(520)
VREvent_ScreenshotTaken = ENUM_VALUE_TYPE(521)
VREvent_ScreenshotFailed = ENUM_VALUE_TYPE(522)
VREvent_SubmitScreenshotToDashboard = ENUM_VALUE_TYPE(523)
VREvent_ScreenshotProgressToDashboard = ENUM_VALUE_TYPE(524)
VREvent_PrimaryDashboardDeviceChanged = ENUM_VALUE_TYPE(525)
VREvent_RoomViewShown = ENUM_VALUE_TYPE(526)
VREvent_RoomViewHidden = ENUM_VALUE_TYPE(527)
VREvent_ShowUI = ENUM_VALUE_TYPE(528)
VREvent_ShowDevTools = ENUM_VALUE_TYPE(529)
VREvent_Notification_Shown = ENUM_VALUE_TYPE(600)
VREvent_Notification_Hidden = ENUM_VALUE_TYPE(601)
VREvent_Notification_BeginInteraction = ENUM_VALUE_TYPE(602)
VREvent_Notification_Destroyed = ENUM_VALUE_TYPE(603)
VREvent_Quit = ENUM_VALUE_TYPE(700)
VREvent_ProcessQuit = ENUM_VALUE_TYPE(701)
VREvent_QuitAborted_UserPrompt = ENUM_VALUE_TYPE(702)
VREvent_QuitAcknowledged = ENUM_VALUE_TYPE(703)
VREvent_DriverRequestedQuit = ENUM_VALUE_TYPE(704)
VREvent_RestartRequested = ENUM_VALUE_TYPE(705)
VREvent_ChaperoneDataHasChanged = ENUM_VALUE_TYPE(800)
VREvent_ChaperoneUniverseHasChanged = ENUM_VALUE_TYPE(801)
VREvent_ChaperoneTempDataHasChanged = ENUM_VALUE_TYPE(802)
VREvent_ChaperoneSettingsHaveChanged = ENUM_VALUE_TYPE(803)
VREvent_SeatedZeroPoseReset = ENUM_VALUE_TYPE(804)
VREvent_ChaperoneFlushCache = ENUM_VALUE_TYPE(805)
VREvent_ChaperoneRoomSetupStarting = ENUM_VALUE_TYPE(806)
VREvent_ChaperoneRoomSetupFinished = ENUM_VALUE_TYPE(807)
VREvent_AudioSettingsHaveChanged = ENUM_VALUE_TYPE(820)
VREvent_BackgroundSettingHasChanged = ENUM_VALUE_TYPE(850)
VREvent_CameraSettingsHaveChanged = ENUM_VALUE_TYPE(851)
VREvent_ReprojectionSettingHasChanged = ENUM_VALUE_TYPE(852)
VREvent_ModelSkinSettingsHaveChanged = ENUM_VALUE_TYPE(853)
VREvent_EnvironmentSettingsHaveChanged = ENUM_VALUE_TYPE(854)
VREvent_PowerSettingsHaveChanged = ENUM_VALUE_TYPE(855)
VREvent_EnableHomeAppSettingsHaveChanged = ENUM_VALUE_TYPE(856)
VREvent_SteamVRSectionSettingChanged = ENUM_VALUE_TYPE(857)
VREvent_LighthouseSectionSettingChanged = ENUM_VALUE_TYPE(858)
VREvent_NullSectionSettingChanged = ENUM_VALUE_TYPE(859)
VREvent_UserInterfaceSectionSettingChanged = ENUM_VALUE_TYPE(860)
VREvent_NotificationsSectionSettingChanged = ENUM_VALUE_TYPE(861)
VREvent_KeyboardSectionSettingChanged = ENUM_VALUE_TYPE(862)
VREvent_PerfSectionSettingChanged = ENUM_VALUE_TYPE(863)
VREvent_DashboardSectionSettingChanged = ENUM_VALUE_TYPE(864)
VREvent_WebInterfaceSectionSettingChanged = ENUM_VALUE_TYPE(865)
VREvent_TrackersSectionSettingChanged = ENUM_VALUE_TYPE(866)
VREvent_LastKnownSectionSettingChanged = ENUM_VALUE_TYPE(867)
VREvent_DismissedWarningsSectionSettingChanged = ENUM_VALUE_TYPE(868)
VREvent_StatusUpdate = ENUM_VALUE_TYPE(900)
VREvent_WebInterface_InstallDriverCompleted = ENUM_VALUE_TYPE(950)
VREvent_MCImageUpdated = ENUM_VALUE_TYPE(1000)
VREvent_FirmwareUpdateStarted = ENUM_VALUE_TYPE(1100)
VREvent_FirmwareUpdateFinished = ENUM_VALUE_TYPE(1101)
VREvent_KeyboardClosed = ENUM_VALUE_TYPE(1200)
VREvent_KeyboardCharInput = ENUM_VALUE_TYPE(1201)
VREvent_KeyboardDone = ENUM_VALUE_TYPE(1202)
VREvent_ApplicationTransitionStarted = ENUM_VALUE_TYPE(1300)
VREvent_ApplicationTransitionAborted = ENUM_VALUE_TYPE(1301)
VREvent_ApplicationTransitionNewAppStarted = ENUM_VALUE_TYPE(1302)
VREvent_ApplicationListUpdated = ENUM_VALUE_TYPE(1303)
VREvent_ApplicationMimeTypeLoad = ENUM_VALUE_TYPE(1304)
VREvent_ApplicationTransitionNewAppLaunchComplete = ENUM_VALUE_TYPE(1305)
VREvent_ProcessConnected = ENUM_VALUE_TYPE(1306)
VREvent_ProcessDisconnected = ENUM_VALUE_TYPE(1307)
VREvent_Compositor_MirrorWindowShown = ENUM_VALUE_TYPE(1400)
VREvent_Compositor_MirrorWindowHidden = ENUM_VALUE_TYPE(1401)
VREvent_Compositor_ChaperoneBoundsShown = ENUM_VALUE_TYPE(1410)
VREvent_Compositor_ChaperoneBoundsHidden = ENUM_VALUE_TYPE(1411)
VREvent_Compositor_DisplayDisconnected = ENUM_VALUE_TYPE(1412)
VREvent_Compositor_DisplayReconnected = ENUM_VALUE_TYPE(1413)
VREvent_Compositor_HDCPError = ENUM_VALUE_TYPE(1414)
VREvent_Compositor_ApplicationNotResponding = ENUM_VALUE_TYPE(1415)
VREvent_Compositor_ApplicationResumed = ENUM_VALUE_TYPE(1416)
VREvent_Compositor_OutOfVideoMemory = ENUM_VALUE_TYPE(1417)
VREvent_TrackedCamera_StartVideoStream = ENUM_VALUE_TYPE(1500)
VREvent_TrackedCamera_StopVideoStream = ENUM_VALUE_TYPE(1501)
VREvent_TrackedCamera_PauseVideoStream = ENUM_VALUE_TYPE(1502)
VREvent_TrackedCamera_ResumeVideoStream = ENUM_VALUE_TYPE(1503)
VREvent_TrackedCamera_EditingSurface = ENUM_VALUE_TYPE(1550)
VREvent_PerformanceTest_EnableCapture = ENUM_VALUE_TYPE(1600)
VREvent_PerformanceTest_DisableCapture = ENUM_VALUE_TYPE(1601)
VREvent_PerformanceTest_FidelityLevel = ENUM_VALUE_TYPE(1602)
VREvent_MessageOverlay_Closed = ENUM_VALUE_TYPE(1650)
VREvent_MessageOverlayCloseRequested = ENUM_VALUE_TYPE(1651)
VREvent_Input_HapticVibration = ENUM_VALUE_TYPE(1700)
VREvent_Input_BindingLoadFailed = ENUM_VALUE_TYPE(1701)
VREvent_Input_BindingLoadSuccessful = ENUM_VALUE_TYPE(1702)
VREvent_Input_ActionManifestReloaded = ENUM_VALUE_TYPE(1703)
VREvent_Input_ActionManifestLoadFailed = ENUM_VALUE_TYPE(1704)
VREvent_Input_ProgressUpdate = ENUM_VALUE_TYPE(1705)
VREvent_Input_TrackerActivated = ENUM_VALUE_TYPE(1706)
VREvent_Input_BindingsUpdated = ENUM_VALUE_TYPE(1707)
VREvent_SpatialAnchors_PoseUpdated = ENUM_VALUE_TYPE(1800)
VREvent_SpatialAnchors_DescriptorUpdated = ENUM_VALUE_TYPE(1801)
VREvent_SpatialAnchors_RequestPoseUpdate = ENUM_VALUE_TYPE(1802)
VREvent_SpatialAnchors_RequestDescriptorUpdate = ENUM_VALUE_TYPE(1803)
VREvent_SystemReport_Started = ENUM_VALUE_TYPE(1900)
VREvent_VendorSpecific_Reserved_Start = ENUM_VALUE_TYPE(10000)
VREvent_VendorSpecific_Reserved_End = ENUM_VALUE_TYPE(19999)

EDeviceActivityLevel = ENUM_TYPE
k_EDeviceActivityLevel_Unknown = ENUM_VALUE_TYPE(-1)
k_EDeviceActivityLevel_Idle = ENUM_VALUE_TYPE(0)
k_EDeviceActivityLevel_UserInteraction = ENUM_VALUE_TYPE(1)
k_EDeviceActivityLevel_UserInteraction_Timeout = ENUM_VALUE_TYPE(2)
k_EDeviceActivityLevel_Standby = ENUM_VALUE_TYPE(3)

EVRButtonId = ENUM_TYPE
k_EButton_System = ENUM_VALUE_TYPE(0)
k_EButton_ApplicationMenu = ENUM_VALUE_TYPE(1)
k_EButton_Grip = ENUM_VALUE_TYPE(2)
k_EButton_DPad_Left = ENUM_VALUE_TYPE(3)
k_EButton_DPad_Up = ENUM_VALUE_TYPE(4)
k_EButton_DPad_Right = ENUM_VALUE_TYPE(5)
k_EButton_DPad_Down = ENUM_VALUE_TYPE(6)
k_EButton_A = ENUM_VALUE_TYPE(7)
k_EButton_ProximitySensor = ENUM_VALUE_TYPE(31)
k_EButton_Axis0 = ENUM_VALUE_TYPE(32)
k_EButton_Axis1 = ENUM_VALUE_TYPE(33)
k_EButton_Axis2 = ENUM_VALUE_TYPE(34)
k_EButton_Axis3 = ENUM_VALUE_TYPE(35)
k_EButton_Axis4 = ENUM_VALUE_TYPE(36)
k_EButton_SteamVR_Touchpad = ENUM_VALUE_TYPE(32)
k_EButton_SteamVR_Trigger = ENUM_VALUE_TYPE(33)
k_EButton_Dashboard_Back = ENUM_VALUE_TYPE(2)
k_EButton_IndexController_A = ENUM_VALUE_TYPE(2)
k_EButton_IndexController_B = ENUM_VALUE_TYPE(1)
k_EButton_IndexController_JoyStick = ENUM_VALUE_TYPE(35)
k_EButton_Max = ENUM_VALUE_TYPE(64)

EVRMouseButton = ENUM_TYPE
VRMouseButton_Left = ENUM_VALUE_TYPE(1)
VRMouseButton_Right = ENUM_VALUE_TYPE(2)
VRMouseButton_Middle = ENUM_VALUE_TYPE(4)

EDualAnalogWhich = ENUM_TYPE
k_EDualAnalog_Left = ENUM_VALUE_TYPE(0)
k_EDualAnalog_Right = ENUM_VALUE_TYPE(1)

EShowUIType = ENUM_TYPE
ShowUI_ControllerBinding = ENUM_VALUE_TYPE(0)
ShowUI_ManageTrackers = ENUM_VALUE_TYPE(1)
ShowUI_Pairing = ENUM_VALUE_TYPE(3)
ShowUI_Settings = ENUM_VALUE_TYPE(4)

EHDCPError = ENUM_TYPE
HDCPError_None = ENUM_VALUE_TYPE(0)
HDCPError_LinkLost = ENUM_VALUE_TYPE(1)
HDCPError_Tampered = ENUM_VALUE_TYPE(2)
HDCPError_DeviceRevoked = ENUM_VALUE_TYPE(3)
HDCPError_Unknown = ENUM_VALUE_TYPE(4)

EVRInputError = ENUM_TYPE
VRInputError_None = ENUM_VALUE_TYPE(0)
VRInputError_NameNotFound = ENUM_VALUE_TYPE(1)
VRInputError_WrongType = ENUM_VALUE_TYPE(2)
VRInputError_InvalidHandle = ENUM_VALUE_TYPE(3)
VRInputError_InvalidParam = ENUM_VALUE_TYPE(4)
VRInputError_NoSteam = ENUM_VALUE_TYPE(5)
VRInputError_MaxCapacityReached = ENUM_VALUE_TYPE(6)
VRInputError_IPCError = ENUM_VALUE_TYPE(7)
VRInputError_NoActiveActionSet = ENUM_VALUE_TYPE(8)
VRInputError_InvalidDevice = ENUM_VALUE_TYPE(9)
VRInputError_InvalidSkeleton = ENUM_VALUE_TYPE(10)
VRInputError_InvalidBoneCount = ENUM_VALUE_TYPE(11)
VRInputError_InvalidCompressedData = ENUM_VALUE_TYPE(12)
VRInputError_NoData = ENUM_VALUE_TYPE(13)
VRInputError_BufferTooSmall = ENUM_VALUE_TYPE(14)
VRInputError_MismatchedActionManifest = ENUM_VALUE_TYPE(15)
VRInputError_MissingSkeletonData = ENUM_VALUE_TYPE(16)
VRInputError_InvalidBoneIndex = ENUM_VALUE_TYPE(17)

EVRSpatialAnchorError = ENUM_TYPE
VRSpatialAnchorError_Success = ENUM_VALUE_TYPE(0)
VRSpatialAnchorError_Internal = ENUM_VALUE_TYPE(1)
VRSpatialAnchorError_UnknownHandle = ENUM_VALUE_TYPE(2)
VRSpatialAnchorError_ArrayTooSmall = ENUM_VALUE_TYPE(3)
VRSpatialAnchorError_InvalidDescriptorChar = ENUM_VALUE_TYPE(4)
VRSpatialAnchorError_NotYetAvailable = ENUM_VALUE_TYPE(5)
VRSpatialAnchorError_NotAvailableInThisUniverse = ENUM_VALUE_TYPE(6)
VRSpatialAnchorError_PermanentlyUnavailable = ENUM_VALUE_TYPE(7)
VRSpatialAnchorError_WrongDriver = ENUM_VALUE_TYPE(8)
VRSpatialAnchorError_DescriptorTooLong = ENUM_VALUE_TYPE(9)
VRSpatialAnchorError_Unknown = ENUM_VALUE_TYPE(10)
VRSpatialAnchorError_NoRoomCalibration = ENUM_VALUE_TYPE(11)
VRSpatialAnchorError_InvalidArgument = ENUM_VALUE_TYPE(12)
VRSpatialAnchorError_UnknownDriver = ENUM_VALUE_TYPE(13)

EHiddenAreaMeshType = ENUM_TYPE
k_eHiddenAreaMesh_Standard = ENUM_VALUE_TYPE(0)
k_eHiddenAreaMesh_Inverse = ENUM_VALUE_TYPE(1)
k_eHiddenAreaMesh_LineLoop = ENUM_VALUE_TYPE(2)
k_eHiddenAreaMesh_Max = ENUM_VALUE_TYPE(3)

EVRControllerAxisType = ENUM_TYPE
k_eControllerAxis_None = ENUM_VALUE_TYPE(0)
k_eControllerAxis_TrackPad = ENUM_VALUE_TYPE(1)
k_eControllerAxis_Joystick = ENUM_VALUE_TYPE(2)
k_eControllerAxis_Trigger = ENUM_VALUE_TYPE(3)

EVRControllerEventOutputType = ENUM_TYPE
ControllerEventOutput_OSEvents = ENUM_VALUE_TYPE(0)
ControllerEventOutput_VREvents = ENUM_VALUE_TYPE(1)

ECollisionBoundsStyle = ENUM_TYPE
COLLISION_BOUNDS_STYLE_BEGINNER = ENUM_VALUE_TYPE(0)
COLLISION_BOUNDS_STYLE_INTERMEDIATE = ENUM_VALUE_TYPE(1)
COLLISION_BOUNDS_STYLE_SQUARES = ENUM_VALUE_TYPE(2)
COLLISION_BOUNDS_STYLE_ADVANCED = ENUM_VALUE_TYPE(3)
COLLISION_BOUNDS_STYLE_NONE = ENUM_VALUE_TYPE(4)
COLLISION_BOUNDS_STYLE_COUNT = ENUM_VALUE_TYPE(5)

EVROverlayError = ENUM_TYPE
VROverlayError_None = ENUM_VALUE_TYPE(0)
VROverlayError_UnknownOverlay = ENUM_VALUE_TYPE(10)
VROverlayError_InvalidHandle = ENUM_VALUE_TYPE(11)
VROverlayError_PermissionDenied = ENUM_VALUE_TYPE(12)
VROverlayError_OverlayLimitExceeded = ENUM_VALUE_TYPE(13)
VROverlayError_WrongVisibilityType = ENUM_VALUE_TYPE(14)
VROverlayError_KeyTooLong = ENUM_VALUE_TYPE(15)
VROverlayError_NameTooLong = ENUM_VALUE_TYPE(16)
VROverlayError_KeyInUse = ENUM_VALUE_TYPE(17)
VROverlayError_WrongTransformType = ENUM_VALUE_TYPE(18)
VROverlayError_InvalidTrackedDevice = ENUM_VALUE_TYPE(19)
VROverlayError_InvalidParameter = ENUM_VALUE_TYPE(20)
VROverlayError_ThumbnailCantBeDestroyed = ENUM_VALUE_TYPE(21)
VROverlayError_ArrayTooSmall = ENUM_VALUE_TYPE(22)
VROverlayError_RequestFailed = ENUM_VALUE_TYPE(23)
VROverlayError_InvalidTexture = ENUM_VALUE_TYPE(24)
VROverlayError_UnableToLoadFile = ENUM_VALUE_TYPE(25)
VROverlayError_KeyboardAlreadyInUse = ENUM_VALUE_TYPE(26)
VROverlayError_NoNeighbor = ENUM_VALUE_TYPE(27)
VROverlayError_TooManyMaskPrimitives = ENUM_VALUE_TYPE(29)
VROverlayError_BadMaskPrimitive = ENUM_VALUE_TYPE(30)
VROverlayError_TextureAlreadyLocked = ENUM_VALUE_TYPE(31)
VROverlayError_TextureLockCapacityReached = ENUM_VALUE_TYPE(32)
VROverlayError_TextureNotLocked = ENUM_VALUE_TYPE(33)

EVRApplicationType = ENUM_TYPE
VRApplication_Other = ENUM_VALUE_TYPE(0)
VRApplication_Scene = ENUM_VALUE_TYPE(1)
VRApplication_Overlay = ENUM_VALUE_TYPE(2)
VRApplication_Background = ENUM_VALUE_TYPE(3)
VRApplication_Utility = ENUM_VALUE_TYPE(4)
VRApplication_VRMonitor = ENUM_VALUE_TYPE(5)
VRApplication_SteamWatchdog = ENUM_VALUE_TYPE(6)
VRApplication_Bootstrapper = ENUM_VALUE_TYPE(7)
VRApplication_WebHelper = ENUM_VALUE_TYPE(8)
VRApplication_Max = ENUM_VALUE_TYPE(9)

EVRFirmwareError = ENUM_TYPE
VRFirmwareError_None = ENUM_VALUE_TYPE(0)
VRFirmwareError_Success = ENUM_VALUE_TYPE(1)
VRFirmwareError_Fail = ENUM_VALUE_TYPE(2)

EVRNotificationError = ENUM_TYPE
VRNotificationError_OK = ENUM_VALUE_TYPE(0)
VRNotificationError_InvalidNotificationId = ENUM_VALUE_TYPE(100)
VRNotificationError_NotificationQueueFull = ENUM_VALUE_TYPE(101)
VRNotificationError_InvalidOverlayHandle = ENUM_VALUE_TYPE(102)
VRNotificationError_SystemWithUserValueAlreadyExists = ENUM_VALUE_TYPE(103)

EVRSkeletalMotionRange = ENUM_TYPE
VRSkeletalMotionRange_WithController = ENUM_VALUE_TYPE(0)
VRSkeletalMotionRange_WithoutController = ENUM_VALUE_TYPE(1)

EVRSkeletalTrackingLevel = ENUM_TYPE
VRSkeletalTracking_Estimated = ENUM_VALUE_TYPE(0)
VRSkeletalTracking_Partial = ENUM_VALUE_TYPE(1)
VRSkeletalTracking_Full = ENUM_VALUE_TYPE(2)
VRSkeletalTrackingLevel_Count = ENUM_VALUE_TYPE(3)
VRSkeletalTrackingLevel_Max = ENUM_VALUE_TYPE(2)

EVRInitError = ENUM_TYPE
VRInitError_None = ENUM_VALUE_TYPE(0)
VRInitError_Unknown = ENUM_VALUE_TYPE(1)
VRInitError_Init_InstallationNotFound = ENUM_VALUE_TYPE(100)
VRInitError_Init_InstallationCorrupt = ENUM_VALUE_TYPE(101)
VRInitError_Init_VRClientDLLNotFound = ENUM_VALUE_TYPE(102)
VRInitError_Init_FileNotFound = ENUM_VALUE_TYPE(103)
VRInitError_Init_FactoryNotFound = ENUM_VALUE_TYPE(104)
VRInitError_Init_InterfaceNotFound = ENUM_VALUE_TYPE(105)
VRInitError_Init_InvalidInterface = ENUM_VALUE_TYPE(106)
VRInitError_Init_UserConfigDirectoryInvalid = ENUM_VALUE_TYPE(107)
VRInitError_Init_HmdNotFound = ENUM_VALUE_TYPE(108)
VRInitError_Init_NotInitialized = ENUM_VALUE_TYPE(109)
VRInitError_Init_PathRegistryNotFound = ENUM_VALUE_TYPE(110)
VRInitError_Init_NoConfigPath = ENUM_VALUE_TYPE(111)
VRInitError_Init_NoLogPath = ENUM_VALUE_TYPE(112)
VRInitError_Init_PathRegistryNotWritable = ENUM_VALUE_TYPE(113)
VRInitError_Init_AppInfoInitFailed = ENUM_VALUE_TYPE(114)
VRInitError_Init_Retry = ENUM_VALUE_TYPE(115)
VRInitError_Init_InitCanceledByUser = ENUM_VALUE_TYPE(116)
VRInitError_Init_AnotherAppLaunching = ENUM_VALUE_TYPE(117)
VRInitError_Init_SettingsInitFailed = ENUM_VALUE_TYPE(118)
VRInitError_Init_ShuttingDown = ENUM_VALUE_TYPE(119)
VRInitError_Init_TooManyObjects = ENUM_VALUE_TYPE(120)
VRInitError_Init_NoServerForBackgroundApp = ENUM_VALUE_TYPE(121)
VRInitError_Init_NotSupportedWithCompositor = ENUM_VALUE_TYPE(122)
VRInitError_Init_NotAvailableToUtilityApps = ENUM_VALUE_TYPE(123)
VRInitError_Init_Internal = ENUM_VALUE_TYPE(124)
VRInitError_Init_HmdDriverIdIsNone = ENUM_VALUE_TYPE(125)
VRInitError_Init_HmdNotFoundPresenceFailed = ENUM_VALUE_TYPE(126)
VRInitError_Init_VRMonitorNotFound = ENUM_VALUE_TYPE(127)
VRInitError_Init_VRMonitorStartupFailed = ENUM_VALUE_TYPE(128)
VRInitError_Init_LowPowerWatchdogNotSupported = ENUM_VALUE_TYPE(129)
VRInitError_Init_InvalidApplicationType = ENUM_VALUE_TYPE(130)
VRInitError_Init_NotAvailableToWatchdogApps = ENUM_VALUE_TYPE(131)
VRInitError_Init_WatchdogDisabledInSettings = ENUM_VALUE_TYPE(132)
VRInitError_Init_VRDashboardNotFound = ENUM_VALUE_TYPE(133)
VRInitError_Init_VRDashboardStartupFailed = ENUM_VALUE_TYPE(134)
VRInitError_Init_VRHomeNotFound = ENUM_VALUE_TYPE(135)
VRInitError_Init_VRHomeStartupFailed = ENUM_VALUE_TYPE(136)
VRInitError_Init_RebootingBusy = ENUM_VALUE_TYPE(137)
VRInitError_Init_FirmwareUpdateBusy = ENUM_VALUE_TYPE(138)
VRInitError_Init_FirmwareRecoveryBusy = ENUM_VALUE_TYPE(139)
VRInitError_Init_USBServiceBusy = ENUM_VALUE_TYPE(140)
VRInitError_Init_VRWebHelperStartupFailed = ENUM_VALUE_TYPE(141)
VRInitError_Init_TrackerManagerInitFailed = ENUM_VALUE_TYPE(142)
VRInitError_Init_AlreadyRunning = ENUM_VALUE_TYPE(143)
VRInitError_Init_FailedForVrMonitor = ENUM_VALUE_TYPE(144)
VRInitError_Driver_Failed = ENUM_VALUE_TYPE(200)
VRInitError_Driver_Unknown = ENUM_VALUE_TYPE(201)
VRInitError_Driver_HmdUnknown = ENUM_VALUE_TYPE(202)
VRInitError_Driver_NotLoaded = ENUM_VALUE_TYPE(203)
VRInitError_Driver_RuntimeOutOfDate = ENUM_VALUE_TYPE(204)
VRInitError_Driver_HmdInUse = ENUM_VALUE_TYPE(205)
VRInitError_Driver_NotCalibrated = ENUM_VALUE_TYPE(206)
VRInitError_Driver_CalibrationInvalid = ENUM_VALUE_TYPE(207)
VRInitError_Driver_HmdDisplayNotFound = ENUM_VALUE_TYPE(208)
VRInitError_Driver_TrackedDeviceInterfaceUnknown = ENUM_VALUE_TYPE(209)
VRInitError_Driver_HmdDriverIdOutOfBounds = ENUM_VALUE_TYPE(211)
VRInitError_Driver_HmdDisplayMirrored = ENUM_VALUE_TYPE(212)
VRInitError_Driver_HmdDisplayNotFoundLaptop = ENUM_VALUE_TYPE(213)
VRInitError_IPC_ServerInitFailed = ENUM_VALUE_TYPE(300)
VRInitError_IPC_ConnectFailed = ENUM_VALUE_TYPE(301)
VRInitError_IPC_SharedStateInitFailed = ENUM_VALUE_TYPE(302)
VRInitError_IPC_CompositorInitFailed = ENUM_VALUE_TYPE(303)
VRInitError_IPC_MutexInitFailed = ENUM_VALUE_TYPE(304)
VRInitError_IPC_Failed = ENUM_VALUE_TYPE(305)
VRInitError_IPC_CompositorConnectFailed = ENUM_VALUE_TYPE(306)
VRInitError_IPC_CompositorInvalidConnectResponse = ENUM_VALUE_TYPE(307)
VRInitError_IPC_ConnectFailedAfterMultipleAttempts = ENUM_VALUE_TYPE(308)
VRInitError_Compositor_Failed = ENUM_VALUE_TYPE(400)
VRInitError_Compositor_D3D11HardwareRequired = ENUM_VALUE_TYPE(401)
VRInitError_Compositor_FirmwareRequiresUpdate = ENUM_VALUE_TYPE(402)
VRInitError_Compositor_OverlayInitFailed = ENUM_VALUE_TYPE(403)
VRInitError_Compositor_ScreenshotsInitFailed = ENUM_VALUE_TYPE(404)
VRInitError_Compositor_UnableToCreateDevice = ENUM_VALUE_TYPE(405)
VRInitError_Compositor_SharedStateIsNull = ENUM_VALUE_TYPE(406)
VRInitError_Compositor_NotificationManagerIsNull = ENUM_VALUE_TYPE(407)
VRInitError_Compositor_ResourceManagerClientIsNull = ENUM_VALUE_TYPE(408)
VRInitError_Compositor_MessageOverlaySharedStateInitFailure = ENUM_VALUE_TYPE(409)
VRInitError_Compositor_PropertiesInterfaceIsNull = ENUM_VALUE_TYPE(410)
VRInitError_Compositor_CreateFullscreenWindowFailed = ENUM_VALUE_TYPE(411)
VRInitError_Compositor_SettingsInterfaceIsNull = ENUM_VALUE_TYPE(412)
VRInitError_Compositor_FailedToShowWindow = ENUM_VALUE_TYPE(413)
VRInitError_Compositor_DistortInterfaceIsNull = ENUM_VALUE_TYPE(414)
VRInitError_Compositor_DisplayFrequencyFailure = ENUM_VALUE_TYPE(415)
VRInitError_Compositor_RendererInitializationFailed = ENUM_VALUE_TYPE(416)
VRInitError_Compositor_DXGIFactoryInterfaceIsNull = ENUM_VALUE_TYPE(417)
VRInitError_Compositor_DXGIFactoryCreateFailed = ENUM_VALUE_TYPE(418)
VRInitError_Compositor_DXGIFactoryQueryFailed = ENUM_VALUE_TYPE(419)
VRInitError_Compositor_InvalidAdapterDesktop = ENUM_VALUE_TYPE(420)
VRInitError_Compositor_InvalidHmdAttachment = ENUM_VALUE_TYPE(421)
VRInitError_Compositor_InvalidOutputDesktop = ENUM_VALUE_TYPE(422)
VRInitError_Compositor_InvalidDeviceProvided = ENUM_VALUE_TYPE(423)
VRInitError_Compositor_D3D11RendererInitializationFailed = ENUM_VALUE_TYPE(424)
VRInitError_Compositor_FailedToFindDisplayMode = ENUM_VALUE_TYPE(425)
VRInitError_Compositor_FailedToCreateSwapChain = ENUM_VALUE_TYPE(426)
VRInitError_Compositor_FailedToGetBackBuffer = ENUM_VALUE_TYPE(427)
VRInitError_Compositor_FailedToCreateRenderTarget = ENUM_VALUE_TYPE(428)
VRInitError_Compositor_FailedToCreateDXGI2SwapChain = ENUM_VALUE_TYPE(429)
VRInitError_Compositor_FailedtoGetDXGI2BackBuffer = ENUM_VALUE_TYPE(430)
VRInitError_Compositor_FailedToCreateDXGI2RenderTarget = ENUM_VALUE_TYPE(431)
VRInitError_Compositor_FailedToGetDXGIDeviceInterface = ENUM_VALUE_TYPE(432)
VRInitError_Compositor_SelectDisplayMode = ENUM_VALUE_TYPE(433)
VRInitError_Compositor_FailedToCreateNvAPIRenderTargets = ENUM_VALUE_TYPE(434)
VRInitError_Compositor_NvAPISetDisplayMode = ENUM_VALUE_TYPE(435)
VRInitError_Compositor_FailedToCreateDirectModeDisplay = ENUM_VALUE_TYPE(436)
VRInitError_Compositor_InvalidHmdPropertyContainer = ENUM_VALUE_TYPE(437)
VRInitError_Compositor_UpdateDisplayFrequency = ENUM_VALUE_TYPE(438)
VRInitError_Compositor_CreateRasterizerState = ENUM_VALUE_TYPE(439)
VRInitError_Compositor_CreateWireframeRasterizerState = ENUM_VALUE_TYPE(440)
VRInitError_Compositor_CreateSamplerState = ENUM_VALUE_TYPE(441)
VRInitError_Compositor_CreateClampToBorderSamplerState = ENUM_VALUE_TYPE(442)
VRInitError_Compositor_CreateAnisoSamplerState = ENUM_VALUE_TYPE(443)
VRInitError_Compositor_CreateOverlaySamplerState = ENUM_VALUE_TYPE(444)
VRInitError_Compositor_CreatePanoramaSamplerState = ENUM_VALUE_TYPE(445)
VRInitError_Compositor_CreateFontSamplerState = ENUM_VALUE_TYPE(446)
VRInitError_Compositor_CreateNoBlendState = ENUM_VALUE_TYPE(447)
VRInitError_Compositor_CreateBlendState = ENUM_VALUE_TYPE(448)
VRInitError_Compositor_CreateAlphaBlendState = ENUM_VALUE_TYPE(449)
VRInitError_Compositor_CreateBlendStateMaskR = ENUM_VALUE_TYPE(450)
VRInitError_Compositor_CreateBlendStateMaskG = ENUM_VALUE_TYPE(451)
VRInitError_Compositor_CreateBlendStateMaskB = ENUM_VALUE_TYPE(452)
VRInitError_Compositor_CreateDepthStencilState = ENUM_VALUE_TYPE(453)
VRInitError_Compositor_CreateDepthStencilStateNoWrite = ENUM_VALUE_TYPE(454)
VRInitError_Compositor_CreateDepthStencilStateNoDepth = ENUM_VALUE_TYPE(455)
VRInitError_Compositor_CreateFlushTexture = ENUM_VALUE_TYPE(456)
VRInitError_Compositor_CreateDistortionSurfaces = ENUM_VALUE_TYPE(457)
VRInitError_Compositor_CreateConstantBuffer = ENUM_VALUE_TYPE(458)
VRInitError_Compositor_CreateHmdPoseConstantBuffer = ENUM_VALUE_TYPE(459)
VRInitError_Compositor_CreateHmdPoseStagingConstantBuffer = ENUM_VALUE_TYPE(460)
VRInitError_Compositor_CreateSharedFrameInfoConstantBuffer = ENUM_VALUE_TYPE(461)
VRInitError_Compositor_CreateOverlayConstantBuffer = ENUM_VALUE_TYPE(462)
VRInitError_Compositor_CreateSceneTextureIndexConstantBuffer = ENUM_VALUE_TYPE(463)
VRInitError_Compositor_CreateReadableSceneTextureIndexConstantBuffer = ENUM_VALUE_TYPE(464)
VRInitError_Compositor_CreateLayerGraphicsTextureIndexConstantBuffer = ENUM_VALUE_TYPE(465)
VRInitError_Compositor_CreateLayerComputeTextureIndexConstantBuffer = ENUM_VALUE_TYPE(466)
VRInitError_Compositor_CreateLayerComputeSceneTextureIndexConstantBuffer = ENUM_VALUE_TYPE(467)
VRInitError_Compositor_CreateComputeHmdPoseConstantBuffer = ENUM_VALUE_TYPE(468)
VRInitError_Compositor_CreateGeomConstantBuffer = ENUM_VALUE_TYPE(469)
VRInitError_Compositor_CreatePanelMaskConstantBuffer = ENUM_VALUE_TYPE(470)
VRInitError_Compositor_CreatePixelSimUBO = ENUM_VALUE_TYPE(471)
VRInitError_Compositor_CreateMSAARenderTextures = ENUM_VALUE_TYPE(472)
VRInitError_Compositor_CreateResolveRenderTextures = ENUM_VALUE_TYPE(473)
VRInitError_Compositor_CreateComputeResolveRenderTextures = ENUM_VALUE_TYPE(474)
VRInitError_Compositor_CreateDriverDirectModeResolveTextures = ENUM_VALUE_TYPE(475)
VRInitError_Compositor_OpenDriverDirectModeResolveTextures = ENUM_VALUE_TYPE(476)
VRInitError_Compositor_CreateFallbackSyncTexture = ENUM_VALUE_TYPE(477)
VRInitError_Compositor_ShareFallbackSyncTexture = ENUM_VALUE_TYPE(478)
VRInitError_Compositor_CreateOverlayIndexBuffer = ENUM_VALUE_TYPE(479)
VRInitError_Compositor_CreateOverlayVertextBuffer = ENUM_VALUE_TYPE(480)
VRInitError_Compositor_CreateTextVertexBuffer = ENUM_VALUE_TYPE(481)
VRInitError_Compositor_CreateTextIndexBuffer = ENUM_VALUE_TYPE(482)
VRInitError_Compositor_CreateMirrorTextures = ENUM_VALUE_TYPE(483)
VRInitError_Compositor_CreateLastFrameRenderTexture = ENUM_VALUE_TYPE(484)
VRInitError_VendorSpecific_UnableToConnectToOculusRuntime = ENUM_VALUE_TYPE(1000)
VRInitError_VendorSpecific_WindowsNotInDevMode = ENUM_VALUE_TYPE(1001)
VRInitError_VendorSpecific_HmdFound_CantOpenDevice = ENUM_VALUE_TYPE(1101)
VRInitError_VendorSpecific_HmdFound_UnableToRequestConfigStart = ENUM_VALUE_TYPE(1102)
VRInitError_VendorSpecific_HmdFound_NoStoredConfig = ENUM_VALUE_TYPE(1103)
VRInitError_VendorSpecific_HmdFound_ConfigTooBig = ENUM_VALUE_TYPE(1104)
VRInitError_VendorSpecific_HmdFound_ConfigTooSmall = ENUM_VALUE_TYPE(1105)
VRInitError_VendorSpecific_HmdFound_UnableToInitZLib = ENUM_VALUE_TYPE(1106)
VRInitError_VendorSpecific_HmdFound_CantReadFirmwareVersion = ENUM_VALUE_TYPE(1107)
VRInitError_VendorSpecific_HmdFound_UnableToSendUserDataStart = ENUM_VALUE_TYPE(1108)
VRInitError_VendorSpecific_HmdFound_UnableToGetUserDataStart = ENUM_VALUE_TYPE(1109)
VRInitError_VendorSpecific_HmdFound_UnableToGetUserDataNext = ENUM_VALUE_TYPE(1110)
VRInitError_VendorSpecific_HmdFound_UserDataAddressRange = ENUM_VALUE_TYPE(1111)
VRInitError_VendorSpecific_HmdFound_UserDataError = ENUM_VALUE_TYPE(1112)
VRInitError_VendorSpecific_HmdFound_ConfigFailedSanityCheck = ENUM_VALUE_TYPE(1113)
VRInitError_Steam_SteamInstallationNotFound = ENUM_VALUE_TYPE(2000)
VRInitError_LastError = ENUM_VALUE_TYPE(2001)

EVRScreenshotType = ENUM_TYPE
VRScreenshotType_None = ENUM_VALUE_TYPE(0)
VRScreenshotType_Mono = ENUM_VALUE_TYPE(1)
VRScreenshotType_Stereo = ENUM_VALUE_TYPE(2)
VRScreenshotType_Cubemap = ENUM_VALUE_TYPE(3)
VRScreenshotType_MonoPanorama = ENUM_VALUE_TYPE(4)
VRScreenshotType_StereoPanorama = ENUM_VALUE_TYPE(5)

EVRScreenshotPropertyFilenames = ENUM_TYPE
VRScreenshotPropertyFilenames_Preview = ENUM_VALUE_TYPE(0)
VRScreenshotPropertyFilenames_VR = ENUM_VALUE_TYPE(1)

EVRTrackedCameraError = ENUM_TYPE
VRTrackedCameraError_None = ENUM_VALUE_TYPE(0)
VRTrackedCameraError_OperationFailed = ENUM_VALUE_TYPE(100)
VRTrackedCameraError_InvalidHandle = ENUM_VALUE_TYPE(101)
VRTrackedCameraError_InvalidFrameHeaderVersion = ENUM_VALUE_TYPE(102)
VRTrackedCameraError_OutOfHandles = ENUM_VALUE_TYPE(103)
VRTrackedCameraError_IPCFailure = ENUM_VALUE_TYPE(104)
VRTrackedCameraError_NotSupportedForThisDevice = ENUM_VALUE_TYPE(105)
VRTrackedCameraError_SharedMemoryFailure = ENUM_VALUE_TYPE(106)
VRTrackedCameraError_FrameBufferingFailure = ENUM_VALUE_TYPE(107)
VRTrackedCameraError_StreamSetupFailure = ENUM_VALUE_TYPE(108)
VRTrackedCameraError_InvalidGLTextureId = ENUM_VALUE_TYPE(109)
VRTrackedCameraError_InvalidSharedTextureHandle = ENUM_VALUE_TYPE(110)
VRTrackedCameraError_FailedToGetGLTextureId = ENUM_VALUE_TYPE(111)
VRTrackedCameraError_SharedTextureFailure = ENUM_VALUE_TYPE(112)
VRTrackedCameraError_NoFrameAvailable = ENUM_VALUE_TYPE(113)
VRTrackedCameraError_InvalidArgument = ENUM_VALUE_TYPE(114)
VRTrackedCameraError_InvalidFrameBufferSize = ENUM_VALUE_TYPE(115)

EVRTrackedCameraFrameLayout = ENUM_TYPE
EVRTrackedCameraFrameLayout_Mono = ENUM_VALUE_TYPE(1)
EVRTrackedCameraFrameLayout_Stereo = ENUM_VALUE_TYPE(2)
EVRTrackedCameraFrameLayout_VerticalLayout = ENUM_VALUE_TYPE(16)
EVRTrackedCameraFrameLayout_HorizontalLayout = ENUM_VALUE_TYPE(32)

EVRTrackedCameraFrameType = ENUM_TYPE
VRTrackedCameraFrameType_Distorted = ENUM_VALUE_TYPE(0)
VRTrackedCameraFrameType_Undistorted = ENUM_VALUE_TYPE(1)
VRTrackedCameraFrameType_MaximumUndistorted = ENUM_VALUE_TYPE(2)
MAX_CAMERA_FRAME_TYPES = ENUM_VALUE_TYPE(3)

EVRDistortionFunctionType = ENUM_TYPE
VRDistortionFunctionType_None = ENUM_VALUE_TYPE(0)
VRDistortionFunctionType_FTheta = ENUM_VALUE_TYPE(1)
VRDistortionFunctionType_Extended_FTheta = ENUM_VALUE_TYPE(2)
MAX_DISTORTION_FUNCTION_TYPES = ENUM_VALUE_TYPE(3)

EVSync = ENUM_TYPE
VSync_None = ENUM_VALUE_TYPE(0)
VSync_WaitRender = ENUM_VALUE_TYPE(1)
VSync_NoWaitRender = ENUM_VALUE_TYPE(2)

EVRMuraCorrectionMode = ENUM_TYPE
EVRMuraCorrectionMode_Default = ENUM_VALUE_TYPE(0)
EVRMuraCorrectionMode_NoCorrection = ENUM_VALUE_TYPE(1)

Imu_OffScaleFlags = ENUM_TYPE
OffScale_AccelX = ENUM_VALUE_TYPE(1)
OffScale_AccelY = ENUM_VALUE_TYPE(2)
OffScale_AccelZ = ENUM_VALUE_TYPE(4)
OffScale_GyroX = ENUM_VALUE_TYPE(8)
OffScale_GyroY = ENUM_VALUE_TYPE(16)
OffScale_GyroZ = ENUM_VALUE_TYPE(32)

EVRApplicationError = ENUM_TYPE
VRApplicationError_None = ENUM_VALUE_TYPE(0)
VRApplicationError_AppKeyAlreadyExists = ENUM_VALUE_TYPE(100)
VRApplicationError_NoManifest = ENUM_VALUE_TYPE(101)
VRApplicationError_NoApplication = ENUM_VALUE_TYPE(102)
VRApplicationError_InvalidIndex = ENUM_VALUE_TYPE(103)
VRApplicationError_UnknownApplication = ENUM_VALUE_TYPE(104)
VRApplicationError_IPCFailed = ENUM_VALUE_TYPE(105)
VRApplicationError_ApplicationAlreadyRunning = ENUM_VALUE_TYPE(106)
VRApplicationError_InvalidManifest = ENUM_VALUE_TYPE(107)
VRApplicationError_InvalidApplication = ENUM_VALUE_TYPE(108)
VRApplicationError_LaunchFailed = ENUM_VALUE_TYPE(109)
VRApplicationError_ApplicationAlreadyStarting = ENUM_VALUE_TYPE(110)
VRApplicationError_LaunchInProgress = ENUM_VALUE_TYPE(111)
VRApplicationError_OldApplicationQuitting = ENUM_VALUE_TYPE(112)
VRApplicationError_TransitionAborted = ENUM_VALUE_TYPE(113)
VRApplicationError_IsTemplate = ENUM_VALUE_TYPE(114)
VRApplicationError_SteamVRIsExiting = ENUM_VALUE_TYPE(115)
VRApplicationError_BufferTooSmall = ENUM_VALUE_TYPE(200)
VRApplicationError_PropertyNotSet = ENUM_VALUE_TYPE(201)
VRApplicationError_UnknownProperty = ENUM_VALUE_TYPE(202)
VRApplicationError_InvalidParameter = ENUM_VALUE_TYPE(203)

EVRApplicationProperty = ENUM_TYPE
VRApplicationProperty_Name_String = ENUM_VALUE_TYPE(0)
VRApplicationProperty_LaunchType_String = ENUM_VALUE_TYPE(11)
VRApplicationProperty_WorkingDirectory_String = ENUM_VALUE_TYPE(12)
VRApplicationProperty_BinaryPath_String = ENUM_VALUE_TYPE(13)
VRApplicationProperty_Arguments_String = ENUM_VALUE_TYPE(14)
VRApplicationProperty_URL_String = ENUM_VALUE_TYPE(15)
VRApplicationProperty_Description_String = ENUM_VALUE_TYPE(50)
VRApplicationProperty_NewsURL_String = ENUM_VALUE_TYPE(51)
VRApplicationProperty_ImagePath_String = ENUM_VALUE_TYPE(52)
VRApplicationProperty_Source_String = ENUM_VALUE_TYPE(53)
VRApplicationProperty_ActionManifestURL_String = ENUM_VALUE_TYPE(54)
VRApplicationProperty_IsDashboardOverlay_Bool = ENUM_VALUE_TYPE(60)
VRApplicationProperty_IsTemplate_Bool = ENUM_VALUE_TYPE(61)
VRApplicationProperty_IsInstanced_Bool = ENUM_VALUE_TYPE(62)
VRApplicationProperty_IsInternal_Bool = ENUM_VALUE_TYPE(63)
VRApplicationProperty_WantsCompositorPauseInStandby_Bool = ENUM_VALUE_TYPE(64)
VRApplicationProperty_LastLaunchTime_Uint64 = ENUM_VALUE_TYPE(70)

EVRApplicationTransitionState = ENUM_TYPE
VRApplicationTransition_None = ENUM_VALUE_TYPE(0)
VRApplicationTransition_OldAppQuitSent = ENUM_VALUE_TYPE(10)
VRApplicationTransition_WaitingForExternalLaunch = ENUM_VALUE_TYPE(11)
VRApplicationTransition_NewAppLaunched = ENUM_VALUE_TYPE(20)

EVRSettingsError = ENUM_TYPE
VRSettingsError_None = ENUM_VALUE_TYPE(0)
VRSettingsError_IPCFailed = ENUM_VALUE_TYPE(1)
VRSettingsError_WriteFailed = ENUM_VALUE_TYPE(2)
VRSettingsError_ReadFailed = ENUM_VALUE_TYPE(3)
VRSettingsError_JsonParseFailed = ENUM_VALUE_TYPE(4)
VRSettingsError_UnsetSettingHasNoDefault = ENUM_VALUE_TYPE(5)

ChaperoneCalibrationState = ENUM_TYPE
ChaperoneCalibrationState_OK = ENUM_VALUE_TYPE(1)
ChaperoneCalibrationState_Warning = ENUM_VALUE_TYPE(100)
ChaperoneCalibrationState_Warning_BaseStationMayHaveMoved = ENUM_VALUE_TYPE(101)
ChaperoneCalibrationState_Warning_BaseStationRemoved = ENUM_VALUE_TYPE(102)
ChaperoneCalibrationState_Warning_SeatedBoundsInvalid = ENUM_VALUE_TYPE(103)
ChaperoneCalibrationState_Error = ENUM_VALUE_TYPE(200)
ChaperoneCalibrationState_Error_BaseStationUninitialized = ENUM_VALUE_TYPE(201)
ChaperoneCalibrationState_Error_BaseStationConflict = ENUM_VALUE_TYPE(202)
ChaperoneCalibrationState_Error_PlayAreaInvalid = ENUM_VALUE_TYPE(203)
ChaperoneCalibrationState_Error_CollisionBoundsInvalid = ENUM_VALUE_TYPE(204)

EChaperoneConfigFile = ENUM_TYPE
EChaperoneConfigFile_Live = ENUM_VALUE_TYPE(1)
EChaperoneConfigFile_Temp = ENUM_VALUE_TYPE(2)

EChaperoneImportFlags = ENUM_TYPE
EChaperoneImport_BoundsOnly = ENUM_VALUE_TYPE(1)

EVRCompositorError = ENUM_TYPE
VRCompositorError_None = ENUM_VALUE_TYPE(0)
VRCompositorError_RequestFailed = ENUM_VALUE_TYPE(1)
VRCompositorError_IncompatibleVersion = ENUM_VALUE_TYPE(100)
VRCompositorError_DoNotHaveFocus = ENUM_VALUE_TYPE(101)
VRCompositorError_InvalidTexture = ENUM_VALUE_TYPE(102)
VRCompositorError_IsNotSceneApplication = ENUM_VALUE_TYPE(103)
VRCompositorError_TextureIsOnWrongDevice = ENUM_VALUE_TYPE(104)
VRCompositorError_TextureUsesUnsupportedFormat = ENUM_VALUE_TYPE(105)
VRCompositorError_SharedTexturesNotSupported = ENUM_VALUE_TYPE(106)
VRCompositorError_IndexOutOfRange = ENUM_VALUE_TYPE(107)
VRCompositorError_AlreadySubmitted = ENUM_VALUE_TYPE(108)
VRCompositorError_InvalidBounds = ENUM_VALUE_TYPE(109)

EVRCompositorTimingMode = ENUM_TYPE
VRCompositorTimingMode_Implicit = ENUM_VALUE_TYPE(0)
VRCompositorTimingMode_Explicit_RuntimePerformsPostPresentHandoff = ENUM_VALUE_TYPE(1)
VRCompositorTimingMode_Explicit_ApplicationPerformsPostPresentHandoff = ENUM_VALUE_TYPE(2)

EVRNotificationType = ENUM_TYPE
EVRNotificationType_Transient = ENUM_VALUE_TYPE(0)
EVRNotificationType_Persistent = ENUM_VALUE_TYPE(1)
EVRNotificationType_Transient_SystemWithUserValue = ENUM_VALUE_TYPE(2)

EVRNotificationStyle = ENUM_TYPE
EVRNotificationStyle_None = ENUM_VALUE_TYPE(0)
EVRNotificationStyle_Application = ENUM_VALUE_TYPE(100)
EVRNotificationStyle_Contact_Disabled = ENUM_VALUE_TYPE(200)
EVRNotificationStyle_Contact_Enabled = ENUM_VALUE_TYPE(201)
EVRNotificationStyle_Contact_Active = ENUM_VALUE_TYPE(202)

VROverlayInputMethod = ENUM_TYPE
VROverlayInputMethod_None = ENUM_VALUE_TYPE(0)
VROverlayInputMethod_Mouse = ENUM_VALUE_TYPE(1)
VROverlayInputMethod_DualAnalog = ENUM_VALUE_TYPE(2)

VROverlayTransformType = ENUM_TYPE
VROverlayTransform_Absolute = ENUM_VALUE_TYPE(0)
VROverlayTransform_TrackedDeviceRelative = ENUM_VALUE_TYPE(1)
VROverlayTransform_SystemOverlay = ENUM_VALUE_TYPE(2)
VROverlayTransform_TrackedComponent = ENUM_VALUE_TYPE(3)

VROverlayFlags = ENUM_TYPE
VROverlayFlags_None = ENUM_VALUE_TYPE(0)
VROverlayFlags_Curved = ENUM_VALUE_TYPE(1)
VROverlayFlags_RGSS4X = ENUM_VALUE_TYPE(2)
VROverlayFlags_NoDashboardTab = ENUM_VALUE_TYPE(3)
VROverlayFlags_AcceptsGamepadEvents = ENUM_VALUE_TYPE(4)
VROverlayFlags_ShowGamepadFocus = ENUM_VALUE_TYPE(5)
VROverlayFlags_SendVRDiscreteScrollEvents = ENUM_VALUE_TYPE(6)
VROverlayFlags_SendVRTouchpadEvents = ENUM_VALUE_TYPE(7)
VROverlayFlags_ShowTouchPadScrollWheel = ENUM_VALUE_TYPE(8)
VROverlayFlags_TransferOwnershipToInternalProcess = ENUM_VALUE_TYPE(9)
VROverlayFlags_SideBySide_Parallel = ENUM_VALUE_TYPE(10)
VROverlayFlags_SideBySide_Crossed = ENUM_VALUE_TYPE(11)
VROverlayFlags_Panorama = ENUM_VALUE_TYPE(12)
VROverlayFlags_StereoPanorama = ENUM_VALUE_TYPE(13)
VROverlayFlags_SortWithNonSceneOverlays = ENUM_VALUE_TYPE(14)
VROverlayFlags_VisibleInDashboard = ENUM_VALUE_TYPE(15)
VROverlayFlags_MakeOverlaysInteractiveIfVisible = ENUM_VALUE_TYPE(16)
VROverlayFlags_SendVRSmoothScrollEvents = ENUM_VALUE_TYPE(17)

VRMessageOverlayResponse = ENUM_TYPE
VRMessageOverlayResponse_ButtonPress_0 = ENUM_VALUE_TYPE(0)
VRMessageOverlayResponse_ButtonPress_1 = ENUM_VALUE_TYPE(1)
VRMessageOverlayResponse_ButtonPress_2 = ENUM_VALUE_TYPE(2)
VRMessageOverlayResponse_ButtonPress_3 = ENUM_VALUE_TYPE(3)
VRMessageOverlayResponse_CouldntFindSystemOverlay = ENUM_VALUE_TYPE(4)
VRMessageOverlayResponse_CouldntFindOrCreateClientOverlay = ENUM_VALUE_TYPE(5)
VRMessageOverlayResponse_ApplicationQuit = ENUM_VALUE_TYPE(6)

EGamepadTextInputMode = ENUM_TYPE
k_EGamepadTextInputModeNormal = ENUM_VALUE_TYPE(0)
k_EGamepadTextInputModePassword = ENUM_VALUE_TYPE(1)
k_EGamepadTextInputModeSubmit = ENUM_VALUE_TYPE(2)

EGamepadTextInputLineMode = ENUM_TYPE
k_EGamepadTextInputLineModeSingleLine = ENUM_VALUE_TYPE(0)
k_EGamepadTextInputLineModeMultipleLines = ENUM_VALUE_TYPE(1)

EOverlayDirection = ENUM_TYPE
OverlayDirection_Up = ENUM_VALUE_TYPE(0)
OverlayDirection_Down = ENUM_VALUE_TYPE(1)
OverlayDirection_Left = ENUM_VALUE_TYPE(2)
OverlayDirection_Right = ENUM_VALUE_TYPE(3)
OverlayDirection_Count = ENUM_VALUE_TYPE(4)

EVROverlayIntersectionMaskPrimitiveType = ENUM_TYPE
OverlayIntersectionPrimitiveType_Rectangle = ENUM_VALUE_TYPE(0)
OverlayIntersectionPrimitiveType_Circle = ENUM_VALUE_TYPE(1)

EVRRenderModelError = ENUM_TYPE
VRRenderModelError_None = ENUM_VALUE_TYPE(0)
VRRenderModelError_Loading = ENUM_VALUE_TYPE(100)
VRRenderModelError_NotSupported = ENUM_VALUE_TYPE(200)
VRRenderModelError_InvalidArg = ENUM_VALUE_TYPE(300)
VRRenderModelError_InvalidModel = ENUM_VALUE_TYPE(301)
VRRenderModelError_NoShapes = ENUM_VALUE_TYPE(302)
VRRenderModelError_MultipleShapes = ENUM_VALUE_TYPE(303)
VRRenderModelError_TooManyVertices = ENUM_VALUE_TYPE(304)
VRRenderModelError_MultipleTextures = ENUM_VALUE_TYPE(305)
VRRenderModelError_BufferTooSmall = ENUM_VALUE_TYPE(306)
VRRenderModelError_NotEnoughNormals = ENUM_VALUE_TYPE(307)
VRRenderModelError_NotEnoughTexCoords = ENUM_VALUE_TYPE(308)
VRRenderModelError_InvalidTexture = ENUM_VALUE_TYPE(400)

EVRComponentProperty = ENUM_TYPE
VRComponentProperty_IsStatic = ENUM_VALUE_TYPE(1)
VRComponentProperty_IsVisible = ENUM_VALUE_TYPE(2)
VRComponentProperty_IsTouched = ENUM_VALUE_TYPE(4)
VRComponentProperty_IsPressed = ENUM_VALUE_TYPE(8)
VRComponentProperty_IsScrolled = ENUM_VALUE_TYPE(16)

EVRScreenshotError = ENUM_TYPE
VRScreenshotError_None = ENUM_VALUE_TYPE(0)
VRScreenshotError_RequestFailed = ENUM_VALUE_TYPE(1)
VRScreenshotError_IncompatibleVersion = ENUM_VALUE_TYPE(100)
VRScreenshotError_NotFound = ENUM_VALUE_TYPE(101)
VRScreenshotError_BufferTooSmall = ENUM_VALUE_TYPE(102)
VRScreenshotError_ScreenshotAlreadyInProgress = ENUM_VALUE_TYPE(108)

EVRSkeletalTransformSpace = ENUM_TYPE
VRSkeletalTransformSpace_Model = ENUM_VALUE_TYPE(0)
VRSkeletalTransformSpace_Parent = ENUM_VALUE_TYPE(1)

EVRSkeletalReferencePose = ENUM_TYPE
VRSkeletalReferencePose_BindPose = ENUM_VALUE_TYPE(0)
VRSkeletalReferencePose_OpenHand = ENUM_VALUE_TYPE(1)
VRSkeletalReferencePose_Fist = ENUM_VALUE_TYPE(2)
VRSkeletalReferencePose_GripLimit = ENUM_VALUE_TYPE(3)

EVRFinger = ENUM_TYPE
VRFinger_Thumb = ENUM_VALUE_TYPE(0)
VRFinger_Index = ENUM_VALUE_TYPE(1)
VRFinger_Middle = ENUM_VALUE_TYPE(2)
VRFinger_Ring = ENUM_VALUE_TYPE(3)
VRFinger_Pinky = ENUM_VALUE_TYPE(4)
VRFinger_Count = ENUM_VALUE_TYPE(5)

EVRFingerSplay = ENUM_TYPE
VRFingerSplay_Thumb_Index = ENUM_VALUE_TYPE(0)
VRFingerSplay_Index_Middle = ENUM_VALUE_TYPE(1)
VRFingerSplay_Middle_Ring = ENUM_VALUE_TYPE(2)
VRFingerSplay_Ring_Pinky = ENUM_VALUE_TYPE(3)
VRFingerSplay_Count = ENUM_VALUE_TYPE(4)

EVRSummaryType = ENUM_TYPE
VRSummaryType_FromAnimation = ENUM_VALUE_TYPE(0)
VRSummaryType_FromDevice = ENUM_VALUE_TYPE(1)

EVRInputFilterCancelType = ENUM_TYPE
VRInputFilterCancel_Timers = ENUM_VALUE_TYPE(0)
VRInputFilterCancel_Momentum = ENUM_VALUE_TYPE(1)

EVRInputStringBits = ENUM_TYPE
VRInputString_Hand = ENUM_VALUE_TYPE(1)
VRInputString_ControllerType = ENUM_VALUE_TYPE(2)
VRInputString_InputSource = ENUM_VALUE_TYPE(4)
VRInputString_All = ENUM_VALUE_TYPE(-1)

EIOBufferError = ENUM_TYPE
IOBuffer_Success = ENUM_VALUE_TYPE(0)
IOBuffer_OperationFailed = ENUM_VALUE_TYPE(100)
IOBuffer_InvalidHandle = ENUM_VALUE_TYPE(101)
IOBuffer_InvalidArgument = ENUM_VALUE_TYPE(102)
IOBuffer_PathExists = ENUM_VALUE_TYPE(103)
IOBuffer_PathDoesNotExist = ENUM_VALUE_TYPE(104)
IOBuffer_Permission = ENUM_VALUE_TYPE(105)

EIOBufferMode = ENUM_TYPE
IOBufferMode_Read = ENUM_VALUE_TYPE(1)
IOBufferMode_Write = ENUM_VALUE_TYPE(2)
IOBufferMode_Create = ENUM_VALUE_TYPE(512)


###################
# Expose Typedefs #
###################

# Use c_ubyte instead of c_char, for better compatibility with Python True/False
openvr_bool = c_ubyte

SpatialAnchorHandle_t = c_uint32
glSharedTextureHandle_t = c_void_p
glInt_t = c_int32
glUInt_t = c_uint32
SharedTextureHandle_t = c_uint64
DriverId_t = c_uint32
TrackedDeviceIndex_t = c_uint32
WebConsoleHandle_t = c_uint64
PropertyContainerHandle_t = c_uint64
PropertyTypeTag_t = c_uint32
DriverHandle_t = PropertyContainerHandle_t
VRActionHandle_t = c_uint64
VRActionSetHandle_t = c_uint64
VRInputValueHandle_t = c_uint64
VROverlayHandle_t = c_uint64
BoneIndex_t = c_int32
TrackedCameraHandle_t = c_uint64
ScreenshotHandle_t = c_uint32
VRNotificationId = c_uint32
VRComponentProperties = c_uint32
TextureID_t = c_int32
IOBufferHandle_t = c_uint64
HmdError = EVRInitError
Hmd_Eye = EVREye
ColorSpace = EColorSpace
HmdTrackingResult = ETrackingResult
TrackedDeviceClass = ETrackedDeviceClass
TrackingUniverseOrigin = ETrackingUniverseOrigin
TrackedDeviceProperty = ETrackedDeviceProperty
TrackedPropertyError = ETrackedPropertyError
VRSubmitFlags_t = EVRSubmitFlags
VRState_t = EVRState
CollisionBoundsStyle_t = ECollisionBoundsStyle
VROverlayError = EVROverlayError
VRFirmwareError = EVRFirmwareError
VRCompositorError = EVRCompositorError
VRScreenshotsError = EVRScreenshotError

##################
# Expose classes #
##################


# Methods to include in all openvr vector classes
class _VectorMixin(object):
    def __init__(self, *args):
        self._setArray(self._getArray().__class__(*args))

    def _getArray(self):
        return self.v

    def _setArray(self, array):
        self.v[:] = array[:]

    def __getitem__(self, key):
        return self._getArray()[key]

    def __len__(self):
        return len(self._getArray())

    def __setitem__(self, key, value):
        self._getArray()[key] = value

    def __str__(self):
        return str(list(self))


class _MatrixMixin(_VectorMixin):
    def _getArray(self):
        return self.m

    def _setArray(self, array):
        self.m[:] = array[:]

    def __str__(self):
        return str(list(list(e) for e in self))


class HmdMatrix34_t(_MatrixMixin, Structure):
    """
    right-handed system
    +y is up
    +x is to the right
    -z is forward
    Distance unit is  meters
    """

    _fields_ = [
        ("m", (c_float * 4) * 3),
    ]


class HmdMatrix33_t(_MatrixMixin, Structure):
    _fields_ = [
        ("m", (c_float * 3) * 3),
    ]


class HmdMatrix44_t(_MatrixMixin, Structure):
    _fields_ = [
        ("m", (c_float * 4) * 4),
    ]


class HmdVector3_t(_VectorMixin, Structure):
    _fields_ = [
        ("v", c_float * 3),
    ]


class HmdVector4_t(_VectorMixin, Structure):
    _fields_ = [
        ("v", c_float * 4),
    ]


class HmdVector3d_t(_VectorMixin, Structure):
    _fields_ = [
        ("v", c_double * 3),
    ]


class HmdVector2_t(_VectorMixin, Structure):
    _fields_ = [
        ("v", c_float * 2),
    ]


class HmdQuaternion_t(Structure):
    _fields_ = [
        ("w", c_double),
        ("x", c_double),
        ("y", c_double),
        ("z", c_double),
    ]


class HmdQuaternionf_t(Structure):
    _fields_ = [
        ("w", c_float),
        ("x", c_float),
        ("y", c_float),
        ("z", c_float),
    ]


class HmdColor_t(Structure):
    _fields_ = [
        ("r", c_float),
        ("g", c_float),
        ("b", c_float),
        ("a", c_float),
    ]


class HmdQuad_t(Structure):
    _fields_ = [
        ("vCorners", HmdVector3_t * 4),
    ]


class HmdRect2_t(Structure):
    _fields_ = [
        ("vTopLeft", HmdVector2_t),
        ("vBottomRight", HmdVector2_t),
    ]


class DistortionCoordinates_t(Structure):
    """
    Used to return the post-distortion UVs for each color channel. 
    UVs range from 0 to 1 with 0,0 in the upper left corner of the 
    source render target. The 0,0 to 1,1 range covers a single eye.
    """

    _fields_ = [
        ("rfRed", c_float * 2),
        ("rfGreen", c_float * 2),
        ("rfBlue", c_float * 2),
    ]


class Texture_t(Structure):
    _fields_ = [
        ("handle", c_void_p),
        ("eType", ETextureType),
        ("eColorSpace", EColorSpace),
    ]


class TrackedDevicePose_t(Structure):
    """describes a single pose for a tracked object"""

    _fields_ = [
        ("mDeviceToAbsoluteTracking", HmdMatrix34_t),
        ("vVelocity", HmdVector3_t),
        ("vAngularVelocity", HmdVector3_t),
        ("eTrackingResult", ETrackingResult),
        ("bPoseIsValid", openvr_bool),
        ("bDeviceIsConnected", openvr_bool),
    ]


class VRTextureBounds_t(Structure):
    """
    Allows the application to control what part of the provided texture will be used in the
    frame buffer.
    """

    _fields_ = [
        ("uMin", c_float),
        ("vMin", c_float),
        ("uMax", c_float),
        ("vMax", c_float),
    ]


class VRTextureWithPose_t(Texture_t):
    """Allows specifying pose used to render provided scene texture (if different from value returned by WaitGetPoses)."""

    _fields_ = [
        ("mDeviceToAbsoluteTracking", HmdMatrix34_t),
    ]


class VRTextureDepthInfo_t(Structure):
    _fields_ = [
        ("handle", c_void_p),
        ("mProjection", HmdMatrix44_t),
        ("vRange", HmdVector2_t),
    ]


class VRTextureWithDepth_t(Texture_t):
    _fields_ = [
        ("depth", VRTextureDepthInfo_t),
    ]


class VRTextureWithPoseAndDepth_t(VRTextureWithPose_t):
    _fields_ = [
        ("depth", VRTextureDepthInfo_t),
    ]


class VRVulkanTextureData_t(Structure):
    """
    Data required for passing Vulkan textures to IVRCompositor::Submit.
    Be sure to call OpenVR_Shutdown before destroying these resources. 
    Please see https://github.com/ValveSoftware/openvr/wiki/Vulkan for Vulkan-specific documentation
    """

    _fields_ = [
        ("m_nImage", c_uint64),
        ("m_pDevice", POINTER(VkDevice_T)),
        ("m_pPhysicalDevice", POINTER(VkPhysicalDevice_T)),
        ("m_pInstance", POINTER(VkInstance_T)),
        ("m_pQueue", POINTER(VkQueue_T)),
        ("m_nQueueFamilyIndex", c_uint32),
        ("m_nWidth", c_uint32),
        ("m_nHeight", c_uint32),
        ("m_nFormat", c_uint32),
        ("m_nSampleCount", c_uint32),
    ]


class D3D12TextureData_t(Structure):
    """
    Data required for passing D3D12 textures to IVRCompositor::Submit.
    Be sure to call OpenVR_Shutdown before destroying these resources.
    """

    _fields_ = [
        ("m_pResource", POINTER(ID3D12Resource)),
        ("m_pCommandQueue", POINTER(ID3D12CommandQueue)),
        ("m_nNodeMask", c_uint32),
    ]


class VREvent_Controller_t(Structure):
    """used for controller button events"""

    _fields_ = [
        ("button", c_uint32),
    ]


class VREvent_Mouse_t(Structure):
    """used for simulated mouse events in overlay space"""

    _fields_ = [
        ("x", c_float),
        ("y", c_float),
        ("button", c_uint32),
    ]


class VREvent_Scroll_t(Structure):
    """used for simulated mouse wheel scroll"""

    _fields_ = [
        ("xdelta", c_float),
        ("ydelta", c_float),
        ("unused", c_uint32),
        ("viewportscale", c_float),
    ]


class VREvent_TouchPadMove_t(Structure):
    """
    when in mouse input mode you can receive data from the touchpad, these events are only sent if the users finger
    is on the touchpad (or just released from it). These events are sent to overlays with the VROverlayFlags_SendVRTouchpadEvents
    flag set.
    """

    _fields_ = [
        ("bFingerDown", openvr_bool),
        ("flSecondsFingerDown", c_float),
        ("fValueXFirst", c_float),
        ("fValueYFirst", c_float),
        ("fValueXRaw", c_float),
        ("fValueYRaw", c_float),
    ]


class VREvent_Notification_t(Structure):
    """notification related events. Details will still change at this point"""

    _fields_ = [
        ("ulUserValue", c_uint64),
        ("notificationId", c_uint32),
    ]


class VREvent_Process_t(Structure):
    """Used for events about processes"""

    _fields_ = [
        ("pid", c_uint32),
        ("oldPid", c_uint32),
        ("bForced", openvr_bool),
        ("bConnectionLost", openvr_bool),
    ]


class VREvent_Overlay_t(Structure):
    """Used for a few events about overlays"""

    _fields_ = [
        ("overlayHandle", c_uint64),
        ("devicePath", c_uint64),
    ]


class VREvent_Status_t(Structure):
    """Used for a few events about overlays"""

    _fields_ = [
        ("statusState", c_uint32),
    ]


class VREvent_Keyboard_t(Structure):
    """Used for keyboard events"""

    _fields_ = [
        ("cNewInput", c_char * 8),
        ("uUserValue", c_uint64),
    ]


class VREvent_Ipd_t(Structure):
    _fields_ = [
        ("ipdMeters", c_float),
    ]


class VREvent_Chaperone_t(Structure):
    _fields_ = [
        ("m_nPreviousUniverse", c_uint64),
        ("m_nCurrentUniverse", c_uint64),
    ]


class VREvent_Reserved_t(Structure):
    """Not actually used for any events"""

    _fields_ = [
        ("reserved0", c_uint64),
        ("reserved1", c_uint64),
        ("reserved2", c_uint64),
        ("reserved3", c_uint64),
        ("reserved4", c_uint64),
        ("reserved5", c_uint64),
    ]


class VREvent_PerformanceTest_t(Structure):
    _fields_ = [
        ("m_nFidelityLevel", c_uint32),
    ]


class VREvent_SeatedZeroPoseReset_t(Structure):
    _fields_ = [
        ("bResetBySystemMenu", openvr_bool),
    ]


class VREvent_Screenshot_t(Structure):
    _fields_ = [
        ("handle", c_uint32),
        ("type", c_uint32),
    ]


class VREvent_ScreenshotProgress_t(Structure):
    _fields_ = [
        ("progress", c_float),
    ]


class VREvent_ApplicationLaunch_t(Structure):
    _fields_ = [
        ("pid", c_uint32),
        ("unArgsHandle", c_uint32),
    ]


class VREvent_EditingCameraSurface_t(Structure):
    _fields_ = [
        ("overlayHandle", c_uint64),
        ("nVisualMode", c_uint32),
    ]


class VREvent_MessageOverlay_t(Structure):
    _fields_ = [
        ("unVRMessageOverlayResponse", c_uint32),
    ]


class VREvent_Property_t(Structure):
    _fields_ = [
        ("container", PropertyContainerHandle_t),
        ("prop", ETrackedDeviceProperty),
    ]


class VREvent_DualAnalog_t(Structure):
    _fields_ = [
        ("x", c_float),
        ("y", c_float),
        ("transformedX", c_float),
        ("transformedY", c_float),
        ("which", EDualAnalogWhich),
    ]


class VREvent_HapticVibration_t(Structure):
    _fields_ = [
        ("containerHandle", c_uint64),
        ("componentHandle", c_uint64),
        ("fDurationSeconds", c_float),
        ("fFrequency", c_float),
        ("fAmplitude", c_float),
    ]


class VREvent_WebConsole_t(Structure):
    _fields_ = [
        ("webConsoleHandle", WebConsoleHandle_t),
    ]


class VREvent_InputBindingLoad_t(Structure):
    _fields_ = [
        ("ulAppContainer", PropertyContainerHandle_t),
        ("pathMessage", c_uint64),
        ("pathUrl", c_uint64),
        ("pathControllerType", c_uint64),
    ]


class VREvent_InputActionManifestLoad_t(Structure):
    _fields_ = [
        ("pathAppKey", c_uint64),
        ("pathMessage", c_uint64),
        ("pathMessageParam", c_uint64),
        ("pathManifestPath", c_uint64),
    ]


class VREvent_SpatialAnchor_t(Structure):
    _fields_ = [
        ("unHandle", SpatialAnchorHandle_t),
    ]


class VREvent_ProgressUpdate_t(Structure):
    _fields_ = [
        ("ulApplicationPropertyContainer", c_uint64),
        ("pathDevice", c_uint64),
        ("pathInputSource", c_uint64),
        ("pathProgressAction", c_uint64),
        ("pathIcon", c_uint64),
        ("fProgress", c_float),
    ]


class VREvent_ShowUI_t(Structure):
    _fields_ = [
        ("eType", EShowUIType),
    ]


class VREvent_ShowDevTools_t(Structure):
    _fields_ = [
        ("nBrowserIdentifier", c_int32),
    ]


class VREvent_HDCPError_t(Structure):
    _fields_ = [
        ("eCode", EHDCPError),
    ]


class VREvent_Data_t(Union):
    _fields_ = [
        ("reserved", VREvent_Reserved_t),
        ("controller", VREvent_Controller_t),
        ("mouse", VREvent_Mouse_t),
        ("scroll", VREvent_Scroll_t),
        ("process", VREvent_Process_t),
        ("notification", VREvent_Notification_t),
        ("overlay", VREvent_Overlay_t),
        ("status", VREvent_Status_t),
        ("keyboard", VREvent_Keyboard_t),
        ("ipd", VREvent_Ipd_t),
        ("chaperone", VREvent_Chaperone_t),
        ("performanceTest", VREvent_PerformanceTest_t),
        ("touchPadMove", VREvent_TouchPadMove_t),
        ("seatedZeroPoseReset", VREvent_SeatedZeroPoseReset_t),
        ("screenshot", VREvent_Screenshot_t),
        ("screenshotProgress", VREvent_ScreenshotProgress_t),
        ("applicationLaunch", VREvent_ApplicationLaunch_t),
        ("cameraSurface", VREvent_EditingCameraSurface_t),
        ("messageOverlay", VREvent_MessageOverlay_t),
        ("property", VREvent_Property_t),
        ("dualAnalog", VREvent_DualAnalog_t),
        ("hapticVibration", VREvent_HapticVibration_t),
        ("webConsole", VREvent_WebConsole_t),
        ("inputBinding", VREvent_InputBindingLoad_t),
        ("actionManifest", VREvent_InputActionManifestLoad_t),
        ("spatialAnchor", VREvent_SpatialAnchor_t),
        ("progressUpdate", VREvent_ProgressUpdate_t),
        ("showUi", VREvent_ShowUI_t),
        ("showDevTools", VREvent_ShowDevTools_t),
        ("hdcpError", VREvent_HDCPError_t),
    ]


class VREvent_t(PackHackStructure):
    """An event posted by the server to all running applications"""

    _fields_ = [
        ("eventType", c_uint32),
        ("trackedDeviceIndex", TrackedDeviceIndex_t),
        ("eventAgeSeconds", c_float),
        ("data", VREvent_Data_t),
    ]


class HiddenAreaMesh_t(Structure):
    """
    The mesh to draw into the stencil (or depth) buffer to perform 
    early stencil (or depth) kills of pixels that will never appear on the HMD.
    This mesh draws on all the pixels that will be hidden after distortion. 

    If the HMD does not provide a visible area mesh pVertexData will be
    NULL and unTriangleCount will be 0.
    """

    _fields_ = [
        ("pVertexData", POINTER(HmdVector2_t)),
        ("unTriangleCount", c_uint32),
    ]


class VRControllerAxis_t(Structure):
    """contains information about one axis on the controller"""

    _fields_ = [
        ("x", c_float),
        ("y", c_float),
    ]


class VRControllerState_t(PackHackStructure):
    """Holds all the state of a controller at one moment in time."""

    _fields_ = [
        ("unPacketNum", c_uint32),
        ("ulButtonPressed", c_uint64),
        ("ulButtonTouched", c_uint64),
        ("rAxis", VRControllerAxis_t * 5),
    ]


class Compositor_OverlaySettings(Structure):
    """Allows the application to customize how the overlay appears in the compositor"""

    _fields_ = [
        ("size", c_uint32),
        ("curved", openvr_bool),
        ("antialias", openvr_bool),
        ("scale", c_float),
        ("distance", c_float),
        ("alpha", c_float),
        ("uOffset", c_float),
        ("vOffset", c_float),
        ("uScale", c_float),
        ("vScale", c_float),
        ("gridDivs", c_float),
        ("gridWidth", c_float),
        ("gridScale", c_float),
        ("transform", HmdMatrix44_t),
    ]


class VRBoneTransform_t(Structure):
    """Holds the transform for a single bone"""

    _fields_ = [
        ("position", HmdVector4_t),
        ("orientation", HmdQuaternionf_t),
    ]


class CameraVideoStreamFrameHeader_t(Structure):
    _fields_ = [
        ("eFrameType", EVRTrackedCameraFrameType),
        ("nWidth", c_uint32),
        ("nHeight", c_uint32),
        ("nBytesPerPixel", c_uint32),
        ("nFrameSequence", c_uint32),
        ("standingTrackedDevicePose", TrackedDevicePose_t),
        ("ulFrameExposureTime", c_uint64),
    ]


class DriverDirectMode_FrameTiming(Structure):
    """Frame timing data provided by direct mode drivers."""

    _fields_ = [
        ("m_nSize", c_uint32),
        ("m_nNumFramePresents", c_uint32),
        ("m_nNumMisPresented", c_uint32),
        ("m_nNumDroppedFrames", c_uint32),
        ("m_nReprojectionFlags", c_uint32),
    ]


class ImuSample_t(Structure):
    _fields_ = [
        ("fSampleTime", c_double),
        ("vAccel", HmdVector3d_t),
        ("vGyro", HmdVector3d_t),
        ("unOffScaleFlags", c_uint32),
    ]


class AppOverrideKeys_t(Structure):
    _fields_ = [
        ("pchKey", c_char_p),
        ("pchValue", c_char_p),
    ]


class Compositor_FrameTiming(Structure):
    """Provides a single frame's timing information to the app"""

    _fields_ = [
        ("m_nSize", c_uint32),
        ("m_nFrameIndex", c_uint32),
        ("m_nNumFramePresents", c_uint32),
        ("m_nNumMisPresented", c_uint32),
        ("m_nNumDroppedFrames", c_uint32),
        ("m_nReprojectionFlags", c_uint32),
        ("m_flSystemTimeInSeconds", c_double),
        ("m_flPreSubmitGpuMs", c_float),
        ("m_flPostSubmitGpuMs", c_float),
        ("m_flTotalRenderGpuMs", c_float),
        ("m_flCompositorRenderGpuMs", c_float),
        ("m_flCompositorRenderCpuMs", c_float),
        ("m_flCompositorIdleCpuMs", c_float),
        ("m_flClientFrameIntervalMs", c_float),
        ("m_flPresentCallCpuMs", c_float),
        ("m_flWaitForPresentCpuMs", c_float),
        ("m_flSubmitFrameMs", c_float),
        ("m_flWaitGetPosesCalledMs", c_float),
        ("m_flNewPosesReadyMs", c_float),
        ("m_flNewFrameReadyMs", c_float),
        ("m_flCompositorUpdateStartMs", c_float),
        ("m_flCompositorUpdateEndMs", c_float),
        ("m_flCompositorRenderStartMs", c_float),
        ("m_HmdPose", TrackedDevicePose_t),
        ("m_nNumVSyncsReadyForUse", c_uint32),
        ("m_nNumVSyncsToFirstView", c_uint32),
    ]


class Compositor_CumulativeStats(Structure):
    """
    Cumulative stats for current application.  These are not cleared until a new app connects,
    but they do stop accumulating once the associated app disconnects.
    """

    _fields_ = [
        ("m_nPid", c_uint32),
        ("m_nNumFramePresents", c_uint32),
        ("m_nNumDroppedFrames", c_uint32),
        ("m_nNumReprojectedFrames", c_uint32),
        ("m_nNumFramePresentsOnStartup", c_uint32),
        ("m_nNumDroppedFramesOnStartup", c_uint32),
        ("m_nNumReprojectedFramesOnStartup", c_uint32),
        ("m_nNumLoading", c_uint32),
        ("m_nNumFramePresentsLoading", c_uint32),
        ("m_nNumDroppedFramesLoading", c_uint32),
        ("m_nNumReprojectedFramesLoading", c_uint32),
        ("m_nNumTimedOut", c_uint32),
        ("m_nNumFramePresentsTimedOut", c_uint32),
        ("m_nNumDroppedFramesTimedOut", c_uint32),
        ("m_nNumReprojectedFramesTimedOut", c_uint32),
    ]


class NotificationBitmap_t(Structure):
    """Used for passing graphic data"""

    _fields_ = [
        ("m_pImageData", c_void_p),
        ("m_nWidth", c_int32),
        ("m_nHeight", c_int32),
        ("m_nBytesPerPixel", c_int32),
    ]


class VROverlayIntersectionParams_t(Structure):
    _fields_ = [
        ("vSource", HmdVector3_t),
        ("vDirection", HmdVector3_t),
        ("eOrigin", ETrackingUniverseOrigin),
    ]


class VROverlayIntersectionResults_t(Structure):
    _fields_ = [
        ("vPoint", HmdVector3_t),
        ("vNormal", HmdVector3_t),
        ("vUVs", HmdVector2_t),
        ("fDistance", c_float),
    ]


class IntersectionMaskRectangle_t(Structure):
    _fields_ = [
        ("m_flTopLeftX", c_float),
        ("m_flTopLeftY", c_float),
        ("m_flWidth", c_float),
        ("m_flHeight", c_float),
    ]


class IntersectionMaskCircle_t(Structure):
    _fields_ = [
        ("m_flCenterX", c_float),
        ("m_flCenterY", c_float),
        ("m_flRadius", c_float),
    ]


class VROverlayIntersectionMaskPrimitive_Data_t(Union):
    """NOTE!!! If you change this you MUST manually update openvr_interop.cs.py and openvr_api_flat.h.py"""

    _fields_ = [
        ("m_Rectangle", IntersectionMaskRectangle_t),
        ("m_Circle", IntersectionMaskCircle_t),
    ]


class VROverlayIntersectionMaskPrimitive_t(Structure):
    _fields_ = [
        ("m_nPrimitiveType", EVROverlayIntersectionMaskPrimitiveType),
        ("m_Primitive", VROverlayIntersectionMaskPrimitive_Data_t),
    ]


class RenderModel_ComponentState_t(Structure):
    """Describes state information about a render-model component, including transforms and other dynamic properties"""

    _fields_ = [
        ("mTrackingToComponentRenderModel", HmdMatrix34_t),
        ("mTrackingToComponentLocal", HmdMatrix34_t),
        ("uProperties", VRComponentProperties),
    ]


class RenderModel_Vertex_t(Structure):
    """A single vertex in a render model"""

    _fields_ = [
        ("vPosition", HmdVector3_t),
        ("vNormal", HmdVector3_t),
        ("rfTextureCoord", c_float * 2),
    ]


class RenderModel_TextureMap_t(Structure):
    _fields_ = [
        ("unWidth", c_uint16),
        ("unHeight", c_uint16),
        ("rubTextureMapData", POINTER(c_uint8)),
    ]


class RenderModel_t(Structure):
    _fields_ = [
        ("rVertexData", POINTER(RenderModel_Vertex_t)),
        ("unVertexCount", c_uint32),
        ("rIndexData", POINTER(c_uint16)),
        ("unTriangleCount", c_uint32),
        ("diffuseTextureId", TextureID_t),
    ]


class RenderModel_ControllerMode_State_t(Structure):
    _fields_ = [
        ("bScrollWheelVisible", openvr_bool),
    ]


class InputAnalogActionData_t(Structure):
    _fields_ = [
        ("bActive", openvr_bool),
        ("activeOrigin", VRInputValueHandle_t),
        ("x", c_float),
        ("y", c_float),
        ("z", c_float),
        ("deltaX", c_float),
        ("deltaY", c_float),
        ("deltaZ", c_float),
        ("fUpdateTime", c_float),
    ]


class InputDigitalActionData_t(Structure):
    _fields_ = [
        ("bActive", openvr_bool),
        ("activeOrigin", VRInputValueHandle_t),
        ("bState", openvr_bool),
        ("bChanged", openvr_bool),
        ("fUpdateTime", c_float),
    ]


class InputPoseActionData_t(Structure):
    _fields_ = [
        ("bActive", openvr_bool),
        ("activeOrigin", VRInputValueHandle_t),
        ("pose", TrackedDevicePose_t),
    ]


class InputSkeletalActionData_t(Structure):
    _fields_ = [
        ("bActive", openvr_bool),
        ("activeOrigin", VRInputValueHandle_t),
    ]


class InputOriginInfo_t(Structure):
    _fields_ = [
        ("devicePath", VRInputValueHandle_t),
        ("trackedDeviceIndex", TrackedDeviceIndex_t),
        ("rchRenderModelComponentName", c_char * 128),
    ]


class VRActiveActionSet_t(Structure):
    _fields_ = [
        ("ulActionSet", VRActionSetHandle_t),
        ("ulRestrictedToDevice", VRInputValueHandle_t),
        ("ulSecondaryActionSet", VRActionSetHandle_t),
        ("unPadding", c_uint32),
        ("nPriority", c_int32),
    ]


class VRSkeletalSummaryData_t(Structure):
    """Contains summary information about the current skeletal pose"""

    _fields_ = [
        ("flFingerCurl", c_float * 5),
        ("flFingerSplay", c_float * 4),
    ]


class SpatialAnchorPose_t(Structure):
    _fields_ = [
        ("mAnchorToAbsoluteTracking", HmdMatrix34_t),
    ]


class COpenVRContext(object):
    def __init__(self):
        self.m_pVRSystem = None
        self.m_pVRChaperone = None
        self.m_pVRChaperoneSetup = None
        self.m_pVRCompositor = None
        self.m_pVROverlay = None
        self.m_pVRResources = None
        self.m_pVRRenderModels = None
        self.m_pVRExtendedDisplay = None
        self.m_pVRSettings = None
        self.m_pVRApplications = None
        self.m_pVRTrackedCamera = None
        self.m_pVRScreenshots = None
        self.m_pVRDriverManager = None
        self.m_pVRInput = None
        self.m_pVRIOBuffer = None
        self.m_pVRSpatialAnchors = None
        self.m_pVRNotifications = None

    def checkClear(self):
        global _vr_token
        if _vr_token != getInitToken():
            self.clear()
            _vr_token = getInitToken()

    def clear(self):  
        self.m_pVRSystem = None
        self.m_pVRChaperone = None
        self.m_pVRChaperoneSetup = None
        self.m_pVRCompositor = None
        self.m_pVROverlay = None
        self.m_pVRResources = None
        self.m_pVRRenderModels = None
        self.m_pVRExtendedDisplay = None
        self.m_pVRSettings = None
        self.m_pVRApplications = None
        self.m_pVRTrackedCamera = None
        self.m_pVRScreenshots = None
        self.m_pVRDriverManager = None
        self.m_pVRInput = None
        self.m_pVRIOBuffer = None
        self.m_pVRSpatialAnchors = None
        self.m_pVRNotifications = None

    def VRSystem(self):
        self.checkClear()
        if self.m_pVRSystem is None:
            self.m_pVRSystem = IVRSystem()
        return self.m_pVRSystem

    def VRChaperone(self):
        self.checkClear()
        if self.m_pVRChaperone is None:
            self.m_pVRChaperone = IVRChaperone()
        return self.m_pVRChaperone

    def VRChaperoneSetup(self):
        self.checkClear()
        if self.m_pVRChaperoneSetup is None:
            self.m_pVRChaperoneSetup = IVRChaperoneSetup()
        return self.m_pVRChaperoneSetup

    def VRCompositor(self):
        self.checkClear()
        if self.m_pVRCompositor is None:
            self.m_pVRCompositor = IVRCompositor()
        return self.m_pVRCompositor

    def VROverlay(self):
        self.checkClear()
        if self.m_pVROverlay is None:
            self.m_pVROverlay = IVROverlay()
        return self.m_pVROverlay

    def VRResources(self):
        self.checkClear()
        if self.m_pVRResources is None:
            self.m_pVRResources = IVRResources()
        return self.m_pVRResources

    def VRScreenshots(self):
        self.checkClear()
        if self.m_pVRScreenshots is None:
            self.m_pVRScreenshots = IVRScreenshots()
        return self.m_pVRScreenshots

    def VRRenderModels(self):
        self.checkClear()
        if self.m_pVRRenderModels is None:
            self.m_pVRRenderModels = IVRRenderModels()
        return self.m_pVRRenderModels

    def VRExtendedDisplay(self):
        self.checkClear()
        if self.m_pVRExtendedDisplay is None:
            self.m_pVRExtendedDisplay = IVRExtendedDisplay()
        return self.m_pVRExtendedDisplay

    def VRSettings(self):
        self.checkClear()
        if self.m_pVRSettings is None:
            self.m_pVRSettings = IVRSettings()
        return self.m_pVRSettings

    def VRApplications(self):
        self.checkClear()
        if self.m_pVRApplications is None:
            self.m_pVRApplications = IVRApplications()
        return self.m_pVRApplications

    def VRTrackedCamera(self):
        self.checkClear()
        if self.m_pVRTrackedCamera is None:
            self.m_pVRTrackedCamera = IVRTrackedCamera()
        return self.m_pVRTrackedCamera

    def VRDriverManager(self):
        self.checkClear()
        if self.m_pVRDriverManager is None:
            self.m_pVRDriverManager = IVRDriverManager()
        return self.m_pVRDriverManager

    def VRInput(self):
        self.checkClear()
        if self.m_pVRInput is None:
            self.m_pVRInput = IVRInput()
        return self.m_pVRInput

    def VRIOBuffer(self):
        self.checkClear()
        if self.m_pVRIOBuffer is None:
            self.m_pVRIOBuffer = IVRIOBuffer()
        return self.m_pVRIOBuffer

    def VRSpatialAnchors(self):
        self.checkClear()
        if self.m_pVRSpatialAnchors is None:
            self.m_pVRSpatialAnchors = IVRSpatialAnchors()
        return self.m_pVRSpatialAnchors

    def VRNotifications(self):
        self.checkClear()
        if self.m_pVRNotifications is None:
            self.m_pVRNotifications = IVRNotifications()
        return self.m_pVRNotifications


# Globals for context management
_vr_token = None
_internal_module_context = COpenVRContext()


def VRSystem():
    return _internal_module_context.VRSystem()


def VRChaperone():
    return _internal_module_context.VRChaperone()


def VRChaperoneSetup():
    return _internal_module_context.VRChaperoneSetup()


def VRCompositor():
    return _internal_module_context.VRCompositor()


def VROverlay():
    return _internal_module_context.VROverlay()


def VRResources():
    return _internal_module_context.VRResources()


def VRScreenshots():
    return _internal_module_context.VRScreenshots()


def VRRenderModels():
    return _internal_module_context.VRRenderModels()


def VRExtendedDisplay():
    return _internal_module_context.VRExtendedDisplay()


def VRSettings():
    return _internal_module_context.VRSettings()


def VRApplications():
    return _internal_module_context.VRApplications()


def VRTrackedCamera():
    return _internal_module_context.VRTrackedCamera()


def VRDriverManager():
    return _internal_module_context.VRDriverManager()


def VRInput():
    return _internal_module_context.VRInput()


def VRIOBuffer():
    return _internal_module_context.VRIOBuffer()


def VRSpatialAnchors():
    return _internal_module_context.VRSpatialAnchors()


def VRNotifications():
    return _internal_module_context.VRNotifications()


class IVRSystem_FnTable(Structure):
    _fields_ = [
        ("getRecommendedRenderTargetSize", OPENVR_FNTABLE_CALLTYPE(None, POINTER(c_uint32), POINTER(c_uint32))),
        ("getProjectionMatrix", OPENVR_FNTABLE_CALLTYPE(HmdMatrix44_t, EVREye, c_float, c_float)),
        ("getProjectionRaw", OPENVR_FNTABLE_CALLTYPE(None, EVREye, POINTER(c_float), POINTER(c_float), POINTER(c_float), POINTER(c_float))),
        ("computeDistortion", OPENVR_FNTABLE_CALLTYPE(openvr_bool, EVREye, c_float, c_float, POINTER(DistortionCoordinates_t))),
        ("getEyeToHeadTransform", OPENVR_FNTABLE_CALLTYPE(HmdMatrix34_t, EVREye)),
        ("getTimeSinceLastVsync", OPENVR_FNTABLE_CALLTYPE(openvr_bool, POINTER(c_float), POINTER(c_uint64))),
        ("getD3D9AdapterIndex", OPENVR_FNTABLE_CALLTYPE(c_int32)),
        ("getDXGIOutputInfo", OPENVR_FNTABLE_CALLTYPE(None, POINTER(c_int32))),
        ("getOutputDevice", OPENVR_FNTABLE_CALLTYPE(None, POINTER(c_uint64), ETextureType, POINTER(VkInstance_T))),
        ("isDisplayOnDesktop", OPENVR_FNTABLE_CALLTYPE(openvr_bool)),
        ("setDisplayVisibility", OPENVR_FNTABLE_CALLTYPE(openvr_bool, openvr_bool)),
        ("getDeviceToAbsoluteTrackingPose", OPENVR_FNTABLE_CALLTYPE(None, ETrackingUniverseOrigin, c_float, POINTER(TrackedDevicePose_t), c_uint32)),
        ("resetSeatedZeroPose", OPENVR_FNTABLE_CALLTYPE(None)),
        ("getSeatedZeroPoseToStandingAbsoluteTrackingPose", OPENVR_FNTABLE_CALLTYPE(HmdMatrix34_t)),
        ("getRawZeroPoseToStandingAbsoluteTrackingPose", OPENVR_FNTABLE_CALLTYPE(HmdMatrix34_t)),
        ("getSortedTrackedDeviceIndicesOfClass", OPENVR_FNTABLE_CALLTYPE(c_uint32, ETrackedDeviceClass, POINTER(TrackedDeviceIndex_t), c_uint32, TrackedDeviceIndex_t)),
        ("getTrackedDeviceActivityLevel", OPENVR_FNTABLE_CALLTYPE(EDeviceActivityLevel, TrackedDeviceIndex_t)),
        ("applyTransform", OPENVR_FNTABLE_CALLTYPE(None, POINTER(TrackedDevicePose_t), POINTER(TrackedDevicePose_t), POINTER(HmdMatrix34_t))),
        ("getTrackedDeviceIndexForControllerRole", OPENVR_FNTABLE_CALLTYPE(TrackedDeviceIndex_t, ETrackedControllerRole)),
        ("getControllerRoleForTrackedDeviceIndex", OPENVR_FNTABLE_CALLTYPE(ETrackedControllerRole, TrackedDeviceIndex_t)),
        ("getTrackedDeviceClass", OPENVR_FNTABLE_CALLTYPE(ETrackedDeviceClass, TrackedDeviceIndex_t)),
        ("isTrackedDeviceConnected", OPENVR_FNTABLE_CALLTYPE(openvr_bool, TrackedDeviceIndex_t)),
        ("getBoolTrackedDeviceProperty", OPENVR_FNTABLE_CALLTYPE(openvr_bool, TrackedDeviceIndex_t, ETrackedDeviceProperty, POINTER(ETrackedPropertyError))),
        ("getFloatTrackedDeviceProperty", OPENVR_FNTABLE_CALLTYPE(c_float, TrackedDeviceIndex_t, ETrackedDeviceProperty, POINTER(ETrackedPropertyError))),
        ("getInt32TrackedDeviceProperty", OPENVR_FNTABLE_CALLTYPE(c_int32, TrackedDeviceIndex_t, ETrackedDeviceProperty, POINTER(ETrackedPropertyError))),
        ("getUint64TrackedDeviceProperty", OPENVR_FNTABLE_CALLTYPE(c_uint64, TrackedDeviceIndex_t, ETrackedDeviceProperty, POINTER(ETrackedPropertyError))),
        ("getMatrix34TrackedDeviceProperty", OPENVR_FNTABLE_CALLTYPE(HmdMatrix34_t, TrackedDeviceIndex_t, ETrackedDeviceProperty, POINTER(ETrackedPropertyError))),
        ("getArrayTrackedDeviceProperty", OPENVR_FNTABLE_CALLTYPE(c_uint32, TrackedDeviceIndex_t, ETrackedDeviceProperty, PropertyTypeTag_t, c_void_p, c_uint32, POINTER(ETrackedPropertyError))),
        ("getStringTrackedDeviceProperty", OPENVR_FNTABLE_CALLTYPE(c_uint32, TrackedDeviceIndex_t, ETrackedDeviceProperty, c_char_p, c_uint32, POINTER(ETrackedPropertyError))),
        ("getPropErrorNameFromEnum", OPENVR_FNTABLE_CALLTYPE(c_char_p, ETrackedPropertyError)),
        ("pollNextEvent", OPENVR_FNTABLE_CALLTYPE(openvr_bool, POINTER(VREvent_t), c_uint32)),
        ("pollNextEventWithPose", OPENVR_FNTABLE_CALLTYPE(openvr_bool, ETrackingUniverseOrigin, POINTER(VREvent_t), c_uint32, POINTER(TrackedDevicePose_t))),
        ("getEventTypeNameFromEnum", OPENVR_FNTABLE_CALLTYPE(c_char_p, EVREventType)),
        ("getHiddenAreaMesh", OPENVR_FNTABLE_CALLTYPE(HiddenAreaMesh_t, EVREye, EHiddenAreaMeshType)),
        ("getControllerState", OPENVR_FNTABLE_CALLTYPE(openvr_bool, TrackedDeviceIndex_t, POINTER(VRControllerState_t), c_uint32)),
        ("getControllerStateWithPose", OPENVR_FNTABLE_CALLTYPE(openvr_bool, ETrackingUniverseOrigin, TrackedDeviceIndex_t, POINTER(VRControllerState_t), c_uint32, POINTER(TrackedDevicePose_t))),
        ("triggerHapticPulse", OPENVR_FNTABLE_CALLTYPE(None, TrackedDeviceIndex_t, c_uint32, c_ushort)),
        ("getButtonIdNameFromEnum", OPENVR_FNTABLE_CALLTYPE(c_char_p, EVRButtonId)),
        ("getControllerAxisTypeNameFromEnum", OPENVR_FNTABLE_CALLTYPE(c_char_p, EVRControllerAxisType)),
        ("isInputAvailable", OPENVR_FNTABLE_CALLTYPE(openvr_bool)),
        ("isSteamVRDrawingControllers", OPENVR_FNTABLE_CALLTYPE(openvr_bool)),
        ("shouldApplicationPause", OPENVR_FNTABLE_CALLTYPE(openvr_bool)),
        ("shouldApplicationReduceRenderingWork", OPENVR_FNTABLE_CALLTYPE(openvr_bool)),
        ("driverDebugRequest", OPENVR_FNTABLE_CALLTYPE(c_uint32, TrackedDeviceIndex_t, c_char_p, c_char_p, c_uint32)),
        ("performFirmwareUpdate", OPENVR_FNTABLE_CALLTYPE(EVRFirmwareError, TrackedDeviceIndex_t)),
        ("acknowledgeQuit_Exiting", OPENVR_FNTABLE_CALLTYPE(None)),
        ("acknowledgeQuit_UserPrompt", OPENVR_FNTABLE_CALLTYPE(None)),
    ]


class IVRSystem(object):
    def __init__(self):
        version_key = IVRSystem_Version
        if not isInterfaceVersionValid(version_key):
            _checkInitError(VRInitError_Init_InterfaceNotFound)
        fn_key = 'FnTable:' + version_key
        fn_type = IVRSystem_FnTable
        fn_table_ptr = cast(getGenericInterface(fn_key), POINTER(fn_type))
        if fn_table_ptr is None:
            raise OpenVRError("Error retrieving VR API for IVRSystem")
        self.function_table = fn_table_ptr.contents

    def getRecommendedRenderTargetSize(self):
        """Suggested size for the intermediate render target that the distortion pulls from."""
        fn = self.function_table.getRecommendedRenderTargetSize
        width = c_uint32()
        height = c_uint32()
        fn(byref(width), byref(height))
        return width.value, height.value

    def getProjectionMatrix(self, eye, nearZ: float, farZ: float):
        """The projection matrix for the specified eye"""
        fn = self.function_table.getProjectionMatrix
        result = fn(eye, nearZ, farZ)
        return result

    def getProjectionRaw(self, eye):
        """
        The components necessary to build your own projection matrix in case your
        application is doing something fancy like infinite Z
        """
        fn = self.function_table.getProjectionRaw
        left = c_float()
        right = c_float()
        top = c_float()
        bottom = c_float()
        fn(eye, byref(left), byref(right), byref(top), byref(bottom))
        return left.value, right.value, top.value, bottom.value

    def computeDistortion(self, eye, u: float, v: float):
        """
        Gets the result of the distortion function for the specified eye and input UVs. UVs go from 0,0 in 
        the upper left of that eye's viewport and 1,1 in the lower right of that eye's viewport.
        Returns true for success. Otherwise, returns false, and distortion coordinates are not suitable.
        """
        fn = self.function_table.computeDistortion
        distortionCoordinates = DistortionCoordinates_t()
        result = fn(eye, u, v, byref(distortionCoordinates))
        return result, distortionCoordinates

    def getEyeToHeadTransform(self, eye):
        """
        Returns the transform from eye space to the head space. Eye space is the per-eye flavor of head
        space that provides stereo disparity. Instead of Model * View * Projection the sequence is Model * View * Eye^-1 * Projection. 
        Normally View and Eye^-1 will be multiplied together and treated as View in your application.
        """
        fn = self.function_table.getEyeToHeadTransform
        result = fn(eye)
        return result

    def getTimeSinceLastVsync(self):
        """
        Returns the number of elapsed seconds since the last recorded vsync event. This 
        will come from a vsync timer event in the timer if possible or from the application-reported
        time if that is not available. If no vsync times are available the function will 
        return zero for vsync time and frame counter and return false from the method.
        """
        fn = self.function_table.getTimeSinceLastVsync
        secondsSinceLastVsync = c_float()
        frameCounter = c_uint64()
        result = fn(byref(secondsSinceLastVsync), byref(frameCounter))
        return result, secondsSinceLastVsync.value, frameCounter.value

    def getD3D9AdapterIndex(self):
        """
        [D3D9 Only]
        Returns the adapter index that the user should pass into CreateDevice to set up D3D9 in such
        a way that it can go full screen exclusive on the HMD. Returns -1 if there was an error.
        """
        fn = self.function_table.getD3D9AdapterIndex
        result = fn()
        return result

    def getDXGIOutputInfo(self):
        """
        [D3D10/11 Only]
        Returns the adapter index that the user should pass into EnumAdapters to create the device 
        and swap chain in DX10 and DX11. If an error occurs the index will be set to -1.
        """
        fn = self.function_table.getDXGIOutputInfo
        adapterIndex = c_int32()
        fn(byref(adapterIndex))
        return adapterIndex.value

    def getOutputDevice(self, textureType):
        """
        Returns platform- and texture-type specific adapter identification so that applications and the
        compositor are creating textures and swap chains on the same GPU. If an error occurs the device
        will be set to 0.
        pInstance is an optional parameter that is required only when textureType is TextureType_Vulkan.
        [D3D10/11/12 Only (D3D9 Not Supported)]
         Returns the adapter LUID that identifies the GPU attached to the HMD. The user should
         enumerate all adapters using IDXGIFactory::EnumAdapters and IDXGIAdapter::GetDesc to find
         the adapter with the matching LUID, or use IDXGIFactory4::EnumAdapterByLuid.
         The discovered IDXGIAdapter should be used to create the device and swap chain.
        [Vulkan Only]
         Returns the VkPhysicalDevice that should be used by the application.
         pInstance must be the instance the application will use to query for the VkPhysicalDevice.  The application
         must create the VkInstance with extensions returned by IVRCompositor::GetVulkanInstanceExtensionsRequired enabled.
        [macOS Only]
         For TextureType_IOSurface returns the id<MTLDevice> that should be used by the application.
         On 10.13+ for TextureType_OpenGL returns the 'registryId' of the renderer which should be used
          by the application. See Apple Technical Q&A QA1168 for information on enumerating GL Renderers, and the
          new kCGLRPRegistryIDLow and kCGLRPRegistryIDHigh CGLRendererProperty values in the 10.13 SDK.
         Pre 10.13 for TextureType_OpenGL returns 0, as there is no dependable way to correlate the HMDs MTLDevice
          with a GL Renderer.
        """
        fn = self.function_table.getOutputDevice
        device = c_uint64()
        instance = VkInstance_T()
        fn(byref(device), textureType, byref(instance))
        return device.value, instance

    def isDisplayOnDesktop(self):
        """Use to determine if the headset display is part of the desktop (i.e. extended) or hidden (i.e. direct mode)."""
        fn = self.function_table.isDisplayOnDesktop
        result = fn()
        return result

    def setDisplayVisibility(self, isVisibleOnDesktop):
        """Set the display visibility (true = extended, false = direct mode).  Return value of true indicates that the change was successful."""
        fn = self.function_table.setDisplayVisibility
        result = fn(isVisibleOnDesktop)
        return result

    def getDeviceToAbsoluteTrackingPose(self, origin, predictedSecondsToPhotonsFromNow: float, trackedDevicePoseArray):
        """
        The pose that the tracker thinks that the HMD will be in at the specified number of seconds into the 
        future. Pass 0 to get the state at the instant the method is called. Most of the time the application should
        calculate the time until the photons will be emitted from the display and pass that time into the method.

        This is roughly analogous to the inverse of the view matrix in most applications, though 
        many games will need to do some additional rotation or translation on top of the rotation
        and translation provided by the head pose.

        For devices where bPoseIsValid is true the application can use the pose to position the device
        in question. The provided array can be any size up to k_unMaxTrackedDeviceCount. 

        Seated experiences should call this method with TrackingUniverseSeated and receive poses relative
        to the seated zero pose. Standing experiences should call this method with TrackingUniverseStanding 
        and receive poses relative to the Chaperone Play Area. TrackingUniverseRawAndUncalibrated should 
        probably not be used unless the application is the Chaperone calibration tool itself, but will provide
        poses relative to the hardware-specific coordinate system in the driver.
        """
        fn = self.function_table.getDeviceToAbsoluteTrackingPose
        if trackedDevicePoseArray is None:
            trackedDevicePoseArrayCount = 0
            trackedDevicePoseArrayArg = None
        elif isinstance(trackedDevicePoseArray, ctypes.Array):
            trackedDevicePoseArrayCount = len(trackedDevicePoseArray)
            trackedDevicePoseArrayArg = byref(trackedDevicePoseArray[0])
        else:
            trackedDevicePoseArrayCount = k_unMaxTrackedDeviceCount
            trackedDevicePoseArray = (TrackedDevicePose_t * trackedDevicePoseArrayCount)()
            trackedDevicePoseArrayArg = byref(trackedDevicePoseArray[0])
        fn(origin, predictedSecondsToPhotonsFromNow, trackedDevicePoseArrayArg, trackedDevicePoseArrayCount)
        return trackedDevicePoseArray

    def resetSeatedZeroPose(self) -> None:
        """
        Sets the zero pose for the seated tracker coordinate system to the current position and yaw of the HMD. After 
        ResetSeatedZeroPose all GetDeviceToAbsoluteTrackingPose calls that pass TrackingUniverseSeated as the origin 
        will be relative to this new zero pose. The new zero coordinate system will not change the fact that the Y axis 
        is up in the real world, so the next pose returned from GetDeviceToAbsoluteTrackingPose after a call to 
        ResetSeatedZeroPose may not be exactly an identity matrix.

        NOTE: This function overrides the user's previously saved seated zero pose and should only be called as the result of a user action. 
        Users are also able to set their seated zero pose via the OpenVR Dashboard.
        """
        fn = self.function_table.resetSeatedZeroPose
        fn()

    def getSeatedZeroPoseToStandingAbsoluteTrackingPose(self):
        """
        Returns the transform from the seated zero pose to the standing absolute tracking system. This allows 
        applications to represent the seated origin to used or transform object positions from one coordinate
        system to the other. 

        The seated origin may or may not be inside the Play Area or Collision Bounds returned by IVRChaperone. Its position 
        depends on what the user has set from the Dashboard settings and previous calls to ResetSeatedZeroPose.
        """
        fn = self.function_table.getSeatedZeroPoseToStandingAbsoluteTrackingPose
        result = fn()
        return result

    def getRawZeroPoseToStandingAbsoluteTrackingPose(self):
        """
        Returns the transform from the tracking origin to the standing absolute tracking system. This allows
        applications to convert from raw tracking space to the calibrated standing coordinate system.
        """
        fn = self.function_table.getRawZeroPoseToStandingAbsoluteTrackingPose
        result = fn()
        return result

    def getSortedTrackedDeviceIndicesOfClass(self, trackedDeviceClass, trackedDeviceIndexArray, relativeToTrackedDeviceIndex=k_unTrackedDeviceIndex_Hmd):
        """
        Get a sorted array of device indices of a given class of tracked devices (e.g. controllers).  Devices are sorted right to left
        relative to the specified tracked device (default: hmd -- pass in -1 for absolute tracking space).  Returns the number of devices
        in the list, or the size of the array needed if not large enough.
        """
        fn = self.function_table.getSortedTrackedDeviceIndicesOfClass
        if trackedDeviceIndexArray is None:
            trackedDeviceIndexArrayCount = 0
            trackedDeviceIndexArrayArg = None
        elif isinstance(trackedDeviceIndexArray, ctypes.Array):
            trackedDeviceIndexArrayCount = len(trackedDeviceIndexArray)
            trackedDeviceIndexArrayArg = byref(trackedDeviceIndexArray[0])
        else:
            trackedDeviceIndexArrayCount = k_unMaxTrackedDeviceCount
            trackedDeviceIndexArray = (TrackedDeviceIndex_t * trackedDeviceIndexArrayCount)()
            trackedDeviceIndexArrayArg = byref(trackedDeviceIndexArray[0])
        result = fn(trackedDeviceClass, trackedDeviceIndexArrayArg, trackedDeviceIndexArrayCount, relativeToTrackedDeviceIndex)
        return result, trackedDeviceIndexArray

    def getTrackedDeviceActivityLevel(self, deviceId):
        """Returns the level of activity on the device."""
        fn = self.function_table.getTrackedDeviceActivityLevel
        result = fn(deviceId)
        return result

    def applyTransform(self, trackedDevicePose, transform):
        """
        Convenience utility to apply the specified transform to the specified pose.
        This properly transforms all pose components, including velocity and angular velocity
        """
        fn = self.function_table.applyTransform
        outputPose = TrackedDevicePose_t()
        fn(byref(outputPose), byref(trackedDevicePose), byref(transform))
        return outputPose

    def getTrackedDeviceIndexForControllerRole(self, deviceType):
        """Returns the device index associated with a specific role, for example the left hand or the right hand. This function is deprecated in favor of the new IVRInput system."""
        fn = self.function_table.getTrackedDeviceIndexForControllerRole
        result = fn(deviceType)
        return result

    def getControllerRoleForTrackedDeviceIndex(self, deviceIndex):
        """Returns the controller type associated with a device index. This function is deprecated in favor of the new IVRInput system."""
        fn = self.function_table.getControllerRoleForTrackedDeviceIndex
        result = fn(deviceIndex)
        return result

    def getTrackedDeviceClass(self, deviceIndex):
        """
        Returns the device class of a tracked device. If there has not been a device connected in this slot
        since the application started this function will return TrackedDevice_Invalid. For previous detected
        devices the function will return the previously observed device class. 

        To determine which devices exist on the system, just loop from 0 to k_unMaxTrackedDeviceCount and check
        the device class. Every device with something other than TrackedDevice_Invalid is associated with an 
        actual tracked device.
        """
        fn = self.function_table.getTrackedDeviceClass
        result = fn(deviceIndex)
        return result

    def isTrackedDeviceConnected(self, deviceIndex):
        """Returns true if there is a device connected in this slot."""
        fn = self.function_table.isTrackedDeviceConnected
        result = fn(deviceIndex)
        return result

    def getBoolTrackedDeviceProperty(self, deviceIndex, prop):
        """Returns a bool property. If the device index is not valid or the property is not a bool type this function will return false."""
        fn = self.function_table.getBoolTrackedDeviceProperty
        error = ETrackedPropertyError()
        result = fn(deviceIndex, prop, byref(error))
        openvr.error_code.TrackedPropertyError.check_error_value(error.value)
        return result

    def getFloatTrackedDeviceProperty(self, deviceIndex, prop):
        """Returns a float property. If the device index is not valid or the property is not a float type this function will return 0."""
        fn = self.function_table.getFloatTrackedDeviceProperty
        error = ETrackedPropertyError()
        result = fn(deviceIndex, prop, byref(error))
        openvr.error_code.TrackedPropertyError.check_error_value(error.value)
        return result

    def getInt32TrackedDeviceProperty(self, deviceIndex, prop):
        """Returns an int property. If the device index is not valid or the property is not a int type this function will return 0."""
        fn = self.function_table.getInt32TrackedDeviceProperty
        error = ETrackedPropertyError()
        result = fn(deviceIndex, prop, byref(error))
        openvr.error_code.TrackedPropertyError.check_error_value(error.value)
        return result

    def getUint64TrackedDeviceProperty(self, deviceIndex, prop):
        """Returns a uint64 property. If the device index is not valid or the property is not a uint64 type this function will return 0."""
        fn = self.function_table.getUint64TrackedDeviceProperty
        error = ETrackedPropertyError()
        result = fn(deviceIndex, prop, byref(error))
        openvr.error_code.TrackedPropertyError.check_error_value(error.value)
        return result

    def getMatrix34TrackedDeviceProperty(self, deviceIndex, prop):
        """Returns a matrix property. If the device index is not valid or the property is not a matrix type, this function will return identity."""
        fn = self.function_table.getMatrix34TrackedDeviceProperty
        error = ETrackedPropertyError()
        result = fn(deviceIndex, prop, byref(error))
        openvr.error_code.TrackedPropertyError.check_error_value(error.value)
        return result

    def getArrayTrackedDeviceProperty(self, deviceIndex, prop, type_, buffer, bufferSize):
        """
        Returns an array of one type of property. If the device index is not valid or the property is not a single value or an array of the specified type,
        this function will return 0. Otherwise it returns the number of bytes necessary to hold the array of properties. If unBufferSize is
        greater than the returned size and pBuffer is non-NULL, pBuffer is filled with the contents of array of properties.
        """
        fn = self.function_table.getArrayTrackedDeviceProperty
        error = ETrackedPropertyError()
        result = fn(deviceIndex, prop, type_, byref(buffer), bufferSize, byref(error))
        openvr.error_code.TrackedPropertyError.check_error_value(error.value)
        return result

    def getStringTrackedDeviceProperty(self, deviceIndex, prop):
        """
        Returns a string property. If the device index is not valid or the property is not a string type this function will 
        return 0. Otherwise it returns the length of the number of bytes necessary to hold this string including the trailing
        null. Strings will always fit in buffers of k_unMaxPropertyStringSize characters.
        """
        fn = self.function_table.getStringTrackedDeviceProperty
        error = ETrackedPropertyError()
        bufferSize = fn(deviceIndex, prop, None, 0, byref(error))
        if bufferSize == 0:
            return ''
        value = ctypes.create_string_buffer(bufferSize)
        fn(deviceIndex, prop, value, bufferSize, byref(error))
        openvr.error_code.TrackedPropertyError.check_error_value(error.value)
        return bytes(value.value).decode('utf-8')

    def getPropErrorNameFromEnum(self, error):
        """
        returns a string that corresponds with the specified property error. The string will be the name 
        of the error enum value for all valid error codes
        """
        fn = self.function_table.getPropErrorNameFromEnum
        result = fn(error)
        return result

    def pollNextEvent(self, event):
        """
        Returns true and fills the event with the next event on the queue if there is one. If there are no events
        this method returns false. uncbVREvent should be the size in bytes of the VREvent_t struct
        """
        fn = self.function_table.pollNextEvent
        vREvent = sizeof(VREvent_t)
        result = fn(byref(event), vREvent)
        return result != 0

    def pollNextEventWithPose(self, origin, event):
        """
        Returns true and fills the event with the next event on the queue if there is one. If there are no events
          this method returns false. Fills in the pose of the associated tracked device in the provided pose struct. 
          This pose will always be older than the call to this function and should not be used to render the device. 
        uncbVREvent should be the size in bytes of the VREvent_t struct
        """
        fn = self.function_table.pollNextEventWithPose
        vREvent = sizeof(VREvent_t)
        trackedDevicePose = TrackedDevicePose_t()
        result = fn(origin, byref(event), vREvent, byref(trackedDevicePose))
        return result, event, trackedDevicePose

    def getEventTypeNameFromEnum(self, type_):
        """returns the name of an EVREvent enum value"""
        fn = self.function_table.getEventTypeNameFromEnum
        result = fn(type_)
        return result

    def getHiddenAreaMesh(self, eye, type_=k_eHiddenAreaMesh_Standard):
        """
        Returns the hidden area mesh for the current HMD. The pixels covered by this mesh will never be seen by the user after the lens distortion is
        applied based on visibility to the panels. If this HMD does not have a hidden area mesh, the vertex data and count will be NULL and 0 respectively.
        This mesh is meant to be rendered into the stencil buffer (or into the depth buffer setting nearz) before rendering each eye's view. 
        This will improve performance by letting the GPU early-reject pixels the user will never see before running the pixel shader.
        NOTE: Render this mesh with backface culling disabled since the winding order of the vertices can be different per-HMD or per-eye.
        Setting the bInverse argument to true will produce the visible area mesh that is commonly used in place of full-screen quads. The visible area mesh covers all of the pixels the hidden area mesh does not cover.
        Setting the bLineLoop argument will return a line loop of vertices in HiddenAreaMesh_t->pVertexData with HiddenAreaMesh_t->unTriangleCount set to the number of vertices.
        """
        fn = self.function_table.getHiddenAreaMesh
        result = fn(eye, type_)
        return result

    def getControllerState(self, controllerDeviceIndex):
        """
        Fills the supplied struct with the current state of the controller. Returns false if the controller index
        is invalid. This function is deprecated in favor of the new IVRInput system.
        """
        fn = self.function_table.getControllerState
        controllerState = VRControllerState_t()
        controllerStateSize = sizeof(VRControllerState_t)
        result = fn(controllerDeviceIndex, byref(controllerState), controllerStateSize)
        return result, controllerState

    def getControllerStateWithPose(self, origin, controllerDeviceIndex):
        """
        fills the supplied struct with the current state of the controller and the provided pose with the pose of 
        the controller when the controller state was updated most recently. Use this form if you need a precise controller
        pose as input to your application when the user presses or releases a button. This function is deprecated in favor of the new IVRInput system.
        """
        fn = self.function_table.getControllerStateWithPose
        controllerState = VRControllerState_t()
        controllerStateSize = sizeof(VRControllerState_t)
        trackedDevicePose = TrackedDevicePose_t()
        result = fn(origin, controllerDeviceIndex, byref(controllerState), controllerStateSize, byref(trackedDevicePose))
        return result, controllerState, trackedDevicePose

    def triggerHapticPulse(self, controllerDeviceIndex, axisId, durationMicroSec: int) -> None:
        """
        Trigger a single haptic pulse on a controller. After this call the application may not trigger another haptic pulse on this controller
        and axis combination for 5ms. This function is deprecated in favor of the new IVRInput system.
        """
        fn = self.function_table.triggerHapticPulse
        fn(controllerDeviceIndex, axisId, durationMicroSec)

    def getButtonIdNameFromEnum(self, buttonId):
        """returns the name of an EVRButtonId enum value. This function is deprecated in favor of the new IVRInput system."""
        fn = self.function_table.getButtonIdNameFromEnum
        result = fn(buttonId)
        return result

    def getControllerAxisTypeNameFromEnum(self, axisType):
        """returns the name of an EVRControllerAxisType enum value. This function is deprecated in favor of the new IVRInput system."""
        fn = self.function_table.getControllerAxisTypeNameFromEnum
        result = fn(axisType)
        return result

    def isInputAvailable(self):
        """
        Returns true if this application is receiving input from the system. This would return false if 
        system-related functionality is consuming the input stream.
        """
        fn = self.function_table.isInputAvailable
        result = fn()
        return result

    def isSteamVRDrawingControllers(self):
        """
        Returns true SteamVR is drawing controllers on top of the application. Applications should consider
        not drawing anything attached to the user's hands in this case.
        """
        fn = self.function_table.isSteamVRDrawingControllers
        result = fn()
        return result

    def shouldApplicationPause(self):
        """
        Returns true if the user has put SteamVR into a mode that is distracting them from the application.
        For applications where this is appropriate, the application should pause ongoing activity.
        """
        fn = self.function_table.shouldApplicationPause
        result = fn()
        return result

    def shouldApplicationReduceRenderingWork(self):
        """
        Returns true if SteamVR is doing significant rendering work and the game should do what it can to reduce
        its own workload. One common way to do this is to reduce the size of the render target provided for each eye.
        """
        fn = self.function_table.shouldApplicationReduceRenderingWork
        result = fn()
        return result

    def driverDebugRequest(self, deviceIndex, request: str):
        """
        Sends a request to the driver for the specified device and returns the response. The maximum response size is 32k,
        but this method can be called with a smaller buffer. If the response exceeds the size of the buffer, it is truncated. 
        The size of the response including its terminating null is returned.
        """
        fn = self.function_table.driverDebugRequest
        if request is not None:
            request = bytes(request, encoding='utf-8')
        responseBufferSize = fn(deviceIndex, request, None, 0)
        if responseBufferSize == 0:
            return ''
        responseBuffer = ctypes.create_string_buffer(responseBufferSize)
        fn(deviceIndex, request, responseBuffer, responseBufferSize)
        return bytes(responseBuffer.value).decode('utf-8')

    def performFirmwareUpdate(self, deviceIndex) -> None:
        """
        Performs the actual firmware update if applicable. 
        The following events will be sent, if VRFirmwareError_None was returned: VREvent_FirmwareUpdateStarted, VREvent_FirmwareUpdateFinished 
        Use the properties Prop_Firmware_UpdateAvailable_Bool, Prop_Firmware_ManualUpdate_Bool, and Prop_Firmware_ManualUpdateURL_String
        to figure our whether a firmware update is available, and to figure out whether its a manual update 
        Prop_Firmware_ManualUpdateURL_String should point to an URL describing the manual update process
        """
        fn = self.function_table.performFirmwareUpdate
        error = fn(deviceIndex)
        openvr.error_code.FirmwareError.check_error_value(error)

    def acknowledgeQuit_Exiting(self) -> None:
        """
        Call this to acknowledge to the system that VREvent_Quit has been received and that the process is exiting.
        This extends the timeout until the process is killed.
        """
        fn = self.function_table.acknowledgeQuit_Exiting
        fn()

    def acknowledgeQuit_UserPrompt(self) -> None:
        """
        Call this to tell the system that the user is being prompted to save data. This
        halts the timeout and dismisses the dashboard (if it was up). Applications should be sure to actually 
        prompt the user to save and then exit afterward, otherwise the user will be left in a confusing state.
        """
        fn = self.function_table.acknowledgeQuit_UserPrompt
        fn()


class IVRApplications_FnTable(Structure):
    _fields_ = [
        ("addApplicationManifest", OPENVR_FNTABLE_CALLTYPE(EVRApplicationError, c_char_p, openvr_bool)),
        ("removeApplicationManifest", OPENVR_FNTABLE_CALLTYPE(EVRApplicationError, c_char_p)),
        ("isApplicationInstalled", OPENVR_FNTABLE_CALLTYPE(openvr_bool, c_char_p)),
        ("getApplicationCount", OPENVR_FNTABLE_CALLTYPE(c_uint32)),
        ("getApplicationKeyByIndex", OPENVR_FNTABLE_CALLTYPE(EVRApplicationError, c_uint32, c_char_p, c_uint32)),
        ("getApplicationKeyByProcessId", OPENVR_FNTABLE_CALLTYPE(EVRApplicationError, c_uint32, c_char_p, c_uint32)),
        ("launchApplication", OPENVR_FNTABLE_CALLTYPE(EVRApplicationError, c_char_p)),
        ("launchTemplateApplication", OPENVR_FNTABLE_CALLTYPE(EVRApplicationError, c_char_p, c_char_p, POINTER(AppOverrideKeys_t), c_uint32)),
        ("launchApplicationFromMimeType", OPENVR_FNTABLE_CALLTYPE(EVRApplicationError, c_char_p, c_char_p)),
        ("launchDashboardOverlay", OPENVR_FNTABLE_CALLTYPE(EVRApplicationError, c_char_p)),
        ("cancelApplicationLaunch", OPENVR_FNTABLE_CALLTYPE(openvr_bool, c_char_p)),
        ("identifyApplication", OPENVR_FNTABLE_CALLTYPE(EVRApplicationError, c_uint32, c_char_p)),
        ("getApplicationProcessId", OPENVR_FNTABLE_CALLTYPE(c_uint32, c_char_p)),
        ("getApplicationsErrorNameFromEnum", OPENVR_FNTABLE_CALLTYPE(c_char_p, EVRApplicationError)),
        ("getApplicationPropertyString", OPENVR_FNTABLE_CALLTYPE(c_uint32, c_char_p, EVRApplicationProperty, c_char_p, c_uint32, POINTER(EVRApplicationError))),
        ("getApplicationPropertyBool", OPENVR_FNTABLE_CALLTYPE(openvr_bool, c_char_p, EVRApplicationProperty, POINTER(EVRApplicationError))),
        ("getApplicationPropertyUint64", OPENVR_FNTABLE_CALLTYPE(c_uint64, c_char_p, EVRApplicationProperty, POINTER(EVRApplicationError))),
        ("setApplicationAutoLaunch", OPENVR_FNTABLE_CALLTYPE(EVRApplicationError, c_char_p, openvr_bool)),
        ("getApplicationAutoLaunch", OPENVR_FNTABLE_CALLTYPE(openvr_bool, c_char_p)),
        ("setDefaultApplicationForMimeType", OPENVR_FNTABLE_CALLTYPE(EVRApplicationError, c_char_p, c_char_p)),
        ("getDefaultApplicationForMimeType", OPENVR_FNTABLE_CALLTYPE(openvr_bool, c_char_p, c_char_p, c_uint32)),
        ("getApplicationSupportedMimeTypes", OPENVR_FNTABLE_CALLTYPE(openvr_bool, c_char_p, c_char_p, c_uint32)),
        ("getApplicationsThatSupportMimeType", OPENVR_FNTABLE_CALLTYPE(c_uint32, c_char_p, c_char_p, c_uint32)),
        ("getApplicationLaunchArguments", OPENVR_FNTABLE_CALLTYPE(c_uint32, c_uint32, c_char_p, c_uint32)),
        ("getStartingApplication", OPENVR_FNTABLE_CALLTYPE(EVRApplicationError, c_char_p, c_uint32)),
        ("getTransitionState", OPENVR_FNTABLE_CALLTYPE(EVRApplicationTransitionState)),
        ("performApplicationPrelaunchCheck", OPENVR_FNTABLE_CALLTYPE(EVRApplicationError, c_char_p)),
        ("getApplicationsTransitionStateNameFromEnum", OPENVR_FNTABLE_CALLTYPE(c_char_p, EVRApplicationTransitionState)),
        ("isQuitUserPromptRequested", OPENVR_FNTABLE_CALLTYPE(openvr_bool)),
        ("launchInternalProcess", OPENVR_FNTABLE_CALLTYPE(EVRApplicationError, c_char_p, c_char_p, c_char_p)),
        ("getCurrentSceneProcessId", OPENVR_FNTABLE_CALLTYPE(c_uint32)),
    ]


class IVRApplications(object):
    def __init__(self):
        version_key = IVRApplications_Version
        if not isInterfaceVersionValid(version_key):
            _checkInitError(VRInitError_Init_InterfaceNotFound)
        fn_key = 'FnTable:' + version_key
        fn_type = IVRApplications_FnTable
        fn_table_ptr = cast(getGenericInterface(fn_key), POINTER(fn_type))
        if fn_table_ptr is None:
            raise OpenVRError("Error retrieving VR API for IVRApplications")
        self.function_table = fn_table_ptr.contents

    def addApplicationManifest(self, applicationManifestFullPath: str, temporary=False) -> None:
        """
        Adds an application manifest to the list to load when building the list of installed applications. 
        Temporary manifests are not automatically loaded
        """
        fn = self.function_table.addApplicationManifest
        if applicationManifestFullPath is not None:
            applicationManifestFullPath = bytes(applicationManifestFullPath, encoding='utf-8')
        error = fn(applicationManifestFullPath, temporary)
        openvr.error_code.ApplicationError.check_error_value(error)

    def removeApplicationManifest(self, applicationManifestFullPath: str) -> None:
        """Removes an application manifest from the list to load when building the list of installed applications."""
        fn = self.function_table.removeApplicationManifest
        if applicationManifestFullPath is not None:
            applicationManifestFullPath = bytes(applicationManifestFullPath, encoding='utf-8')
        error = fn(applicationManifestFullPath)
        openvr.error_code.ApplicationError.check_error_value(error)

    def isApplicationInstalled(self, appKey: str):
        """Returns true if an application is installed"""
        fn = self.function_table.isApplicationInstalled
        if appKey is not None:
            appKey = bytes(appKey, encoding='utf-8')
        result = fn(appKey)
        return result

    def getApplicationCount(self):
        """Returns the number of applications available in the list"""
        fn = self.function_table.getApplicationCount
        result = fn()
        return result

    def getApplicationKeyByIndex(self, applicationIndex):
        """
        Returns the key of the specified application. The index is at least 0 and is less than the return 
        value of GetApplicationCount(). The buffer should be at least k_unMaxApplicationKeyLength in order to 
        fit the key.
        """
        fn = self.function_table.getApplicationKeyByIndex
        appKeyBufferLen = fn(applicationIndex, None, 0)
        if appKeyBufferLen == 0:
            return ''
        appKeyBuffer = ctypes.create_string_buffer(appKeyBufferLen)
        error = fn(applicationIndex, appKeyBuffer, appKeyBufferLen)
        openvr.error_code.ApplicationError.check_error_value(error)
        return bytes(appKeyBuffer.value).decode('utf-8')

    def getApplicationKeyByProcessId(self, processId):
        """
        Returns the key of the application for the specified Process Id. The buffer should be at least 
        k_unMaxApplicationKeyLength in order to fit the key.
        """
        fn = self.function_table.getApplicationKeyByProcessId
        appKeyBufferLen = fn(processId, None, 0)
        if appKeyBufferLen == 0:
            return ''
        appKeyBuffer = ctypes.create_string_buffer(appKeyBufferLen)
        error = fn(processId, appKeyBuffer, appKeyBufferLen)
        openvr.error_code.ApplicationError.check_error_value(error)
        return bytes(appKeyBuffer.value).decode('utf-8')

    def launchApplication(self, appKey: str) -> None:
        """
        Launches the application. The existing scene application will exit and then the new application will start.
        This call is not valid for dashboard overlay applications.
        """
        fn = self.function_table.launchApplication
        if appKey is not None:
            appKey = bytes(appKey, encoding='utf-8')
        error = fn(appKey)
        openvr.error_code.ApplicationError.check_error_value(error)

    def launchTemplateApplication(self, templateAppKey: str, newAppKey: str, keys) -> None:
        """
        Launches an instance of an application of type template, with its app key being pchNewAppKey (which must be unique) and optionally override sections
        from the manifest file via AppOverrideKeys_t
        """
        fn = self.function_table.launchTemplateApplication
        if templateAppKey is not None:
            templateAppKey = bytes(templateAppKey, encoding='utf-8')
        if newAppKey is not None:
            newAppKey = bytes(newAppKey, encoding='utf-8')
        if keys is None:
            keys = 0
            keysArg = None
        elif isinstance(keys, ctypes.Array):
            keys = len(keys)
            keysArg = byref(keys[0])
        else:
            keys = 1
            keys = (AppOverrideKeys_t * keys)()
            keysArg = byref(keys[0])
        error = fn(templateAppKey, newAppKey, keysArg, keys)
        openvr.error_code.ApplicationError.check_error_value(error)

    def launchApplicationFromMimeType(self, mimeType: str, args: str) -> None:
        """launches the application currently associated with this mime type and passes it the option args, typically the filename or object name of the item being launched"""
        fn = self.function_table.launchApplicationFromMimeType
        if mimeType is not None:
            mimeType = bytes(mimeType, encoding='utf-8')
        if args is not None:
            args = bytes(args, encoding='utf-8')
        error = fn(mimeType, args)
        openvr.error_code.ApplicationError.check_error_value(error)

    def launchDashboardOverlay(self, appKey: str) -> None:
        """
        Launches the dashboard overlay application if it is not already running. This call is only valid for 
        dashboard overlay applications.
        """
        fn = self.function_table.launchDashboardOverlay
        if appKey is not None:
            appKey = bytes(appKey, encoding='utf-8')
        error = fn(appKey)
        openvr.error_code.ApplicationError.check_error_value(error)

    def cancelApplicationLaunch(self, appKey: str):
        """Cancel a pending launch for an application"""
        fn = self.function_table.cancelApplicationLaunch
        if appKey is not None:
            appKey = bytes(appKey, encoding='utf-8')
        result = fn(appKey)
        return result

    def identifyApplication(self, processId, appKey: str) -> None:
        """
        Identifies a running application. OpenVR can't always tell which process started in response
        to a URL. This function allows a URL handler (or the process itself) to identify the app key 
        for the now running application. Passing a process ID of 0 identifies the calling process. 
        The application must be one that's known to the system via a call to AddApplicationManifest.
        """
        fn = self.function_table.identifyApplication
        if appKey is not None:
            appKey = bytes(appKey, encoding='utf-8')
        error = fn(processId, appKey)
        openvr.error_code.ApplicationError.check_error_value(error)

    def getApplicationProcessId(self, appKey: str):
        """Returns the process ID for an application. Return 0 if the application was not found or is not running."""
        fn = self.function_table.getApplicationProcessId
        if appKey is not None:
            appKey = bytes(appKey, encoding='utf-8')
        result = fn(appKey)
        return result

    def getApplicationsErrorNameFromEnum(self, error):
        """Returns a string for an applications error"""
        fn = self.function_table.getApplicationsErrorNameFromEnum
        result = fn(error)
        return result

    def getApplicationPropertyString(self, appKey: str, property_):
        """Returns a value for an application property. The required buffer size to fit this value will be returned."""
        fn = self.function_table.getApplicationPropertyString
        if appKey is not None:
            appKey = bytes(appKey, encoding='utf-8')
        error = EVRApplicationError()
        propertyValueBufferLen = fn(appKey, property_, None, 0, byref(error))
        if propertyValueBufferLen == 0:
            return ''
        propertyValueBuffer = ctypes.create_string_buffer(propertyValueBufferLen)
        fn(appKey, property_, propertyValueBuffer, propertyValueBufferLen, byref(error))
        openvr.error_code.ApplicationError.check_error_value(error.value)
        return bytes(propertyValueBuffer.value).decode('utf-8')

    def getApplicationPropertyBool(self, appKey: str, property_):
        """Returns a bool value for an application property. Returns false in all error cases."""
        fn = self.function_table.getApplicationPropertyBool
        if appKey is not None:
            appKey = bytes(appKey, encoding='utf-8')
        error = EVRApplicationError()
        result = fn(appKey, property_, byref(error))
        openvr.error_code.ApplicationError.check_error_value(error.value)
        return result

    def getApplicationPropertyUint64(self, appKey: str, property_):
        """Returns a uint64 value for an application property. Returns 0 in all error cases."""
        fn = self.function_table.getApplicationPropertyUint64
        if appKey is not None:
            appKey = bytes(appKey, encoding='utf-8')
        error = EVRApplicationError()
        result = fn(appKey, property_, byref(error))
        openvr.error_code.ApplicationError.check_error_value(error.value)
        return result

    def setApplicationAutoLaunch(self, appKey: str, autoLaunch) -> None:
        """Sets the application auto-launch flag. This is only valid for applications which return true for VRApplicationProperty_IsDashboardOverlay_Bool."""
        fn = self.function_table.setApplicationAutoLaunch
        if appKey is not None:
            appKey = bytes(appKey, encoding='utf-8')
        error = fn(appKey, autoLaunch)
        openvr.error_code.ApplicationError.check_error_value(error)

    def getApplicationAutoLaunch(self, appKey: str):
        """Gets the application auto-launch flag. This is only valid for applications which return true for VRApplicationProperty_IsDashboardOverlay_Bool."""
        fn = self.function_table.getApplicationAutoLaunch
        if appKey is not None:
            appKey = bytes(appKey, encoding='utf-8')
        result = fn(appKey)
        return result

    def setDefaultApplicationForMimeType(self, appKey: str, mimeType: str) -> None:
        """Adds this mime-type to the list of supported mime types for this application"""
        fn = self.function_table.setDefaultApplicationForMimeType
        if appKey is not None:
            appKey = bytes(appKey, encoding='utf-8')
        if mimeType is not None:
            mimeType = bytes(mimeType, encoding='utf-8')
        error = fn(appKey, mimeType)
        openvr.error_code.ApplicationError.check_error_value(error)

    def getDefaultApplicationForMimeType(self, mimeType: str):
        """return the app key that will open this mime type"""
        fn = self.function_table.getDefaultApplicationForMimeType
        if mimeType is not None:
            mimeType = bytes(mimeType, encoding='utf-8')
        appKeyBufferLen = fn(mimeType, None, 0)
        if appKeyBufferLen == 0:
            return ''
        appKeyBuffer = ctypes.create_string_buffer(appKeyBufferLen)
        fn(mimeType, appKeyBuffer, appKeyBufferLen)
        return bytes(appKeyBuffer.value).decode('utf-8')

    def getApplicationSupportedMimeTypes(self, appKey: str):
        """Get the list of supported mime types for this application, comma-delimited"""
        fn = self.function_table.getApplicationSupportedMimeTypes
        if appKey is not None:
            appKey = bytes(appKey, encoding='utf-8')
        mimeTypesBuffer = fn(appKey, None, 0)
        if mimeTypesBuffer == 0:
            return ''
        mimeTypesBuffer = ctypes.create_string_buffer(mimeTypesBuffer)
        fn(appKey, mimeTypesBuffer, mimeTypesBuffer)
        return bytes(mimeTypesBuffer.value).decode('utf-8')

    def getApplicationsThatSupportMimeType(self, mimeType: str):
        """Get the list of app-keys that support this mime type, comma-delimited, the return value is number of bytes you need to return the full string"""
        fn = self.function_table.getApplicationsThatSupportMimeType
        if mimeType is not None:
            mimeType = bytes(mimeType, encoding='utf-8')
        appKeysThatSupportBuffer = fn(mimeType, None, 0)
        if appKeysThatSupportBuffer == 0:
            return ''
        appKeysThatSupportBuffer = ctypes.create_string_buffer(appKeysThatSupportBuffer)
        fn(mimeType, appKeysThatSupportBuffer, appKeysThatSupportBuffer)
        return bytes(appKeysThatSupportBuffer.value).decode('utf-8')

    def getApplicationLaunchArguments(self, handle):
        """Get the args list from an app launch that had the process already running, you call this when you get a VREvent_ApplicationMimeTypeLoad"""
        fn = self.function_table.getApplicationLaunchArguments
        args = fn(handle, None, 0)
        if args == 0:
            return ''
        args = ctypes.create_string_buffer(args)
        fn(handle, args, args)
        return bytes(args.value).decode('utf-8')

    def getStartingApplication(self):
        """Returns the app key for the application that is starting up"""
        fn = self.function_table.getStartingApplication
        appKeyBufferLen = fn(None, 0)
        if appKeyBufferLen == 0:
            return ''
        appKeyBuffer = ctypes.create_string_buffer(appKeyBufferLen)
        error = fn(appKeyBuffer, appKeyBufferLen)
        openvr.error_code.ApplicationError.check_error_value(error)
        return bytes(appKeyBuffer.value).decode('utf-8')

    def getTransitionState(self):
        """Returns the application transition state"""
        fn = self.function_table.getTransitionState
        result = fn()
        return result

    def performApplicationPrelaunchCheck(self, appKey: str) -> None:
        """
        Returns errors that would prevent the specified application from launching immediately. Calling this function will
        cause the current scene application to quit, so only call it when you are actually about to launch something else.
        What the caller should do about these failures depends on the failure:
          VRApplicationError_OldApplicationQuitting - An existing application has been told to quit. Wait for a VREvent_ProcessQuit
                                                      and try again.
          VRApplicationError_ApplicationAlreadyStarting - This application is already starting. This is a permanent failure.
          VRApplicationError_LaunchInProgress         - A different application is already starting. This is a permanent failure.
          VRApplicationError_None                   - Go ahead and launch. Everything is clear.
        """
        fn = self.function_table.performApplicationPrelaunchCheck
        if appKey is not None:
            appKey = bytes(appKey, encoding='utf-8')
        error = fn(appKey)
        openvr.error_code.ApplicationError.check_error_value(error)

    def getApplicationsTransitionStateNameFromEnum(self, state):
        """Returns a string for an application transition state"""
        fn = self.function_table.getApplicationsTransitionStateNameFromEnum
        result = fn(state)
        return result

    def isQuitUserPromptRequested(self):
        """Returns true if the outgoing scene app has requested a save prompt before exiting"""
        fn = self.function_table.isQuitUserPromptRequested
        result = fn()
        return result

    def launchInternalProcess(self, binaryPath: str, arguments: str, workingDirectory: str) -> None:
        """
        Starts a subprocess within the calling application. This
        suppresses all application transition UI and automatically identifies the new executable 
        as part of the same application. On success the calling process should exit immediately. 
        If working directory is NULL or "" the directory portion of the binary path will be 
        the working directory.
        """
        fn = self.function_table.launchInternalProcess
        if binaryPath is not None:
            binaryPath = bytes(binaryPath, encoding='utf-8')
        if arguments is not None:
            arguments = bytes(arguments, encoding='utf-8')
        if workingDirectory is not None:
            workingDirectory = bytes(workingDirectory, encoding='utf-8')
        error = fn(binaryPath, arguments, workingDirectory)
        openvr.error_code.ApplicationError.check_error_value(error)

    def getCurrentSceneProcessId(self):
        """
        Returns the current scene process ID according to the application system. A scene process will get scene
        focus once it starts rendering, but it will appear here once it calls VR_Init with the Scene application
        type.
        """
        fn = self.function_table.getCurrentSceneProcessId
        result = fn()
        return result


class IVRSettings_FnTable(Structure):
    _fields_ = [
        ("getSettingsErrorNameFromEnum", OPENVR_FNTABLE_CALLTYPE(c_char_p, EVRSettingsError)),
        ("sync", OPENVR_FNTABLE_CALLTYPE(openvr_bool, openvr_bool, POINTER(EVRSettingsError))),
        ("setBool", OPENVR_FNTABLE_CALLTYPE(None, c_char_p, c_char_p, openvr_bool, POINTER(EVRSettingsError))),
        ("setInt32", OPENVR_FNTABLE_CALLTYPE(None, c_char_p, c_char_p, c_int32, POINTER(EVRSettingsError))),
        ("setFloat", OPENVR_FNTABLE_CALLTYPE(None, c_char_p, c_char_p, c_float, POINTER(EVRSettingsError))),
        ("setString", OPENVR_FNTABLE_CALLTYPE(None, c_char_p, c_char_p, c_char_p, POINTER(EVRSettingsError))),
        ("getBool", OPENVR_FNTABLE_CALLTYPE(openvr_bool, c_char_p, c_char_p, POINTER(EVRSettingsError))),
        ("getInt32", OPENVR_FNTABLE_CALLTYPE(c_int32, c_char_p, c_char_p, POINTER(EVRSettingsError))),
        ("getFloat", OPENVR_FNTABLE_CALLTYPE(c_float, c_char_p, c_char_p, POINTER(EVRSettingsError))),
        ("getString", OPENVR_FNTABLE_CALLTYPE(None, c_char_p, c_char_p, c_char_p, c_uint32, POINTER(EVRSettingsError))),
        ("removeSection", OPENVR_FNTABLE_CALLTYPE(None, c_char_p, POINTER(EVRSettingsError))),
        ("removeKeyInSection", OPENVR_FNTABLE_CALLTYPE(None, c_char_p, c_char_p, POINTER(EVRSettingsError))),
    ]


class IVRSettings(object):
    def __init__(self):
        version_key = IVRSettings_Version
        if not isInterfaceVersionValid(version_key):
            _checkInitError(VRInitError_Init_InterfaceNotFound)
        fn_key = 'FnTable:' + version_key
        fn_type = IVRSettings_FnTable
        fn_table_ptr = cast(getGenericInterface(fn_key), POINTER(fn_type))
        if fn_table_ptr is None:
            raise OpenVRError("Error retrieving VR API for IVRSettings")
        self.function_table = fn_table_ptr.contents

    def getSettingsErrorNameFromEnum(self, error):
        fn = self.function_table.getSettingsErrorNameFromEnum
        result = fn(error)
        return result

    def sync(self, force=False):
        """Returns true if file sync occurred (force or settings dirty)"""
        fn = self.function_table.sync
        error = EVRSettingsError()
        result = fn(force, byref(error))
        openvr.error_code.SettingsError.check_error_value(error.value)
        return result

    def setBool(self, section: str, settingsKey: str, value) -> None:
        fn = self.function_table.setBool
        if section is not None:
            section = bytes(section, encoding='utf-8')
        if settingsKey is not None:
            settingsKey = bytes(settingsKey, encoding='utf-8')
        error = EVRSettingsError()
        fn(section, settingsKey, value, byref(error))
        openvr.error_code.SettingsError.check_error_value(error.value)

    def setInt32(self, section: str, settingsKey: str, value) -> None:
        fn = self.function_table.setInt32
        if section is not None:
            section = bytes(section, encoding='utf-8')
        if settingsKey is not None:
            settingsKey = bytes(settingsKey, encoding='utf-8')
        error = EVRSettingsError()
        fn(section, settingsKey, value, byref(error))
        openvr.error_code.SettingsError.check_error_value(error.value)

    def setFloat(self, section: str, settingsKey: str, value: float) -> None:
        fn = self.function_table.setFloat
        if section is not None:
            section = bytes(section, encoding='utf-8')
        if settingsKey is not None:
            settingsKey = bytes(settingsKey, encoding='utf-8')
        error = EVRSettingsError()
        fn(section, settingsKey, value, byref(error))
        openvr.error_code.SettingsError.check_error_value(error.value)

    def setString(self, section: str, settingsKey: str, value: str) -> None:
        fn = self.function_table.setString
        if section is not None:
            section = bytes(section, encoding='utf-8')
        if settingsKey is not None:
            settingsKey = bytes(settingsKey, encoding='utf-8')
        if value is not None:
            value = bytes(value, encoding='utf-8')
        error = EVRSettingsError()
        fn(section, settingsKey, value, byref(error))
        openvr.error_code.SettingsError.check_error_value(error.value)

    def getBool(self, section: str, settingsKey: str):
        """
        Users of the system need to provide a proper default in default.vrsettings in the resources/settings/ directory
        of either the runtime or the driver_xxx directory. Otherwise the default will be false, 0, 0.0 or ""
        """
        fn = self.function_table.getBool
        if section is not None:
            section = bytes(section, encoding='utf-8')
        if settingsKey is not None:
            settingsKey = bytes(settingsKey, encoding='utf-8')
        error = EVRSettingsError()
        result = fn(section, settingsKey, byref(error))
        openvr.error_code.SettingsError.check_error_value(error.value)
        return result

    def getInt32(self, section: str, settingsKey: str):
        fn = self.function_table.getInt32
        if section is not None:
            section = bytes(section, encoding='utf-8')
        if settingsKey is not None:
            settingsKey = bytes(settingsKey, encoding='utf-8')
        error = EVRSettingsError()
        result = fn(section, settingsKey, byref(error))
        openvr.error_code.SettingsError.check_error_value(error.value)
        return result

    def getFloat(self, section: str, settingsKey: str):
        fn = self.function_table.getFloat
        if section is not None:
            section = bytes(section, encoding='utf-8')
        if settingsKey is not None:
            settingsKey = bytes(settingsKey, encoding='utf-8')
        error = EVRSettingsError()
        result = fn(section, settingsKey, byref(error))
        openvr.error_code.SettingsError.check_error_value(error.value)
        return result

    def getString(self, section: str, settingsKey: str):
        fn = self.function_table.getString
        if section is not None:
            section = bytes(section, encoding='utf-8')
        if settingsKey is not None:
            settingsKey = bytes(settingsKey, encoding='utf-8')
        error = EVRSettingsError()
        valueLen = fn(section, settingsKey, None, 0, byref(error))
        if valueLen == 0:
            return ''
        value = ctypes.create_string_buffer(valueLen)
        fn(section, settingsKey, value, valueLen, byref(error))
        openvr.error_code.SettingsError.check_error_value(error.value)
        return bytes(value.value).decode('utf-8')

    def removeSection(self, section: str) -> None:
        fn = self.function_table.removeSection
        if section is not None:
            section = bytes(section, encoding='utf-8')
        error = EVRSettingsError()
        fn(section, byref(error))
        openvr.error_code.SettingsError.check_error_value(error.value)

    def removeKeyInSection(self, section: str, settingsKey: str) -> None:
        fn = self.function_table.removeKeyInSection
        if section is not None:
            section = bytes(section, encoding='utf-8')
        if settingsKey is not None:
            settingsKey = bytes(settingsKey, encoding='utf-8')
        error = EVRSettingsError()
        fn(section, settingsKey, byref(error))
        openvr.error_code.SettingsError.check_error_value(error.value)


class IVRChaperone_FnTable(Structure):
    _fields_ = [
        ("getCalibrationState", OPENVR_FNTABLE_CALLTYPE(ChaperoneCalibrationState)),
        ("getPlayAreaSize", OPENVR_FNTABLE_CALLTYPE(openvr_bool, POINTER(c_float), POINTER(c_float))),
        ("getPlayAreaRect", OPENVR_FNTABLE_CALLTYPE(openvr_bool, POINTER(HmdQuad_t))),
        ("reloadInfo", OPENVR_FNTABLE_CALLTYPE(None)),
        ("setSceneColor", OPENVR_FNTABLE_CALLTYPE(None, HmdColor_t)),
        ("getBoundsColor", OPENVR_FNTABLE_CALLTYPE(None, POINTER(HmdColor_t), c_int, c_float, POINTER(HmdColor_t))),
        ("areBoundsVisible", OPENVR_FNTABLE_CALLTYPE(openvr_bool)),
        ("forceBoundsVisible", OPENVR_FNTABLE_CALLTYPE(None, openvr_bool)),
    ]


class IVRChaperone(object):
    """
    HIGH LEVEL TRACKING SPACE ASSUMPTIONS:
    0,0,0 is the preferred standing area center.
    0Y is the floor height.
    -Z is the preferred forward facing direction.
    """

    def __init__(self):
        version_key = IVRChaperone_Version
        if not isInterfaceVersionValid(version_key):
            _checkInitError(VRInitError_Init_InterfaceNotFound)
        fn_key = 'FnTable:' + version_key
        fn_type = IVRChaperone_FnTable
        fn_table_ptr = cast(getGenericInterface(fn_key), POINTER(fn_type))
        if fn_table_ptr is None:
            raise OpenVRError("Error retrieving VR API for IVRChaperone")
        self.function_table = fn_table_ptr.contents

    def getCalibrationState(self):
        """Get the current state of Chaperone calibration. This state can change at any time during a session due to physical base station changes."""
        fn = self.function_table.getCalibrationState
        result = fn()
        return result

    def getPlayAreaSize(self):
        """
        Returns the width and depth of the Play Area (formerly named Soft Bounds) in X and Z. 
        Tracking space center (0,0,0) is the center of the Play Area.
        """
        fn = self.function_table.getPlayAreaSize
        sizeX = c_float()
        sizeZ = c_float()
        result = fn(byref(sizeX), byref(sizeZ))
        return result, sizeX.value, sizeZ.value

    def getPlayAreaRect(self):
        """
        Returns the 4 corner positions of the Play Area (formerly named Soft Bounds).
        Corners are in counter-clockwise order.
        Standing center (0,0,0) is the center of the Play Area.
        It's a rectangle.
        2 sides are parallel to the X axis and 2 sides are parallel to the Z axis.
        Height of every corner is 0Y (on the floor).
        """
        fn = self.function_table.getPlayAreaRect
        rect = HmdQuad_t()
        result = fn(byref(rect))
        return result, rect

    def reloadInfo(self) -> None:
        """Reload Chaperone data from the .vrchap file on disk."""
        fn = self.function_table.reloadInfo
        fn()

    def setSceneColor(self, color) -> None:
        """Optionally give the chaperone system a hit about the color and brightness in the scene"""
        fn = self.function_table.setSceneColor
        fn(color)

    def getBoundsColor(self, numOutputColors: int, collisionBoundsFadeDistance: float):
        """Get the current chaperone bounds draw color and brightness"""
        fn = self.function_table.getBoundsColor
        outputColorArray = HmdColor_t()
        outputCameraColor = HmdColor_t()
        fn(byref(outputColorArray), numOutputColors, collisionBoundsFadeDistance, byref(outputCameraColor))
        return outputColorArray, outputCameraColor

    def areBoundsVisible(self):
        """Determine whether the bounds are showing right now"""
        fn = self.function_table.areBoundsVisible
        result = fn()
        return result

    def forceBoundsVisible(self, force) -> None:
        """Force the bounds to show, mostly for utilities"""
        fn = self.function_table.forceBoundsVisible
        fn(force)


class IVRChaperoneSetup_FnTable(Structure):
    _fields_ = [
        ("commitWorkingCopy", OPENVR_FNTABLE_CALLTYPE(openvr_bool, EChaperoneConfigFile)),
        ("revertWorkingCopy", OPENVR_FNTABLE_CALLTYPE(None)),
        ("getWorkingPlayAreaSize", OPENVR_FNTABLE_CALLTYPE(openvr_bool, POINTER(c_float), POINTER(c_float))),
        ("getWorkingPlayAreaRect", OPENVR_FNTABLE_CALLTYPE(openvr_bool, POINTER(HmdQuad_t))),
        ("getWorkingCollisionBoundsInfo", OPENVR_FNTABLE_CALLTYPE(openvr_bool, POINTER(HmdQuad_t), POINTER(c_uint32))),
        ("getLiveCollisionBoundsInfo", OPENVR_FNTABLE_CALLTYPE(openvr_bool, POINTER(HmdQuad_t), POINTER(c_uint32))),
        ("getWorkingSeatedZeroPoseToRawTrackingPose", OPENVR_FNTABLE_CALLTYPE(openvr_bool, POINTER(HmdMatrix34_t))),
        ("getWorkingStandingZeroPoseToRawTrackingPose", OPENVR_FNTABLE_CALLTYPE(openvr_bool, POINTER(HmdMatrix34_t))),
        ("setWorkingPlayAreaSize", OPENVR_FNTABLE_CALLTYPE(None, c_float, c_float)),
        ("setWorkingCollisionBoundsInfo", OPENVR_FNTABLE_CALLTYPE(None, POINTER(HmdQuad_t), c_uint32)),
        ("setWorkingPerimeter", OPENVR_FNTABLE_CALLTYPE(None, POINTER(HmdVector2_t), c_uint32)),
        ("setWorkingSeatedZeroPoseToRawTrackingPose", OPENVR_FNTABLE_CALLTYPE(None, POINTER(HmdMatrix34_t))),
        ("setWorkingStandingZeroPoseToRawTrackingPose", OPENVR_FNTABLE_CALLTYPE(None, POINTER(HmdMatrix34_t))),
        ("reloadFromDisk", OPENVR_FNTABLE_CALLTYPE(None, EChaperoneConfigFile)),
        ("getLiveSeatedZeroPoseToRawTrackingPose", OPENVR_FNTABLE_CALLTYPE(openvr_bool, POINTER(HmdMatrix34_t))),
        ("exportLiveToBuffer", OPENVR_FNTABLE_CALLTYPE(openvr_bool, c_char_p, POINTER(c_uint32))),
        ("importFromBufferToWorking", OPENVR_FNTABLE_CALLTYPE(openvr_bool, c_char_p, c_uint32)),
        ("showWorkingSetPreview", OPENVR_FNTABLE_CALLTYPE(None)),
        ("hideWorkingSetPreview", OPENVR_FNTABLE_CALLTYPE(None)),
        ("roomSetupStarting", OPENVR_FNTABLE_CALLTYPE(None)),
    ]


class IVRChaperoneSetup(object):
    """
    Manages the working copy of the chaperone info. By default this will be the same as the 
    live copy. Any changes made with this interface will stay in the working copy until 
    CommitWorkingCopy() is called, at which point the working copy and the live copy will be 
    the same again.
    """

    def __init__(self):
        version_key = IVRChaperoneSetup_Version
        if not isInterfaceVersionValid(version_key):
            _checkInitError(VRInitError_Init_InterfaceNotFound)
        fn_key = 'FnTable:' + version_key
        fn_type = IVRChaperoneSetup_FnTable
        fn_table_ptr = cast(getGenericInterface(fn_key), POINTER(fn_type))
        if fn_table_ptr is None:
            raise OpenVRError("Error retrieving VR API for IVRChaperoneSetup")
        self.function_table = fn_table_ptr.contents

    def commitWorkingCopy(self, configFile):
        """Saves the current working copy to disk"""
        fn = self.function_table.commitWorkingCopy
        result = fn(configFile)
        return result

    def revertWorkingCopy(self) -> None:
        """
        Reverts the working copy to match the live chaperone calibration.
        To modify existing data this MUST be do WHILE getting a non-error ChaperoneCalibrationStatus.
        Only after this should you do gets and sets on the existing data.
        """
        fn = self.function_table.revertWorkingCopy
        fn()

    def getWorkingPlayAreaSize(self):
        """
        Returns the width and depth of the Play Area (formerly named Soft Bounds) in X and Z from the working copy.
        Tracking space center (0,0,0) is the center of the Play Area.
        """
        fn = self.function_table.getWorkingPlayAreaSize
        sizeX = c_float()
        sizeZ = c_float()
        result = fn(byref(sizeX), byref(sizeZ))
        return result, sizeX.value, sizeZ.value

    def getWorkingPlayAreaRect(self):
        """
        Returns the 4 corner positions of the Play Area (formerly named Soft Bounds) from the working copy.
        Corners are in clockwise order.
        Tracking space center (0,0,0) is the center of the Play Area.
        It's a rectangle.
        2 sides are parallel to the X axis and 2 sides are parallel to the Z axis.
        Height of every corner is 0Y (on the floor).
        """
        fn = self.function_table.getWorkingPlayAreaRect
        rect = HmdQuad_t()
        result = fn(byref(rect))
        return result, rect

    def getWorkingCollisionBoundsInfo(self):
        """
        Returns the number of Quads if the buffer points to null. Otherwise it returns Quads 
        into the buffer up to the max specified from the working copy.
        """
        fn = self.function_table.getWorkingCollisionBoundsInfo
        quadsBuffer = HmdQuad_t()
        quadsCount = c_uint32()
        result = fn(byref(quadsBuffer), byref(quadsCount))
        return result, quadsBuffer, quadsCount.value

    def getLiveCollisionBoundsInfo(self):
        """
        Returns the number of Quads if the buffer points to null. Otherwise it returns Quads 
        into the buffer up to the max specified.
        """
        fn = self.function_table.getLiveCollisionBoundsInfo
        quadsBuffer = HmdQuad_t()
        quadsCount = c_uint32()
        result = fn(byref(quadsBuffer), byref(quadsCount))
        return result, quadsBuffer, quadsCount.value

    def getWorkingSeatedZeroPoseToRawTrackingPose(self):
        """Returns the preferred seated position from the working copy."""
        fn = self.function_table.getWorkingSeatedZeroPoseToRawTrackingPose
        seatedZeroPoseToRawTrackingPose = HmdMatrix34_t()
        result = fn(byref(seatedZeroPoseToRawTrackingPose))
        return result, seatedZeroPoseToRawTrackingPose

    def getWorkingStandingZeroPoseToRawTrackingPose(self):
        """Returns the standing origin from the working copy."""
        fn = self.function_table.getWorkingStandingZeroPoseToRawTrackingPose
        standingZeroPoseToRawTrackingPose = HmdMatrix34_t()
        result = fn(byref(standingZeroPoseToRawTrackingPose))
        return result, standingZeroPoseToRawTrackingPose

    def setWorkingPlayAreaSize(self, x: float, z: float) -> None:
        """Sets the Play Area in the working copy."""
        fn = self.function_table.setWorkingPlayAreaSize
        fn(x, z)

    def setWorkingCollisionBoundsInfo(self, quadsBuffer):
        """Sets the Collision Bounds in the working copy."""
        fn = self.function_table.setWorkingCollisionBoundsInfo
        if quadsBuffer is None:
            quadsCount = 0
            quadsBufferArg = None
        elif isinstance(quadsBuffer, ctypes.Array):
            quadsCount = len(quadsBuffer)
            quadsBufferArg = byref(quadsBuffer[0])
        else:
            quadsCount = 1
            quadsBuffer = (HmdQuad_t * quadsCount)()
            quadsBufferArg = byref(quadsBuffer[0])
        fn(quadsBufferArg, quadsCount)
        return quadsBuffer

    def setWorkingPerimeter(self, pointBuffer):
        """Sets the Collision Bounds in the working copy."""
        fn = self.function_table.setWorkingPerimeter
        if pointBuffer is None:
            pointCount = 0
            pointBufferArg = None
        elif isinstance(pointBuffer, ctypes.Array):
            pointCount = len(pointBuffer)
            pointBufferArg = byref(pointBuffer[0])
        else:
            pointCount = 1
            pointBuffer = (HmdVector2_t * pointCount)()
            pointBufferArg = byref(pointBuffer[0])
        fn(pointBufferArg, pointCount)
        return pointBuffer

    def setWorkingSeatedZeroPoseToRawTrackingPose(self, matSeatedZeroPoseToRawTrackingPose) -> None:
        """Sets the preferred seated position in the working copy."""
        fn = self.function_table.setWorkingSeatedZeroPoseToRawTrackingPose
        fn(byref(matSeatedZeroPoseToRawTrackingPose))

    def setWorkingStandingZeroPoseToRawTrackingPose(self, matStandingZeroPoseToRawTrackingPose) -> None:
        """Sets the preferred standing position in the working copy."""
        fn = self.function_table.setWorkingStandingZeroPoseToRawTrackingPose
        fn(byref(matStandingZeroPoseToRawTrackingPose))

    def reloadFromDisk(self, configFile) -> None:
        """Tear everything down and reload it from the file on disk"""
        fn = self.function_table.reloadFromDisk
        fn(configFile)

    def getLiveSeatedZeroPoseToRawTrackingPose(self):
        """Returns the preferred seated position."""
        fn = self.function_table.getLiveSeatedZeroPoseToRawTrackingPose
        seatedZeroPoseToRawTrackingPose = HmdMatrix34_t()
        result = fn(byref(seatedZeroPoseToRawTrackingPose))
        return result, seatedZeroPoseToRawTrackingPose

    def exportLiveToBuffer(self):
        fn = self.function_table.exportLiveToBuffer
        bufferLength = fn(None, 0)
        if bufferLength == 0:
            return ''
        buffer = ctypes.create_string_buffer(bufferLength)
        fn(buffer, bufferLength)
        return bytes(buffer.value).decode('utf-8')

    def importFromBufferToWorking(self, buffer: str, importFlags):
        fn = self.function_table.importFromBufferToWorking
        if buffer is not None:
            buffer = bytes(buffer, encoding='utf-8')
        result = fn(buffer, importFlags)
        return result

    def showWorkingSetPreview(self) -> None:
        """Shows the chaperone data in the working set to preview in the compositor."""
        fn = self.function_table.showWorkingSetPreview
        fn()

    def hideWorkingSetPreview(self) -> None:
        """Hides the chaperone data in the working set to preview in the compositor (if it was visible)."""
        fn = self.function_table.hideWorkingSetPreview
        fn()

    def roomSetupStarting(self) -> None:
        """
        Fire an event that the tracking system can use to know room setup is about to begin. This lets the tracking
        system make any last minute adjustments that should be incorporated into the new setup.  If the user is adjusting
        live in HMD using a tweak tool, keep in mind that calling this might cause the user to see the room jump.
        """
        fn = self.function_table.roomSetupStarting
        fn()


class IVRCompositor_FnTable(Structure):
    _fields_ = [
        ("setTrackingSpace", OPENVR_FNTABLE_CALLTYPE(None, ETrackingUniverseOrigin)),
        ("getTrackingSpace", OPENVR_FNTABLE_CALLTYPE(ETrackingUniverseOrigin)),
        ("waitGetPoses", OPENVR_FNTABLE_CALLTYPE(EVRCompositorError, POINTER(TrackedDevicePose_t), c_uint32, POINTER(TrackedDevicePose_t), c_uint32)),
        ("getLastPoses", OPENVR_FNTABLE_CALLTYPE(EVRCompositorError, POINTER(TrackedDevicePose_t), c_uint32, POINTER(TrackedDevicePose_t), c_uint32)),
        ("getLastPoseForTrackedDeviceIndex", OPENVR_FNTABLE_CALLTYPE(EVRCompositorError, TrackedDeviceIndex_t, POINTER(TrackedDevicePose_t), POINTER(TrackedDevicePose_t))),
        ("submit", OPENVR_FNTABLE_CALLTYPE(EVRCompositorError, EVREye, POINTER(Texture_t), POINTER(VRTextureBounds_t), EVRSubmitFlags)),
        ("clearLastSubmittedFrame", OPENVR_FNTABLE_CALLTYPE(None)),
        ("postPresentHandoff", OPENVR_FNTABLE_CALLTYPE(None)),
        ("getFrameTiming", OPENVR_FNTABLE_CALLTYPE(openvr_bool, POINTER(Compositor_FrameTiming), c_uint32)),
        ("getFrameTimings", OPENVR_FNTABLE_CALLTYPE(c_uint32, POINTER(Compositor_FrameTiming), c_uint32)),
        ("getFrameTimeRemaining", OPENVR_FNTABLE_CALLTYPE(c_float)),
        ("getCumulativeStats", OPENVR_FNTABLE_CALLTYPE(None, POINTER(Compositor_CumulativeStats), c_uint32)),
        ("fadeToColor", OPENVR_FNTABLE_CALLTYPE(None, c_float, c_float, c_float, c_float, c_float, openvr_bool)),
        ("getCurrentFadeColor", OPENVR_FNTABLE_CALLTYPE(HmdColor_t, openvr_bool)),
        ("fadeGrid", OPENVR_FNTABLE_CALLTYPE(None, c_float, openvr_bool)),
        ("getCurrentGridAlpha", OPENVR_FNTABLE_CALLTYPE(c_float)),
        ("setSkyboxOverride", OPENVR_FNTABLE_CALLTYPE(EVRCompositorError, POINTER(Texture_t), c_uint32)),
        ("clearSkyboxOverride", OPENVR_FNTABLE_CALLTYPE(None)),
        ("compositorBringToFront", OPENVR_FNTABLE_CALLTYPE(None)),
        ("compositorGoToBack", OPENVR_FNTABLE_CALLTYPE(None)),
        ("compositorQuit", OPENVR_FNTABLE_CALLTYPE(None)),
        ("isFullscreen", OPENVR_FNTABLE_CALLTYPE(openvr_bool)),
        ("getCurrentSceneFocusProcess", OPENVR_FNTABLE_CALLTYPE(c_uint32)),
        ("getLastFrameRenderer", OPENVR_FNTABLE_CALLTYPE(c_uint32)),
        ("canRenderScene", OPENVR_FNTABLE_CALLTYPE(openvr_bool)),
        ("showMirrorWindow", OPENVR_FNTABLE_CALLTYPE(None)),
        ("hideMirrorWindow", OPENVR_FNTABLE_CALLTYPE(None)),
        ("isMirrorWindowVisible", OPENVR_FNTABLE_CALLTYPE(openvr_bool)),
        ("compositorDumpImages", OPENVR_FNTABLE_CALLTYPE(None)),
        ("shouldAppRenderWithLowResources", OPENVR_FNTABLE_CALLTYPE(openvr_bool)),
        ("forceInterleavedReprojectionOn", OPENVR_FNTABLE_CALLTYPE(None, openvr_bool)),
        ("forceReconnectProcess", OPENVR_FNTABLE_CALLTYPE(None)),
        ("suspendRendering", OPENVR_FNTABLE_CALLTYPE(None, openvr_bool)),
        ("getMirrorTextureD3D11", OPENVR_FNTABLE_CALLTYPE(EVRCompositorError, EVREye, c_void_p, POINTER(c_void_p))),
        ("releaseMirrorTextureD3D11", OPENVR_FNTABLE_CALLTYPE(None, c_void_p)),
        ("getMirrorTextureGL", OPENVR_FNTABLE_CALLTYPE(EVRCompositorError, EVREye, POINTER(glUInt_t), POINTER(glSharedTextureHandle_t))),
        ("releaseSharedGLTexture", OPENVR_FNTABLE_CALLTYPE(openvr_bool, glUInt_t, glSharedTextureHandle_t)),
        ("lockGLSharedTextureForAccess", OPENVR_FNTABLE_CALLTYPE(None, glSharedTextureHandle_t)),
        ("unlockGLSharedTextureForAccess", OPENVR_FNTABLE_CALLTYPE(None, glSharedTextureHandle_t)),
        ("getVulkanInstanceExtensionsRequired", OPENVR_FNTABLE_CALLTYPE(c_uint32, c_char_p, c_uint32)),
        ("getVulkanDeviceExtensionsRequired", OPENVR_FNTABLE_CALLTYPE(c_uint32, POINTER(VkPhysicalDevice_T), c_char_p, c_uint32)),
        ("setExplicitTimingMode", OPENVR_FNTABLE_CALLTYPE(None, EVRCompositorTimingMode)),
        ("submitExplicitTimingData", OPENVR_FNTABLE_CALLTYPE(EVRCompositorError)),
        ("isMotionSmoothingEnabled", OPENVR_FNTABLE_CALLTYPE(openvr_bool)),
        ("isMotionSmoothingSupported", OPENVR_FNTABLE_CALLTYPE(openvr_bool)),
        ("isCurrentSceneFocusAppLoading", OPENVR_FNTABLE_CALLTYPE(openvr_bool)),
    ]


class IVRCompositor(object):
    """Allows the application to interact with the compositor"""

    def __init__(self):
        version_key = IVRCompositor_Version
        if not isInterfaceVersionValid(version_key):
            _checkInitError(VRInitError_Init_InterfaceNotFound)
        fn_key = 'FnTable:' + version_key
        fn_type = IVRCompositor_FnTable
        fn_table_ptr = cast(getGenericInterface(fn_key), POINTER(fn_type))
        if fn_table_ptr is None:
            raise OpenVRError("Error retrieving VR API for IVRCompositor")
        self.function_table = fn_table_ptr.contents

    def setTrackingSpace(self, origin) -> None:
        """Sets tracking space returned by WaitGetPoses"""
        fn = self.function_table.setTrackingSpace
        fn(origin)

    def getTrackingSpace(self):
        """Gets current tracking space returned by WaitGetPoses"""
        fn = self.function_table.getTrackingSpace
        result = fn()
        return result

    def waitGetPoses(self, renderPoseArray, gamePoseArray):
        """
        Scene applications should call this function to get poses to render with (and optionally poses predicted an additional frame out to use for gameplay).
        This function will block until "running start" milliseconds before the start of the frame, and should be called at the last moment before needing to
        start rendering.

        Return codes:
          - IsNotSceneApplication (make sure to call VR_Init with VRApplicaiton_Scene)
          - DoNotHaveFocus (some other app has taken focus - this will throttle the call to 10hz to reduce the impact on that app)
        """
        fn = self.function_table.waitGetPoses
        if renderPoseArray is None:
            renderPoseArrayCount = 0
            renderPoseArrayArg = None
        elif isinstance(renderPoseArray, ctypes.Array):
            renderPoseArrayCount = len(renderPoseArray)
            renderPoseArrayArg = byref(renderPoseArray[0])
        else:
            renderPoseArrayCount = k_unMaxTrackedDeviceCount
            renderPoseArray = (TrackedDevicePose_t * renderPoseArrayCount)()
            renderPoseArrayArg = byref(renderPoseArray[0])
        if gamePoseArray is None:
            gamePoseArrayCount = 0
            gamePoseArrayArg = None
        elif isinstance(gamePoseArray, ctypes.Array):
            gamePoseArrayCount = len(gamePoseArray)
            gamePoseArrayArg = byref(gamePoseArray[0])
        else:
            gamePoseArrayCount = k_unMaxTrackedDeviceCount
            gamePoseArray = (TrackedDevicePose_t * gamePoseArrayCount)()
            gamePoseArrayArg = byref(gamePoseArray[0])
        error = fn(renderPoseArrayArg, renderPoseArrayCount, gamePoseArrayArg, gamePoseArrayCount)
        openvr.error_code.CompositorError.check_error_value(error)
        return renderPoseArray, gamePoseArray

    def getLastPoses(self, renderPoseArray, gamePoseArray):
        """Get the last set of poses returned by WaitGetPoses."""
        fn = self.function_table.getLastPoses
        if renderPoseArray is None:
            renderPoseArrayCount = 0
            renderPoseArrayArg = None
        elif isinstance(renderPoseArray, ctypes.Array):
            renderPoseArrayCount = len(renderPoseArray)
            renderPoseArrayArg = byref(renderPoseArray[0])
        else:
            renderPoseArrayCount = k_unMaxTrackedDeviceCount
            renderPoseArray = (TrackedDevicePose_t * renderPoseArrayCount)()
            renderPoseArrayArg = byref(renderPoseArray[0])
        if gamePoseArray is None:
            gamePoseArrayCount = 0
            gamePoseArrayArg = None
        elif isinstance(gamePoseArray, ctypes.Array):
            gamePoseArrayCount = len(gamePoseArray)
            gamePoseArrayArg = byref(gamePoseArray[0])
        else:
            gamePoseArrayCount = k_unMaxTrackedDeviceCount
            gamePoseArray = (TrackedDevicePose_t * gamePoseArrayCount)()
            gamePoseArrayArg = byref(gamePoseArray[0])
        error = fn(renderPoseArrayArg, renderPoseArrayCount, gamePoseArrayArg, gamePoseArrayCount)
        openvr.error_code.CompositorError.check_error_value(error)
        return renderPoseArray, gamePoseArray

    def getLastPoseForTrackedDeviceIndex(self, deviceIndex):
        """
        Interface for accessing last set of poses returned by WaitGetPoses one at a time.
        Returns VRCompositorError_IndexOutOfRange if unDeviceIndex not less than k_unMaxTrackedDeviceCount otherwise VRCompositorError_None.
        It is okay to pass NULL for either pose if you only want one of the values.
        """
        fn = self.function_table.getLastPoseForTrackedDeviceIndex
        outputPose = TrackedDevicePose_t()
        outputGamePose = TrackedDevicePose_t()
        error = fn(deviceIndex, byref(outputPose), byref(outputGamePose))
        openvr.error_code.CompositorError.check_error_value(error)
        return outputPose, outputGamePose

    def submit(self, eye, texture, bounds=None, submitFlags=Submit_Default) -> None:
        """
        Updated scene texture to display. If pBounds is NULL the entire texture will be used.  If called from an OpenGL app, consider adding a glFlush after
        Submitting both frames to signal the driver to start processing, otherwise it may wait until the command buffer fills up, causing the app to miss frames.

        OpenGL dirty state:
          glBindTexture

        Return codes:
          - IsNotSceneApplication (make sure to call VR_Init with VRApplicaiton_Scene)
          - DoNotHaveFocus (some other app has taken focus)
          - TextureIsOnWrongDevice (application did not use proper AdapterIndex - see IVRSystem.GetDXGIOutputInfo)
          - SharedTexturesNotSupported (application needs to call CreateDXGIFactory1 or later before creating DX device)
          - TextureUsesUnsupportedFormat (scene textures must be compatible with DXGI sharing rules - e.g. uncompressed, no mips, etc.)
          - InvalidTexture (usually means bad arguments passed in)
          - AlreadySubmitted (app has submitted two left textures or two right textures in a single frame - i.e. before calling WaitGetPoses again)
        """
        fn = self.function_table.submit
        error = fn(eye, byref(texture), byref(bounds), submitFlags)
        openvr.error_code.CompositorError.check_error_value(error)

    def clearLastSubmittedFrame(self) -> None:
        """
        Clears the frame that was sent with the last call to Submit. This will cause the 
        compositor to show the grid until Submit is called again.
        """
        fn = self.function_table.clearLastSubmittedFrame
        fn()

    def postPresentHandoff(self) -> None:
        """
        Call immediately after presenting your app's window (i.e. companion window) to unblock the compositor.
        This is an optional call, which only needs to be used if you can't instead call WaitGetPoses immediately after Present.
        For example, if your engine's render and game loop are not on separate threads, or blocking the render thread until 3ms before the next vsync would
        introduce a deadlock of some sort.  This function tells the compositor that you have finished all rendering after having Submitted buffers for both
        eyes, and it is free to start its rendering work.  This should only be called from the same thread you are rendering on.
        """
        fn = self.function_table.postPresentHandoff
        fn()

    def getFrameTiming(self, framesAgo=0):
        """
        Returns true if timing data is filled it.  Sets oldest timing info if nFramesAgo is larger than the stored history.
        Be sure to set timing.size = sizeof(Compositor_FrameTiming) on struct passed in before calling this function.
        """
        fn = self.function_table.getFrameTiming
        timing = Compositor_FrameTiming()
        result = fn(byref(timing), framesAgo)
        return result, timing

    def getFrameTimings(self, timing):
        """
        Interface for copying a range of timing data.  Frames are returned in ascending order (oldest to newest) with the last being the most recent frame.
        Only the first entry's m_nSize needs to be set, as the rest will be inferred from that.  Returns total number of entries filled out.
        """
        fn = self.function_table.getFrameTimings
        if timing is None:
            frames = 0
            timingArg = None
        elif isinstance(timing, ctypes.Array):
            frames = len(timing)
            timingArg = byref(timing[0])
        else:
            frames = 1
            timing = (Compositor_FrameTiming * frames)()
            timingArg = byref(timing[0])
        result = fn(timingArg, frames)
        return result, timing

    def getFrameTimeRemaining(self):
        """
        Returns the time in seconds left in the current (as identified by FrameTiming's frameIndex) frame.
        Due to "running start", this value may roll over to the next frame before ever reaching 0.0.
        """
        fn = self.function_table.getFrameTimeRemaining
        result = fn()
        return result

    def getCumulativeStats(self, statsSizeInBytes):
        """Fills out stats accumulated for the last connected application.  Pass in sizeof( Compositor_CumulativeStats ) as second parameter."""
        fn = self.function_table.getCumulativeStats
        stats = Compositor_CumulativeStats()
        fn(byref(stats), statsSizeInBytes)
        return stats

    def fadeToColor(self, seconds: float, red: float, green: float, blue: float, alpha: float, background=False) -> None:
        """
        Fades the view on the HMD to the specified color. The fade will take fSeconds, and the color values are between
        0.0 and 1.0. This color is faded on top of the scene based on the alpha parameter. Removing the fade color instantly 
        would be FadeToColor( 0.0, 0.0, 0.0, 0.0, 0.0 ).  Values are in un-premultiplied alpha space.
        """
        fn = self.function_table.fadeToColor
        fn(seconds, red, green, blue, alpha, background)

    def getCurrentFadeColor(self, background=False):
        """Get current fade color value."""
        fn = self.function_table.getCurrentFadeColor
        result = fn(background)
        return result

    def fadeGrid(self, seconds: float, fadeIn) -> None:
        """Fading the Grid in or out in fSeconds"""
        fn = self.function_table.fadeGrid
        fn(seconds, fadeIn)

    def getCurrentGridAlpha(self):
        """Get current alpha value of grid."""
        fn = self.function_table.getCurrentGridAlpha
        result = fn()
        return result

    def setSkyboxOverride(self, textures) -> None:
        """
        Override the skybox used in the compositor (e.g. for during level loads when the app can't feed scene images fast enough)
        Order is Front, Back, Left, Right, Top, Bottom.  If only a single texture is passed, it is assumed in lat-long format.
        If two are passed, it is assumed a lat-long stereo pair.
        """
        fn = self.function_table.setSkyboxOverride
        if textures is None:
            textureCount = 0
            texturesArg = None
        elif isinstance(textures, ctypes.Array):
            textureCount = len(textures)
            texturesArg = byref(textures[0])
        else:
            textureCount = 1
            textures = (Texture_t * textureCount)()
            texturesArg = byref(textures[0])
        error = fn(texturesArg, textureCount)
        openvr.error_code.CompositorError.check_error_value(error)

    def clearSkyboxOverride(self) -> None:
        """Resets compositor skybox back to defaults."""
        fn = self.function_table.clearSkyboxOverride
        fn()

    def compositorBringToFront(self) -> None:
        """
        Brings the compositor window to the front. This is useful for covering any other window that may be on the HMD
        and is obscuring the compositor window.
        """
        fn = self.function_table.compositorBringToFront
        fn()

    def compositorGoToBack(self) -> None:
        """Pushes the compositor window to the back. This is useful for allowing other applications to draw directly to the HMD."""
        fn = self.function_table.compositorGoToBack
        fn()

    def compositorQuit(self) -> None:
        """
        Tells the compositor process to clean up and exit. You do not need to call this function at shutdown. Under normal 
        circumstances the compositor will manage its own life cycle based on what applications are running.
        """
        fn = self.function_table.compositorQuit
        fn()

    def isFullscreen(self):
        """Return whether the compositor is fullscreen"""
        fn = self.function_table.isFullscreen
        result = fn()
        return result

    def getCurrentSceneFocusProcess(self):
        """Returns the process ID of the process that is currently rendering the scene"""
        fn = self.function_table.getCurrentSceneFocusProcess
        result = fn()
        return result

    def getLastFrameRenderer(self):
        """
        Returns the process ID of the process that rendered the last frame (or 0 if the compositor itself rendered the frame.)
        Returns 0 when fading out from an app and the app's process Id when fading into an app.
        """
        fn = self.function_table.getLastFrameRenderer
        result = fn()
        return result

    def canRenderScene(self):
        """Returns true if the current process has the scene focus"""
        fn = self.function_table.canRenderScene
        result = fn()
        return result

    def showMirrorWindow(self) -> None:
        """Creates a window on the primary monitor to display what is being shown in the headset."""
        fn = self.function_table.showMirrorWindow
        fn()

    def hideMirrorWindow(self) -> None:
        """Closes the mirror window."""
        fn = self.function_table.hideMirrorWindow
        fn()

    def isMirrorWindowVisible(self):
        """Returns true if the mirror window is shown."""
        fn = self.function_table.isMirrorWindowVisible
        result = fn()
        return result

    def compositorDumpImages(self) -> None:
        """Writes back buffer and stereo left/right pair from the application to a 'screenshots' folder in the SteamVR runtime root."""
        fn = self.function_table.compositorDumpImages
        fn()

    def shouldAppRenderWithLowResources(self):
        """Let an app know it should be rendering with low resources."""
        fn = self.function_table.shouldAppRenderWithLowResources
        result = fn()
        return result

    def forceInterleavedReprojectionOn(self, override) -> None:
        """Override interleaved reprojection logic to force on."""
        fn = self.function_table.forceInterleavedReprojectionOn
        fn(override)

    def forceReconnectProcess(self) -> None:
        """Force reconnecting to the compositor process."""
        fn = self.function_table.forceReconnectProcess
        fn()

    def suspendRendering(self, suspend) -> None:
        """Temporarily suspends rendering (useful for finer control over scene transitions)."""
        fn = self.function_table.suspendRendering
        fn(suspend)

    def getMirrorTextureD3D11(self, eye, d3D11DeviceOrResource):
        """
        Opens a shared D3D11 texture with the undistorted composited image for each eye.  Use ReleaseMirrorTextureD3D11 when finished
        instead of calling Release on the resource itself.
        """
        fn = self.function_table.getMirrorTextureD3D11
        d3D11ShaderResourceView = c_void_p()
        error = fn(eye, byref(d3D11DeviceOrResource), byref(d3D11ShaderResourceView))
        openvr.error_code.CompositorError.check_error_value(error)
        return d3D11ShaderResourceView.value

    def releaseMirrorTextureD3D11(self, d3D11ShaderResourceView) -> None:
        fn = self.function_table.releaseMirrorTextureD3D11
        fn(byref(d3D11ShaderResourceView))

    def getMirrorTextureGL(self, eye):
        """Access to mirror textures from OpenGL."""
        fn = self.function_table.getMirrorTextureGL
        textureId = glUInt_t()
        sharedTextureHandle = glSharedTextureHandle_t()
        error = fn(eye, byref(textureId), byref(sharedTextureHandle))
        openvr.error_code.CompositorError.check_error_value(error)
        return textureId, sharedTextureHandle

    def releaseSharedGLTexture(self, textureId, sharedTextureHandle):
        fn = self.function_table.releaseSharedGLTexture
        result = fn(textureId, sharedTextureHandle)
        return result

    def lockGLSharedTextureForAccess(self, sharedTextureHandle) -> None:
        fn = self.function_table.lockGLSharedTextureForAccess
        fn(sharedTextureHandle)

    def unlockGLSharedTextureForAccess(self, sharedTextureHandle) -> None:
        fn = self.function_table.unlockGLSharedTextureForAccess
        fn(sharedTextureHandle)

    def getVulkanInstanceExtensionsRequired(self):
        """
        [Vulkan Only]
        return 0. Otherwise it returns the length of the number of bytes necessary to hold this string including the trailing
        null.  The string will be a space separated list of-required instance extensions to enable in VkCreateInstance
        """
        fn = self.function_table.getVulkanInstanceExtensionsRequired
        bufferSize = fn(None, 0)
        if bufferSize == 0:
            return ''
        value = ctypes.create_string_buffer(bufferSize)
        fn(value, bufferSize)
        return bytes(value.value).decode('utf-8')

    def getVulkanDeviceExtensionsRequired(self):
        """
        [Vulkan only]
        return 0. Otherwise it returns the length of the number of bytes necessary to hold this string including the trailing
        null.  The string will be a space separated list of required device extensions to enable in VkCreateDevice
        """
        fn = self.function_table.getVulkanDeviceExtensionsRequired
        physicalDevice = VkPhysicalDevice_T()
        bufferSize = fn(byref(physicalDevice), None, 0)
        if bufferSize == 0:
            return ''
        value = ctypes.create_string_buffer(bufferSize)
        fn(byref(physicalDevice), value, bufferSize)
        return physicalDevice, bytes(value.value).decode('utf-8')

    def setExplicitTimingMode(self, timingMode) -> None:
        """
        [ Vulkan/D3D12 Only ]
        There are two purposes for SetExplicitTimingMode:
          1. To get a more accurate GPU timestamp for when the frame begins in Vulkan/D3D12 applications.
          2. (Optional) To avoid having WaitGetPoses access the Vulkan queue so that the queue can be accessed from
          another thread while WaitGetPoses is executing.

        More accurate GPU timestamp for the start of the frame is achieved by the application calling
        SubmitExplicitTimingData immediately before its first submission to the Vulkan/D3D12 queue.
        This is more accurate because normally this GPU timestamp is recorded during WaitGetPoses.  In D3D11, 
        WaitGetPoses queues a GPU timestamp write, but it does not actually get submitted to the GPU until the 
        application flushes.  By using SubmitExplicitTimingData, the timestamp is recorded at the same place for 
        Vulkan/D3D12 as it is for D3D11, resulting in a more accurate GPU time measurement for the frame.

        Avoiding WaitGetPoses accessing the Vulkan queue can be achieved using SetExplicitTimingMode as well.  If this is desired,
        the application should set the timing mode to Explicit_ApplicationPerformsPostPresentHandoff and *MUST* call PostPresentHandoff
        itself. If these conditions are met, then WaitGetPoses is guaranteed not to access the queue.  Note that PostPresentHandoff
        and SubmitExplicitTimingData will access the queue, so only WaitGetPoses becomes safe for accessing the queue from another
        thread.
        """
        fn = self.function_table.setExplicitTimingMode
        fn(timingMode)

    def submitExplicitTimingData(self) -> None:
        """
        [ Vulkan/D3D12 Only ]
        Submit explicit timing data.  When SetExplicitTimingMode is true, this must be called immediately before
        the application's first vkQueueSubmit (Vulkan) or ID3D12CommandQueue::ExecuteCommandLists (D3D12) of each frame.
        This function will insert a GPU timestamp write just before the application starts its rendering.  This function
        will perform a vkQueueSubmit on Vulkan so must not be done simultaneously with VkQueue operations on another thread.
        Returns VRCompositorError_RequestFailed if SetExplicitTimingMode is not enabled.
        """
        fn = self.function_table.submitExplicitTimingData
        error = fn()
        openvr.error_code.CompositorError.check_error_value(error)

    def isMotionSmoothingEnabled(self):
        """
        Indicates whether or not motion smoothing is enabled by the user settings.
        If you want to know if motion smoothing actually triggered due to a late frame, check Compositor_FrameTiming
        m_nReprojectionFlags & VRCompositor_ReprojectionMotion instead.
        """
        fn = self.function_table.isMotionSmoothingEnabled
        result = fn()
        return result

    def isMotionSmoothingSupported(self):
        """Indicates whether or not motion smoothing is supported by the current hardware."""
        fn = self.function_table.isMotionSmoothingSupported
        result = fn()
        return result

    def isCurrentSceneFocusAppLoading(self):
        """
        Indicates whether or not the current scene focus app is currently loading.  This is inferred from its use of FadeGrid to
        explicitly fade to the compositor to cover up the fact that it cannot render at a sustained full framerate during this time.
        """
        fn = self.function_table.isCurrentSceneFocusAppLoading
        result = fn()
        return result


class IVRNotifications_FnTable(Structure):
    _fields_ = [
        ("createNotification", OPENVR_FNTABLE_CALLTYPE(EVRNotificationError, VROverlayHandle_t, c_uint64, EVRNotificationType, c_char_p, EVRNotificationStyle, POINTER(NotificationBitmap_t), POINTER(VRNotificationId))),
        ("removeNotification", OPENVR_FNTABLE_CALLTYPE(EVRNotificationError, VRNotificationId)),
    ]


class IVRNotifications(object):
    """
    Allows notification sources to interact with the VR system
    This current interface is not yet implemented. Do not use yet.
    """

    def __init__(self):
        version_key = IVRNotifications_Version
        if not isInterfaceVersionValid(version_key):
            _checkInitError(VRInitError_Init_InterfaceNotFound)
        fn_key = 'FnTable:' + version_key
        fn_type = IVRNotifications_FnTable
        fn_table_ptr = cast(getGenericInterface(fn_key), POINTER(fn_type))
        if fn_table_ptr is None:
            raise OpenVRError("Error retrieving VR API for IVRNotifications")
        self.function_table = fn_table_ptr.contents

    def createNotification(self, overlayHandle, userValue, type_, text: str, style, image):
        """
        Create a notification and enqueue it to be shown to the user.
        An overlay handle is required to create a notification, as otherwise it would be impossible for a user to act on it.
        To create a two-line notification, use a line break ('\\n') to split the text into two lines.
        The pImage argument may be NULL, in which case the specified overlay's icon will be used instead.
        """
        fn = self.function_table.createNotification
        if text is not None:
            text = bytes(text, encoding='utf-8')
        notificationId = VRNotificationId()
        error = fn(overlayHandle, userValue, type_, text, style, byref(image), byref(notificationId))
        openvr.error_code.NotificationError.check_error_value(error)
        return notificationId

    def removeNotification(self, notificationId) -> None:
        """Destroy a notification, hiding it first if it currently shown to the user."""
        fn = self.function_table.removeNotification
        error = fn(notificationId)
        openvr.error_code.NotificationError.check_error_value(error)


class IVROverlay_FnTable(Structure):
    _fields_ = [
        ("findOverlay", OPENVR_FNTABLE_CALLTYPE(EVROverlayError, c_char_p, POINTER(VROverlayHandle_t))),
        ("createOverlay", OPENVR_FNTABLE_CALLTYPE(EVROverlayError, c_char_p, c_char_p, POINTER(VROverlayHandle_t))),
        ("destroyOverlay", OPENVR_FNTABLE_CALLTYPE(EVROverlayError, VROverlayHandle_t)),
        ("setHighQualityOverlay", OPENVR_FNTABLE_CALLTYPE(EVROverlayError, VROverlayHandle_t)),
        ("getHighQualityOverlay", OPENVR_FNTABLE_CALLTYPE(VROverlayHandle_t)),
        ("getOverlayKey", OPENVR_FNTABLE_CALLTYPE(c_uint32, VROverlayHandle_t, c_char_p, c_uint32, POINTER(EVROverlayError))),
        ("getOverlayName", OPENVR_FNTABLE_CALLTYPE(c_uint32, VROverlayHandle_t, c_char_p, c_uint32, POINTER(EVROverlayError))),
        ("setOverlayName", OPENVR_FNTABLE_CALLTYPE(EVROverlayError, VROverlayHandle_t, c_char_p)),
        ("getOverlayImageData", OPENVR_FNTABLE_CALLTYPE(EVROverlayError, VROverlayHandle_t, c_void_p, c_uint32, POINTER(c_uint32), POINTER(c_uint32))),
        ("getOverlayErrorNameFromEnum", OPENVR_FNTABLE_CALLTYPE(c_char_p, EVROverlayError)),
        ("setOverlayRenderingPid", OPENVR_FNTABLE_CALLTYPE(EVROverlayError, VROverlayHandle_t, c_uint32)),
        ("getOverlayRenderingPid", OPENVR_FNTABLE_CALLTYPE(c_uint32, VROverlayHandle_t)),
        ("setOverlayFlag", OPENVR_FNTABLE_CALLTYPE(EVROverlayError, VROverlayHandle_t, VROverlayFlags, openvr_bool)),
        ("getOverlayFlag", OPENVR_FNTABLE_CALLTYPE(EVROverlayError, VROverlayHandle_t, VROverlayFlags, POINTER(openvr_bool))),
        ("setOverlayColor", OPENVR_FNTABLE_CALLTYPE(EVROverlayError, VROverlayHandle_t, c_float, c_float, c_float)),
        ("getOverlayColor", OPENVR_FNTABLE_CALLTYPE(EVROverlayError, VROverlayHandle_t, POINTER(c_float), POINTER(c_float), POINTER(c_float))),
        ("setOverlayAlpha", OPENVR_FNTABLE_CALLTYPE(EVROverlayError, VROverlayHandle_t, c_float)),
        ("getOverlayAlpha", OPENVR_FNTABLE_CALLTYPE(EVROverlayError, VROverlayHandle_t, POINTER(c_float))),
        ("setOverlayTexelAspect", OPENVR_FNTABLE_CALLTYPE(EVROverlayError, VROverlayHandle_t, c_float)),
        ("getOverlayTexelAspect", OPENVR_FNTABLE_CALLTYPE(EVROverlayError, VROverlayHandle_t, POINTER(c_float))),
        ("setOverlaySortOrder", OPENVR_FNTABLE_CALLTYPE(EVROverlayError, VROverlayHandle_t, c_uint32)),
        ("getOverlaySortOrder", OPENVR_FNTABLE_CALLTYPE(EVROverlayError, VROverlayHandle_t, POINTER(c_uint32))),
        ("setOverlayWidthInMeters", OPENVR_FNTABLE_CALLTYPE(EVROverlayError, VROverlayHandle_t, c_float)),
        ("getOverlayWidthInMeters", OPENVR_FNTABLE_CALLTYPE(EVROverlayError, VROverlayHandle_t, POINTER(c_float))),
        ("setOverlayAutoCurveDistanceRangeInMeters", OPENVR_FNTABLE_CALLTYPE(EVROverlayError, VROverlayHandle_t, c_float, c_float)),
        ("getOverlayAutoCurveDistanceRangeInMeters", OPENVR_FNTABLE_CALLTYPE(EVROverlayError, VROverlayHandle_t, POINTER(c_float), POINTER(c_float))),
        ("setOverlayTextureColorSpace", OPENVR_FNTABLE_CALLTYPE(EVROverlayError, VROverlayHandle_t, EColorSpace)),
        ("getOverlayTextureColorSpace", OPENVR_FNTABLE_CALLTYPE(EVROverlayError, VROverlayHandle_t, POINTER(EColorSpace))),
        ("setOverlayTextureBounds", OPENVR_FNTABLE_CALLTYPE(EVROverlayError, VROverlayHandle_t, POINTER(VRTextureBounds_t))),
        ("getOverlayTextureBounds", OPENVR_FNTABLE_CALLTYPE(EVROverlayError, VROverlayHandle_t, POINTER(VRTextureBounds_t))),
        ("getOverlayRenderModel", OPENVR_FNTABLE_CALLTYPE(c_uint32, VROverlayHandle_t, c_char_p, c_uint32, POINTER(HmdColor_t), POINTER(EVROverlayError))),
        ("setOverlayRenderModel", OPENVR_FNTABLE_CALLTYPE(EVROverlayError, VROverlayHandle_t, c_char_p, POINTER(HmdColor_t))),
        ("getOverlayTransformType", OPENVR_FNTABLE_CALLTYPE(EVROverlayError, VROverlayHandle_t, POINTER(VROverlayTransformType))),
        ("setOverlayTransformAbsolute", OPENVR_FNTABLE_CALLTYPE(EVROverlayError, VROverlayHandle_t, ETrackingUniverseOrigin, POINTER(HmdMatrix34_t))),
        ("getOverlayTransformAbsolute", OPENVR_FNTABLE_CALLTYPE(EVROverlayError, VROverlayHandle_t, POINTER(ETrackingUniverseOrigin), POINTER(HmdMatrix34_t))),
        ("setOverlayTransformTrackedDeviceRelative", OPENVR_FNTABLE_CALLTYPE(EVROverlayError, VROverlayHandle_t, TrackedDeviceIndex_t, POINTER(HmdMatrix34_t))),
        ("getOverlayTransformTrackedDeviceRelative", OPENVR_FNTABLE_CALLTYPE(EVROverlayError, VROverlayHandle_t, POINTER(TrackedDeviceIndex_t), POINTER(HmdMatrix34_t))),
        ("setOverlayTransformTrackedDeviceComponent", OPENVR_FNTABLE_CALLTYPE(EVROverlayError, VROverlayHandle_t, TrackedDeviceIndex_t, c_char_p)),
        ("getOverlayTransformTrackedDeviceComponent", OPENVR_FNTABLE_CALLTYPE(EVROverlayError, VROverlayHandle_t, POINTER(TrackedDeviceIndex_t), c_char_p, c_uint32)),
        ("getOverlayTransformOverlayRelative", OPENVR_FNTABLE_CALLTYPE(EVROverlayError, VROverlayHandle_t, POINTER(VROverlayHandle_t), POINTER(HmdMatrix34_t))),
        ("setOverlayTransformOverlayRelative", OPENVR_FNTABLE_CALLTYPE(EVROverlayError, VROverlayHandle_t, VROverlayHandle_t, POINTER(HmdMatrix34_t))),
        ("showOverlay", OPENVR_FNTABLE_CALLTYPE(EVROverlayError, VROverlayHandle_t)),
        ("hideOverlay", OPENVR_FNTABLE_CALLTYPE(EVROverlayError, VROverlayHandle_t)),
        ("isOverlayVisible", OPENVR_FNTABLE_CALLTYPE(openvr_bool, VROverlayHandle_t)),
        ("getTransformForOverlayCoordinates", OPENVR_FNTABLE_CALLTYPE(EVROverlayError, VROverlayHandle_t, ETrackingUniverseOrigin, HmdVector2_t, POINTER(HmdMatrix34_t))),
        ("pollNextOverlayEvent", OPENVR_FNTABLE_CALLTYPE(openvr_bool, VROverlayHandle_t, POINTER(VREvent_t), c_uint32)),
        ("getOverlayInputMethod", OPENVR_FNTABLE_CALLTYPE(EVROverlayError, VROverlayHandle_t, POINTER(VROverlayInputMethod))),
        ("setOverlayInputMethod", OPENVR_FNTABLE_CALLTYPE(EVROverlayError, VROverlayHandle_t, VROverlayInputMethod)),
        ("getOverlayMouseScale", OPENVR_FNTABLE_CALLTYPE(EVROverlayError, VROverlayHandle_t, POINTER(HmdVector2_t))),
        ("setOverlayMouseScale", OPENVR_FNTABLE_CALLTYPE(EVROverlayError, VROverlayHandle_t, POINTER(HmdVector2_t))),
        ("computeOverlayIntersection", OPENVR_FNTABLE_CALLTYPE(openvr_bool, VROverlayHandle_t, POINTER(VROverlayIntersectionParams_t), POINTER(VROverlayIntersectionResults_t))),
        ("isHoverTargetOverlay", OPENVR_FNTABLE_CALLTYPE(openvr_bool, VROverlayHandle_t)),
        ("getGamepadFocusOverlay", OPENVR_FNTABLE_CALLTYPE(VROverlayHandle_t)),
        ("setGamepadFocusOverlay", OPENVR_FNTABLE_CALLTYPE(EVROverlayError, VROverlayHandle_t)),
        ("setOverlayNeighbor", OPENVR_FNTABLE_CALLTYPE(EVROverlayError, EOverlayDirection, VROverlayHandle_t, VROverlayHandle_t)),
        ("moveGamepadFocusToNeighbor", OPENVR_FNTABLE_CALLTYPE(EVROverlayError, EOverlayDirection, VROverlayHandle_t)),
        ("setOverlayDualAnalogTransform", OPENVR_FNTABLE_CALLTYPE(EVROverlayError, VROverlayHandle_t, EDualAnalogWhich, POINTER(HmdVector2_t), c_float)),
        ("getOverlayDualAnalogTransform", OPENVR_FNTABLE_CALLTYPE(EVROverlayError, VROverlayHandle_t, EDualAnalogWhich, POINTER(HmdVector2_t), POINTER(c_float))),
        ("setOverlayTexture", OPENVR_FNTABLE_CALLTYPE(EVROverlayError, VROverlayHandle_t, POINTER(Texture_t))),
        ("clearOverlayTexture", OPENVR_FNTABLE_CALLTYPE(EVROverlayError, VROverlayHandle_t)),
        ("setOverlayRaw", OPENVR_FNTABLE_CALLTYPE(EVROverlayError, VROverlayHandle_t, c_void_p, c_uint32, c_uint32, c_uint32)),
        ("setOverlayFromFile", OPENVR_FNTABLE_CALLTYPE(EVROverlayError, VROverlayHandle_t, c_char_p)),
        ("getOverlayTexture", OPENVR_FNTABLE_CALLTYPE(EVROverlayError, VROverlayHandle_t, POINTER(c_void_p), c_void_p, POINTER(c_uint32), POINTER(c_uint32), POINTER(c_uint32), POINTER(ETextureType), POINTER(EColorSpace), POINTER(VRTextureBounds_t))),
        ("releaseNativeOverlayHandle", OPENVR_FNTABLE_CALLTYPE(EVROverlayError, VROverlayHandle_t, c_void_p)),
        ("getOverlayTextureSize", OPENVR_FNTABLE_CALLTYPE(EVROverlayError, VROverlayHandle_t, POINTER(c_uint32), POINTER(c_uint32))),
        ("createDashboardOverlay", OPENVR_FNTABLE_CALLTYPE(EVROverlayError, c_char_p, c_char_p, POINTER(VROverlayHandle_t), POINTER(VROverlayHandle_t))),
        ("isDashboardVisible", OPENVR_FNTABLE_CALLTYPE(openvr_bool)),
        ("isActiveDashboardOverlay", OPENVR_FNTABLE_CALLTYPE(openvr_bool, VROverlayHandle_t)),
        ("setDashboardOverlaySceneProcess", OPENVR_FNTABLE_CALLTYPE(EVROverlayError, VROverlayHandle_t, c_uint32)),
        ("getDashboardOverlaySceneProcess", OPENVR_FNTABLE_CALLTYPE(EVROverlayError, VROverlayHandle_t, POINTER(c_uint32))),
        ("showDashboard", OPENVR_FNTABLE_CALLTYPE(None, c_char_p)),
        ("getPrimaryDashboardDevice", OPENVR_FNTABLE_CALLTYPE(TrackedDeviceIndex_t)),
        ("showKeyboard", OPENVR_FNTABLE_CALLTYPE(EVROverlayError, EGamepadTextInputMode, EGamepadTextInputLineMode, c_char_p, c_uint32, c_char_p, openvr_bool, c_uint64)),
        ("showKeyboardForOverlay", OPENVR_FNTABLE_CALLTYPE(EVROverlayError, VROverlayHandle_t, EGamepadTextInputMode, EGamepadTextInputLineMode, c_char_p, c_uint32, c_char_p, openvr_bool, c_uint64)),
        ("getKeyboardText", OPENVR_FNTABLE_CALLTYPE(c_uint32, c_char_p, c_uint32)),
        ("hideKeyboard", OPENVR_FNTABLE_CALLTYPE(None)),
        ("setKeyboardTransformAbsolute", OPENVR_FNTABLE_CALLTYPE(None, ETrackingUniverseOrigin, POINTER(HmdMatrix34_t))),
        ("setKeyboardPositionForOverlay", OPENVR_FNTABLE_CALLTYPE(None, VROverlayHandle_t, HmdRect2_t)),
        ("setOverlayIntersectionMask", OPENVR_FNTABLE_CALLTYPE(EVROverlayError, VROverlayHandle_t, POINTER(VROverlayIntersectionMaskPrimitive_t), c_uint32, c_uint32)),
        ("getOverlayFlags", OPENVR_FNTABLE_CALLTYPE(EVROverlayError, VROverlayHandle_t, POINTER(c_uint32))),
        ("showMessageOverlay", OPENVR_FNTABLE_CALLTYPE(VRMessageOverlayResponse, c_char_p, c_char_p, c_char_p, c_char_p, c_char_p, c_char_p)),
        ("closeMessageOverlay", OPENVR_FNTABLE_CALLTYPE(None)),
    ]


class IVROverlay(object):
    def __init__(self):
        version_key = IVROverlay_Version
        if not isInterfaceVersionValid(version_key):
            _checkInitError(VRInitError_Init_InterfaceNotFound)
        fn_key = 'FnTable:' + version_key
        fn_type = IVROverlay_FnTable
        fn_table_ptr = cast(getGenericInterface(fn_key), POINTER(fn_type))
        if fn_table_ptr is None:
            raise OpenVRError("Error retrieving VR API for IVROverlay")
        self.function_table = fn_table_ptr.contents

    def findOverlay(self, overlayKey: str):
        """Finds an existing overlay with the specified key."""
        fn = self.function_table.findOverlay
        if overlayKey is not None:
            overlayKey = bytes(overlayKey, encoding='utf-8')
        overlayHandle = VROverlayHandle_t()
        error = fn(overlayKey, byref(overlayHandle))
        openvr.error_code.OverlayError.check_error_value(error)
        return overlayHandle.value

    def createOverlay(self, overlayKey: str, overlayName: str):
        """Creates a new named overlay. All overlays start hidden and with default settings."""
        fn = self.function_table.createOverlay
        if overlayKey is not None:
            overlayKey = bytes(overlayKey, encoding='utf-8')
        if overlayName is not None:
            overlayName = bytes(overlayName, encoding='utf-8')
        overlayHandle = VROverlayHandle_t()
        error = fn(overlayKey, overlayName, byref(overlayHandle))
        openvr.error_code.OverlayError.check_error_value(error)
        return overlayHandle.value

    def destroyOverlay(self, overlayHandle) -> None:
        """
        Destroys the specified overlay. When an application calls VR_Shutdown all overlays created by that app are
        automatically destroyed.
        """
        fn = self.function_table.destroyOverlay
        error = fn(overlayHandle)
        openvr.error_code.OverlayError.check_error_value(error)

    def setHighQualityOverlay(self, overlayHandle) -> None:
        """
        Specify which overlay to use the high quality render path.  This overlay will be composited in during the distortion pass which
        results in it drawing on top of everything else, but also at a higher quality as it samples the source texture directly rather than
        rasterizing into each eye's render texture first.  Because if this, only one of these is supported at any given time.  It is most useful
        for overlays that are expected to take up most of the user's view (e.g. streaming video).
        This mode does not support mouse input to your overlay.
        """
        fn = self.function_table.setHighQualityOverlay
        error = fn(overlayHandle)
        openvr.error_code.OverlayError.check_error_value(error)

    def getHighQualityOverlay(self):
        """
        Returns the overlay handle of the current overlay being rendered using the single high quality overlay render path.
        Otherwise it will return k_ulOverlayHandleInvalid.
        """
        fn = self.function_table.getHighQualityOverlay
        result = fn()
        return result

    def getOverlayKey(self, overlayHandle):
        """
        Fills the provided buffer with the string key of the overlay. Returns the size of buffer required to store the key, including
        the terminating null character. k_unVROverlayMaxKeyLength will be enough bytes to fit the string.
        """
        fn = self.function_table.getOverlayKey
        error = EVROverlayError()
        bufferSize = fn(overlayHandle, None, 0, byref(error))
        if bufferSize == 0:
            return ''
        value = ctypes.create_string_buffer(bufferSize)
        fn(overlayHandle, value, bufferSize, byref(error))
        openvr.error_code.OverlayError.check_error_value(error.value)
        return bytes(value.value).decode('utf-8')

    def getOverlayName(self, overlayHandle):
        """
        Fills the provided buffer with the friendly name of the overlay. Returns the size of buffer required to store the key, including
        the terminating null character. k_unVROverlayMaxNameLength will be enough bytes to fit the string.
        """
        fn = self.function_table.getOverlayName
        error = EVROverlayError()
        bufferSize = fn(overlayHandle, None, 0, byref(error))
        if bufferSize == 0:
            return ''
        value = ctypes.create_string_buffer(bufferSize)
        fn(overlayHandle, value, bufferSize, byref(error))
        openvr.error_code.OverlayError.check_error_value(error.value)
        return bytes(value.value).decode('utf-8')

    def setOverlayName(self, overlayHandle, name: str) -> None:
        """set the name to use for this overlay"""
        fn = self.function_table.setOverlayName
        if name is not None:
            name = bytes(name, encoding='utf-8')
        error = fn(overlayHandle, name)
        openvr.error_code.OverlayError.check_error_value(error)

    def getOverlayImageData(self, overlayHandle, buffer, bufferSize):
        """
        Gets the raw image data from an overlay. Overlay image data is always returned as RGBA data, 4 bytes per pixel. If the buffer is not large enough, width and height 
        will be set and VROverlayError_ArrayTooSmall is returned.
        """
        fn = self.function_table.getOverlayImageData
        width = c_uint32()
        height = c_uint32()
        error = fn(overlayHandle, byref(buffer), bufferSize, byref(width), byref(height))
        openvr.error_code.OverlayError.check_error_value(error)
        return width.value, height.value

    def getOverlayErrorNameFromEnum(self, error):
        """
        returns a string that corresponds with the specified overlay error. The string will be the name 
        of the error enum value for all valid error codes
        """
        fn = self.function_table.getOverlayErrorNameFromEnum
        result = fn(error)
        return result

    def setOverlayRenderingPid(self, overlayHandle, pID) -> None:
        """
        Sets the pid that is allowed to render to this overlay (the creator pid is always allow to render),
        by default this is the pid of the process that made the overlay
        """
        fn = self.function_table.setOverlayRenderingPid
        error = fn(overlayHandle, pID)
        openvr.error_code.OverlayError.check_error_value(error)

    def getOverlayRenderingPid(self, overlayHandle):
        """Gets the pid that is allowed to render to this overlay"""
        fn = self.function_table.getOverlayRenderingPid
        result = fn(overlayHandle)
        return result

    def setOverlayFlag(self, overlayHandle, overlayFlag, enabled) -> None:
        """Specify flag setting for a given overlay"""
        fn = self.function_table.setOverlayFlag
        error = fn(overlayHandle, overlayFlag, enabled)
        openvr.error_code.OverlayError.check_error_value(error)

    def getOverlayFlag(self, overlayHandle, overlayFlag):
        """Sets flag setting for a given overlay"""
        fn = self.function_table.getOverlayFlag
        enabled = openvr_bool()
        error = fn(overlayHandle, overlayFlag, byref(enabled))
        openvr.error_code.OverlayError.check_error_value(error)
        return enabled

    def setOverlayColor(self, overlayHandle, red: float, green: float, blue: float) -> None:
        """Sets the color tint of the overlay quad. Use 0.0 to 1.0 per channel."""
        fn = self.function_table.setOverlayColor
        error = fn(overlayHandle, red, green, blue)
        openvr.error_code.OverlayError.check_error_value(error)

    def getOverlayColor(self, overlayHandle):
        """Gets the color tint of the overlay quad."""
        fn = self.function_table.getOverlayColor
        red = c_float()
        green = c_float()
        blue = c_float()
        error = fn(overlayHandle, byref(red), byref(green), byref(blue))
        openvr.error_code.OverlayError.check_error_value(error)
        return red.value, green.value, blue.value

    def setOverlayAlpha(self, overlayHandle, alpha: float) -> None:
        """Sets the alpha of the overlay quad. Use 1.0 for 100 percent opacity to 0.0 for 0 percent opacity."""
        fn = self.function_table.setOverlayAlpha
        error = fn(overlayHandle, alpha)
        openvr.error_code.OverlayError.check_error_value(error)

    def getOverlayAlpha(self, overlayHandle):
        """Gets the alpha of the overlay quad. By default overlays are rendering at 100 percent alpha (1.0)."""
        fn = self.function_table.getOverlayAlpha
        alpha = c_float()
        error = fn(overlayHandle, byref(alpha))
        openvr.error_code.OverlayError.check_error_value(error)
        return alpha.value

    def setOverlayTexelAspect(self, overlayHandle, texelAspect: float) -> None:
        """
        Sets the aspect ratio of the texels in the overlay. 1.0 means the texels are square. 2.0 means the texels
        are twice as wide as they are tall. Defaults to 1.0.
        """
        fn = self.function_table.setOverlayTexelAspect
        error = fn(overlayHandle, texelAspect)
        openvr.error_code.OverlayError.check_error_value(error)

    def getOverlayTexelAspect(self, overlayHandle):
        """Gets the aspect ratio of the texels in the overlay. Defaults to 1.0"""
        fn = self.function_table.getOverlayTexelAspect
        texelAspect = c_float()
        error = fn(overlayHandle, byref(texelAspect))
        openvr.error_code.OverlayError.check_error_value(error)
        return texelAspect.value

    def setOverlaySortOrder(self, overlayHandle, sortOrder) -> None:
        """
        Sets the rendering sort order for the overlay. Overlays are rendered this order:
           Overlays owned by the scene application
           Overlays owned by some other application

        Within a category overlays are rendered lowest sort order to highest sort order. Overlays with the same 
        sort order are rendered back to front base on distance from the HMD.

        Sort order defaults to 0.
        """
        fn = self.function_table.setOverlaySortOrder
        error = fn(overlayHandle, sortOrder)
        openvr.error_code.OverlayError.check_error_value(error)

    def getOverlaySortOrder(self, overlayHandle):
        """Gets the sort order of the overlay. See SetOverlaySortOrder for how this works."""
        fn = self.function_table.getOverlaySortOrder
        sortOrder = c_uint32()
        error = fn(overlayHandle, byref(sortOrder))
        openvr.error_code.OverlayError.check_error_value(error)
        return sortOrder.value

    def setOverlayWidthInMeters(self, overlayHandle, widthInMeters: float) -> None:
        """Sets the width of the overlay quad in meters. By default overlays are rendered on a quad that is 1 meter across"""
        fn = self.function_table.setOverlayWidthInMeters
        error = fn(overlayHandle, widthInMeters)
        openvr.error_code.OverlayError.check_error_value(error)

    def getOverlayWidthInMeters(self, overlayHandle):
        """Returns the width of the overlay quad in meters. By default overlays are rendered on a quad that is 1 meter across"""
        fn = self.function_table.getOverlayWidthInMeters
        widthInMeters = c_float()
        error = fn(overlayHandle, byref(widthInMeters))
        openvr.error_code.OverlayError.check_error_value(error)
        return widthInMeters.value

    def setOverlayAutoCurveDistanceRangeInMeters(self, overlayHandle, minDistanceInMeters: float, maxDistanceInMeters: float) -> None:
        """
        For high-quality curved overlays only, sets the distance range in meters from the overlay used to automatically curve
        the surface around the viewer.  Min is distance is when the surface will be most curved.  Max is when least curved.
        """
        fn = self.function_table.setOverlayAutoCurveDistanceRangeInMeters
        error = fn(overlayHandle, minDistanceInMeters, maxDistanceInMeters)
        openvr.error_code.OverlayError.check_error_value(error)

    def getOverlayAutoCurveDistanceRangeInMeters(self, overlayHandle):
        """
        For high-quality curved overlays only, gets the distance range in meters from the overlay used to automatically curve
        the surface around the viewer.  Min is distance is when the surface will be most curved.  Max is when least curved.
        """
        fn = self.function_table.getOverlayAutoCurveDistanceRangeInMeters
        minDistanceInMeters = c_float()
        maxDistanceInMeters = c_float()
        error = fn(overlayHandle, byref(minDistanceInMeters), byref(maxDistanceInMeters))
        openvr.error_code.OverlayError.check_error_value(error)
        return minDistanceInMeters.value, maxDistanceInMeters.value

    def setOverlayTextureColorSpace(self, overlayHandle, textureColorSpace) -> None:
        """
        Sets the colorspace the overlay texture's data is in.  Defaults to 'auto'.
        If the texture needs to be resolved, you should call SetOverlayTexture with the appropriate colorspace instead.
        """
        fn = self.function_table.setOverlayTextureColorSpace
        error = fn(overlayHandle, textureColorSpace)
        openvr.error_code.OverlayError.check_error_value(error)

    def getOverlayTextureColorSpace(self, overlayHandle):
        """Gets the overlay's current colorspace setting."""
        fn = self.function_table.getOverlayTextureColorSpace
        textureColorSpace = EColorSpace()
        error = fn(overlayHandle, byref(textureColorSpace))
        openvr.error_code.OverlayError.check_error_value(error)
        return textureColorSpace

    def setOverlayTextureBounds(self, overlayHandle, overlayTextureBounds) -> None:
        """Sets the part of the texture to use for the overlay. UV Min is the upper left corner and UV Max is the lower right corner."""
        fn = self.function_table.setOverlayTextureBounds
        error = fn(overlayHandle, byref(overlayTextureBounds))
        openvr.error_code.OverlayError.check_error_value(error)

    def getOverlayTextureBounds(self, overlayHandle):
        """Gets the part of the texture to use for the overlay. UV Min is the upper left corner and UV Max is the lower right corner."""
        fn = self.function_table.getOverlayTextureBounds
        overlayTextureBounds = VRTextureBounds_t()
        error = fn(overlayHandle, byref(overlayTextureBounds))
        openvr.error_code.OverlayError.check_error_value(error)
        return overlayTextureBounds

    def getOverlayRenderModel(self, overlayHandle):
        """Gets render model to draw behind this overlay"""
        fn = self.function_table.getOverlayRenderModel
        color = HmdColor_t()
        error = EVROverlayError()
        bufferSize = fn(overlayHandle, None, 0, byref(color), byref(error))
        if bufferSize == 0:
            return ''
        value = ctypes.create_string_buffer(bufferSize)
        fn(overlayHandle, value, bufferSize, byref(color), byref(error))
        openvr.error_code.OverlayError.check_error_value(error.value)
        return bytes(value.value).decode('utf-8'), color

    def setOverlayRenderModel(self, overlayHandle, renderModel: str, color) -> None:
        """
        Sets render model to draw behind this overlay and the vertex color to use, pass null for pColor to match the overlays vertex color. 
        The model is scaled by the same amount as the overlay, with a default of 1m.
        """
        fn = self.function_table.setOverlayRenderModel
        if renderModel is not None:
            renderModel = bytes(renderModel, encoding='utf-8')
        error = fn(overlayHandle, renderModel, byref(color))
        openvr.error_code.OverlayError.check_error_value(error)

    def getOverlayTransformType(self, overlayHandle):
        """Returns the transform type of this overlay."""
        fn = self.function_table.getOverlayTransformType
        transformType = VROverlayTransformType()
        error = fn(overlayHandle, byref(transformType))
        openvr.error_code.OverlayError.check_error_value(error)
        return transformType

    def setOverlayTransformAbsolute(self, overlayHandle, trackingOrigin, trackingOriginToOverlayTransform) -> None:
        """Sets the transform to absolute tracking origin."""
        fn = self.function_table.setOverlayTransformAbsolute
        error = fn(overlayHandle, trackingOrigin, byref(trackingOriginToOverlayTransform))
        openvr.error_code.OverlayError.check_error_value(error)

    def getOverlayTransformAbsolute(self, overlayHandle):
        """Gets the transform if it is absolute. Returns an error if the transform is some other type."""
        fn = self.function_table.getOverlayTransformAbsolute
        trackingOrigin = ETrackingUniverseOrigin()
        trackingOriginToOverlayTransform = HmdMatrix34_t()
        error = fn(overlayHandle, byref(trackingOrigin), byref(trackingOriginToOverlayTransform))
        openvr.error_code.OverlayError.check_error_value(error)
        return trackingOrigin, trackingOriginToOverlayTransform

    def setOverlayTransformTrackedDeviceRelative(self, overlayHandle, trackedDevice, trackedDeviceToOverlayTransform) -> None:
        """Sets the transform to relative to the transform of the specified tracked device."""
        fn = self.function_table.setOverlayTransformTrackedDeviceRelative
        error = fn(overlayHandle, trackedDevice, byref(trackedDeviceToOverlayTransform))
        openvr.error_code.OverlayError.check_error_value(error)

    def getOverlayTransformTrackedDeviceRelative(self, overlayHandle):
        """Gets the transform if it is relative to a tracked device. Returns an error if the transform is some other type."""
        fn = self.function_table.getOverlayTransformTrackedDeviceRelative
        trackedDevice = TrackedDeviceIndex_t()
        trackedDeviceToOverlayTransform = HmdMatrix34_t()
        error = fn(overlayHandle, byref(trackedDevice), byref(trackedDeviceToOverlayTransform))
        openvr.error_code.OverlayError.check_error_value(error)
        return trackedDevice, trackedDeviceToOverlayTransform

    def setOverlayTransformTrackedDeviceComponent(self, overlayHandle, deviceIndex, componentName: str) -> None:
        """
        Sets the transform to draw the overlay on a rendermodel component mesh instead of a quad. This will only draw when the system is
        drawing the device. Overlays with this transform type cannot receive mouse events.
        """
        fn = self.function_table.setOverlayTransformTrackedDeviceComponent
        if componentName is not None:
            componentName = bytes(componentName, encoding='utf-8')
        error = fn(overlayHandle, deviceIndex, componentName)
        openvr.error_code.OverlayError.check_error_value(error)

    def getOverlayTransformTrackedDeviceComponent(self, overlayHandle):
        """Gets the transform information when the overlay is rendering on a component."""
        fn = self.function_table.getOverlayTransformTrackedDeviceComponent
        deviceIndex = TrackedDeviceIndex_t()
        componentNameSize = fn(overlayHandle, byref(deviceIndex), None, 0)
        if componentNameSize == 0:
            return ''
        componentName = ctypes.create_string_buffer(componentNameSize)
        error = fn(overlayHandle, byref(deviceIndex), componentName, componentNameSize)
        openvr.error_code.OverlayError.check_error_value(error)
        return deviceIndex, bytes(componentName.value).decode('utf-8')

    def getOverlayTransformOverlayRelative(self, overlayHandle):
        """Gets the transform if it is relative to another overlay. Returns an error if the transform is some other type."""
        fn = self.function_table.getOverlayTransformOverlayRelative
        overlayHandleParent = VROverlayHandle_t()
        parentOverlayToOverlayTransform = HmdMatrix34_t()
        error = fn(overlayHandle, byref(overlayHandleParent), byref(parentOverlayToOverlayTransform))
        openvr.error_code.OverlayError.check_error_value(error)
        return overlayHandleParent.value, parentOverlayToOverlayTransform

    def setOverlayTransformOverlayRelative(self, overlayHandle, overlayHandleParent, parentOverlayToOverlayTransform) -> None:
        """Sets the transform to relative to the transform of the specified overlay. This overlays visibility will also track the parents visibility"""
        fn = self.function_table.setOverlayTransformOverlayRelative
        error = fn(overlayHandle, overlayHandleParent, byref(parentOverlayToOverlayTransform))
        openvr.error_code.OverlayError.check_error_value(error)

    def showOverlay(self, overlayHandle) -> None:
        """Shows the VR overlay.  For dashboard overlays, only the Dashboard Manager is allowed to call this."""
        fn = self.function_table.showOverlay
        error = fn(overlayHandle)
        openvr.error_code.OverlayError.check_error_value(error)

    def hideOverlay(self, overlayHandle) -> None:
        """Hides the VR overlay.  For dashboard overlays, only the Dashboard Manager is allowed to call this."""
        fn = self.function_table.hideOverlay
        error = fn(overlayHandle)
        openvr.error_code.OverlayError.check_error_value(error)

    def isOverlayVisible(self, overlayHandle):
        """Returns true if the overlay is visible."""
        fn = self.function_table.isOverlayVisible
        result = fn(overlayHandle)
        return result

    def getTransformForOverlayCoordinates(self, overlayHandle, trackingOrigin, coordinatesInOverlay):
        """Get the transform in 3d space associated with a specific 2d point in the overlay's coordinate space (where 0,0 is the lower left). -Z points out of the overlay"""
        fn = self.function_table.getTransformForOverlayCoordinates
        transform = HmdMatrix34_t()
        error = fn(overlayHandle, trackingOrigin, coordinatesInOverlay, byref(transform))
        openvr.error_code.OverlayError.check_error_value(error)
        return transform

    def pollNextOverlayEvent(self, overlayHandle, event):
        """
        Returns true and fills the event with the next event on the overlay's event queue, if there is one. 
        If there are no events this method returns false. uncbVREvent should be the size in bytes of the VREvent_t struct
        """
        fn = self.function_table.pollNextOverlayEvent
        vREvent = sizeof(VREvent_t)
        result = fn(overlayHandle, byref(event), vREvent)
        return result, event

    def getOverlayInputMethod(self, overlayHandle):
        """Returns the current input settings for the specified overlay."""
        fn = self.function_table.getOverlayInputMethod
        inputMethod = VROverlayInputMethod()
        error = fn(overlayHandle, byref(inputMethod))
        openvr.error_code.OverlayError.check_error_value(error)
        return inputMethod

    def setOverlayInputMethod(self, overlayHandle, inputMethod) -> None:
        """Sets the input settings for the specified overlay."""
        fn = self.function_table.setOverlayInputMethod
        error = fn(overlayHandle, inputMethod)
        openvr.error_code.OverlayError.check_error_value(error)

    def getOverlayMouseScale(self, overlayHandle):
        """
        Gets the mouse scaling factor that is used for mouse events. The actual texture may be a different size, but this is
        typically the size of the underlying UI in pixels.
        """
        fn = self.function_table.getOverlayMouseScale
        mouseScale = HmdVector2_t()
        error = fn(overlayHandle, byref(mouseScale))
        openvr.error_code.OverlayError.check_error_value(error)
        return mouseScale

    def setOverlayMouseScale(self, overlayHandle, mouseScale) -> None:
        """
        Sets the mouse scaling factor that is used for mouse events. The actual texture may be a different size, but this is
        typically the size of the underlying UI in pixels (not in world space).
        """
        fn = self.function_table.setOverlayMouseScale
        error = fn(overlayHandle, byref(mouseScale))
        openvr.error_code.OverlayError.check_error_value(error)

    def computeOverlayIntersection(self, overlayHandle, params):
        """
        Computes the overlay-space pixel coordinates of where the ray intersects the overlay with the
        specified settings. Returns false if there is no intersection.
        """
        fn = self.function_table.computeOverlayIntersection
        results = VROverlayIntersectionResults_t()
        result = fn(overlayHandle, byref(params), byref(results))
        return result, results

    def isHoverTargetOverlay(self, overlayHandle):
        """
        Returns true if the specified overlay is the hover target. An overlay is the hover target when it is the last overlay "moused over" 
        by the virtual mouse pointer
        """
        fn = self.function_table.isHoverTargetOverlay
        result = fn(overlayHandle)
        return result

    def getGamepadFocusOverlay(self):
        """Returns the current Gamepad focus overlay"""
        fn = self.function_table.getGamepadFocusOverlay
        result = fn()
        return result

    def setGamepadFocusOverlay(self, newFocusOverlay) -> None:
        """Sets the current Gamepad focus overlay"""
        fn = self.function_table.setGamepadFocusOverlay
        error = fn(newFocusOverlay)
        openvr.error_code.OverlayError.check_error_value(error)

    def setOverlayNeighbor(self, direction, from_, to) -> None:
        """
        Sets an overlay's neighbor. This will also set the neighbor of the "to" overlay
        to point back to the "from" overlay. If an overlay's neighbor is set to invalid both
        ends will be cleared
        """
        fn = self.function_table.setOverlayNeighbor
        error = fn(direction, from_, to)
        openvr.error_code.OverlayError.check_error_value(error)

    def moveGamepadFocusToNeighbor(self, direction, from_) -> None:
        """
        Changes the Gamepad focus from one overlay to one of its neighbors. Returns VROverlayError_NoNeighbor if there is no
        neighbor in that direction
        """
        fn = self.function_table.moveGamepadFocusToNeighbor
        error = fn(direction, from_)
        openvr.error_code.OverlayError.check_error_value(error)

    def setOverlayDualAnalogTransform(self, overlay, which, center, radius: float) -> None:
        """Sets the analog input to Dual Analog coordinate scale for the specified overlay."""
        fn = self.function_table.setOverlayDualAnalogTransform
        error = fn(overlay, which, byref(center), radius)
        openvr.error_code.OverlayError.check_error_value(error)

    def getOverlayDualAnalogTransform(self, overlay, which):
        """Gets the analog input to Dual Analog coordinate scale for the specified overlay."""
        fn = self.function_table.getOverlayDualAnalogTransform
        center = HmdVector2_t()
        radius = c_float()
        error = fn(overlay, which, byref(center), byref(radius))
        openvr.error_code.OverlayError.check_error_value(error)
        return center, radius.value

    def setOverlayTexture(self, overlayHandle, texture) -> None:
        """
        Texture to draw for the overlay. This function can only be called by the overlay's creator or renderer process (see SetOverlayRenderingPid) .

        OpenGL dirty state:
          glBindTexture
        """
        fn = self.function_table.setOverlayTexture
        error = fn(overlayHandle, byref(texture))
        openvr.error_code.OverlayError.check_error_value(error)

    def clearOverlayTexture(self, overlayHandle) -> None:
        """Use this to tell the overlay system to release the texture set for this overlay."""
        fn = self.function_table.clearOverlayTexture
        error = fn(overlayHandle)
        openvr.error_code.OverlayError.check_error_value(error)

    def setOverlayRaw(self, overlayHandle, buffer, width, height, depth) -> None:
        """
        Separate interface for providing the data as a stream of bytes, but there is an upper bound on data 
        that can be sent. This function can only be called by the overlay's renderer process.
        """
        fn = self.function_table.setOverlayRaw
        error = fn(overlayHandle, byref(buffer), width, height, depth)
        openvr.error_code.OverlayError.check_error_value(error)

    def setOverlayFromFile(self, overlayHandle, filePath: str) -> None:
        """
        Separate interface for providing the image through a filename: can be png or jpg, and should not be bigger than 1920x1080.
        This function can only be called by the overlay's renderer process
        """
        fn = self.function_table.setOverlayFromFile
        if filePath is not None:
            filePath = bytes(filePath, encoding='utf-8')
        error = fn(overlayHandle, filePath)
        openvr.error_code.OverlayError.check_error_value(error)

    def getOverlayTexture(self, overlayHandle, nativeTextureRef):
        """
        Get the native texture handle/device for an overlay you have created.
        On windows this handle will be a ID3D11ShaderResourceView with a ID3D11Texture2D bound.

        The texture will always be sized to match the backing texture you supplied in SetOverlayTexture above.

        You MUST call ReleaseNativeOverlayHandle() with pNativeTextureHandle once you are done with this texture.

        pNativeTextureHandle is an OUTPUT, it will be a pointer to a ID3D11ShaderResourceView *.
        pNativeTextureRef is an INPUT and should be a ID3D11Resource *. The device used by pNativeTextureRef will be used to bind pNativeTextureHandle.
        """
        fn = self.function_table.getOverlayTexture
        nativeTextureHandle = c_void_p()
        width = c_uint32()
        height = c_uint32()
        nativeFormat = c_uint32()
        aPIType = ETextureType()
        colorSpace = EColorSpace()
        textureBounds = VRTextureBounds_t()
        error = fn(overlayHandle, byref(nativeTextureHandle), byref(nativeTextureRef), byref(width), byref(height), byref(nativeFormat), byref(aPIType), byref(colorSpace), byref(textureBounds))
        openvr.error_code.OverlayError.check_error_value(error)
        return nativeTextureHandle.value, width.value, height.value, nativeFormat.value, aPIType, colorSpace, textureBounds

    def releaseNativeOverlayHandle(self, overlayHandle, nativeTextureHandle) -> None:
        """
        Release the pNativeTextureHandle provided from the GetOverlayTexture call, this allows the system to free the underlying GPU resources for this object,
        so only do it once you stop rendering this texture.
        """
        fn = self.function_table.releaseNativeOverlayHandle
        error = fn(overlayHandle, byref(nativeTextureHandle))
        openvr.error_code.OverlayError.check_error_value(error)

    def getOverlayTextureSize(self, overlayHandle):
        """Get the size of the overlay texture"""
        fn = self.function_table.getOverlayTextureSize
        width = c_uint32()
        height = c_uint32()
        error = fn(overlayHandle, byref(width), byref(height))
        openvr.error_code.OverlayError.check_error_value(error)
        return width.value, height.value

    def createDashboardOverlay(self, overlayKey: str, overlayFriendlyName: str):
        """Creates a dashboard overlay and returns its handle"""
        fn = self.function_table.createDashboardOverlay
        if overlayKey is not None:
            overlayKey = bytes(overlayKey, encoding='utf-8')
        if overlayFriendlyName is not None:
            overlayFriendlyName = bytes(overlayFriendlyName, encoding='utf-8')
        mainHandle = VROverlayHandle_t()
        thumbnailHandle = VROverlayHandle_t()
        error = fn(overlayKey, overlayFriendlyName, byref(mainHandle), byref(thumbnailHandle))
        openvr.error_code.OverlayError.check_error_value(error)
        return mainHandle.value, thumbnailHandle.value

    def isDashboardVisible(self):
        """Returns true if the dashboard is visible"""
        fn = self.function_table.isDashboardVisible
        result = fn()
        return result

    def isActiveDashboardOverlay(self, overlayHandle):
        """returns true if the dashboard is visible and the specified overlay is the active system Overlay"""
        fn = self.function_table.isActiveDashboardOverlay
        result = fn(overlayHandle)
        return result

    def setDashboardOverlaySceneProcess(self, overlayHandle, processId) -> None:
        """Sets the dashboard overlay to only appear when the specified process ID has scene focus"""
        fn = self.function_table.setDashboardOverlaySceneProcess
        error = fn(overlayHandle, processId)
        openvr.error_code.OverlayError.check_error_value(error)

    def getDashboardOverlaySceneProcess(self, overlayHandle):
        """Gets the process ID that this dashboard overlay requires to have scene focus"""
        fn = self.function_table.getDashboardOverlaySceneProcess
        processId = c_uint32()
        error = fn(overlayHandle, byref(processId))
        openvr.error_code.OverlayError.check_error_value(error)
        return processId.value

    def showDashboard(self, overlayToShow: str) -> None:
        """Shows the dashboard."""
        fn = self.function_table.showDashboard
        if overlayToShow is not None:
            overlayToShow = bytes(overlayToShow, encoding='utf-8')
        fn(overlayToShow)

    def getPrimaryDashboardDevice(self):
        """Returns the tracked device that has the laser pointer in the dashboard"""
        fn = self.function_table.getPrimaryDashboardDevice
        result = fn()
        return result

    def showKeyboard(self, inputMode, lineInputMode, description: str, charMax, existingText: str, useMinimalMode, userValue) -> None:
        """Show the virtual keyboard to accept input"""
        fn = self.function_table.showKeyboard
        if description is not None:
            description = bytes(description, encoding='utf-8')
        if existingText is not None:
            existingText = bytes(existingText, encoding='utf-8')
        error = fn(inputMode, lineInputMode, description, charMax, existingText, useMinimalMode, userValue)
        openvr.error_code.OverlayError.check_error_value(error)

    def showKeyboardForOverlay(self, overlayHandle, inputMode, lineInputMode, description: str, charMax, existingText: str, useMinimalMode, userValue) -> None:
        fn = self.function_table.showKeyboardForOverlay
        if description is not None:
            description = bytes(description, encoding='utf-8')
        if existingText is not None:
            existingText = bytes(existingText, encoding='utf-8')
        error = fn(overlayHandle, inputMode, lineInputMode, description, charMax, existingText, useMinimalMode, userValue)
        openvr.error_code.OverlayError.check_error_value(error)

    def getKeyboardText(self):
        """Get the text that was entered into the text input"""
        fn = self.function_table.getKeyboardText
        text = fn(None, 0)
        if text == 0:
            return ''
        text = ctypes.create_string_buffer(text)
        fn(text, text)
        return bytes(text.value).decode('utf-8')

    def hideKeyboard(self) -> None:
        """Hide the virtual keyboard"""
        fn = self.function_table.hideKeyboard
        fn()

    def setKeyboardTransformAbsolute(self, trackingOrigin, trackingOriginToKeyboardTransform) -> None:
        """Set the position of the keyboard in world space"""
        fn = self.function_table.setKeyboardTransformAbsolute
        fn(trackingOrigin, byref(trackingOriginToKeyboardTransform))

    def setKeyboardPositionForOverlay(self, overlayHandle, rect) -> None:
        """Set the position of the keyboard in overlay space by telling it to avoid a rectangle in the overlay. Rectangle coords have (0,0) in the bottom left"""
        fn = self.function_table.setKeyboardPositionForOverlay
        fn(overlayHandle, rect)

    def setOverlayIntersectionMask(self, overlayHandle, numMaskPrimitives, primitiveSize=sizeof(VROverlayIntersectionMaskPrimitive_t)):
        """
        Sets a list of primitives to be used for controller ray intersection
        typically the size of the underlying UI in pixels (not in world space).
        """
        fn = self.function_table.setOverlayIntersectionMask
        maskPrimitives = VROverlayIntersectionMaskPrimitive_t()
        error = fn(overlayHandle, byref(maskPrimitives), numMaskPrimitives, primitiveSize)
        openvr.error_code.OverlayError.check_error_value(error)
        return maskPrimitives

    def getOverlayFlags(self, overlayHandle):
        fn = self.function_table.getOverlayFlags
        flags = c_uint32()
        error = fn(overlayHandle, byref(flags))
        openvr.error_code.OverlayError.check_error_value(error)
        return flags.value

    def showMessageOverlay(self, text: str, caption: str, button0Text: str, button1Text: str=None, button2Text: str=None, button3Text: str=None):
        """Show the message overlay. This will block and return you a result."""
        fn = self.function_table.showMessageOverlay
        if text is not None:
            text = bytes(text, encoding='utf-8')
        if caption is not None:
            caption = bytes(caption, encoding='utf-8')
        if button0Text is not None:
            button0Text = bytes(button0Text, encoding='utf-8')
        if button1Text is not None:
            button1Text = bytes(button1Text, encoding='utf-8')
        if button2Text is not None:
            button2Text = bytes(button2Text, encoding='utf-8')
        if button3Text is not None:
            button3Text = bytes(button3Text, encoding='utf-8')
        result = fn(text, caption, button0Text, button1Text, button2Text, button3Text)
        return result

    def closeMessageOverlay(self) -> None:
        """If the calling process owns the overlay and it's open, this will close it."""
        fn = self.function_table.closeMessageOverlay
        fn()


class IVRRenderModels_FnTable(Structure):
    _fields_ = [
        ("loadRenderModel_Async", OPENVR_FNTABLE_CALLTYPE(EVRRenderModelError, c_char_p, POINTER(POINTER(RenderModel_t)))),
        ("freeRenderModel", OPENVR_FNTABLE_CALLTYPE(None, POINTER(RenderModel_t))),
        ("loadTexture_Async", OPENVR_FNTABLE_CALLTYPE(EVRRenderModelError, TextureID_t, POINTER(POINTER(RenderModel_TextureMap_t)))),
        ("freeTexture", OPENVR_FNTABLE_CALLTYPE(None, POINTER(RenderModel_TextureMap_t))),
        ("loadTextureD3D11_Async", OPENVR_FNTABLE_CALLTYPE(EVRRenderModelError, TextureID_t, c_void_p, POINTER(c_void_p))),
        ("loadIntoTextureD3D11_Async", OPENVR_FNTABLE_CALLTYPE(EVRRenderModelError, TextureID_t, c_void_p)),
        ("freeTextureD3D11", OPENVR_FNTABLE_CALLTYPE(None, c_void_p)),
        ("getRenderModelName", OPENVR_FNTABLE_CALLTYPE(c_uint32, c_uint32, c_char_p, c_uint32)),
        ("getRenderModelCount", OPENVR_FNTABLE_CALLTYPE(c_uint32)),
        ("getComponentCount", OPENVR_FNTABLE_CALLTYPE(c_uint32, c_char_p)),
        ("getComponentName", OPENVR_FNTABLE_CALLTYPE(c_uint32, c_char_p, c_uint32, c_char_p, c_uint32)),
        ("getComponentButtonMask", OPENVR_FNTABLE_CALLTYPE(c_uint64, c_char_p, c_char_p)),
        ("getComponentRenderModelName", OPENVR_FNTABLE_CALLTYPE(c_uint32, c_char_p, c_char_p, c_char_p, c_uint32)),
        ("getComponentStateForDevicePath", OPENVR_FNTABLE_CALLTYPE(openvr_bool, c_char_p, c_char_p, VRInputValueHandle_t, POINTER(RenderModel_ControllerMode_State_t), POINTER(RenderModel_ComponentState_t))),
        ("getComponentState", OPENVR_FNTABLE_CALLTYPE(openvr_bool, c_char_p, c_char_p, POINTER(VRControllerState_t), POINTER(RenderModel_ControllerMode_State_t), POINTER(RenderModel_ComponentState_t))),
        ("renderModelHasComponent", OPENVR_FNTABLE_CALLTYPE(openvr_bool, c_char_p, c_char_p)),
        ("getRenderModelThumbnailURL", OPENVR_FNTABLE_CALLTYPE(c_uint32, c_char_p, c_char_p, c_uint32, POINTER(EVRRenderModelError))),
        ("getRenderModelOriginalPath", OPENVR_FNTABLE_CALLTYPE(c_uint32, c_char_p, c_char_p, c_uint32, POINTER(EVRRenderModelError))),
        ("getRenderModelErrorNameFromEnum", OPENVR_FNTABLE_CALLTYPE(c_char_p, EVRRenderModelError)),
    ]


class IVRRenderModels(object):
    def __init__(self):
        version_key = IVRRenderModels_Version
        if not isInterfaceVersionValid(version_key):
            _checkInitError(VRInitError_Init_InterfaceNotFound)
        fn_key = 'FnTable:' + version_key
        fn_type = IVRRenderModels_FnTable
        fn_table_ptr = cast(getGenericInterface(fn_key), POINTER(fn_type))
        if fn_table_ptr is None:
            raise OpenVRError("Error retrieving VR API for IVRRenderModels")
        self.function_table = fn_table_ptr.contents

    def loadRenderModel_Async(self, renderModelName: str):
        """
        Loads and returns a render model for use in the application. pchRenderModelName should be a render model name
        from the Prop_RenderModelName_String property or an absolute path name to a render model on disk. 

        The resulting render model is valid until VR_Shutdown() is called or until FreeRenderModel() is called. When the 
        application is finished with the render model it should call FreeRenderModel() to free the memory associated
        with the model.

        The method returns VRRenderModelError_Loading while the render model is still being loaded.
        The method returns VRRenderModelError_None once loaded successfully, otherwise will return an error.
        """
        fn = self.function_table.loadRenderModel_Async
        if renderModelName is not None:
            renderModelName = bytes(renderModelName, encoding='utf-8')
        renderModel = POINTER(RenderModel_t)()
        error = fn(renderModelName, byref(renderModel))
        if renderModel:
            renderModel = renderModel.contents
        else:
            renderModel = None
        openvr.error_code.RenderModelError.check_error_value(error)
        return renderModel

    def freeRenderModel(self, renderModel) -> None:
        """
        Frees a previously returned render model
        It is safe to call this on a null ptr.
        """
        fn = self.function_table.freeRenderModel
        fn(byref(renderModel))

    def loadTexture_Async(self, textureId):
        """Loads and returns a texture for use in the application."""
        fn = self.function_table.loadTexture_Async
        texture = POINTER(RenderModel_TextureMap_t)()
        error = fn(textureId, byref(texture))
        if texture:
            texture = texture.contents
        else:
            texture = None
        openvr.error_code.RenderModelError.check_error_value(error)
        return texture

    def freeTexture(self, texture) -> None:
        """
        Frees a previously returned texture
        It is safe to call this on a null ptr.
        """
        fn = self.function_table.freeTexture
        fn(byref(texture))

    def loadTextureD3D11_Async(self, textureId, d3D11Device):
        """Creates a D3D11 texture and loads data into it."""
        fn = self.function_table.loadTextureD3D11_Async
        d3D11Texture2D = c_void_p()
        error = fn(textureId, byref(d3D11Device), byref(d3D11Texture2D))
        openvr.error_code.RenderModelError.check_error_value(error)
        return d3D11Texture2D.value

    def loadIntoTextureD3D11_Async(self, textureId, dstTexture) -> None:
        """Helper function to copy the bits into an existing texture."""
        fn = self.function_table.loadIntoTextureD3D11_Async
        error = fn(textureId, byref(dstTexture))
        openvr.error_code.RenderModelError.check_error_value(error)

    def freeTextureD3D11(self, d3D11Texture2D) -> None:
        """Use this to free textures created with LoadTextureD3D11_Async instead of calling Release on them."""
        fn = self.function_table.freeTextureD3D11
        fn(byref(d3D11Texture2D))

    def getRenderModelName(self, renderModelIndex):
        """
        Use this to get the names of available render models.  Index does not correlate to a tracked device index, but
        is only used for iterating over all available render models.  If the index is out of range, this function will return 0.
        Otherwise, it will return the size of the buffer required for the name.
        """
        fn = self.function_table.getRenderModelName
        renderModelNameLen = fn(renderModelIndex, None, 0)
        if renderModelNameLen == 0:
            return ''
        renderModelName = ctypes.create_string_buffer(renderModelNameLen)
        fn(renderModelIndex, renderModelName, renderModelNameLen)
        return bytes(renderModelName.value).decode('utf-8')

    def getRenderModelCount(self):
        """Returns the number of available render models."""
        fn = self.function_table.getRenderModelCount
        result = fn()
        return result

    def getComponentCount(self, renderModelName: str):
        """
        Returns the number of components of the specified render model.
        Components are useful when client application wish to draw, label, or otherwise interact with components of tracked objects.
        Examples controller components:
         renderable things such as triggers, buttons
         non-renderable things which include coordinate systems such as 'tip', 'base', a neutral controller agnostic hand-pose
         If all controller components are enumerated and rendered, it will be equivalent to drawing the traditional render model
         Returns 0 if components not supported, >0 otherwise
        """
        fn = self.function_table.getComponentCount
        if renderModelName is not None:
            renderModelName = bytes(renderModelName, encoding='utf-8')
        result = fn(renderModelName)
        return result

    def getComponentName(self, renderModelName: str, componentIndex):
        """
        Use this to get the names of available components.  Index does not correlate to a tracked device index, but
        is only used for iterating over all available components.  If the index is out of range, this function will return 0.
        Otherwise, it will return the size of the buffer required for the name.
        """
        fn = self.function_table.getComponentName
        if renderModelName is not None:
            renderModelName = bytes(renderModelName, encoding='utf-8')
        componentNameLen = fn(renderModelName, componentIndex, None, 0)
        if componentNameLen == 0:
            return ''
        componentName = ctypes.create_string_buffer(componentNameLen)
        fn(renderModelName, componentIndex, componentName, componentNameLen)
        return bytes(componentName.value).decode('utf-8')

    def getComponentButtonMask(self, renderModelName: str, componentName: str):
        """
        Get the button mask for all buttons associated with this component
        If no buttons (or axes) are associated with this component, return 0
        Note: multiple components may be associated with the same button. Ex: two grip buttons on a single controller.
        Note: A single component may be associated with multiple buttons. Ex: A trackpad which also provides "D-pad" functionality
        """
        fn = self.function_table.getComponentButtonMask
        if renderModelName is not None:
            renderModelName = bytes(renderModelName, encoding='utf-8')
        if componentName is not None:
            componentName = bytes(componentName, encoding='utf-8')
        result = fn(renderModelName, componentName)
        return result

    def getComponentRenderModelName(self, renderModelName: str, componentName: str):
        """
        Use this to get the render model name for the specified rendermode/component combination, to be passed to LoadRenderModel.
        If the component name is out of range, this function will return 0.
        Otherwise, it will return the size of the buffer required for the name.
        """
        fn = self.function_table.getComponentRenderModelName
        if renderModelName is not None:
            renderModelName = bytes(renderModelName, encoding='utf-8')
        if componentName is not None:
            componentName = bytes(componentName, encoding='utf-8')
        componentRenderModelNameLen = fn(renderModelName, componentName, None, 0)
        if componentRenderModelNameLen == 0:
            return ''
        componentRenderModelName = ctypes.create_string_buffer(componentRenderModelNameLen)
        fn(renderModelName, componentName, componentRenderModelName, componentRenderModelNameLen)
        return bytes(componentRenderModelName.value).decode('utf-8')

    def getComponentStateForDevicePath(self, renderModelName: str, componentName: str, devicePath, state):
        """
        Use this to query information about the component, as a function of the controller state.

        For dynamic controller components (ex: trigger) values will reflect component motions
        For static components this will return a consistent value independent of the VRControllerState_t

        If the pchRenderModelName or pchComponentName is invalid, this will return false (and transforms will be set to identity).
        Otherwise, return true
        Note: For dynamic objects, visibility may be dynamic. (I.e., true/false will be returned based on controller state and controller mode state )
        """
        fn = self.function_table.getComponentStateForDevicePath
        if renderModelName is not None:
            renderModelName = bytes(renderModelName, encoding='utf-8')
        if componentName is not None:
            componentName = bytes(componentName, encoding='utf-8')
        componentState = RenderModel_ComponentState_t()
        result = fn(renderModelName, componentName, devicePath, byref(state), byref(componentState))
        return result, componentState

    def getComponentState(self, renderModelName: str, componentName: str, controllerState, state):
        """This version of GetComponentState takes a controller state block instead of an action origin. This function is deprecated. You should use the new input system and GetComponentStateForDevicePath instead."""
        fn = self.function_table.getComponentState
        if renderModelName is not None:
            renderModelName = bytes(renderModelName, encoding='utf-8')
        if componentName is not None:
            componentName = bytes(componentName, encoding='utf-8')
        componentState = RenderModel_ComponentState_t()
        result = fn(renderModelName, componentName, byref(controllerState), byref(state), byref(componentState))
        return result, componentState

    def renderModelHasComponent(self, renderModelName: str, componentName: str):
        """Returns true if the render model has a component with the specified name"""
        fn = self.function_table.renderModelHasComponent
        if renderModelName is not None:
            renderModelName = bytes(renderModelName, encoding='utf-8')
        if componentName is not None:
            componentName = bytes(componentName, encoding='utf-8')
        result = fn(renderModelName, componentName)
        return result

    def getRenderModelThumbnailURL(self, renderModelName: str):
        """Returns the URL of the thumbnail image for this rendermodel"""
        fn = self.function_table.getRenderModelThumbnailURL
        if renderModelName is not None:
            renderModelName = bytes(renderModelName, encoding='utf-8')
        error = EVRRenderModelError()
        thumbnailURLLen = fn(renderModelName, None, 0, byref(error))
        if thumbnailURLLen == 0:
            return ''
        thumbnailURL = ctypes.create_string_buffer(thumbnailURLLen)
        fn(renderModelName, thumbnailURL, thumbnailURLLen, byref(error))
        openvr.error_code.RenderModelError.check_error_value(error.value)
        return bytes(thumbnailURL.value).decode('utf-8')

    def getRenderModelOriginalPath(self, renderModelName: str):
        """
        Provides a render model path that will load the unskinned model if the model name provided has been replace by the user. If the model
        hasn't been replaced the path value will still be a valid path to load the model. Pass this to LoadRenderModel_Async, etc. to load the
        model.
        """
        fn = self.function_table.getRenderModelOriginalPath
        if renderModelName is not None:
            renderModelName = bytes(renderModelName, encoding='utf-8')
        error = EVRRenderModelError()
        originalPathLen = fn(renderModelName, None, 0, byref(error))
        if originalPathLen == 0:
            return ''
        originalPath = ctypes.create_string_buffer(originalPathLen)
        fn(renderModelName, originalPath, originalPathLen, byref(error))
        openvr.error_code.RenderModelError.check_error_value(error.value)
        return bytes(originalPath.value).decode('utf-8')

    def getRenderModelErrorNameFromEnum(self, error):
        """Returns a string for a render model error"""
        fn = self.function_table.getRenderModelErrorNameFromEnum
        result = fn(error)
        return result


class IVRExtendedDisplay_FnTable(Structure):
    _fields_ = [
        ("getWindowBounds", OPENVR_FNTABLE_CALLTYPE(None, POINTER(c_int32), POINTER(c_int32), POINTER(c_uint32), POINTER(c_uint32))),
        ("getEyeOutputViewport", OPENVR_FNTABLE_CALLTYPE(None, EVREye, POINTER(c_uint32), POINTER(c_uint32), POINTER(c_uint32), POINTER(c_uint32))),
        ("getDXGIOutputInfo", OPENVR_FNTABLE_CALLTYPE(None, POINTER(c_int32), POINTER(c_int32))),
    ]


class IVRExtendedDisplay(object):
    """
    NOTE: Use of this interface is not recommended in production applications. It will not work for displays which use
    direct-to-display mode. Creating our own window is also incompatible with the VR compositor and is not available when the compositor is running.
    """

    def __init__(self):
        version_key = IVRExtendedDisplay_Version
        if not isInterfaceVersionValid(version_key):
            _checkInitError(VRInitError_Init_InterfaceNotFound)
        fn_key = 'FnTable:' + version_key
        fn_type = IVRExtendedDisplay_FnTable
        fn_table_ptr = cast(getGenericInterface(fn_key), POINTER(fn_type))
        if fn_table_ptr is None:
            raise OpenVRError("Error retrieving VR API for IVRExtendedDisplay")
        self.function_table = fn_table_ptr.contents

    def getWindowBounds(self):
        """Size and position that the window needs to be on the VR display."""
        fn = self.function_table.getWindowBounds
        x = c_int32()
        y = c_int32()
        width = c_uint32()
        height = c_uint32()
        fn(byref(x), byref(y), byref(width), byref(height))
        return x.value, y.value, width.value, height.value

    def getEyeOutputViewport(self, eye):
        """Gets the viewport in the frame buffer to draw the output of the distortion into"""
        fn = self.function_table.getEyeOutputViewport
        x = c_uint32()
        y = c_uint32()
        width = c_uint32()
        height = c_uint32()
        fn(eye, byref(x), byref(y), byref(width), byref(height))
        return x.value, y.value, width.value, height.value

    def getDXGIOutputInfo(self):
        """
        [D3D10/11 Only]
        Returns the adapter index and output index that the user should pass into EnumAdapters and EnumOutputs
        to create the device and swap chain in DX10 and DX11. If an error occurs both indices will be set to -1.
        """
        fn = self.function_table.getDXGIOutputInfo
        adapterIndex = c_int32()
        adapterOutputIndex = c_int32()
        fn(byref(adapterIndex), byref(adapterOutputIndex))
        return adapterIndex.value, adapterOutputIndex.value


class IVRTrackedCamera_FnTable(Structure):
    _fields_ = [
        ("getCameraErrorNameFromEnum", OPENVR_FNTABLE_CALLTYPE(c_char_p, EVRTrackedCameraError)),
        ("hasCamera", OPENVR_FNTABLE_CALLTYPE(EVRTrackedCameraError, TrackedDeviceIndex_t, POINTER(openvr_bool))),
        ("getCameraFrameSize", OPENVR_FNTABLE_CALLTYPE(EVRTrackedCameraError, TrackedDeviceIndex_t, EVRTrackedCameraFrameType, POINTER(c_uint32), POINTER(c_uint32), POINTER(c_uint32))),
        ("getCameraIntrinsics", OPENVR_FNTABLE_CALLTYPE(EVRTrackedCameraError, TrackedDeviceIndex_t, c_uint32, EVRTrackedCameraFrameType, POINTER(HmdVector2_t), POINTER(HmdVector2_t))),
        ("getCameraProjection", OPENVR_FNTABLE_CALLTYPE(EVRTrackedCameraError, TrackedDeviceIndex_t, c_uint32, EVRTrackedCameraFrameType, c_float, c_float, POINTER(HmdMatrix44_t))),
        ("acquireVideoStreamingService", OPENVR_FNTABLE_CALLTYPE(EVRTrackedCameraError, TrackedDeviceIndex_t, POINTER(TrackedCameraHandle_t))),
        ("releaseVideoStreamingService", OPENVR_FNTABLE_CALLTYPE(EVRTrackedCameraError, TrackedCameraHandle_t)),
        ("getVideoStreamFrameBuffer", OPENVR_FNTABLE_CALLTYPE(EVRTrackedCameraError, TrackedCameraHandle_t, EVRTrackedCameraFrameType, c_void_p, c_uint32, POINTER(CameraVideoStreamFrameHeader_t), c_uint32)),
        ("getVideoStreamTextureSize", OPENVR_FNTABLE_CALLTYPE(EVRTrackedCameraError, TrackedDeviceIndex_t, EVRTrackedCameraFrameType, POINTER(VRTextureBounds_t), POINTER(c_uint32), POINTER(c_uint32))),
        ("getVideoStreamTextureD3D11", OPENVR_FNTABLE_CALLTYPE(EVRTrackedCameraError, TrackedCameraHandle_t, EVRTrackedCameraFrameType, c_void_p, POINTER(c_void_p), POINTER(CameraVideoStreamFrameHeader_t), c_uint32)),
        ("getVideoStreamTextureGL", OPENVR_FNTABLE_CALLTYPE(EVRTrackedCameraError, TrackedCameraHandle_t, EVRTrackedCameraFrameType, POINTER(glUInt_t), POINTER(CameraVideoStreamFrameHeader_t), c_uint32)),
        ("releaseVideoStreamTextureGL", OPENVR_FNTABLE_CALLTYPE(EVRTrackedCameraError, TrackedCameraHandle_t, glUInt_t)),
    ]


class IVRTrackedCamera(object):
    def __init__(self):
        version_key = IVRTrackedCamera_Version
        if not isInterfaceVersionValid(version_key):
            _checkInitError(VRInitError_Init_InterfaceNotFound)
        fn_key = 'FnTable:' + version_key
        fn_type = IVRTrackedCamera_FnTable
        fn_table_ptr = cast(getGenericInterface(fn_key), POINTER(fn_type))
        if fn_table_ptr is None:
            raise OpenVRError("Error retrieving VR API for IVRTrackedCamera")
        self.function_table = fn_table_ptr.contents

    def getCameraErrorNameFromEnum(self, cameraError):
        """Returns a string for an error"""
        fn = self.function_table.getCameraErrorNameFromEnum
        result = fn(cameraError)
        return result

    def hasCamera(self, deviceIndex):
        """For convenience, same as tracked property request Prop_HasCamera_Bool"""
        fn = self.function_table.hasCamera
        hasCamera = openvr_bool()
        error = fn(deviceIndex, byref(hasCamera))
        openvr.error_code.TrackedCameraError.check_error_value(error)
        return hasCamera

    def getCameraFrameSize(self, deviceIndex, frameType):
        """Gets size of the image frame."""
        fn = self.function_table.getCameraFrameSize
        width = c_uint32()
        height = c_uint32()
        frameBufferSize = c_uint32()
        error = fn(deviceIndex, frameType, byref(width), byref(height), byref(frameBufferSize))
        openvr.error_code.TrackedCameraError.check_error_value(error)
        return width.value, height.value, frameBufferSize.value

    def getCameraIntrinsics(self, deviceIndex, cameraIndex, frameType):
        fn = self.function_table.getCameraIntrinsics
        focalLength = HmdVector2_t()
        center = HmdVector2_t()
        error = fn(deviceIndex, cameraIndex, frameType, byref(focalLength), byref(center))
        openvr.error_code.TrackedCameraError.check_error_value(error)
        return focalLength, center

    def getCameraProjection(self, deviceIndex, cameraIndex, frameType, zNear: float, zFar: float):
        fn = self.function_table.getCameraProjection
        projection = HmdMatrix44_t()
        error = fn(deviceIndex, cameraIndex, frameType, zNear, zFar, byref(projection))
        openvr.error_code.TrackedCameraError.check_error_value(error)
        return projection

    def acquireVideoStreamingService(self, deviceIndex):
        """
        Acquiring streaming service permits video streaming for the caller. Releasing hints the system that video services do not need to be maintained for this client.
        If the camera has not already been activated, a one time spin up may incur some auto exposure as well as initial streaming frame delays.
        The camera should be considered a global resource accessible for shared consumption but not exclusive to any caller.
        The camera may go inactive due to lack of active consumers or headset idleness.
        """
        fn = self.function_table.acquireVideoStreamingService
        handle = TrackedCameraHandle_t()
        error = fn(deviceIndex, byref(handle))
        openvr.error_code.TrackedCameraError.check_error_value(error)
        return handle

    def releaseVideoStreamingService(self, trackedCamera) -> None:
        fn = self.function_table.releaseVideoStreamingService
        error = fn(trackedCamera)
        openvr.error_code.TrackedCameraError.check_error_value(error)

    def getVideoStreamFrameBuffer(self, trackedCamera, frameType, frameBuffer, frameBufferSize):
        """
        Copies the image frame into a caller's provided buffer. The image data is currently provided as RGBA data, 4 bytes per pixel.
        A caller can provide null for the framebuffer or frameheader if not desired. Requesting the frame header first, followed by the frame buffer allows
        the caller to determine if the frame as advanced per the frame header sequence. 
        If there is no frame available yet, due to initial camera spinup or re-activation, the error will be VRTrackedCameraError_NoFrameAvailable.
        Ideally a caller should be polling at ~16ms intervals
        """
        fn = self.function_table.getVideoStreamFrameBuffer
        frameHeader = CameraVideoStreamFrameHeader_t()
        frameHeaderSize = sizeof(CameraVideoStreamFrameHeader_t)
        error = fn(trackedCamera, frameType, byref(frameBuffer), frameBufferSize, byref(frameHeader), frameHeaderSize)
        openvr.error_code.TrackedCameraError.check_error_value(error)
        return frameHeader

    def getVideoStreamTextureSize(self, deviceIndex, frameType):
        """Gets size of the image frame."""
        fn = self.function_table.getVideoStreamTextureSize
        textureBounds = VRTextureBounds_t()
        width = c_uint32()
        height = c_uint32()
        error = fn(deviceIndex, frameType, byref(textureBounds), byref(width), byref(height))
        openvr.error_code.TrackedCameraError.check_error_value(error)
        return textureBounds, width.value, height.value

    def getVideoStreamTextureD3D11(self, trackedCamera, frameType, d3D11DeviceOrResource):
        """
        Access a shared D3D11 texture for the specified tracked camera stream.
        The camera frame type VRTrackedCameraFrameType_Undistorted is not supported directly as a shared texture. It is an interior subregion of the shared texture VRTrackedCameraFrameType_MaximumUndistorted.
        Instead, use GetVideoStreamTextureSize() with VRTrackedCameraFrameType_Undistorted to determine the proper interior subregion bounds along with GetVideoStreamTextureD3D11() with
        VRTrackedCameraFrameType_MaximumUndistorted to provide the texture. The VRTrackedCameraFrameType_MaximumUndistorted will yield an image where the invalid regions are decoded
        by the alpha channel having a zero component. The valid regions all have a non-zero alpha component. The subregion as described by VRTrackedCameraFrameType_Undistorted 
        guarantees a rectangle where all pixels are valid.
        """
        fn = self.function_table.getVideoStreamTextureD3D11
        d3D11ShaderResourceView = c_void_p()
        frameHeader = CameraVideoStreamFrameHeader_t()
        frameHeaderSize = sizeof(CameraVideoStreamFrameHeader_t)
        error = fn(trackedCamera, frameType, byref(d3D11DeviceOrResource), byref(d3D11ShaderResourceView), byref(frameHeader), frameHeaderSize)
        openvr.error_code.TrackedCameraError.check_error_value(error)
        return d3D11ShaderResourceView.value, frameHeader

    def getVideoStreamTextureGL(self, trackedCamera, frameType):
        """Access a shared GL texture for the specified tracked camera stream"""
        fn = self.function_table.getVideoStreamTextureGL
        textureId = glUInt_t()
        frameHeader = CameraVideoStreamFrameHeader_t()
        frameHeaderSize = sizeof(CameraVideoStreamFrameHeader_t)
        error = fn(trackedCamera, frameType, byref(textureId), byref(frameHeader), frameHeaderSize)
        openvr.error_code.TrackedCameraError.check_error_value(error)
        return textureId, frameHeader

    def releaseVideoStreamTextureGL(self, trackedCamera, textureId) -> None:
        fn = self.function_table.releaseVideoStreamTextureGL
        error = fn(trackedCamera, textureId)
        openvr.error_code.TrackedCameraError.check_error_value(error)


class IVRScreenshots_FnTable(Structure):
    _fields_ = [
        ("requestScreenshot", OPENVR_FNTABLE_CALLTYPE(EVRScreenshotError, POINTER(ScreenshotHandle_t), EVRScreenshotType, c_char_p, c_char_p)),
        ("hookScreenshot", OPENVR_FNTABLE_CALLTYPE(EVRScreenshotError, POINTER(EVRScreenshotType), c_int)),
        ("getScreenshotPropertyType", OPENVR_FNTABLE_CALLTYPE(EVRScreenshotType, ScreenshotHandle_t, POINTER(EVRScreenshotError))),
        ("getScreenshotPropertyFilename", OPENVR_FNTABLE_CALLTYPE(c_uint32, ScreenshotHandle_t, EVRScreenshotPropertyFilenames, c_char_p, c_uint32, POINTER(EVRScreenshotError))),
        ("updateScreenshotProgress", OPENVR_FNTABLE_CALLTYPE(EVRScreenshotError, ScreenshotHandle_t, c_float)),
        ("takeStereoScreenshot", OPENVR_FNTABLE_CALLTYPE(EVRScreenshotError, POINTER(ScreenshotHandle_t), c_char_p, c_char_p)),
        ("submitScreenshot", OPENVR_FNTABLE_CALLTYPE(EVRScreenshotError, ScreenshotHandle_t, EVRScreenshotType, c_char_p, c_char_p)),
    ]


class IVRScreenshots(object):
    """Allows the application to generate screenshots"""

    def __init__(self):
        version_key = IVRScreenshots_Version
        if not isInterfaceVersionValid(version_key):
            _checkInitError(VRInitError_Init_InterfaceNotFound)
        fn_key = 'FnTable:' + version_key
        fn_type = IVRScreenshots_FnTable
        fn_table_ptr = cast(getGenericInterface(fn_key), POINTER(fn_type))
        if fn_table_ptr is None:
            raise OpenVRError("Error retrieving VR API for IVRScreenshots")
        self.function_table = fn_table_ptr.contents

    def requestScreenshot(self, type_, previewFilename: str, vRFilename: str):
        """
        Request a screenshot of the requested type.
        A request of the VRScreenshotType_Stereo type will always
        work. Other types will depend on the underlying application
        support.
        The first file name is for the preview image and should be a
        regular screenshot (ideally from the left eye). The second
        is the VR screenshot in the correct format. They should be
        in the same aspect ratio.  Formats per type:
        VRScreenshotType_Mono: the VR filename is ignored (can be
        nullptr), this is a normal flat single shot.
        VRScreenshotType_Stereo:  The VR image should be a
        side-by-side with the left eye image on the left.
        VRScreenshotType_Cubemap: The VR image should be six square
        images composited horizontally.
        VRScreenshotType_StereoPanorama: above/below with left eye
        panorama being the above image.  Image is typically square
        with the panorama being 2x horizontal.

        Note that the VR dashboard will call this function when
        the user presses the screenshot binding (currently System
        Button + Trigger).  If Steam is running, the destination
        file names will be in %TEMP% and will be copied into
        Steam's screenshot library for the running application
        once SubmitScreenshot() is called.
        If Steam is not running, the paths will be in the user's
        documents folder under Documents\\SteamVR\\Screenshots.
        Other VR applications can call this to initiate a
        screenshot outside of user control.
        The destination file names do not need an extension,
        will be replaced with the correct one for the format
        which is currently .png.
        """
        fn = self.function_table.requestScreenshot
        outScreenshotHandle = ScreenshotHandle_t()
        if previewFilename is not None:
            previewFilename = bytes(previewFilename, encoding='utf-8')
        if vRFilename is not None:
            vRFilename = bytes(vRFilename, encoding='utf-8')
        error = fn(byref(outScreenshotHandle), type_, previewFilename, vRFilename)
        openvr.error_code.ScreenshotError.check_error_value(error)
        return outScreenshotHandle

    def hookScreenshot(self, supportedTypes) -> None:
        """
        Called by the running VR application to indicate that it
        wishes to be in charge of screenshots.  If the
        application does not call this, the Compositor will only
        support VRScreenshotType_Stereo screenshots that will be
        captured without notification to the running app.
        Once hooked your application will receive a
        VREvent_RequestScreenshot event when the user presses the
        buttons to take a screenshot.
        """
        fn = self.function_table.hookScreenshot
        if supportedTypes is None:
            types = 0
            supportedTypesArg = None
        elif isinstance(supportedTypes, ctypes.Array):
            types = len(supportedTypes)
            supportedTypesArg = byref(supportedTypes[0])
        else:
            types = 1
            supportedTypes = (EVRScreenshotType * types)()
            supportedTypesArg = byref(supportedTypes[0])
        error = fn(supportedTypesArg, types)
        openvr.error_code.ScreenshotError.check_error_value(error)

    def getScreenshotPropertyType(self, screenshotHandle):
        """
        When your application receives a
        VREvent_RequestScreenshot event, call these functions to get
        the details of the screenshot request.
        """
        fn = self.function_table.getScreenshotPropertyType
        error = EVRScreenshotError()
        result = fn(screenshotHandle, byref(error))
        openvr.error_code.ScreenshotError.check_error_value(error.value)
        return result

    def getScreenshotPropertyFilename(self, screenshotHandle, filenameType):
        """
        Get the filename for the preview or vr image (see
        vr::EScreenshotPropertyFilenames).  The return value is
        the size of the string.
        """
        fn = self.function_table.getScreenshotPropertyFilename
        error = EVRScreenshotError()
        filename = fn(screenshotHandle, filenameType, None, 0, byref(error))
        if filename == 0:
            return ''
        filename = ctypes.create_string_buffer(filename)
        fn(screenshotHandle, filenameType, filename, filename, byref(error))
        openvr.error_code.ScreenshotError.check_error_value(error.value)
        return bytes(filename.value).decode('utf-8')

    def updateScreenshotProgress(self, screenshotHandle, progress: float) -> None:
        """
        Call this if the application is taking the screen shot
        will take more than a few ms processing. This will result
        in an overlay being presented that shows a completion
        bar.
        """
        fn = self.function_table.updateScreenshotProgress
        error = fn(screenshotHandle, progress)
        openvr.error_code.ScreenshotError.check_error_value(error)

    def takeStereoScreenshot(self, previewFilename: str, vRFilename: str):
        """
        Tells the compositor to take an internal screenshot of
        type VRScreenshotType_Stereo. It will take the current
        submitted scene textures of the running application and
        write them into the preview image and a side-by-side file
        for the VR image.
        This is similar to request screenshot, but doesn't ever
        talk to the application, just takes the shot and submits.
        """
        fn = self.function_table.takeStereoScreenshot
        outScreenshotHandle = ScreenshotHandle_t()
        if previewFilename is not None:
            previewFilename = bytes(previewFilename, encoding='utf-8')
        if vRFilename is not None:
            vRFilename = bytes(vRFilename, encoding='utf-8')
        error = fn(byref(outScreenshotHandle), previewFilename, vRFilename)
        openvr.error_code.ScreenshotError.check_error_value(error)
        return outScreenshotHandle

    def submitScreenshot(self, screenshotHandle, type_, sourcePreviewFilename: str, sourceVRFilename: str) -> None:
        """
        Submit the completed screenshot.  If Steam is running
        this will call into the Steam client and upload the
        screenshot to the screenshots section of the library for
        the running application.  If Steam is not running, this
        function will display a notification to the user that the
        screenshot was taken. The paths should be full paths with
        extensions.
        File paths should be absolute including extensions.
        screenshotHandle can be k_unScreenshotHandleInvalid if this
        was a new shot taking by the app to be saved and not
        initiated by a user (achievement earned or something)
        """
        fn = self.function_table.submitScreenshot
        if sourcePreviewFilename is not None:
            sourcePreviewFilename = bytes(sourcePreviewFilename, encoding='utf-8')
        if sourceVRFilename is not None:
            sourceVRFilename = bytes(sourceVRFilename, encoding='utf-8')
        error = fn(screenshotHandle, type_, sourcePreviewFilename, sourceVRFilename)
        openvr.error_code.ScreenshotError.check_error_value(error)


class IVRResources_FnTable(Structure):
    _fields_ = [
        ("loadSharedResource", OPENVR_FNTABLE_CALLTYPE(c_uint32, c_char_p, c_char_p, c_uint32)),
        ("getResourceFullPath", OPENVR_FNTABLE_CALLTYPE(c_uint32, c_char_p, c_char_p, c_char_p, c_uint32)),
    ]


class IVRResources(object):
    def __init__(self):
        version_key = IVRResources_Version
        if not isInterfaceVersionValid(version_key):
            _checkInitError(VRInitError_Init_InterfaceNotFound)
        fn_key = 'FnTable:' + version_key
        fn_type = IVRResources_FnTable
        fn_table_ptr = cast(getGenericInterface(fn_key), POINTER(fn_type))
        if fn_table_ptr is None:
            raise OpenVRError("Error retrieving VR API for IVRResources")
        self.function_table = fn_table_ptr.contents

    def loadSharedResource(self, resourceName: str, bufferLen):
        """
        Loads the specified resource into the provided buffer if large enough.
        Returns the size in bytes of the buffer required to hold the specified resource.
        """
        fn = self.function_table.loadSharedResource
        if resourceName is not None:
            resourceName = bytes(resourceName, encoding='utf-8')
        buffer = c_char()
        result = fn(resourceName, byref(buffer), bufferLen)
        return result, buffer.value

    def getResourceFullPath(self, resourceName: str, resourceTypeDirectory: str):
        """
        Provides the full path to the specified resource. Resource names can include named directories for
        drivers and other things, and this resolves all of those and returns the actual physical path. 
        pchResourceTypeDirectory is the subdirectory of resources to look in.
        """
        fn = self.function_table.getResourceFullPath
        if resourceName is not None:
            resourceName = bytes(resourceName, encoding='utf-8')
        if resourceTypeDirectory is not None:
            resourceTypeDirectory = bytes(resourceTypeDirectory, encoding='utf-8')
        bufferLen = fn(resourceName, resourceTypeDirectory, None, 0)
        if bufferLen == 0:
            return ''
        pathBuffer = ctypes.create_string_buffer(bufferLen)
        fn(resourceName, resourceTypeDirectory, pathBuffer, bufferLen)
        return bytes(pathBuffer.value).decode('utf-8')


class IVRDriverManager_FnTable(Structure):
    _fields_ = [
        ("getDriverCount", OPENVR_FNTABLE_CALLTYPE(c_uint32)),
        ("getDriverName", OPENVR_FNTABLE_CALLTYPE(c_uint32, DriverId_t, c_char_p, c_uint32)),
        ("getDriverHandle", OPENVR_FNTABLE_CALLTYPE(DriverHandle_t, c_char_p)),
    ]


class IVRDriverManager(object):
    def __init__(self):
        version_key = IVRDriverManager_Version
        if not isInterfaceVersionValid(version_key):
            _checkInitError(VRInitError_Init_InterfaceNotFound)
        fn_key = 'FnTable:' + version_key
        fn_type = IVRDriverManager_FnTable
        fn_table_ptr = cast(getGenericInterface(fn_key), POINTER(fn_type))
        if fn_table_ptr is None:
            raise OpenVRError("Error retrieving VR API for IVRDriverManager")
        self.function_table = fn_table_ptr.contents

    def getDriverCount(self):
        fn = self.function_table.getDriverCount
        result = fn()
        return result

    def getDriverName(self, driver):
        """Returns the length of the number of bytes necessary to hold this string including the trailing null."""
        fn = self.function_table.getDriverName
        bufferSize = fn(driver, None, 0)
        if bufferSize == 0:
            return ''
        value = ctypes.create_string_buffer(bufferSize)
        fn(driver, value, bufferSize)
        return bytes(value.value).decode('utf-8')

    def getDriverHandle(self, driverName: str):
        fn = self.function_table.getDriverHandle
        if driverName is not None:
            driverName = bytes(driverName, encoding='utf-8')
        result = fn(driverName)
        return result


class IVRInput_FnTable(Structure):
    _fields_ = [
        ("setActionManifestPath", OPENVR_FNTABLE_CALLTYPE(EVRInputError, c_char_p)),
        ("getActionSetHandle", OPENVR_FNTABLE_CALLTYPE(EVRInputError, c_char_p, POINTER(VRActionSetHandle_t))),
        ("getActionHandle", OPENVR_FNTABLE_CALLTYPE(EVRInputError, c_char_p, POINTER(VRActionHandle_t))),
        ("getInputSourceHandle", OPENVR_FNTABLE_CALLTYPE(EVRInputError, c_char_p, POINTER(VRInputValueHandle_t))),
        ("updateActionState", OPENVR_FNTABLE_CALLTYPE(EVRInputError, POINTER(VRActiveActionSet_t), c_uint32, c_uint32)),
        ("getDigitalActionData", OPENVR_FNTABLE_CALLTYPE(EVRInputError, VRActionHandle_t, POINTER(InputDigitalActionData_t), c_uint32, VRInputValueHandle_t)),
        ("getAnalogActionData", OPENVR_FNTABLE_CALLTYPE(EVRInputError, VRActionHandle_t, POINTER(InputAnalogActionData_t), c_uint32, VRInputValueHandle_t)),
        ("getPoseActionDataRelativeToNow", OPENVR_FNTABLE_CALLTYPE(EVRInputError, VRActionHandle_t, ETrackingUniverseOrigin, c_float, POINTER(InputPoseActionData_t), c_uint32, VRInputValueHandle_t)),
        ("getPoseActionDataForNextFrame", OPENVR_FNTABLE_CALLTYPE(EVRInputError, VRActionHandle_t, ETrackingUniverseOrigin, POINTER(InputPoseActionData_t), c_uint32, VRInputValueHandle_t)),
        ("getSkeletalActionData", OPENVR_FNTABLE_CALLTYPE(EVRInputError, VRActionHandle_t, POINTER(InputSkeletalActionData_t), c_uint32)),
        ("getBoneCount", OPENVR_FNTABLE_CALLTYPE(EVRInputError, VRActionHandle_t, POINTER(c_uint32))),
        ("getBoneHierarchy", OPENVR_FNTABLE_CALLTYPE(EVRInputError, VRActionHandle_t, POINTER(BoneIndex_t), c_uint32)),
        ("getBoneName", OPENVR_FNTABLE_CALLTYPE(EVRInputError, VRActionHandle_t, BoneIndex_t, c_char_p, c_uint32)),
        ("getSkeletalReferenceTransforms", OPENVR_FNTABLE_CALLTYPE(EVRInputError, VRActionHandle_t, EVRSkeletalTransformSpace, EVRSkeletalReferencePose, POINTER(VRBoneTransform_t), c_uint32)),
        ("getSkeletalTrackingLevel", OPENVR_FNTABLE_CALLTYPE(EVRInputError, VRActionHandle_t, POINTER(EVRSkeletalTrackingLevel))),
        ("getSkeletalBoneData", OPENVR_FNTABLE_CALLTYPE(EVRInputError, VRActionHandle_t, EVRSkeletalTransformSpace, EVRSkeletalMotionRange, POINTER(VRBoneTransform_t), c_uint32)),
        ("getSkeletalSummaryData", OPENVR_FNTABLE_CALLTYPE(EVRInputError, VRActionHandle_t, EVRSummaryType, POINTER(VRSkeletalSummaryData_t))),
        ("getSkeletalBoneDataCompressed", OPENVR_FNTABLE_CALLTYPE(EVRInputError, VRActionHandle_t, EVRSkeletalMotionRange, c_void_p, c_uint32, POINTER(c_uint32))),
        ("decompressSkeletalBoneData", OPENVR_FNTABLE_CALLTYPE(EVRInputError, c_void_p, c_uint32, EVRSkeletalTransformSpace, POINTER(VRBoneTransform_t), c_uint32)),
        ("triggerHapticVibrationAction", OPENVR_FNTABLE_CALLTYPE(EVRInputError, VRActionHandle_t, c_float, c_float, c_float, c_float, VRInputValueHandle_t)),
        ("getActionOrigins", OPENVR_FNTABLE_CALLTYPE(EVRInputError, VRActionSetHandle_t, VRActionHandle_t, POINTER(VRInputValueHandle_t), c_uint32)),
        ("getOriginLocalizedName", OPENVR_FNTABLE_CALLTYPE(EVRInputError, VRInputValueHandle_t, c_char_p, c_uint32, c_int32)),
        ("getOriginTrackedDeviceInfo", OPENVR_FNTABLE_CALLTYPE(EVRInputError, VRInputValueHandle_t, POINTER(InputOriginInfo_t), c_uint32)),
        ("showActionOrigins", OPENVR_FNTABLE_CALLTYPE(EVRInputError, VRActionSetHandle_t, VRActionHandle_t)),
        ("showBindingsForActionSet", OPENVR_FNTABLE_CALLTYPE(EVRInputError, POINTER(VRActiveActionSet_t), c_uint32, c_uint32, VRInputValueHandle_t)),
        ("isUsingLegacyInput", OPENVR_FNTABLE_CALLTYPE(openvr_bool)),
    ]


class IVRInput(object):
    def __init__(self):
        version_key = IVRInput_Version
        if not isInterfaceVersionValid(version_key):
            _checkInitError(VRInitError_Init_InterfaceNotFound)
        fn_key = 'FnTable:' + version_key
        fn_type = IVRInput_FnTable
        fn_table_ptr = cast(getGenericInterface(fn_key), POINTER(fn_type))
        if fn_table_ptr is None:
            raise OpenVRError("Error retrieving VR API for IVRInput")
        self.function_table = fn_table_ptr.contents

    def setActionManifestPath(self, actionManifestPath: str) -> None:
        """
        Sets the path to the action manifest JSON file that is used by this application. If this information
        was set on the Steam partner site, calls to this function are ignored. If the Steam partner site
        setting and the path provided by this call are different, VRInputError_MismatchedActionManifest is returned. 
        This call must be made before the first call to UpdateActionState or IVRSystem::PollNextEvent.
        """
        fn = self.function_table.setActionManifestPath
        if actionManifestPath is not None:
            actionManifestPath = bytes(actionManifestPath, encoding='utf-8')
        error = fn(actionManifestPath)
        openvr.error_code.InputError.check_error_value(error)

    def getActionSetHandle(self, actionSetName: str):
        """Returns a handle for an action set. This handle is used for all performance-sensitive calls."""
        fn = self.function_table.getActionSetHandle
        if actionSetName is not None:
            actionSetName = bytes(actionSetName, encoding='utf-8')
        handle = VRActionSetHandle_t()
        error = fn(actionSetName, byref(handle))
        openvr.error_code.InputError.check_error_value(error)
        return handle.value

    def getActionHandle(self, actionName: str):
        """Returns a handle for an action. This handle is used for all performance-sensitive calls."""
        fn = self.function_table.getActionHandle
        if actionName is not None:
            actionName = bytes(actionName, encoding='utf-8')
        handle = VRActionHandle_t()
        error = fn(actionName, byref(handle))
        openvr.error_code.InputError.check_error_value(error)
        return handle.value

    def getInputSourceHandle(self, inputSourcePath: str):
        """Returns a handle for any path in the input system. E.g. /user/hand/right"""
        fn = self.function_table.getInputSourceHandle
        if inputSourcePath is not None:
            inputSourcePath = bytes(inputSourcePath, encoding='utf-8')
        handle = VRInputValueHandle_t()
        error = fn(inputSourcePath, byref(handle))
        openvr.error_code.InputError.check_error_value(error)
        return handle.value

    def updateActionState(self, sets):
        """
        Reads the current state into all actions. After this call, the results of Get*Action calls 
        will be the same until the next call to UpdateActionState.
        """
        fn = self.function_table.updateActionState
        if sets is None:
            setCount = 0
            setsArg = None
        elif isinstance(sets, ctypes.Array):
            setCount = len(sets)
            setsArg = byref(sets[0])
        else:
            setCount = 1
            sets = (VRActiveActionSet_t * setCount)()
            setsArg = byref(sets[0])
        sizeOfVRSelectedActionSet_t = sizeof(VRActiveActionSet_t)
        error = fn(setsArg, sizeOfVRSelectedActionSet_t, setCount)
        openvr.error_code.InputError.check_error_value(error)
        return sets

    def getDigitalActionData(self, action, restrictToDevice):
        """
        Reads the state of a digital action given its handle. This will return VRInputError_WrongType if the type of
        action is something other than digital
        """
        fn = self.function_table.getDigitalActionData
        actionData = InputDigitalActionData_t()
        actionDataSize = sizeof(InputDigitalActionData_t)
        error = fn(action, byref(actionData), actionDataSize, restrictToDevice)
        openvr.error_code.InputError.check_error_value(error)
        return actionData

    def getAnalogActionData(self, action, restrictToDevice):
        """
        Reads the state of an analog action given its handle. This will return VRInputError_WrongType if the type of
        action is something other than analog
        """
        fn = self.function_table.getAnalogActionData
        actionData = InputAnalogActionData_t()
        actionDataSize = sizeof(InputAnalogActionData_t)
        error = fn(action, byref(actionData), actionDataSize, restrictToDevice)
        openvr.error_code.InputError.check_error_value(error)
        return actionData

    def getPoseActionDataRelativeToNow(self, action, origin, predictedSecondsFromNow: float, restrictToDevice):
        """
        Reads the state of a pose action given its handle for the number of seconds relative to now. This
        will generally be called with negative times from the fUpdateTime fields in other actions.
        """
        fn = self.function_table.getPoseActionDataRelativeToNow
        actionData = InputPoseActionData_t()
        actionDataSize = sizeof(InputPoseActionData_t)
        error = fn(action, origin, predictedSecondsFromNow, byref(actionData), actionDataSize, restrictToDevice)
        openvr.error_code.InputError.check_error_value(error)
        return actionData

    def getPoseActionDataForNextFrame(self, action, origin, restrictToDevice):
        """
        Reads the state of a pose action given its handle. The returned values will match the values returned
        by the last call to IVRCompositor::WaitGetPoses().
        """
        fn = self.function_table.getPoseActionDataForNextFrame
        actionData = InputPoseActionData_t()
        actionDataSize = sizeof(InputPoseActionData_t)
        error = fn(action, origin, byref(actionData), actionDataSize, restrictToDevice)
        openvr.error_code.InputError.check_error_value(error)
        return actionData

    def getSkeletalActionData(self, action):
        """Reads the state of a skeletal action given its handle."""
        fn = self.function_table.getSkeletalActionData
        actionData = InputSkeletalActionData_t()
        actionDataSize = sizeof(InputSkeletalActionData_t)
        error = fn(action, byref(actionData), actionDataSize)
        openvr.error_code.InputError.check_error_value(error)
        return actionData

    def getBoneCount(self, action):
        """Reads the number of bones in skeleton associated with the given action"""
        fn = self.function_table.getBoneCount
        boneCount = c_uint32()
        error = fn(action, byref(boneCount))
        openvr.error_code.InputError.check_error_value(error)
        return boneCount.value

    def getBoneHierarchy(self, action, parentIndices):
        """Fills the given array with the index of each bone's parent in the skeleton associated with the given action"""
        fn = self.function_table.getBoneHierarchy
        if parentIndices is None:
            indexArayCount = 0
            parentIndicesArg = None
        elif isinstance(parentIndices, ctypes.Array):
            indexArayCount = len(parentIndices)
            parentIndicesArg = byref(parentIndices[0])
        else:
            indexArayCount = 1
            parentIndices = (BoneIndex_t * indexArayCount)()
            parentIndicesArg = byref(parentIndices[0])
        error = fn(action, parentIndicesArg, indexArayCount)
        openvr.error_code.InputError.check_error_value(error)
        return parentIndices

    def getBoneName(self, action, boneIndex):
        """Fills the given buffer with the name of the bone at the given index in the skeleton associated with the given action"""
        fn = self.function_table.getBoneName
        nameBufferSize = fn(action, boneIndex, None, 0)
        if nameBufferSize == 0:
            return ''
        boneName = ctypes.create_string_buffer(nameBufferSize)
        error = fn(action, boneIndex, boneName, nameBufferSize)
        openvr.error_code.InputError.check_error_value(error)
        return bytes(boneName.value).decode('utf-8')

    def getSkeletalReferenceTransforms(self, action, transformSpace, referencePose, transformArray):
        """Fills the given buffer with the transforms for a specific static skeletal reference pose"""
        fn = self.function_table.getSkeletalReferenceTransforms
        if transformArray is None:
            transformArrayCount = 0
            transformArrayArg = None
        elif isinstance(transformArray, ctypes.Array):
            transformArrayCount = len(transformArray)
            transformArrayArg = byref(transformArray[0])
        else:
            transformArrayCount = 1
            transformArray = (VRBoneTransform_t * transformArrayCount)()
            transformArrayArg = byref(transformArray[0])
        error = fn(action, transformSpace, referencePose, transformArrayArg, transformArrayCount)
        openvr.error_code.InputError.check_error_value(error)
        return transformArray

    def getSkeletalTrackingLevel(self, action):
        """Reads the level of accuracy to which the controller is able to track the user to recreate a skeletal pose"""
        fn = self.function_table.getSkeletalTrackingLevel
        skeletalTrackingLevel = EVRSkeletalTrackingLevel()
        error = fn(action, byref(skeletalTrackingLevel))
        openvr.error_code.InputError.check_error_value(error)
        return skeletalTrackingLevel

    def getSkeletalBoneData(self, action, transformSpace, motionRange, transformArray):
        """Reads the state of the skeletal bone data associated with this action and copies it into the given buffer."""
        fn = self.function_table.getSkeletalBoneData
        if transformArray is None:
            transformArrayCount = 0
            transformArrayArg = None
        elif isinstance(transformArray, ctypes.Array):
            transformArrayCount = len(transformArray)
            transformArrayArg = byref(transformArray[0])
        else:
            transformArrayCount = 1
            transformArray = (VRBoneTransform_t * transformArrayCount)()
            transformArrayArg = byref(transformArray[0])
        error = fn(action, transformSpace, motionRange, transformArrayArg, transformArrayCount)
        openvr.error_code.InputError.check_error_value(error)
        return transformArray

    def getSkeletalSummaryData(self, action, summaryType):
        """Reads summary information about the current pose of the skeleton associated with the given action."""
        fn = self.function_table.getSkeletalSummaryData
        skeletalSummaryData = VRSkeletalSummaryData_t()
        error = fn(action, summaryType, byref(skeletalSummaryData))
        openvr.error_code.InputError.check_error_value(error)
        return skeletalSummaryData

    def getSkeletalBoneDataCompressed(self, action, motionRange, compressedData, compressedSize):
        """
        Reads the state of the skeletal bone data in a compressed form that is suitable for
        sending over the network. The required buffer size will never exceed ( sizeof(VR_BoneTransform_t)*boneCount + 2).
        Usually the size will be much smaller.
        """
        fn = self.function_table.getSkeletalBoneDataCompressed
        requiredCompressedSize = c_uint32()
        error = fn(action, motionRange, byref(compressedData), compressedSize, byref(requiredCompressedSize))
        openvr.error_code.InputError.check_error_value(error)
        return requiredCompressedSize.value

    def decompressSkeletalBoneData(self, compressedBuffer, compressedBufferSize, transformSpace, transformArray):
        """Turns a compressed buffer from GetSkeletalBoneDataCompressed and turns it back into a bone transform array."""
        fn = self.function_table.decompressSkeletalBoneData
        if transformArray is None:
            transformArrayCount = 0
            transformArrayArg = None
        elif isinstance(transformArray, ctypes.Array):
            transformArrayCount = len(transformArray)
            transformArrayArg = byref(transformArray[0])
        else:
            transformArrayCount = 1
            transformArray = (VRBoneTransform_t * transformArrayCount)()
            transformArrayArg = byref(transformArray[0])
        error = fn(byref(compressedBuffer), compressedBufferSize, transformSpace, transformArrayArg, transformArrayCount)
        openvr.error_code.InputError.check_error_value(error)
        return transformArray

    def triggerHapticVibrationAction(self, action, startSecondsFromNow: float, durationSeconds: float, frequency: float, amplitude: float, restrictToDevice) -> None:
        """Triggers a haptic event as described by the specified action"""
        fn = self.function_table.triggerHapticVibrationAction
        error = fn(action, startSecondsFromNow, durationSeconds, frequency, amplitude, restrictToDevice)
        openvr.error_code.InputError.check_error_value(error)

    def getActionOrigins(self, actionSetHandle, digitalActionHandle, originsOut):
        """Retrieve origin handles for an action"""
        fn = self.function_table.getActionOrigins
        if originsOut is None:
            originOutCount = 0
            originsOutArg = None
        elif isinstance(originsOut, ctypes.Array):
            originOutCount = len(originsOut)
            originsOutArg = byref(originsOut[0])
        else:
            originOutCount = 1
            originsOut = (VRInputValueHandle_t * originOutCount)()
            originsOutArg = byref(originsOut[0])
        error = fn(actionSetHandle, digitalActionHandle, originsOutArg, originOutCount)
        openvr.error_code.InputError.check_error_value(error)
        return originsOut.value

    def getOriginLocalizedName(self, origin, stringSectionsToInclude):
        """
        Retrieves the name of the origin in the current language. unStringSectionsToInclude is a bitfield of values in EVRInputStringBits that allows the 
        application to specify which parts of the origin's information it wants a string for.
        """
        fn = self.function_table.getOriginLocalizedName
        nameArraySize = fn(origin, None, 0, stringSectionsToInclude)
        if nameArraySize == 0:
            return ''
        nameArray = ctypes.create_string_buffer(nameArraySize)
        error = fn(origin, nameArray, nameArraySize, stringSectionsToInclude)
        openvr.error_code.InputError.check_error_value(error)
        return bytes(nameArray.value).decode('utf-8')

    def getOriginTrackedDeviceInfo(self, origin):
        """Retrieves useful information for the origin of this action"""
        fn = self.function_table.getOriginTrackedDeviceInfo
        originInfo = InputOriginInfo_t()
        originInfoSize = sizeof(InputOriginInfo_t)
        error = fn(origin, byref(originInfo), originInfoSize)
        openvr.error_code.InputError.check_error_value(error)
        return originInfo

    def showActionOrigins(self, actionSetHandle, actionHandle) -> None:
        """Shows the current binding for the action in-headset"""
        fn = self.function_table.showActionOrigins
        error = fn(actionSetHandle, actionHandle)
        openvr.error_code.InputError.check_error_value(error)

    def showBindingsForActionSet(self, sets, originToHighlight):
        """Shows the current binding all the actions in the specified action sets"""
        fn = self.function_table.showBindingsForActionSet
        if sets is None:
            setCount = 0
            setsArg = None
        elif isinstance(sets, ctypes.Array):
            setCount = len(sets)
            setsArg = byref(sets[0])
        else:
            setCount = 1
            sets = (VRActiveActionSet_t * setCount)()
            setsArg = byref(sets[0])
        sizeOfVRSelectedActionSet_t = sizeof(VRActiveActionSet_t)
        error = fn(setsArg, sizeOfVRSelectedActionSet_t, setCount, originToHighlight)
        openvr.error_code.InputError.check_error_value(error)
        return sets

    def isUsingLegacyInput(self):
        """--------------- Legacy Input -------------------"""
        fn = self.function_table.isUsingLegacyInput
        result = fn()
        return result


class IVRIOBuffer_FnTable(Structure):
    _fields_ = [
        ("open", OPENVR_FNTABLE_CALLTYPE(EIOBufferError, c_char_p, EIOBufferMode, c_uint32, c_uint32, POINTER(IOBufferHandle_t))),
        ("close", OPENVR_FNTABLE_CALLTYPE(EIOBufferError, IOBufferHandle_t)),
        ("read", OPENVR_FNTABLE_CALLTYPE(EIOBufferError, IOBufferHandle_t, c_void_p, c_uint32, POINTER(c_uint32))),
        ("write", OPENVR_FNTABLE_CALLTYPE(EIOBufferError, IOBufferHandle_t, c_void_p, c_uint32)),
        ("propertyContainer", OPENVR_FNTABLE_CALLTYPE(PropertyContainerHandle_t, IOBufferHandle_t)),
        ("hasReaders", OPENVR_FNTABLE_CALLTYPE(openvr_bool, IOBufferHandle_t)),
    ]


class IVRIOBuffer(object):
    """
    ----------------------------------------------------------------------------------------------
    Purpose:
    ----------------------------------------------------------------------------------------------
    """

    def __init__(self):
        version_key = IVRIOBuffer_Version
        if not isInterfaceVersionValid(version_key):
            _checkInitError(VRInitError_Init_InterfaceNotFound)
        fn_key = 'FnTable:' + version_key
        fn_type = IVRIOBuffer_FnTable
        fn_table_ptr = cast(getGenericInterface(fn_key), POINTER(fn_type))
        if fn_table_ptr is None:
            raise OpenVRError("Error retrieving VR API for IVRIOBuffer")
        self.function_table = fn_table_ptr.contents

    def open(self, path: str, mode, elementSize, elements):
        """opens an existing or creates a new IOBuffer of unSize bytes"""
        fn = self.function_table.open
        if path is not None:
            path = bytes(path, encoding='utf-8')
        buffer = IOBufferHandle_t()
        error = fn(path, mode, elementSize, elements, byref(buffer))
        openvr.error_code.IOBufferError.check_error_value(error)
        return buffer

    def close(self, buffer) -> None:
        """closes a previously opened or created buffer"""
        fn = self.function_table.close
        error = fn(buffer)
        openvr.error_code.IOBufferError.check_error_value(error)

    def read(self, buffer, dst, bytes_):
        """reads up to unBytes from buffer into *pDst, returning number of bytes read in *punRead"""
        fn = self.function_table.read
        read = c_uint32()
        error = fn(buffer, byref(dst), bytes_, byref(read))
        openvr.error_code.IOBufferError.check_error_value(error)
        return read.value

    def write(self, buffer, src, bytes_) -> None:
        """writes unBytes of data from *pSrc into a buffer."""
        fn = self.function_table.write
        error = fn(buffer, byref(src), bytes_)
        openvr.error_code.IOBufferError.check_error_value(error)

    def propertyContainer(self, buffer):
        """retrieves the property container of an buffer."""
        fn = self.function_table.propertyContainer
        result = fn(buffer)
        return result

    def hasReaders(self, buffer):
        """inexpensively checks for readers to allow writers to fast-fail potentially expensive copies and writes."""
        fn = self.function_table.hasReaders
        result = fn(buffer)
        return result


class IVRSpatialAnchors_FnTable(Structure):
    _fields_ = [
        ("createSpatialAnchorFromDescriptor", OPENVR_FNTABLE_CALLTYPE(EVRSpatialAnchorError, c_char_p, POINTER(SpatialAnchorHandle_t))),
        ("createSpatialAnchorFromPose", OPENVR_FNTABLE_CALLTYPE(EVRSpatialAnchorError, TrackedDeviceIndex_t, ETrackingUniverseOrigin, POINTER(SpatialAnchorPose_t), POINTER(SpatialAnchorHandle_t))),
        ("getSpatialAnchorPose", OPENVR_FNTABLE_CALLTYPE(EVRSpatialAnchorError, SpatialAnchorHandle_t, ETrackingUniverseOrigin, POINTER(SpatialAnchorPose_t))),
        ("getSpatialAnchorDescriptor", OPENVR_FNTABLE_CALLTYPE(EVRSpatialAnchorError, SpatialAnchorHandle_t, c_char_p, POINTER(c_uint32))),
    ]


class IVRSpatialAnchors(object):
    def __init__(self):
        version_key = IVRSpatialAnchors_Version
        if not isInterfaceVersionValid(version_key):
            _checkInitError(VRInitError_Init_InterfaceNotFound)
        fn_key = 'FnTable:' + version_key
        fn_type = IVRSpatialAnchors_FnTable
        fn_table_ptr = cast(getGenericInterface(fn_key), POINTER(fn_type))
        if fn_table_ptr is None:
            raise OpenVRError("Error retrieving VR API for IVRSpatialAnchors")
        self.function_table = fn_table_ptr.contents

    def createSpatialAnchorFromDescriptor(self, descriptor: str):
        """
        Returns a handle for an spatial anchor described by "descriptor".  On success, pHandle
        will contain a handle valid for this session.  Caller can wait for an event or occasionally
        poll GetSpatialAnchorPose() to find the virtual coordinate associated with this anchor.
        """
        fn = self.function_table.createSpatialAnchorFromDescriptor
        if descriptor is not None:
            descriptor = bytes(descriptor, encoding='utf-8')
        handleOut = SpatialAnchorHandle_t()
        error = fn(descriptor, byref(handleOut))
        openvr.error_code.SpatialAnchorError.check_error_value(error)
        return handleOut.value

    def createSpatialAnchorFromPose(self, deviceIndex, origin):
        """
        Returns a handle for an new spatial anchor at pPose.  On success, pHandle
        will contain a handle valid for this session.  Caller can wait for an event or occasionally
        poll GetSpatialAnchorDescriptor() to find the permanent descriptor for this pose.
        The result of GetSpatialAnchorPose() may evolve from this initial position if the driver chooses
        to update it.
        The anchor will be associated with the driver that provides unDeviceIndex, and the driver may use that specific
        device as a hint for how to best create the anchor.
        The eOrigin must match whatever tracking origin you are working in (seated/standing/raw).
        This should be called when the user is close to (and ideally looking at/interacting with) the target physical
        location.  At that moment, the driver will have the most information about how to recover that physical point
        in the future, and the quality of the anchor (when the descriptor is re-used) will be highest.
        The caller may decide to apply offsets from this initial pose, but is advised to stay relatively close to the 
        original pose location for highest fidelity.
        """
        fn = self.function_table.createSpatialAnchorFromPose
        pose = SpatialAnchorPose_t()
        handleOut = SpatialAnchorHandle_t()
        error = fn(deviceIndex, origin, byref(pose), byref(handleOut))
        openvr.error_code.SpatialAnchorError.check_error_value(error)
        return pose, handleOut.value

    def getSpatialAnchorPose(self, handle, origin):
        """
        Get the pose for a given handle.  This is intended to be cheap enough to call every frame (or fairly often)
        so that the driver can refine this position when it has more information available.
        """
        fn = self.function_table.getSpatialAnchorPose
        poseOut = SpatialAnchorPose_t()
        error = fn(handle, origin, byref(poseOut))
        openvr.error_code.SpatialAnchorError.check_error_value(error)
        return poseOut

    def getSpatialAnchorDescriptor(self, handle):
        """
        Get the descriptor for a given handle.  This will be empty for handles where the driver has not
        yet built a descriptor.  It will be the application-supplied descriptor for previously saved anchors
        that the application is requesting poses for.  If the driver has called UpdateSpatialAnchorDescriptor()
        already in this session, it will be the descriptor provided by the driver.
        Returns true if the descriptor fits into the buffer, else false.  Buffer size should be at least
        k_unMaxSpatialAnchorDescriptorSize.
        """
        fn = self.function_table.getSpatialAnchorDescriptor
        descriptorBufferLenInOut = fn(handle, None, 0)
        if descriptorBufferLenInOut == 0:
            return ''
        descriptorOut = ctypes.create_string_buffer(descriptorBufferLenInOut)
        error = fn(handle, descriptorOut, descriptorBufferLenInOut)
        openvr.error_code.SpatialAnchorError.check_error_value(error)
        return bytes(descriptorOut.value).decode('utf-8')


####################
# Expose functions #
####################

def _checkInitError(error):
    """
    Replace openvr error return code with a python exception
    """
    if error != VRInitError_None:
        shutdown()
        raise OpenVRError("%s (error number %d)" % (getVRInitErrorAsSymbol(error), error))


# Copying VR_Init inline implementation from https://github.com/ValveSoftware/openvr/blob/master/headers/openvr.h
# and from https://github.com/phr00t/jMonkeyVR/blob/master/src/jmevr/input/OpenVR.java
def init(applicationType, pStartupInfo=None):
    """
    Finds the active installation of the VR API and initializes it. The provided path must be absolute
    or relative to the current working directory. These are the local install versions of the equivalent
    functions in steamvr.h and will work without a local Steam install.
    
    This path is to the "root" of the VR API install. That's the directory with
    the "drivers" directory and a platform (i.e. "win32") directory in it, not the directory with the DLL itself.
    """
    initInternal2(applicationType, pStartupInfo)
    # Retrieve "System" API
    return VRSystem()


def shutdown():
    """
    unloads vrclient.dll. Any interface pointers from the interface are
    invalid after this point
    """
    shutdownInternal()  # OK, this is just like inline definition in openvr.h


_openvr.VR_IsHmdPresent.restype = openvr_bool
_openvr.VR_IsHmdPresent.argtypes = []


def isHmdPresent():
    """
    Returns true if there is an HMD attached. This check is as lightweight as possible and
    can be called outside of VR_Init/VR_Shutdown. It should be used when an application wants
    to know if initializing VR is a possibility but isn't ready to take that step yet.
    """
    fn = _openvr.VR_IsHmdPresent
    result = fn()
    return result


_openvr.VR_IsRuntimeInstalled.restype = openvr_bool
_openvr.VR_IsRuntimeInstalled.argtypes = []


def isRuntimeInstalled():
    """Returns true if the OpenVR runtime is installed."""
    fn = _openvr.VR_IsRuntimeInstalled
    result = fn()
    return result


_openvr.VR_GetRuntimePath.restype = openvr_bool
_openvr.VR_GetRuntimePath.argtypes = [c_char_p, c_uint32, POINTER(c_uint32)]


def getRuntimePath():
    """Returns where the OpenVR runtime is installed."""
    fn = _openvr.VR_GetRuntimePath
    requiredBufferSize = c_uint32()
    pathBuffer = ctypes.create_string_buffer(1)
    fn(pathBuffer, 1, byref(requiredBufferSize))
    bufferSize = requiredBufferSize.value
    if bufferSize == 0:
        return ''
    pathBuffer = ctypes.create_string_buffer(bufferSize)
    fn(pathBuffer, bufferSize, byref(requiredBufferSize))
    return bytes(pathBuffer.value).decode('utf-8')


_openvr.VR_GetVRInitErrorAsSymbol.restype = c_char_p
_openvr.VR_GetVRInitErrorAsSymbol.argtypes = [EVRInitError]


def getVRInitErrorAsSymbol(error):
    """Returns the name of the enum value for an EVRInitError. This function may be called outside of VR_Init()/VR_Shutdown()."""
    fn = _openvr.VR_GetVRInitErrorAsSymbol
    result = fn(error)
    return result


_openvr.VR_GetVRInitErrorAsEnglishDescription.restype = c_char_p
_openvr.VR_GetVRInitErrorAsEnglishDescription.argtypes = [EVRInitError]


def getVRInitErrorAsEnglishDescription(error):
    """
    Returns an English string for an EVRInitError. Applications should call VR_GetVRInitErrorAsSymbol instead and
    use that as a key to look up their own localized error message. This function may be called outside of VR_Init()/VR_Shutdown().
    """
    fn = _openvr.VR_GetVRInitErrorAsEnglishDescription
    result = fn(error)
    return result


_openvr.VR_GetGenericInterface.restype = c_void_p
_openvr.VR_GetGenericInterface.argtypes = [c_char_p, POINTER(EVRInitError)]


def getGenericInterface(interfaceVersion: str):
    """
    Returns the interface of the specified version. This method must be called after VR_Init. The
    pointer returned is valid until VR_Shutdown is called.
    """
    fn = _openvr.VR_GetGenericInterface
    if interfaceVersion is not None:
        interfaceVersion = bytes(interfaceVersion, encoding='utf-8')
    error = EVRInitError()
    result = fn(interfaceVersion, byref(error))
    openvr.error_code.InitError.check_error_value(error.value)
    return result


_openvr.VR_IsInterfaceVersionValid.restype = openvr_bool
_openvr.VR_IsInterfaceVersionValid.argtypes = [c_char_p]


def isInterfaceVersionValid(interfaceVersion: str):
    """Returns whether the interface of the specified version exists."""
    fn = _openvr.VR_IsInterfaceVersionValid
    if interfaceVersion is not None:
        interfaceVersion = bytes(interfaceVersion, encoding='utf-8')
    result = fn(interfaceVersion)
    return result


_openvr.VR_GetInitToken.restype = c_uint32
_openvr.VR_GetInitToken.argtypes = []


def getInitToken():
    """Returns a token that represents whether the VR interface handles need to be reloaded"""
    fn = _openvr.VR_GetInitToken
    result = fn()
    return result


_openvr.VR_InitInternal2.restype = c_uint32
_openvr.VR_InitInternal2.argtypes = [POINTER(EVRInitError), EVRApplicationType, c_char_p]


def initInternal2(applicationType, startupInfo: str):
    fn = _openvr.VR_InitInternal2
    error = EVRInitError()
    if startupInfo is not None:
        startupInfo = bytes(startupInfo, encoding='utf-8')
    result = fn(byref(error), applicationType, startupInfo)
    openvr.error_code.InitError.check_error_value(error.value)
    return result


_openvr.VR_ShutdownInternal.restype = None
_openvr.VR_ShutdownInternal.argtypes = []


def shutdownInternal() -> None:
    fn = _openvr.VR_ShutdownInternal
    fn()
