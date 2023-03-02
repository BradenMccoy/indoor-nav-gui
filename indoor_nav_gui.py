# imports
import sys
import os
import depthai as dai
import numpy as np
import cv2
import blobconverter
import logging
from PyQt5 import QtWidgets as qtw
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent

# global variables

CAM_WIDTH = 640
CAM_HEIGHT = 400
# At the moment, the camera is 45 cm from the ground, pointed 30 degrees downward
MOUNT_ELEVATION = 45
MOUNT_ANGLE = -30
HFOV = 71.9  # Horizontal field of view
VFOV = 50.0  # Vertical field of view
BASELINE = 7.5  # Distance between stereo cameras in cm
FOCAL = 883.15  # Magic number needed for disparity -> depth calculation

has_logged_object = False

# primary app
class App(qtw.QWidget):
    # setup program ui
    def setup_ui(self, main_window):
        main_window.setObjectName("MainWindow")
        main_window.setStyleSheet("background-color: black;")
        main_window.resize(927, 652)

        # initialize all views
        self.settings_view = SettingsView(main_window)
        self.collision_indicator_view = CollisionIndicatorView(main_window)
        self.log_view = LogView(main_window)
        self.camera_view = CameraView(
            main_window, self.settings_view, self.collision_indicator_view)

        self.retranslate_ui(main_window)
        QMetaObject.connectSlotsByName(main_window)

    def retranslate_ui(self, main_window):
        _translate = QCoreApplication.translate
        main_window.setWindowTitle(_translate(
            "MainWindow", "Collision Detection"))

# view of depth camera output
class CameraView(qtw.QWidget):
    media_player = QMediaPlayer()
    file_path = os.path.join(os.getcwd(), "soundfx/warning.mp3")
    url = QUrl.fromLocalFile(file_path)
    content = QMediaContent(url)
    media_player.setMedia(content)

    def __init__(self, parent_widget, settings, collision_indicator):
        super(CameraView, self).__init__()
        # camera output
        self.camera_view = qtw.QWidget(parent_widget)
        self.camera_view.setGeometry(QRect(30, 20, 871, 361))
        self.camera_view.setObjectName("CameraView")
        self.camera_view.setStyleSheet("background-color: white;")

        self.settings = settings
        self.collision_ind = collision_indicator

        self.video_label = qtw.QLabel()

        layout = qtw.QVBoxLayout()
        layout.addWidget(self.video_label)
        self.camera_view.setLayout(layout)

    # draw current frame of camera output
    @pyqtSlot(np.ndarray)
    def update_frame(self, frame):
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image = QImage(frame, frame.shape[1],
                       frame.shape[0], QImage.Format_RGB888)
        pixmap_image = QPixmap.fromImage(image)
        pixmap_image = pixmap_image.scaled(self.camera_view.frameGeometry(
        ).width(), self.camera_view.frameGeometry().height())
        self.video_label.setPixmap(pixmap_image)

    # display collision warning for nearby obstacle
    def display_warning(self):
        if not has_logged_object:
            logging.warning("Warning! You are moving close to an obstacle!")
        if self.settings.has_sound():
            self.media_player.setMedia(self.settings.get_audio())
            self.media_player.play()
        self.collision_ind.warning_symbol_hidden(False)

# indication of collisions with warning symbol and danger value
class CollisionIndicatorView(qtw.QWidget):
    def __init__(self, parent_widget):
        self.collision_indicator_view = qtw.QWidget(parent_widget)
        self.collision_indicator_view.setGeometry(QRect(29, 399, 211, 231))
        self.collision_indicator_view.setObjectName("CollisionIndicatorView")
        self.collision_indicator_view.setStyleSheet("background-color: white;")

        # warning symbol
        self.warning_widget = qtw.QWidget(parent_widget)
        self.warning_widget.setGeometry(QRect(30, 20, 871, 361))
        self.warning_symbol = QPixmap("images/warning.png").scaled(int(self.warning_widget.height() / 2),
                                                                   int(self.warning_widget.width(
                                                                   ) / 2),
                                                                   Qt.KeepAspectRatio, Qt.FastTransformation)
        self.warning_label = qtw.QLabel()
        self.warning_label.setPixmap(self.warning_symbol)

        self.warning_layout = qtw.QVBoxLayout()
        self.warning_layout.addWidget(self.warning_label)
        self.warning_widget.setLayout(self.warning_layout)
        self.warning_label.setHidden(True)

        # danger value
        self.danger_widget = qtw.QWidget(parent_widget)
        self.danger_widget.setGeometry(QRect(30, 20, 871, 361))

        self.danger_label = qtw.QLabel()
        self.danger_label.setText("Danger: 0")

        self.danger_layout = qtw.QVBoxLayout()
        self.danger_layout.addWidget(self.danger_label)
        self.danger_widget.setLayout(self.danger_layout)

        layout = qtw.QVBoxLayout()
        layout.addWidget(self.warning_label)
        layout.addWidget(self.danger_label)

        self.collision_indicator_view.setLayout(layout)

    # hide collision warning symbol
    def warning_symbol_hidden(self, b):
        self.warning_label.setHidden(b)

    # dynamically update danger value in real time
    def update_danger(self, new_danger):
        self.danger_label.setText(new_danger)

# object detection logs when a warning is issued
class LogView(qtw.QWidget):
    def __init__(self, parent_widget):
        self.log_view = qtw.QWidget(parent_widget)
        self.log_view.setGeometry(QRect(259, 399, 411, 231))
        self.log_view.setObjectName("LogView")
        self.log_view.setStyleSheet("background-color: white;")

        self.log_controller = LogController(self.log_view)
        logging.getLogger().addHandler(self.log_controller)

# settings used to tailor the program user experience
class SettingsView(qtw.QWidget):
    audio_warning = True

    def __init__(self, parent_widget):
        super(SettingsView, self).__init__()
        self.settings_view = qtw.QWidget(parent_widget)
        self.settings_view.setGeometry(QRect(690, 400, 211, 231))
        self.settings_view.setObjectName("SettingsView")
        self.settings_view.setStyleSheet("background-color: white;")

        # mute button for auditory collision warnings
        self.mute_button = qtw.QPushButton() #" Audio Warning")
        self.mute_button.clicked.connect(lambda: self.toggle_sound())
        self.mute_button.setFont(QFont('Arial', 14))
        self.mute_button.setIcon(QIcon("images/unmute.png"))
        self.mute_button.setText(" Mute Audio")

        # change sound button for customizing warning sound
        self.change_sound_button = qtw.QPushButton("Change Warning Sound")
        self.change_sound_button.clicked.connect(lambda: self.change_sound())
        self.change_sound_button.setFont(QFont('Arial', 14))

        layout = qtw.QVBoxLayout()
        layout.addWidget(self.mute_button)
        layout.addWidget(self.change_sound_button)
        self.settings_view.setLayout(layout)

    # get the current audio file
    def get_audio(self):
        if self.audio_file == None:
            return "soundfx/default.mp3"
        return self.audio_file

    # change current audio file to the selected audio file
    def change_sound(self):
        dialog = qtw.QFileDialog(self, directory="soundfx/")
        if dialog.exec_() == qtw.QDialog.Accepted:
            self.audio_file = dialog.selectedFiles()[0]
            logging.warning("Selected " + os.path.basename(self.audio_file))

    # turn collision warning sound on or off
    def toggle_sound(self):
        self.audio_warning = not self.audio_warning
        if self.audio_warning:
            self.mute_button.setIcon(QIcon("images/unmute.png"))
            self.mute_button.setText(" Mute Audio")
        else:
            self.mute_button.setIcon(QIcon("images/mute.png"))
            self.mute_button.setText(" Unmute Audio")

    # whether or not sound is enabled
    def has_sound(self):
        return self.audio_warning

# controller for object collision detection logs
class LogController(logging.Handler):
    def __init__(self, parent_widget):
        super(LogController, self).__init__()

        self.log_text = qtw.QPlainTextEdit(parent_widget)
        self.log_text.resize(411, 231)
        self.log_text.setFont(QFont('Arial', 12))
        self.log_text.setReadOnly(True)

    # add log to log box
    def emit(self, msg):
        msg = self.format(msg)
        self.log_text.appendPlainText(msg)

# get current frame of camera output
def get_frame(queue):
    # Get frame from queue
    frame = queue.get()
    # Convert frame to OpenCV format
    return frame.getCvFrame()

# set resolution and determine if camera is left or right on device
def get_mono_camera(pipeline, isLeft):
    mono = pipeline.createMonoCamera()

    mono.setResolution(dai.MonoCameraProperties.SensorResolution.THE_400_P)

    if isLeft:
        mono.setBoardSocket(dai.CameraBoardSocket.LEFT)
    else:
        mono.setBoardSocket(dai.CameraBoardSocket.RIGHT)
    return mono

# get stereo pair and link mono cameras to it
def get_stereo_pair(pipeline, monoLeft, monoRight):
    stereo = pipeline.createStereoDepth()

    # Turn on occlusion check (small performance hit, but output is less noisy)
    stereo.setLeftRightCheck(True)
    # Link mono cameras to the stereo pair
    monoLeft.out.link(stereo.left)
    monoRight.out.link(stereo.right)

    return stereo

# set up properties of frame
def get_reference():
    # same dimensions as images from the camera
    reference_frame = np.zeros((CAM_HEIGHT, CAM_WIDTH))

    # generate an array of theta values based on VFOV and MOUNT_ANGLE
    theta = np.linspace(-(VFOV / 2) + MOUNT_ANGLE, VFOV /
                        2 + MOUNT_ANGLE, CAM_HEIGHT)
    # calculate elevation factor
    elevation_factor = MOUNT_ELEVATION / np.tan(np.radians(theta))
    # get an array of brightness values
    brightness = depth_to_brightness(elevation_factor)
    # tile brightness array along the second axis CAM_WIDTH times and create the referenceFrame array
    reference_frame = np.tile(brightness[:, np.newaxis], (1, CAM_WIDTH))

    return reference_frame.astype(np.uint8)


# Image brightness (0 to 255) to depth (cm)
# Ideally we'd use disparity to depth, but our test cases already map disparity from
# 0 to 255, while the raw disparity value is 0 to 95, so we convert brightness to
# disparity first, then disparity to depth.
def brightness_to_depth(b):
    disparity = (95 * b) / 255

    return BASELINE * FOCAL / disparity

# opposite of brightness to depth
def depth_to_brightness(d):
    disparity = BASELINE * FOCAL / d

    return disparity


# Use the current frame to compute a danger value ranging from 0 to 10, purely
# based on distance from an object.
def analyze_frame(frame):
    # experimentally, an average value of 50 is extreme danger
    # so we just divide by 5 to get a decent 0-10 danger value,
    # and subtract that from 10 to get the difference, giving 10
    # for the highest danger, and 0 for the lowest.
    danger = 10 - np.clip(int(np.mean(frame) / 5), 0, 10)
    return danger, frame


if __name__ == "__main__":
    app = qtw.QApplication(sys.argv)

    main_window = qtw.QWidget()
    ui = App()
    ui.setup_ui(main_window)
    main_window.show()

    pipeline = dai.Pipeline()

    # Get side cameras
    monoLeft = get_mono_camera(pipeline, isLeft=True)
    monoRight = get_mono_camera(pipeline, isLeft=False)

    # Get color camera
    cam_rgb = pipeline.create(dai.node.ColorCamera)
    cam_rgb.setInterleaved(False)

    # Next, we want a neural network that will produce the detections
    detection_nn = pipeline.createMobileNetDetectionNetwork()
    # Blob is the Neural Network file, compiled for MyriadX. It contains both the definition and weights of the model
    # We're using a blobconverter tool to retreive the MobileNetSSD blob automatically from OpenVINO Model Zoo
    detection_nn.setBlobPath(blobconverter.from_zoo(
        name='mobilenet-ssd', shaves=6))
    # Next, we filter out the detections that are below a confidence threshold. Confidence can be anywhere between <0..1>
    detection_nn.setConfidenceThreshold(0.5)
    # Next, we link the camera 'preview' output to the neural network detection input, so that it can produce detections
    cam_rgb.preview.link(detection_nn.input)

    stereo = get_stereo_pair(pipeline, monoLeft, monoRight)

    xOutDisp = pipeline.createXLinkOut()
    xOutDisp.setStreamName("disparity")

    xout_rgb = pipeline.create(dai.node.XLinkOut)
    xout_rgb.setStreamName("rgb")
    cam_rgb.video.link(xout_rgb.input)

    # The same XLinkOut mechanism will be used to receive nn results
    xout_nn = pipeline.createXLinkOut()
    xout_nn.setStreamName("nn")
    detection_nn.out.link(xout_nn.input)

    stereo.disparity.link(xOutDisp.input)

    try:
        # Connect device
        with dai.Device(pipeline) as device:
            disparityQueue = device.getOutputQueue(
                name="disparity", maxSize=1, blocking=False)
            q_nn = device.getOutputQueue("nn")

            rgbQueue = device.getOutputQueue("rgb")
            frame = None
            detections = []
            # map disparity from 0 to 255
            disparityMultiplier = 255 / stereo.initialConfig.getMaxDisparity()

            # Since the detections returned by nn have values from <0..1> range, they need to be multiplied by frame width/height to
            # receive the actual position of the bounding box on the image
            def frameNorm(frame, bbox):
                normVals = np.full(len(bbox), frame.shape[0])
                normVals[::2] = frame.shape[1]
                return (np.clip(np.array(bbox), 0, 1) * normVals).astype(int)

            '''
                Disparity: Double array of uint8
                    each is in range from 0 -> 255, 0(furthest) 255(closest)
                    [0][0] is top left (?)
                    [0][X] is top right
                    [X][0] is bottom left
                    [X][X] is bottom right
    
            '''

            while True:
                # Code for color camera and nn
                rgb_in = rgbQueue.tryGet()
                in_nn = q_nn.tryGet()
                rgb_frame = None

                if rgb_in is not None:
                    rgb_frame = rgb_in.getCvFrame()

                if in_nn is not None:
                    # when data from nn is received, we take the detections array that contains mobilenet-ssd results
                    detections = in_nn.detections

                # Code for depth camera
                disparity = get_frame(disparityQueue)
                disparity = (disparity * disparityMultiplier).astype(np.uint8)

                danger, depth_frame = analyze_frame(
                    disparity)  # Result is type np.uint8

                if rgb_frame is not None:
                    for detection in detections:
                        # for each bounding box, we first normalize it to match the frame size
                        bbox = frameNorm(
                            rgb_frame, (detection.xmin, detection.ymin, detection.xmax, detection.ymax))
                        # and then draw a rectangle on the frame to show the actual result
                        cv2.rectangle(
                            rgb_frame, (bbox[0], bbox[1]), (bbox[2], bbox[3]), (255, 0, 0), 2)
                    # After all the drawing is finished, we show the frame on the screen
                    ui.camera_view.update_frame(rgb_frame)

                # show collision warning if computed danger is above 5
                if danger > 5:
                    ui.camera_view.display_warning()
                    has_logged_object = True
                # otherwise hide the warning
                else:
                    ui.camera_view.collision_ind.warning_symbol_hidden(True)
                    has_logged_object = False

                ui.collision_indicator_view.update_danger(
                    "Danger: " + str(danger))

                # Check for keyboard input
                key = cv2.waitKey(1)
    except RuntimeError:
        # if camera is not connected, let user know instead of crashing
        ui.camera_view.video_label.setText(
            "Please connect the depth camera and reload the program!")
        sys.exit(app.exec_())
