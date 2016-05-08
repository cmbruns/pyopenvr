#!/bin/env python

import sys
import openvr

print "OpenVR test program"

if openvr.isHmdPresent():
    print "VR head set found"

if openvr.isRuntimeInstalled():
    print "Runtime is installed"

vr_system = openvr.init(openvr.EVRApplicationType_VRApplication_Scene)

print openvr.runtimePath()

# print vr_system.getRecommendedRenderTargetSize()

print vr_system.isDisplayOnDesktop()

for i in range(50):
    xform = vr_system.getEyeToHeadTransform(openvr.EVREye_Eye_Left)
    print xform

vr_system.shutdown()
