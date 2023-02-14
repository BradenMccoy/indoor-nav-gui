import sys, os
import camera_input as camera
import numpy as np
import cv2
from PyQt5 import QtWidgets as qtw
from PyQt5.QtCore import QUrl, QThread, pyqtSignal, QObject, pyqtSlot
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtGui import QPixmap, QImage


class MainWindow(qtw.QWidget):
    # Sets up the media player to play warning sound
    media_player = QMediaPlayer()
    file_path = os.path.join(os.getcwd(), "soundfx/warning.mp3")
    url = QUrl.fromLocalFile(file_path)
    content = QMediaContent(url)
    media_player.setMedia(content)

    def __init__(self, *arg, **kwargs):
        super().__init__(*arg, **kwargs)

        self.warning_button = qtw.QPushButton("Warning Button")
        self.warning_button.clicked.connect(self.warning)
        self.video_label = qtw.QLabel()

        self.VideoThread = VideoThread()

        layout = qtw.QVBoxLayout()
        layout.addWidget(self.warning_button)
        layout.addWidget(self.video_label)
        self.setLayout(layout)

        self.show()

    @pyqtSlot(np.ndarray)
    def update_frame(self, frame):
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image = QImage(frame, frame.shape[1], frame.shape[0], QImage.Format_RGB888)
        self.video_label.setPixmap(QPixmap.fromImage(image))


    def warning(self):
        self.media_player.play()



if __name__ == "__main__":

    app = qtw.QApplication(sys.argv)

    camera_input = camera.CameraInput()
    frame_updater_thread = camera.FrameUpdaterThread(camera_input)
    frame_updater_thread.start()

    w = MainWindow()
    sys.exit(app.exec())
