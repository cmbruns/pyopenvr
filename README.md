# pyopenvr
### Unofficial python bindings for Valve's OpenVR virtual reality SDK, located at https://github.com/ValveSoftware/openvr

## Installation
- [ ] Install Python 2.7+ or 3.5+ https://www.python.org/download/
- [ ] Install HTC Vive SteamVR
- [ ] ``pip install openvr`` OR download the installer at https://github.com/cmbruns/pyopenvr/releases

## Use

```python
import sys
import time
import openvr

openvr.init(openvr.VRApplication_Scene)

poses_t = openvr.TrackedDevicePose_t * openvr.k_unMaxTrackedDeviceCount
poses = poses_t()

for i in range(100):
    openvr.VRCompositor().waitGetPoses(poses, len(poses), None, 0)
    hmd_pose = poses[openvr.k_unTrackedDeviceIndex_Hmd]
    print(hmd_pose.mDeviceToAbsoluteTracking)
    sys.stdout.flush()
    time.sleep(0.2)

openvr.shutdown()
```

