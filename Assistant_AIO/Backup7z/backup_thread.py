from PyQt6.QtCore import QThread, pyqtSignal
import time
from backup import compress_and_upload

class BackupThread(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal(bool, str)

    def __init__(self, files, password=None):
        super().__init__()
        self.files = files
        self.password = password

    def run(self):
        try:
            # Simulación de progreso (actualiza según tu lógica real)
            for i in range(1, 101):
                time.sleep(0.05)
                self.progress.emit(i)
            
            result = compress_and_upload(self.files, self.password)
            self.finished.emit(True, result)
        except Exception as e:
            self.finished.emit(False, str(e))