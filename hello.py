#!/bin/env python

import openvr

print "Hello"

if not openvr.is_hmd_present():
    sys.exit(0)

openvr.init()
openvr.shutdown()
