#!/bin/env python

from distutils.core import setup

# Load module version from ovr/version.py
exec(open('src/openvr/version.py').read())

setup(
    name = "openvr",
    version = __version__,
    author = "Christopher Bruns",
    author_email = "cmbruns@rotatingpenguin.com",
    description = "Valve OpenVR SDK python bindings using ctypes",
    url = "https://github.com/cmbruns/pyopenvr",
    download_url = "https://github.com/cmbruns/pyopenvr/tarball/" + __version__,
    package_dir = {'': 'src'},
    packages = ['openvr', 'openvr.glframework'],
    package_data = {'openvr': ['*.dll', '*.so', '*.dylib']},
    keywords = "openvr valve htc vive vr virtual reality",
    classifiers = [],
)
