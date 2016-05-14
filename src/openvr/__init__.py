#!/bin/env python

# Python bindings for OpenVR API version 0.9.20
# from https://github.com/ValveSoftware/openvr
# Created May 7, 2016 Christopher Bruns

import os
import platform
import ctypes
from ctypes import *

from .version import __version__

####################################################################
### Load OpenVR shared library, so we can access it using ctypes ###
####################################################################

# Detect 32-bit vs 64-bit python
if sizeof(c_void_p) == 4:
    _openvr_lib_name = "openvr_api_32"
else:
    _openvr_lib_name = "openvr_api_64"

# Add current directory to PATH, so we can load the DLL from right here.
os.environ['PATH'] += os.pathsep + os.path.dirname(__file__)
_openvr = cdll.LoadLibrary(_openvr_lib_name)

# Function pointer table calling convention
if platform.system() == 'Windows':
    OPENVR_FNTABLE_CALLTYPE = WINFUNCTYPE # __stdcall in openvr_capi.h
else:
    OPENVR_FNTABLE_CALLTYPE = CFUNCTYPE # __cdecl


########################
### Expose constants ###
########################

k_unTrackingStringSize = 32
k_unMaxDriverDebugResponseSize = 32768
k_unTrackedDeviceIndex_Hmd = 0
k_unMaxTrackedDeviceCount = 16
k_unTrackedDeviceIndexInvalid = 4294967295
k_unMaxPropertyStringSize = 32768
k_unControllerStateAxisCount = 5
k_ulOverlayHandleInvalid = 0
IVRSystem_Version = b"IVRSystem_012"
IVRExtendedDisplay_Version = b"IVRExtendedDisplay_001"
k_unMaxApplicationKeyLength = 128
IVRApplications_Version = b"IVRApplications_005"
IVRChaperone_Version = b"IVRChaperone_003"
IVRChaperoneSetup_Version = b"IVRChaperoneSetup_005"
IVRCompositor_Version = b"IVRCompositor_014"
k_unVROverlayMaxKeyLength = 128
k_unVROverlayMaxNameLength = 128
k_unMaxOverlayCount = 32
IVROverlay_Version = b"IVROverlay_011"
k_pch_Controller_Component_GDC2015 = b"gdc2015"
k_pch_Controller_Component_Base = b"base"
k_pch_Controller_Component_Tip = b"tip"
k_pch_Controller_Component_HandGrip = b"handgrip"
k_pch_Controller_Component_Status = b"status"
IVRRenderModels_Version = b"IVRRenderModels_005"
k_unNotificationTextMaxSize = 256
IVRNotifications_Version = b"IVRNotifications_002"
k_unMaxSettingsKeyLength = 128
IVRSettings_Version = b"IVRSettings_001"
k_pch_SteamVR_Section = b"steamvr"
k_pch_SteamVR_RequireHmd_String = b"requireHmd"
k_pch_SteamVR_ForcedDriverKey_String = b"forcedDriver"
k_pch_SteamVR_ForcedHmdKey_String = b"forcedHmd"
k_pch_SteamVR_DisplayDebug_Bool = b"displayDebug"
k_pch_SteamVR_DebugProcessPipe_String = b"debugProcessPipe"
k_pch_SteamVR_EnableDistortion_Bool = b"enableDistortion"
k_pch_SteamVR_DisplayDebugX_Int32 = b"displayDebugX"
k_pch_SteamVR_DisplayDebugY_Int32 = b"displayDebugY"
k_pch_SteamVR_SendSystemButtonToAllApps_Bool = b"sendSystemButtonToAllApps"
k_pch_SteamVR_LogLevel_Int32 = b"loglevel"
k_pch_SteamVR_IPD_Float = b"ipd"
k_pch_SteamVR_Background_String = b"background"
k_pch_SteamVR_GridColor_String = b"gridColor"
k_pch_SteamVR_PlayAreaColor_String = b"playAreaColor"
k_pch_SteamVR_ActivateMultipleDrivers_Bool = b"activateMultipleDrivers"
k_pch_SteamVR_PowerOffOnExit_Bool = b"powerOffOnExit"
k_pch_SteamVR_StandbyAppRunningTimeout_Float = b"standbyAppRunningTimeout"
k_pch_SteamVR_StandbyNoAppTimeout_Float = b"standbyNoAppTimeout"
k_pch_SteamVR_DirectMode_Bool = b"directMode"
k_pch_SteamVR_DirectModeEdidVid_Int32 = b"directModeEdidVid"
k_pch_SteamVR_DirectModeEdidPid_Int32 = b"directModeEdidPid"
k_pch_SteamVR_UsingSpeakers_Bool = b"usingSpeakers"
k_pch_SteamVR_SpeakersForwardYawOffsetDegrees_Float = b"speakersForwardYawOffsetDegrees"
k_pch_SteamVR_BaseStationPowerManagement_Bool = b"basestationPowerManagement"
k_pch_SteamVR_NeverKillProcesses_Bool = b"neverKillProcesses"
k_pch_SteamVR_RenderTargetMultiplier_Float = b"renderTargetMultiplier"
k_pch_SteamVR_AllowReprojection_Bool = b"allowReprojection"
k_pch_Lighthouse_Section = b"driver_lighthouse"
k_pch_Lighthouse_DisableIMU_Bool = b"disableimu"
k_pch_Lighthouse_UseDisambiguation_String = b"usedisambiguation"
k_pch_Lighthouse_DisambiguationDebug_Int32 = b"disambiguationdebug"
k_pch_Lighthouse_PrimaryBasestation_Int32 = b"primarybasestation"
k_pch_Lighthouse_LighthouseName_String = b"lighthousename"
k_pch_Lighthouse_MaxIncidenceAngleDegrees_Float = b"maxincidenceangledegrees"
k_pch_Lighthouse_UseLighthouseDirect_Bool = b"uselighthousedirect"
k_pch_Lighthouse_DBHistory_Bool = b"dbhistory"
k_pch_Lighthouse_OriginOffsetX_Float = b"originoffsetx"
k_pch_Lighthouse_OriginOffsetY_Float = b"originoffsety"
k_pch_Lighthouse_OriginOffsetZ_Float = b"originoffsetz"
k_pch_Lighthouse_HeadingOffset_Float = b"headingoffset"
k_pch_Null_Section = b"driver_null"
k_pch_Null_EnableNullDriver_Bool = b"enable"
k_pch_Null_SerialNumber_String = b"serialNumber"
k_pch_Null_ModelNumber_String = b"modelNumber"
k_pch_Null_WindowX_Int32 = b"windowX"
k_pch_Null_WindowY_Int32 = b"windowY"
k_pch_Null_WindowWidth_Int32 = b"windowWidth"
k_pch_Null_WindowHeight_Int32 = b"windowHeight"
k_pch_Null_RenderWidth_Int32 = b"renderWidth"
k_pch_Null_RenderHeight_Int32 = b"renderHeight"
k_pch_Null_SecondsFromVsyncToPhotons_Float = b"secondsFromVsyncToPhotons"
k_pch_Null_DisplayFrequency_Float = b"displayFrequency"
k_pch_UserInterface_Section = b"userinterface"
k_pch_UserInterface_StatusAlwaysOnTop_Bool = b"StatusAlwaysOnTop"
k_pch_Notifications_Section = b"notifications"
k_pch_Notifications_DoNotDisturb_Bool = b"DoNotDisturb"
k_pch_Keyboard_Section = b"keyboard"
k_pch_Keyboard_TutorialCompletions = b"TutorialCompletions"
k_pch_Keyboard_ScaleX = b"ScaleX"
k_pch_Keyboard_ScaleY = b"ScaleY"
k_pch_Keyboard_OffsetLeftX = b"OffsetLeftX"
k_pch_Keyboard_OffsetRightX = b"OffsetRightX"
k_pch_Keyboard_OffsetY = b"OffsetY"
k_pch_Keyboard_Smoothing = b"Smoothing"
k_pch_Perf_Section = b"perfcheck"
k_pch_Perf_HeuristicActive_Bool = b"heuristicActive"
k_pch_Perf_NotifyInHMD_Bool = b"warnInHMD"
k_pch_Perf_NotifyOnlyOnce_Bool = b"warnOnlyOnce"
k_pch_Perf_AllowTimingStore_Bool = b"allowTimingStore"
k_pch_Perf_SaveTimingsOnExit_Bool = b"saveTimingsOnExit"
k_pch_Perf_TestData_Float = b"perfTestData"
k_pch_CollisionBounds_Section = b"collisionBounds"
k_pch_CollisionBounds_Style_Int32 = b"CollisionBoundsStyle"
k_pch_CollisionBounds_GroundPerimeterOn_Bool = b"CollisionBoundsGroundPerimeterOn"
k_pch_CollisionBounds_CenterMarkerOn_Bool = b"CollisionBoundsCenterMarkerOn"
k_pch_CollisionBounds_PlaySpaceOn_Bool = b"CollisionBoundsPlaySpaceOn"
k_pch_CollisionBounds_FadeDistance_Float = b"CollisionBoundsFadeDistance"
k_pch_CollisionBounds_ColorGammaR_Int32 = b"CollisionBoundsColorGammaR"
k_pch_CollisionBounds_ColorGammaG_Int32 = b"CollisionBoundsColorGammaG"
k_pch_CollisionBounds_ColorGammaB_Int32 = b"CollisionBoundsColorGammaB"
k_pch_CollisionBounds_ColorGammaA_Int32 = b"CollisionBoundsColorGammaA"
k_pch_Camera_Section = b"camera"
k_pch_Camera_EnableCamera_Bool = b"enableCamera"
k_pch_Camera_EnableCameraInDashboard_Bool = b"enableCameraInDashboard"
k_pch_Camera_EnableCameraForCollisionBounds_Bool = b"enableCameraForCollisionBounds"
k_pch_Camera_EnableCameraForRoomView_Bool = b"enableCameraForRoomView"
k_pch_Camera_BoundsColorGammaR_Int32 = b"cameraBoundsColorGammaR"
k_pch_Camera_BoundsColorGammaG_Int32 = b"cameraBoundsColorGammaG"
k_pch_Camera_BoundsColorGammaB_Int32 = b"cameraBoundsColorGammaB"
k_pch_Camera_BoundsColorGammaA_Int32 = b"cameraBoundsColorGammaA"
k_pch_audio_Section = b"audio"
k_pch_audio_OnPlaybackDevice_String = b"onPlaybackDevice"
k_pch_audio_OnRecordDevice_String = b"onRecordDevice"
k_pch_audio_OnPlaybackMirrorDevice_String = b"onPlaybackMirrorDevice"
k_pch_audio_OffPlaybackDevice_String = b"offPlaybackDevice"
k_pch_audio_OffRecordDevice_String = b"offRecordDevice"
k_pch_audio_VIVEHDMIGain = b"viveHDMIGain"

#############################
### Expose enum constants ###
#############################

ENUM_TYPE = c_uint32

EVREye = ENUM_TYPE
Eye_Left = ENUM_TYPE(0)
Eye_Right = ENUM_TYPE(1)

EGraphicsAPIConvention = ENUM_TYPE
API_DirectX = ENUM_TYPE(0)
API_OpenGL = ENUM_TYPE(1)

EColorSpace = ENUM_TYPE
ColorSpace_Auto = ENUM_TYPE(0)
ColorSpace_Gamma = ENUM_TYPE(1)
ColorSpace_Linear = ENUM_TYPE(2)

ETrackingResult = ENUM_TYPE
TrackingResult_Uninitialized = ENUM_TYPE(1)
TrackingResult_Calibrating_InProgress = ENUM_TYPE(100)
TrackingResult_Calibrating_OutOfRange = ENUM_TYPE(101)
TrackingResult_Running_OK = ENUM_TYPE(200)
TrackingResult_Running_OutOfRange = ENUM_TYPE(201)

ETrackedDeviceClass = ENUM_TYPE
TrackedDeviceClass_Invalid = ENUM_TYPE(0)
TrackedDeviceClass_HMD = ENUM_TYPE(1)
TrackedDeviceClass_Controller = ENUM_TYPE(2)
TrackedDeviceClass_TrackingReference = ENUM_TYPE(4)
TrackedDeviceClass_Other = ENUM_TYPE(1000)

ETrackedControllerRole = ENUM_TYPE
TrackedControllerRole_Invalid = ENUM_TYPE(0)
TrackedControllerRole_LeftHand = ENUM_TYPE(1)
TrackedControllerRole_RightHand = ENUM_TYPE(2)

ETrackingUniverseOrigin = ENUM_TYPE
TrackingUniverseSeated = ENUM_TYPE(0)
TrackingUniverseStanding = ENUM_TYPE(1)
TrackingUniverseRawAndUncalibrated = ENUM_TYPE(2)

ETrackedDeviceProperty = ENUM_TYPE
Prop_TrackingSystemName_String = ENUM_TYPE(1000)
Prop_ModelNumber_String = ENUM_TYPE(1001)
Prop_SerialNumber_String = ENUM_TYPE(1002)
Prop_RenderModelName_String = ENUM_TYPE(1003)
Prop_WillDriftInYaw_Bool = ENUM_TYPE(1004)
Prop_ManufacturerName_String = ENUM_TYPE(1005)
Prop_TrackingFirmwareVersion_String = ENUM_TYPE(1006)
Prop_HardwareRevision_String = ENUM_TYPE(1007)
Prop_AllWirelessDongleDescriptions_String = ENUM_TYPE(1008)
Prop_ConnectedWirelessDongle_String = ENUM_TYPE(1009)
Prop_DeviceIsWireless_Bool = ENUM_TYPE(1010)
Prop_DeviceIsCharging_Bool = ENUM_TYPE(1011)
Prop_DeviceBatteryPercentage_Float = ENUM_TYPE(1012)
Prop_StatusDisplayTransform_Matrix34 = ENUM_TYPE(1013)
Prop_Firmware_UpdateAvailable_Bool = ENUM_TYPE(1014)
Prop_Firmware_ManualUpdate_Bool = ENUM_TYPE(1015)
Prop_Firmware_ManualUpdateURL_String = ENUM_TYPE(1016)
Prop_HardwareRevision_Uint64 = ENUM_TYPE(1017)
Prop_FirmwareVersion_Uint64 = ENUM_TYPE(1018)
Prop_FPGAVersion_Uint64 = ENUM_TYPE(1019)
Prop_VRCVersion_Uint64 = ENUM_TYPE(1020)
Prop_RadioVersion_Uint64 = ENUM_TYPE(1021)
Prop_DongleVersion_Uint64 = ENUM_TYPE(1022)
Prop_BlockServerShutdown_Bool = ENUM_TYPE(1023)
Prop_CanUnifyCoordinateSystemWithHmd_Bool = ENUM_TYPE(1024)
Prop_ContainsProximitySensor_Bool = ENUM_TYPE(1025)
Prop_DeviceProvidesBatteryStatus_Bool = ENUM_TYPE(1026)
Prop_DeviceCanPowerOff_Bool = ENUM_TYPE(1027)
Prop_Firmware_ProgrammingTarget_String = ENUM_TYPE(1028)
Prop_DeviceClass_Int32 = ENUM_TYPE(1029)
Prop_HasCamera_Bool = ENUM_TYPE(1030)
Prop_DriverVersion_String = ENUM_TYPE(1031)
Prop_Firmware_ForceUpdateRequired_Bool = ENUM_TYPE(1032)
Prop_ReportsTimeSinceVSync_Bool = ENUM_TYPE(2000)
Prop_SecondsFromVsyncToPhotons_Float = ENUM_TYPE(2001)
Prop_DisplayFrequency_Float = ENUM_TYPE(2002)
Prop_UserIpdMeters_Float = ENUM_TYPE(2003)
Prop_CurrentUniverseId_Uint64 = ENUM_TYPE(2004)
Prop_PreviousUniverseId_Uint64 = ENUM_TYPE(2005)
Prop_DisplayFirmwareVersion_Uint64 = ENUM_TYPE(2006)
Prop_IsOnDesktop_Bool = ENUM_TYPE(2007)
Prop_DisplayMCType_Int32 = ENUM_TYPE(2008)
Prop_DisplayMCOffset_Float = ENUM_TYPE(2009)
Prop_DisplayMCScale_Float = ENUM_TYPE(2010)
Prop_EdidVendorID_Int32 = ENUM_TYPE(2011)
Prop_DisplayMCImageLeft_String = ENUM_TYPE(2012)
Prop_DisplayMCImageRight_String = ENUM_TYPE(2013)
Prop_DisplayGCBlackClamp_Float = ENUM_TYPE(2014)
Prop_EdidProductID_Int32 = ENUM_TYPE(2015)
Prop_CameraToHeadTransform_Matrix34 = ENUM_TYPE(2016)
Prop_DisplayGCType_Int32 = ENUM_TYPE(2017)
Prop_DisplayGCOffset_Float = ENUM_TYPE(2018)
Prop_DisplayGCScale_Float = ENUM_TYPE(2019)
Prop_DisplayGCPrescale_Float = ENUM_TYPE(2020)
Prop_DisplayGCImage_String = ENUM_TYPE(2021)
Prop_LensCenterLeftU_Float = ENUM_TYPE(2022)
Prop_LensCenterLeftV_Float = ENUM_TYPE(2023)
Prop_LensCenterRightU_Float = ENUM_TYPE(2024)
Prop_LensCenterRightV_Float = ENUM_TYPE(2025)
Prop_UserHeadToEyeDepthMeters_Float = ENUM_TYPE(2026)
Prop_CameraFirmwareVersion_Uint64 = ENUM_TYPE(2027)
Prop_CameraFirmwareDescription_String = ENUM_TYPE(2028)
Prop_DisplayFPGAVersion_Uint64 = ENUM_TYPE(2029)
Prop_DisplayBootloaderVersion_Uint64 = ENUM_TYPE(2030)
Prop_DisplayHardwareVersion_Uint64 = ENUM_TYPE(2031)
Prop_AudioFirmwareVersion_Uint64 = ENUM_TYPE(2032)
Prop_CameraCompatibilityMode_Int32 = ENUM_TYPE(2033)
Prop_AttachedDeviceId_String = ENUM_TYPE(3000)
Prop_SupportedButtons_Uint64 = ENUM_TYPE(3001)
Prop_Axis0Type_Int32 = ENUM_TYPE(3002)
Prop_Axis1Type_Int32 = ENUM_TYPE(3003)
Prop_Axis2Type_Int32 = ENUM_TYPE(3004)
Prop_Axis3Type_Int32 = ENUM_TYPE(3005)
Prop_Axis4Type_Int32 = ENUM_TYPE(3006)
Prop_FieldOfViewLeftDegrees_Float = ENUM_TYPE(4000)
Prop_FieldOfViewRightDegrees_Float = ENUM_TYPE(4001)
Prop_FieldOfViewTopDegrees_Float = ENUM_TYPE(4002)
Prop_FieldOfViewBottomDegrees_Float = ENUM_TYPE(4003)
Prop_TrackingRangeMinimumMeters_Float = ENUM_TYPE(4004)
Prop_TrackingRangeMaximumMeters_Float = ENUM_TYPE(4005)
Prop_ModeLabel_String = ENUM_TYPE(4006)
Prop_VendorSpecific_Reserved_Start = ENUM_TYPE(10000)
Prop_VendorSpecific_Reserved_End = ENUM_TYPE(10999)

ETrackedPropertyError = ENUM_TYPE
TrackedProp_Success = ENUM_TYPE(0)
TrackedProp_WrongDataType = ENUM_TYPE(1)
TrackedProp_WrongDeviceClass = ENUM_TYPE(2)
TrackedProp_BufferTooSmall = ENUM_TYPE(3)
TrackedProp_UnknownProperty = ENUM_TYPE(4)
TrackedProp_InvalidDevice = ENUM_TYPE(5)
TrackedProp_CouldNotContactServer = ENUM_TYPE(6)
TrackedProp_ValueNotProvidedByDevice = ENUM_TYPE(7)
TrackedProp_StringExceedsMaximumLength = ENUM_TYPE(8)
TrackedProp_NotYetAvailable = ENUM_TYPE(9)

EVRSubmitFlags = ENUM_TYPE
Submit_Default = ENUM_TYPE(0)
Submit_LensDistortionAlreadyApplied = ENUM_TYPE(1)
Submit_GlRenderBuffer = ENUM_TYPE(2)

EVRState = ENUM_TYPE
VRState_Undefined = ENUM_TYPE(-1)
VRState_Off = ENUM_TYPE(0)
VRState_Searching = ENUM_TYPE(1)
VRState_Searching_Alert = ENUM_TYPE(2)
VRState_Ready = ENUM_TYPE(3)
VRState_Ready_Alert = ENUM_TYPE(4)
VRState_NotReady = ENUM_TYPE(5)
VRState_Standby = ENUM_TYPE(6)

EVREventType = ENUM_TYPE
VREvent_None = ENUM_TYPE(0)
VREvent_TrackedDeviceActivated = ENUM_TYPE(100)
VREvent_TrackedDeviceDeactivated = ENUM_TYPE(101)
VREvent_TrackedDeviceUpdated = ENUM_TYPE(102)
VREvent_TrackedDeviceUserInteractionStarted = ENUM_TYPE(103)
VREvent_TrackedDeviceUserInteractionEnded = ENUM_TYPE(104)
VREvent_IpdChanged = ENUM_TYPE(105)
VREvent_EnterStandbyMode = ENUM_TYPE(106)
VREvent_LeaveStandbyMode = ENUM_TYPE(107)
VREvent_TrackedDeviceRoleChanged = ENUM_TYPE(108)
VREvent_ButtonPress = ENUM_TYPE(200)
VREvent_ButtonUnpress = ENUM_TYPE(201)
VREvent_ButtonTouch = ENUM_TYPE(202)
VREvent_ButtonUntouch = ENUM_TYPE(203)
VREvent_MouseMove = ENUM_TYPE(300)
VREvent_MouseButtonDown = ENUM_TYPE(301)
VREvent_MouseButtonUp = ENUM_TYPE(302)
VREvent_FocusEnter = ENUM_TYPE(303)
VREvent_FocusLeave = ENUM_TYPE(304)
VREvent_Scroll = ENUM_TYPE(305)
VREvent_TouchPadMove = ENUM_TYPE(306)
VREvent_InputFocusCaptured = ENUM_TYPE(400)
VREvent_InputFocusReleased = ENUM_TYPE(401)
VREvent_SceneFocusLost = ENUM_TYPE(402)
VREvent_SceneFocusGained = ENUM_TYPE(403)
VREvent_SceneApplicationChanged = ENUM_TYPE(404)
VREvent_SceneFocusChanged = ENUM_TYPE(405)
VREvent_InputFocusChanged = ENUM_TYPE(406)
VREvent_HideRenderModels = ENUM_TYPE(410)
VREvent_ShowRenderModels = ENUM_TYPE(411)
VREvent_OverlayShown = ENUM_TYPE(500)
VREvent_OverlayHidden = ENUM_TYPE(501)
VREvent_DashboardActivated = ENUM_TYPE(502)
VREvent_DashboardDeactivated = ENUM_TYPE(503)
VREvent_DashboardThumbSelected = ENUM_TYPE(504)
VREvent_DashboardRequested = ENUM_TYPE(505)
VREvent_ResetDashboard = ENUM_TYPE(506)
VREvent_RenderToast = ENUM_TYPE(507)
VREvent_ImageLoaded = ENUM_TYPE(508)
VREvent_ShowKeyboard = ENUM_TYPE(509)
VREvent_HideKeyboard = ENUM_TYPE(510)
VREvent_OverlayGamepadFocusGained = ENUM_TYPE(511)
VREvent_OverlayGamepadFocusLost = ENUM_TYPE(512)
VREvent_OverlaySharedTextureChanged = ENUM_TYPE(513)
VREvent_DashboardGuideButtonDown = ENUM_TYPE(514)
VREvent_DashboardGuideButtonUp = ENUM_TYPE(515)
VREvent_Notification_Shown = ENUM_TYPE(600)
VREvent_Notification_Hidden = ENUM_TYPE(601)
VREvent_Notification_BeginInteraction = ENUM_TYPE(602)
VREvent_Notification_Destroyed = ENUM_TYPE(603)
VREvent_Quit = ENUM_TYPE(700)
VREvent_ProcessQuit = ENUM_TYPE(701)
VREvent_QuitAborted_UserPrompt = ENUM_TYPE(702)
VREvent_QuitAcknowledged = ENUM_TYPE(703)
VREvent_DriverRequestedQuit = ENUM_TYPE(704)
VREvent_ChaperoneDataHasChanged = ENUM_TYPE(800)
VREvent_ChaperoneUniverseHasChanged = ENUM_TYPE(801)
VREvent_ChaperoneTempDataHasChanged = ENUM_TYPE(802)
VREvent_ChaperoneSettingsHaveChanged = ENUM_TYPE(803)
VREvent_SeatedZeroPoseReset = ENUM_TYPE(804)
VREvent_AudioSettingsHaveChanged = ENUM_TYPE(820)
VREvent_BackgroundSettingHasChanged = ENUM_TYPE(850)
VREvent_CameraSettingsHaveChanged = ENUM_TYPE(851)
VREvent_ReprojectionSettingHasChanged = ENUM_TYPE(852)
VREvent_StatusUpdate = ENUM_TYPE(900)
VREvent_MCImageUpdated = ENUM_TYPE(1000)
VREvent_FirmwareUpdateStarted = ENUM_TYPE(1100)
VREvent_FirmwareUpdateFinished = ENUM_TYPE(1101)
VREvent_KeyboardClosed = ENUM_TYPE(1200)
VREvent_KeyboardCharInput = ENUM_TYPE(1201)
VREvent_KeyboardDone = ENUM_TYPE(1202)
VREvent_ApplicationTransitionStarted = ENUM_TYPE(1300)
VREvent_ApplicationTransitionAborted = ENUM_TYPE(1301)
VREvent_ApplicationTransitionNewAppStarted = ENUM_TYPE(1302)
VREvent_Compositor_MirrorWindowShown = ENUM_TYPE(1400)
VREvent_Compositor_MirrorWindowHidden = ENUM_TYPE(1401)
VREvent_Compositor_ChaperoneBoundsShown = ENUM_TYPE(1410)
VREvent_Compositor_ChaperoneBoundsHidden = ENUM_TYPE(1411)
VREvent_TrackedCamera_StartVideoStream = ENUM_TYPE(1500)
VREvent_TrackedCamera_StopVideoStream = ENUM_TYPE(1501)
VREvent_TrackedCamera_PauseVideoStream = ENUM_TYPE(1502)
VREvent_TrackedCamera_ResumeVideoStream = ENUM_TYPE(1503)
VREvent_PerformanceTest_EnableCapture = ENUM_TYPE(1600)
VREvent_PerformanceTest_DisableCapture = ENUM_TYPE(1601)
VREvent_PerformanceTest_FidelityLevel = ENUM_TYPE(1602)
VREvent_VendorSpecific_Reserved_Start = ENUM_TYPE(10000)
VREvent_VendorSpecific_Reserved_End = ENUM_TYPE(19999)

EDeviceActivityLevel = ENUM_TYPE
k_EDeviceActivityLevel_Unknown = ENUM_TYPE(-1)
k_EDeviceActivityLevel_Idle = ENUM_TYPE(0)
k_EDeviceActivityLevel_UserInteraction = ENUM_TYPE(1)
k_EDeviceActivityLevel_UserInteraction_Timeout = ENUM_TYPE(2)
k_EDeviceActivityLevel_Standby = ENUM_TYPE(3)

EVRButtonId = ENUM_TYPE
k_EButton_System = ENUM_TYPE(0)
k_EButton_ApplicationMenu = ENUM_TYPE(1)
k_EButton_Grip = ENUM_TYPE(2)
k_EButton_DPad_Left = ENUM_TYPE(3)
k_EButton_DPad_Up = ENUM_TYPE(4)
k_EButton_DPad_Right = ENUM_TYPE(5)
k_EButton_DPad_Down = ENUM_TYPE(6)
k_EButton_A = ENUM_TYPE(7)
k_EButton_Axis0 = ENUM_TYPE(32)
k_EButton_Axis1 = ENUM_TYPE(33)
k_EButton_Axis2 = ENUM_TYPE(34)
k_EButton_Axis3 = ENUM_TYPE(35)
k_EButton_Axis4 = ENUM_TYPE(36)
k_EButton_SteamVR_Touchpad = ENUM_TYPE(32)
k_EButton_SteamVR_Trigger = ENUM_TYPE(33)
k_EButton_Dashboard_Back = ENUM_TYPE(2)
k_EButton_Max = ENUM_TYPE(64)

EVRMouseButton = ENUM_TYPE
VRMouseButton_Left = ENUM_TYPE(1)
VRMouseButton_Right = ENUM_TYPE(2)
VRMouseButton_Middle = ENUM_TYPE(4)

EVRControllerAxisType = ENUM_TYPE
k_eControllerAxis_None = ENUM_TYPE(0)
k_eControllerAxis_TrackPad = ENUM_TYPE(1)
k_eControllerAxis_Joystick = ENUM_TYPE(2)
k_eControllerAxis_Trigger = ENUM_TYPE(3)

EVRControllerEventOutputType = ENUM_TYPE
ControllerEventOutput_OSEvents = ENUM_TYPE(0)
ControllerEventOutput_VREvents = ENUM_TYPE(1)

ECollisionBoundsStyle = ENUM_TYPE
COLLISION_BOUNDS_STYLE_BEGINNER = ENUM_TYPE(0)
COLLISION_BOUNDS_STYLE_INTERMEDIATE = ENUM_TYPE(1)
COLLISION_BOUNDS_STYLE_SQUARES = ENUM_TYPE(2)
COLLISION_BOUNDS_STYLE_ADVANCED = ENUM_TYPE(3)
COLLISION_BOUNDS_STYLE_NONE = ENUM_TYPE(4)
COLLISION_BOUNDS_STYLE_COUNT = ENUM_TYPE(5)

EVROverlayError = ENUM_TYPE
VROverlayError_None = ENUM_TYPE(0)
VROverlayError_UnknownOverlay = ENUM_TYPE(10)
VROverlayError_InvalidHandle = ENUM_TYPE(11)
VROverlayError_PermissionDenied = ENUM_TYPE(12)
VROverlayError_OverlayLimitExceeded = ENUM_TYPE(13)
VROverlayError_WrongVisibilityType = ENUM_TYPE(14)
VROverlayError_KeyTooLong = ENUM_TYPE(15)
VROverlayError_NameTooLong = ENUM_TYPE(16)
VROverlayError_KeyInUse = ENUM_TYPE(17)
VROverlayError_WrongTransformType = ENUM_TYPE(18)
VROverlayError_InvalidTrackedDevice = ENUM_TYPE(19)
VROverlayError_InvalidParameter = ENUM_TYPE(20)
VROverlayError_ThumbnailCantBeDestroyed = ENUM_TYPE(21)
VROverlayError_ArrayTooSmall = ENUM_TYPE(22)
VROverlayError_RequestFailed = ENUM_TYPE(23)
VROverlayError_InvalidTexture = ENUM_TYPE(24)
VROverlayError_UnableToLoadFile = ENUM_TYPE(25)
VROVerlayError_KeyboardAlreadyInUse = ENUM_TYPE(26)
VROverlayError_NoNeighbor = ENUM_TYPE(27)

EVRApplicationType = ENUM_TYPE
VRApplication_Other = ENUM_TYPE(0)
VRApplication_Scene = ENUM_TYPE(1)
VRApplication_Overlay = ENUM_TYPE(2)
VRApplication_Background = ENUM_TYPE(3)
VRApplication_Utility = ENUM_TYPE(4)
VRApplication_VRMonitor = ENUM_TYPE(5)

EVRFirmwareError = ENUM_TYPE
VRFirmwareError_None = ENUM_TYPE(0)
VRFirmwareError_Success = ENUM_TYPE(1)
VRFirmwareError_Fail = ENUM_TYPE(2)

EVRNotificationError = ENUM_TYPE
VRNotificationError_OK = ENUM_TYPE(0)
VRNotificationError_InvalidNotificationId = ENUM_TYPE(100)
VRNotificationError_NotificationQueueFull = ENUM_TYPE(101)
VRNotificationError_InvalidOverlayHandle = ENUM_TYPE(102)

EVRInitError = ENUM_TYPE
VRInitError_None = ENUM_TYPE(0)
VRInitError_Unknown = ENUM_TYPE(1)
VRInitError_Init_InstallationNotFound = ENUM_TYPE(100)
VRInitError_Init_InstallationCorrupt = ENUM_TYPE(101)
VRInitError_Init_VRClientDLLNotFound = ENUM_TYPE(102)
VRInitError_Init_FileNotFound = ENUM_TYPE(103)
VRInitError_Init_FactoryNotFound = ENUM_TYPE(104)
VRInitError_Init_InterfaceNotFound = ENUM_TYPE(105)
VRInitError_Init_InvalidInterface = ENUM_TYPE(106)
VRInitError_Init_UserConfigDirectoryInvalid = ENUM_TYPE(107)
VRInitError_Init_HmdNotFound = ENUM_TYPE(108)
VRInitError_Init_NotInitialized = ENUM_TYPE(109)
VRInitError_Init_PathRegistryNotFound = ENUM_TYPE(110)
VRInitError_Init_NoConfigPath = ENUM_TYPE(111)
VRInitError_Init_NoLogPath = ENUM_TYPE(112)
VRInitError_Init_PathRegistryNotWritable = ENUM_TYPE(113)
VRInitError_Init_AppInfoInitFailed = ENUM_TYPE(114)
VRInitError_Init_Retry = ENUM_TYPE(115)
VRInitError_Init_InitCanceledByUser = ENUM_TYPE(116)
VRInitError_Init_AnotherAppLaunching = ENUM_TYPE(117)
VRInitError_Init_SettingsInitFailed = ENUM_TYPE(118)
VRInitError_Init_ShuttingDown = ENUM_TYPE(119)
VRInitError_Init_TooManyObjects = ENUM_TYPE(120)
VRInitError_Init_NoServerForBackgroundApp = ENUM_TYPE(121)
VRInitError_Init_NotSupportedWithCompositor = ENUM_TYPE(122)
VRInitError_Init_NotAvailableToUtilityApps = ENUM_TYPE(123)
VRInitError_Init_Internal = ENUM_TYPE(124)
VRInitError_Driver_Failed = ENUM_TYPE(200)
VRInitError_Driver_Unknown = ENUM_TYPE(201)
VRInitError_Driver_HmdUnknown = ENUM_TYPE(202)
VRInitError_Driver_NotLoaded = ENUM_TYPE(203)
VRInitError_Driver_RuntimeOutOfDate = ENUM_TYPE(204)
VRInitError_Driver_HmdInUse = ENUM_TYPE(205)
VRInitError_Driver_NotCalibrated = ENUM_TYPE(206)
VRInitError_Driver_CalibrationInvalid = ENUM_TYPE(207)
VRInitError_Driver_HmdDisplayNotFound = ENUM_TYPE(208)
VRInitError_IPC_ServerInitFailed = ENUM_TYPE(300)
VRInitError_IPC_ConnectFailed = ENUM_TYPE(301)
VRInitError_IPC_SharedStateInitFailed = ENUM_TYPE(302)
VRInitError_IPC_CompositorInitFailed = ENUM_TYPE(303)
VRInitError_IPC_MutexInitFailed = ENUM_TYPE(304)
VRInitError_IPC_Failed = ENUM_TYPE(305)
VRInitError_Compositor_Failed = ENUM_TYPE(400)
VRInitError_Compositor_D3D11HardwareRequired = ENUM_TYPE(401)
VRInitError_Compositor_FirmwareRequiresUpdate = ENUM_TYPE(402)
VRInitError_VendorSpecific_UnableToConnectToOculusRuntime = ENUM_TYPE(1000)
VRInitError_VendorSpecific_HmdFound_CantOpenDevice = ENUM_TYPE(1101)
VRInitError_VendorSpecific_HmdFound_UnableToRequestConfigStart = ENUM_TYPE(1102)
VRInitError_VendorSpecific_HmdFound_NoStoredConfig = ENUM_TYPE(1103)
VRInitError_VendorSpecific_HmdFound_ConfigTooBig = ENUM_TYPE(1104)
VRInitError_VendorSpecific_HmdFound_ConfigTooSmall = ENUM_TYPE(1105)
VRInitError_VendorSpecific_HmdFound_UnableToInitZLib = ENUM_TYPE(1106)
VRInitError_VendorSpecific_HmdFound_CantReadFirmwareVersion = ENUM_TYPE(1107)
VRInitError_VendorSpecific_HmdFound_UnableToSendUserDataStart = ENUM_TYPE(1108)
VRInitError_VendorSpecific_HmdFound_UnableToGetUserDataStart = ENUM_TYPE(1109)
VRInitError_VendorSpecific_HmdFound_UnableToGetUserDataNext = ENUM_TYPE(1110)
VRInitError_VendorSpecific_HmdFound_UserDataAddressRange = ENUM_TYPE(1111)
VRInitError_VendorSpecific_HmdFound_UserDataError = ENUM_TYPE(1112)
VRInitError_VendorSpecific_HmdFound_ConfigFailedSanityCheck = ENUM_TYPE(1113)
VRInitError_Steam_SteamInstallationNotFound = ENUM_TYPE(2000)

EVRApplicationError = ENUM_TYPE
VRApplicationError_None = ENUM_TYPE(0)
VRApplicationError_AppKeyAlreadyExists = ENUM_TYPE(100)
VRApplicationError_NoManifest = ENUM_TYPE(101)
VRApplicationError_NoApplication = ENUM_TYPE(102)
VRApplicationError_InvalidIndex = ENUM_TYPE(103)
VRApplicationError_UnknownApplication = ENUM_TYPE(104)
VRApplicationError_IPCFailed = ENUM_TYPE(105)
VRApplicationError_ApplicationAlreadyRunning = ENUM_TYPE(106)
VRApplicationError_InvalidManifest = ENUM_TYPE(107)
VRApplicationError_InvalidApplication = ENUM_TYPE(108)
VRApplicationError_LaunchFailed = ENUM_TYPE(109)
VRApplicationError_ApplicationAlreadyStarting = ENUM_TYPE(110)
VRApplicationError_LaunchInProgress = ENUM_TYPE(111)
VRApplicationError_OldApplicationQuitting = ENUM_TYPE(112)
VRApplicationError_TransitionAborted = ENUM_TYPE(113)
VRApplicationError_IsTemplate = ENUM_TYPE(114)
VRApplicationError_BufferTooSmall = ENUM_TYPE(200)
VRApplicationError_PropertyNotSet = ENUM_TYPE(201)
VRApplicationError_UnknownProperty = ENUM_TYPE(202)
VRApplicationError_InvalidParameter = ENUM_TYPE(203)

EVRApplicationProperty = ENUM_TYPE
VRApplicationProperty_Name_String = ENUM_TYPE(0)
VRApplicationProperty_LaunchType_String = ENUM_TYPE(11)
VRApplicationProperty_WorkingDirectory_String = ENUM_TYPE(12)
VRApplicationProperty_BinaryPath_String = ENUM_TYPE(13)
VRApplicationProperty_Arguments_String = ENUM_TYPE(14)
VRApplicationProperty_URL_String = ENUM_TYPE(15)
VRApplicationProperty_Description_String = ENUM_TYPE(50)
VRApplicationProperty_NewsURL_String = ENUM_TYPE(51)
VRApplicationProperty_ImagePath_String = ENUM_TYPE(52)
VRApplicationProperty_Source_String = ENUM_TYPE(53)
VRApplicationProperty_IsDashboardOverlay_Bool = ENUM_TYPE(60)
VRApplicationProperty_IsTemplate_Bool = ENUM_TYPE(61)
VRApplicationProperty_IsInstanced_Bool = ENUM_TYPE(62)
VRApplicationProperty_LastLaunchTime_Uint64 = ENUM_TYPE(70)

EVRApplicationTransitionState = ENUM_TYPE
VRApplicationTransition_None = ENUM_TYPE(0)
VRApplicationTransition_OldAppQuitSent = ENUM_TYPE(10)
VRApplicationTransition_WaitingForExternalLaunch = ENUM_TYPE(11)
VRApplicationTransition_NewAppLaunched = ENUM_TYPE(20)

ChaperoneCalibrationState = ENUM_TYPE
ChaperoneCalibrationState_OK = ENUM_TYPE(1)
ChaperoneCalibrationState_Warning = ENUM_TYPE(100)
ChaperoneCalibrationState_Warning_BaseStationMayHaveMoved = ENUM_TYPE(101)
ChaperoneCalibrationState_Warning_BaseStationRemoved = ENUM_TYPE(102)
ChaperoneCalibrationState_Warning_SeatedBoundsInvalid = ENUM_TYPE(103)
ChaperoneCalibrationState_Error = ENUM_TYPE(200)
ChaperoneCalibrationState_Error_BaseStationUninitalized = ENUM_TYPE(201)
ChaperoneCalibrationState_Error_BaseStationConflict = ENUM_TYPE(202)
ChaperoneCalibrationState_Error_PlayAreaInvalid = ENUM_TYPE(203)
ChaperoneCalibrationState_Error_CollisionBoundsInvalid = ENUM_TYPE(204)

EChaperoneConfigFile = ENUM_TYPE
EChaperoneConfigFile_Live = ENUM_TYPE(1)
EChaperoneConfigFile_Temp = ENUM_TYPE(2)

EChaperoneImportFlags = ENUM_TYPE
EChaperoneImport_BoundsOnly = ENUM_TYPE(1)

EVRCompositorError = ENUM_TYPE
VRCompositorError_None = ENUM_TYPE(0)
VRCompositorError_IncompatibleVersion = ENUM_TYPE(100)
VRCompositorError_DoNotHaveFocus = ENUM_TYPE(101)
VRCompositorError_InvalidTexture = ENUM_TYPE(102)
VRCompositorError_IsNotSceneApplication = ENUM_TYPE(103)
VRCompositorError_TextureIsOnWrongDevice = ENUM_TYPE(104)
VRCompositorError_TextureUsesUnsupportedFormat = ENUM_TYPE(105)
VRCompositorError_SharedTexturesNotSupported = ENUM_TYPE(106)
VRCompositorError_IndexOutOfRange = ENUM_TYPE(107)

VROverlayInputMethod = ENUM_TYPE
VROverlayInputMethod_None = ENUM_TYPE(0)
VROverlayInputMethod_Mouse = ENUM_TYPE(1)

VROverlayTransformType = ENUM_TYPE
VROverlayTransform_Absolute = ENUM_TYPE(0)
VROverlayTransform_TrackedDeviceRelative = ENUM_TYPE(1)
VROverlayTransform_SystemOverlay = ENUM_TYPE(2)
VROverlayTransform_TrackedComponent = ENUM_TYPE(3)

VROverlayFlags = ENUM_TYPE
VROverlayFlags_None = ENUM_TYPE(0)
VROverlayFlags_Curved = ENUM_TYPE(1)
VROverlayFlags_RGSS4X = ENUM_TYPE(2)
VROverlayFlags_NoDashboardTab = ENUM_TYPE(3)
VROverlayFlags_AcceptsGamepadEvents = ENUM_TYPE(4)
VROverlayFlags_ShowGamepadFocus = ENUM_TYPE(5)
VROverlayFlags_SendVRScrollEvents = ENUM_TYPE(6)
VROverlayFlags_SendVRTouchpadEvents = ENUM_TYPE(7)
VROverlayFlags_ShowTouchPadScrollWheel = ENUM_TYPE(8)
VROverlayFlags_TransferOwnershipToInternalProcess = ENUM_TYPE(9)

EGamepadTextInputMode = ENUM_TYPE
k_EGamepadTextInputModeNormal = ENUM_TYPE(0)
k_EGamepadTextInputModePassword = ENUM_TYPE(1)
k_EGamepadTextInputModeSubmit = ENUM_TYPE(2)

EGamepadTextInputLineMode = ENUM_TYPE
k_EGamepadTextInputLineModeSingleLine = ENUM_TYPE(0)
k_EGamepadTextInputLineModeMultipleLines = ENUM_TYPE(1)

EOverlayDirection = ENUM_TYPE
OverlayDirection_Up = ENUM_TYPE(0)
OverlayDirection_Down = ENUM_TYPE(1)
OverlayDirection_Left = ENUM_TYPE(2)
OverlayDirection_Right = ENUM_TYPE(3)
OverlayDirection_Count = ENUM_TYPE(4)

EVRRenderModelError = ENUM_TYPE
VRRenderModelError_None = ENUM_TYPE(0)
VRRenderModelError_Loading = ENUM_TYPE(100)
VRRenderModelError_NotSupported = ENUM_TYPE(200)
VRRenderModelError_InvalidArg = ENUM_TYPE(300)
VRRenderModelError_InvalidModel = ENUM_TYPE(301)
VRRenderModelError_NoShapes = ENUM_TYPE(302)
VRRenderModelError_MultipleShapes = ENUM_TYPE(303)
VRRenderModelError_TooManyIndices = ENUM_TYPE(304)
VRRenderModelError_MultipleTextures = ENUM_TYPE(305)
VRRenderModelError_InvalidTexture = ENUM_TYPE(400)

EVRComponentProperty = ENUM_TYPE
VRComponentProperty_IsStatic = ENUM_TYPE(1)
VRComponentProperty_IsVisible = ENUM_TYPE(2)
VRComponentProperty_IsTouched = ENUM_TYPE(4)
VRComponentProperty_IsPressed = ENUM_TYPE(8)
VRComponentProperty_IsScrolled = ENUM_TYPE(16)

EVRNotificationType = ENUM_TYPE
Transient = ENUM_TYPE(0)
Persistent = ENUM_TYPE(1)

EVRNotificationStyle = ENUM_TYPE
EVRNotificationStyle_None = ENUM_TYPE(0)
EVRNotificationStyle_Application = ENUM_TYPE(100)
EVRNotificationStyle_Contact_Disabled = ENUM_TYPE(200)
EVRNotificationStyle_Contact_Enabled = ENUM_TYPE(201)
EVRNotificationStyle_Contact_Active = ENUM_TYPE(202)

EVRSettingsError = ENUM_TYPE
VRSettingsError_None = ENUM_TYPE(0)
VRSettingsError_IPCFailed = ENUM_TYPE(1)
VRSettingsError_WriteFailed = ENUM_TYPE(2)
VRSettingsError_ReadFailed = ENUM_TYPE(3)


#######################
### Expose Typedefs ###
#######################

# Use c_ubyte instead of c_char, for better compatibility with Python True/False
openvr_bool = c_ubyte

TrackedDeviceIndex_t = c_uint32
VRNotificationId = c_uint32
VROverlayHandle_t = c_uint64
glSharedTextureHandle_t = c_void_p
glInt_t = c_int32
glUInt_t = c_uint32
TrackedDeviceIndex_t = c_uint32
VROverlayHandle_t = c_uint64
VRComponentProperties = c_uint32
TextureID_t = c_int32
VRNotificationId = c_uint32
HmdError = EVRInitError
Hmd_Eye = EVREye
GraphicsAPIConvention = EGraphicsAPIConvention
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

######################
### Expose classes ###
######################

class OpenVRError(RuntimeError):
    """
    OpenVRError is a custom exception type for when OpenVR functions return a failure code.
    Such a specific exception type allows more precise exception handling that does just raising Exception().
    """
    pass


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
    _fields_ = [
        ("m", (c_float * 4) * 3),
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
    _fields_ = [
        ("rfRed", c_float * 2),
        ("rfGreen", c_float * 2),
        ("rfBlue", c_float * 2),
    ]


class Texture_t(Structure):
    _fields_ = [
        ("handle", c_void_p),
        ("eType", EGraphicsAPIConvention),
        ("eColorSpace", EColorSpace),
    ]


class TrackedDevicePose_t(Structure):
    _fields_ = [
        ("mDeviceToAbsoluteTracking", HmdMatrix34_t),
        ("vVelocity", HmdVector3_t),
        ("vAngularVelocity", HmdVector3_t),
        ("eTrackingResult", ETrackingResult),
        ("bPoseIsValid", openvr_bool),
        ("bDeviceIsConnected", openvr_bool),
    ]


class VRTextureBounds_t(Structure):
    _fields_ = [
        ("uMin", c_float),
        ("vMin", c_float),
        ("uMax", c_float),
        ("vMax", c_float),
    ]


class VREvent_Controller_t(Structure):
    _fields_ = [
        ("button", c_uint32),
    ]


class VREvent_Mouse_t(Structure):
    _fields_ = [
        ("x", c_float),
        ("y", c_float),
        ("button", c_uint32),
    ]


class VREvent_Scroll_t(Structure):
    _fields_ = [
        ("xdelta", c_float),
        ("ydelta", c_float),
        ("repeatCount", c_uint32),
    ]


class VREvent_TouchPadMove_t(Structure):
    _fields_ = [
        ("bFingerDown", openvr_bool),
        ("flSecondsFingerDown", c_float),
        ("fValueXFirst", c_float),
        ("fValueYFirst", c_float),
        ("fValueXRaw", c_float),
        ("fValueYRaw", c_float),
    ]


class VREvent_Notification_t(Structure):
    _fields_ = [
        ("ulUserValue", c_uint64),
        ("notificationId", c_uint32),
    ]


class VREvent_Process_t(Structure):
    _fields_ = [
        ("pid", c_uint32),
        ("oldPid", c_uint32),
        ("bForced", openvr_bool),
    ]


class VREvent_Overlay_t(Structure):
    _fields_ = [
        ("overlayHandle", c_uint64),
    ]


class VREvent_Status_t(Structure):
    _fields_ = [
        ("statusState", c_uint32),
    ]


class VREvent_Keyboard_t(Structure):
    _fields_ = [
        ("cNewInput", c_char_p * 8),
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
    _fields_ = [
        ("reserved0", c_uint64),
        ("reserved1", c_uint64),
    ]


class VREvent_PerformanceTest_t(Structure):
    _fields_ = [
        ("m_nFidelityLevel", c_uint32),
    ]


class VREvent_SeatedZeroPoseReset_t(Structure):
    _fields_ = [
        ("bResetBySystemMenu", openvr_bool),
    ]


class HiddenAreaMesh_t(Structure):
    _fields_ = [
        ("pVertexData", POINTER(HmdVector2_t)),
        ("unTriangleCount", c_uint32),
    ]


class VRControllerAxis_t(Structure):
    _fields_ = [
        ("x", c_float),
        ("y", c_float),
    ]


class VRControllerState_t(Structure):
    _fields_ = [
        ("unPacketNum", c_uint32),
        ("ulButtonPressed", c_uint64),
        ("ulButtonTouched", c_uint64),
        ("rAxis", VRControllerAxis_t * 5),
    ]


class Compositor_OverlaySettings(Structure):
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


class AppOverrideKeys_t(Structure):
    _fields_ = [
        ("pchKey", c_char_p),
        ("pchValue", c_char_p),
    ]


class Compositor_FrameTiming(Structure):
    _fields_ = [
        ("m_nSize", c_uint32),
        ("m_nFrameIndex", c_uint32),
        ("m_nNumFramePresents", c_uint32),
        ("m_nNumDroppedFrames", c_uint32),
        ("m_flSystemTimeInSeconds", c_double),
        ("m_flSceneRenderGpuMs", c_float),
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
        ("m_nFidelityLevel", c_int32),
        ("m_nReprojectionFlags", c_uint32),
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


class RenderModel_ComponentState_t(Structure):
    _fields_ = [
        ("mTrackingToComponentRenderModel", HmdMatrix34_t),
        ("mTrackingToComponentLocal", HmdMatrix34_t),
        ("uProperties", VRComponentProperties),
    ]


class RenderModel_Vertex_t(Structure):
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


class NotificationBitmap_t(Structure):
    _fields_ = [
        ("bytes", c_void_p),
        ("width", c_int32),
        ("height", c_int32),
        ("depth", c_int32),
    ]


class COpenVRContext(Structure):
    _fields_ = [
        ("m_pVRSystem", POINTER(c_int)),
        ("m_pVRChaperone", POINTER(c_int)),
        ("m_pVRChaperoneSetup", POINTER(c_int)),
        ("m_pVRCompositor", POINTER(c_int)),
        ("m_pVROverlay", POINTER(c_int)),
        ("m_pVRRenderModels", POINTER(c_int)),
        ("m_pVRExtendedDisplay", POINTER(c_int)),
        ("m_pVRSettings", POINTER(c_int)),
        ("m_pVRApplications", POINTER(c_int)),
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
    ]


class VREvent_t(Structure):
    _fields_ = [
        ("eventType", c_uint32),
        ("trackedDeviceIndex", TrackedDeviceIndex_t),
        ("eventAgeSeconds", c_float),
        ("data", VREvent_Data_t),
    ]


class IVRSystem_FnTable(Structure):
    _fields_ = [
        ("getRecommendedRenderTargetSize", OPENVR_FNTABLE_CALLTYPE(None, POINTER(c_uint32), POINTER(c_uint32))),
        ("getProjectionMatrix", OPENVR_FNTABLE_CALLTYPE(HmdMatrix44_t, EVREye, c_float, c_float, EGraphicsAPIConvention)),
        ("getProjectionRaw", OPENVR_FNTABLE_CALLTYPE(None, EVREye, POINTER(c_float), POINTER(c_float), POINTER(c_float), POINTER(c_float))),
        ("computeDistortion", OPENVR_FNTABLE_CALLTYPE(DistortionCoordinates_t, EVREye, c_float, c_float)),
        ("getEyeToHeadTransform", OPENVR_FNTABLE_CALLTYPE(HmdMatrix34_t, EVREye)),
        ("getTimeSinceLastVsync", OPENVR_FNTABLE_CALLTYPE(openvr_bool, POINTER(c_float), POINTER(c_uint64))),
        ("getD3D9AdapterIndex", OPENVR_FNTABLE_CALLTYPE(c_int32)),
        ("getDXGIOutputInfo", OPENVR_FNTABLE_CALLTYPE(None, POINTER(c_int32))),
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
        ("getStringTrackedDeviceProperty", OPENVR_FNTABLE_CALLTYPE(c_uint32, TrackedDeviceIndex_t, ETrackedDeviceProperty, c_char_p, c_uint32, POINTER(ETrackedPropertyError))),
        ("getPropErrorNameFromEnum", OPENVR_FNTABLE_CALLTYPE(c_char_p, ETrackedPropertyError)),
        ("pollNextEvent", OPENVR_FNTABLE_CALLTYPE(openvr_bool, POINTER(VREvent_t), c_uint32)),
        ("pollNextEventWithPose", OPENVR_FNTABLE_CALLTYPE(openvr_bool, ETrackingUniverseOrigin, POINTER(VREvent_t), c_uint32, POINTER(TrackedDevicePose_t))),
        ("getEventTypeNameFromEnum", OPENVR_FNTABLE_CALLTYPE(c_char_p, EVREventType)),
        ("getHiddenAreaMesh", OPENVR_FNTABLE_CALLTYPE(HiddenAreaMesh_t, EVREye)),
        ("getControllerState", OPENVR_FNTABLE_CALLTYPE(openvr_bool, TrackedDeviceIndex_t, POINTER(VRControllerState_t))),
        ("getControllerStateWithPose", OPENVR_FNTABLE_CALLTYPE(openvr_bool, ETrackingUniverseOrigin, TrackedDeviceIndex_t, POINTER(VRControllerState_t), POINTER(TrackedDevicePose_t))),
        ("triggerHapticPulse", OPENVR_FNTABLE_CALLTYPE(None, TrackedDeviceIndex_t, c_uint32, c_ushort)),
        ("getButtonIdNameFromEnum", OPENVR_FNTABLE_CALLTYPE(c_char_p, EVRButtonId)),
        ("getControllerAxisTypeNameFromEnum", OPENVR_FNTABLE_CALLTYPE(c_char_p, EVRControllerAxisType)),
        ("captureInputFocus", OPENVR_FNTABLE_CALLTYPE(openvr_bool)),
        ("releaseInputFocus", OPENVR_FNTABLE_CALLTYPE(None)),
        ("isInputFocusCapturedByAnotherProcess", OPENVR_FNTABLE_CALLTYPE(openvr_bool)),
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
        # Thank you lukexi https://github.com/lukexi/openvr-hs/blob/master/cbits/openvr_capi_helper.c#L9
        fn_key = b"FnTable:" + version_key
        fn_type = IVRSystem_FnTable
        fn_table_ptr = cast(getGenericInterface(fn_key), POINTER(fn_type))
        if fn_table_ptr is None:
            raise OpenVRError("Error retrieving VR API for IVRSystem")
        self.function_table = fn_table_ptr.contents

    def getRecommendedRenderTargetSize(self):
        fn = self.function_table.getRecommendedRenderTargetSize
        pnWidth = c_uint32()
        pnHeight = c_uint32()
        result = fn(byref(pnWidth), byref(pnHeight))
        return pnWidth, pnHeight

    def getProjectionMatrix(self, eEye, fNearZ, fFarZ, eProjType):
        fn = self.function_table.getProjectionMatrix
        result = fn(eEye, fNearZ, fFarZ, eProjType)
        return result

    def getProjectionRaw(self, eEye):
        fn = self.function_table.getProjectionRaw
        pfLeft = c_float()
        pfRight = c_float()
        pfTop = c_float()
        pfBottom = c_float()
        result = fn(eEye, byref(pfLeft), byref(pfRight), byref(pfTop), byref(pfBottom))
        return pfLeft, pfRight, pfTop, pfBottom

    def computeDistortion(self, eEye, fU, fV):
        fn = self.function_table.computeDistortion
        result = fn(eEye, fU, fV)
        return result

    def getEyeToHeadTransform(self, eEye):
        fn = self.function_table.getEyeToHeadTransform
        result = fn(eEye)
        return result

    def getTimeSinceLastVsync(self):
        fn = self.function_table.getTimeSinceLastVsync
        pfSecondsSinceLastVsync = c_float()
        pulFrameCounter = c_uint64()
        result = fn(byref(pfSecondsSinceLastVsync), byref(pulFrameCounter))
        return result, pfSecondsSinceLastVsync, pulFrameCounter

    def getD3D9AdapterIndex(self):
        fn = self.function_table.getD3D9AdapterIndex
        result = fn()
        return result

    def getDXGIOutputInfo(self):
        fn = self.function_table.getDXGIOutputInfo
        pnAdapterIndex = c_int32()
        result = fn(byref(pnAdapterIndex))
        return pnAdapterIndex

    def isDisplayOnDesktop(self):
        fn = self.function_table.isDisplayOnDesktop
        result = fn()
        return result

    def setDisplayVisibility(self, bIsVisibleOnDesktop):
        fn = self.function_table.setDisplayVisibility
        result = fn(bIsVisibleOnDesktop)
        return result

    def getDeviceToAbsoluteTrackingPose(self, eOrigin, fPredictedSecondsToPhotonsFromNow, unTrackedDevicePoseArrayCount, pTrackedDevicePoseArray=None):
        fn = self.function_table.getDeviceToAbsoluteTrackingPose
        if pTrackedDevicePoseArray is None:
            pTrackedDevicePoseArray = (TrackedDevicePose_t * unTrackedDevicePoseArrayCount)()
        pTrackedDevicePoseArray = cast(pTrackedDevicePoseArray, POINTER(TrackedDevicePose_t))
        result = fn(eOrigin, fPredictedSecondsToPhotonsFromNow, pTrackedDevicePoseArray, unTrackedDevicePoseArrayCount)
        return pTrackedDevicePoseArray

    def resetSeatedZeroPose(self):
        fn = self.function_table.resetSeatedZeroPose
        result = fn()

    def getSeatedZeroPoseToStandingAbsoluteTrackingPose(self):
        fn = self.function_table.getSeatedZeroPoseToStandingAbsoluteTrackingPose
        result = fn()
        return result

    def getRawZeroPoseToStandingAbsoluteTrackingPose(self):
        fn = self.function_table.getRawZeroPoseToStandingAbsoluteTrackingPose
        result = fn()
        return result

    def getSortedTrackedDeviceIndicesOfClass(self, eTrackedDeviceClass, unTrackedDeviceIndexArrayCount, unRelativeToTrackedDeviceIndex):
        fn = self.function_table.getSortedTrackedDeviceIndicesOfClass
        punTrackedDeviceIndexArray = TrackedDeviceIndex_t()
        result = fn(eTrackedDeviceClass, byref(punTrackedDeviceIndexArray), unTrackedDeviceIndexArrayCount, unRelativeToTrackedDeviceIndex)
        return result, punTrackedDeviceIndexArray

    def getTrackedDeviceActivityLevel(self, unDeviceId):
        fn = self.function_table.getTrackedDeviceActivityLevel
        result = fn(unDeviceId)
        return result

    def applyTransform(self):
        fn = self.function_table.applyTransform
        pOutputPose = TrackedDevicePose_t()
        pTrackedDevicePose = TrackedDevicePose_t()
        pTransform = HmdMatrix34_t()
        result = fn(byref(pOutputPose), byref(pTrackedDevicePose), byref(pTransform))
        return pOutputPose, pTrackedDevicePose, pTransform

    def getTrackedDeviceIndexForControllerRole(self, unDeviceType):
        fn = self.function_table.getTrackedDeviceIndexForControllerRole
        result = fn(unDeviceType)
        return result

    def getControllerRoleForTrackedDeviceIndex(self, unDeviceIndex):
        fn = self.function_table.getControllerRoleForTrackedDeviceIndex
        result = fn(unDeviceIndex)
        return result

    def getTrackedDeviceClass(self, unDeviceIndex):
        fn = self.function_table.getTrackedDeviceClass
        result = fn(unDeviceIndex)
        return result

    def isTrackedDeviceConnected(self, unDeviceIndex):
        fn = self.function_table.isTrackedDeviceConnected
        result = fn(unDeviceIndex)
        return result

    def getBoolTrackedDeviceProperty(self, unDeviceIndex, prop):
        fn = self.function_table.getBoolTrackedDeviceProperty
        pError = ETrackedPropertyError()
        result = fn(unDeviceIndex, prop, byref(pError))
        return result, pError

    def getFloatTrackedDeviceProperty(self, unDeviceIndex, prop):
        fn = self.function_table.getFloatTrackedDeviceProperty
        pError = ETrackedPropertyError()
        result = fn(unDeviceIndex, prop, byref(pError))
        return result, pError

    def getInt32TrackedDeviceProperty(self, unDeviceIndex, prop):
        fn = self.function_table.getInt32TrackedDeviceProperty
        pError = ETrackedPropertyError()
        result = fn(unDeviceIndex, prop, byref(pError))
        return result, pError

    def getUint64TrackedDeviceProperty(self, unDeviceIndex, prop):
        fn = self.function_table.getUint64TrackedDeviceProperty
        pError = ETrackedPropertyError()
        result = fn(unDeviceIndex, prop, byref(pError))
        return result, pError

    def getMatrix34TrackedDeviceProperty(self, unDeviceIndex, prop):
        fn = self.function_table.getMatrix34TrackedDeviceProperty
        pError = ETrackedPropertyError()
        result = fn(unDeviceIndex, prop, byref(pError))
        return result, pError

    def getStringTrackedDeviceProperty(self, unDeviceIndex, prop, pchValue, unBufferSize):
        fn = self.function_table.getStringTrackedDeviceProperty
        pError = ETrackedPropertyError()
        result = fn(unDeviceIndex, prop, pchValue, unBufferSize, byref(pError))
        return result, pError

    def getPropErrorNameFromEnum(self, error):
        fn = self.function_table.getPropErrorNameFromEnum
        result = fn(error)
        return result

    def pollNextEvent(self, uncbVREvent):
        fn = self.function_table.pollNextEvent
        pEvent = VREvent_t()
        result = fn(byref(pEvent), uncbVREvent)
        return result, pEvent

    def pollNextEventWithPose(self, eOrigin, uncbVREvent):
        fn = self.function_table.pollNextEventWithPose
        pEvent = VREvent_t()
        pTrackedDevicePose = TrackedDevicePose_t()
        result = fn(eOrigin, byref(pEvent), uncbVREvent, byref(pTrackedDevicePose))
        return result, pEvent, pTrackedDevicePose

    def getEventTypeNameFromEnum(self, eType):
        fn = self.function_table.getEventTypeNameFromEnum
        result = fn(eType)
        return result

    def getHiddenAreaMesh(self, eEye):
        fn = self.function_table.getHiddenAreaMesh
        result = fn(eEye)
        return result

    def getControllerState(self, unControllerDeviceIndex):
        fn = self.function_table.getControllerState
        pControllerState = VRControllerState_t()
        result = fn(unControllerDeviceIndex, byref(pControllerState))
        return result, pControllerState

    def getControllerStateWithPose(self, eOrigin, unControllerDeviceIndex):
        fn = self.function_table.getControllerStateWithPose
        pControllerState = VRControllerState_t()
        pTrackedDevicePose = TrackedDevicePose_t()
        result = fn(eOrigin, unControllerDeviceIndex, byref(pControllerState), byref(pTrackedDevicePose))
        return result, pControllerState, pTrackedDevicePose

    def triggerHapticPulse(self, unControllerDeviceIndex, unAxisId, usDurationMicroSec):
        fn = self.function_table.triggerHapticPulse
        result = fn(unControllerDeviceIndex, unAxisId, usDurationMicroSec)

    def getButtonIdNameFromEnum(self, eButtonId):
        fn = self.function_table.getButtonIdNameFromEnum
        result = fn(eButtonId)
        return result

    def getControllerAxisTypeNameFromEnum(self, eAxisType):
        fn = self.function_table.getControllerAxisTypeNameFromEnum
        result = fn(eAxisType)
        return result

    def captureInputFocus(self):
        fn = self.function_table.captureInputFocus
        result = fn()
        return result

    def releaseInputFocus(self):
        fn = self.function_table.releaseInputFocus
        result = fn()

    def isInputFocusCapturedByAnotherProcess(self):
        fn = self.function_table.isInputFocusCapturedByAnotherProcess
        result = fn()
        return result

    def driverDebugRequest(self, unDeviceIndex, pchRequest, pchResponseBuffer, unResponseBufferSize):
        fn = self.function_table.driverDebugRequest
        result = fn(unDeviceIndex, pchRequest, pchResponseBuffer, unResponseBufferSize)
        return result

    def performFirmwareUpdate(self, unDeviceIndex):
        fn = self.function_table.performFirmwareUpdate
        result = fn(unDeviceIndex)
        return result

    def acknowledgeQuit_Exiting(self):
        fn = self.function_table.acknowledgeQuit_Exiting
        result = fn()

    def acknowledgeQuit_UserPrompt(self):
        fn = self.function_table.acknowledgeQuit_UserPrompt
        result = fn()



class IVRExtendedDisplay_FnTable(Structure):
    _fields_ = [
        ("getWindowBounds", OPENVR_FNTABLE_CALLTYPE(None, POINTER(c_int32), POINTER(c_int32), POINTER(c_uint32), POINTER(c_uint32))),
        ("getEyeOutputViewport", OPENVR_FNTABLE_CALLTYPE(None, EVREye, POINTER(c_uint32), POINTER(c_uint32), POINTER(c_uint32), POINTER(c_uint32))),
        ("getDXGIOutputInfo", OPENVR_FNTABLE_CALLTYPE(None, POINTER(c_int32), POINTER(c_int32))),
    ]


class IVRExtendedDisplay(object):
    def __init__(self):
        version_key = IVRExtendedDisplay_Version
        if not isInterfaceVersionValid(version_key):
            _checkInitError(VRInitError_Init_InterfaceNotFound)
        # Thank you lukexi https://github.com/lukexi/openvr-hs/blob/master/cbits/openvr_capi_helper.c#L9
        fn_key = b"FnTable:" + version_key
        fn_type = IVRExtendedDisplay_FnTable
        fn_table_ptr = cast(getGenericInterface(fn_key), POINTER(fn_type))
        if fn_table_ptr is None:
            raise OpenVRError("Error retrieving VR API for IVRExtendedDisplay")
        self.function_table = fn_table_ptr.contents

    def getWindowBounds(self):
        fn = self.function_table.getWindowBounds
        pnX = c_int32()
        pnY = c_int32()
        pnWidth = c_uint32()
        pnHeight = c_uint32()
        result = fn(byref(pnX), byref(pnY), byref(pnWidth), byref(pnHeight))
        return pnX, pnY, pnWidth, pnHeight

    def getEyeOutputViewport(self, eEye):
        fn = self.function_table.getEyeOutputViewport
        pnX = c_uint32()
        pnY = c_uint32()
        pnWidth = c_uint32()
        pnHeight = c_uint32()
        result = fn(eEye, byref(pnX), byref(pnY), byref(pnWidth), byref(pnHeight))
        return pnX, pnY, pnWidth, pnHeight

    def getDXGIOutputInfo(self):
        fn = self.function_table.getDXGIOutputInfo
        pnAdapterIndex = c_int32()
        pnAdapterOutputIndex = c_int32()
        result = fn(byref(pnAdapterIndex), byref(pnAdapterOutputIndex))
        return pnAdapterIndex, pnAdapterOutputIndex



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
        ("getStartingApplication", OPENVR_FNTABLE_CALLTYPE(EVRApplicationError, c_char_p, c_uint32)),
        ("getTransitionState", OPENVR_FNTABLE_CALLTYPE(EVRApplicationTransitionState)),
        ("performApplicationPrelaunchCheck", OPENVR_FNTABLE_CALLTYPE(EVRApplicationError, c_char_p)),
        ("getApplicationsTransitionStateNameFromEnum", OPENVR_FNTABLE_CALLTYPE(c_char_p, EVRApplicationTransitionState)),
        ("isQuitUserPromptRequested", OPENVR_FNTABLE_CALLTYPE(openvr_bool)),
        ("launchInternalProcess", OPENVR_FNTABLE_CALLTYPE(EVRApplicationError, c_char_p, c_char_p, c_char_p)),
    ]


class IVRApplications(object):
    def __init__(self):
        version_key = IVRApplications_Version
        if not isInterfaceVersionValid(version_key):
            _checkInitError(VRInitError_Init_InterfaceNotFound)
        # Thank you lukexi https://github.com/lukexi/openvr-hs/blob/master/cbits/openvr_capi_helper.c#L9
        fn_key = b"FnTable:" + version_key
        fn_type = IVRApplications_FnTable
        fn_table_ptr = cast(getGenericInterface(fn_key), POINTER(fn_type))
        if fn_table_ptr is None:
            raise OpenVRError("Error retrieving VR API for IVRApplications")
        self.function_table = fn_table_ptr.contents

    def addApplicationManifest(self, pchApplicationManifestFullPath, bTemporary):
        fn = self.function_table.addApplicationManifest
        result = fn(pchApplicationManifestFullPath, bTemporary)
        return result

    def removeApplicationManifest(self, pchApplicationManifestFullPath):
        fn = self.function_table.removeApplicationManifest
        result = fn(pchApplicationManifestFullPath)
        return result

    def isApplicationInstalled(self, pchAppKey):
        fn = self.function_table.isApplicationInstalled
        result = fn(pchAppKey)
        return result

    def getApplicationCount(self):
        fn = self.function_table.getApplicationCount
        result = fn()
        return result

    def getApplicationKeyByIndex(self, unApplicationIndex, pchAppKeyBuffer, unAppKeyBufferLen):
        fn = self.function_table.getApplicationKeyByIndex
        result = fn(unApplicationIndex, pchAppKeyBuffer, unAppKeyBufferLen)
        return result

    def getApplicationKeyByProcessId(self, unProcessId, pchAppKeyBuffer, unAppKeyBufferLen):
        fn = self.function_table.getApplicationKeyByProcessId
        result = fn(unProcessId, pchAppKeyBuffer, unAppKeyBufferLen)
        return result

    def launchApplication(self, pchAppKey):
        fn = self.function_table.launchApplication
        result = fn(pchAppKey)
        return result

    def launchTemplateApplication(self, pchTemplateAppKey, pchNewAppKey, unKeys):
        fn = self.function_table.launchTemplateApplication
        pKeys = AppOverrideKeys_t()
        result = fn(pchTemplateAppKey, pchNewAppKey, byref(pKeys), unKeys)
        return result, pKeys

    def launchDashboardOverlay(self, pchAppKey):
        fn = self.function_table.launchDashboardOverlay
        result = fn(pchAppKey)
        return result

    def cancelApplicationLaunch(self, pchAppKey):
        fn = self.function_table.cancelApplicationLaunch
        result = fn(pchAppKey)
        return result

    def identifyApplication(self, unProcessId, pchAppKey):
        fn = self.function_table.identifyApplication
        result = fn(unProcessId, pchAppKey)
        return result

    def getApplicationProcessId(self, pchAppKey):
        fn = self.function_table.getApplicationProcessId
        result = fn(pchAppKey)
        return result

    def getApplicationsErrorNameFromEnum(self, error):
        fn = self.function_table.getApplicationsErrorNameFromEnum
        result = fn(error)
        return result

    def getApplicationPropertyString(self, pchAppKey, eProperty, pchPropertyValueBuffer, unPropertyValueBufferLen):
        fn = self.function_table.getApplicationPropertyString
        peError = EVRApplicationError()
        result = fn(pchAppKey, eProperty, pchPropertyValueBuffer, unPropertyValueBufferLen, byref(peError))
        return result, peError

    def getApplicationPropertyBool(self, pchAppKey, eProperty):
        fn = self.function_table.getApplicationPropertyBool
        peError = EVRApplicationError()
        result = fn(pchAppKey, eProperty, byref(peError))
        return result, peError

    def getApplicationPropertyUint64(self, pchAppKey, eProperty):
        fn = self.function_table.getApplicationPropertyUint64
        peError = EVRApplicationError()
        result = fn(pchAppKey, eProperty, byref(peError))
        return result, peError

    def setApplicationAutoLaunch(self, pchAppKey, bAutoLaunch):
        fn = self.function_table.setApplicationAutoLaunch
        result = fn(pchAppKey, bAutoLaunch)
        return result

    def getApplicationAutoLaunch(self, pchAppKey):
        fn = self.function_table.getApplicationAutoLaunch
        result = fn(pchAppKey)
        return result

    def getStartingApplication(self, pchAppKeyBuffer, unAppKeyBufferLen):
        fn = self.function_table.getStartingApplication
        result = fn(pchAppKeyBuffer, unAppKeyBufferLen)
        return result

    def getTransitionState(self):
        fn = self.function_table.getTransitionState
        result = fn()
        return result

    def performApplicationPrelaunchCheck(self, pchAppKey):
        fn = self.function_table.performApplicationPrelaunchCheck
        result = fn(pchAppKey)
        return result

    def getApplicationsTransitionStateNameFromEnum(self, state):
        fn = self.function_table.getApplicationsTransitionStateNameFromEnum
        result = fn(state)
        return result

    def isQuitUserPromptRequested(self):
        fn = self.function_table.isQuitUserPromptRequested
        result = fn()
        return result

    def launchInternalProcess(self, pchBinaryPath, pchArguments, pchWorkingDirectory):
        fn = self.function_table.launchInternalProcess
        result = fn(pchBinaryPath, pchArguments, pchWorkingDirectory)
        return result



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
    def __init__(self):
        version_key = IVRChaperone_Version
        if not isInterfaceVersionValid(version_key):
            _checkInitError(VRInitError_Init_InterfaceNotFound)
        # Thank you lukexi https://github.com/lukexi/openvr-hs/blob/master/cbits/openvr_capi_helper.c#L9
        fn_key = b"FnTable:" + version_key
        fn_type = IVRChaperone_FnTable
        fn_table_ptr = cast(getGenericInterface(fn_key), POINTER(fn_type))
        if fn_table_ptr is None:
            raise OpenVRError("Error retrieving VR API for IVRChaperone")
        self.function_table = fn_table_ptr.contents

    def getCalibrationState(self):
        fn = self.function_table.getCalibrationState
        result = fn()
        return result

    def getPlayAreaSize(self):
        fn = self.function_table.getPlayAreaSize
        pSizeX = c_float()
        pSizeZ = c_float()
        result = fn(byref(pSizeX), byref(pSizeZ))
        return result, pSizeX, pSizeZ

    def getPlayAreaRect(self):
        fn = self.function_table.getPlayAreaRect
        rect = HmdQuad_t()
        result = fn(byref(rect))
        return result, rect

    def reloadInfo(self):
        fn = self.function_table.reloadInfo
        result = fn()

    def setSceneColor(self, color):
        fn = self.function_table.setSceneColor
        result = fn(color)

    def getBoundsColor(self, nNumOutputColors, flCollisionBoundsFadeDistance):
        fn = self.function_table.getBoundsColor
        pOutputColorArray = HmdColor_t()
        pOutputCameraColor = HmdColor_t()
        result = fn(byref(pOutputColorArray), nNumOutputColors, flCollisionBoundsFadeDistance, byref(pOutputCameraColor))
        return pOutputColorArray, pOutputCameraColor

    def areBoundsVisible(self):
        fn = self.function_table.areBoundsVisible
        result = fn()
        return result

    def forceBoundsVisible(self, bForce):
        fn = self.function_table.forceBoundsVisible
        result = fn(bForce)



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
        ("setWorkingSeatedZeroPoseToRawTrackingPose", OPENVR_FNTABLE_CALLTYPE(None, POINTER(HmdMatrix34_t))),
        ("setWorkingStandingZeroPoseToRawTrackingPose", OPENVR_FNTABLE_CALLTYPE(None, POINTER(HmdMatrix34_t))),
        ("reloadFromDisk", OPENVR_FNTABLE_CALLTYPE(None, EChaperoneConfigFile)),
        ("getLiveSeatedZeroPoseToRawTrackingPose", OPENVR_FNTABLE_CALLTYPE(openvr_bool, POINTER(HmdMatrix34_t))),
        ("setWorkingCollisionBoundsTagsInfo", OPENVR_FNTABLE_CALLTYPE(None, POINTER(c_uint8), c_uint32)),
        ("getLiveCollisionBoundsTagsInfo", OPENVR_FNTABLE_CALLTYPE(openvr_bool, POINTER(c_uint8), POINTER(c_uint32))),
        ("setWorkingPhysicalBoundsInfo", OPENVR_FNTABLE_CALLTYPE(openvr_bool, POINTER(HmdQuad_t), c_uint32)),
        ("getLivePhysicalBoundsInfo", OPENVR_FNTABLE_CALLTYPE(openvr_bool, POINTER(HmdQuad_t), POINTER(c_uint32))),
        ("exportLiveToBuffer", OPENVR_FNTABLE_CALLTYPE(openvr_bool, c_char_p, POINTER(c_uint32))),
        ("importFromBufferToWorking", OPENVR_FNTABLE_CALLTYPE(openvr_bool, c_char_p, c_uint32)),
    ]


class IVRChaperoneSetup(object):
    def __init__(self):
        version_key = IVRChaperoneSetup_Version
        if not isInterfaceVersionValid(version_key):
            _checkInitError(VRInitError_Init_InterfaceNotFound)
        # Thank you lukexi https://github.com/lukexi/openvr-hs/blob/master/cbits/openvr_capi_helper.c#L9
        fn_key = b"FnTable:" + version_key
        fn_type = IVRChaperoneSetup_FnTable
        fn_table_ptr = cast(getGenericInterface(fn_key), POINTER(fn_type))
        if fn_table_ptr is None:
            raise OpenVRError("Error retrieving VR API for IVRChaperoneSetup")
        self.function_table = fn_table_ptr.contents

    def commitWorkingCopy(self, configFile):
        fn = self.function_table.commitWorkingCopy
        result = fn(configFile)
        return result

    def revertWorkingCopy(self):
        fn = self.function_table.revertWorkingCopy
        result = fn()

    def getWorkingPlayAreaSize(self):
        fn = self.function_table.getWorkingPlayAreaSize
        pSizeX = c_float()
        pSizeZ = c_float()
        result = fn(byref(pSizeX), byref(pSizeZ))
        return result, pSizeX, pSizeZ

    def getWorkingPlayAreaRect(self):
        fn = self.function_table.getWorkingPlayAreaRect
        rect = HmdQuad_t()
        result = fn(byref(rect))
        return result, rect

    def getWorkingCollisionBoundsInfo(self):
        fn = self.function_table.getWorkingCollisionBoundsInfo
        pQuadsBuffer = HmdQuad_t()
        punQuadsCount = c_uint32()
        result = fn(byref(pQuadsBuffer), byref(punQuadsCount))
        return result, pQuadsBuffer, punQuadsCount

    def getLiveCollisionBoundsInfo(self):
        fn = self.function_table.getLiveCollisionBoundsInfo
        pQuadsBuffer = HmdQuad_t()
        punQuadsCount = c_uint32()
        result = fn(byref(pQuadsBuffer), byref(punQuadsCount))
        return result, pQuadsBuffer, punQuadsCount

    def getWorkingSeatedZeroPoseToRawTrackingPose(self):
        fn = self.function_table.getWorkingSeatedZeroPoseToRawTrackingPose
        pmatSeatedZeroPoseToRawTrackingPose = HmdMatrix34_t()
        result = fn(byref(pmatSeatedZeroPoseToRawTrackingPose))
        return result, pmatSeatedZeroPoseToRawTrackingPose

    def getWorkingStandingZeroPoseToRawTrackingPose(self):
        fn = self.function_table.getWorkingStandingZeroPoseToRawTrackingPose
        pmatStandingZeroPoseToRawTrackingPose = HmdMatrix34_t()
        result = fn(byref(pmatStandingZeroPoseToRawTrackingPose))
        return result, pmatStandingZeroPoseToRawTrackingPose

    def setWorkingPlayAreaSize(self, sizeX, sizeZ):
        fn = self.function_table.setWorkingPlayAreaSize
        result = fn(sizeX, sizeZ)

    def setWorkingCollisionBoundsInfo(self, unQuadsCount):
        fn = self.function_table.setWorkingCollisionBoundsInfo
        pQuadsBuffer = HmdQuad_t()
        result = fn(byref(pQuadsBuffer), unQuadsCount)
        return pQuadsBuffer

    def setWorkingSeatedZeroPoseToRawTrackingPose(self):
        fn = self.function_table.setWorkingSeatedZeroPoseToRawTrackingPose
        pMatSeatedZeroPoseToRawTrackingPose = HmdMatrix34_t()
        result = fn(byref(pMatSeatedZeroPoseToRawTrackingPose))
        return pMatSeatedZeroPoseToRawTrackingPose

    def setWorkingStandingZeroPoseToRawTrackingPose(self):
        fn = self.function_table.setWorkingStandingZeroPoseToRawTrackingPose
        pMatStandingZeroPoseToRawTrackingPose = HmdMatrix34_t()
        result = fn(byref(pMatStandingZeroPoseToRawTrackingPose))
        return pMatStandingZeroPoseToRawTrackingPose

    def reloadFromDisk(self, configFile):
        fn = self.function_table.reloadFromDisk
        result = fn(configFile)

    def getLiveSeatedZeroPoseToRawTrackingPose(self):
        fn = self.function_table.getLiveSeatedZeroPoseToRawTrackingPose
        pmatSeatedZeroPoseToRawTrackingPose = HmdMatrix34_t()
        result = fn(byref(pmatSeatedZeroPoseToRawTrackingPose))
        return result, pmatSeatedZeroPoseToRawTrackingPose

    def setWorkingCollisionBoundsTagsInfo(self, unTagCount):
        fn = self.function_table.setWorkingCollisionBoundsTagsInfo
        pTagsBuffer = c_uint8()
        result = fn(byref(pTagsBuffer), unTagCount)
        return pTagsBuffer

    def getLiveCollisionBoundsTagsInfo(self):
        fn = self.function_table.getLiveCollisionBoundsTagsInfo
        pTagsBuffer = c_uint8()
        punTagCount = c_uint32()
        result = fn(byref(pTagsBuffer), byref(punTagCount))
        return result, pTagsBuffer, punTagCount

    def setWorkingPhysicalBoundsInfo(self, unQuadsCount):
        fn = self.function_table.setWorkingPhysicalBoundsInfo
        pQuadsBuffer = HmdQuad_t()
        result = fn(byref(pQuadsBuffer), unQuadsCount)
        return result, pQuadsBuffer

    def getLivePhysicalBoundsInfo(self):
        fn = self.function_table.getLivePhysicalBoundsInfo
        pQuadsBuffer = HmdQuad_t()
        punQuadsCount = c_uint32()
        result = fn(byref(pQuadsBuffer), byref(punQuadsCount))
        return result, pQuadsBuffer, punQuadsCount

    def exportLiveToBuffer(self, pBuffer):
        fn = self.function_table.exportLiveToBuffer
        pnBufferLength = c_uint32()
        result = fn(pBuffer, byref(pnBufferLength))
        return result, pnBufferLength

    def importFromBufferToWorking(self, pBuffer, nImportFlags):
        fn = self.function_table.importFromBufferToWorking
        result = fn(pBuffer, nImportFlags)
        return result



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
        ("getFrameTimeRemaining", OPENVR_FNTABLE_CALLTYPE(c_float)),
        ("fadeToColor", OPENVR_FNTABLE_CALLTYPE(None, c_float, c_float, c_float, c_float, c_float, openvr_bool)),
        ("fadeGrid", OPENVR_FNTABLE_CALLTYPE(None, c_float, openvr_bool)),
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
    ]


class IVRCompositor(object):
    def __init__(self):
        version_key = IVRCompositor_Version
        if not isInterfaceVersionValid(version_key):
            _checkInitError(VRInitError_Init_InterfaceNotFound)
        # Thank you lukexi https://github.com/lukexi/openvr-hs/blob/master/cbits/openvr_capi_helper.c#L9
        fn_key = b"FnTable:" + version_key
        fn_type = IVRCompositor_FnTable
        fn_table_ptr = cast(getGenericInterface(fn_key), POINTER(fn_type))
        if fn_table_ptr is None:
            raise OpenVRError("Error retrieving VR API for IVRCompositor")
        self.function_table = fn_table_ptr.contents

    def setTrackingSpace(self, eOrigin):
        fn = self.function_table.setTrackingSpace
        result = fn(eOrigin)

    def getTrackingSpace(self):
        fn = self.function_table.getTrackingSpace
        result = fn()
        return result

    def waitGetPoses(self, unRenderPoseArrayCount, unGamePoseArrayCount):
        fn = self.function_table.waitGetPoses
        pRenderPoseArray = TrackedDevicePose_t()
        pGamePoseArray = TrackedDevicePose_t()
        result = fn(byref(pRenderPoseArray), unRenderPoseArrayCount, byref(pGamePoseArray), unGamePoseArrayCount)
        return result, pRenderPoseArray, pGamePoseArray

    def getLastPoses(self, unRenderPoseArrayCount, unGamePoseArrayCount):
        fn = self.function_table.getLastPoses
        pRenderPoseArray = TrackedDevicePose_t()
        pGamePoseArray = TrackedDevicePose_t()
        result = fn(byref(pRenderPoseArray), unRenderPoseArrayCount, byref(pGamePoseArray), unGamePoseArrayCount)
        return result, pRenderPoseArray, pGamePoseArray

    def getLastPoseForTrackedDeviceIndex(self, unDeviceIndex):
        fn = self.function_table.getLastPoseForTrackedDeviceIndex
        pOutputPose = TrackedDevicePose_t()
        pOutputGamePose = TrackedDevicePose_t()
        result = fn(unDeviceIndex, byref(pOutputPose), byref(pOutputGamePose))
        return result, pOutputPose, pOutputGamePose

    def submit(self, eEye, nSubmitFlags):
        fn = self.function_table.submit
        pTexture = Texture_t()
        pBounds = VRTextureBounds_t()
        result = fn(eEye, byref(pTexture), byref(pBounds), nSubmitFlags)
        return result, pTexture, pBounds

    def clearLastSubmittedFrame(self):
        fn = self.function_table.clearLastSubmittedFrame
        result = fn()

    def postPresentHandoff(self):
        fn = self.function_table.postPresentHandoff
        result = fn()

    def getFrameTiming(self, unFramesAgo):
        fn = self.function_table.getFrameTiming
        pTiming = Compositor_FrameTiming()
        result = fn(byref(pTiming), unFramesAgo)
        return result, pTiming

    def getFrameTimeRemaining(self):
        fn = self.function_table.getFrameTimeRemaining
        result = fn()
        return result

    def fadeToColor(self, fSeconds, fRed, fGreen, fBlue, fAlpha, bBackground):
        fn = self.function_table.fadeToColor
        result = fn(fSeconds, fRed, fGreen, fBlue, fAlpha, bBackground)

    def fadeGrid(self, fSeconds, bFadeIn):
        fn = self.function_table.fadeGrid
        result = fn(fSeconds, bFadeIn)

    def setSkyboxOverride(self, unTextureCount):
        fn = self.function_table.setSkyboxOverride
        pTextures = Texture_t()
        result = fn(byref(pTextures), unTextureCount)
        return result, pTextures

    def clearSkyboxOverride(self):
        fn = self.function_table.clearSkyboxOverride
        result = fn()

    def compositorBringToFront(self):
        fn = self.function_table.compositorBringToFront
        result = fn()

    def compositorGoToBack(self):
        fn = self.function_table.compositorGoToBack
        result = fn()

    def compositorQuit(self):
        fn = self.function_table.compositorQuit
        result = fn()

    def isFullscreen(self):
        fn = self.function_table.isFullscreen
        result = fn()
        return result

    def getCurrentSceneFocusProcess(self):
        fn = self.function_table.getCurrentSceneFocusProcess
        result = fn()
        return result

    def getLastFrameRenderer(self):
        fn = self.function_table.getLastFrameRenderer
        result = fn()
        return result

    def canRenderScene(self):
        fn = self.function_table.canRenderScene
        result = fn()
        return result

    def showMirrorWindow(self):
        fn = self.function_table.showMirrorWindow
        result = fn()

    def hideMirrorWindow(self):
        fn = self.function_table.hideMirrorWindow
        result = fn()

    def isMirrorWindowVisible(self):
        fn = self.function_table.isMirrorWindowVisible
        result = fn()
        return result

    def compositorDumpImages(self):
        fn = self.function_table.compositorDumpImages
        result = fn()

    def shouldAppRenderWithLowResources(self):
        fn = self.function_table.shouldAppRenderWithLowResources
        result = fn()
        return result

    def forceInterleavedReprojectionOn(self, bOverride):
        fn = self.function_table.forceInterleavedReprojectionOn
        result = fn(bOverride)

    def forceReconnectProcess(self):
        fn = self.function_table.forceReconnectProcess
        result = fn()

    def suspendRendering(self, bSuspend):
        fn = self.function_table.suspendRendering
        result = fn(bSuspend)



class IVROverlay_FnTable(Structure):
    _fields_ = [
        ("findOverlay", OPENVR_FNTABLE_CALLTYPE(EVROverlayError, c_char_p, POINTER(VROverlayHandle_t))),
        ("createOverlay", OPENVR_FNTABLE_CALLTYPE(EVROverlayError, c_char_p, c_char_p, POINTER(VROverlayHandle_t))),
        ("destroyOverlay", OPENVR_FNTABLE_CALLTYPE(EVROverlayError, VROverlayHandle_t)),
        ("setHighQualityOverlay", OPENVR_FNTABLE_CALLTYPE(EVROverlayError, VROverlayHandle_t)),
        ("getHighQualityOverlay", OPENVR_FNTABLE_CALLTYPE(VROverlayHandle_t)),
        ("getOverlayKey", OPENVR_FNTABLE_CALLTYPE(c_uint32, VROverlayHandle_t, c_char_p, c_uint32, POINTER(EVROverlayError))),
        ("getOverlayName", OPENVR_FNTABLE_CALLTYPE(c_uint32, VROverlayHandle_t, c_char_p, c_uint32, POINTER(EVROverlayError))),
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
        ("setOverlayWidthInMeters", OPENVR_FNTABLE_CALLTYPE(EVROverlayError, VROverlayHandle_t, c_float)),
        ("getOverlayWidthInMeters", OPENVR_FNTABLE_CALLTYPE(EVROverlayError, VROverlayHandle_t, POINTER(c_float))),
        ("setOverlayAutoCurveDistanceRangeInMeters", OPENVR_FNTABLE_CALLTYPE(EVROverlayError, VROverlayHandle_t, c_float, c_float)),
        ("getOverlayAutoCurveDistanceRangeInMeters", OPENVR_FNTABLE_CALLTYPE(EVROverlayError, VROverlayHandle_t, POINTER(c_float), POINTER(c_float))),
        ("setOverlayTextureColorSpace", OPENVR_FNTABLE_CALLTYPE(EVROverlayError, VROverlayHandle_t, EColorSpace)),
        ("getOverlayTextureColorSpace", OPENVR_FNTABLE_CALLTYPE(EVROverlayError, VROverlayHandle_t, POINTER(EColorSpace))),
        ("setOverlayTextureBounds", OPENVR_FNTABLE_CALLTYPE(EVROverlayError, VROverlayHandle_t, POINTER(VRTextureBounds_t))),
        ("getOverlayTextureBounds", OPENVR_FNTABLE_CALLTYPE(EVROverlayError, VROverlayHandle_t, POINTER(VRTextureBounds_t))),
        ("getOverlayTransformType", OPENVR_FNTABLE_CALLTYPE(EVROverlayError, VROverlayHandle_t, POINTER(VROverlayTransformType))),
        ("setOverlayTransformAbsolute", OPENVR_FNTABLE_CALLTYPE(EVROverlayError, VROverlayHandle_t, ETrackingUniverseOrigin, POINTER(HmdMatrix34_t))),
        ("getOverlayTransformAbsolute", OPENVR_FNTABLE_CALLTYPE(EVROverlayError, VROverlayHandle_t, POINTER(ETrackingUniverseOrigin), POINTER(HmdMatrix34_t))),
        ("setOverlayTransformTrackedDeviceRelative", OPENVR_FNTABLE_CALLTYPE(EVROverlayError, VROverlayHandle_t, TrackedDeviceIndex_t, POINTER(HmdMatrix34_t))),
        ("getOverlayTransformTrackedDeviceRelative", OPENVR_FNTABLE_CALLTYPE(EVROverlayError, VROverlayHandle_t, POINTER(TrackedDeviceIndex_t), POINTER(HmdMatrix34_t))),
        ("setOverlayTransformTrackedDeviceComponent", OPENVR_FNTABLE_CALLTYPE(EVROverlayError, VROverlayHandle_t, TrackedDeviceIndex_t, c_char_p)),
        ("getOverlayTransformTrackedDeviceComponent", OPENVR_FNTABLE_CALLTYPE(EVROverlayError, VROverlayHandle_t, POINTER(TrackedDeviceIndex_t), c_char_p, c_uint32)),
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
        ("handleControllerOverlayInteractionAsMouse", OPENVR_FNTABLE_CALLTYPE(openvr_bool, VROverlayHandle_t, TrackedDeviceIndex_t)),
        ("isHoverTargetOverlay", OPENVR_FNTABLE_CALLTYPE(openvr_bool, VROverlayHandle_t)),
        ("getGamepadFocusOverlay", OPENVR_FNTABLE_CALLTYPE(VROverlayHandle_t)),
        ("setGamepadFocusOverlay", OPENVR_FNTABLE_CALLTYPE(EVROverlayError, VROverlayHandle_t)),
        ("setOverlayNeighbor", OPENVR_FNTABLE_CALLTYPE(EVROverlayError, EOverlayDirection, VROverlayHandle_t, VROverlayHandle_t)),
        ("moveGamepadFocusToNeighbor", OPENVR_FNTABLE_CALLTYPE(EVROverlayError, EOverlayDirection, VROverlayHandle_t)),
        ("setOverlayTexture", OPENVR_FNTABLE_CALLTYPE(EVROverlayError, VROverlayHandle_t, POINTER(Texture_t))),
        ("clearOverlayTexture", OPENVR_FNTABLE_CALLTYPE(EVROverlayError, VROverlayHandle_t)),
        ("setOverlayRaw", OPENVR_FNTABLE_CALLTYPE(EVROverlayError, VROverlayHandle_t, c_void_p, c_uint32, c_uint32, c_uint32)),
        ("setOverlayFromFile", OPENVR_FNTABLE_CALLTYPE(EVROverlayError, VROverlayHandle_t, c_char_p)),
        ("getOverlayTexture", OPENVR_FNTABLE_CALLTYPE(EVROverlayError, VROverlayHandle_t, POINTER(c_void_p), c_void_p, POINTER(c_uint32), POINTER(c_uint32), POINTER(c_uint32), POINTER(EGraphicsAPIConvention), POINTER(EColorSpace))),
        ("releaseNativeOverlayHandle", OPENVR_FNTABLE_CALLTYPE(EVROverlayError, VROverlayHandle_t, c_void_p)),
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
    ]


class IVROverlay(object):
    def __init__(self):
        version_key = IVROverlay_Version
        if not isInterfaceVersionValid(version_key):
            _checkInitError(VRInitError_Init_InterfaceNotFound)
        # Thank you lukexi https://github.com/lukexi/openvr-hs/blob/master/cbits/openvr_capi_helper.c#L9
        fn_key = b"FnTable:" + version_key
        fn_type = IVROverlay_FnTable
        fn_table_ptr = cast(getGenericInterface(fn_key), POINTER(fn_type))
        if fn_table_ptr is None:
            raise OpenVRError("Error retrieving VR API for IVROverlay")
        self.function_table = fn_table_ptr.contents

    def findOverlay(self, pchOverlayKey):
        fn = self.function_table.findOverlay
        pOverlayHandle = VROverlayHandle_t()
        result = fn(pchOverlayKey, byref(pOverlayHandle))
        return result, pOverlayHandle

    def createOverlay(self, pchOverlayKey, pchOverlayFriendlyName):
        fn = self.function_table.createOverlay
        pOverlayHandle = VROverlayHandle_t()
        result = fn(pchOverlayKey, pchOverlayFriendlyName, byref(pOverlayHandle))
        return result, pOverlayHandle

    def destroyOverlay(self, ulOverlayHandle):
        fn = self.function_table.destroyOverlay
        result = fn(ulOverlayHandle)
        return result

    def setHighQualityOverlay(self, ulOverlayHandle):
        fn = self.function_table.setHighQualityOverlay
        result = fn(ulOverlayHandle)
        return result

    def getHighQualityOverlay(self):
        fn = self.function_table.getHighQualityOverlay
        result = fn()
        return result

    def getOverlayKey(self, ulOverlayHandle, pchValue, unBufferSize):
        fn = self.function_table.getOverlayKey
        pError = EVROverlayError()
        result = fn(ulOverlayHandle, pchValue, unBufferSize, byref(pError))
        return result, pError

    def getOverlayName(self, ulOverlayHandle, pchValue, unBufferSize):
        fn = self.function_table.getOverlayName
        pError = EVROverlayError()
        result = fn(ulOverlayHandle, pchValue, unBufferSize, byref(pError))
        return result, pError

    def getOverlayImageData(self, ulOverlayHandle, pvBuffer, unBufferSize):
        fn = self.function_table.getOverlayImageData
        punWidth = c_uint32()
        punHeight = c_uint32()
        result = fn(ulOverlayHandle, pvBuffer, unBufferSize, byref(punWidth), byref(punHeight))
        return result, punWidth, punHeight

    def getOverlayErrorNameFromEnum(self, error):
        fn = self.function_table.getOverlayErrorNameFromEnum
        result = fn(error)
        return result

    def setOverlayRenderingPid(self, ulOverlayHandle, unPID):
        fn = self.function_table.setOverlayRenderingPid
        result = fn(ulOverlayHandle, unPID)
        return result

    def getOverlayRenderingPid(self, ulOverlayHandle):
        fn = self.function_table.getOverlayRenderingPid
        result = fn(ulOverlayHandle)
        return result

    def setOverlayFlag(self, ulOverlayHandle, eOverlayFlag, bEnabled):
        fn = self.function_table.setOverlayFlag
        result = fn(ulOverlayHandle, eOverlayFlag, bEnabled)
        return result

    def getOverlayFlag(self, ulOverlayHandle, eOverlayFlag):
        fn = self.function_table.getOverlayFlag
        pbEnabled = openvr_bool()
        result = fn(ulOverlayHandle, eOverlayFlag, byref(pbEnabled))
        return result, pbEnabled

    def setOverlayColor(self, ulOverlayHandle, fRed, fGreen, fBlue):
        fn = self.function_table.setOverlayColor
        result = fn(ulOverlayHandle, fRed, fGreen, fBlue)
        return result

    def getOverlayColor(self, ulOverlayHandle):
        fn = self.function_table.getOverlayColor
        pfRed = c_float()
        pfGreen = c_float()
        pfBlue = c_float()
        result = fn(ulOverlayHandle, byref(pfRed), byref(pfGreen), byref(pfBlue))
        return result, pfRed, pfGreen, pfBlue

    def setOverlayAlpha(self, ulOverlayHandle, fAlpha):
        fn = self.function_table.setOverlayAlpha
        result = fn(ulOverlayHandle, fAlpha)
        return result

    def getOverlayAlpha(self, ulOverlayHandle):
        fn = self.function_table.getOverlayAlpha
        pfAlpha = c_float()
        result = fn(ulOverlayHandle, byref(pfAlpha))
        return result, pfAlpha

    def setOverlayWidthInMeters(self, ulOverlayHandle, fWidthInMeters):
        fn = self.function_table.setOverlayWidthInMeters
        result = fn(ulOverlayHandle, fWidthInMeters)
        return result

    def getOverlayWidthInMeters(self, ulOverlayHandle):
        fn = self.function_table.getOverlayWidthInMeters
        pfWidthInMeters = c_float()
        result = fn(ulOverlayHandle, byref(pfWidthInMeters))
        return result, pfWidthInMeters

    def setOverlayAutoCurveDistanceRangeInMeters(self, ulOverlayHandle, fMinDistanceInMeters, fMaxDistanceInMeters):
        fn = self.function_table.setOverlayAutoCurveDistanceRangeInMeters
        result = fn(ulOverlayHandle, fMinDistanceInMeters, fMaxDistanceInMeters)
        return result

    def getOverlayAutoCurveDistanceRangeInMeters(self, ulOverlayHandle):
        fn = self.function_table.getOverlayAutoCurveDistanceRangeInMeters
        pfMinDistanceInMeters = c_float()
        pfMaxDistanceInMeters = c_float()
        result = fn(ulOverlayHandle, byref(pfMinDistanceInMeters), byref(pfMaxDistanceInMeters))
        return result, pfMinDistanceInMeters, pfMaxDistanceInMeters

    def setOverlayTextureColorSpace(self, ulOverlayHandle, eTextureColorSpace):
        fn = self.function_table.setOverlayTextureColorSpace
        result = fn(ulOverlayHandle, eTextureColorSpace)
        return result

    def getOverlayTextureColorSpace(self, ulOverlayHandle):
        fn = self.function_table.getOverlayTextureColorSpace
        peTextureColorSpace = EColorSpace()
        result = fn(ulOverlayHandle, byref(peTextureColorSpace))
        return result, peTextureColorSpace

    def setOverlayTextureBounds(self, ulOverlayHandle):
        fn = self.function_table.setOverlayTextureBounds
        pOverlayTextureBounds = VRTextureBounds_t()
        result = fn(ulOverlayHandle, byref(pOverlayTextureBounds))
        return result, pOverlayTextureBounds

    def getOverlayTextureBounds(self, ulOverlayHandle):
        fn = self.function_table.getOverlayTextureBounds
        pOverlayTextureBounds = VRTextureBounds_t()
        result = fn(ulOverlayHandle, byref(pOverlayTextureBounds))
        return result, pOverlayTextureBounds

    def getOverlayTransformType(self, ulOverlayHandle):
        fn = self.function_table.getOverlayTransformType
        peTransformType = VROverlayTransformType()
        result = fn(ulOverlayHandle, byref(peTransformType))
        return result, peTransformType

    def setOverlayTransformAbsolute(self, ulOverlayHandle, eTrackingOrigin):
        fn = self.function_table.setOverlayTransformAbsolute
        pmatTrackingOriginToOverlayTransform = HmdMatrix34_t()
        result = fn(ulOverlayHandle, eTrackingOrigin, byref(pmatTrackingOriginToOverlayTransform))
        return result, pmatTrackingOriginToOverlayTransform

    def getOverlayTransformAbsolute(self, ulOverlayHandle):
        fn = self.function_table.getOverlayTransformAbsolute
        peTrackingOrigin = ETrackingUniverseOrigin()
        pmatTrackingOriginToOverlayTransform = HmdMatrix34_t()
        result = fn(ulOverlayHandle, byref(peTrackingOrigin), byref(pmatTrackingOriginToOverlayTransform))
        return result, peTrackingOrigin, pmatTrackingOriginToOverlayTransform

    def setOverlayTransformTrackedDeviceRelative(self, ulOverlayHandle, unTrackedDevice):
        fn = self.function_table.setOverlayTransformTrackedDeviceRelative
        pmatTrackedDeviceToOverlayTransform = HmdMatrix34_t()
        result = fn(ulOverlayHandle, unTrackedDevice, byref(pmatTrackedDeviceToOverlayTransform))
        return result, pmatTrackedDeviceToOverlayTransform

    def getOverlayTransformTrackedDeviceRelative(self, ulOverlayHandle):
        fn = self.function_table.getOverlayTransformTrackedDeviceRelative
        punTrackedDevice = TrackedDeviceIndex_t()
        pmatTrackedDeviceToOverlayTransform = HmdMatrix34_t()
        result = fn(ulOverlayHandle, byref(punTrackedDevice), byref(pmatTrackedDeviceToOverlayTransform))
        return result, punTrackedDevice, pmatTrackedDeviceToOverlayTransform

    def setOverlayTransformTrackedDeviceComponent(self, ulOverlayHandle, unDeviceIndex, pchComponentName):
        fn = self.function_table.setOverlayTransformTrackedDeviceComponent
        result = fn(ulOverlayHandle, unDeviceIndex, pchComponentName)
        return result

    def getOverlayTransformTrackedDeviceComponent(self, ulOverlayHandle, pchComponentName, unComponentNameSize):
        fn = self.function_table.getOverlayTransformTrackedDeviceComponent
        punDeviceIndex = TrackedDeviceIndex_t()
        result = fn(ulOverlayHandle, byref(punDeviceIndex), pchComponentName, unComponentNameSize)
        return result, punDeviceIndex

    def showOverlay(self, ulOverlayHandle):
        fn = self.function_table.showOverlay
        result = fn(ulOverlayHandle)
        return result

    def hideOverlay(self, ulOverlayHandle):
        fn = self.function_table.hideOverlay
        result = fn(ulOverlayHandle)
        return result

    def isOverlayVisible(self, ulOverlayHandle):
        fn = self.function_table.isOverlayVisible
        result = fn(ulOverlayHandle)
        return result

    def getTransformForOverlayCoordinates(self, ulOverlayHandle, eTrackingOrigin, coordinatesInOverlay):
        fn = self.function_table.getTransformForOverlayCoordinates
        pmatTransform = HmdMatrix34_t()
        result = fn(ulOverlayHandle, eTrackingOrigin, coordinatesInOverlay, byref(pmatTransform))
        return result, pmatTransform

    def pollNextOverlayEvent(self, ulOverlayHandle, uncbVREvent):
        fn = self.function_table.pollNextOverlayEvent
        pEvent = VREvent_t()
        result = fn(ulOverlayHandle, byref(pEvent), uncbVREvent)
        return result, pEvent

    def getOverlayInputMethod(self, ulOverlayHandle):
        fn = self.function_table.getOverlayInputMethod
        peInputMethod = VROverlayInputMethod()
        result = fn(ulOverlayHandle, byref(peInputMethod))
        return result, peInputMethod

    def setOverlayInputMethod(self, ulOverlayHandle, eInputMethod):
        fn = self.function_table.setOverlayInputMethod
        result = fn(ulOverlayHandle, eInputMethod)
        return result

    def getOverlayMouseScale(self, ulOverlayHandle):
        fn = self.function_table.getOverlayMouseScale
        pvecMouseScale = HmdVector2_t()
        result = fn(ulOverlayHandle, byref(pvecMouseScale))
        return result, pvecMouseScale

    def setOverlayMouseScale(self, ulOverlayHandle):
        fn = self.function_table.setOverlayMouseScale
        pvecMouseScale = HmdVector2_t()
        result = fn(ulOverlayHandle, byref(pvecMouseScale))
        return result, pvecMouseScale

    def computeOverlayIntersection(self, ulOverlayHandle):
        fn = self.function_table.computeOverlayIntersection
        pParams = VROverlayIntersectionParams_t()
        pResults = VROverlayIntersectionResults_t()
        result = fn(ulOverlayHandle, byref(pParams), byref(pResults))
        return result, pParams, pResults

    def handleControllerOverlayInteractionAsMouse(self, ulOverlayHandle, unControllerDeviceIndex):
        fn = self.function_table.handleControllerOverlayInteractionAsMouse
        result = fn(ulOverlayHandle, unControllerDeviceIndex)
        return result

    def isHoverTargetOverlay(self, ulOverlayHandle):
        fn = self.function_table.isHoverTargetOverlay
        result = fn(ulOverlayHandle)
        return result

    def getGamepadFocusOverlay(self):
        fn = self.function_table.getGamepadFocusOverlay
        result = fn()
        return result

    def setGamepadFocusOverlay(self, ulNewFocusOverlay):
        fn = self.function_table.setGamepadFocusOverlay
        result = fn(ulNewFocusOverlay)
        return result

    def setOverlayNeighbor(self, eDirection, ulFrom, ulTo):
        fn = self.function_table.setOverlayNeighbor
        result = fn(eDirection, ulFrom, ulTo)
        return result

    def moveGamepadFocusToNeighbor(self, eDirection, ulFrom):
        fn = self.function_table.moveGamepadFocusToNeighbor
        result = fn(eDirection, ulFrom)
        return result

    def setOverlayTexture(self, ulOverlayHandle):
        fn = self.function_table.setOverlayTexture
        pTexture = Texture_t()
        result = fn(ulOverlayHandle, byref(pTexture))
        return result, pTexture

    def clearOverlayTexture(self, ulOverlayHandle):
        fn = self.function_table.clearOverlayTexture
        result = fn(ulOverlayHandle)
        return result

    def setOverlayRaw(self, ulOverlayHandle, pvBuffer, unWidth, unHeight, unDepth):
        fn = self.function_table.setOverlayRaw
        result = fn(ulOverlayHandle, pvBuffer, unWidth, unHeight, unDepth)
        return result

    def setOverlayFromFile(self, ulOverlayHandle, pchFilePath):
        fn = self.function_table.setOverlayFromFile
        result = fn(ulOverlayHandle, pchFilePath)
        return result

    def getOverlayTexture(self, ulOverlayHandle, pNativeTextureRef):
        fn = self.function_table.getOverlayTexture
        pNativeTextureHandle = c_void_p()
        pWidth = c_uint32()
        pHeight = c_uint32()
        pNativeFormat = c_uint32()
        pAPI = EGraphicsAPIConvention()
        pColorSpace = EColorSpace()
        result = fn(ulOverlayHandle, byref(pNativeTextureHandle), pNativeTextureRef, byref(pWidth), byref(pHeight), byref(pNativeFormat), byref(pAPI), byref(pColorSpace))
        return result, pNativeTextureHandle, pWidth, pHeight, pNativeFormat, pAPI, pColorSpace

    def releaseNativeOverlayHandle(self, ulOverlayHandle, pNativeTextureHandle):
        fn = self.function_table.releaseNativeOverlayHandle
        result = fn(ulOverlayHandle, pNativeTextureHandle)
        return result

    def createDashboardOverlay(self, pchOverlayKey, pchOverlayFriendlyName):
        fn = self.function_table.createDashboardOverlay
        pMainHandle = VROverlayHandle_t()
        pThumbnailHandle = VROverlayHandle_t()
        result = fn(pchOverlayKey, pchOverlayFriendlyName, byref(pMainHandle), byref(pThumbnailHandle))
        return result, pMainHandle, pThumbnailHandle

    def isDashboardVisible(self):
        fn = self.function_table.isDashboardVisible
        result = fn()
        return result

    def isActiveDashboardOverlay(self, ulOverlayHandle):
        fn = self.function_table.isActiveDashboardOverlay
        result = fn(ulOverlayHandle)
        return result

    def setDashboardOverlaySceneProcess(self, ulOverlayHandle, unProcessId):
        fn = self.function_table.setDashboardOverlaySceneProcess
        result = fn(ulOverlayHandle, unProcessId)
        return result

    def getDashboardOverlaySceneProcess(self, ulOverlayHandle):
        fn = self.function_table.getDashboardOverlaySceneProcess
        punProcessId = c_uint32()
        result = fn(ulOverlayHandle, byref(punProcessId))
        return result, punProcessId

    def showDashboard(self, pchOverlayToShow):
        fn = self.function_table.showDashboard
        result = fn(pchOverlayToShow)

    def getPrimaryDashboardDevice(self):
        fn = self.function_table.getPrimaryDashboardDevice
        result = fn()
        return result

    def showKeyboard(self, eInputMode, eLineInputMode, pchDescription, unCharMax, pchExistingText, bUseMinimalMode, uUserValue):
        fn = self.function_table.showKeyboard
        result = fn(eInputMode, eLineInputMode, pchDescription, unCharMax, pchExistingText, bUseMinimalMode, uUserValue)
        return result

    def showKeyboardForOverlay(self, ulOverlayHandle, eInputMode, eLineInputMode, pchDescription, unCharMax, pchExistingText, bUseMinimalMode, uUserValue):
        fn = self.function_table.showKeyboardForOverlay
        result = fn(ulOverlayHandle, eInputMode, eLineInputMode, pchDescription, unCharMax, pchExistingText, bUseMinimalMode, uUserValue)
        return result

    def getKeyboardText(self, pchText, cchText):
        fn = self.function_table.getKeyboardText
        result = fn(pchText, cchText)
        return result

    def hideKeyboard(self):
        fn = self.function_table.hideKeyboard
        result = fn()

    def setKeyboardTransformAbsolute(self, eTrackingOrigin):
        fn = self.function_table.setKeyboardTransformAbsolute
        pmatTrackingOriginToKeyboardTransform = HmdMatrix34_t()
        result = fn(eTrackingOrigin, byref(pmatTrackingOriginToKeyboardTransform))
        return pmatTrackingOriginToKeyboardTransform

    def setKeyboardPositionForOverlay(self, ulOverlayHandle, avoidRect):
        fn = self.function_table.setKeyboardPositionForOverlay
        result = fn(ulOverlayHandle, avoidRect)



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
        ("getComponentState", OPENVR_FNTABLE_CALLTYPE(openvr_bool, c_char_p, c_char_p, POINTER(VRControllerState_t), POINTER(RenderModel_ControllerMode_State_t), POINTER(RenderModel_ComponentState_t))),
        ("renderModelHasComponent", OPENVR_FNTABLE_CALLTYPE(openvr_bool, c_char_p, c_char_p)),
    ]


class IVRRenderModels(object):
    def __init__(self):
        version_key = IVRRenderModels_Version
        if not isInterfaceVersionValid(version_key):
            _checkInitError(VRInitError_Init_InterfaceNotFound)
        # Thank you lukexi https://github.com/lukexi/openvr-hs/blob/master/cbits/openvr_capi_helper.c#L9
        fn_key = b"FnTable:" + version_key
        fn_type = IVRRenderModels_FnTable
        fn_table_ptr = cast(getGenericInterface(fn_key), POINTER(fn_type))
        if fn_table_ptr is None:
            raise OpenVRError("Error retrieving VR API for IVRRenderModels")
        self.function_table = fn_table_ptr.contents

    def loadRenderModel_Async(self, pchRenderModelName):
        fn = self.function_table.loadRenderModel_Async
        ppRenderModel = POINTER(RenderModel_t)()
        result = fn(pchRenderModelName, byref(ppRenderModel))
        return result, ppRenderModel

    def freeRenderModel(self):
        fn = self.function_table.freeRenderModel
        pRenderModel = RenderModel_t()
        result = fn(byref(pRenderModel))
        return pRenderModel

    def loadTexture_Async(self, textureId):
        fn = self.function_table.loadTexture_Async
        ppTexture = POINTER(RenderModel_TextureMap_t)()
        result = fn(textureId, byref(ppTexture))
        return result, ppTexture

    def freeTexture(self):
        fn = self.function_table.freeTexture
        pTexture = RenderModel_TextureMap_t()
        result = fn(byref(pTexture))
        return pTexture

    def loadTextureD3D11_Async(self, textureId, pD3D11Device):
        fn = self.function_table.loadTextureD3D11_Async
        ppD3D11Texture2D = c_void_p()
        result = fn(textureId, pD3D11Device, byref(ppD3D11Texture2D))
        return result, ppD3D11Texture2D

    def loadIntoTextureD3D11_Async(self, textureId, pDstTexture):
        fn = self.function_table.loadIntoTextureD3D11_Async
        result = fn(textureId, pDstTexture)
        return result

    def freeTextureD3D11(self, pD3D11Texture2D):
        fn = self.function_table.freeTextureD3D11
        result = fn(pD3D11Texture2D)

    def getRenderModelName(self, unRenderModelIndex, pchRenderModelName, unRenderModelNameLen):
        fn = self.function_table.getRenderModelName
        result = fn(unRenderModelIndex, pchRenderModelName, unRenderModelNameLen)
        return result

    def getRenderModelCount(self):
        fn = self.function_table.getRenderModelCount
        result = fn()
        return result

    def getComponentCount(self, pchRenderModelName):
        fn = self.function_table.getComponentCount
        result = fn(pchRenderModelName)
        return result

    def getComponentName(self, pchRenderModelName, unComponentIndex, pchComponentName, unComponentNameLen):
        fn = self.function_table.getComponentName
        result = fn(pchRenderModelName, unComponentIndex, pchComponentName, unComponentNameLen)
        return result

    def getComponentButtonMask(self, pchRenderModelName, pchComponentName):
        fn = self.function_table.getComponentButtonMask
        result = fn(pchRenderModelName, pchComponentName)
        return result

    def getComponentRenderModelName(self, pchRenderModelName, pchComponentName, pchComponentRenderModelName, unComponentRenderModelNameLen):
        fn = self.function_table.getComponentRenderModelName
        result = fn(pchRenderModelName, pchComponentName, pchComponentRenderModelName, unComponentRenderModelNameLen)
        return result

    def getComponentState(self, pchRenderModelName, pchComponentName):
        fn = self.function_table.getComponentState
        pControllerState = VRControllerState_t()
        pState = RenderModel_ControllerMode_State_t()
        pComponentState = RenderModel_ComponentState_t()
        result = fn(pchRenderModelName, pchComponentName, byref(pControllerState), byref(pState), byref(pComponentState))
        return result, pControllerState, pState, pComponentState

    def renderModelHasComponent(self, pchRenderModelName, pchComponentName):
        fn = self.function_table.renderModelHasComponent
        result = fn(pchRenderModelName, pchComponentName)
        return result



class IVRNotifications_FnTable(Structure):
    _fields_ = [
        ("createNotification", OPENVR_FNTABLE_CALLTYPE(EVRNotificationError, VROverlayHandle_t, c_uint64, EVRNotificationType, c_char_p, EVRNotificationStyle, POINTER(NotificationBitmap_t), POINTER(VRNotificationId))),
        ("removeNotification", OPENVR_FNTABLE_CALLTYPE(EVRNotificationError, VRNotificationId)),
    ]


class IVRNotifications(object):
    def __init__(self):
        version_key = IVRNotifications_Version
        if not isInterfaceVersionValid(version_key):
            _checkInitError(VRInitError_Init_InterfaceNotFound)
        # Thank you lukexi https://github.com/lukexi/openvr-hs/blob/master/cbits/openvr_capi_helper.c#L9
        fn_key = b"FnTable:" + version_key
        fn_type = IVRNotifications_FnTable
        fn_table_ptr = cast(getGenericInterface(fn_key), POINTER(fn_type))
        if fn_table_ptr is None:
            raise OpenVRError("Error retrieving VR API for IVRNotifications")
        self.function_table = fn_table_ptr.contents

    def createNotification(self, ulOverlayHandle, ulUserValue, type, pchText, style):
        fn = self.function_table.createNotification
        pImage = NotificationBitmap_t()
        pNotificationId = VRNotificationId()
        result = fn(ulOverlayHandle, ulUserValue, type, pchText, style, byref(pImage), byref(pNotificationId))
        return result, pImage, pNotificationId

    def removeNotification(self, notificationId):
        fn = self.function_table.removeNotification
        result = fn(notificationId)
        return result



class IVRSettings_FnTable(Structure):
    _fields_ = [
        ("getSettingsErrorNameFromEnum", OPENVR_FNTABLE_CALLTYPE(c_char_p, EVRSettingsError)),
        ("sync", OPENVR_FNTABLE_CALLTYPE(openvr_bool, openvr_bool, POINTER(EVRSettingsError))),
        ("getBool", OPENVR_FNTABLE_CALLTYPE(openvr_bool, c_char_p, c_char_p, openvr_bool, POINTER(EVRSettingsError))),
        ("setBool", OPENVR_FNTABLE_CALLTYPE(None, c_char_p, c_char_p, openvr_bool, POINTER(EVRSettingsError))),
        ("getInt32", OPENVR_FNTABLE_CALLTYPE(c_int32, c_char_p, c_char_p, c_int32, POINTER(EVRSettingsError))),
        ("setInt32", OPENVR_FNTABLE_CALLTYPE(None, c_char_p, c_char_p, c_int32, POINTER(EVRSettingsError))),
        ("getFloat", OPENVR_FNTABLE_CALLTYPE(c_float, c_char_p, c_char_p, c_float, POINTER(EVRSettingsError))),
        ("setFloat", OPENVR_FNTABLE_CALLTYPE(None, c_char_p, c_char_p, c_float, POINTER(EVRSettingsError))),
        ("getString", OPENVR_FNTABLE_CALLTYPE(None, c_char_p, c_char_p, c_char_p, c_uint32, c_char_p, POINTER(EVRSettingsError))),
        ("setString", OPENVR_FNTABLE_CALLTYPE(None, c_char_p, c_char_p, c_char_p, POINTER(EVRSettingsError))),
        ("removeSection", OPENVR_FNTABLE_CALLTYPE(None, c_char_p, POINTER(EVRSettingsError))),
        ("removeKeyInSection", OPENVR_FNTABLE_CALLTYPE(None, c_char_p, c_char_p, POINTER(EVRSettingsError))),
    ]


class IVRSettings(object):
    def __init__(self):
        version_key = IVRSettings_Version
        if not isInterfaceVersionValid(version_key):
            _checkInitError(VRInitError_Init_InterfaceNotFound)
        # Thank you lukexi https://github.com/lukexi/openvr-hs/blob/master/cbits/openvr_capi_helper.c#L9
        fn_key = b"FnTable:" + version_key
        fn_type = IVRSettings_FnTable
        fn_table_ptr = cast(getGenericInterface(fn_key), POINTER(fn_type))
        if fn_table_ptr is None:
            raise OpenVRError("Error retrieving VR API for IVRSettings")
        self.function_table = fn_table_ptr.contents

    def getSettingsErrorNameFromEnum(self, eError):
        fn = self.function_table.getSettingsErrorNameFromEnum
        result = fn(eError)
        return result

    def sync(self, bForce):
        fn = self.function_table.sync
        peError = EVRSettingsError()
        result = fn(bForce, byref(peError))
        return result, peError

    def getBool(self, pchSection, pchSettingsKey, bDefaultValue):
        fn = self.function_table.getBool
        peError = EVRSettingsError()
        result = fn(pchSection, pchSettingsKey, bDefaultValue, byref(peError))
        return result, peError

    def setBool(self, pchSection, pchSettingsKey, bValue):
        fn = self.function_table.setBool
        peError = EVRSettingsError()
        result = fn(pchSection, pchSettingsKey, bValue, byref(peError))
        return peError

    def getInt32(self, pchSection, pchSettingsKey, nDefaultValue):
        fn = self.function_table.getInt32
        peError = EVRSettingsError()
        result = fn(pchSection, pchSettingsKey, nDefaultValue, byref(peError))
        return result, peError

    def setInt32(self, pchSection, pchSettingsKey, nValue):
        fn = self.function_table.setInt32
        peError = EVRSettingsError()
        result = fn(pchSection, pchSettingsKey, nValue, byref(peError))
        return peError

    def getFloat(self, pchSection, pchSettingsKey, flDefaultValue):
        fn = self.function_table.getFloat
        peError = EVRSettingsError()
        result = fn(pchSection, pchSettingsKey, flDefaultValue, byref(peError))
        return result, peError

    def setFloat(self, pchSection, pchSettingsKey, flValue):
        fn = self.function_table.setFloat
        peError = EVRSettingsError()
        result = fn(pchSection, pchSettingsKey, flValue, byref(peError))
        return peError

    def getString(self, pchSection, pchSettingsKey, pchValue, unValueLen, pchDefaultValue):
        fn = self.function_table.getString
        peError = EVRSettingsError()
        result = fn(pchSection, pchSettingsKey, pchValue, unValueLen, pchDefaultValue, byref(peError))
        return peError

    def setString(self, pchSection, pchSettingsKey, pchValue):
        fn = self.function_table.setString
        peError = EVRSettingsError()
        result = fn(pchSection, pchSettingsKey, pchValue, byref(peError))
        return peError

    def removeSection(self, pchSection):
        fn = self.function_table.removeSection
        peError = EVRSettingsError()
        result = fn(pchSection, byref(peError))
        return peError

    def removeKeyInSection(self, pchSection, pchSettingsKey):
        fn = self.function_table.removeKeyInSection
        peError = EVRSettingsError()
        result = fn(pchSection, pchSettingsKey, byref(peError))
        return peError




########################
### Expose functions ###
########################

def _checkInitError(error):
    """
    Replace openvr error return code with a python exception
    """
    if error.value != VRInitError_None.value:
        shutdown()
        raise OpenVRError(getVRInitErrorAsSymbol(error) + str(error))    


# Copying VR_Init inline implementation from https://github.com/ValveSoftware/openvr/blob/master/headers/openvr.h
# and from https://github.com/phr00t/jMonkeyVR/blob/master/src/jmevr/input/OpenVR.java
def init(applicationType):
    """
    Finds the active installation of the VR API and initializes it. The provided path must be absolute
    or relative to the current working directory. These are the local install versions of the equivalent
    functions in steamvr.h and will work without a local Steam install.
    
    This path is to the "root" of the VR API install. That's the directory with
    the "drivers" directory and a platform (i.e. "win32") directory in it, not the directory with the DLL itself.
    """
    initInternal(applicationType)
    # Retrieve "System" API
    return IVRSystem()


def shutdown():
    """
    unloads vrclient.dll. Any interface pointers from the interface are
    invalid after this point
    """
    shutdownInternal() # OK, this is just like inline definition in openvr.h


_openvr.VR_IsHmdPresent.restype = openvr_bool
_openvr.VR_IsHmdPresent.argtypes = []
def isHmdPresent():
    """
    Returns true if there is an HMD attached. This check is as lightweight as possible and
    can be called outside of VR_Init/VR_Shutdown. It should be used when an application wants
    to know if initializing VR is a possibility but isn't ready to take that step yet.
    """
    result = _openvr.VR_IsHmdPresent()
    return result


_openvr.VR_IsRuntimeInstalled.restype = openvr_bool
_openvr.VR_IsRuntimeInstalled.argtypes = []
def isRuntimeInstalled():
    """
    Returns true if the OpenVR runtime is installed.
    """
    result = _openvr.VR_IsRuntimeInstalled()
    return result


_openvr.VR_RuntimePath.restype = c_char_p
_openvr.VR_RuntimePath.argtypes = []
def runtimePath():
    """
    Returns where the OpenVR runtime is installed.
    """
    result = _openvr.VR_RuntimePath()
    return result


_openvr.VR_GetVRInitErrorAsSymbol.restype = c_char_p
_openvr.VR_GetVRInitErrorAsSymbol.argtypes = [EVRInitError]
def getVRInitErrorAsSymbol(error):
    """
    Returns the name of the enum value for an EVRInitError. This function may be called outside of VR_Init()/VR_Shutdown().
    """
    result = _openvr.VR_GetVRInitErrorAsSymbol(error)
    return result


_openvr.VR_GetVRInitErrorAsEnglishDescription.restype = c_char_p
_openvr.VR_GetVRInitErrorAsEnglishDescription.argtypes = [EVRInitError]
def getVRInitErrorAsEnglishDescription(error):
    """
    Returns an english string for an EVRInitError. Applications should call VR_GetVRInitErrorAsSymbol instead and
    use that as a key to look up their own localized error message. This function may be called outside of VR_Init()/VR_Shutdown().
    """
    result = _openvr.VR_GetVRInitErrorAsEnglishDescription(error)
    return result


_openvr.VR_GetGenericInterface.restype = c_void_p
_openvr.VR_GetGenericInterface.argtypes = [c_char_p, POINTER(EVRInitError)]
def getGenericInterface(interfaceVersion):
    """
    Returns the interface of the specified version. This method must be called after VR_Init. The
    pointer returned is valid until VR_Shutdown is called.
    """
    error = EVRInitError()
    result = _openvr.VR_GetGenericInterface(interfaceVersion, byref(error))
    _checkInitError(error)
    return result


_openvr.VR_IsInterfaceVersionValid.restype = openvr_bool
_openvr.VR_IsInterfaceVersionValid.argtypes = [c_char_p]
def isInterfaceVersionValid(interfaceVersion):
    """
    Returns whether the interface of the specified version exists.
    """
    result = _openvr.VR_IsInterfaceVersionValid(interfaceVersion)
    return result


_openvr.VR_GetInitToken.restype = c_uint32
_openvr.VR_GetInitToken.argtypes = []
def getInitToken():
    """
    Returns a token that represents whether the VR interface handles need to be reloaded
    """
    result = _openvr.VR_GetInitToken()
    return result


_openvr.VR_InitInternal.restype = c_uint32
_openvr.VR_InitInternal.argtypes = [POINTER(EVRInitError), EVRApplicationType]
def initInternal(eApplicationType):
    error = EVRInitError()
    result = _openvr.VR_InitInternal(byref(error), eApplicationType)
    _checkInitError(error)
    return result


_openvr.VR_ShutdownInternal.restype = None
_openvr.VR_ShutdownInternal.argtypes = []
def shutdownInternal():
    result = _openvr.VR_ShutdownInternal()


