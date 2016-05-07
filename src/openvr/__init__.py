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
_openvr = cdll.openvr_api


########################
### Expose constants ###
########################

IVRSystem_Version = "IVRSystem_012"


#############################
### Expose enum constants ###
#############################

ENUM_TYPE = c_int32

EVRInitError = ENUM_TYPE
EVRInitError_VRInitError_None = ENUM_TYPE(0)
EVRInitError_VRInitError_Unknown = ENUM_TYPE(1)
EVRInitError_VRInitError_Init_InstallationNotFound = ENUM_TYPE(100)
EVRInitError_VRInitError_Init_InstallationCorrupt = ENUM_TYPE(101)
EVRInitError_VRInitError_Init_VRClientDLLNotFound = ENUM_TYPE(102)
# TODO: put in a bunch more of these EVRInit...

EVRApplicationType = ENUM_TYPE
EVRApplicationType_VRApplication_Other = ENUM_TYPE(0)
EVRApplicationType_VRApplication_Scene = ENUM_TYPE(1)
EVRApplicationType_VRApplication_Overlay = ENUM_TYPE(2)
EVRApplicationType_VRApplication_Background = ENUM_TYPE(3)
EVRApplicationType_VRApplication_Utility = ENUM_TYPE(4)
EVRApplicationType_VRApplication_VRMonitor = ENUM_TYPE(5)


######################
### Expose classes ###
######################

class OpenVRError(RuntimeError):
    """
    OpenVRError is a custom exception type for when OpenVR functions return a failure code.
    Such a specific exception type allows more precise exception handling that does just raising Exception().
    """
    pass

# Anonymous structures
class IVRSystem(Structure):
    pass
class IVRChaperone(Structure):
    pass
class IVRCompositor(Structure):
    pass
class IVROverlay(Structure):
    pass
class IVRRenderModels(Structure):
    pass

class IVRSystem_FnTable(Structure):
    _fields__ = [
        ("getRecommendedRenderTargetSize", WINFUNCTYPE(None, POINTER(c_uint32), POINTER(c_uint32))),
    ]
    """
        ("", void (OPENVR_FNTABLE_CALLTYPE *GetRecommendedRenderTargetSize)(uint32_t * pnWidth, uint32_t * pnHeight)),
        ("", struct HmdMatrix44_t (OPENVR_FNTABLE_CALLTYPE *GetProjectionMatrix)(EVREye eEye, float fNearZ, float fFarZ, EGraphicsAPIConvention eProjType);
        ("", void (OPENVR_FNTABLE_CALLTYPE *GetProjectionRaw)(EVREye eEye, float * pfLeft, float * pfRight, float * pfTop, float * pfBottom);
        ("", struct DistortionCoordinates_t (OPENVR_FNTABLE_CALLTYPE *ComputeDistortion)(EVREye eEye, float fU, float fV);
        ("", struct HmdMatrix34_t (OPENVR_FNTABLE_CALLTYPE *GetEyeToHeadTransform)(EVREye eEye);
        ("", bool (OPENVR_FNTABLE_CALLTYPE *GetTimeSinceLastVsync)(float * pfSecondsSinceLastVsync, uint64_t * pulFrameCounter);
        ("", int32_t (OPENVR_FNTABLE_CALLTYPE *GetD3D9AdapterIndex)();
        ("", void (OPENVR_FNTABLE_CALLTYPE *GetDXGIOutputInfo)(int32_t * pnAdapterIndex);
        ("", bool (OPENVR_FNTABLE_CALLTYPE *IsDisplayOnDesktop)();
        ("", bool (OPENVR_FNTABLE_CALLTYPE *SetDisplayVisibility)(bool bIsVisibleOnDesktop);
        ("", void (OPENVR_FNTABLE_CALLTYPE *GetDeviceToAbsoluteTrackingPose)(ETrackingUniverseOrigin eOrigin, float fPredictedSecondsToPhotonsFromNow, struct TrackedDevicePose_t * pTrackedDevicePoseArray, uint32_t unTrackedDevicePoseArrayCount);
        ("", void (OPENVR_FNTABLE_CALLTYPE *ResetSeatedZeroPose)();
        ("", struct HmdMatrix34_t (OPENVR_FNTABLE_CALLTYPE *GetSeatedZeroPoseToStandingAbsoluteTrackingPose)();
        ("", struct HmdMatrix34_t (OPENVR_FNTABLE_CALLTYPE *GetRawZeroPoseToStandingAbsoluteTrackingPose)();
        ("", uint32_t (OPENVR_FNTABLE_CALLTYPE *GetSortedTrackedDeviceIndicesOfClass)(ETrackedDeviceClass eTrackedDeviceClass, TrackedDeviceIndex_t * punTrackedDeviceIndexArray, uint32_t unTrackedDeviceIndexArrayCount, TrackedDeviceIndex_t unRelativeToTrackedDeviceIndex);
        ("", EDeviceActivityLevel (OPENVR_FNTABLE_CALLTYPE *GetTrackedDeviceActivityLevel)(TrackedDeviceIndex_t unDeviceId);
        ("", void (OPENVR_FNTABLE_CALLTYPE *ApplyTransform)(struct TrackedDevicePose_t * pOutputPose, struct TrackedDevicePose_t * pTrackedDevicePose, struct HmdMatrix34_t * pTransform);
        ("", TrackedDeviceIndex_t (OPENVR_FNTABLE_CALLTYPE *GetTrackedDeviceIndexForControllerRole)(ETrackedControllerRole unDeviceType);
        ("", ETrackedControllerRole (OPENVR_FNTABLE_CALLTYPE *GetControllerRoleForTrackedDeviceIndex)(TrackedDeviceIndex_t unDeviceIndex);
        ("", ETrackedDeviceClass (OPENVR_FNTABLE_CALLTYPE *GetTrackedDeviceClass)(TrackedDeviceIndex_t unDeviceIndex);
        ("", bool (OPENVR_FNTABLE_CALLTYPE *IsTrackedDeviceConnected)(TrackedDeviceIndex_t unDeviceIndex);
        ("", bool (OPENVR_FNTABLE_CALLTYPE *GetBoolTrackedDeviceProperty)(TrackedDeviceIndex_t unDeviceIndex, ETrackedDeviceProperty prop, ETrackedPropertyError * pError);
        ("", float (OPENVR_FNTABLE_CALLTYPE *GetFloatTrackedDeviceProperty)(TrackedDeviceIndex_t unDeviceIndex, ETrackedDeviceProperty prop, ETrackedPropertyError * pError);
        ("", int32_t (OPENVR_FNTABLE_CALLTYPE *GetInt32TrackedDeviceProperty)(TrackedDeviceIndex_t unDeviceIndex, ETrackedDeviceProperty prop, ETrackedPropertyError * pError);
        ("", uint64_t (OPENVR_FNTABLE_CALLTYPE *GetUint64TrackedDeviceProperty)(TrackedDeviceIndex_t unDeviceIndex, ETrackedDeviceProperty prop, ETrackedPropertyError * pError);
        ("", struct HmdMatrix34_t (OPENVR_FNTABLE_CALLTYPE *GetMatrix34TrackedDeviceProperty)(TrackedDeviceIndex_t unDeviceIndex, ETrackedDeviceProperty prop, ETrackedPropertyError * pError);
        ("", uint32_t (OPENVR_FNTABLE_CALLTYPE *GetStringTrackedDeviceProperty)(TrackedDeviceIndex_t unDeviceIndex, ETrackedDeviceProperty prop, char * pchValue, uint32_t unBufferSize, ETrackedPropertyError * pError);
        ("", char * (OPENVR_FNTABLE_CALLTYPE *GetPropErrorNameFromEnum)(ETrackedPropertyError error);
        ("", bool (OPENVR_FNTABLE_CALLTYPE *PollNextEvent)(struct VREvent_t * pEvent, uint32_t uncbVREvent);
        ("", bool (OPENVR_FNTABLE_CALLTYPE *PollNextEventWithPose)(ETrackingUniverseOrigin eOrigin, struct VREvent_t * pEvent, uint32_t uncbVREvent, TrackedDevicePose_t * pTrackedDevicePose);
        ("", char * (OPENVR_FNTABLE_CALLTYPE *GetEventTypeNameFromEnum)(EVREventType eType);
        ("", struct HiddenAreaMesh_t (OPENVR_FNTABLE_CALLTYPE *GetHiddenAreaMesh)(EVREye eEye);
        ("", bool (OPENVR_FNTABLE_CALLTYPE *GetControllerState)(TrackedDeviceIndex_t unControllerDeviceIndex, VRControllerState_t * pControllerState);
        ("", bool (OPENVR_FNTABLE_CALLTYPE *GetControllerStateWithPose)(ETrackingUniverseOrigin eOrigin, TrackedDeviceIndex_t unControllerDeviceIndex, VRControllerState_t * pControllerState, struct TrackedDevicePose_t * pTrackedDevicePose);
        ("", void (OPENVR_FNTABLE_CALLTYPE *TriggerHapticPulse)(TrackedDeviceIndex_t unControllerDeviceIndex, uint32_t unAxisId, unsigned short usDurationMicroSec);
        ("", char * (OPENVR_FNTABLE_CALLTYPE *GetButtonIdNameFromEnum)(EVRButtonId eButtonId);
        ("", char * (OPENVR_FNTABLE_CALLTYPE *GetControllerAxisTypeNameFromEnum)(EVRControllerAxisType eAxisType);
        ("", bool (OPENVR_FNTABLE_CALLTYPE *CaptureInputFocus)();
        ("", void (OPENVR_FNTABLE_CALLTYPE *ReleaseInputFocus)();
        ("", bool (OPENVR_FNTABLE_CALLTYPE *IsInputFocusCapturedByAnotherProcess)();
        ("", uint32_t (OPENVR_FNTABLE_CALLTYPE *DriverDebugRequest)(TrackedDeviceIndex_t unDeviceIndex, char * pchRequest, char * pchResponseBuffer, uint32_t unResponseBufferSize);
        ("", EVRFirmwareError (OPENVR_FNTABLE_CALLTYPE *PerformFirmwareUpdate)(TrackedDeviceIndex_t unDeviceIndex);
        ("", void (OPENVR_FNTABLE_CALLTYPE *AcknowledgeQuit_Exiting)();
        ("", void (OPENVR_FNTABLE_CALLTYPE *AcknowledgeQuit_UserPrompt)();
    ]
    """

########################
### Expose functions ###
########################

_openvr.VR_GetGenericInterface.restype = POINTER(IVRSystem_FnTable)
_openvr.VR_GetGenericInterface.argtypes = [c_char_p, POINTER(EVRInitError)]
def getGenericInterface(interfaceVersion, error):
    return _openvr.VR_GetGenericInterface(interfaceVersion, error)


_openvr.VR_GetVRInitErrorAsSymbol.restype = c_char_p
_openvr.VR_GetVRInitErrorAsSymbol.argtypes = [EVRInitError]
def getInitErrorAsSymbol(error):
    return _openvr.VR_GetVRInitErrorAsSymbol(error)


_openvr.VR_InitInternal.restype = POINTER(c_int)
_openvr.VR_InitInternal.argtypes = [POINTER(EVRInitError), EVRApplicationType]
# Copying VR_Init inline implementation from https://github.com/ValveSoftware/openvr/blob/master/headers/openvr.h
# and from https://github.com/phr00t/jMonkeyVR/blob/master/src/jmevr/input/OpenVR.java
def init():
    eError = EVRInitError()
    vrToken = _openvr.VR_InitInternal(byref(eError), EVRApplicationType_VRApplication_Scene)
    if eError.value != EVRInitError_VRInitError_None.value:
        shutdown()
        raise OpenVRError(getInitErrorAsSymbol(eError) + str(eError))
    systemFunctions = getGenericInterface(IVRSystem_Version, eError)
    print systemFunctions
    # TODO: 


_openvr.VR_IsHmdPresent.restype = c_bool
_openvr.VR_IsHmdPresent.argtypes = []
def isHmdPresent():
    return _openvr.VR_IsHmdPresent()


_openvr.VR_IsRuntimeInstalled.restype = c_bool
_openvr.VR_IsRuntimeInstalled.argtypes = []
def isRuntimeInstalled():
    return _openvr.VR_IsRuntimeInstalled()


_openvr.VR_ShutdownInternal.restype = None
_openvr.VR_ShutdownInternal.argtypes = []
def shutdown():
    _openvr.VR_ShutdownInternal() # OK, this is just like inline definition in openvr.h


##########################################
### Wrap API in Object Oriented python ###
##########################################

class System:
    def __init__(self):
        self.ptr = init()

    def shutdown():
        if self.ptr is None:
            return
        shutdown()
        self.ptr = None

