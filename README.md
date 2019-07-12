# pyopenvr
### Unofficial python bindings for Valve's OpenVR virtual reality SDK, located at https://github.com/ValveSoftware/openvr

## Installation
- [ ] Install Python 3.5+ https://www.python.org/download/
- [ ] Install HTC Vive SteamVR
- [ ] ``pip install openvr`` OR download the installer at https://github.com/cmbruns/pyopenvr/releases

## Use

```python
import sys
import time
import openvr

openvr.init(openvr.VRApplication_Scene)
poses = []  # will be populated with proper type after first call
for i in range(100):
    poses, _ = openvr.VRCompositor().waitGetPoses(poses, None)
    hmd_pose = poses[openvr.k_unTrackedDeviceIndex_Hmd]
    print(hmd_pose.mDeviceToAbsoluteTracking)
    sys.stdout.flush()
    time.sleep(0.2)
openvr.shutdown()
```


For more advanced usage, consult the example at https://github.com/cmbruns/pyopenvr/blob/master/src/samples/glfw/hellovr_glfw.py, which is a complete faithful translation into python from the original C++ sample at https://github.com/ValveSoftware/openvr/tree/master/samples/hellovr_opengl
