"""
Created on Apr 18, 2017

@author: Christopher Bruns
"""

import math

import numpy


def pack(matrix, do_transpose=False):
    if do_transpose:
        return numpy.ascontiguousarray(matrix.T)
    else:
        return numpy.ascontiguousarray(matrix)


def frustum(left, right, bottom, top, z_near, z_far):
    a = (right + left) / (right - left)
    b = (top + bottom) / (top - bottom)
    c = -(z_far + z_near) / (z_far - z_near)
    d = -(2.0 * z_far * z_near) / (z_far - z_near)
    return numpy.matrix([
            [2.0 * z_near / (right - left), 0.0, a, 0.0],
            [0.0, 2.0 * z_near / (top - bottom), b, 0.0],
            [0.0, 0.0, c, d],
            [0.0, 0.0, -1.0, 0.0]], dtype=numpy.float32).T


def identity():
    return numpy.matrix([
            [1, 0, 0, 0],
            [0, 1, 0, 0],
            [0, 0, 1, 0],
            [0, 0, 0, 1]], dtype=numpy.float32)


def perspective(fov_y, aspect, z_near, z_far):
    f_h = math.tan(fov_y / 2.0 / 180.0 * math.pi) * z_near
    f_w = f_h * aspect
    return frustum(-f_w, f_w, -f_h, f_h, z_near, z_far)


def rotate_x(angle):
    s = math.sin(float(angle))
    c = math.cos(float(angle))
    return numpy.matrix([
            [1, 0, 0, 0],
            [0, c, -s, 0],
            [0, s, c, 0],
            [0, 0, 0, 1]], dtype=numpy.float32).T


def rotate_y(angle):
    s = math.sin(float(angle))
    c = math.cos(float(angle))
    return numpy.matrix([
            [c, 0, s, 0],
            [0, 1, 0, 0],
            [-s, 0, c, 0],
            [0, 0, 0, 1]], dtype=numpy.float32).T


def rotate_z(angle):
    s = math.sin(float(angle))
    c = math.cos(float(angle))
    return numpy.matrix([
            [c, -s, 0, 0],
            [s, c, 0, 0],
            [0, 0, 1, 0],
            [0, 0, 0, 1]], dtype=numpy.float32).T


def scale(sx, sy=None, sz=None):
    if sy is None:
        sy = sx
    if sz is None:
        sz = sx
    return numpy.matrix([
                         (sx, 0, 0, 0),
                         (0, sy, 0, 0),
                         (0, 0, sz, 0),
                         (0, 0, 0, 1)], dtype=numpy.float32)


def translate(xyz):
    x, y, z = xyz
    array = [
            [1, 0, 0, x],
            [0, 1, 0, y],
            [0, 0, 1, z],
            [0, 0, 0, 1]]
    mat = numpy.matrix(array, dtype=numpy.float32)
    return mat.T


