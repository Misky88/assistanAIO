from PyQt6.QtCore import QThread, pyqtSignal
import time
from backup import compress_and_upload

class BackupThread(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal(bool, str)

    def __init__(self, files, password=None, output_name="backup.7z", part_size=None, encrypt_metadata=False, 
                immutable=False, immutability_duration=None):
        super().__init__()
        self.files = files
        self.password = password
        self.output_name = output_name
        self.part_size = part_size
        self.encrypt_metadata = encrypt_metadata
        self.immutable = immutable
        self.immutability_duration = immutability_duration


    def run(self):
        try:
            for i in range(1, 101):
                time.sleep(0.05)
                self.progress.emit(i)

            result = compress_and_upload(
                self.files,
                self.password,
                output_name=self.output_name,
                part_size=self.part_size
            )
            self.finished.emit(True, result)
        except Exception as e:
            self.finished.emit(False, str(e))
