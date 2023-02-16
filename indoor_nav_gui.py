import sys, os
import camera_input as camera
import math
import depthai as dai
import numpy as np
import cv2
from PyQt5 import QtWidgets as qtw
from PyQt5.QtCore import Qt, QCoreApplication, QMetaObject, QRect, QUrl, QThread, pyqtSignal, QObject, pyqtSlot
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent

class App(qtw.QWidget):
    def setupUI(self, window):
        MainWindow.setObjectName("MainWindow")
        MainWindow.setStyleSheet('background-color: black;')
        MainWindow.resize(927, 652)

        self.CameraView = CameraView(MainWindow)

        self.CollisionIndicatorView = CollisionIndicatorView(MainWindow)
        
        self.LogView = LogView(MainWindow)
        
        self.SettingsView = SettingsView(MainWindow)

        self.retranslateUi(MainWindow)
        QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Collision Detection"))

class CameraView(qtw.QWidget):
    media_player = QMediaPlayer()
    file_path = os.path.join(os.getcwd(), "soundfx/warning.mp3")
    url = QUrl.fromLocalFile(file_path)
    content = QMediaContent(url)
    media_player.setMedia(content)
    show_warning = False

    def __init__(self, ParentWidget):

        self.CameraView = qtw.QWidget(ParentWidget)
        self.CameraView.setGeometry(QRect(30, 20, 871, 361))
        self.CameraView.setObjectName("CameraView")
        self.CameraView.setStyleSheet('background-color: white;')

        self.warning_button = qtw.QPushButton("Warning Button")
        self.warning_button.clicked.connect(lambda: self.display_warning())
        self.video_label = qtw.QLabel()
        
        self.warning_widget = qtw.QWidget(self.CameraView)
        self.warning_widget.setGeometry(QRect(30, 20, 871, 361))
        self.warning_symbol = QPixmap("images/warning-symbol.png").scaled(int(self.warning_widget.height()/2), int(self.warning_widget.width()/2), Qt.KeepAspectRatio, Qt.FastTransformation)
        self.warning_label = qtw.QLabel()
        self.warning_label.setPixmap(self.warning_symbol)
        
        self.warning_layout = qtw.QVBoxLayout()
        self.warning_layout.addWidget(self.warning_label)
        self.warning_widget.setLayout(self.warning_layout)
        self.warning_label.setHidden(True)
        
        layout = qtw.QVBoxLayout()
        layout.addWidget(self.warning_button)
        layout.addWidget(self.warning_widget)
        layout.addWidget(self.video_label)
        self.CameraView.setLayout(layout)

    @pyqtSlot(np.ndarray)
    def update_frame(self, frame):
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image = QImage(frame, frame.shape[1], frame.shape[0], QImage.Format_RGB888)
        self.video_label.setPixmap(QPixmap.fromImage(image))


    def display_warning(self):
        #self.show_warning = not self.show_warning

        self.media_player.play()
        self.warning_label.setHidden(False)

class CollisionIndicatorView(qtw.QWidget):
    def __init__(self, ParentWidget):
        self.CollisionIndicatorView = qtw.QWidget(ParentWidget)
        self.CollisionIndicatorView.setGeometry(QRect(29, 399, 211, 231))
        self.CollisionIndicatorView.setObjectName("CollisionIndicatorView")
        self.CollisionIndicatorView.setStyleSheet('background-color: white;')

class LogView(qtw.QWidget):
    def __init__(self, ParentWidget):
        self.LogView = qtw.QWidget(ParentWidget)
        self.LogView.setGeometry(QRect(259, 399, 411, 231))
        self.LogView.setObjectName("LogView")
        self.LogView.setStyleSheet('background-color: white;')

class SettingsView(qtw.QWidget):
    def __init__(self, ParentWidget):
        self.SettingsView = qtw.QWidget(ParentWidget)
        self.SettingsView.setGeometry(QRect(690, 400, 211, 231))
        self.SettingsView.setObjectName("SettingsView")
        self.SettingsView.setStyleSheet('background-color: white;')


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

WINDOW = "Indoor Nav"


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
    referenceFrame = np.zeros((CAM_HEIGHT, CAM_WIDTH))  # same dimensions as images from the camera

    # Iterating in interpreted python instead of numpy
    # This is slow, but we only do this once at startup
    for y in range(0, CAM_HEIGHT):
        # Angle of the current pixel
        theta = ((1.0 - (y / CAM_HEIGHT)) * VFOV) - (VFOV / 2) + MOUNT_ANGLE

        brightness = depthToBrightness(MOUNT_ELEVATION / (abs(math.tan(math.radians(theta)))))

        for x in range(0, CAM_WIDTH):
            referenceFrame[y][x] = brightness

    return referenceFrame.astype(np.uint8)


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
	Analyzes a given frame compared to what is considered a safe reference image
	returns the danger value, and a new frame which highlights dangerous areas in white
'''


def analyze_frame(frame, referenceFrame):
    frame = np.where(frame != 0, frame, referenceFrame)  # replace unknown values with whatever value is expected

    # we then find the difference between the expected depth and actual depth

    # terrible no-good bad hacky workaround for underflow during subtraction:
    frame = np.clip(np.abs(np.subtract(frame.astype(np.int16), referenceFrame.astype(np.int16))), 0, 255).astype(
        np.uint8)
    # essentially, cast both operands to int16, subtract, get absolute value, clamp to [0,255], cast back to uint8

    # we're now left with an image where black means expected, white means unexpected.
    # therefore, looking for white in the image gives an estimate of danger

    # experimentally, an average value of 50 is extreme danger
    # so we just divide by 5 to get a decent 0-10 danger value
    # there's some issues with the math so an empty room gives danger of like, 2? but that's fine for now
    danger = np.clip(int(np.mean(frame) / 5), 0, 10)
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

    MainWindow = qtw.QWidget()
    ui = App()
    ui.setupUI(MainWindow)
    MainWindow.show()

    pipeline = dai.Pipeline()

    # Get side cameras
    monoLeft = getMonoCamera(pipeline, isLeft=True)
    monoRight = getMonoCamera(pipeline, isLeft=False)

    stereo = getStereoPair(pipeline, monoLeft, monoRight)

    xOutDisp = pipeline.createXLinkOut()
    xOutDisp.setStreamName("disparity")

    stereo.disparity.link(xOutDisp.input)

    try:
        # Connect device
        with dai.Device(pipeline) as device:
            disparityQueue = device.getOutputQueue(name="disparity", maxSize=1, blocking=False)

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
                disparity = getFrame(disparityQueue)
                disparity = (disparity * disparityMultiplier).astype(np.uint8)

                danger, result = analyze_frame(disparity, referenceFrame)

                # cv2.imshow(WINDOW, result)
                ui.CameraView.update_frame(result)
                if danger > 5:
                    ui.CameraView.display_warning()
                else:
                    ui.CameraView.warning_label.setHidden(True)

                setSlider("Danger", WINDOW, danger)

                # Check for keyboard input
                key = cv2.waitKey(1)
                if key == ord('q'):
                    # Quit when q is pressed
                    break

            cv2.destroyAllWindows()

        sys.exit(app.exec_())
    except RuntimeError:
        ui.CameraView.video_label.setText("Please plug in the depth camera and reload the program")
        sys.exit(app.exec_())

