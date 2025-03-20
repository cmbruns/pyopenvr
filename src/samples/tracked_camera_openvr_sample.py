from ctypes import c_uint8, POINTER
import sys
from typing import Optional

from PySide6 import QtGui, QtWidgets
from PySide6.QtCore import QPoint
from PySide6.QtGui import QColor, QImage, Qt
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

    def set_frame_image(self, p_frame_image: POINTER(c_uint8), n_frame_width: int, n_frame_height: int, frame_header: openvr.CameraVideoStreamFrameHeader_t):
        if frame_header is not None:
            self.m_CurrentFrameHeader = frame_header    
        if p_frame_image and n_frame_width and n_frame_height:
            if self.m_source_image and (self.m_source_image.width() != n_frame_width or self.m_source_image.height() != n_frame_height):
                # dimension changed
                self.m_source_image = None 
            if not self.m_source_image:
                # allocate to expected dimensions
                self.m_source_image = QImage(n_frame_width, n_frame_height, QImage.Format_RGB32)
            for y in range(n_frame_height):
                for x in range(n_frame_width):
                    self.m_source_image.setPixel(
                        x, y,
                        QColor(p_frame_image[0], p_frame_image[1], p_frame_image[2]).rgba()
                    )
                    p_frame_image += 4
        # schedule a repaint
        self.update()
    

class CQTrackedCameraOpenVRSample(QtWidgets.QMainWindow):
    def __init__(self, parent: QtWidgets.QWidget = None):
        super().__init__(parent)


def main():
    a = QtWidgets.QApplication(sys.argv)
    w = CQTrackedCameraOpenVRSample()
    w.show()
    sys.exit(a.exec())


if __name__ == "__main__":
    main()
