from PyQt6.QtCore import QThread, pyqtSignal
from backup import compress_and_upload

class BackupThread(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal(bool, str)

    def __init__(self, files, output_name):
        super().__init__()
        self.files = files
        self.output_name = output_name

    def run(self):
        try:
            result = compress_and_upload(
                self.files,
                self.output_name,
                progress_callback=self.progress.emit
            )
            self.finished.emit(True, result)
        except Exception as e:
            self.finished.emit(False, str(e))
