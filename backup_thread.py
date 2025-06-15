from PyQt6.QtCore import QThread, pyqtSignal
from backup import compress_and_upload
from PyQt6.QtWidgets import QMessageBox

class BackupThread(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal(bool, str)

    def __init__(self, files, output_name, password=None):
        super().__init__()
        self.files = files
        self.output_name = output_name
        self.password = password

    def run(self):
        try:
            output_file = f"{self.output_name}.7z"
            result = compress_and_upload(
                self.files,
                password=self.password,
                output_name=self.output_name,
                progress_callback=self.progress.emit
            )
            self.finished.emit(True, result)
        except Exception as e:
            self.finished.emit(False, str(e))

def on_backup_finished(self, success, result):
    if success:
        QMessageBox.information(self, "Éxito", f"Backup completado exitosamente: {result}")
    else:
        QMessageBox.critical(self, "Error", f"Error en el backup: {result}")
