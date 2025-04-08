import sys
import subprocess
import os
import json
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QPushButton,
                             QLineEdit, QLabel, QFileDialog, QMessageBox, QCheckBox)

CONFIG_FILE = "config.json"
RCLONE_CONFIG_PATH = "C:\\rclone\\rclone.conf"
WINFSP_URL = "https://winfsp.dev/rel/"

class BackupB2App(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.load_config()
        self.check_winfsp()
    
    def init_ui(self):
        self.setWindowTitle("Backup App con B2")
        self.setGeometry(100, 100, 500, 400)
        
        layout = QVBoxLayout()

        self.bucket_label = QLabel("Nombre del bucket B2:")
        self.bucket_input = QLineEdit()
        layout.addWidget(self.bucket_label)
        layout.addWidget(self.bucket_input)
        
        self.access_key_label = QLabel("B2 Account ID:")
        self.access_key_input = QLineEdit()
        layout.addWidget(self.access_key_label)
        layout.addWidget(self.access_key_input)

        self.secret_key_label = QLabel("B2 Application Key:")
        self.secret_key_input = QLineEdit()
        self.secret_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.secret_key_label)
        layout.addWidget(self.secret_key_input)
        
        self.save_credentials_button = QPushButton("Guardar Credenciales B2")
        self.save_credentials_button.clicked.connect(self.save_b2_credentials)
        layout.addWidget(self.save_credentials_button)
        
        self.mount_button = QPushButton("Montar B2")
        self.mount_button.clicked.connect(self.mount_b2)
        layout.addWidget(self.mount_button)
        
        self.unmount_button = QPushButton("Desmontar B2")
        self.unmount_button.clicked.connect(self.unmount_b2)
        layout.addWidget(self.unmount_button)
        
        self.autostart_checkbox = QCheckBox("Montar B2 en el arranque")
        self.autostart_checkbox.stateChanged.connect(self.toggle_autostart)
        layout.addWidget(self.autostart_checkbox)
        
        self.backup_button = QPushButton("Seleccionar Carpeta para Backup")
        self.backup_button.clicked.connect(self.select_backup_folder)
        layout.addWidget(self.backup_button)
        
        self.setLayout(layout)
    
    def check_winfsp(self):
        try:
            result = subprocess.run(["fsptool-x64", "--version"], capture_output=True, text=True)
            if result.returncode != 0:
                raise FileNotFoundError
        except FileNotFoundError:
            QMessageBox.warning(self, "WinFsp no encontrado", "WinFsp no está instalado. Se procederá a descargar e instalar automáticamente.")
            self.install_winfsp()
            self.add_winfsp_to_path()
    
    def install_winfsp(self):
        installer_path = os.path.join(os.getcwd(), "winfsp-installer.exe")
        subprocess.run(["powershell", "-Command", f"Invoke-WebRequest -Uri {WINFSP_URL} -OutFile {installer_path}"], shell=True)
        subprocess.run([installer_path, "/S"], shell=True)
        QMessageBox.information(self, "Instalación Completa", "WinFsp ha sido instalado. Reinicie el sistema si es necesario.")
    
    def add_winfsp_to_path(self):
        winfsp_path = "C:\\Program Files (x86)\\WinFsp\\bin"
        current_path = os.environ.get("PATH", "")
        if winfsp_path not in current_path:
            os.environ["PATH"] = f"{winfsp_path};{current_path}"
            subprocess.run(f'setx PATH "{os.environ["PATH"]}"', shell=True)
            QMessageBox.information(self, "PATH Actualizado", "WinFsp ha sido agregado al PATH del sistema. Reinicie el sistema si es necesario.")
    
    def save_b2_credentials(self):
        access_key = self.access_key_input.text().strip()
        secret_key = self.secret_key_input.text().strip()

        if not access_key or not secret_key:
            QMessageBox.warning(self, "Error", "Debe ingresar Account ID y Application Key")
            return

        os.makedirs(os.path.dirname(RCLONE_CONFIG_PATH), exist_ok=True)
        with open(RCLONE_CONFIG_PATH, "w") as f:
            f.write(f"[b2]\n")
            f.write(f"type = b2\n")
            f.write(f"account = {access_key}\n")
            f.write(f"key = {secret_key}\n")
        
        QMessageBox.information(self, "Éxito", "Credenciales guardadas correctamente")
        self.save_config()
    
    def mount_b2(self):
        bucket = self.bucket_input.text().strip()
        if not bucket:
            QMessageBox.warning(self, "Error", "Debe ingresar un nombre de bucket")
            return
        
        if not self.is_rclone_available():
            QMessageBox.critical(self, "Error", "rclone no está disponible en el PATH del sistema. Por favor, instale rclone y asegúrese de que esté en el PATH.")
            return
        
        mount_command = f"rclone mount b2:{bucket} X:\\ --vfs-cache-mode full"
        subprocess.Popen(mount_command, shell=True)
        QMessageBox.information(self, "Éxito", f"Bucket {bucket} montado en la unidad X:")
        self.save_config()

    def is_rclone_available(self):
        try:
            subprocess.run(["rclone", "--version"], capture_output=True, text=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False
    
    def unmount_b2(self):
        subprocess.run("taskkill /IM rclone.exe /F", shell=True)
        QMessageBox.information(self, "Desmontado", "Se desmontó el almacenamiento B2.")
    
    def select_backup_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Seleccionar Carpeta para Backup")
        if folder:
            backup_command = f"robocopy {folder} X:\\Backup /MIR"
            subprocess.run(backup_command, shell=True)
            QMessageBox.information(self, "Backup Completado", f"Backup de {folder} guardado en B2")
    
    def toggle_autostart(self):
        if self.autostart_checkbox.isChecked():
            script_path = os.path.abspath(__file__)
            autostart_command = f'reg add HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run /v B2Mount /t REG_SZ /d "{script_path}" /f'
            subprocess.run(autostart_command, shell=True)
        else:
            remove_autostart = 'reg delete HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run /v B2Mount /f'
            subprocess.run(remove_autostart, shell=True)
        self.save_config()
    
    def save_config(self):
        config = {
            "bucket": self.bucket_input.text(),
            "autostart": self.autostart_checkbox.isChecked()
        }
        with open(CONFIG_FILE, "w") as f:
            json.dump(config, f)
    
    def load_config(self):
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "r") as f:
                config = json.load(f)
                self.bucket_input.setText(config.get("bucket", ""))
                self.autostart_checkbox.setChecked(config.get("autostart", False))

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = BackupB2App()
    window.show()
    sys.exit(app.exec())
