#!/bin/env python

import sys
import time
import openvr

openvr.init(openvr.VRApplication_Scene)

# Create data structure to hold locations of tracked devices such as headsets, controllers, and lighthouses
poses_t = openvr.TrackedDevicePose_t * openvr.k_unMaxTrackedDeviceCount
poses = poses_t()

# Print out headset transform five times a second for 20 seconds
for i in range(100):
    openvr.VRCompositor().waitGetPoses(poses, len(poses), None, 0)
    hmd_pose = poses[openvr.k_unTrackedDeviceIndex_Hmd]
    print(hmd_pose.mDeviceToAbsoluteTracking)
    sys.stdout.flush()
    time.sleep(0.2)

openvr.shutdown()
