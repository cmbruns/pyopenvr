#!/bin/env python

import unittest
import ctypes

import openvr


class TestProperties(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_bool(self):
        # Create various values for testing
        # A) Built in python booleans
        bt1 = True
        bf1 = False
        # B) OVR wrapped booleans
        bt2 = openvr.openvr_bool(1)
        bf2 = openvr.openvr_bool(0)
        # C) chr's, which might accidently get used sometimes
        # This is the most dangerous situation, because bool(chr(0)) == False
        bt3 = chr(1)
        bf3 = chr(0) # DANGER!
        # Make sure we understand who is true and false in boolean context
        self.assertTrue(bool(bt1))
        self.assertTrue(bool(bt2))
        self.assertTrue(bool(bt3))

        self.assertFalse(bool(bf1))
        self.assertFalse(bool(bf2))
        self.assertTrue(bool(bf3)) # Danger!


if __name__ == '__main__':
    unittest.main()

