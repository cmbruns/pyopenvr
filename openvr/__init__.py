#!/bin/env python

# Python bindings for OpenVR API version 0.9.20
# from https://github.com/ValveSoftware/openvr
# Created May 7, 2016 Christopher Bruns

import os
import ctypes
from ctypes import *

# Add current directory to PATH, so we can load the DLL from right here.
os.environ['PATH'] = os.path.dirname(__file__) + ';' + os.environ['PATH']
_openvr = cdll.openvr_api

ENUM_TYPE = c_int32

EVRInitError = ENUM_TYPE


EVRApplicationType = ENUM_TYPE
EVRApplicationType_VRApplication_Other = 0
EVRApplicationType_VRApplication_Scene = 1
EVRApplicationType_VRApplication_Overlay = 2
EVRApplicationType_VRApplication_Background = 3
EVRApplicationType_VRApplication_Utility = 4
EVRApplicationType_VRApplication_VRMonitor = 5

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

_openvr.VR_InitInternal.restype = POINTER(IVRSystem)
_openvr.VR_InitInternal.argtypes = [POINTER(EVRInitError), EVRApplicationType]
def init():
    error_result = EVRInitError()
    result = _openvr.VR_InitInternal(byref(error_result), EVRApplicationType_VRApplication_Scene)

_openvr.VR_IsHmdPresent.restype = c_bool
_openvr.VR_IsHmdPresent.argtypes = []
def is_hmd_present():
    return _openvr.VR_IsHmdPresent()

_openvr.VR_ShutdownInternal.restype = None
_openvr.VR_ShutdownInternal.argtypes = []
def shutdown():
    _openvr.VR_ShutdownInternal()


class System:
    def __init__(self):
        self.ptr = init()

    def shutdown():
        if self.ptr is None:
            return
        shutdown()
        self.ptr = None

