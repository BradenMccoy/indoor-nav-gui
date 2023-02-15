import sys, os
import camera_input as camera
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
    show_warning = True

    def __init__(self, ParentWidget):
        self.CameraView = qtw.QWidget(ParentWidget)
        self.CameraView.setGeometry(QRect(30, 20, 871, 361))
        self.CameraView.setObjectName("CameraView")
        self.CameraView.setStyleSheet('background-color: white;')

        self.warning_button = qtw.QPushButton("Warning Button")
        self.warning_button.clicked.connect(lambda: self.display_warning())
        self.video_label = qtw.QLabel()

        self.VideoThread = VideoThread() 
        
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
        self.show_warning = not self.show_warning

        self.media_player.play()
        self.warning_label.setHidden((self.show_warning))

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

if __name__ == "__main__":
    app = qtw.QApplication(sys.argv)

    camera_input = camera.CameraInput()
    frame_updater_thread = camera.FrameUpdaterThread(camera_input)
    frame_updater_thread.start()

    MainWindow = qtw.QWidget()
    ui = App()
    ui.setupUI(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
