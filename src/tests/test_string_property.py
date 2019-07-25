#!/bin/env python

import unittest

import openvr


class TestStringProperties(unittest.TestCase):
    def setUp(self):
        self.vr_sys = openvr.init(openvr.VRApplication_Other)

    def tearDown(self):
        pass

    def get_string_raises(self):
        #  1009 : Prop_ConnectedWirelessDongle_String = [error: TrackedProp_UnknownProperty]
        prop = self.vr_sys.getStringTrackedDeviceProperty(0, openvr.Prop_ConnectedWirelessDongle_String)
        return prop

    def get_string1(self):
        prop = self.vr_sys.getStringTrackedDeviceProperty(0, openvr.Prop_TrackingSystemName_String)
        return prop

    def test_string_properties(self):
        self.assertRaises(openvr.error_code.TrackedProp_UnknownProperty, self.get_string_raises)
        tsn = self.get_string1()
        self.assertTrue(len(tsn) > 0)


if __name__ == '__main__':
    unittest.main()

