#!/bin/env python

# Python bindings for OpenVR API version 0.9.20
# from https://github.com/ValveSoftware/openvr
# Created May 7, 2016 Christopher Bruns

import os
import ctypes
from ctypes import *

####################################################################
### Load OpenVR shared library, so we can access it using ctypes ###
####################################################################

# Add current directory to PATH, so we can load the DLL from right here.
os.environ['PATH'] = os.path.dirname(__file__) + ';' + os.environ['PATH']
_openvr_windll = windll.openvr_api
_openvr_cdll = cdll.openvr_api
_openvr = _openvr_cdll


########################
### Expose constants ###
########################

IVRSystem_Version = "IVRSystem_012"


#############################
### Expose enum constants ###
#############################

ENUM_TYPE = c_uint32

EVREye = ENUM_TYPE
EVREye_Eye_Left = ENUM_TYPE(0)
EVREye_Eye_Right = ENUM_TYPE(1)

EGraphicsAPIConvention = ENUM_TYPE
EGraphicsAPIConvention_API_DirectX = ENUM_TYPE(0)
EGraphicsAPIConvention_API_OpenGL = ENUM_TYPE(1)

EColorSpace = ENUM_TYPE
EColorSpace_ColorSpace_Auto = ENUM_TYPE(0)
EColorSpace_ColorSpace_Gamma = ENUM_TYPE(1)
EColorSpace_ColorSpace_Linear = ENUM_TYPE(2)

ETrackingResult = ENUM_TYPE
ETrackingResult_TrackingResult_Uninitialized = ENUM_TYPE(1)
ETrackingResult_TrackingResult_Calibrating_InProgress = ENUM_TYPE(100)
ETrackingResult_TrackingResult_Calibrating_OutOfRange = ENUM_TYPE(101)
ETrackingResult_TrackingResult_Running_OK = ENUM_TYPE(200)
ETrackingResult_TrackingResult_Running_OutOfRange = ENUM_TYPE(201)

ETrackedDeviceClass = ENUM_TYPE
ETrackedDeviceClass_TrackedDeviceClass_Invalid = ENUM_TYPE(0)
ETrackedDeviceClass_TrackedDeviceClass_HMD = ENUM_TYPE(1)
ETrackedDeviceClass_TrackedDeviceClass_Controller = ENUM_TYPE(2)
ETrackedDeviceClass_TrackedDeviceClass_TrackingReference = ENUM_TYPE(4)
ETrackedDeviceClass_TrackedDeviceClass_Other = ENUM_TYPE(1000)

ETrackedControllerRole = ENUM_TYPE
ETrackedControllerRole_TrackedControllerRole_Invalid = ENUM_TYPE(0)
ETrackedControllerRole_TrackedControllerRole_LeftHand = ENUM_TYPE(1)
ETrackedControllerRole_TrackedControllerRole_RightHand = ENUM_TYPE(2)

ETrackingUniverseOrigin = ENUM_TYPE
ETrackingUniverseOrigin_TrackingUniverseSeated = ENUM_TYPE(0)
ETrackingUniverseOrigin_TrackingUniverseStanding = ENUM_TYPE(1)
ETrackingUniverseOrigin_TrackingUniverseRawAndUncalibrated = ENUM_TYPE(2)

ETrackedDeviceProperty = ENUM_TYPE
ETrackedDeviceProperty_Prop_TrackingSystemName_String = ENUM_TYPE(1000)
ETrackedDeviceProperty_Prop_ModelNumber_String = ENUM_TYPE(1001)
ETrackedDeviceProperty_Prop_SerialNumber_String = ENUM_TYPE(1002)
ETrackedDeviceProperty_Prop_RenderModelName_String = ENUM_TYPE(1003)
ETrackedDeviceProperty_Prop_WillDriftInYaw_Bool = ENUM_TYPE(1004)
ETrackedDeviceProperty_Prop_ManufacturerName_String = ENUM_TYPE(1005)
ETrackedDeviceProperty_Prop_TrackingFirmwareVersion_String = ENUM_TYPE(1006)
ETrackedDeviceProperty_Prop_HardwareRevision_String = ENUM_TYPE(1007)
ETrackedDeviceProperty_Prop_AllWirelessDongleDescriptions_String = ENUM_TYPE(1008)
ETrackedDeviceProperty_Prop_ConnectedWirelessDongle_String = ENUM_TYPE(1009)
ETrackedDeviceProperty_Prop_DeviceIsWireless_Bool = ENUM_TYPE(1010)
ETrackedDeviceProperty_Prop_DeviceIsCharging_Bool = ENUM_TYPE(1011)
ETrackedDeviceProperty_Prop_DeviceBatteryPercentage_Float = ENUM_TYPE(1012)
ETrackedDeviceProperty_Prop_StatusDisplayTransform_Matrix34 = ENUM_TYPE(1013)
ETrackedDeviceProperty_Prop_Firmware_UpdateAvailable_Bool = ENUM_TYPE(1014)
ETrackedDeviceProperty_Prop_Firmware_ManualUpdate_Bool = ENUM_TYPE(1015)
ETrackedDeviceProperty_Prop_Firmware_ManualUpdateURL_String = ENUM_TYPE(1016)
ETrackedDeviceProperty_Prop_HardwareRevision_Uint64 = ENUM_TYPE(1017)
ETrackedDeviceProperty_Prop_FirmwareVersion_Uint64 = ENUM_TYPE(1018)
ETrackedDeviceProperty_Prop_FPGAVersion_Uint64 = ENUM_TYPE(1019)
ETrackedDeviceProperty_Prop_VRCVersion_Uint64 = ENUM_TYPE(1020)
ETrackedDeviceProperty_Prop_RadioVersion_Uint64 = ENUM_TYPE(1021)
ETrackedDeviceProperty_Prop_DongleVersion_Uint64 = ENUM_TYPE(1022)
ETrackedDeviceProperty_Prop_BlockServerShutdown_Bool = ENUM_TYPE(1023)
ETrackedDeviceProperty_Prop_CanUnifyCoordinateSystemWithHmd_Bool = ENUM_TYPE(1024)
ETrackedDeviceProperty_Prop_ContainsProximitySensor_Bool = ENUM_TYPE(1025)
ETrackedDeviceProperty_Prop_DeviceProvidesBatteryStatus_Bool = ENUM_TYPE(1026)
ETrackedDeviceProperty_Prop_DeviceCanPowerOff_Bool = ENUM_TYPE(1027)
ETrackedDeviceProperty_Prop_Firmware_ProgrammingTarget_String = ENUM_TYPE(1028)
ETrackedDeviceProperty_Prop_DeviceClass_Int32 = ENUM_TYPE(1029)
ETrackedDeviceProperty_Prop_HasCamera_Bool = ENUM_TYPE(1030)
ETrackedDeviceProperty_Prop_DriverVersion_String = ENUM_TYPE(1031)
ETrackedDeviceProperty_Prop_Firmware_ForceUpdateRequired_Bool = ENUM_TYPE(1032)
ETrackedDeviceProperty_Prop_ReportsTimeSinceVSync_Bool = ENUM_TYPE(2000)
ETrackedDeviceProperty_Prop_SecondsFromVsyncToPhotons_Float = ENUM_TYPE(2001)
ETrackedDeviceProperty_Prop_DisplayFrequency_Float = ENUM_TYPE(2002)
ETrackedDeviceProperty_Prop_UserIpdMeters_Float = ENUM_TYPE(2003)
ETrackedDeviceProperty_Prop_CurrentUniverseId_Uint64 = ENUM_TYPE(2004)
ETrackedDeviceProperty_Prop_PreviousUniverseId_Uint64 = ENUM_TYPE(2005)
ETrackedDeviceProperty_Prop_DisplayFirmwareVersion_Uint64 = ENUM_TYPE(2006)
ETrackedDeviceProperty_Prop_IsOnDesktop_Bool = ENUM_TYPE(2007)
ETrackedDeviceProperty_Prop_DisplayMCType_Int32 = ENUM_TYPE(2008)
ETrackedDeviceProperty_Prop_DisplayMCOffset_Float = ENUM_TYPE(2009)
ETrackedDeviceProperty_Prop_DisplayMCScale_Float = ENUM_TYPE(2010)
ETrackedDeviceProperty_Prop_EdidVendorID_Int32 = ENUM_TYPE(2011)
ETrackedDeviceProperty_Prop_DisplayMCImageLeft_String = ENUM_TYPE(2012)
ETrackedDeviceProperty_Prop_DisplayMCImageRight_String = ENUM_TYPE(2013)
ETrackedDeviceProperty_Prop_DisplayGCBlackClamp_Float = ENUM_TYPE(2014)
ETrackedDeviceProperty_Prop_EdidProductID_Int32 = ENUM_TYPE(2015)
ETrackedDeviceProperty_Prop_CameraToHeadTransform_Matrix34 = ENUM_TYPE(2016)
ETrackedDeviceProperty_Prop_DisplayGCType_Int32 = ENUM_TYPE(2017)
ETrackedDeviceProperty_Prop_DisplayGCOffset_Float = ENUM_TYPE(2018)
ETrackedDeviceProperty_Prop_DisplayGCScale_Float = ENUM_TYPE(2019)
ETrackedDeviceProperty_Prop_DisplayGCPrescale_Float = ENUM_TYPE(2020)
ETrackedDeviceProperty_Prop_DisplayGCImage_String = ENUM_TYPE(2021)
ETrackedDeviceProperty_Prop_LensCenterLeftU_Float = ENUM_TYPE(2022)
ETrackedDeviceProperty_Prop_LensCenterLeftV_Float = ENUM_TYPE(2023)
ETrackedDeviceProperty_Prop_LensCenterRightU_Float = ENUM_TYPE(2024)
ETrackedDeviceProperty_Prop_LensCenterRightV_Float = ENUM_TYPE(2025)
ETrackedDeviceProperty_Prop_UserHeadToEyeDepthMeters_Float = ENUM_TYPE(2026)
ETrackedDeviceProperty_Prop_CameraFirmwareVersion_Uint64 = ENUM_TYPE(2027)
ETrackedDeviceProperty_Prop_CameraFirmwareDescription_String = ENUM_TYPE(2028)
ETrackedDeviceProperty_Prop_DisplayFPGAVersion_Uint64 = ENUM_TYPE(2029)
ETrackedDeviceProperty_Prop_DisplayBootloaderVersion_Uint64 = ENUM_TYPE(2030)
ETrackedDeviceProperty_Prop_DisplayHardwareVersion_Uint64 = ENUM_TYPE(2031)
ETrackedDeviceProperty_Prop_AudioFirmwareVersion_Uint64 = ENUM_TYPE(2032)
ETrackedDeviceProperty_Prop_CameraCompatibilityMode_Int32 = ENUM_TYPE(2033)
ETrackedDeviceProperty_Prop_AttachedDeviceId_String = ENUM_TYPE(3000)
ETrackedDeviceProperty_Prop_SupportedButtons_Uint64 = ENUM_TYPE(3001)
ETrackedDeviceProperty_Prop_Axis0Type_Int32 = ENUM_TYPE(3002)
ETrackedDeviceProperty_Prop_Axis1Type_Int32 = ENUM_TYPE(3003)
ETrackedDeviceProperty_Prop_Axis2Type_Int32 = ENUM_TYPE(3004)
ETrackedDeviceProperty_Prop_Axis3Type_Int32 = ENUM_TYPE(3005)
ETrackedDeviceProperty_Prop_Axis4Type_Int32 = ENUM_TYPE(3006)
ETrackedDeviceProperty_Prop_FieldOfViewLeftDegrees_Float = ENUM_TYPE(4000)
ETrackedDeviceProperty_Prop_FieldOfViewRightDegrees_Float = ENUM_TYPE(4001)
ETrackedDeviceProperty_Prop_FieldOfViewTopDegrees_Float = ENUM_TYPE(4002)
ETrackedDeviceProperty_Prop_FieldOfViewBottomDegrees_Float = ENUM_TYPE(4003)
ETrackedDeviceProperty_Prop_TrackingRangeMinimumMeters_Float = ENUM_TYPE(4004)
ETrackedDeviceProperty_Prop_TrackingRangeMaximumMeters_Float = ENUM_TYPE(4005)
ETrackedDeviceProperty_Prop_ModeLabel_String = ENUM_TYPE(4006)
ETrackedDeviceProperty_Prop_VendorSpecific_Reserved_Start = ENUM_TYPE(10000)
ETrackedDeviceProperty_Prop_VendorSpecific_Reserved_End = ENUM_TYPE(10999)

ETrackedPropertyError = ENUM_TYPE
ETrackedPropertyError_TrackedProp_Success = ENUM_TYPE(0)
ETrackedPropertyError_TrackedProp_WrongDataType = ENUM_TYPE(1)
ETrackedPropertyError_TrackedProp_WrongDeviceClass = ENUM_TYPE(2)
ETrackedPropertyError_TrackedProp_BufferTooSmall = ENUM_TYPE(3)
ETrackedPropertyError_TrackedProp_UnknownProperty = ENUM_TYPE(4)
ETrackedPropertyError_TrackedProp_InvalidDevice = ENUM_TYPE(5)
ETrackedPropertyError_TrackedProp_CouldNotContactServer = ENUM_TYPE(6)
ETrackedPropertyError_TrackedProp_ValueNotProvidedByDevice = ENUM_TYPE(7)
ETrackedPropertyError_TrackedProp_StringExceedsMaximumLength = ENUM_TYPE(8)
ETrackedPropertyError_TrackedProp_NotYetAvailable = ENUM_TYPE(9)

EVRSubmitFlags = ENUM_TYPE
EVRSubmitFlags_Submit_Default = ENUM_TYPE(0)
EVRSubmitFlags_Submit_LensDistortionAlreadyApplied = ENUM_TYPE(1)
EVRSubmitFlags_Submit_GlRenderBuffer = ENUM_TYPE(2)

EVRState = ENUM_TYPE
EVRState_VRState_Undefined = ENUM_TYPE(-1)
EVRState_VRState_Off = ENUM_TYPE(0)
EVRState_VRState_Searching = ENUM_TYPE(1)
EVRState_VRState_Searching_Alert = ENUM_TYPE(2)
EVRState_VRState_Ready = ENUM_TYPE(3)
EVRState_VRState_Ready_Alert = ENUM_TYPE(4)
EVRState_VRState_NotReady = ENUM_TYPE(5)
EVRState_VRState_Standby = ENUM_TYPE(6)

EVREventType = ENUM_TYPE
EVREventType_VREvent_None = ENUM_TYPE(0)
EVREventType_VREvent_TrackedDeviceActivated = ENUM_TYPE(100)
EVREventType_VREvent_TrackedDeviceDeactivated = ENUM_TYPE(101)
EVREventType_VREvent_TrackedDeviceUpdated = ENUM_TYPE(102)
EVREventType_VREvent_TrackedDeviceUserInteractionStarted = ENUM_TYPE(103)
EVREventType_VREvent_TrackedDeviceUserInteractionEnded = ENUM_TYPE(104)
EVREventType_VREvent_IpdChanged = ENUM_TYPE(105)
EVREventType_VREvent_EnterStandbyMode = ENUM_TYPE(106)
EVREventType_VREvent_LeaveStandbyMode = ENUM_TYPE(107)
EVREventType_VREvent_TrackedDeviceRoleChanged = ENUM_TYPE(108)
EVREventType_VREvent_ButtonPress = ENUM_TYPE(200)
EVREventType_VREvent_ButtonUnpress = ENUM_TYPE(201)
EVREventType_VREvent_ButtonTouch = ENUM_TYPE(202)
EVREventType_VREvent_ButtonUntouch = ENUM_TYPE(203)
EVREventType_VREvent_MouseMove = ENUM_TYPE(300)
EVREventType_VREvent_MouseButtonDown = ENUM_TYPE(301)
EVREventType_VREvent_MouseButtonUp = ENUM_TYPE(302)
EVREventType_VREvent_FocusEnter = ENUM_TYPE(303)
EVREventType_VREvent_FocusLeave = ENUM_TYPE(304)
EVREventType_VREvent_Scroll = ENUM_TYPE(305)
EVREventType_VREvent_TouchPadMove = ENUM_TYPE(306)
EVREventType_VREvent_InputFocusCaptured = ENUM_TYPE(400)
EVREventType_VREvent_InputFocusReleased = ENUM_TYPE(401)
EVREventType_VREvent_SceneFocusLost = ENUM_TYPE(402)
EVREventType_VREvent_SceneFocusGained = ENUM_TYPE(403)
EVREventType_VREvent_SceneApplicationChanged = ENUM_TYPE(404)
EVREventType_VREvent_SceneFocusChanged = ENUM_TYPE(405)
EVREventType_VREvent_InputFocusChanged = ENUM_TYPE(406)
EVREventType_VREvent_HideRenderModels = ENUM_TYPE(410)
EVREventType_VREvent_ShowRenderModels = ENUM_TYPE(411)
EVREventType_VREvent_OverlayShown = ENUM_TYPE(500)
EVREventType_VREvent_OverlayHidden = ENUM_TYPE(501)
EVREventType_VREvent_DashboardActivated = ENUM_TYPE(502)
EVREventType_VREvent_DashboardDeactivated = ENUM_TYPE(503)
EVREventType_VREvent_DashboardThumbSelected = ENUM_TYPE(504)
EVREventType_VREvent_DashboardRequested = ENUM_TYPE(505)
EVREventType_VREvent_ResetDashboard = ENUM_TYPE(506)
EVREventType_VREvent_RenderToast = ENUM_TYPE(507)
EVREventType_VREvent_ImageLoaded = ENUM_TYPE(508)
EVREventType_VREvent_ShowKeyboard = ENUM_TYPE(509)
EVREventType_VREvent_HideKeyboard = ENUM_TYPE(510)
EVREventType_VREvent_OverlayGamepadFocusGained = ENUM_TYPE(511)
EVREventType_VREvent_OverlayGamepadFocusLost = ENUM_TYPE(512)
EVREventType_VREvent_OverlaySharedTextureChanged = ENUM_TYPE(513)
EVREventType_VREvent_DashboardGuideButtonDown = ENUM_TYPE(514)
EVREventType_VREvent_DashboardGuideButtonUp = ENUM_TYPE(515)
EVREventType_VREvent_Notification_Shown = ENUM_TYPE(600)
EVREventType_VREvent_Notification_Hidden = ENUM_TYPE(601)
EVREventType_VREvent_Notification_BeginInteraction = ENUM_TYPE(602)
EVREventType_VREvent_Notification_Destroyed = ENUM_TYPE(603)
EVREventType_VREvent_Quit = ENUM_TYPE(700)
EVREventType_VREvent_ProcessQuit = ENUM_TYPE(701)
EVREventType_VREvent_QuitAborted_UserPrompt = ENUM_TYPE(702)
EVREventType_VREvent_QuitAcknowledged = ENUM_TYPE(703)
EVREventType_VREvent_DriverRequestedQuit = ENUM_TYPE(704)
EVREventType_VREvent_ChaperoneDataHasChanged = ENUM_TYPE(800)
EVREventType_VREvent_ChaperoneUniverseHasChanged = ENUM_TYPE(801)
EVREventType_VREvent_ChaperoneTempDataHasChanged = ENUM_TYPE(802)
EVREventType_VREvent_ChaperoneSettingsHaveChanged = ENUM_TYPE(803)
EVREventType_VREvent_SeatedZeroPoseReset = ENUM_TYPE(804)
EVREventType_VREvent_AudioSettingsHaveChanged = ENUM_TYPE(820)
EVREventType_VREvent_BackgroundSettingHasChanged = ENUM_TYPE(850)
EVREventType_VREvent_CameraSettingsHaveChanged = ENUM_TYPE(851)
EVREventType_VREvent_ReprojectionSettingHasChanged = ENUM_TYPE(852)
EVREventType_VREvent_StatusUpdate = ENUM_TYPE(900)
EVREventType_VREvent_MCImageUpdated = ENUM_TYPE(1000)
EVREventType_VREvent_FirmwareUpdateStarted = ENUM_TYPE(1100)
EVREventType_VREvent_FirmwareUpdateFinished = ENUM_TYPE(1101)
EVREventType_VREvent_KeyboardClosed = ENUM_TYPE(1200)
EVREventType_VREvent_KeyboardCharInput = ENUM_TYPE(1201)
EVREventType_VREvent_KeyboardDone = ENUM_TYPE(1202)
EVREventType_VREvent_ApplicationTransitionStarted = ENUM_TYPE(1300)
EVREventType_VREvent_ApplicationTransitionAborted = ENUM_TYPE(1301)
EVREventType_VREvent_ApplicationTransitionNewAppStarted = ENUM_TYPE(1302)
EVREventType_VREvent_Compositor_MirrorWindowShown = ENUM_TYPE(1400)
EVREventType_VREvent_Compositor_MirrorWindowHidden = ENUM_TYPE(1401)
EVREventType_VREvent_Compositor_ChaperoneBoundsShown = ENUM_TYPE(1410)
EVREventType_VREvent_Compositor_ChaperoneBoundsHidden = ENUM_TYPE(1411)
EVREventType_VREvent_TrackedCamera_StartVideoStream = ENUM_TYPE(1500)
EVREventType_VREvent_TrackedCamera_StopVideoStream = ENUM_TYPE(1501)
EVREventType_VREvent_TrackedCamera_PauseVideoStream = ENUM_TYPE(1502)
EVREventType_VREvent_TrackedCamera_ResumeVideoStream = ENUM_TYPE(1503)
EVREventType_VREvent_PerformanceTest_EnableCapture = ENUM_TYPE(1600)
EVREventType_VREvent_PerformanceTest_DisableCapture = ENUM_TYPE(1601)
EVREventType_VREvent_PerformanceTest_FidelityLevel = ENUM_TYPE(1602)
EVREventType_VREvent_VendorSpecific_Reserved_Start = ENUM_TYPE(10000)
EVREventType_VREvent_VendorSpecific_Reserved_End = ENUM_TYPE(19999)

EDeviceActivityLevel = ENUM_TYPE
EDeviceActivityLevel_k_EDeviceActivityLevel_Unknown = ENUM_TYPE(-1)
EDeviceActivityLevel_k_EDeviceActivityLevel_Idle = ENUM_TYPE(0)
EDeviceActivityLevel_k_EDeviceActivityLevel_UserInteraction = ENUM_TYPE(1)
EDeviceActivityLevel_k_EDeviceActivityLevel_UserInteraction_Timeout = ENUM_TYPE(2)
EDeviceActivityLevel_k_EDeviceActivityLevel_Standby = ENUM_TYPE(3)

EVRButtonId = ENUM_TYPE
EVRButtonId_k_EButton_System = ENUM_TYPE(0)
EVRButtonId_k_EButton_ApplicationMenu = ENUM_TYPE(1)
EVRButtonId_k_EButton_Grip = ENUM_TYPE(2)
EVRButtonId_k_EButton_DPad_Left = ENUM_TYPE(3)
EVRButtonId_k_EButton_DPad_Up = ENUM_TYPE(4)
EVRButtonId_k_EButton_DPad_Right = ENUM_TYPE(5)
EVRButtonId_k_EButton_DPad_Down = ENUM_TYPE(6)
EVRButtonId_k_EButton_A = ENUM_TYPE(7)
EVRButtonId_k_EButton_Axis0 = ENUM_TYPE(32)
EVRButtonId_k_EButton_Axis1 = ENUM_TYPE(33)
EVRButtonId_k_EButton_Axis2 = ENUM_TYPE(34)
EVRButtonId_k_EButton_Axis3 = ENUM_TYPE(35)
EVRButtonId_k_EButton_Axis4 = ENUM_TYPE(36)
EVRButtonId_k_EButton_SteamVR_Touchpad = ENUM_TYPE(32)
EVRButtonId_k_EButton_SteamVR_Trigger = ENUM_TYPE(33)
EVRButtonId_k_EButton_Dashboard_Back = ENUM_TYPE(2)
EVRButtonId_k_EButton_Max = ENUM_TYPE(64)

EVRMouseButton = ENUM_TYPE
EVRMouseButton_VRMouseButton_Left = ENUM_TYPE(1)
EVRMouseButton_VRMouseButton_Right = ENUM_TYPE(2)
EVRMouseButton_VRMouseButton_Middle = ENUM_TYPE(4)

EVRControllerAxisType = ENUM_TYPE
EVRControllerAxisType_k_eControllerAxis_None = ENUM_TYPE(0)
EVRControllerAxisType_k_eControllerAxis_TrackPad = ENUM_TYPE(1)
EVRControllerAxisType_k_eControllerAxis_Joystick = ENUM_TYPE(2)
EVRControllerAxisType_k_eControllerAxis_Trigger = ENUM_TYPE(3)

EVRControllerEventOutputType = ENUM_TYPE
EVRControllerEventOutputType_ControllerEventOutput_OSEvents = ENUM_TYPE(0)
EVRControllerEventOutputType_ControllerEventOutput_VREvents = ENUM_TYPE(1)

ECollisionBoundsStyle = ENUM_TYPE
ECollisionBoundsStyle_COLLISION_BOUNDS_STYLE_BEGINNER = ENUM_TYPE(0)
ECollisionBoundsStyle_COLLISION_BOUNDS_STYLE_INTERMEDIATE = ENUM_TYPE(1)
ECollisionBoundsStyle_COLLISION_BOUNDS_STYLE_SQUARES = ENUM_TYPE(2)
ECollisionBoundsStyle_COLLISION_BOUNDS_STYLE_ADVANCED = ENUM_TYPE(3)
ECollisionBoundsStyle_COLLISION_BOUNDS_STYLE_NONE = ENUM_TYPE(4)
ECollisionBoundsStyle_COLLISION_BOUNDS_STYLE_COUNT = ENUM_TYPE(5)

EVROverlayError = ENUM_TYPE
EVROverlayError_VROverlayError_None = ENUM_TYPE(0)
EVROverlayError_VROverlayError_UnknownOverlay = ENUM_TYPE(10)
EVROverlayError_VROverlayError_InvalidHandle = ENUM_TYPE(11)
EVROverlayError_VROverlayError_PermissionDenied = ENUM_TYPE(12)
EVROverlayError_VROverlayError_OverlayLimitExceeded = ENUM_TYPE(13)
EVROverlayError_VROverlayError_WrongVisibilityType = ENUM_TYPE(14)
EVROverlayError_VROverlayError_KeyTooLong = ENUM_TYPE(15)
EVROverlayError_VROverlayError_NameTooLong = ENUM_TYPE(16)
EVROverlayError_VROverlayError_KeyInUse = ENUM_TYPE(17)
EVROverlayError_VROverlayError_WrongTransformType = ENUM_TYPE(18)
EVROverlayError_VROverlayError_InvalidTrackedDevice = ENUM_TYPE(19)
EVROverlayError_VROverlayError_InvalidParameter = ENUM_TYPE(20)
EVROverlayError_VROverlayError_ThumbnailCantBeDestroyed = ENUM_TYPE(21)
EVROverlayError_VROverlayError_ArrayTooSmall = ENUM_TYPE(22)
EVROverlayError_VROverlayError_RequestFailed = ENUM_TYPE(23)
EVROverlayError_VROverlayError_InvalidTexture = ENUM_TYPE(24)
EVROverlayError_VROverlayError_UnableToLoadFile = ENUM_TYPE(25)
EVROverlayError_VROVerlayError_KeyboardAlreadyInUse = ENUM_TYPE(26)
EVROverlayError_VROverlayError_NoNeighbor = ENUM_TYPE(27)

EVRApplicationType = ENUM_TYPE
EVRApplicationType_VRApplication_Other = ENUM_TYPE(0)
EVRApplicationType_VRApplication_Scene = ENUM_TYPE(1)
EVRApplicationType_VRApplication_Overlay = ENUM_TYPE(2)
EVRApplicationType_VRApplication_Background = ENUM_TYPE(3)
EVRApplicationType_VRApplication_Utility = ENUM_TYPE(4)
EVRApplicationType_VRApplication_VRMonitor = ENUM_TYPE(5)

EVRFirmwareError = ENUM_TYPE
EVRFirmwareError_VRFirmwareError_None = ENUM_TYPE(0)
EVRFirmwareError_VRFirmwareError_Success = ENUM_TYPE(1)
EVRFirmwareError_VRFirmwareError_Fail = ENUM_TYPE(2)

EVRNotificationError = ENUM_TYPE
EVRNotificationError_VRNotificationError_OK = ENUM_TYPE(0)
EVRNotificationError_VRNotificationError_InvalidNotificationId = ENUM_TYPE(100)
EVRNotificationError_VRNotificationError_NotificationQueueFull = ENUM_TYPE(101)
EVRNotificationError_VRNotificationError_InvalidOverlayHandle = ENUM_TYPE(102)

EVRInitError = ENUM_TYPE
EVRInitError_VRInitError_None = ENUM_TYPE(0)
EVRInitError_VRInitError_Unknown = ENUM_TYPE(1)
EVRInitError_VRInitError_Init_InstallationNotFound = ENUM_TYPE(100)
EVRInitError_VRInitError_Init_InstallationCorrupt = ENUM_TYPE(101)
EVRInitError_VRInitError_Init_VRClientDLLNotFound = ENUM_TYPE(102)
EVRInitError_VRInitError_Init_FileNotFound = ENUM_TYPE(103)
EVRInitError_VRInitError_Init_FactoryNotFound = ENUM_TYPE(104)
EVRInitError_VRInitError_Init_InterfaceNotFound = ENUM_TYPE(105)
EVRInitError_VRInitError_Init_InvalidInterface = ENUM_TYPE(106)
EVRInitError_VRInitError_Init_UserConfigDirectoryInvalid = ENUM_TYPE(107)
EVRInitError_VRInitError_Init_HmdNotFound = ENUM_TYPE(108)
EVRInitError_VRInitError_Init_NotInitialized = ENUM_TYPE(109)
EVRInitError_VRInitError_Init_PathRegistryNotFound = ENUM_TYPE(110)
EVRInitError_VRInitError_Init_NoConfigPath = ENUM_TYPE(111)
EVRInitError_VRInitError_Init_NoLogPath = ENUM_TYPE(112)
EVRInitError_VRInitError_Init_PathRegistryNotWritable = ENUM_TYPE(113)
EVRInitError_VRInitError_Init_AppInfoInitFailed = ENUM_TYPE(114)
EVRInitError_VRInitError_Init_Retry = ENUM_TYPE(115)
EVRInitError_VRInitError_Init_InitCanceledByUser = ENUM_TYPE(116)
EVRInitError_VRInitError_Init_AnotherAppLaunching = ENUM_TYPE(117)
EVRInitError_VRInitError_Init_SettingsInitFailed = ENUM_TYPE(118)
EVRInitError_VRInitError_Init_ShuttingDown = ENUM_TYPE(119)
EVRInitError_VRInitError_Init_TooManyObjects = ENUM_TYPE(120)
EVRInitError_VRInitError_Init_NoServerForBackgroundApp = ENUM_TYPE(121)
EVRInitError_VRInitError_Init_NotSupportedWithCompositor = ENUM_TYPE(122)
EVRInitError_VRInitError_Init_NotAvailableToUtilityApps = ENUM_TYPE(123)
EVRInitError_VRInitError_Init_Internal = ENUM_TYPE(124)
EVRInitError_VRInitError_Driver_Failed = ENUM_TYPE(200)
EVRInitError_VRInitError_Driver_Unknown = ENUM_TYPE(201)
EVRInitError_VRInitError_Driver_HmdUnknown = ENUM_TYPE(202)
EVRInitError_VRInitError_Driver_NotLoaded = ENUM_TYPE(203)
EVRInitError_VRInitError_Driver_RuntimeOutOfDate = ENUM_TYPE(204)
EVRInitError_VRInitError_Driver_HmdInUse = ENUM_TYPE(205)
EVRInitError_VRInitError_Driver_NotCalibrated = ENUM_TYPE(206)
EVRInitError_VRInitError_Driver_CalibrationInvalid = ENUM_TYPE(207)
EVRInitError_VRInitError_Driver_HmdDisplayNotFound = ENUM_TYPE(208)
EVRInitError_VRInitError_IPC_ServerInitFailed = ENUM_TYPE(300)
EVRInitError_VRInitError_IPC_ConnectFailed = ENUM_TYPE(301)
EVRInitError_VRInitError_IPC_SharedStateInitFailed = ENUM_TYPE(302)
EVRInitError_VRInitError_IPC_CompositorInitFailed = ENUM_TYPE(303)
EVRInitError_VRInitError_IPC_MutexInitFailed = ENUM_TYPE(304)
EVRInitError_VRInitError_IPC_Failed = ENUM_TYPE(305)
EVRInitError_VRInitError_Compositor_Failed = ENUM_TYPE(400)
EVRInitError_VRInitError_Compositor_D3D11HardwareRequired = ENUM_TYPE(401)
EVRInitError_VRInitError_Compositor_FirmwareRequiresUpdate = ENUM_TYPE(402)
EVRInitError_VRInitError_VendorSpecific_UnableToConnectToOculusRuntime = ENUM_TYPE(1000)
EVRInitError_VRInitError_VendorSpecific_HmdFound_CantOpenDevice = ENUM_TYPE(1101)
EVRInitError_VRInitError_VendorSpecific_HmdFound_UnableToRequestConfigStart = ENUM_TYPE(1102)
EVRInitError_VRInitError_VendorSpecific_HmdFound_NoStoredConfig = ENUM_TYPE(1103)
EVRInitError_VRInitError_VendorSpecific_HmdFound_ConfigTooBig = ENUM_TYPE(1104)
EVRInitError_VRInitError_VendorSpecific_HmdFound_ConfigTooSmall = ENUM_TYPE(1105)
EVRInitError_VRInitError_VendorSpecific_HmdFound_UnableToInitZLib = ENUM_TYPE(1106)
EVRInitError_VRInitError_VendorSpecific_HmdFound_CantReadFirmwareVersion = ENUM_TYPE(1107)
EVRInitError_VRInitError_VendorSpecific_HmdFound_UnableToSendUserDataStart = ENUM_TYPE(1108)
EVRInitError_VRInitError_VendorSpecific_HmdFound_UnableToGetUserDataStart = ENUM_TYPE(1109)
EVRInitError_VRInitError_VendorSpecific_HmdFound_UnableToGetUserDataNext = ENUM_TYPE(1110)
EVRInitError_VRInitError_VendorSpecific_HmdFound_UserDataAddressRange = ENUM_TYPE(1111)
EVRInitError_VRInitError_VendorSpecific_HmdFound_UserDataError = ENUM_TYPE(1112)
EVRInitError_VRInitError_VendorSpecific_HmdFound_ConfigFailedSanityCheck = ENUM_TYPE(1113)
EVRInitError_VRInitError_Steam_SteamInstallationNotFound = ENUM_TYPE(2000)

EVRApplicationError = ENUM_TYPE
EVRApplicationError_VRApplicationError_None = ENUM_TYPE(0)
EVRApplicationError_VRApplicationError_AppKeyAlreadyExists = ENUM_TYPE(100)
EVRApplicationError_VRApplicationError_NoManifest = ENUM_TYPE(101)
EVRApplicationError_VRApplicationError_NoApplication = ENUM_TYPE(102)
EVRApplicationError_VRApplicationError_InvalidIndex = ENUM_TYPE(103)
EVRApplicationError_VRApplicationError_UnknownApplication = ENUM_TYPE(104)
EVRApplicationError_VRApplicationError_IPCFailed = ENUM_TYPE(105)
EVRApplicationError_VRApplicationError_ApplicationAlreadyRunning = ENUM_TYPE(106)
EVRApplicationError_VRApplicationError_InvalidManifest = ENUM_TYPE(107)
EVRApplicationError_VRApplicationError_InvalidApplication = ENUM_TYPE(108)
EVRApplicationError_VRApplicationError_LaunchFailed = ENUM_TYPE(109)
EVRApplicationError_VRApplicationError_ApplicationAlreadyStarting = ENUM_TYPE(110)
EVRApplicationError_VRApplicationError_LaunchInProgress = ENUM_TYPE(111)
EVRApplicationError_VRApplicationError_OldApplicationQuitting = ENUM_TYPE(112)
EVRApplicationError_VRApplicationError_TransitionAborted = ENUM_TYPE(113)
EVRApplicationError_VRApplicationError_IsTemplate = ENUM_TYPE(114)
EVRApplicationError_VRApplicationError_BufferTooSmall = ENUM_TYPE(200)
EVRApplicationError_VRApplicationError_PropertyNotSet = ENUM_TYPE(201)
EVRApplicationError_VRApplicationError_UnknownProperty = ENUM_TYPE(202)
EVRApplicationError_VRApplicationError_InvalidParameter = ENUM_TYPE(203)

EVRApplicationProperty = ENUM_TYPE
EVRApplicationProperty_VRApplicationProperty_Name_String = ENUM_TYPE(0)
EVRApplicationProperty_VRApplicationProperty_LaunchType_String = ENUM_TYPE(11)
EVRApplicationProperty_VRApplicationProperty_WorkingDirectory_String = ENUM_TYPE(12)
EVRApplicationProperty_VRApplicationProperty_BinaryPath_String = ENUM_TYPE(13)
EVRApplicationProperty_VRApplicationProperty_Arguments_String = ENUM_TYPE(14)
EVRApplicationProperty_VRApplicationProperty_URL_String = ENUM_TYPE(15)
EVRApplicationProperty_VRApplicationProperty_Description_String = ENUM_TYPE(50)
EVRApplicationProperty_VRApplicationProperty_NewsURL_String = ENUM_TYPE(51)
EVRApplicationProperty_VRApplicationProperty_ImagePath_String = ENUM_TYPE(52)
EVRApplicationProperty_VRApplicationProperty_Source_String = ENUM_TYPE(53)
EVRApplicationProperty_VRApplicationProperty_IsDashboardOverlay_Bool = ENUM_TYPE(60)
EVRApplicationProperty_VRApplicationProperty_IsTemplate_Bool = ENUM_TYPE(61)
EVRApplicationProperty_VRApplicationProperty_IsInstanced_Bool = ENUM_TYPE(62)
EVRApplicationProperty_VRApplicationProperty_LastLaunchTime_Uint64 = ENUM_TYPE(70)

EVRApplicationTransitionState = ENUM_TYPE
EVRApplicationTransitionState_VRApplicationTransition_None = ENUM_TYPE(0)
EVRApplicationTransitionState_VRApplicationTransition_OldAppQuitSent = ENUM_TYPE(10)
EVRApplicationTransitionState_VRApplicationTransition_WaitingForExternalLaunch = ENUM_TYPE(11)
EVRApplicationTransitionState_VRApplicationTransition_NewAppLaunched = ENUM_TYPE(20)

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
EChaperoneImportFlags_EChaperoneImport_BoundsOnly = ENUM_TYPE(1)

EVRCompositorError = ENUM_TYPE
EVRCompositorError_VRCompositorError_None = ENUM_TYPE(0)
EVRCompositorError_VRCompositorError_IncompatibleVersion = ENUM_TYPE(100)
EVRCompositorError_VRCompositorError_DoNotHaveFocus = ENUM_TYPE(101)
EVRCompositorError_VRCompositorError_InvalidTexture = ENUM_TYPE(102)
EVRCompositorError_VRCompositorError_IsNotSceneApplication = ENUM_TYPE(103)
EVRCompositorError_VRCompositorError_TextureIsOnWrongDevice = ENUM_TYPE(104)
EVRCompositorError_VRCompositorError_TextureUsesUnsupportedFormat = ENUM_TYPE(105)
EVRCompositorError_VRCompositorError_SharedTexturesNotSupported = ENUM_TYPE(106)
EVRCompositorError_VRCompositorError_IndexOutOfRange = ENUM_TYPE(107)

VROverlayInputMethod = ENUM_TYPE
VROverlayInputMethod_None = ENUM_TYPE(0)
VROverlayInputMethod_Mouse = ENUM_TYPE(1)

VROverlayTransformType = ENUM_TYPE
VROverlayTransformType_VROverlayTransform_Absolute = ENUM_TYPE(0)
VROverlayTransformType_VROverlayTransform_TrackedDeviceRelative = ENUM_TYPE(1)
VROverlayTransformType_VROverlayTransform_SystemOverlay = ENUM_TYPE(2)
VROverlayTransformType_VROverlayTransform_TrackedComponent = ENUM_TYPE(3)

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
EGamepadTextInputMode_k_EGamepadTextInputModeNormal = ENUM_TYPE(0)
EGamepadTextInputMode_k_EGamepadTextInputModePassword = ENUM_TYPE(1)
EGamepadTextInputMode_k_EGamepadTextInputModeSubmit = ENUM_TYPE(2)

EGamepadTextInputLineMode = ENUM_TYPE
EGamepadTextInputLineMode_k_EGamepadTextInputLineModeSingleLine = ENUM_TYPE(0)
EGamepadTextInputLineMode_k_EGamepadTextInputLineModeMultipleLines = ENUM_TYPE(1)

EOverlayDirection = ENUM_TYPE
EOverlayDirection_OverlayDirection_Up = ENUM_TYPE(0)
EOverlayDirection_OverlayDirection_Down = ENUM_TYPE(1)
EOverlayDirection_OverlayDirection_Left = ENUM_TYPE(2)
EOverlayDirection_OverlayDirection_Right = ENUM_TYPE(3)
EOverlayDirection_OverlayDirection_Count = ENUM_TYPE(4)

EVRRenderModelError = ENUM_TYPE
EVRRenderModelError_VRRenderModelError_None = ENUM_TYPE(0)
EVRRenderModelError_VRRenderModelError_Loading = ENUM_TYPE(100)
EVRRenderModelError_VRRenderModelError_NotSupported = ENUM_TYPE(200)
EVRRenderModelError_VRRenderModelError_InvalidArg = ENUM_TYPE(300)
EVRRenderModelError_VRRenderModelError_InvalidModel = ENUM_TYPE(301)
EVRRenderModelError_VRRenderModelError_NoShapes = ENUM_TYPE(302)
EVRRenderModelError_VRRenderModelError_MultipleShapes = ENUM_TYPE(303)
EVRRenderModelError_VRRenderModelError_TooManyIndices = ENUM_TYPE(304)
EVRRenderModelError_VRRenderModelError_MultipleTextures = ENUM_TYPE(305)
EVRRenderModelError_VRRenderModelError_InvalidTexture = ENUM_TYPE(400)

EVRComponentProperty = ENUM_TYPE
EVRComponentProperty_VRComponentProperty_IsStatic = ENUM_TYPE(1)
EVRComponentProperty_VRComponentProperty_IsVisible = ENUM_TYPE(2)
EVRComponentProperty_VRComponentProperty_IsTouched = ENUM_TYPE(4)
EVRComponentProperty_VRComponentProperty_IsPressed = ENUM_TYPE(8)
EVRComponentProperty_VRComponentProperty_IsScrolled = ENUM_TYPE(16)

EVRNotificationType = ENUM_TYPE
EVRNotificationType_Transient = ENUM_TYPE(0)
EVRNotificationType_Persistent = ENUM_TYPE(1)

EVRNotificationStyle = ENUM_TYPE
EVRNotificationStyle_None = ENUM_TYPE(0)
EVRNotificationStyle_Application = ENUM_TYPE(100)
EVRNotificationStyle_Contact_Disabled = ENUM_TYPE(200)
EVRNotificationStyle_Contact_Enabled = ENUM_TYPE(201)
EVRNotificationStyle_Contact_Active = ENUM_TYPE(202)

EVRSettingsError = ENUM_TYPE
EVRSettingsError_VRSettingsError_None = ENUM_TYPE(0)
EVRSettingsError_VRSettingsError_IPCFailed = ENUM_TYPE(1)
EVRSettingsError_VRSettingsError_WriteFailed = ENUM_TYPE(2)
EVRSettingsError_VRSettingsError_ReadFailed = ENUM_TYPE(3)


################
### Typedefs ###
################

openvr_bool = c_uint8 # c_char
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

class HmdMatrix34_t(Structure):
    _fields_ = [
        ("m", (c_float * 4) * 3),
    ]


class HmdMatrix44_t(Structure):
    _fields_ = [
        ("m", (c_float * 4) * 4),
    ]


class HmdVector3_t(Structure):
    _fields_ = [
        ("v", c_float * 3),
    ]


class HmdVector4_t(Structure):
    _fields_ = [
        ("v", c_float * 4),
    ]


class HmdVector3d_t(Structure):
    _fields_ = [
        ("v", c_double * 3),
    ]


class HmdVector2_t(Structure):
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
        ("getRecommendedRenderTargetSize", WINFUNCTYPE(None, POINTER(c_uint32), POINTER(c_uint32))),
        ("getProjectionMatrix", WINFUNCTYPE(HmdMatrix44_t, EVREye, c_float, c_float, EGraphicsAPIConvention)),
        ("getProjectionRaw", WINFUNCTYPE(None, EVREye, POINTER(c_float), POINTER(c_float), POINTER(c_float), POINTER(c_float))),
        ("computeDistortion", WINFUNCTYPE(DistortionCoordinates_t, EVREye, c_float, c_float)),
        ("getEyeToHeadTransform", WINFUNCTYPE(HmdMatrix34_t, EVREye)),
        ("getTimeSinceLastVsync", WINFUNCTYPE(openvr_bool, POINTER(c_float), POINTER(c_uint64))),
        ("getD3D9AdapterIndex", WINFUNCTYPE(c_int32)),
        ("getDXGIOutputInfo", WINFUNCTYPE(None, POINTER(c_int32))),
        ("isDisplayOnDesktop", WINFUNCTYPE(openvr_bool)),
        ("setDisplayVisibility", WINFUNCTYPE(openvr_bool, openvr_bool)),
        ("getDeviceToAbsoluteTrackingPose", WINFUNCTYPE(None, ETrackingUniverseOrigin, c_float, POINTER(TrackedDevicePose_t), c_uint32)),
        ("resetSeatedZeroPose", WINFUNCTYPE(None)),
        ("getSeatedZeroPoseToStandingAbsoluteTrackingPose", WINFUNCTYPE(HmdMatrix34_t)),
        ("getRawZeroPoseToStandingAbsoluteTrackingPose", WINFUNCTYPE(HmdMatrix34_t)),
        ("getSortedTrackedDeviceIndicesOfClass", WINFUNCTYPE(c_uint32, ETrackedDeviceClass, POINTER(TrackedDeviceIndex_t), c_uint32, TrackedDeviceIndex_t)),
        ("getTrackedDeviceActivityLevel", WINFUNCTYPE(EDeviceActivityLevel, TrackedDeviceIndex_t)),
        ("applyTransform", WINFUNCTYPE(None, POINTER(TrackedDevicePose_t), POINTER(TrackedDevicePose_t), POINTER(HmdMatrix34_t))),
        ("getTrackedDeviceIndexForControllerRole", WINFUNCTYPE(TrackedDeviceIndex_t, ETrackedControllerRole)),
        ("getControllerRoleForTrackedDeviceIndex", WINFUNCTYPE(ETrackedControllerRole, TrackedDeviceIndex_t)),
        ("getTrackedDeviceClass", WINFUNCTYPE(ETrackedDeviceClass, TrackedDeviceIndex_t)),
        ("isTrackedDeviceConnected", WINFUNCTYPE(openvr_bool, TrackedDeviceIndex_t)),
        ("getBoolTrackedDeviceProperty", WINFUNCTYPE(openvr_bool, TrackedDeviceIndex_t, ETrackedDeviceProperty, POINTER(ETrackedPropertyError))),
        ("getFloatTrackedDeviceProperty", WINFUNCTYPE(c_float, TrackedDeviceIndex_t, ETrackedDeviceProperty, POINTER(ETrackedPropertyError))),
        ("getInt32TrackedDeviceProperty", WINFUNCTYPE(c_int32, TrackedDeviceIndex_t, ETrackedDeviceProperty, POINTER(ETrackedPropertyError))),
        ("getUint64TrackedDeviceProperty", WINFUNCTYPE(c_uint64, TrackedDeviceIndex_t, ETrackedDeviceProperty, POINTER(ETrackedPropertyError))),
        ("getMatrix34TrackedDeviceProperty", WINFUNCTYPE(HmdMatrix34_t, TrackedDeviceIndex_t, ETrackedDeviceProperty, POINTER(ETrackedPropertyError))),
        ("getStringTrackedDeviceProperty", WINFUNCTYPE(c_uint32, TrackedDeviceIndex_t, ETrackedDeviceProperty, c_char_p, c_uint32, POINTER(ETrackedPropertyError))),
        ("getPropErrorNameFromEnum", WINFUNCTYPE(c_char_p, ETrackedPropertyError)),
        ("pollNextEvent", WINFUNCTYPE(openvr_bool, POINTER(VREvent_t), c_uint32)),
        ("pollNextEventWithPose", WINFUNCTYPE(openvr_bool, ETrackingUniverseOrigin, POINTER(VREvent_t), c_uint32, POINTER(TrackedDevicePose_t))),
        ("getEventTypeNameFromEnum", WINFUNCTYPE(c_char_p, EVREventType)),
        ("getHiddenAreaMesh", WINFUNCTYPE(HiddenAreaMesh_t, EVREye)),
        ("getControllerState", WINFUNCTYPE(openvr_bool, TrackedDeviceIndex_t, POINTER(VRControllerState_t))),
        ("getControllerStateWithPose", WINFUNCTYPE(openvr_bool, ETrackingUniverseOrigin, TrackedDeviceIndex_t, POINTER(VRControllerState_t), POINTER(TrackedDevicePose_t))),
        ("triggerHapticPulse", WINFUNCTYPE(None, TrackedDeviceIndex_t, c_uint32, c_ushort)),
        ("getButtonIdNameFromEnum", WINFUNCTYPE(c_char_p, EVRButtonId)),
        ("getControllerAxisTypeNameFromEnum", WINFUNCTYPE(c_char_p, EVRControllerAxisType)),
        ("captureInputFocus", WINFUNCTYPE(openvr_bool)),
        ("releaseInputFocus", WINFUNCTYPE(None)),
        ("isInputFocusCapturedByAnotherProcess", WINFUNCTYPE(openvr_bool)),
        ("driverDebugRequest", WINFUNCTYPE(c_uint32, TrackedDeviceIndex_t, c_char_p, c_char_p, c_uint32)),
        ("performFirmwareUpdate", WINFUNCTYPE(EVRFirmwareError, TrackedDeviceIndex_t)),
        ("acknowledgeQuit_Exiting", WINFUNCTYPE(None)),
        ("acknowledgeQuit_UserPrompt", WINFUNCTYPE(None)),
    ]


class IVRExtendedDisplay_FnTable(Structure):
    _fields_ = [
        ("getWindowBounds", WINFUNCTYPE(None, POINTER(c_int32), POINTER(c_int32), POINTER(c_uint32), POINTER(c_uint32))),
        ("getEyeOutputViewport", WINFUNCTYPE(None, EVREye, POINTER(c_uint32), POINTER(c_uint32), POINTER(c_uint32), POINTER(c_uint32))),
        ("getDXGIOutputInfo", WINFUNCTYPE(None, POINTER(c_int32), POINTER(c_int32))),
    ]


class IVRApplications_FnTable(Structure):
    _fields_ = [
        ("addApplicationManifest", WINFUNCTYPE(EVRApplicationError, c_char_p, openvr_bool)),
        ("removeApplicationManifest", WINFUNCTYPE(EVRApplicationError, c_char_p)),
        ("isApplicationInstalled", WINFUNCTYPE(openvr_bool, c_char_p)),
        ("getApplicationCount", WINFUNCTYPE(c_uint32)),
        ("getApplicationKeyByIndex", WINFUNCTYPE(EVRApplicationError, c_uint32, c_char_p, c_uint32)),
        ("getApplicationKeyByProcessId", WINFUNCTYPE(EVRApplicationError, c_uint32, c_char_p, c_uint32)),
        ("launchApplication", WINFUNCTYPE(EVRApplicationError, c_char_p)),
        ("launchTemplateApplication", WINFUNCTYPE(EVRApplicationError, c_char_p, c_char_p, POINTER(AppOverrideKeys_t), c_uint32)),
        ("launchDashboardOverlay", WINFUNCTYPE(EVRApplicationError, c_char_p)),
        ("cancelApplicationLaunch", WINFUNCTYPE(openvr_bool, c_char_p)),
        ("identifyApplication", WINFUNCTYPE(EVRApplicationError, c_uint32, c_char_p)),
        ("getApplicationProcessId", WINFUNCTYPE(c_uint32, c_char_p)),
        ("getApplicationsErrorNameFromEnum", WINFUNCTYPE(c_char_p, EVRApplicationError)),
        ("getApplicationPropertyString", WINFUNCTYPE(c_uint32, c_char_p, EVRApplicationProperty, c_char_p, c_uint32, POINTER(EVRApplicationError))),
        ("getApplicationPropertyBool", WINFUNCTYPE(openvr_bool, c_char_p, EVRApplicationProperty, POINTER(EVRApplicationError))),
        ("getApplicationPropertyUint64", WINFUNCTYPE(c_uint64, c_char_p, EVRApplicationProperty, POINTER(EVRApplicationError))),
        ("setApplicationAutoLaunch", WINFUNCTYPE(EVRApplicationError, c_char_p, openvr_bool)),
        ("getApplicationAutoLaunch", WINFUNCTYPE(openvr_bool, c_char_p)),
        ("getStartingApplication", WINFUNCTYPE(EVRApplicationError, c_char_p, c_uint32)),
        ("getTransitionState", WINFUNCTYPE(EVRApplicationTransitionState)),
        ("performApplicationPrelaunchCheck", WINFUNCTYPE(EVRApplicationError, c_char_p)),
        ("getApplicationsTransitionStateNameFromEnum", WINFUNCTYPE(c_char_p, EVRApplicationTransitionState)),
        ("isQuitUserPromptRequested", WINFUNCTYPE(openvr_bool)),
        ("launchInternalProcess", WINFUNCTYPE(EVRApplicationError, c_char_p, c_char_p, c_char_p)),
    ]


class IVRChaperone_FnTable(Structure):
    _fields_ = [
        ("getCalibrationState", WINFUNCTYPE(ChaperoneCalibrationState)),
        ("getPlayAreaSize", WINFUNCTYPE(openvr_bool, POINTER(c_float), POINTER(c_float))),
        ("getPlayAreaRect", WINFUNCTYPE(openvr_bool, POINTER(HmdQuad_t))),
        ("reloadInfo", WINFUNCTYPE(None)),
        ("setSceneColor", WINFUNCTYPE(None, HmdColor_t)),
        ("getBoundsColor", WINFUNCTYPE(None, POINTER(HmdColor_t), c_int, c_float, POINTER(HmdColor_t))),
        ("areBoundsVisible", WINFUNCTYPE(openvr_bool)),
        ("forceBoundsVisible", WINFUNCTYPE(None, openvr_bool)),
    ]


class IVRChaperoneSetup_FnTable(Structure):
    _fields_ = [
        ("commitWorkingCopy", WINFUNCTYPE(openvr_bool, EChaperoneConfigFile)),
        ("revertWorkingCopy", WINFUNCTYPE(None)),
        ("getWorkingPlayAreaSize", WINFUNCTYPE(openvr_bool, POINTER(c_float), POINTER(c_float))),
        ("getWorkingPlayAreaRect", WINFUNCTYPE(openvr_bool, POINTER(HmdQuad_t))),
        ("getWorkingCollisionBoundsInfo", WINFUNCTYPE(openvr_bool, POINTER(HmdQuad_t), POINTER(c_uint32))),
        ("getLiveCollisionBoundsInfo", WINFUNCTYPE(openvr_bool, POINTER(HmdQuad_t), POINTER(c_uint32))),
        ("getWorkingSeatedZeroPoseToRawTrackingPose", WINFUNCTYPE(openvr_bool, POINTER(HmdMatrix34_t))),
        ("getWorkingStandingZeroPoseToRawTrackingPose", WINFUNCTYPE(openvr_bool, POINTER(HmdMatrix34_t))),
        ("setWorkingPlayAreaSize", WINFUNCTYPE(None, c_float, c_float)),
        ("setWorkingCollisionBoundsInfo", WINFUNCTYPE(None, POINTER(HmdQuad_t), c_uint32)),
        ("setWorkingSeatedZeroPoseToRawTrackingPose", WINFUNCTYPE(None, POINTER(HmdMatrix34_t))),
        ("setWorkingStandingZeroPoseToRawTrackingPose", WINFUNCTYPE(None, POINTER(HmdMatrix34_t))),
        ("reloadFromDisk", WINFUNCTYPE(None, EChaperoneConfigFile)),
        ("getLiveSeatedZeroPoseToRawTrackingPose", WINFUNCTYPE(openvr_bool, POINTER(HmdMatrix34_t))),
        ("setWorkingCollisionBoundsTagsInfo", WINFUNCTYPE(None, POINTER(c_uint8), c_uint32)),
        ("getLiveCollisionBoundsTagsInfo", WINFUNCTYPE(openvr_bool, POINTER(c_uint8), POINTER(c_uint32))),
        ("setWorkingPhysicalBoundsInfo", WINFUNCTYPE(openvr_bool, POINTER(HmdQuad_t), c_uint32)),
        ("getLivePhysicalBoundsInfo", WINFUNCTYPE(openvr_bool, POINTER(HmdQuad_t), POINTER(c_uint32))),
        ("exportLiveToBuffer", WINFUNCTYPE(openvr_bool, c_char_p, POINTER(c_uint32))),
        ("importFromBufferToWorking", WINFUNCTYPE(openvr_bool, c_char_p, c_uint32)),
    ]


class IVRCompositor_FnTable(Structure):
    _fields_ = [
        ("setTrackingSpace", WINFUNCTYPE(None, ETrackingUniverseOrigin)),
        ("getTrackingSpace", WINFUNCTYPE(ETrackingUniverseOrigin)),
        ("waitGetPoses", WINFUNCTYPE(EVRCompositorError, POINTER(TrackedDevicePose_t), c_uint32, POINTER(TrackedDevicePose_t), c_uint32)),
        ("getLastPoses", WINFUNCTYPE(EVRCompositorError, POINTER(TrackedDevicePose_t), c_uint32, POINTER(TrackedDevicePose_t), c_uint32)),
        ("getLastPoseForTrackedDeviceIndex", WINFUNCTYPE(EVRCompositorError, TrackedDeviceIndex_t, POINTER(TrackedDevicePose_t), POINTER(TrackedDevicePose_t))),
        ("submit", WINFUNCTYPE(EVRCompositorError, EVREye, POINTER(Texture_t), POINTER(VRTextureBounds_t), EVRSubmitFlags)),
        ("clearLastSubmittedFrame", WINFUNCTYPE(None)),
        ("postPresentHandoff", WINFUNCTYPE(None)),
        ("getFrameTiming", WINFUNCTYPE(openvr_bool, POINTER(Compositor_FrameTiming), c_uint32)),
        ("getFrameTimeRemaining", WINFUNCTYPE(c_float)),
        ("fadeToColor", WINFUNCTYPE(None, c_float, c_float, c_float, c_float, c_float, openvr_bool)),
        ("fadeGrid", WINFUNCTYPE(None, c_float, openvr_bool)),
        ("setSkyboxOverride", WINFUNCTYPE(EVRCompositorError, POINTER(Texture_t), c_uint32)),
        ("clearSkyboxOverride", WINFUNCTYPE(None)),
        ("compositorBringToFront", WINFUNCTYPE(None)),
        ("compositorGoToBack", WINFUNCTYPE(None)),
        ("compositorQuit", WINFUNCTYPE(None)),
        ("isFullscreen", WINFUNCTYPE(openvr_bool)),
        ("getCurrentSceneFocusProcess", WINFUNCTYPE(c_uint32)),
        ("getLastFrameRenderer", WINFUNCTYPE(c_uint32)),
        ("canRenderScene", WINFUNCTYPE(openvr_bool)),
        ("showMirrorWindow", WINFUNCTYPE(None)),
        ("hideMirrorWindow", WINFUNCTYPE(None)),
        ("isMirrorWindowVisible", WINFUNCTYPE(openvr_bool)),
        ("compositorDumpImages", WINFUNCTYPE(None)),
        ("shouldAppRenderWithLowResources", WINFUNCTYPE(openvr_bool)),
        ("forceInterleavedReprojectionOn", WINFUNCTYPE(None, openvr_bool)),
        ("forceReconnectProcess", WINFUNCTYPE(None)),
        ("suspendRendering", WINFUNCTYPE(None, openvr_bool)),
    ]


class IVROverlay_FnTable(Structure):
    _fields_ = [
        ("findOverlay", WINFUNCTYPE(EVROverlayError, c_char_p, POINTER(VROverlayHandle_t))),
        ("createOverlay", WINFUNCTYPE(EVROverlayError, c_char_p, c_char_p, POINTER(VROverlayHandle_t))),
        ("destroyOverlay", WINFUNCTYPE(EVROverlayError, VROverlayHandle_t)),
        ("setHighQualityOverlay", WINFUNCTYPE(EVROverlayError, VROverlayHandle_t)),
        ("getHighQualityOverlay", WINFUNCTYPE(VROverlayHandle_t)),
        ("getOverlayKey", WINFUNCTYPE(c_uint32, VROverlayHandle_t, c_char_p, c_uint32, POINTER(EVROverlayError))),
        ("getOverlayName", WINFUNCTYPE(c_uint32, VROverlayHandle_t, c_char_p, c_uint32, POINTER(EVROverlayError))),
        ("getOverlayImageData", WINFUNCTYPE(EVROverlayError, VROverlayHandle_t, c_void_p, c_uint32, POINTER(c_uint32), POINTER(c_uint32))),
        ("getOverlayErrorNameFromEnum", WINFUNCTYPE(c_char_p, EVROverlayError)),
        ("setOverlayRenderingPid", WINFUNCTYPE(EVROverlayError, VROverlayHandle_t, c_uint32)),
        ("getOverlayRenderingPid", WINFUNCTYPE(c_uint32, VROverlayHandle_t)),
        ("setOverlayFlag", WINFUNCTYPE(EVROverlayError, VROverlayHandle_t, VROverlayFlags, openvr_bool)),
        ("getOverlayFlag", WINFUNCTYPE(EVROverlayError, VROverlayHandle_t, VROverlayFlags, POINTER(openvr_bool))),
        ("setOverlayColor", WINFUNCTYPE(EVROverlayError, VROverlayHandle_t, c_float, c_float, c_float)),
        ("getOverlayColor", WINFUNCTYPE(EVROverlayError, VROverlayHandle_t, POINTER(c_float), POINTER(c_float), POINTER(c_float))),
        ("setOverlayAlpha", WINFUNCTYPE(EVROverlayError, VROverlayHandle_t, c_float)),
        ("getOverlayAlpha", WINFUNCTYPE(EVROverlayError, VROverlayHandle_t, POINTER(c_float))),
        ("setOverlayWidthInMeters", WINFUNCTYPE(EVROverlayError, VROverlayHandle_t, c_float)),
        ("getOverlayWidthInMeters", WINFUNCTYPE(EVROverlayError, VROverlayHandle_t, POINTER(c_float))),
        ("setOverlayAutoCurveDistanceRangeInMeters", WINFUNCTYPE(EVROverlayError, VROverlayHandle_t, c_float, c_float)),
        ("getOverlayAutoCurveDistanceRangeInMeters", WINFUNCTYPE(EVROverlayError, VROverlayHandle_t, POINTER(c_float), POINTER(c_float))),
        ("setOverlayTextureColorSpace", WINFUNCTYPE(EVROverlayError, VROverlayHandle_t, EColorSpace)),
        ("getOverlayTextureColorSpace", WINFUNCTYPE(EVROverlayError, VROverlayHandle_t, POINTER(EColorSpace))),
        ("setOverlayTextureBounds", WINFUNCTYPE(EVROverlayError, VROverlayHandle_t, POINTER(VRTextureBounds_t))),
        ("getOverlayTextureBounds", WINFUNCTYPE(EVROverlayError, VROverlayHandle_t, POINTER(VRTextureBounds_t))),
        ("getOverlayTransformType", WINFUNCTYPE(EVROverlayError, VROverlayHandle_t, POINTER(VROverlayTransformType))),
        ("setOverlayTransformAbsolute", WINFUNCTYPE(EVROverlayError, VROverlayHandle_t, ETrackingUniverseOrigin, POINTER(HmdMatrix34_t))),
        ("getOverlayTransformAbsolute", WINFUNCTYPE(EVROverlayError, VROverlayHandle_t, POINTER(ETrackingUniverseOrigin), POINTER(HmdMatrix34_t))),
        ("setOverlayTransformTrackedDeviceRelative", WINFUNCTYPE(EVROverlayError, VROverlayHandle_t, TrackedDeviceIndex_t, POINTER(HmdMatrix34_t))),
        ("getOverlayTransformTrackedDeviceRelative", WINFUNCTYPE(EVROverlayError, VROverlayHandle_t, POINTER(TrackedDeviceIndex_t), POINTER(HmdMatrix34_t))),
        ("setOverlayTransformTrackedDeviceComponent", WINFUNCTYPE(EVROverlayError, VROverlayHandle_t, TrackedDeviceIndex_t, c_char_p)),
        ("getOverlayTransformTrackedDeviceComponent", WINFUNCTYPE(EVROverlayError, VROverlayHandle_t, POINTER(TrackedDeviceIndex_t), c_char_p, c_uint32)),
        ("showOverlay", WINFUNCTYPE(EVROverlayError, VROverlayHandle_t)),
        ("hideOverlay", WINFUNCTYPE(EVROverlayError, VROverlayHandle_t)),
        ("isOverlayVisible", WINFUNCTYPE(openvr_bool, VROverlayHandle_t)),
        ("getTransformForOverlayCoordinates", WINFUNCTYPE(EVROverlayError, VROverlayHandle_t, ETrackingUniverseOrigin, HmdVector2_t, POINTER(HmdMatrix34_t))),
        ("pollNextOverlayEvent", WINFUNCTYPE(openvr_bool, VROverlayHandle_t, POINTER(VREvent_t), c_uint32)),
        ("getOverlayInputMethod", WINFUNCTYPE(EVROverlayError, VROverlayHandle_t, POINTER(VROverlayInputMethod))),
        ("setOverlayInputMethod", WINFUNCTYPE(EVROverlayError, VROverlayHandle_t, VROverlayInputMethod)),
        ("getOverlayMouseScale", WINFUNCTYPE(EVROverlayError, VROverlayHandle_t, POINTER(HmdVector2_t))),
        ("setOverlayMouseScale", WINFUNCTYPE(EVROverlayError, VROverlayHandle_t, POINTER(HmdVector2_t))),
        ("computeOverlayIntersection", WINFUNCTYPE(openvr_bool, VROverlayHandle_t, POINTER(VROverlayIntersectionParams_t), POINTER(VROverlayIntersectionResults_t))),
        ("handleControllerOverlayInteractionAsMouse", WINFUNCTYPE(openvr_bool, VROverlayHandle_t, TrackedDeviceIndex_t)),
        ("isHoverTargetOverlay", WINFUNCTYPE(openvr_bool, VROverlayHandle_t)),
        ("getGamepadFocusOverlay", WINFUNCTYPE(VROverlayHandle_t)),
        ("setGamepadFocusOverlay", WINFUNCTYPE(EVROverlayError, VROverlayHandle_t)),
        ("setOverlayNeighbor", WINFUNCTYPE(EVROverlayError, EOverlayDirection, VROverlayHandle_t, VROverlayHandle_t)),
        ("moveGamepadFocusToNeighbor", WINFUNCTYPE(EVROverlayError, EOverlayDirection, VROverlayHandle_t)),
        ("setOverlayTexture", WINFUNCTYPE(EVROverlayError, VROverlayHandle_t, POINTER(Texture_t))),
        ("clearOverlayTexture", WINFUNCTYPE(EVROverlayError, VROverlayHandle_t)),
        ("setOverlayRaw", WINFUNCTYPE(EVROverlayError, VROverlayHandle_t, c_void_p, c_uint32, c_uint32, c_uint32)),
        ("setOverlayFromFile", WINFUNCTYPE(EVROverlayError, VROverlayHandle_t, c_char_p)),
        ("getOverlayTexture", WINFUNCTYPE(EVROverlayError, VROverlayHandle_t, POINTER(c_void_p), c_void_p, POINTER(c_uint32), POINTER(c_uint32), POINTER(c_uint32), POINTER(EGraphicsAPIConvention), POINTER(EColorSpace))),
        ("releaseNativeOverlayHandle", WINFUNCTYPE(EVROverlayError, VROverlayHandle_t, c_void_p)),
        ("createDashboardOverlay", WINFUNCTYPE(EVROverlayError, c_char_p, c_char_p, POINTER(VROverlayHandle_t), POINTER(VROverlayHandle_t))),
        ("isDashboardVisible", WINFUNCTYPE(openvr_bool)),
        ("isActiveDashboardOverlay", WINFUNCTYPE(openvr_bool, VROverlayHandle_t)),
        ("setDashboardOverlaySceneProcess", WINFUNCTYPE(EVROverlayError, VROverlayHandle_t, c_uint32)),
        ("getDashboardOverlaySceneProcess", WINFUNCTYPE(EVROverlayError, VROverlayHandle_t, POINTER(c_uint32))),
        ("showDashboard", WINFUNCTYPE(None, c_char_p)),
        ("getPrimaryDashboardDevice", WINFUNCTYPE(TrackedDeviceIndex_t)),
        ("showKeyboard", WINFUNCTYPE(EVROverlayError, EGamepadTextInputMode, EGamepadTextInputLineMode, c_char_p, c_uint32, c_char_p, openvr_bool, c_uint64)),
        ("showKeyboardForOverlay", WINFUNCTYPE(EVROverlayError, VROverlayHandle_t, EGamepadTextInputMode, EGamepadTextInputLineMode, c_char_p, c_uint32, c_char_p, openvr_bool, c_uint64)),
        ("getKeyboardText", WINFUNCTYPE(c_uint32, c_char_p, c_uint32)),
        ("hideKeyboard", WINFUNCTYPE(None)),
        ("setKeyboardTransformAbsolute", WINFUNCTYPE(None, ETrackingUniverseOrigin, POINTER(HmdMatrix34_t))),
        ("setKeyboardPositionForOverlay", WINFUNCTYPE(None, VROverlayHandle_t, HmdRect2_t)),
    ]


class IVRRenderModels_FnTable(Structure):
    _fields_ = [
        ("loadRenderModel_Async", WINFUNCTYPE(EVRRenderModelError, c_char_p, POINTER(POINTER(RenderModel_t)))),
        ("freeRenderModel", WINFUNCTYPE(None, POINTER(RenderModel_t))),
        ("loadTexture_Async", WINFUNCTYPE(EVRRenderModelError, TextureID_t, POINTER(POINTER(RenderModel_TextureMap_t)))),
        ("freeTexture", WINFUNCTYPE(None, POINTER(RenderModel_TextureMap_t))),
        ("loadTextureD3D11_Async", WINFUNCTYPE(EVRRenderModelError, TextureID_t, c_void_p, POINTER(c_void_p))),
        ("loadIntoTextureD3D11_Async", WINFUNCTYPE(EVRRenderModelError, TextureID_t, c_void_p)),
        ("freeTextureD3D11", WINFUNCTYPE(None, c_void_p)),
        ("getRenderModelName", WINFUNCTYPE(c_uint32, c_uint32, c_char_p, c_uint32)),
        ("getRenderModelCount", WINFUNCTYPE(c_uint32)),
        ("getComponentCount", WINFUNCTYPE(c_uint32, c_char_p)),
        ("getComponentName", WINFUNCTYPE(c_uint32, c_char_p, c_uint32, c_char_p, c_uint32)),
        ("getComponentButtonMask", WINFUNCTYPE(c_uint64, c_char_p, c_char_p)),
        ("getComponentRenderModelName", WINFUNCTYPE(c_uint32, c_char_p, c_char_p, c_char_p, c_uint32)),
        ("getComponentState", WINFUNCTYPE(openvr_bool, c_char_p, c_char_p, POINTER(VRControllerState_t), POINTER(RenderModel_ControllerMode_State_t), POINTER(RenderModel_ComponentState_t))),
        ("renderModelHasComponent", WINFUNCTYPE(openvr_bool, c_char_p, c_char_p)),
    ]


class IVRNotifications_FnTable(Structure):
    _fields_ = [
        ("createNotification", WINFUNCTYPE(EVRNotificationError, VROverlayHandle_t, c_uint64, EVRNotificationType, c_char_p, EVRNotificationStyle, POINTER(NotificationBitmap_t), POINTER(VRNotificationId))),
        ("removeNotification", WINFUNCTYPE(EVRNotificationError, VRNotificationId)),
    ]


class IVRSettings_FnTable(Structure):
    _fields_ = [
        ("getSettingsErrorNameFromEnum", WINFUNCTYPE(c_char_p, EVRSettingsError)),
        ("sync", WINFUNCTYPE(openvr_bool, openvr_bool, POINTER(EVRSettingsError))),
        ("getBool", WINFUNCTYPE(openvr_bool, c_char_p, c_char_p, openvr_bool, POINTER(EVRSettingsError))),
        ("setBool", WINFUNCTYPE(None, c_char_p, c_char_p, openvr_bool, POINTER(EVRSettingsError))),
        ("getInt32", WINFUNCTYPE(c_int32, c_char_p, c_char_p, c_int32, POINTER(EVRSettingsError))),
        ("setInt32", WINFUNCTYPE(None, c_char_p, c_char_p, c_int32, POINTER(EVRSettingsError))),
        ("getFloat", WINFUNCTYPE(c_float, c_char_p, c_char_p, c_float, POINTER(EVRSettingsError))),
        ("setFloat", WINFUNCTYPE(None, c_char_p, c_char_p, c_float, POINTER(EVRSettingsError))),
        ("getString", WINFUNCTYPE(None, c_char_p, c_char_p, c_char_p, c_uint32, c_char_p, POINTER(EVRSettingsError))),
        ("setString", WINFUNCTYPE(None, c_char_p, c_char_p, c_char_p, POINTER(EVRSettingsError))),
        ("removeSection", WINFUNCTYPE(None, c_char_p, POINTER(EVRSettingsError))),
        ("removeKeyInSection", WINFUNCTYPE(None, c_char_p, c_char_p, POINTER(EVRSettingsError))),
    ]


########################
### Expose functions ###
########################

def _checkInitError(error):
    if error.value != EVRInitError_VRInitError_None.value:
        shutdown()
        raise OpenVRError(getInitErrorAsSymbol(error) + str(error))    

_openvr.VR_GetGenericInterface.restype = POINTER(IVRSystem_FnTable)
_openvr.VR_GetGenericInterface.argtypes = [c_char_p, POINTER(EVRInitError)]
def getGenericInterface(interfaceVersion):
    error = EVRInitError()
    ptr = _openvr.VR_GetGenericInterface(interfaceVersion, error)
    _checkInitError(error)
    return ptr.contents

_openvr.VR_GetVRInitErrorAsSymbol.restype = c_char_p
_openvr.VR_GetVRInitErrorAsSymbol.argtypes = [EVRInitError]
def getInitErrorAsSymbol(error):
    return _openvr.VR_GetVRInitErrorAsSymbol(error)

_openvr.VR_InitInternal.restype = c_uint32
_openvr.VR_InitInternal.argtypes = [POINTER(EVRInitError), EVRApplicationType]
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
    eError = EVRInitError()
    _vr_token = _openvr.VR_InitInternal(byref(eError), applicationType)
    _checkInitError(eError)
    # Retrieve "System" API
    if not isInterfaceVersionValid(IVRSystem_Version):
        _checkInitError(EVRInitError_VRInitError_Init_InterfaceNotFound)
    systemFunctions = getGenericInterface(IVRSystem_Version)
    if systemFunctions is None:
        raise OpenVRError("Error retrieving VR API")
    return IVRSystem(system_functions=systemFunctions)


_openvr.VR_IsHmdPresent.restype = openvr_bool
_openvr.VR_IsHmdPresent.argtypes = []
def isHmdPresent():
    """
    Returns true if there is an HMD attached. This check is as lightweight as possible and
    can be called outside of VR_Init/VR_Shutdown. It should be used when an application wants
    to know if initializing VR is a possibility but isn't ready to take that step yet.   
    """
    return _openvr.VR_IsHmdPresent()


_openvr.VR_IsInterfaceVersionValid.restype = openvr_bool
_openvr.VR_IsInterfaceVersionValid.argtypes = [c_char_p]
def isInterfaceVersionValid(version):
    return _openvr.VR_IsInterfaceVersionValid(version)


_openvr.VR_IsRuntimeInstalled.restype = openvr_bool
_openvr.VR_IsRuntimeInstalled.argtypes = []
def isRuntimeInstalled():
    """
    Returns true if the OpenVR runtime is installed.
    """
    return _openvr.VR_IsRuntimeInstalled()


_openvr.VR_RuntimePath.restype = c_char_p
_openvr.VR_RuntimePath.argtypes = []
def runtimePath():
    """
    Returns where the OpenVR runtime is installed.
    """
    return _openvr.VR_RuntimePath()


_openvr.VR_ShutdownInternal.restype = None
_openvr.VR_ShutdownInternal.argtypes = []
def shutdown():
    """
    unloads vrclient.dll. Any interface pointers from the interface are
    invalid after this point
    """
    _openvr.VR_ShutdownInternal() # OK, this is just like inline definition in openvr.h


#################################################
### Wrap OpenVR API in Object Oriented python ###
#################################################

class IVRSystem:
    def __init__(self, system_functions):
        self.system_functions = system_functions

    def shutdown(self):
        if self.system_functions is None:
            return
        shutdown()
        self.system_functions = None

    def getEyeToHeadTransform(self, eye):
        fn = self.system_functions.getEyeToHeadTransform
        return fn(eye)

    def getRecommendedRenderTargetSize(self):
        fn = self.system_functions.getRecommendedRenderTargetSize
        w = c_uint32()
        h = c_uint32()
        fn(byref(w), byref(h))
        return w, h

    def isDisplayOnDesktop(self):
        fn = self.system_functions.isDisplayOnDesktop
        return fn()


class COpenVRContext():
    def __init__(self):
        self.clear()

    def clear(self):
        pass

_vr_token = c_uint32()
