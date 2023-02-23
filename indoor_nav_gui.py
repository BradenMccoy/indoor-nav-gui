import sys, os
import camera_input as camera
import math
import depthai as dai
import numpy as np
import cv2
import logging
from PyQt5 import QtWidgets as qtw
from PyQt5.QtCore import Qt, QCoreApplication, QMetaObject, QRect, QUrl, QThread, pyqtSignal, QObject, pyqtSlot
from PyQt5.QtGui import QPixmap, QImage, QIcon, QFont
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent

class App(qtw.QWidget):
    def setupUI(self, main_window):
        main_window.setObjectName("MainWindow")
        main_window.setStyleSheet("background-color: black;")
        main_window.resize(927, 652)

        self.settings_view = SettingsView(main_window)
        self.collision_indicator_view = CollisionIndicatorView(main_window)
        self.log_view = LogView(main_window)
        self.camera_view = CameraView(main_window, self.settings_view, self.collision_indicator_view)
        

        self.retranslateUi(main_window)
        QMetaObject.connectSlotsByName(main_window)

    def retranslateUi(self, main_window):
        _translate = QCoreApplication.translate
        main_window.setWindowTitle(_translate("MainWindow", "Collision Detection"))

class CameraView(qtw.QWidget):
    media_player = QMediaPlayer()
    file_path = os.path.join(os.getcwd(), "soundfx/warning.mp3")
    url = QUrl.fromLocalFile(file_path)
    content = QMediaContent(url)
    media_player.setMedia(content)
    show_warning = True
    auditory_warning = True

    def __init__(self, parent_widget, settings, collision_indicator):
        super(CameraView, self).__init__()
        self.camera_view = qtw.QWidget(parent_widget)
        self.camera_view.setGeometry(QRect(30, 20, 871, 361))
        self.camera_view.setObjectName("CameraView")
        self.camera_view.setStyleSheet("background-color: white;")

        self.settings = settings
        self.collision_ind = collision_indicator

        # self.warning_button = qtw.QPushButton("Warning Button")
        # self.warning_button.clicked.connect(lambda: self.display_warning())
        self.video_label = qtw.QLabel()

        
        layout = qtw.QVBoxLayout()
        # layout.addWidget(self.warning_button)
        #  layout.addWidget(self.warning_widget, alignment=Qt.AlignRight | Qt.AlignBottom)
        layout.addWidget(self.video_label)
        self.camera_view.setLayout(layout)

    @pyqtSlot(np.ndarray)
    def update_frame(self, frame):
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image = QImage(frame, frame.shape[1], frame.shape[0], QImage.Format_RGB888)
        pixmap_image = QPixmap.fromImage(image)
        pixmap_image = pixmap_image.scaled(self.camera_view.frameGeometry().width(),self.camera_view.frameGeometry().height())
        self.video_label.setPixmap(pixmap_image)

    def display_warning(self):
        logging.warning("Door detect, width 72 in / 189 cm")
        logging.critical("Door detect, width 20 in / 51 cm - WARNING!")
        if self.settings.hasSound():
            logging.info("sound played")
            self.media_player.play()
        self.collision_ind.warning_symbol_hidden(False)
        

class CollisionIndicatorView(qtw.QWidget):
    def __init__(self, parent_widget):
        self.collision_indicator_view = qtw.QWidget(parent_widget)
        self.collision_indicator_view.setGeometry(QRect(29, 399, 211, 231))
        self.collision_indicator_view.setObjectName("CollisionIndicatorView")
        self.collision_indicator_view.setStyleSheet("background-color: white;")

        self.warning_widget = qtw.QWidget(parent_widget)
        self.warning_widget.setGeometry(QRect(30, 20, 871, 361))
        self.warning_symbol = QPixmap("images/warning.png").scaled(int(self.warning_widget.height() / 2),
                                                                   int(self.warning_widget.width() / 2),
                                                                   Qt.KeepAspectRatio, Qt.FastTransformation)
        self.warning_label = qtw.QLabel()
        self.warning_label.setPixmap(self.warning_symbol)

        self.warning_layout = qtw.QVBoxLayout()
        self.warning_layout.addWidget(self.warning_label)
        self.warning_widget.setLayout(self.warning_layout)
        self.warning_label.setHidden(True)

        layout = qtw.QVBoxLayout()
        layout.addWidget(self.warning_label)

        self.collision_indicator_view.setLayout(layout)

    def warning_symbol_hidden(self, b):
        self.warning_label.setHidden(b)

class LogView(qtw.QWidget):
    def __init__(self, parent_widget):
        self.log_view = qtw.QWidget(parent_widget)
        self.log_view.setGeometry(QRect(259, 399, 411, 231))
        self.log_view.setObjectName("LogView")
        self.log_view.setStyleSheet("background-color: white;")

        self.log_controller = LogController(self.log_view)
        logging.getLogger().addHandler(self.log_controller)

class SettingsView(qtw.QWidget):
    audio_warning = True

    def __init__(self, parent_widget):
        super(SettingsView, self).__init__()
        self.settings_view = qtw.QWidget(parent_widget)
        self.settings_view.setGeometry(QRect(690, 400, 211, 231))
        self.settings_view.setObjectName("SettingsView")
        self.settings_view.setStyleSheet("background-color: white;")

        self.mute_button = qtw.QPushButton(" Audio Warning")
        self.mute_button.clicked.connect(lambda: self.toggleSound())
        self.mute_button.setFont(QFont('Arial', 14))
        self.mute_button.setIcon(QIcon("images/unmute.png"))

        layout = qtw.QVBoxLayout()
        layout.addWidget(self.mute_button)
        self.settings_view.setLayout(layout)

    def toggleSound(self):
        self.audio_warning = not self.audio_warning
        if self.audio_warning:
            self.mute_button.setIcon(QIcon("images/unmute.png"))
        else:
            self.mute_button.setIcon(QIcon("images/mute.png"))

    def hasSound(self):
        return self.audio_warning

class LogController(logging.Handler):
    def __init__(self, parent_widget):
        super(LogController, self).__init__()

        self.log_text = qtw.QPlainTextEdit(parent_widget)
        self.log_text.resize(411, 231)
        self.log_text.setFont(QFont('Arial', 12))
        self.log_text.setReadOnly(True)

    def emit(self, msg):
        msg = self.format(msg)
        self.log_text.appendPlainText(msg)

MEASURED_AVERAGE = 255 / 771.665  # (max_dist-min_dist)/2+min_dist then converted to 0->255 range

ESTIMATED_SAFE_VALUE = 140  # Camera pointed about 30 degrees down 14 inches from the ground reads this pretty consistently
WARNING_THRESHOLD = 5
DANGER_THRESHOLD = 10

CAM_WIDTH = 640
CAM_HEIGHT = 400

# At the moment, the camera is 45 cm from the ground, pointed 30 degrees downward
MOUNT_ELEVATION = 45
MOUNT_ANGLE = -30

HFOV = 71.9  # Horizontal field of view
VFOV = 50.0  # Vertical field of view
BASELINE = 7.5  # Distance between stereo cameras in cm
FOCAL = 883.15  # Magic number needed for disparity -> depth calculation

WINDOW = "Collision Detection"


def getFrame(queue):
    # Get frame from queue
    frame = queue.get()
    # Convert frame to OpenCV format
    return frame.getCvFrame()


def getMonoCamera(pipeline, isLeft):
    mono = pipeline.createMonoCamera()

    mono.setResolution(dai.MonoCameraProperties.SensorResolution.THE_400_P)

    if isLeft:
        mono.setBoardSocket(dai.CameraBoardSocket.LEFT)
    else:
        mono.setBoardSocket(dai.CameraBoardSocket.RIGHT)
    return mono


def getStereoPair(pipeline, monoLeft, monoRight):
    stereo = pipeline.createStereoDepth()

    # Turn on occlusion check (small performance hit, but output is less noisy)
    stereo.setLeftRightCheck(True)
    # Link mono cameras to the stereo pair
    monoLeft.out.link(stereo.left)
    monoRight.out.link(stereo.right)

    return stereo


def get_reference():
    reference_frame = np.zeros((CAM_HEIGHT, CAM_WIDTH))  # same dimensions as images from the camera

    # Iterating in interpreted python instead of numpy
    # This is slow, but we only do this once at startup
    # for y in range(0, CAM_HEIGHT):
    #     # Angle of the current pixel
    #     theta = ((1.0 - (y / CAM_HEIGHT)) * VFOV) - (VFOV / 2) + MOUNT_ANGLE

    #     brightness = depthToBrightness(MOUNT_ELEVATION / (abs(math.tan(math.radians(theta)))))

    #     for x in range(0, CAM_WIDTH):
    #         referenceFrame[y][x] = brightness

    # generate an array of theta values based on VFOV and MOUNT_ANGLE
    theta = np.linspace(-(VFOV / 2) + MOUNT_ANGLE, VFOV / 2 + MOUNT_ANGLE, CAM_HEIGHT)
	# calculate elevation factor
    elevation_factor = MOUNT_ELEVATION / np.tan(np.radians(theta))
	# get an array of brightness values
    brightness = depthToBrightness(elevation_factor)
	# tile brightness array along the second axis CAM_WIDTH times and create the referenceFrame array
    reference_frame = np.tile(brightness[:, np.newaxis], (1, CAM_WIDTH))

    return reference_frame.astype(np.uint8)


# Image brightness (0 to 255) to depth (cm)
# Ideally we'd use disparity to depth, but our test cases already map disparity from
# 0 to 255, while the raw disparity value is 0 to 95, so we convert brightness to
# disparity first, then disparity to depth.
def brightnessToDepth(b):
    disparity = (95 * b) / 255

    return BASELINE * FOCAL / disparity


def depthToBrightness(d):
    disparity = BASELINE * FOCAL / d

    return disparity


'''
	Use the current frame to compute a danger value ranging from 0 to 10, purely
    based on distance from an object.
'''
def analyze_frame(frame):
    # experimentally, an average value of 50 is extreme danger
    # so we just divide by 5 to get a decent 0-10 danger value,
    # and subtract that from 10 to get the difference, giving 10
    # for the highest danger, and 0 for the lowest.
    danger = 10 - np.clip(int(np.mean(frame) / 5), 0, 10)
    return danger, frame


# UI helper functions to workaround lambda arguments
def makeSlider(name, window, a_min, a_max):
    cv2.createTrackbar(name, window, a_min, a_max, (lambda x: x))
    cv2.setTrackbarPos(name, window, int((a_min + a_max) / 2))


def setSlider(name, window, val):
    cv2.setTrackbarPos(name, window, val)


if __name__ == "__main__":
    app = qtw.QApplication(sys.argv)

    #camera_input = camera.CameraInput()
    #camera_input.setup()
    #frame_updater_thread = camera.FrameUpdaterThread(camera_input)
    #frame_updater_thread.start()

    main_window = qtw.QWidget()
    ui = App()
    ui.setupUI(main_window)
    main_window.show()

    pipeline = dai.Pipeline()

    # Get side cameras
    monoLeft = getMonoCamera(pipeline, isLeft=True)
    monoRight = getMonoCamera(pipeline, isLeft=False)

    # Get color camera
    cam_rgb = pipeline.create(dai.node.ColorCamera)
    # cam_rgb.setPreviewSize(300, 300)
    cam_rgb.setInterleaved(False)

    stereo = getStereoPair(pipeline, monoLeft, monoRight)

    xOutDisp = pipeline.createXLinkOut()
    xOutDisp.setStreamName("disparity")

    xout_rgb = pipeline.create(dai.node.XLinkOut)
    xout_rgb.setStreamName("rgb")
    cam_rgb.video.link(xout_rgb.input)

    stereo.disparity.link(xOutDisp.input)

    try:
        # Connect device
        with dai.Device(pipeline) as device:
            disparityQueue = device.getOutputQueue(name="disparity", maxSize=1, blocking=False)

            rgbQueue = device.getOutputQueue("rgb")
            frame = None
            # map disparity from 0 to 255
            disparityMultiplier = 255 / stereo.initialConfig.getMaxDisparity()

            '''
                Disparity: Double array of uint8
                    each is in range from 0 -> 255, 0(furthest) 255(closest)
                    [0][0] is top left (?)
                    [0][X] is top right
                    [X][0] is bottom left
                    [X][X] is bottom right
    
            '''

            cv2.namedWindow(WINDOW)

            makeSlider("Danger", WINDOW, 0, DANGER_THRESHOLD)
            referenceFrame = get_reference()

            while True:
                # Code for color camera
                rgb_in = rgbQueue.tryGet()
                if rgb_in is not None:
                    rgb_frame = rgb_in.getCvFrame()
                    ui.camera_view.update_frame(rgb_frame)

                # Code for depth camera

                disparity = getFrame(disparityQueue)
                disparity = (disparity * disparityMultiplier).astype(np.uint8)

                danger, depth_frame = analyze_frame(disparity)  # Result is type np.uint8

                # cv2.imshow(WINDOW, result)
                # ui.camera_view.update_frame(depth_frame)

                if danger > 5:
                    ui.camera_view.display_warning()
                else:
                    ui.camera_view.collision_ind.warning_symbol_hidden(True)

                setSlider("Danger", WINDOW, danger)

                # Check for keyboard input
                key = cv2.waitKey(1)
                if key == ord('q'):
                    # Quit when q is pressed
                    break

            cv2.destroyAllWindows()

        sys.exit(app.exec_())
    except RuntimeError:
        ui.camera_view.video_label.setText("Please plug in the depth camera and reload the program")
        sys.exit(app.exec_())

