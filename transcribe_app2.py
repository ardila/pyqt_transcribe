import sys
from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QPushButton
import pyaudio
import wave
import threading

class Recorder():
    def __init__(self, filename):
        self.filename = filename
        self.frames = []
        self.recording = False

        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=44100,
            input=True,
            frames_per_buffer=1024,
            stream_callback=self.callback
        )

    def start(self):
        self.recording = True
        self.stream.start_stream()

    def stop(self):
        self.recording = False
        self.stream.stop_stream()
        self.stream.close()
        self.p.terminate()

        wf = wave.open(self.filename, 'wb')
        wf.setnchannels(1)
        wf.setsampwidth(self.p.get_sample_size(pyaudio.paInt16))
        wf.setframerate(44100)
        wf.writeframes(b''.join(self.frames))
        wf.close()

    def callback(self, in_data, frame_count, time_info, status):
        self.frames.append(in_data)
        return (in_data, pyaudio.paContinue)

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Audio Recorder")
        self.setGeometry(100, 100, 200, 100)

        self.record_button = QPushButton("Record", self)
        self.record_button.move(30, 30)
        self.record_button.clicked.connect(self.start_recording)

        self.stop_button = QPushButton("Stop", self)
        self.stop_button.move(100, 30)
        self.stop_button.setEnabled(False)
        self.stop_button.clicked.connect(self.stop_recording)

        self.show()

    def start_recording(self):
        self.recorder = Recorder("recording.wav")
        self.recording_thread = threading.Thread(target=self.recorder.start)
        self.recording_thread.start()

        self.record_button.setEnabled(False)
        self.stop_button.setEnabled(True)

    def stop_recording(self):
        self.recorder.stop()
        self.recording_thread.join()

        self.record_button.setEnabled(True)
        self.stop_button.setEnabled(False)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec())