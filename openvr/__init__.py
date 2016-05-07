#!/bin/env python

import os
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


_openvr.VR_InitInternal.restype = POINTER(c_int)
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


class IVRSystem:
    def __init__(self):
        self.ptr = init()

    def shutdown():
        shutdown()
        self.ptr = None

