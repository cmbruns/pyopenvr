from typing import Optional

import sys

from PySide6 import QtGui, QtWidgets
from PySide6.QtCore import QPoint
from PySide6.QtGui import QColor, Qt
from PySide6.QtWidgets import QSizePolicy

import openvr


class CQCameraPreviewImage(QtWidgets.QWidget):
    def __init__(self, parent: QtWidgets.QWidget = None):
        super().__init__(parent)
        self.m_source_image: Optional[QtGui.QImage] = None
        self.m_CurrentFrameHeader = openvr.CameraVideoStreamFrameHeader_t()
        self.setContentsMargins(0, 0, 0, 0)
        # the image fully paints all of its pixels, qt does not need to do it
        self.setAttribute(Qt.WA_OpaquePaintEvent, True)
        self.setAttribute(Qt.WA_NoSystemBackground, True)
        self.setAutoFillBackground(False)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    def paintEvent(self, event: QtGui.QPaintEvent):
        painter = QtGui.QPainter(self)
        # determine the allowable painting area properly inscribed by any border widgets
        paint_rect = self.contentsRect().intersected(event.rect())
        if paint_rect.isEmpty():
            # nothing to do
            return
        painter.fillRect(self.contentsRect(), QColor(180, 180, 180))
        if self.m_source_image is not None and not self.m_source_image.isNull():
            painter.drawImage(QPoint(0, 0), self.m_source_image)
        draw_font = painter.font()
        draw_font.setBold(True)
        painter.setFont(draw_font)
        n_label_y = 0
        painter.setPen(QColor(0, 255, 255))
        painter.drawText(
            0, n_label_y,
            self.contentsRect().width(), self.contentsRect().height(),
            Qt.AlignRight | Qt.AlignTop,
            f"Frame Size: {self.m_CurrentFrameHeader.nWidth}x{self.m_CurrentFrameHeader.nHeight}"
        )
        n_label_y += 20
        painter.drawText(
            0, n_label_y,
            self.contentsRect().width(), self.contentsRect().height(),
            Qt.AlignRight | Qt.AlignTop,
            f"Frame Sequence: {self.m_CurrentFrameHeader.nFrameSequence}")
        n_label_y += 30
        if self.m_CurrentFrameHeader.trackedDevicePose.bPoseIsValid:
            painter.setPen(QColor(0, 255, 0))
        else:
            painter.setPen(QColor(255, 255, 0))
        vld = "Valid" if self.m_CurrentFrameHeader.trackedDevicePose.bPoseIsValid else "Invalid"
        painter.drawText(
            0, n_label_y,
            self.contentsRect().width(), self.contentsRect().height(),
            Qt.AlignRight | Qt.AlignTop,
            f"Pose: {vld}"
        )
        n_label_y += 20
        for i in range(3):
            # emit the matrix
            matrix = self.m_CurrentFrameHeader.trackedDevicePose.mDeviceToAbsoluteTracking
            painter.drawText(
                0, n_label_y,
                self.contentsRect().width(), self.contentsRect().height(),
                Qt.AlignRight | Qt.AlignTop,
                f"{matrix.m[i][0]:2.2f} {matrix.m[i][1]:2.2f} {matrix.m[i][2]:2.2f} {matrix.m[i][3]:2.2f}",
            )
            n_label_y += 20
        n_label_y += 10
        painter.drawText(
            0, n_label_y,
            self.contentsRect().width(), self.contentsRect().height(),
            Qt.AlignRight | Qt.AlignTop, "Pose Velocity:")
        n_label_y += 20
        velocity = self.m_CurrentFrameHeader.trackedDevicePose.vVelocity
        painter.drawText(
            0,
            n_label_y,
            self.contentsRect().width(),
            self.contentsRect().height(),
            Qt.AlignRight | Qt.AlignTop,
            f"{velocity.v[0]:2.2f} {velocity.v[1]:2.2f} {velocity.v[2]:2.2f}",
        )
        n_label_y += 30
        painter.drawText(0, n_label_y, self.contentsRect().width(), self.contentsRect().height(),
                         Qt.AlignRight | Qt.AlignTop, "Pose Angular Velocity:")
        n_label_y += 20
        angular_velocity = self.m_CurrentFrameHeader.trackedDevicePose.vVelocity
        painter.drawText(
            0, n_label_y,
            self.contentsRect().width(), self.contentsRect().height(),
            Qt.AlignRight | Qt.AlignTop,
            f"{angular_velocity.v[0]:2.2f} {angular_velocity.v[1]:2.2f} {angular_velocity.v[2]:2.2f}",
        )
        n_label_y += 20


class CQTrackedCameraOpenVR(QtWidgets.QMainWindow):
    def __init__(self, parent: QtWidgets.QWidget = None):
        super().__init__(parent)


def main():
    a = QtWidgets.QApplication(sys.argv)
    w = CQTrackedCameraOpenVR()
    w.show()
    sys.exit(a.exec())


if __name__ == "__main__":
    main()
