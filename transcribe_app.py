import sys
import threading
import wave
from queue import Queue

import lameenc
import pyaudio
from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton


class AudioRecorder(QObject):
    finished = pyqtSignal()

    def __init__(self, filename):
        super().__init__()
        self.filename = filename
        self.frames = []
        self.should_stop = False

    def start(self):
        CHUNK = 1024
        FORMAT = pyaudio.paInt16
        CHANNELS = 1
        RATE = 44100

        p = pyaudio.PyAudio()

        stream = p.open(format=FORMAT,
                        channels=CHANNELS,
                        rate=RATE,
                        input=True,
                        frames_per_buffer=CHUNK)

        self.frames = []

        while not self.should_stop:
            data = stream.read(CHUNK)
            self.frames.append(data)

        stream.stop_stream()
        stream.close()
        p.terminate()

        wf = wave.open(self.filename, 'wb')
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(p.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(self.frames))
        wf.close()
        self.transcode_mp3()

    def transcode_mp3(self):
        # Convert WAV to MP3 using lameenc
        with open(self.filename, 'rb') as wav_file:
            wav_data = wav_file.read()

        mp3_data = lameenc.encode(wav_data, rate=44100, channels=1)
        with open(self.filename[:-4] + ".mp3", 'wb') as mp3_file:
            mp3_file.write(mp3_data)

    def stop(self):
        self.should_stop = True
        self.finished.emit()

def start_recorder(filename):
    recorder = AudioRecorder(filename)
    thread = threading.Thread(target=recorder.start)
    thread.start()
    return recorder

class MainWindow(QMainWindow):
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
        self.recorder = start_recorder("recording.wav")
        self.stop_button.setEnabled(True)
        self.record_button.setEnabled(False)

    def stop_recording(self):
        self.recorder.stop()
        self.recorder.finished.connect(self.on_finished_recording)

    def on_finished_recording(self):
        self.record_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        del self.recorder


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())