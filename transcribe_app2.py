import sys
from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QPushButton, QLabel, QPlainTextEdit
from PyQt6.QtCore import Qt
import pyaudio
import wave
import threading
import whisper

model = whisper.load_model("base")

class Transcriber(QObject):
    transcription_done = pyqtSignal(str)

    def __init__(self):
        super().__init__()

    def transcribe(self, filename):
        result = model.transcribe(filename)
        transcription = result["text"]
        self.transcription_done.emit(transcription)

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
        self.setGeometry(100, 100, 400, 200)

        # Create a label to display transcription
        self.transcription_edit = QPlainTextEdit(self)
        self.transcription_edit.setGeometry(30, 70, 340, 100)
        self.transcription_edit.setReadOnly(True)
        self.transcription_edit.setPlainText("Transcription will appear here.")

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

        self.transcriber = Transcriber()
        self.transcriber.transcription_done.connect(self.on_transcription_done)
        self.transcription_edit.setPlainText("Transcribing...")
        threading.Thread(target=self.transcriber.transcribe, args=("recording.wav",)).start()

    def on_transcription_done(self, transcription):
        # Create a new label with the updated transcription
        self.transcription_edit.setPlainText(transcription)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec())