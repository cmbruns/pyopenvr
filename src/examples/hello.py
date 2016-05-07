#!/bin/env python

import sys
import openvr

print "OpenVR test program"

if openvr.isHmdPresent():
    print "VR head set found"

if openvr.isRuntimeInstalled():
    print "Runtime is installed"

vr_system = openvr.init()
vr_system.shutdown()
