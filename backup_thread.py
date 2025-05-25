from PyQt6.QtCore import QThread, pyqtSignal
import time
from backup import compress_and_upload

class BackupThread(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal(bool, str)

    def __init__(
        self, files, destination, part_size=None, password=None,
        encrypt_filenames=False, immutable=False, immutability_days=0,
        encryption_algorithm="AES-256", output_name="backup.7z"
    ):
        super().__init__()
        self.files = files
        self.destination = destination
        self.part_size = part_size
        self.password = password
        self.encrypt_filenames = encrypt_filenames
        self.immutable = immutable
        self.immutability_days = immutability_days
        self.encryption_algorithm = encryption_algorithm
        self.output_name = output_name


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
