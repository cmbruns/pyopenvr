#!/bin/env python

import unittest
import ctypes

import openvr


class TestCompositor_FrameTiming(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_ctor(self):
        cft = openvr.Compositor_FrameTiming()
        self.assertEqual(ctypes.sizeof(openvr.Compositor_FrameTiming), cft.m_nSize)


if __name__ == '__main__':
    unittest.main()

