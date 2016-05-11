#!/bin/env python

import sys
import time
import openvr

vr_system = openvr.init(openvr.VRApplication_Scene)

for i in range(100):
    poses = vr_system.getDeviceToAbsoluteTrackingPose(
        openvr.TrackingUniverseStanding,
        0,
        openvr.k_unMaxTrackedDeviceCount)
    pose = poses[openvr.k_unTrackedDeviceIndex_Hmd]
    print pose.mDeviceToAbsoluteTracking
    sys.stdout.flush()
    time.sleep(0.2)

openvr.shutdown()
