#!/bin/env python

import sys
import openvr

print "OpenVR test program"

if openvr.isHmdPresent():
    print "VR head set found"
else:
    sys.exit(0)

if openvr.isRuntimeInstalled():
    print "Runtime is installed"

print openvr.getInitErrorAsSymbol(openvr.EVRInitError_VRInitError_Init_InstallationCorrupt)

openvr.init()
openvr.shutdown()
