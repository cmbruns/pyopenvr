#!/bin/env python

import unittest
import ctypes

import openvr


class TestVector(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_vector(self):
        v = openvr.HmdVector2_t(1, 2)
        self.assertEqual(1, v[0])
        self.assertEqual(2, v[1])
        self.assertEqual(2, len(v))
        v[1] = 3
        self.assertEqual(3, v[1])

if __name__ == '__main__':
    unittest.main()

