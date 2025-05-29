from PyQt6.QtCore import QThread, pyqtSignal
import time
from backup import compress_and_upload

class BackupThread(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal(bool, str)

    def __init__(
        self,
        files,
        password=None,
        output_name="backup",
        part_size=None,
        encrypt_metadata=False,
        immutable=False,
        immutability_duration=None,
        encryption_algorithm="AES256"
    ):
        super().__init__()
        print(">>> BACKUPTHREAD USADO:", __file__)
        self.files = files
        self.password = password
        self.output_name = output_name
        self.part_size = part_size
        self.encrypt_metadata = encrypt_metadata
        self.immutable = immutable
        self.immutability_duration = immutability_duration
        self.encryption_algorithm = encryption_algorithm

    def run(self):
        try:
            for i in range(1, 101):
                time.sleep(0.02)
                self.progress.emit(i)
            result = compress_and_upload(
                self.files,
                self.password,
                self.output_name,
                self.part_size,
                self.encrypt_metadata,
                self.immutable,
                self.immutability_duration,
                self.encryption_algorithm
            )
            self.finished.emit(True, result)
        except Exception as e:
            self.finished.emit(False, str(e))
