#!/bin/env python

# file qt_pyside_app.py

import sys

from PySide.QtCore import Qt, QTimer
from PySide.QtGui import QApplication, QMainWindow
from PySide.QtOpenGL import QGLWidget, QGLFormat

"""
Toy PySide application for use with "hello world" examples demonstrating pyopenvr
"""


class MyGlWidget(QGLWidget):
    "PySideApp uses Qt library to create an opengl context, listen to keyboard events, and clean up"

    def __init__(self, renderer, glformat, app):
        "Creates an OpenGL context and a window, and acquires OpenGL resources"
        super(MyGlWidget, self).__init__(glformat)
        self.renderer = renderer
        self.app = app
        # Use a timer to rerender as fast as possible
        self.timer = QTimer(self)
        self.timer.setSingleShot(True)
        self.timer.setInterval(0)
        self.timer.timeout.connect(self.render_vr)
        # Accept keyboard events
        self.setFocusPolicy(Qt.StrongFocus)

    def __enter__(self):
        "setup for RAII using 'with' keyword"
        return self

    def __exit__(self, type_arg, value, traceback):
        "cleanup for RAII using 'with' keyword"
        self.dispose_gl()

    def initializeGL(self):
        if self.renderer is not None:
            self.renderer.init_gl()
        self.timer.start()

    def paintGL(self):
        "render scene one time"
        self.renderer.render_scene()
        self.swapBuffers() # Seems OK even in single-buffer mode
        
    def render_vr(self):
        self.makeCurrent()
        self.paintGL()
        self.doneCurrent()
        self.timer.start() # render again real soon now

    def disposeGL(self):
        if self.renderer is not None:
            self.makeCurrent()
            self.renderer.dispose_gl()
            self.doneCurrent()

    def keyPressEvent(self, event):
        "press ESCAPE to quit the application"
        key = event.key()
        if key == Qt.Key_Escape:
            self.app.quit()
            
            
class QtPysideApp(QApplication):
    def __init__(self, renderer, title):
        QApplication.__init__(self, sys.argv)
        self.window = QMainWindow()
        self.window.setWindowTitle(title)
        self.window.resize(800,600)
        # Get OpenGL 4.1 context
        glformat = QGLFormat()
        glformat.setVersion(4, 1)
        glformat.setProfile(QGLFormat.CoreProfile)
        glformat.setDoubleBuffer(False)
        self.glwidget = MyGlWidget(renderer, glformat, self)
        self.window.setCentralWidget(self.glwidget)
        self.window.show()
        
    def __enter__(self):
        "setup for RAII using 'with' keyword"
        return self

    def __exit__(self, type_arg, value, traceback):
        "cleanup for RAII using 'with' keyword"
        self.glwidget.disposeGL()

    def run_loop(self):
        retval = self.exec_()
        sys.exit(retval)


if __name__ == "__main__":
    from openvr.gl_renderer import OpenVrGlRenderer
    from openvr.color_cube_actor import ColorCubeActor
    actor = ColorCubeActor()
    renderer = OpenVrGlRenderer(actor)
    with QtPysideApp(renderer, "PySide OpenVR color cube") as qtPysideApp:
        qtPysideApp.run_loop()
