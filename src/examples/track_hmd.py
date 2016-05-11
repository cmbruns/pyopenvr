#!/bin/env python

import sys
import time
import openvr

vr_system = openvr.init(openvr.EVRApplicationType_VRApplication_Scene)

for i in range(100):
    pose = vr_system.getDeviceToAbsoluteTrackingPose(
        openvr.TrackingUniverseStanding,
        0,
        1)
    print pose
    sys.stdout.flush()
    time.sleep(0.2)

vr_system.shutdown()
