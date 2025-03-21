from ctypes import c_uint8, POINTER
import datetime
import logging
import sys
from typing import Optional

from PySide6 import QtGui
from PySide6.QtCore import QPoint, QElapsedTimer, QTimer, Slot
from PySide6.QtGui import QAction, QColor, QImage, Qt, QPalette, QTextCursor
from PySide6.QtWidgets import QApplication, QMainWindow, QSizePolicy, QWidget, QTextEdit, QSplitter

import openvr as vr


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


def message_color(r, g, b):
    return (r << 16) | (g << 8) | b


MESSAGE_COLOR_NORMAL = message_color(0, 0, 0)
MESSAGE_COLOR_WARNING = message_color(255, 255, 0)
MESSAGE_COLOR_ERROR = message_color(255, 0, 0)

INVALID_TRACKED_CAMERA_HANDLE = vr.TrackedCameraHandle_t(0)  # TODO: into openvr namespace


class CQCameraPreviewImage(QWidget):
    def __init__(self, parent: QWidget = None):
        super().__init__(parent)
        self.m_source_image: Optional[QtGui.QImage] = None
        self.m_CurrentFrameHeader = vr.CameraVideoStreamFrameHeader_t()
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
            painter.drawImage(QPoint(0, 0), self.m_source_image.rgbSwapped())
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

    def set_frame_image(self, p_frame_image: POINTER(c_uint8), n_frame_width: int, n_frame_height: int, frame_header: vr.CameraVideoStreamFrameHeader_t):
        if frame_header is not None:
            self.m_CurrentFrameHeader = frame_header    
        if p_frame_image and n_frame_width and n_frame_height:
            if self.m_source_image and (self.m_source_image.width() != n_frame_width or self.m_source_image.height() != n_frame_height):
                # dimension changed
                self.m_source_image = None 
            if self.m_source_image is None:
                # allocate to expected dimensions
                self.m_source_image = QImage(
                    p_frame_image,  # Attach to buffer for speed
                    n_frame_width, n_frame_height,
                    4 * n_frame_width, QImage.Format_RGB32,
                )
        # schedule a repaint
        self.update()
    

class CQTrackedCameraOpenVRSample(QMainWindow):
    def __init__(self, parent: QWidget = None):
        super().__init__(parent)
        self.m_pVRSystem: Optional[vr.IVRSystem] = None
        self.m_pVRTrackedCamera: Optional[vr.IVRTrackedCamera] = None
        self.m_hTrackedCamera = vr.TrackedCameraHandle_t(0)  # INVALID_TRACKED_CAMERA_HANDLE
        self.m_nCameraFrameWidth: int = 0
        self.m_nCameraFrameHeight: int = 0
        self.m_nCameraFrameBufferSize: int = 0
        self.m_pCameraFrameBuffer: POINTER(c_uint8) = None
        self.setWindowTitle("Tracked Camera OpenVR Test")
        self.m_pMessageText = QTextEdit()
        self.m_pSplitter = QSplitter(Qt.Vertical, self)
        self.m_pCameraPreviewImage = CQCameraPreviewImage(self)
        self.m_HMDSerialNumberString = None
        self.create_primary_windows()
        self.setFocusPolicy(Qt.StrongFocus)
        self.log_message(logging.INFO, f"Build: {datetime.datetime.now()}\n")
        self.m_pExitAction = QAction("Exit", self)
        self.m_pExitAction.triggered.connect(self.on_exit_action)
        self.m_pToggleStreamingAction = QAction("Toggle Streaming", self)
        self.m_pToggleStreamingAction.setCheckable(True)
        self.m_pToggleStreamingAction.triggered.connect(self.on_toggle_streaming_action)
        self.m_pMainMenu = self.menuBar().addMenu("&Main")
        self.m_pMainMenu.addAction(self.m_pToggleStreamingAction)
        self.m_pMainMenu.addSeparator()
        self.m_pMainMenu.addAction(self.m_pExitAction)
        self.m_VideoSignalTime = QElapsedTimer()
        self.m_pDisplayRefreshTimer = QTimer(self)
        self.m_pDisplayRefreshTimer.setInterval(16)
        self.m_pDisplayRefreshTimer.timeout.connect(self.on_display_refresh_timeout)
        self.m_nLastFrameSequence = 0

    def __enter__(self):
        b_valid_openvr = self.init_openvr()
        if not b_valid_openvr:
            # No valid HMD, inhibit any expected user options
            self.m_pMainMenu.setEnabled(False)
        # create an update timer
        self.m_pDisplayRefreshTimer.start()
        self.resize(900, 700)
        return self

    def __exit__(self, exc_type, value, traceback):
        self.m_pVRSystem = None
        self.m_pVRTrackedCamera = None

    def showEvent(self, show_event: QtGui.QShowEvent):
        self.set_splitter_position(0.75)
        # auto start streaming, same as user triggering
        self.m_pToggleStreamingAction.trigger()

    def closeEvent(self, close_event: QtGui.QCloseEvent):
        if self.m_pVRTrackedCamera:
            self.m_pVRTrackedCamera.releaseVideoStreamingService(self.m_hTrackedCamera)
        close_event.accept()

    def set_splitter_position(self, fl_split_factor: float):
        splitter_sizes = self.m_pSplitter.sizes()
        n_total_height = 0
        for ss in splitter_sizes:
            n_total_height += ss
        if not n_total_height:
            # This occurs when the window hasn't been shown yet at all, app is still starting up.
            # The splitter split factor will get forced down again during the initial show event of the parent.
            return
        n_top_height = int(fl_split_factor * n_total_height)
        n_bottom_height = n_total_height - n_top_height
        if n_top_height != splitter_sizes[0] or n_bottom_height != splitter_sizes[1]:
            splitter_sizes.clear()
            splitter_sizes.append(n_top_height)
            splitter_sizes.append(n_bottom_height)
            self.m_pSplitter.setSizes(splitter_sizes)
    
    def log_message(self, log_level: int, message: str):
        if self.m_pMessageText:
            rgba_color = MESSAGE_COLOR_NORMAL
            if log_level == logging.WARNING:
                rgba_color = MESSAGE_COLOR_WARNING
            elif log_level == logging.ERROR:
                rgba_color = MESSAGE_COLOR_ERROR
            text_color = QColor((rgba_color >> 16) & 0xFF, (rgba_color >> 8) & 0xFF, (rgba_color & 0xFF), 0xFF)
            self.m_pMessageText.setTextColor(text_color)
            self.m_pMessageText.insertPlainText(f"{message}\n")
            self.m_pMessageText.moveCursor(QTextCursor.End, QTextCursor.MoveAnchor)
        logger.log(log_level, message)
    
    def create_primary_windows(self):
        self.m_pMessageText.setLineWrapMode(QTextEdit.NoWrap)
        self.m_pMessageText.setReadOnly(True)
        self.m_pMessageText.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        palette = self.m_pMessageText.palette()
        palette.setColor(QPalette.Base, QColor(180, 180, 180))
        self.m_pMessageText.setPalette(palette)
        self.m_pMessageText.setAutoFillBackground(True)
        self.m_pSplitter.setHandleWidth(8)
        self.m_pSplitter.setChildrenCollapsible(False)
        self.m_pCameraPreviewImage.setMinimumHeight(100)
        self.m_pMessageText.setMinimumHeight(100)
        self.m_pSplitter.addWidget(self.m_pCameraPreviewImage)
        self.m_pSplitter.addWidget(self.m_pMessageText)
        self.setCentralWidget(self.m_pSplitter)

    @Slot()
    def on_exit_action(self):
        self.close()

    @Slot()
    def on_display_refresh_timeout(self):
        if not self.m_pVRTrackedCamera or not self.m_hTrackedCamera:
            return
        if self.m_VideoSignalTime.elapsed() >= 2000:
            # No frames after 2 seconds...
            self.log_message(logging.ERROR, "No Video Frames Arriving!")
            self.m_VideoSignalTime.restart()
        # get the frame header only
        try:
            frame_header = self.m_pVRTrackedCamera.getVideoStreamFrameBuffer(
                self.m_hTrackedCamera,
                vr.VRTrackedCameraFrameType_Undistorted,
                None,
                0,
            )
        except BaseException as exc:
            print(exc)
            return
        if frame_header.nFrameSequence == self.m_nLastFrameSequence:
            # frame hasn't changed yet, nothing to do
            return
        self.m_VideoSignalTime.restart()
        # Frame has changed, do the more expensive frame buffer copy
        frame_header = self.m_pVRTrackedCamera.getVideoStreamFrameBuffer(
            self.m_hTrackedCamera, vr.VRTrackedCameraFrameType_Undistorted,
            self.m_pCameraFrameBuffer, self.m_nCameraFrameBufferSize,
        )
        self.m_nLastFrameSequence = frame_header.nFrameSequence
        self.m_pCameraPreviewImage.set_frame_image(
            self.m_pCameraFrameBuffer,
            self.m_nCameraFrameWidth, self.m_nCameraFrameHeight,
            frame_header,
        )

    @Slot()
    def on_toggle_streaming_action(self):
        if self.m_pToggleStreamingAction.isChecked():
            self.start_video_preview()
        else:
            self.stop_video_preview()
    
    def start_video_preview(self) -> bool:
        self.log_message(logging.INFO, "StartVideoPreview()")
        # Allocate for camera frame buffer requirements
        self.m_nCameraFrameWidth, self.m_nCameraFrameHeight, nCameraFrameBufferSize = (
            self.m_pVRTrackedCamera.getCameraFrameSize(
                vr.k_unTrackedDeviceIndex_Hmd, vr.VRTrackedCameraFrameType_Undistorted,
            )
        )
        if nCameraFrameBufferSize and nCameraFrameBufferSize != self.m_nCameraFrameBufferSize:
            self.m_pCameraFrameBuffer = None
            self.m_nCameraFrameBufferSize = nCameraFrameBufferSize
            self.m_pCameraFrameBuffer = (c_uint8 * self.m_nCameraFrameBufferSize)()
            # memset(self.m_pCameraFrameBuffer, 0, self.m_nCameraFrameBufferSize)
        self.m_nLastFrameSequence = 0
        self.m_VideoSignalTime.start()
        self.m_hTrackedCamera = self.m_pVRTrackedCamera.acquireVideoStreamingService(vr.k_unTrackedDeviceIndex_Hmd)
        if self.m_hTrackedCamera == INVALID_TRACKED_CAMERA_HANDLE:
            self.log_message(logging.ERROR, "AcquireVideoStreamingService() Failed!")
            return False
        return True
    
    def stop_video_preview(self):
        self.log_message(logging.INFO, "StopVideoPreview()")
    
        self.m_pVRTrackedCamera.releaseVideoStreamingService(self.m_hTrackedCamera)
        self.m_hTrackedCamera = INVALID_TRACKED_CAMERA_HANDLE
    
    def init_openvr(self) -> bool:
        # Loading the SteamVR Runtime
        self.log_message(logging.INFO, "Starting OpenVR...")
        self.m_pVRSystem = vr.init(vr.VRApplication_Scene)
        system_name = self.m_pVRSystem.getStringTrackedDeviceProperty(
            vr.k_unTrackedDeviceIndex_Hmd,
            vr.Prop_TrackingSystemName_String)
        serial_number = self.m_pVRSystem.getStringTrackedDeviceProperty(
            vr.k_unTrackedDeviceIndex_Hmd,
            vr.Prop_SerialNumber_String)
        self.m_HMDSerialNumberString = serial_number
        self.log_message(logging.INFO, f"VR HMD: {system_name} {serial_number}")
    
        self.m_pVRTrackedCamera = vr.VRTrackedCamera()
        if not self.m_pVRTrackedCamera:
            self.log_message(logging.ERROR, "Unable to get Tracked Camera interface.")
            return False
        b_has_camera = self.m_pVRTrackedCamera.hasCamera(vr.k_unTrackedDeviceIndex_Hmd)
        if not b_has_camera:
            self.log_message(
                logging.ERROR,
                f"No Tracked Camera Available!")
            return False
        # Accessing the FW description is just a further check to ensure camera communication is valid as expected.
        buffer = self.m_pVRSystem.getStringTrackedDeviceProperty(
            vr.k_unTrackedDeviceIndex_Hmd,
            vr.Prop_CameraFirmwareDescription_String,
        )
        self.log_message(logging.INFO, f"Camera Firmware: {buffer}")
        return True


def main():
    a = QApplication(sys.argv)
    with CQTrackedCameraOpenVRSample() as w:
        w.show()
        sys.exit(a.exec())


if __name__ == "__main__":
    main()
